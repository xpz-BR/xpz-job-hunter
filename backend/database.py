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
    
    # Table: user_profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT DEFAULT '',
        category TEXT DEFAULT 'todos',
        desired_roles TEXT DEFAULT '',
        skills TEXT DEFAULT '',
        experience_level TEXT DEFAULT 'junior',
        shifts TEXT DEFAULT 'integral',
        contract_types TEXT DEFAULT 'clt',
        strict_level_filter INTEGER DEFAULT 1,
        education TEXT DEFAULT '',
        location TEXT DEFAULT '',
        remote_only INTEGER DEFAULT 0,
        min_salary REAL DEFAULT 0,
        bio TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Safe column migrations if database already existed
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(user_profile)").fetchall()]
    new_cols = {
        "category": "TEXT DEFAULT 'todos'",
        "shifts": "TEXT DEFAULT 'integral'",
        "contract_types": "TEXT DEFAULT 'clt'",
        "strict_level_filter": "INTEGER DEFAULT 1"
    }
    for col_name, col_type in new_cols.items():
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE user_profile ADD COLUMN {col_name} {col_type};")

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
        shift TEXT DEFAULT '',
        category TEXT DEFAULT '',
        description TEXT,
        match_score INTEGER DEFAULT 0,
        matched_skills TEXT DEFAULT '[]',
        missing_skills TEXT DEFAULT '[]',
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check for shift and category in saved_jobs
    saved_cols = [row[1] for row in cursor.execute("PRAGMA table_info(saved_jobs)").fetchall()]
    if "shift" not in saved_cols:
        cursor.execute("ALTER TABLE saved_jobs ADD COLUMN shift TEXT DEFAULT '';")
    if "category" not in saved_cols:
        cursor.execute("ALTER TABLE saved_jobs ADD COLUMN category TEXT DEFAULT '';")

    # Ensure at least one profile row exists
    cursor.execute("SELECT id FROM user_profile LIMIT 1;")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO user_profile (
            full_name, category, desired_roles, skills, experience_level, 
            shifts, contract_types, strict_level_filter, education, location, remote_only
        ) VALUES (
            'Candidato', 'administracao', 'Assistente Administrativo, Auxiliar de Escritório', 
            'Excel Avançado, Rotinas Administrativas, Atendimento ao Cliente, Faturamento', 
            'junior', 'integral,manha', 'clt,estagio,aprendiz', 1, 
            'Ensino Médio Completo / Superior Cursando', 'Brasil', 0
        );
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
        data["skills_list"] = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()]
        data["roles_list"] = [r.strip() for r in (data.get("desired_roles") or "").split(",") if r.strip()]
        data["shifts_list"] = [sh.strip() for sh in (data.get("shifts") or "").split(",") if sh.strip()]
        data["contract_types_list"] = [c.strip() for c in (data.get("contract_types") or "").split(",") if c.strip()]
        return data
    return {}

def update_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE user_profile SET
        full_name = :full_name,
        category = :category,
        desired_roles = :desired_roles,
        skills = :skills,
        experience_level = :experience_level,
        shifts = :shifts,
        contract_types = :contract_types,
        strict_level_filter = :strict_level_filter,
        education = :education,
        location = :location,
        remote_only = :remote_only,
        min_salary = :min_salary,
        bio = :bio,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
    """, {
        "full_name": data.get("full_name", ""),
        "category": data.get("category", "todos"),
        "desired_roles": data.get("desired_roles", ""),
        "skills": data.get("skills", ""),
        "experience_level": data.get("experience_level", "junior"),
        "shifts": data.get("shifts", "integral"),
        "contract_types": data.get("contract_types", "clt"),
        "strict_level_filter": 1 if data.get("strict_level_filter", True) else 0,
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
        (job_id, title, company, location, site, url, salary, job_type, shift, category, description, match_score, matched_skills, missing_skills)
        VALUES (:job_id, :title, :company, :location, :site, :url, :salary, :job_type, :shift, :category, :description, :match_score, :matched_skills, :missing_skills)
        """, {
            "job_id": str(job.get("id") or job.get("job_id") or job.get("url")),
            "title": job.get("title", "Sem título"),
            "company": job.get("company", "Não informada"),
            "location": job.get("location", ""),
            "site": job.get("site", "Web"),
            "url": job.get("url", ""),
            "salary": job.get("salary", ""),
            "job_type": job.get("job_type", ""),
            "shift": job.get("shift", ""),
            "category": job.get("category", ""),
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
