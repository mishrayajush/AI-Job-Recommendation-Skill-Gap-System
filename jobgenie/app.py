import re
import os
import random
import pdfplumber
import pandas as pd
from flask import Flask, render_template, request, jsonify
from io import BytesIO

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "jobs.csv")

try:
    jobs_df = pd.read_csv(CSV_PATH, encoding="utf-8")
    jobs_df.columns = jobs_df.columns.str.lower().str.strip()
    before = len(jobs_df)
    jobs_df = jobs_df.drop_duplicates(
        subset=["job_title", "company", "location"], keep="first").reset_index(drop=True)
    print(
        f"Loaded {len(jobs_df)} jobs (removed {before - len(jobs_df)} duplicates).")
except FileNotFoundError:
    print(f"jobs.csv not found at {CSV_PATH}")
    jobs_df = pd.DataFrame()
except Exception as e:
    print(f"Error loading jobs.csv: {e}")
    jobs_df = pd.DataFrame()

SKILLS = [
    "python", "java", "c++", "c", "r", "perl", "scala", "go", "rust", "kotlin", "swift",
    "typescript", "javascript", "ruby", "php", "matlab", "bash", "shell scripting",
    "sql", "ms sql", "mysql", "postgresql", "sqlite", "nosql", "mongodb", "redis",
    "cassandra", "oracle", "dynamodb", "firebase", "elasticsearch",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "data science", "data analysis", "eda", "nlp", "natural language processing",
    "computer vision", "neural network", "neural networks", "reinforcement learning",
    "scikit-learn", "sklearn", "xgboost", "lightgbm", "random forest",
    "predictive modeling", "feature engineering", "model deployment",
    "statistics", "statistical analysis", "hypothesis testing", "regression",
    "classification", "clustering", "time series", "data mining", "big data",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "scipy",
    "power bi", "tableau", "qlikview", "looker", "google data studio",
    "excel", "ms excel", "vba", "pivot table", "vlookup", "advanced excel",
    "jupyter", "jupyter notebook", "google colab",
    "aws", "azure", "gcp", "google cloud", "devops", "terraform", "ansible",
    "docker", "kubernetes", "ci/cd", "jenkins", "git", "github", "gitlab",
    "linux", "unix", "windows server",
    "html", "css", "react", "angular", "vue", "javascript",
    "node", "nodejs", "flask", "django", "fastapi", "spring", "spring boot",
    "rest api", "graphql", "microservices",
    "selenium", "software testing", "automation testing", "api testing",
    "unit testing", "pytest", "jest",
    "sap", "tally", "gst", "accounting", "taxation", "payroll", "audit",
    "finance", "financial modeling", "risk management", "financial analysis",
    "bookkeeping", "balance sheet", "tds", "erp",
    "networking", "network security", "cybersecurity", "ethical hacking",
    "firewall", "tcp/ip", "ccna",
    "project management", "scrum", "agile", "sdlc", "mis",
    "data entry", "ms word", "powerpoint", "ms office", "communication skills",
    "troubleshooting", "technical support", "streamlit",
    "raspberry pi", "arduino", "iot", "embedded systems",
    "digital marketing", "seo", "sem", "social media", "crm", "salesforce",
    "recruitment", "talent acquisition", "human resources",
]

