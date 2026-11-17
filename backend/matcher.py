import re
from typing import Dict, Any, List, Optional
from .catalog import SHIFT_OPTIONS, CONTRACT_OPTIONS, EXPERIENCE_LEVELS

# Level keywords mapping
LEVEL_RULES = {
    "aprendiz": {
        "positive": ["aprendiz", "jovem aprendiz", "menor aprendiz"],
        "negative": ["senior", "sênior", "sr", "pleno", "pl", "coordenador", "gerente", "especialista", "lead", "head"]
    },
    "estagio": {
        "positive": ["estágio", "estagio", "estagiário", "estagiaria", "intern", "internship", "bolsa auxílio"],
        "negative": ["senior", "sênior", "sr", "pleno", "pl", "coordenador", "gerente", "especialista", "lead", "head"]
    },
    "junior": {
        "positive": ["junior", "júnior", "jr", "iniciante", "entry level", "trainee", "auxiliar", "assistente"],
        "negative": ["senior", "sênior", "sr", "lead", "head", "diretor", "especialista", "principal", "architect", "gerente", "coordenador"]
    },
    "pleno": {
        "positive": ["pleno", "pl", "mid", "intermediário", "analista"],
        "negative": ["estágio", "estagiário", "aprendiz", "diretor", "head"]
    },
    "senior": {
        "positive": ["senior", "sênior", "sr", "lead", "head", "especialista", "principal", "gerente", "coordenador"],
        "negative": ["estágio", "estagiário", "aprendiz", "iniciante", "auxiliar", "assistente"]
    }
}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[/\\+_,]', ' ', text)
    return text

def detect_shift(text: str) -> str:
    t = text.lower()
    for shift in SHIFT_OPTIONS:
        for kw in shift["keywords"]:
            if kw in t:
                return shift["id"]
    return "integral"  # default standard

def detect_contract(text: str) -> str:
    t = text.lower()
    for contract in CONTRACT_OPTIONS:
        for kw in contract["keywords"]:
            if kw in t:
                return contract["id"]
    return "clt"  # default standard

def detect_level(text: str) -> str:
    t = text.lower()
    for lvl in ["aprendiz", "estagio", "junior", "senior", "pleno"]:
        for kw in LEVEL_RULES[lvl]["positive"]:
            if kw in t:
                return lvl
    return "pleno"

