"""
pipeline/clean.py

Cleans and normalises raw job postings:
- Deduplicates postings
- Normalises city names to canonical Indian cities
- Normalises role titles to canonical role taxonomy
- Normalises experience range (min_exp, max_exp)
- Parses diverse salary expressions to annual INR (min, max, median)
- Handles missing values cleanly
- Logs rows kept at each step
"""

import logging
import os
import re
import sys
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("cleaner")

# Canonical Role Taxonomy and Regex patterns
ROLE_TAXONOMY = {
    "Backend Developer": [
        r"\bback[- ]?end\b", r"\bapi\b", r"\bspring boot\b", r"\bdjango\b", r"\bfastapi\b",
        r"\bjava\b.*\bdeveloper\b", r"\bpython\b.*\bbackend\b", r"\bgo\b.*\bdeveloper\b",
        r"\bnode\.?js\b.*\bdeveloper\b", r"\bsoftware development engineer - backend\b"
    ],
    "Frontend Developer": [
        r"\bfront[- ]?end\b", r"\breact(\.js)?\b", r"\bui engineer\b", r"\bweb developer\b",
        r"\bnext\.?js\b", r"\bangular\b", r"\bvue(\.js)?\b"
    ],
    "Full Stack Developer": [
        r"\bfull[- ]?stack\b", r"\bmern\b", r"\bmean stack\b",
        r"\bsoftware development engineer - fullstack\b"
    ],
    "Data Engineer": [
        r"\bdata engineer\b", r"\bbig data\b", r"\betl\b", r"\bdata pipeline\b",
        r"\banalytics engineer\b", r"\bdata infrastructure\b"
    ],
    "Machine Learning Engineer": [
        r"\bmachine learning\b", r"\bml engineer\b", r"\bai[- /]?ml\b",
        r"\bdata scientist\b", r"\bdeep learning\b", r"\bnlp engineer\b",
        r"\bapplied ai\b", r"\bcomputer vision\b"
    ],
    "DevOps Engineer": [
        r"\bdevops\b", r"\bsre\b", r"\bsite reliability\b", r"\bcloud.*engineer\b",
        r"\bplatform engineer\b", r"\binfrastructure engineer\b", r"\bkubernetes engineer\b"
    ],
    "Data Analyst": [
        r"\bdata analyst\b", r"\bpower bi\b", r"\btableau\b", r"\bbi developer\b",
        r"\bbusiness intelligence\b", r"\bproduct analyst\b"
    ],
    "Mobile Developer": [
        r"\bmobile\b", r"\bandroid\b", r"\bios\b", r"\bflutter\b",
        r"\breact[- ]?native\b", r"\bswiftui\b"
    ]
}

# Canonical City Taxonomy
CITY_TAXONOMY = {
    "Bengaluru": [r"\bbengaluru\b", r"\bbangalore\b", r"\bblr\b"],
    "Hyderabad": [r"\bhyderabad\b", r"\bsecunderabad\b", r"\bcyberabad\b"],
    "Pune": [r"\bpune\b"],
    "Delhi NCR": [r"\bdelhi\b", r"\bnew delhi\b", r"\bgurgaon\b", r"\bgurugram\b", r"\bnoida\b", r"\bgreater noida\b", r"\bncr\b"],
    "Mumbai": [r"\bmumbai\b", r"\bbombay\b", r"\bnavi mumbai\b", r"\bthane\b"],
    "Chennai": [r"\bchennai\b", r"\bmadras\b"],
    "Kolkata": [r"\bkolkata\b", r"\bcalcutta\b"],
    "Ahmedabad": [r"\bahmedabad\b", r"\bahmadabad\b", r"\bgandhinagar\b"],
    "Kochi": [r"\bkochi\b", r"\bcochin\b", r"\bernakulam\b"],
    "Jaipur": [r"\bjaipur\b"]
}

def normalise_role(title: str) -> str:
    if not isinstance(title, str) or not title.strip():
        return None
    title_lower = title.lower()
    
    # Priority check for Full Stack before Frontend/Backend
    if re.search(r"\bfull[- ]?stack\b", title_lower):
        return "Full Stack Developer"

    for canonical, patterns in ROLE_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, title_lower):
                return canonical
    return None

def normalise_city(location: str) -> str:
    if not isinstance(location, str) or not location.strip():
        return None
    loc_lower = location.lower()
    for canonical, patterns in CITY_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, loc_lower):
                return canonical
    return None

def parse_experience(exp_str: str) -> tuple[float, float]:
    """
    Parses experience strings like:
    '0-1 years', '1 - 3 yrs', 'Fresher', '5+ years', '3 to 5 years', 'Junior'
    Returns (min_exp, max_exp) in years.
    """
    if not isinstance(exp_str, str) or not exp_str.strip():
        return (0.0, 2.0)
    
    s = exp_str.strip().lower()
    if "fresher" in s or "entry level" in s:
        return (0.0, 1.0)
    if "junior" in s:
        return (1.0, 3.0)
    if "mid" in s:
        return (3.0, 6.0)
    if "senior" in s:
        return (5.0, 9.0)
    if "lead" in s or "architect" in s:
        return (8.0, 14.0)

    # Check for range: 'X-Y' or 'X to Y'
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", s)
    if range_match:
        mn = float(range_match.group(1))
        mx = float(range_match.group(2))
        return (mn, mx)
        
    # Check for 'X+ years'
    plus_match = re.search(r"(\d+(?:\.\d+)?)\s*\+", s)
    if plus_match:
        mn = float(plus_match.group(1))
        return (mn, mn + 3.0)
        
    # Single number
    num_match = re.search(r"(\d+(?:\.\d+)?)", s)
    if num_match:
        val = float(num_match.group(1))
        return (val, val + 2.0)

    return (0.0, 2.0)