SKILL_ALIASES = {
    "python programming": "python", "python3": "python", "python 3": "python", "core python": "python", "python based": "python", "python language": "python",
    "machine-learning": "machine learning", "machinelearning": "machine learning", "ml": "machine learning", "machine learning models": "machine learning", "machine learning algorithms": "machine learning",
    "deep-learning": "deep learning", "deep learning models": "deep learning", "deep learning algorithms": "deep learning", "deep neural networks": "deep learning", "dnn": "deep learning", "dl": "deep learning",
    "natural language processing": "nlp", "natural-language-processing": "nlp",
    "computer-vision": "computer vision",
    "artificial intelligence": "machine learning", "ai": "machine learning",
    "sci-kit learn": "scikit-learn", "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
    "ms excel": "excel", "microsoft excel": "excel", "advanced excel": "excel", "msexcel": "excel", "excel based": "excel", "excel based reporting": "excel", "excel reporting": "excel",
    "sql server": "sql", "ms sql server": "sql", "t-sql": "sql", "tsql": "sql", "pl/sql": "sql", "plsql": "sql",
    "power-bi": "power bi", "powerbi": "power bi",
    "node.js": "nodejs", "node js": "nodejs",
    "react.js": "react", "reactjs": "react",
    "vue.js": "vue", "vuejs": "vue",
    "git hub": "github",
    "google cloud platform": "gcp", "google cloud": "gcp",
    "amazon web services": "aws",
    "rest": "rest api", "restful": "rest api", "restful api": "rest api", "restful apis": "rest api",
    "spring boot": "spring", "mysql database": "mysql",
    "postgres": "postgresql", "mongo db": "mongodb", "mongo": "mongodb",
    "tensor flow": "tensorflow", "py torch": "pytorch",
    "java programming": "java", "c plus plus": "c++",
    "javascript programming": "javascript", "js": "javascript",
    "html5": "html", "css3": "css",
    "devops engineer": "devops",
    "data analytics": "data analysis", "data visualisation": "data analysis", "data visualization": "data analysis",
    "business intelligence": "power bi", "tableau desktop": "tableau",
    "ms word": "ms office", "microsoft word": "ms office", "microsoft office": "ms office", "ms powerpoint": "powerpoint",
    "statistical analysis": "statistics", "probability and statistics": "statistics", "stats": "statistics",
    "human resource": "human resources", "hr management": "human resources",
}

ALL_SECTION_HEADINGS = [
    "experience", "work experience", "professional experience", "employment history",
    "professional background", "career history", "career summary", "industry work",
    "work history", "job history", "past experience", "relevant experience",
    "education", "academic background", "qualifications", "academic qualifications",
    "educational background", "academic history",
    "projects", "project experience", "personal projects", "academic projects", "key projects", "project work",
    "certifications", "certificates", "achievements", "awards",
    "summary", "objective", "profile", "about", "about me",
    "career objective", "professional summary", "personal statement",
    "hobbies", "interests", "references", "languages",
    "technical skills", "tech skills", "key skills", "core skills",
    "skills", "skills & expertise", "core competencies",
    "tools & technologies", "expertise", "internship", "internships",
    "training", "volunteer", "publications", "research"
]

SKILL_SECTION_HEADINGS = [
    "technical skills", "tech skills", "key skills", "core skills",
    "skills", "skills & expertise", "skills and expertise",
    "core competencies", "competencies", "tools & technologies",
    "tools and technologies", "technologies", "expertise",
    "programming languages", "languages & tools", "it skills",
    "software skills", "professional skills", "areas of expertise", "skill set", "skillset"
]

