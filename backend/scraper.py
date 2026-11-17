import hashlib
import json
import logging
import re
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Fallback curated seed jobs for testing or when external networks/rate-limits block requests
SEED_JOBS: List[Dict[str, Any]] = [
    {
        "id": "seed-1",
        "title": "Desenvolvedor Python Júnior",
        "company": "TechNova Soluções",
        "location": "Brasil (Remoto)",
        "site": "Remotive",
        "url": "https://remotive.com",
        "salary": "R$ 4.000 - R$ 5.500",
        "job_type": "Full-time",
        "description": "Estamos em busca de um Desenvolvedor Python Júnior para atuar em nossa equipe de backend. Requisitos: Conhecimento em Python, FastAPI ou Flask, SQL (SQLite/PostgreSQL), Git, APIs REST e interesse em aprender Docker e Cloud.",
        "date_posted": "Hoje"
    },
    {
        "id": "seed-2",
        "title": "Backend Developer - Python & APIs",
        "company": "DataStream Corp",
        "location": "São Paulo, SP (Híbrido)",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 6.000 - R$ 8.500",
        "job_type": "Full-time",
        "description": "Buscamos desenvolvedor backend com foco em microsserviços. Exigências: Python 3+, Docker, Git, CI/CD, bancos relacionais e NoSQL. Conhecimento em mensageria (RabbitMQ ou Kafka) e testes automatizados são diferenciais.",
        "date_posted": "Ontem"
    },
    {
        "id": "seed-3",
        "title": "Desenvolvedor Full Stack Júnior (Python/JS)",
        "company": "WebCraft Digital",
        "location": "Remoto",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 4.500",
        "job_type": "Full-time",
        "description": "Vaga para desenvolvedor full stack iniciante. Tecnologias utilizadas: Python no backend (FastAPI/Django), HTML5, CSS3, JavaScript puro no frontend e SQLite/MySQL.",
        "date_posted": "Há 2 dias"
    },
    {
        "id": "seed-4",
        "title": "Estagiário / Trainee em Desenvolvimento de Software",
        "company": "InovaTech Labs",
        "location": "Remoto",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 2.000 + Benefícios",
        "job_type": "Estágio",
        "description": "Oportunidade para estudantes de Ciência da Computação, Engenharia de Software ou correlatas. Desejável conhecimento em lógica de programação, Python ou JavaScript, e vontade de aprender Git e metodologias ágeis.",
        "date_posted": "Há 3 dias"
    },
    {
        "id": "seed-5",
        "title": "Senior Python Architect & Tech Lead",
        "company": "Global Cloud Systems",
        "location": "Remoto (Internacional)",
        "site": "Glassdoor",
        "url": "https://glassdoor.com",
        "salary": "$ 70,000 - $ 95,000 / ano",
        "job_type": "Full-time",
        "description": "Senior Python Engineer needed to architect high-throughput data processing pipelines. 6+ years experience, Kubernetes, AWS, microservices, distributed systems and advanced Python required.",
        "date_posted": "Há 1 semana"
    }
]

def clean_html(raw_html: str) -> str:
    """Removes HTML tags from descriptions."""
    if not raw_html:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', raw_html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def generate_job_id(title: str, company: str, site: str) -> str:
    hash_str = f"{title}_{company}_{site}".lower()
    return hashlib.md5(hash_str.encode()).hexdigest()[:12]

def fetch_remotive_jobs(search_term: str = "", limit: int = 25) -> List[Dict[str, Any]]:
    """
    Fetches remote jobs from Remotive's free public API without requiring keys.
    """
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {}
        if search_term:
            params["search"] = search_term
            
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            raw_jobs = data.get("jobs", [])
            for r in raw_jobs[:limit]:
                clean_desc = clean_html(r.get("description", ""))
                jobs.append({
                    "id": f"remotive-{r.get('id')}",
                    "title": r.get("title", ""),
                    "company": r.get("company_name", ""),
                    "location": r.get("candidate_required_location", "Qualquer lugar (Remoto)"),
                    "site": "Remotive",
                    "url": r.get("url", ""),
                    "salary": r.get("salary", "Não divulgado"),
                    "job_type": r.get("job_type", "Full-time"),
                    "description": clean_desc,
                    "date_posted": r.get("publication_date", "")[:10]
                })
    except Exception as e:
        logger.warning(f"Error fetching from Remotive API: {e}")
    return jobs