def parse_salary_inr(raw_sal: str) -> tuple[int | None, int | None, int | None]:
    """
    Parses salary strings into annual INR:
    - '8 - 12 LPA' -> (800000, 1200000, 1000000)
    - '14 LPA' -> (1400000, 1400000, 1400000)
    - '₹800,000 - ₹1,200,000' -> (800000, 1200000, 1000000)
    - '₹65,000 per month' -> (780000, 780000, 780000)
    Returns (salary_min_inr, salary_max_inr, salary_median_inr)
    """
    if not isinstance(raw_sal, str) or not raw_sal.strip():
        return (None, None, None)
        
    s = raw_sal.replace(",", "").strip()
    
    # 1. LPA format: e.g. "8 - 12 LPA", "8.5 LPA"
    if re.search(r"lpa|lacs?|lakhs?", s, re.IGNORECASE):
        # Range in LPA
        lpa_range = re.findall(r"(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)?\s*(?:lpa|lac|lakh)", s, re.IGNORECASE)
        if lpa_range:
            g1, g2 = lpa_range[0]
            val1 = float(g1)
            val2 = float(g2) if g2 else val1
            min_inr = int(min(val1, val2) * 100000)
            max_inr = int(max(val1, val2) * 100000)
            med_inr = int((min_inr + max_inr) / 2)
            return (min_inr, max_inr, med_inr)

    # 2. Monthly format: e.g. "₹65000 / month", "50000 per month"
    if re.search(r"month|p\.?m\.?", s, re.IGNORECASE):
        nums = re.findall(r"\b(\d{4,8})\b", s)
        if nums:
            monthly = float(nums[0])
            annual = int(monthly * 12)
            return (annual, annual, annual)

    # 3. Direct annual INR range: e.g. "800000 - 1200000", "₹1500000"
    nums = [int(n) for n in re.findall(r"\b(\d{5,9})\b", s)]
    if len(nums) >= 2:
        min_inr = min(nums[0], nums[1])
        max_inr = max(nums[0], nums[1])
        med_inr = int((min_inr + max_inr) / 2)
        return (min_inr, max_inr, med_inr)
    elif len(nums) == 1:
        val = nums[0]
        return (val, val, val)

    return (None, None, None)

def clean_data(raw_csv_path: str = "data/raw/jobs_raw.csv", output_csv_path: str = "data/processed/jobs_cleaned.csv") -> pd.DataFrame:
    logger.info("Starting data cleaning pipeline...")
    
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Source file not found at: {raw_csv_path}")

    # Step 0: Load data
    df = pd.read_csv(raw_csv_path)
    total_raw = len(df)
    logger.info(f"[Step 0] Loaded raw postings: {total_raw} rows")

    # Step 1: Handle missing core values
    df_step1 = df.dropna(subset=["title", "company", "location", "description"]).copy()
    logger.info(f"[Step 1] Dropped null core fields -> {len(df_step1)} rows kept ({total_raw - len(df_step1)} dropped)")

    # Step 2: Deduplication
    df_step2 = df_step1.drop_duplicates(subset=["title", "company", "location", "description"]).copy()
    logger.info(f"[Step 2] Deduplicated postings -> {len(df_step2)} rows kept ({len(df_step1) - len(df_step2)} duplicates dropped)")

    # Step 3: Role normalisation
    df_step2["role"] = df_step2["title"].apply(normalise_role)
    df_step3 = df_step2.dropna(subset=["role"]).copy()
    logger.info(f"[Step 3] Role title normalisation -> {len(df_step3)} rows matched taxonomy ({len(df_step2) - len(df_step3)} unmapped titles dropped)")

    # Step 4: City normalisation
    df_step3["city"] = df_step3["location"].apply(normalise_city)
    df_step4 = df_step3.dropna(subset=["city"]).copy()
    logger.info(f"[Step 4] City normalisation -> {len(df_step4)} rows matched Indian city taxonomy ({len(df_step3) - len(df_step4)} dropped)")

    # Step 5: Experience parsing
    exp_parsed = df_step4["experience"].apply(parse_experience)
    df_step4["min_exp"] = [p[0] for p in exp_parsed]
    df_step4["max_exp"] = [p[1] for p in exp_parsed]
    logger.info(f"[Step 5] Experience parsed for {len(df_step4)} rows")

    # Step 6: Salary parsing to annual INR
    salary_parsed = df_step4["salary"].apply(parse_salary_inr)
    df_step4["salary_min_inr"] = [p[0] for p in salary_parsed]
    df_step4["salary_max_inr"] = [p[1] for p in salary_parsed]
    df_step4["salary_median_inr"] = [p[2] for p in salary_parsed]
    
    n_with_salary = df_step4["salary_median_inr"].notna().sum()
    logger.info(f"[Step 6] Salary parsed: {n_with_salary} rows with valid salary ({len(df_step4) - n_with_salary} missing/disclosed)")

    # Final selection of columns
    cleaned_df = df_step4[[
        "job_id", "title", "role", "company", "location", "city",
        "min_exp", "max_exp", "salary_min_inr", "salary_max_inr", "salary_median_inr",
        "description", "posted_date"
    ]].copy()

    # Step 7: Export
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    cleaned_df.to_csv(output_csv_path, index=False, encoding="utf-8")
    logger.info(f"[Step 7] Cleaned dataset saved to '{output_csv_path}' -> {len(cleaned_df)} final rows.")
    
    return cleaned_df

if __name__ == "__main__":
    clean_data()