DOMAIN_PROFILES = {
    "data_science": {
        "label": "Data Science / ML / AI",
        "resume_keywords": ["data science", "machine learning", "deep learning", "artificial intelligence", "data scientist", "ml engineer", "data analyst", "bsc data science", "b.sc data science", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "eda", "nlp", "computer vision", "neural network", "statistics", "data mining", "predictive modeling", "big data", "keras", "data analysis", "business analyst", "business intelligence", "analytics"],
        "job_keywords": ["data scientist", "machine learning", "ml engineer", "data analyst", "deep learning", "ai engineer", "data engineer", "business analyst", "python developer", "data science", "nlp", "computer vision", "analytics", "bi analyst", "research analyst", "statistician", "data", "analyst", "science", "intelligence", "ml", "ai"]
    },
    "software_dev": {
        "label": "Software Development / IT",
        "resume_keywords": ["software engineer", "software developer", "backend", "frontend", "full stack", "web developer", "b.tech", "btech", "b.e", "be computer", "computer science", "information technology", "bca", "mca", "java", "react", "angular", "node", "django", "spring", "microservices", "rest api", "cloud", "devops", "docker", "kubernetes"],
        "job_keywords": ["software engineer", "software developer", "backend developer", "frontend developer", "full stack", "web developer", "java developer", "python developer", "react developer", "node developer", "devops", "cloud engineer", "mobile developer", "android", "ios", "developer", "programmer", "engineer", "it"]
    },
    "finance_commerce": {
        "label": "Finance / Commerce / Accounting",
        "resume_keywords": ["bcom", "b.com", "mcom", "m.com", "bms", "bba", "mba finance", "chartered accountant", "ca", "cma", "cs", "commerce", "accounting", "taxation", "gst", "tds", "tally", "sap", "financial analysis", "audit", "bookkeeping", "balance sheet", "income tax", "financial modeling", "investment", "banking"],
        "job_keywords": ["accountant", "finance", "accounting", "tax", "audit", "tally", "gst", "financial analyst", "banking", "investment", "ca", "commerce", "bookkeeping", "payroll", "billing", "cost accountant", "credit analyst", "equity", "treasury", "risk analyst", "executive"]
    },
    "marketing_sales": {
        "label": "Marketing / Sales / Business",
        "resume_keywords": ["marketing", "digital marketing", "sales", "business development", "bba", "mba marketing", "social media", "seo", "sem", "content marketing", "brand management", "crm", "lead generation", "market research", "advertising", "public relations"],
        "job_keywords": ["marketing", "sales", "business development", "digital marketing", "seo", "social media", "brand manager", "content writer", "marketing executive", "sales executive", "growth hacker", "product marketing", "advertising", "media planner", "crm"]
    },
    "hr_admin": {
        "label": "HR / Administration",
        "resume_keywords": ["human resources", "hr", "talent acquisition", "recruitment", "payroll", "employee relations", "performance management", "bba hr", "mba hr", "organizational behavior", "labor law", "office administration", "executive assistant"],
        "job_keywords": ["hr", "human resources", "recruiter", "talent acquisition", "payroll", "hr executive", "hr manager", "admin", "office manager", "hr generalist", "recruitment", "employee engagement"]
    },
    "data_entry_ops": {
        "label": "Data Entry / Operations",
        "resume_keywords": ["data entry", "back office", "operations", "mis", "mis reporting", "ms excel", "ms office", "typing", "word processing"],
        "job_keywords": ["data entry", "back office", "operations", "excel", "office assistant", "data operator", "clerk", "mis executive"]
    }
}

DOMAIN_ROLE_TERMS = {
    "data_science":     ["analyst", "scientist", "researcher", "data", "ml", "ai", "intelligence"],
    "software_dev":     ["engineer", "developer", "programmer", "architect", "devops", "sre"],
    "finance_commerce": ["accountant", "auditor", "finance", "tax", "billing", "treasurer"],
    "marketing_sales":  ["marketing", "sales", "growth", "brand", "content", "media"],
    "hr_admin":         ["hr", "recruiter", "talent", "payroll", "admin", "office manager"],
    "data_entry_ops":   ["data entry", "operator", "clerk", "back office", "mis"],
}

NOISE_PATTERNS = re.compile(
    r'^(responsibilities|technologies used|tools used|tools|tech stack|'
    r'key responsibilities|duties|tasks|role|roles|overview|description|'
    r'achievements|accomplishments|highlights)[\s:]*$', re.IGNORECASE
)

TIER1 = {"python", "r", "java", "scala", "machine learning", "deep learning", "nlp", "computer vision", "data science", "data analysis", "sql", "tensorflow", "pytorch", "keras", "scikit-learn", "tableau",
         "power bi", "react", "angular", "nodejs", "django", "flask", "fastapi", "spring", "excel", "sap", "tally", "accounting", "financial modeling", "digital marketing", "seo", "human resources", "recruitment"}
TIER2 = {"pandas", "numpy", "matplotlib", "seaborn", "plotly", "scipy", "xgboost", "lightgbm", "random forest", "mongodb",
         "postgresql", "mysql", "redis", "elasticsearch", "aws", "azure", "gcp", "docker", "kubernetes", "git", "github"}


def normalize_skill_text(text):
    t = re.sub(r'[-_]', ' ', text.lower())
    for alias, canonical in SKILL_ALIASES.items():
        t = re.sub(r'\b' + re.escape(alias) + r'\b', canonical, t)
    return t


def _extract_section(text, headings, all_headings):
    """Generic section extractor — returns list of non-empty lines from a named section."""
    lines, inside, result = text.split('\n'), False, []
    for line in lines:
        s, sl = line.strip(), line.strip().lower()
        if any(re.search(r'\b' + re.escape(h) + r'\b', sl) for h in headings):
            inside = True
            continue
        if inside and any(re.search(r'\b' + re.escape(h) + r'\b', sl) for h in all_headings if h not in headings):
            inside = False
        if inside and s:
            result.append(s)
    return result


