"""
pipeline/extract_skills.py

Extracts skills from job descriptions using spaCy PhraseMatcher:
- Loads canonical skills and aliases from data/skills.yaml (not hardcoded in code)
- Uses spaCy token-boundary PhraseMatcher for word-boundary safety
- Handles tricky tokens (Go, R, C++, Node.js) with case-sensitivity controls
- Deduplicates skills per posting
- Maps every matched alias to its canonical skill name
"""

import json
import logging
import os
import sys
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("skill_extractor")

class SkillExtractor:
    def __init__(self, skills_yaml_path: str = "data/skills.yaml"):
        self.skills_yaml_path = skills_yaml_path
        self.nlp = spacy.blank("en")
        
        # Two PhraseMatchers:
        # 1. Lowercase matcher for general case-insensitive skills
        self.matcher_lower = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        # 2. Exact matcher for case-sensitive single words like "Go", "R"
        self.matcher_exact = PhraseMatcher(self.nlp.vocab)
        
        # Mappings: pattern string id -> canonical skill name
        self.id_to_canonical: dict[str, str] = {}
        self.canonical_skills: dict[str, dict] = {}
        
        self._load_skills()

    def _load_skills(self):
        if not os.path.exists(self.skills_yaml_path):
            raise FileNotFoundError(f"Skills definition file not found: {self.skills_yaml_path}")
            
        with open(self.skills_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        skills_list = data.get("skills", [])
        logger.info(f"Loaded {len(skills_list)} skills from {self.skills_yaml_path}")
        
        lower_patterns_by_id = {}
        exact_patterns_by_id = {}

        for item in skills_list:
            canonical = item["canonical"]
            category = item.get("category", "General")
            aliases = item.get("aliases", [])
            case_sensitive_aliases = item.get("case_sensitive_aliases", [])
            
            self.canonical_skills[canonical] = {
                "canonical": canonical,
                "category": category,
                "aliases": aliases
            }
            
            str_id = f"SKILL_{canonical}"
            self.id_to_canonical[str_id] = canonical

            # Case-insensitive patterns
            lower_docs = []
            # Canonical itself as pattern
            if canonical not in ["Go", "R"]:
                lower_docs.append(self.nlp.make_doc(canonical))
                
            for alias in aliases:
                # If alias is tricky like 'go' or 'r', skip lowercase matching unless specified
                if alias.lower() in ["go", "r"]:
                    continue
                lower_docs.append(self.nlp.make_doc(alias))
                
            if lower_docs:
                lower_patterns_by_id[str_id] = lower_docs
                
            # Case-sensitive patterns (e.g. "Go", "R")
            exact_docs = []
            for cs in case_sensitive_aliases:
                exact_docs.append(self.nlp.make_doc(cs))
            if canonical in ["Go", "R"]:
                exact_docs.append(self.nlp.make_doc(canonical))
                
            if exact_docs:
                exact_patterns_by_id[str_id] = exact_docs

        for str_id, docs in lower_patterns_by_id.items():
            self.matcher_lower.add(str_id, docs)
            
        for str_id, docs in exact_patterns_by_id.items():
            self.matcher_exact.add(str_id, docs)

    def extract_skills(self, text: str) -> list[str]:
        """
        Extracts all canonical skills present in the text with word-boundary safety.
        Returns a sorted list of unique canonical skill names.
        """
        if not text or not isinstance(text, str):
            return []
            
        doc = self.nlp(text)
        found_canonicals = set()
        
        # 1. Lowercase matches
        matches_lower = self.matcher_lower(doc)
        for match_id, start, end in matches_lower:
            str_id = self.nlp.vocab.strings[match_id]
            canonical = self.id_to_canonical.get(str_id)
            if canonical:
                found_canonicals.add(canonical)
                
        # 2. Exact matches
        matches_exact = self.matcher_exact(doc)
        for match_id, start, end in matches_exact:
            str_id = self.nlp.vocab.strings[match_id]
            canonical = self.id_to_canonical.get(str_id)
            if canonical:
                found_canonicals.add(canonical)

        return sorted(list(found_canonicals))

def run_extraction(
    cleaned_csv_path: str = "data/processed/jobs_cleaned.csv",
    output_skills_csv: str = "data/processed/job_skills.csv",
    output_enriched_csv: str = "data/processed/jobs_with_skills.csv"
):
    logger.info("Initializing SkillExtractor...")
    extractor = SkillExtractor()
    
    logger.info(f"Reading cleaned jobs from {cleaned_csv_path}...")
    df = pd.read_csv(cleaned_csv_path)
    
    job_skills_records = []
    enriched_skills_col = []
    
    logger.info(f"Extracting skills for {len(df)} jobs...")
    for idx, row in df.iterrows():
        job_id = row["job_id"]
        # Combine title and description for comprehensive extraction
        full_text = f"{row['title']}\n{row['description']}"
        skills = extractor.extract_skills(full_text)
        
        enriched_skills_col.append(";".join(skills))
        for sk in skills:
            job_skills_records.append({
                "job_id": job_id,
                "skill_canonical": sk
            })
            
    # Save job_skills.csv
    skills_df = pd.DataFrame(job_skills_records)
    skills_df.to_csv(output_skills_csv, index=False, encoding="utf-8")
    logger.info(f"Extracted {len(skills_df)} total skill-job associations -> saved to '{output_skills_csv}'")
    
    # Save jobs_with_skills.csv
    df["skills"] = enriched_skills_col
    df.to_csv(output_enriched_csv, index=False, encoding="utf-8")
    logger.info(f"Enriched jobs with skills column -> saved to '{output_enriched_csv}'")
    
    # Summary of most common extracted skills
    top_extracted = skills_df["skill_canonical"].value_counts().head(10)
    logger.info(f"Top 10 extracted skills overall:\n{top_extracted.to_string()}")

if __name__ == "__main__":
    run_extraction()