def calculate_match(
    job: Dict[str, Any], 
    profile: Dict[str, Any],
    strict_level: bool = True
) -> Dict[str, Any]:
    """
    Calculates detailed compatibility between candidate profile and a job.
    Includes strict seniority filtering, shift matching, and contract matching.
    """
    job_title = job.get("title", "")
    job_desc = job.get("description", "")
    job_location = job.get("location", "")
    job_type = job.get("job_type", "")
    
    full_text = f"{job_title} {job_desc} {job_location} {job_type}".lower()
    title_lower = job_title.lower()
    
    # User Preferences
    user_level = (profile.get("experience_level") or "junior").lower()
    user_category = (profile.get("category") or "todos").lower()
    user_shifts = profile.get("shifts_list") or ["integral"]
    user_contracts = profile.get("contract_types_list") or ["clt"]
    remote_only = bool(profile.get("remote_only", False))
    
    # Detect job characteristics
    job_shift = job.get("shift") or detect_shift(full_text)
    job_contract = job.get("contract_type") or detect_contract(full_text)
    job_level = detect_level(f"{job_title} {job_desc}")

    # ==========================================
    # 1. STRICT SENIORITY / LEVEL FILTER
    # ==========================================
    level_score = 15.0
    level_fit = "match"
    is_level_conflict = False

    if user_level in LEVEL_RULES:
        rules = LEVEL_RULES[user_level]
        has_positive = any(re.search(r'\b' + re.escape(p) + r'\b', title_lower) for p in rules["positive"])
        has_negative = any(re.search(r'\b' + re.escape(n) + r'\b', title_lower) for n in rules["negative"])

        if has_negative:
            is_level_conflict = True
            level_fit = "conflict"
            level_score = 0.0
        elif has_positive:
            level_fit = "match"
            level_score = 15.0
        else:
            # Neutral / unspecified in title
            level_fit = "compatible"
            level_score = 10.0

    # If strict filtering is active and there's a direct level conflict in title
    # (e.g. user is Junior/Estágio and job title is "Sênior / Lead / Especialista")
    if strict_level and is_level_conflict:
        # Mark job as excluded so search can discard it
        return {
            **job,
            "match_score": 0,
            "is_excluded": True,
            "exclusion_reason": f"Nível incompatível: Vaga exige {job_level.upper()} e seu perfil busca {user_level.upper()}."
        }

    # ==========================================
    # 2. ROLE & TITLE MATCHING (Weight: 35%)
    # ==========================================
    raw_roles = profile.get("roles_list", [])
    if not raw_roles and profile.get("desired_roles"):
        raw_roles = [r.strip() for r in profile.get("desired_roles").split(",") if r.strip()]

    role_score = 0.0
    if raw_roles:
        max_sim = 0.0
        for r in raw_roles:
            r_norm = r.lower().strip()
            if not r_norm:
                continue
            # Exact phrase match in title
            if r_norm in title_lower:
                max_sim = 1.0
                break
            
            # Token match (excluding generic terms like 'junior', 'desenvolvedor', 'assistente')
            r_words = set(re.findall(r'\b\w{3,}\b', r_norm))
            t_words = set(re.findall(r'\b\w{3,}\b', title_lower))
            if r_words:
                overlap = r_words.intersection(t_words)
                sim = len(overlap) / len(r_words)
                if sim > max_sim:
                    max_sim = sim
                    
        role_score = max_sim * 35.0
    else:
        role_score = 25.0

    # ==========================================
    # 3. SKILLS MATCHING (Weight: 35%)
    # ==========================================
    raw_skills = profile.get("skills_list", [])
    if not raw_skills and profile.get("skills"):
        raw_skills = [s.strip() for s in profile.get("skills").split(",") if s.strip()]

    matched_skills = []
    missing_skills = []

    for s in raw_skills:
        s_norm = s.strip().lower()
        if not s_norm:
            continue
        # Search boundary
        pattern = r'(?:\b|_)' + re.escape(s_norm) + r'(?:\b|_)'
        if re.search(pattern, full_text):
            matched_skills.append(s)
        else:
            missing_skills.append(s)

    if raw_skills:
        skill_ratio = len(matched_skills) / len(raw_skills)
        skill_score = skill_ratio * 35.0
    else:
        skill_score = 20.0

    # ==========================================
    # 4. SHIFT (TURNO) & CONTRACT MATCHING (Weight: 15%)
    # ==========================================
    shift_score = 7.5
    if job_shift in user_shifts or "todos" in user_shifts:
        shift_score = 7.5
    else:
        # Check if job says 'flexível' or general
        if "flexivel" in user_shifts or job_shift == "integral":
            shift_score = 5.0
        else:
            shift_score = 2.0

    contract_score = 7.5
    if job_contract in user_contracts or "todos" in user_contracts:
        contract_score = 7.5
    else:
        contract_score = 3.0

    # Remote preference modifier
    remote_keywords = ["remote", "remoto", "home office", "teletrabalho", "híbrido"]
    is_remote = any(k in full_text for k in remote_keywords) or "remoto" in job_location.lower()

    if remote_only and not is_remote:
        # Deduct score if user strictly wanted remote
        role_score = max(0.0, role_score - 10.0)

    # Compute Total Score
    total_score = round(skill_score + role_score + level_score + shift_score + contract_score)
    total_score = max(5, min(99, total_score))

    enriched_job = dict(job)
    enriched_job["match_score"] = total_score
    enriched_job["matched_skills"] = matched_skills
    enriched_job["missing_skills"] = missing_skills
    enriched_job["detected_shift"] = job_shift
    enriched_job["detected_contract"] = job_contract
    enriched_job["detected_level"] = job_level
    enriched_job["is_remote"] = is_remote
    enriched_job["is_excluded"] = False
    enriched_job["score_breakdown"] = {
        "skills": round(skill_score, 1),
        "role": round(role_score, 1),
        "level": round(level_score, 1),
        "shift": round(shift_score, 1),
        "contract": round(contract_score, 1)
    }
    return enriched_job

def score_and_rank_jobs(
    jobs: List[Dict[str, Any]], 
    profile: Dict[str, Any],
    strict_level: bool = True
) -> List[Dict[str, Any]]:
    """Scores jobs, removes strict conflicts, and ranks by compatibility."""
    scored_list = []
    for j in jobs:
        scored = calculate_match(j, profile, strict_level=strict_level)
        if not scored.get("is_excluded"):
            scored_list.append(scored)
            
    scored_list.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored_list