def detect_domain(resume_text, resume_skills, education, summary):
    combined = normalize_skill_text(
        (resume_text + " " + " ".join(education) + " " + summary).lower())
    skill_str = normalize_skill_text(" ".join(resume_skills).lower())
    scores = {
        d: sum(1 for kw in p["resume_keywords"] if kw.lower() in combined) +
        sum(2 for kw in p["resume_keywords"] if kw.lower() in skill_str)
        for d, p in DOMAIN_PROFILES.items()
    }
    best = max(scores, key=scores.get)
    return ("general", "General Profile") if scores[best] < 1 else (best, DOMAIN_PROFILES[best]["label"])


def job_matches_domain(job_title, job_description, domain):
    if domain == "general":
        return True
    combined, title_lower = (
        job_title + " " + job_description).lower(), job_title.lower()
    if any(kw.lower() in combined for kw in DOMAIN_PROFILES[domain]["job_keywords"]):
        return True
    return any(term in title_lower for term in DOMAIN_ROLE_TERMS.get(domain, []))


def extract_text_from_pdf(file):
    file_bytes = file.read()
    file.seek(0)
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        return "\n".join(t for page in pdf.pages if (t := page.extract_text(x_tolerance=3, y_tolerance=3)))


def extract_personal_info(text):
    info = {"name": "", "email": "", "phone": "",
            "linkedin": "", "github": "", "location": ""}
    for line in text.strip().split('\n')[:6]:
        s = line.strip()
        if s and s == s.upper() and len(s.split()) <= 4:
            continue
        if s and not re.search(r'\d', s) and 2 <= len(s.split()) <= 6:
            if not any(kw in s.lower() for kw in ["resume", "cv", "@", "http", "www", "engineer", "developer", "analyst", "scientist", "manager", "consultant", "designer", "architect", "executive", "specialist"]):
                info["name"] = s.title()
                break

    if m := re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text):
        info["email"] = m.group().lower()
    if m := re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text):
        info["phone"] = m.group().strip()

    if m := re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE):
        info["linkedin"] = "https://" + m.group()
    elif re.search(r'\blinkedin\b', text, re.IGNORECASE):
        info["linkedin"] = "LinkedIn (linked)"

    if m := re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE):
        info["github"] = "https://" + m.group()
    elif re.search(r'\bgithub\b', text, re.IGNORECASE):
        info["github"] = "GitHub (linked)"

    if m := re.search(r'\b([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*,?\s*India)\b', text):
        info["location"] = m.group().strip()
    elif m := re.search(r'\b(Mumbai|Delhi|Bangalore|Bengaluru|Hyderabad|Chennai|Pune|Kolkata|Ahmedabad|Noida|Gurgaon|Gurugram|Jaipur|Surat|Lucknow|Indore|Bhopal|Chandigarh|Coimbatore|Kochi|Nagpur|Vadodara|Visakhapatnam|Patna|Bhubaneswar)(?:[,\s]+(?:Maharashtra|Karnataka|Telangana|Tamil Nadu|Uttar Pradesh|Gujarat|Rajasthan|West Bengal|Madhya Pradesh|Punjab|Kerala|Andhra Pradesh|Bihar|Odisha))?', text, re.IGNORECASE):
        info["location"] = m.group().strip()
    return info


def extract_education(text):
    edu_h = ["education", "academic background", "qualifications"]
    edu_text = " ".join(_extract_section(text, edu_h, ALL_SECTION_HEADINGS))
    degrees = []
    for m in re.finditer(r'(B\.?Sc\.?|B\.?Tech\.?|B\.?E\.?|BCA|BBA|B\.?Com\.?|M\.?Sc\.?|M\.?Tech\.?|MBA|MCA|Ph\.?D\.?|HSC|SSC|12th|10th)\s*(?:in\s+)?([A-Za-z\s&]{2,40}?)(?=\s*[-–|,\d]|$)', edu_text, re.IGNORECASE):
        entry = f"{m.group(1).strip()} in {m.group(2).strip()}".strip()
        if entry not in degrees:
            degrees.append(entry)
    years = re.findall(r'\b(20\d{2})\b', edu_text)
    return degrees[:3], max(years) if years else ""


