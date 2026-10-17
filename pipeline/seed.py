"""
pipeline/seed.py

Generates a realistic synthetic job-market dataset with:
- 5,500+ postings
- 8 canonical job roles (with raw title variations)
- 10 Indian cities (with raw naming variations: Bangalore/Bengaluru, Gurgaon/Delhi NCR, etc.)
- 110+ well-known tech employers in India
- Realistic salary correlated with experience band, role, and city tier
- Realistic experience bands (0-1 yrs freshers, 1-3 yrs juniors, 3-6 yrs mid, 6-10 yrs senior, 10+ yrs lead)
- Skills strongly correlated by role
- Realistic messiness: duplicate postings, diverse salary formats (LPA, monthly, INR strings, nulls)
- Uncleaned text descriptions mentioning skills, aliases, and tricky tokens (Go, R, C++, Node.js)
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

# Set seed for reproducible distribution
random.seed(42)

COMPANIES = [
    # Top Product / Startups / Decacorns
    "Flipkart", "Swiggy", "Zomato", "Razorpay", "Zepto", "CRED", "PhonePe", "Paytm", "Meesho",
    "Zerodha", "Groww", "InMobi", "Postman", "BrowserStack", "Hasura", "Juspay", "Urban Company",
    "Nykaa", "MakeMyTrip", "Freshworks", "Zoho", "Licious", "Cars24", "Delhivery", "Policybazaar",
    "Blinkit", "Ola", "PharmEasy", "Dream11", "KreditBee", "Spinny", "Upstox", "Acko", "CoinSwitch",
    "Pine Labs", "Classplus", "Darwinbox", "Lendingkart", "LeadSquared", "Shiprocket", "Shadowfax",
    # Global Tech MNCs in India
    "Google India", "Microsoft India", "Amazon India", "Apple India", "Meta India", "Adobe India",
    "Salesforce India", "Uber India", "Atlassian India", "Intuit India", "Walmart Global Tech",
    "Oracle India", "Cisco Systems", "SAP Labs India", "PayPal India", "LinkedIn India", "VMware",
    "ServiceNow", "Qualcomm India", "NVIDIA India", "Intel India", "AMD India", "Twilio",
    "Stripe India", "Airbnb India", "Target India", "Tesco Bengaluru", "Target Technology",
    # Global Banks / FinTech Capability Centres
    "Goldman Sachs", "Morgan Stanley", "JPMorgan Chase", "Barclays", "Deutsche Bank", "Wells Fargo",
    "BNP Paribas", "Standard Chartered", "HSBC India", "Citi", "American Express", "UBS India",
    "Fidelity Investments", "Bank of America", "Mastercard", "Visa India", "Societe Generale",
    # IT Services & Consulting Majors
    "Tata Consultancy Services", "Infosys", "Wipro", "HCLTech", "Tech Mahindra", "LTIMindtree",
    "Cognizant", "Capgemini India", "Accenture India", "Deloitte India", "PwC India", "EY India",
    "KPMG India", "Persistent Systems", "Mphasis", "Coforge", "Birlasoft", "KPIT Technologies",
    "Hexaware Technologies", "Sonata Software", "Tata Elxsi", "Cyient", "Zensar Technologies"
]

ROLES_METADATA = {
    "Backend Developer": {
        "titles": [
            "Backend Developer", "Senior Backend Engineer", "Junior Backend Dev", "Backend Software Engineer",
            "Software Development Engineer - Backend", "Python Backend Developer", "Java Backend Engineer",
            "Go Backend Engineer", "Node.js Backend Developer", "API Engineer - Backend"
        ],
        "core_skills": ["Python", "Java", "Go", "FastAPI", "Django", "Spring Boot", "Node.js", "PostgreSQL", "Redis", "Docker", "REST API", "Git", "SQL"],
        "bonus_skills": ["AWS", "Kubernetes", "Microservices", "Apache Kafka", "RabbitMQ", "GraphQL", "gRPC", "Linux", "CI/CD", "System Design"],
        "base_salary_fresh": 7.5,
        "salary_growth_rate": 2.4
    },
    "Frontend Developer": {
        "titles": [
            "Frontend Developer", "Frontend Engineer", "React.js Developer", "UI Engineer",
            "Senior Frontend Engineer", "Junior Frontend Developer", "Web Developer (Frontend)",
            "Software Engineer - Frontend", "Next.js Developer"
        ],
        "core_skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Tailwind CSS", "Redux", "Git"],
        "bonus_skills": ["Next.js", "Vue.js", "Webpack", "Vite", "Jest", "GraphQL", "REST API", "Sass", "Responsive Design", "Zustand"],
        "base_salary_fresh": 6.5,
        "salary_growth_rate": 2.2
    },
    "Full Stack Developer": {
        "titles": [
            "Full Stack Developer", "Fullstack Engineer", "Senior Full Stack Engineer", "MERN Stack Developer",
            "Full Stack Software Engineer", "Python/React Full Stack Developer", "Java Full Stack Developer",
            "Software Development Engineer - Fullstack"
        ],
        "core_skills": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "PostgreSQL", "MongoDB", "REST API", "Git", "HTML", "CSS"],
        "bonus_skills": ["Docker", "AWS", "Next.js", "Tailwind CSS", "Redis", "Express.js", "GraphQL", "FastAPI", "CI/CD", "System Design"],
        "base_salary_fresh": 7.0,
        "salary_growth_rate": 2.5
    },
    "Data Engineer": {
        "titles": [
            "Data Engineer", "Senior Data Engineer", "Big Data Engineer", "Data Pipeline Engineer",
            "ETL Developer", "Cloud Data Engineer", "Analytics Engineer", "Data Infrastructure Engineer"
        ],
        "core_skills": ["Python", "SQL", "Apache Spark", "Apache Airflow", "PostgreSQL", "Docker", "Git", "ETL", "Data Warehousing"],
        "bonus_skills": ["AWS", "Snowflake", "BigQuery", "Apache Kafka", "dbt", "Hadoop", "Databricks", "Linux", "PySpark", "Scala"],
        "base_salary_fresh": 8.0,
        "salary_growth_rate": 2.6
    },
    "Machine Learning Engineer": {
        "titles": [
            "Machine Learning Engineer", "Senior ML Engineer", "AI/ML Engineer", "Data Scientist - ML",
            "Deep Learning Engineer", "Applied AI Scientist", "NLP Engineer", "Computer Vision Engineer"
        ],
        "core_skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-learn", "Git", "SQL"],
        "bonus_skills": ["NLP", "Computer Vision", "Docker", "AWS", "FastAPI", "Hugging Face", "LangChain", "Large Language Models", "RAG", "MLOps"],
        "base_salary_fresh": 9.0,
        "salary_growth_rate": 2.8
    },
    "DevOps Engineer": {
        "titles": [
            "DevOps Engineer", "Senior DevOps Engineer", "Cloud & DevOps Engineer", "Site Reliability Engineer",
            "SRE / DevOps Specialist", "Infrastructure Engineer", "Platform Engineer", "Kubernetes Engineer"
        ],
        "core_skills": ["Docker", "Kubernetes", "Linux", "AWS", "CI/CD", "Terraform", "Git", "Bash", "Shell Scripting"],
        "bonus_skills": ["Jenkins", "GitHub Actions", "Ansible", "Prometheus", "Grafana", "Python", "Go", "Helm", "Azure", "Google Cloud", "Nginx"],
        "base_salary_fresh": 8.0,
        "salary_growth_rate": 2.6
    },
    "Data Analyst": {
        "titles": [
            "Data Analyst", "Senior Data Analyst", "Business Intelligence Analyst", "Product Analyst",
            "Marketing Data Analyst", "Operations Data Analyst", "BI Developer - Tableau/PowerBI"
        ],
        "core_skills": ["SQL", "Python", "Tableau", "Power BI", "Pandas", "Data Warehousing"],
        "bonus_skills": ["R", "Excel", "Data Modeling", "ETL", "PostgreSQL", "BigQuery", "Snowflake", "Statistics", "Git"],
        "base_salary_fresh": 5.5,
        "salary_growth_rate": 1.9
    },
    "Mobile Developer": {
        "titles": [
            "Mobile Developer", "React Native Developer", "Flutter Developer", "Android Developer",
            "iOS Developer", "Senior Mobile App Engineer", "Mobile Software Engineer", "Cross-Platform Mobile Dev"
        ],
        "core_skills": ["React Native", "Flutter", "JavaScript", "TypeScript", "Kotlin", "Swift", "Git", "REST API"],
        "bonus_skills": ["Android Development", "iOS Development", "SwiftUI", "Jetpack Compose", "Redux", "GraphQL", "Firebase", "CI/CD"],
        "base_salary_fresh": 6.5,
        "salary_growth_rate": 2.2
    }
}

# 10 Indian cities with realistic raw variations
CITIES = {
    "Bengaluru": {
        "variations": ["Bengaluru", "Bangalore", "Bengaluru/Bangalore", "Bangalore Urban", "Bengaluru, Karnataka"],
        "tier_multiplier": 1.25,
        "weight": 35
    },
    "Hyderabad": {
        "variations": ["Hyderabad", "Hyderabad/Secunderabad", "Hyderabad, Telangana", "Cyberabad"],
        "tier_multiplier": 1.15,
        "weight": 18
    },
    "Pune": {
        "variations": ["Pune", "Pune, Maharashtra", "Pune City"],
        "tier_multiplier": 1.10,
        "weight": 14
    },
    "Delhi NCR": {
        "variations": ["Delhi NCR", "Delhi", "New Delhi", "Gurgaon", "Gurugram", "Noida", "Greater Noida"],
        "tier_multiplier": 1.18,
        "weight": 16
    },
    "Mumbai": {
        "variations": ["Mumbai", "Bombay", "Navi Mumbai", "Mumbai Suburban", "Thane, Mumbai"],
        "tier_multiplier": 1.20,
        "weight": 10
    },
    "Chennai": {
        "variations": ["Chennai", "Madras", "Chennai, Tamil Nadu"],
        "tier_multiplier": 1.05,
        "weight": 8
    },
    "Kolkata": {
        "variations": ["Kolkata", "Calcutta", "Kolkata, West Bengal"],
        "tier_multiplier": 0.90,
        "weight": 4
    },
    "Ahmedabad": {
        "variations": ["Ahmedabad", "Ahmadabad", "Gandhinagar/Ahmedabad"],
        "tier_multiplier": 0.88,
        "weight": 3
    },
    "Kochi": {
        "variations": ["Kochi", "Cochin", "Ernakulam/Kochi"],
        "tier_multiplier": 0.85,
        "weight": 2
    },
    "Jaipur": {
        "variations": ["Jaipur", "Jaipur, Rajasthan"],
        "tier_multiplier": 0.82,
        "weight": 2
    }
}

EXPERIENCE_LEVELS = [
    {"label": "0-1 years", "min_exp": 0, "max_exp": 1, "raw": ["0-1 years", "0 - 1 yrs", "Fresher", "Entry Level", "0 to 1 year"], "weight": 20},
    {"label": "1-3 years", "min_exp": 1, "max_exp": 3, "raw": ["1-3 years", "1 - 3 yrs", "1 to 3 years", "2+ years", "Junior"], "weight": 35},
    {"label": "3-6 years", "min_exp": 3, "max_exp": 6, "raw": ["3-6 years", "3 to 6 yrs", "4+ years", "Mid-level", "3 - 5 years"], "weight": 28},
    {"label": "6-10 years", "min_exp": 6, "max_exp": 10, "raw": ["6-10 years", "6 - 10 yrs", "7+ years", "Senior", "6 to 8 years"], "weight": 13},
    {"label": "10+ years", "min_exp": 10, "max_exp": 15, "raw": ["10+ years", "10 - 15 yrs", "Lead / Architect", "12+ years"], "weight": 4}
]

def generate_salary_and_raw_string(base_fresh, growth_rate, exp_val, tier_mult, company):
    # Tier multiplier on base
    is_top_product = company in [
        "Google India", "Microsoft India", "Amazon India", "Flipkart", "CRED", "Uber India",
        "Atlassian India", "Goldman Sachs", "Morgan Stanley", "Salesforce India"
    ]
    is_it_service = company in [
        "Tata Consultancy Services", "Infosys", "Wipro", "HCLTech", "Tech Mahindra", "Cognizant"
    ]
    
    comp_factor = 1.45 if is_top_product else (0.78 if is_it_service else 1.05)
    
    # Calculate median annual salary in LPA
    mean_lpa = (base_fresh + (exp_val * growth_rate)) * tier_mult * comp_factor
    # Random variation around mean
    actual_lpa = max(3.0, round(random.gauss(mean_lpa, mean_lpa * 0.15), 1))
    
    # Min - Max range around actual
    spread = round(actual_lpa * random.uniform(0.12, 0.28), 1)
    min_lpa = round(max(2.5, actual_lpa - spread / 2), 1)
    max_lpa = round(actual_lpa + spread / 2, 1)
    
    # Randomly decide format for raw salary field:
    fmt_choice = random.random()
    if fmt_choice < 0.10:
        # Missing salary (10% of postings don't disclose salary)
        raw_salary = ""
    elif fmt_choice < 0.45:
        # Range in LPA format: "8 - 12 LPA"
        raw_salary = f"{min_lpa} - {max_lpa} LPA"
    elif fmt_choice < 0.65:
        # Single LPA: "14 LPA"
        raw_salary = f"{actual_lpa} LPA"
    elif fmt_choice < 0.80:
        # INR exact numbers: "800000 - 1200000 INR"
        min_inr = int(min_lpa * 100000)
        max_inr = int(max_lpa * 100000)
        raw_salary = f"₹{min_inr:,} - ₹{max_inr:,}"
    elif fmt_choice < 0.90:
        # Single INR string: "₹1,500,000 per annum"
        inr_val = int(actual_lpa * 100000)
        raw_salary = f"₹{inr_val:,} per annum"
    else:
        # Monthly salary: "₹65,000 / month"
        monthly = int((actual_lpa * 100000) / 12)
        raw_salary = f"₹{monthly:,} per month"
        
    return min_lpa, max_lpa, raw_salary

def build_job_description(role_name, title, company, city, skills_list, exp_raw):
    intro_sentences = [
        f"{company} is hiring a talented {title} to join our high-growth engineering team in {city}.",
            f"We are looking for an experienced and ambitious {title} at {company} to build scalable systems.",
        f"Join {company} as a {title}! You will design and deploy mission-critical features.",
        f"At {company}, we are transforming the tech landscape and seeking a passionate {title}."
    ]
    
    # Tricky token inclusions (Go, R, C++, Node.js) in context to ensure clean testing
    extras = []
    if "Go" in skills_list and random.random() < 0.4:
        extras.append("The service is written in Go and high-performance microservices. Candidate must go above and beyond.")
    if "R" in skills_list and random.random() < 0.4:
        extras.append("Experience with R programming for statistical computation is a huge plus.")
    if "C++" in skills_list and random.random() < 0.4:
        extras.append("Low-latency components require solid knowledge of C++ and memory safety.")
    if "Node.js" in skills_list and random.random() < 0.4:
        extras.append("Backend services leverage Node.js alongside modern asynchronous paradigms.")
        
    skills_text = ", ".join(skills_list)
    desc = (
        f"{random.choice(intro_sentences)}\n\n"
        f"Key Requirements & Experience:\n"
        f"- Experience Level: {exp_raw}\n"
        f"- Hands-on proficiency with: {skills_text}.\n"
        f"- Strong debugging skills, clean code principles, and collaborative mindset.\n"
        f"{' '.join(extras)}\n\n"
        f"Responsibilities:\n"
        f"- Architect, implement, and maintain scalable applications.\n"
        f"- Collaborate with cross-functional teams across engineering, QA, and product.\n"
        f"- Participate in code reviews, technical discussions, and engineering milestones."
    )
    return desc

def generate_dataset(n_target=5600):
    postings = []
    
    # Flatten city choices by weight
    city_keys = list(CITIES.keys())
    city_weights = [CITIES[c]["weight"] for c in city_keys]
    
    # Roles list
    role_names = list(ROLES_METADATA.keys())
    
    # Experience weights
    exp_weights = [e["weight"] for e in EXPERIENCE_LEVELS]
    
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(1, n_target + 1):
        job_id = f"JOB-{i:06d}"
        role_canonical = random.choice(role_names)
        role_meta = ROLES_METADATA[role_canonical]
        raw_title = random.choice(role_meta["titles"])
        
        company = random.choice(COMPANIES)
        city_canonical = random.choices(city_keys, weights=city_weights, k=1)[0]
        city_meta = CITIES[city_canonical]
        raw_city = random.choice(city_meta["variations"])
        
        exp_meta = random.choices(EXPERIENCE_LEVELS, weights=exp_weights, k=1)[0]
        raw_exp = random.choice(exp_meta["raw"])
        avg_exp = (exp_meta["min_exp"] + exp_meta["max_exp"]) / 2.0
        
        # Salary
        min_lpa, max_lpa, raw_salary = generate_salary_and_raw_string(
            role_meta["base_salary_fresh"],
            role_meta["salary_growth_rate"],
            avg_exp,
            city_meta["tier_multiplier"],
            company
        )
        
        # Correlated skills selection (pick 4-7 core skills and 2-4 bonus skills)
        n_core = min(len(role_meta["core_skills"]), random.randint(4, 7))
        n_bonus = min(len(role_meta["bonus_skills"]), random.randint(2, 4))
        selected_skills = random.sample(role_meta["core_skills"], n_core) + random.sample(role_meta["bonus_skills"], n_bonus)
        
        # Description
        description = build_job_description(role_canonical, raw_title, company, raw_city, selected_skills, raw_exp)
        
        # Posted date
        days_offset = random.randint(0, 90)
        posted_at = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        postings.append({
            "job_id": job_id,
            "raw_title": raw_title,
            "canonical_role": role_canonical,
            "company": company,
            "raw_location": raw_city,
            "canonical_city": city_canonical,
            "raw_experience": raw_exp,
            "min_exp": exp_meta["min_exp"],
            "max_exp": exp_meta["max_exp"],
            "raw_salary": raw_salary,
            "min_salary_lpa": min_lpa if raw_salary else None,
            "max_salary_lpa": max_lpa if raw_salary else None,
            "skills": selected_skills,
            "description": description,
            "posted_date": posted_at
        })

    # Add ~4% realistic duplicate postings (same company, title, raw_location, raw_salary)
    n_dupes = int(len(postings) * 0.04)
    dupe_sources = random.sample(postings, n_dupes)
    for idx, d in enumerate(dupe_sources, start=len(postings) + 1):
        copy_d = dict(d)
        copy_d["job_id"] = f"JOB-{idx:06d}"
        postings.append(copy_d)

    random.shuffle(postings)
    return postings

def save_dataset(postings, raw_dir="data/raw"):
    os.makedirs(raw_dir, exist_ok=True)
    csv_path = os.path.join(raw_dir, "jobs_raw.csv")
    json_path = os.path.join(raw_dir, "jobs_raw.json")
    
    # Save CSV
    fieldnames = [
        "job_id", "title", "company", "location", "experience", "salary",
        "description", "posted_date"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in postings:
            writer.writerow({
                "job_id": p["job_id"],
                "title": p["raw_title"],
                "company": p["company"],
                "location": p["raw_location"],
                "experience": p["raw_experience"],
                "salary": p["raw_salary"],
                "description": p["description"],
                "posted_date": p["posted_date"]
            })
            
    # Save JSON summary / sample
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(postings[:50], f, indent=2)
        
    print(f"Generated {len(postings)} raw job postings in '{csv_path}' and sample in '{json_path}'.")

if __name__ == "__main__":
    data = generate_dataset(5600)
    save_dataset(data)
