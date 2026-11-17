import sqlite3
import json
import os
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "job_hunter.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table: user_profile (single-user or multi-profile support)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT DEFAULT '',
        desired_roles TEXT DEFAULT '',        -- Comma or JSON array of roles
        skills TEXT DEFAULT '',               -- Comma or JSON array of skills
        experience_level TEXT DEFAULT 'junior', -- junior, pleno/mid, senior
        education TEXT DEFAULT '',            -- High school, College, Bachelor, etc.
        location TEXT DEFAULT '',             -- e.g. 'Brazil', 'São Paulo', 'Remote'
        remote_only INTEGER DEFAULT 0,        -- 1 if remote only
        min_salary REAL DEFAULT 0,
        bio TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table: saved_jobs (favorites)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE,
        title TEXT NOT NULL,
        company TEXT,
        location TEXT,
        site TEXT,
        url TEXT,
        salary TEXT,
        job_type TEXT,
        description TEXT,
        match_score INTEGER DEFAULT 0,
        matched_skills TEXT DEFAULT '[]',
        missing_skills TEXT DEFAULT '[]',
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table: search_cache (to avoid re-scraping recently searched queries)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_cache (
        query_key TEXT PRIMARY KEY,
        results_json TEXT NOT NULL,
        cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ensure at least one profile row exists
    cursor.execute("SELECT id FROM user_profile LIMIT 1;")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO user_profile (full_name, desired_roles, skills, experience_level, education, location, remote_only)
        VALUES ('Candidato', 'Desenvolvedor Python, Backend Developer', 'Python, FastAPI, SQL, Git, Docker', 'junior', 'Ensino Superior em Andamento', 'Brasil', 1);
        """)

    conn.commit()
    conn.close()

def get_profile() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        # Parse skills and roles into lists for easier frontend usage
        data["skills_list"] = [s.strip() for s in data["skills"].split(",") if s.strip()]
        data["roles_list"] = [r.strip() for r in data["desired_roles"].split(",") if r.strip()]
        return data
    return {}

def update_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE user_profile SET
        full_name = :full_name,
        desired_roles = :desired_roles,
        skills = :skills,
        experience_level = :experience_level,
        education = :education,
        location = :location,
        remote_only = :remote_only,
        min_salary = :min_salary,
        bio = :bio,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
    """, {
        "full_name": data.get("full_name", ""),
        "desired_roles": data.get("desired_roles", ""),
        "skills": data.get("skills", ""),
        "experience_level": data.get("experience_level", "junior"),
        "education": data.get("education", ""),
        "location": data.get("location", ""),
        "remote_only": 1 if data.get("remote_only") else 0,
        "min_salary": float(data.get("min_salary") or 0),
        "bio": data.get("bio", "")
    })
    conn.commit()
    conn.close()
    return get_profile()

def save_favorite_job(job: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO saved_jobs 
        (job_id, title, company, location, site, url, salary, job_type, description, match_score, matched_skills, missing_skills)
        VALUES (:job_id, :title, :company, :location, :site, :url, :salary, :job_type, :description, :match_score, :matched_skills, :missing_skills)
        """, {
            "job_id": str(job.get("id") or job.get("job_id") or job.get("url")),
            "title": job.get("title", "Sem título"),
            "company": job.get("company", "Não informada"),
            "location": job.get("location", ""),
            "site": job.get("site", "Web"),
            "url": job.get("url", ""),
            "salary": job.get("salary", ""),
            "job_type": job.get("job_type", ""),
            "description": job.get("description", ""),
            "match_score": job.get("match_score", 0),
            "matched_skills": json.dumps(job.get("matched_skills", [])),
            "missing_skills": json.dumps(job.get("missing_skills", []))
        })
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving job: {e}")
        return False
    finally:
        conn.close()

def delete_favorite_job(job_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_jobs WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    return True

def list_favorite_jobs() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_jobs ORDER BY saved_at DESC;")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        item["matched_skills"] = json.loads(item.get("matched_skills") or "[]")
        item["missing_skills"] = json.loads(item.get("missing_skills") or "[]")
        results.append(item)
    return results