def extract_work_experience(text):
    exp_h = ["experience", "work experience", "professional experience", "employment history", "professional background", "career history",
             "career summary", "industry work", "work history", "job history", "past experience", "relevant experience", "internship", "internships", "training"]
    lines = _extract_section(text, exp_h, ALL_SECTION_HEADINGS)
    seen, result = set(), []
    for l in lines:
        clean = l.strip()
        if clean in seen or NOISE_PATTERNS.match(clean) or not (8 <= len(clean) <= 150):
            continue
        seen.add(clean)
        result.append(clean)
    return result[:5]


def extract_summary(text):
    sum_h = ["summary", "objective", "profile", "about",
             "career objective", "professional summary"]
    lines = _extract_section(text, sum_h, ALL_SECTION_HEADINGS)
    return " ".join(lines)[:350] if lines else ""


def extract_certifications(text):
    cert_h = ["certifications", "certificates", "certification",
              "courses", "training", "achievements", "awards"]
    certs, seen = [], set()
    for s in _extract_section(text, cert_h, ALL_SECTION_HEADINGS):
        if len(s) <= 4:
            continue
        clean = re.sub(r'^[\-\•\*\>]+\s*', '', s).strip()
        if clean and clean not in seen:
            seen.add(clean)
            certs.append(clean)
    return certs[:5]


def compute_ats_score(personal_info, resume_skills, education, experience, certifications, summary):
    c = sum([5 * bool(personal_info.get(k)) for k in ["name", "email", "phone"]]) + \
        (5 if personal_info.get("linkedin") or personal_info.get("github") else 0)
    breakdown = {
        "Contact Info":   {"score": min(c, 20),                       "max": 20},
        "Skills":         {"score": min(len(resume_skills) * 2, 30),  "max": 30},
        "Education":      {"score": 20 if education else 0,           "max": 20},
        "Experience":     {"score": min(len(experience) * 5, 15),     "max": 15},
        "Certifications": {"score": min(len(certifications) * 3, 10), "max": 10},
        "Summary":        {"score": 5 if summary else 0,              "max": 5},
    }
    return min(sum(v["score"] for v in breakdown.values()), 100), breakdown


def extract_skills_from_resume(text):
    lines, inside, skills_text = text.split('\n'), False, ""
    for line in lines:
        s = line.strip().lower()
        is_skill = any(re.search(r'\b' + re.escape(h) + r'\b', s)
                       for h in SKILL_SECTION_HEADINGS)
        is_end = any(re.search(r'\b' + re.escape(h) + r'\b', s)
                     for h in ALL_SECTION_HEADINGS if h not in SKILL_SECTION_HEADINGS)
        if is_skill:
            inside = True
            continue
        if inside and is_end:
            inside = False
        if inside:
            skills_text += " " + s

    skill_section_norm = normalize_skill_text(skills_text)
    full_text_norm = normalize_skill_text(text.lower())
    search = skill_section_norm if skill_section_norm.strip() else full_text_norm
    found = [sk for sk in SKILLS if re.search(
        r'\b' + re.escape(sk) + r'\b', search)]
    if not found:
        found = [sk for sk in SKILLS if re.search(
            r'\b' + re.escape(sk) + r'\b', full_text_norm)][:20]
    return list(dict.fromkeys(found))


def extract_source_from_url(url):
    u = str(url).lower()
    for src in ["linkedin", "indeed", "naukri"]:
        if src in u:
            return src
    return "other"


def extract_skills_from_text(text):
    t = normalize_skill_text(str(text).lower())
    found = [sk for sk in SKILLS if re.search(
        r'\b' + re.escape(sk) + r'\b', t)]
    found.sort(key=lambda sk: 0 if sk in TIER1 else 1 if sk in TIER2 else 2)
    return ', '.join(found[:10]) if found else 'general'