def fetch_arbeitnow_jobs(search_term: str = "", limit: int = 25) -> List[Dict[str, Any]]:
    """
    Fetches jobs from Arbeitnow's free public API.
    """
    jobs = []
    try:
        url = "https://www.arbeitnow.com/api/job-board-api"
        params = {}
        if search_term:
            params["search"] = search_term
            
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            raw_jobs = data.get("data", [])
            for r in raw_jobs[:limit]:
                clean_desc = clean_html(r.get("description", ""))
                jobs.append({
                    "id": f"arbeitnow-{r.get('slug')}",
                    "title": r.get("title", ""),
                    "company": r.get("company_name", ""),
                    "location": r.get("location", "Remoto / Europa"),
                    "site": "Arbeitnow",
                    "url": r.get("url", ""),
                    "salary": "Não divulgado",
                    "job_type": "Full-time" if not r.get("remote") else "Remoto",
                    "description": clean_desc,
                    "date_posted": "Recente"
                })
    except Exception as e:
        logger.warning(f"Error fetching from Arbeitnow API: {e}")
    return jobs

def fetch_jobspy_jobs(
    search_term: str = "python", 
    location: str = "Brazil", 
    sites: Optional[List[str]] = None,
    results_wanted: int = 15
) -> List[Dict[str, Any]]:
    """
    Scrapes jobs using python-jobspy from LinkedIn, Indeed, Glassdoor, ZipRecruiter.
    """
    if sites is None:
        sites = ["indeed", "linkedin", "glassdoor"]
        
    jobs = []
    try:
        from jobspy import scrape_jobs
        
        df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=168, # last 7 days
            country_indeed="brazil" if "brazil" in location.lower() or "brasil" in location.lower() else "usa"
        )
        
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                site_name = str(row.get("site", "Web")).capitalize()
                title = str(row.get("title", "Sem título"))
                company = str(row.get("company", "Empresa confidencial"))
                desc = clean_html(str(row.get("description", "")))
                job_url = str(row.get("job_url", ""))
                loc = str(row.get("location", location))
                
                # Format salary if min/max exists
                min_amt = row.get("min_amount")
                max_amt = row.get("max_amount")
                interval = row.get("interval", "")
                salary_str = "Não divulgado"
                if min_amt and max_amt:
                    salary_str = f"{min_amt:,.0f} - {max_amt:,.0f} ({interval})"
                elif min_amt:
                    salary_str = f"A partir de {min_amt:,.0f} ({interval})"

                jobs.append({
                    "id": generate_job_id(title, company, site_name),
                    "title": title,
                    "company": company,
                    "location": loc,
                    "site": site_name,
                    "url": job_url,
                    "salary": salary_str,
                    "job_type": str(row.get("job_type", "Full-time")),
                    "description": desc,
                    "date_posted": str(row.get("date_posted", "Recent"))
                })
    except Exception as e:
        logger.warning(f"JobSpy scraping error: {e}")
        
    return jobs

def search_all_sources(
    query: str,
    location: str = "Brasil",
    sources: Optional[List[str]] = None,
    limit: int = 30
) -> List[Dict[str, Any]]:
    """
    Orchestrates searching across chosen sources with graceful degradation.
    """
    if sources is None:
        sources = ["remotive", "jobspy"]
        
    collected: List[Dict[str, Any]] = []
    
    # 1. Remotive API
    if "remotive" in sources:
        remotive_jobs = fetch_remotive_jobs(query, limit=limit // 2)
        collected.extend(remotive_jobs)
        
    # 2. Arbeitnow API
    if "arbeitnow" in sources:
        arbeit_jobs = fetch_arbeitnow_jobs(query, limit=limit // 2)
        collected.extend(arbeit_jobs)

    # 3. JobSpy (Indeed / LinkedIn)
    if "jobspy" in sources:
        spy_jobs = fetch_jobspy_jobs(search_term=query, location=location, results_wanted=15)
        collected.extend(spy_jobs)

    # 4. If no external results succeeded (e.g. offline / rate limits), filter seed jobs
    if not collected:
        logger.info("Using seed fallback jobs matching query.")
        query_norm = query.lower()
        for seed in SEED_JOBS:
            if query_norm in seed["title"].lower() or query_norm in seed["description"].lower():
                collected.append(seed)
        if not collected:
            collected = list(SEED_JOBS)

    # Deduplicate by job id or (title + company)
    seen_ids = set()
    deduped = []
    for job in collected:
        jid = job.get("id") or generate_job_id(job.get("title", ""), job.get("company", ""), job.get("site", ""))
        if jid not in seen_ids:
            seen_ids.add(jid)
            deduped.append(job)
            
    return deduped[:limit]
