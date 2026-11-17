import re
from typing import Dict, Any, List, Tuple

# Common tech synonyms and normalization map
SYNONYMS = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "node": "nodejs",
    "node.js": "nodejs",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "c#": "csharp",
    "c++": "cpp",
    "golang": "go",
    ".net": "dotnet",
    "aws": "amazon web services",
    "gcp": "google cloud",
}

# Known popular tech skills to detect in descriptions even if candidate didn't list them
KNOWN_TECH_CATALOG = [
    "python", "javascript", "typescript", "java", "c#", "c++", "go", "ruby", "php", "rust", "swift", "kotlin",
    "react", "angular", "vue", "next.js", "node", "nodejs", "fastapi", "flask", "django", "express", "spring", "spring boot",
    "laravel", "asp.net", "html", "css", "tailwind", "bootstrap", "sass",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab", "ci/cd", "linux", "graphql", "rest api"
]

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    # Normalize some punctuation
    text = re.sub(r'[/\\+_,]', ' ', text)
    return text

def extract_tokens(text: str) -> set:
    norm = normalize_text(text)
    tokens = set(re.findall(r'\b[a-zA-Z0-9#\.\+\-]{2,}\b', norm))
    # Replace synonyms
    normalized_tokens = set()
    for t in tokens:
        normalized_tokens.add(SYNONYMS.get(t, t))
    return normalized_tokens

def calculate_match(job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates compatibility between a job posting and a candidate's profile.
    Returns:
        job dictionary enriched with match_score (0-100), matched_skills, missing_skills,
        level_fit, and score_breakdown.
    """
    job_title = job.get("title", "")
    job_desc = job.get("description", "")
    job_location = job.get("location", "")
    full_text = f"{job_title} {job_desc} {job_location}".lower()
    
    # 1. Skills Matching (Weight: 50%)
    raw_user_skills = profile.get("skills_list", [])
    if not raw_user_skills and profile.get("skills"):
        raw_user_skills = [s.strip() for s in profile.get("skills").split(",") if s.strip()]
    
    matched_skills = []
    missing_skills = []
    
    for s in raw_user_skills:
        s_norm = s.strip().lower()
        if not s_norm:
            continue
        # Check synonyms
        target_term = SYNONYMS.get(s_norm, s_norm)
        # Search word boundaries in text
        pattern = r'(?:\b|_)' + re.escape(target_term) + r'(?:\b|_)'
        if re.search(pattern, full_text):
            matched_skills.append(s)
        elif s_norm in full_text:
            matched_skills.append(s)
        else:
            missing_skills.append(s)
            
    if raw_user_skills:
        skill_ratio = len(matched_skills) / len(raw_user_skills)
        skill_points = skill_ratio * 50.0
    else:
        skill_points = 35.0  # neutral if user has no skills listed yet
        
    # 2. Desired Roles / Title Matching (Weight: 30%)
    raw_roles = profile.get("roles_list", [])
    if not raw_roles and profile.get("desired_roles"):
        raw_roles = [r.strip() for r in profile.get("desired_roles").split(",") if r.strip()]
        
    role_points = 0.0
    title_lower = job_title.lower()
    
    if raw_roles:
        max_role_sim = 0.0
        title_tokens = extract_tokens(job_title)
        
        for role in raw_roles:
            role_tokens = extract_tokens(role)
            if not role_tokens:
                continue
            common = role_tokens.intersection(title_tokens)
            sim = len(common) / len(role_tokens)
            # Exact phrase match bonus
            if role.lower() in title_lower:
                sim = 1.0
            if sim > max_role_sim:
                max_role_sim = sim
                
        role_points = max_role_sim * 30.0
    else:
        role_points = 20.0  # neutral default

    # 3. Experience Level Fit (Weight: 10%)
    user_level = (profile.get("experience_level") or "junior").lower()
    level_points = 10.0
    level_fit = "match"
    
    senior_patterns = ["senior", "sênior", "sr", "lead", "staff", "principal", "especialista"]
    junior_patterns = ["junior", "júnior", "jr", "estágio", "estagiário", "trainee", "iniciante", "entry level"]
    mid_patterns = ["pleno", "mid", "pl"]
    
    is_job_senior = any(p in title_lower for p in senior_patterns)
    is_job_junior = any(p in title_lower for p in junior_patterns)
    is_job_mid = any(p in title_lower for p in mid_patterns)
    
    if "junior" in user_level or "estagi" in user_level:
        if is_job_junior:
            level_points = 10.0
            level_fit = "match"
        elif is_job_senior:
            level_points = 2.0
            level_fit = "higher"
        elif is_job_mid:
            level_points = 6.0
            level_fit = "slightly_higher"
        else:
            level_points = 8.0  # Not specified in title
    elif "senior" in user_level:
        if is_job_senior:
            level_points = 10.0
            level_fit = "match"
        elif is_job_junior:
            level_points = 4.0
            level_fit = "lower"
        else:
            level_points = 8.0
    else:  # Pleno
        if is_job_mid:
            level_points = 10.0
        elif is_job_junior:
            level_points = 7.0
        elif is_job_senior:
            level_points = 6.0
        else:
            level_points = 8.0

    # 4. Modality / Remote Match (Weight: 10%)
    remote_only = profile.get("remote_only")
    remote_points = 10.0
    remote_keywords = ["remote", "remoto", "home office", "anywhere", "teletrabalho"]
    is_remote_job = any(k in full_text for k in remote_keywords) or "remote" in job.get("job_type", "").lower()
    
    if remote_only:
        if is_remote_job:
            remote_points = 10.0
        else:
            remote_points = 2.0
    else:
        remote_points = 10.0

    total_score = round(skill_points + role_points + level_points + remote_points)
    total_score = max(5, min(99, total_score))  # Keep in realistic range (5% to 99%)

    # Extra tech required by the job that user might not have
    extra_detected = []
    job_tokens = extract_tokens(full_text)
    user_tokens = extract_tokens(" ".join(raw_user_skills))
    for tech in KNOWN_TECH_CATALOG:
        if tech in job_tokens and tech not in user_tokens:
            extra_detected.append(tech.title())

    enriched_job = dict(job)
    enriched_job["match_score"] = total_score
    enriched_job["matched_skills"] = matched_skills
    enriched_job["missing_skills"] = missing_skills
    enriched_job["extra_tech"] = extra_detected[:6]  # top 6 extra skills found
    enriched_job["is_remote"] = is_remote_job
    enriched_job["level_fit"] = level_fit
    enriched_job["score_breakdown"] = {
        "skills": round(skill_points, 1),
        "role": round(role_points, 1),
        "level": round(level_points, 1),
        "remote": round(remote_points, 1)
    }
    return enriched_job

def score_and_rank_jobs(jobs: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scores a list of jobs and sorts them by match_score descending."""
    ranked = [calculate_match(j, profile) for j in jobs]
    ranked.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return ranked