def extract_experience_from_text(text):
    t = str(text).lower()
    if re.search(r'(5\s*\+?\s*year|senior|lead\s|principal|head\s*of|[678]|10\s*year)', t):
        return '3+'
    if re.search(r'(3\s*\+?\s*year|3\s*[-–to]+\s*5|min(?:imum)?\s*3|at\s*least\s*3|4\s*year)', t):
        return '3+'
    if re.search(r'(2\s*[-–to]+\s*[35]|2\s*\+?\s*year|min(?:imum)?\s*2|at\s*least\s*2)', t):
        return '2-3'
    if re.search(r'(fresher|0\s*[-–to]+\s*[12]|entry[\s\-]?level|no\s*experience|graduate|1\s*\+?\s*year|1\s*year|min(?:imum)?\s*6\s*month|6\s*month)', t):
        return '0-2'
    if m := re.search(r'(\d+)\s*\+?\s*(?:yr|yrs|year|years)', t):
        n = int(m.group(1))
        return '3+' if n >= 4 else '2-3' if n >= 2 else '0-2'
    return '0-2'


def compute_match_score(resume_skills, job_text, job_title=""):
    if not resume_skills:
        return 50
    job_norm = normalize_skill_text(job_text.lower())
    title_norm = normalize_skill_text(job_title.lower())
    resume_norm = [normalize_skill_text(s) for s in resume_skills]
    job_skill_hits = [sk for sk in SKILLS if re.search(
        r'\b' + re.escape(sk) + r'\b', job_norm)]
    matched = [s for s in resume_norm if re.search(
        r'\b' + re.escape(s) + r'\b', job_norm)]
    n_matched = len(matched)
    union = set(resume_norm) | set(job_skill_hits)
    jaccard = (n_matched / len(union) * 100) if union else 0
    coverage = (n_matched / len(resume_norm) * 100) if resume_norm else 0
    base_score = int(0.40 * jaccard + 0.60 * coverage)
    title_bonus = 12 if any(re.search(
        r'\b' + re.escape(s) + r'\b', title_norm) for s in resume_norm) else 0
    role_bonus = 10 if any(kw in title_norm for kw in ["data", "analyst", "engineer", "developer", "scientist", "science", "ml", "ai",
                           "intelligence", "analytics", "python", "sql", "it", "software", "database", "business", "research", "intern", "trainee"]) else 0
    return max(30, min(base_score + title_bonus + role_bonus + min(n_matched * 2, 18), 99))


def _build_job_row(row, resume_skills, domain_filter=None):
    job_url = str(row.get("job_url", ""))
    job_description = str(row.get("description", ""))
    job_title = str(row.get("job_title", ""))
    combined = job_description + ' ' + job_title
    if domain_filter and not job_matches_domain(job_title, job_description, domain_filter):
        return None
    salary = str(row.get("salary", "")).strip()
    location = str(row.get("location", "")).strip()
    return {
        "job_title":    job_title,
        "company":      str(row.get("company", "")),
        "location":     location if location and location != 'nan' else "India",
        "description":  job_description[:220],
        "rating":       row.get("rating") if pd.notna(row.get("rating")) else "N/A",
        "salary":       salary if salary and salary != 'nan' else "Not disclosed",
        "job_url":      job_url,
        "company_logo": str(row.get("company_logo", "")),
        "source":       extract_source_from_url(job_url),
        "skills":       extract_skills_from_text(combined),
        "experience":   extract_experience_from_text(job_description),
        "match_score":  compute_match_score(resume_skills, combined, job_title),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume_skills, personal_info = [], {}
        education, grad_year, work_exp, certifications, summary = [], "", [], [], ""
        ats_score, ats_breakdown = 0, {}
        detected_domain, domain_label = "general", "General Profile"

        if "resume" in request.files:
            resume = request.files["resume"]
            if resume and resume.filename.lower().endswith(".pdf"):
                try:
                    raw_text = extract_text_from_pdf(resume)
                    resume_skills = extract_skills_from_resume(raw_text)
                    personal_info = extract_personal_info(raw_text)
                    education, grad_year = extract_education(raw_text)
                    work_exp = extract_work_experience(raw_text)
                    certifications = extract_certifications(raw_text)
                    summary = extract_summary(raw_text)
                    ats_score, ats_breakdown = compute_ats_score(
                        personal_info, resume_skills, education, work_exp, certifications, summary)
                    detected_domain, domain_label = detect_domain(
                        raw_text, resume_skills, education, summary)
                    print(
                        f"Domain: {detected_domain} | Skills: {resume_skills}")
                except Exception as e:
                    print(f"Resume parsing error: {e}")

        matched_jobs = [j for _, row in jobs_df.iterrows() if (
            j := _build_job_row(row, resume_skills, detected_domain))]
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        if len(matched_jobs) < 10:
            matched_jobs = sorted(
                [j for _, row in jobs_df.iterrows() if (
                    j := _build_job_row(row, resume_skills))],
                key=lambda x: x["match_score"], reverse=True
            )[:100]

        return render_template("results.html", jobs=matched_jobs, resume_skills=resume_skills,
                               personal_info=personal_info, education=education, grad_year=grad_year,
                               work_exp=work_exp, certifications=certifications, summary=summary,
                               ats_score=ats_score, ats_breakdown=ats_breakdown,
                               domain_label=domain_label, total_jobs=len(matched_jobs))

    return render_template("index.html")


CHAT_RESPONSES = [
    (["hello", "hi", "hey"],
     "Hey there! 👋 I'm JobGenie. Ask me about your ATS score, job matches, or resume tips!"),
    (["how does this work", "how do you work", "what do you do"],
     "Upload your PDF → I detect your domain (Data Science, IT, Finance etc.) → show only relevant jobs → compute ATS score! 🎯"),
    (["ats", "ats score"],         "ATS score is out of 100! Contact Info (20pts) + Skills (30pts) + Education (20pts) + Experience (15pts) + Certifications (10pts) + Summary (5pts) 📊"),
    (["domain", "profile", "what type"],
     "I detect your profile — Data Science, Software Dev, Finance/Commerce, Marketing, HR, or Data Entry — and only show relevant jobs for your background! 🎯"),
    (["resume", "cv", "upload"],
     "Upload your PDF resume on the home page. I'll detect your domain and show only relevant jobs with an ATS score! 📄"),
    (["skill", "skills"],
     "I detect 80+ skills like Python, SQL, Excel, ML, TensorFlow, Flask, AWS and more. More skills = better matches! 💡"),
    (["match", "score", "percent", "%"],
     "Match score = overlap between your resume skills and job description + title similarity. 70%+ great, 45-69% decent, below 45% low."),
    (["filter", "linkedin", "indeed", "naukri"],
     "Use the left sidebar to filter by source, experience level, or skills. Combine filters for best results! 🔍"),
    (["experience", "fresher", "senior"],
     "Filter by 0–2 yrs (fresher), 2–3 yrs (mid), 3+ yrs (senior). You can select multiple! 📊"),
    (["apply"],
     "Click 'Apply Now' on any job card — it opens the real job listing directly! 🚀"),
    (["salary", "pay", "ctc"],
     "Salary depends on what the company disclosed. Many say 'Not disclosed'. Check individual cards! 💰"),
    (["tip", "tips", "improve"],
     "Tips: ✅ Add Summary ✅ List all skills clearly ✅ Add certifications ✅ Include LinkedIn/GitHub ✅ Keep it 1-2 pages!"),
    (["education", "degree", "college"],
     "I extract your degree and grad year automatically! Education adds up to 20pts to your ATS score. 🎓"),
    (["certification", "certificate"],
     "Certifications boost ATS score by up to 10pts! IBM, Microsoft, Google certs are highly valued. 🏆"),
    (["location", "remote"],
     "Check location tags on each card. Search 'remote' in the search bar for remote jobs! 📍"),
    (["search", "find"],
     "Use the search bar to find jobs by title or company. Works alongside all filters! 🔎"),
    (["low match", "why low"],
     "Low match means fewer skill overlaps. Add more relevant skills to your resume or try different filters!"),
    (["thank", "thanks", "awesome", "great"],
     "You're welcome! Best of luck with your job search! 🧞‍♂️✨"),
]


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").strip().lower()
    for keywords, reply in CHAT_RESPONSES:
        if any(w in msg for w in keywords):
            return jsonify({"reply": reply})
    return jsonify({"reply": "I can help with: ATS score, domain detection, resume tips, match scores, or applying to jobs. What would you like to know? 😊"})


if __name__ == "__main__":
    app.run(debug=False)
