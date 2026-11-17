import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .database import (
    init_db,
    get_profile,
    update_profile,
    save_favorite_job,
    delete_favorite_job,
    list_favorite_jobs
)
from .catalog import (
    JOB_CATEGORIES,
    SHIFT_OPTIONS,
    CONTRACT_OPTIONS,
    EXPERIENCE_LEVELS
)
from .scraper import search_all_sources
from .matcher import score_and_rank_jobs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_hunter")

app = FastAPI(
    title="Job-Hunter API",
    description="Motor de busca de vagas com cálculo inteligente de compatibilidade para todas as áreas",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database initialized successfully with new columns and catalog.")

# Path to frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Pydantic Schemas
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = ""
    category: Optional[str] = "administracao"
    desired_roles: Optional[str] = ""
    skills: Optional[str] = ""
    experience_level: Optional[str] = "junior"
    shifts: Optional[str] = "integral"
    contract_types: Optional[str] = "clt"
    strict_level_filter: Optional[bool] = True
    education: Optional[str] = ""
    location: Optional[str] = ""
    remote_only: Optional[bool] = False
    min_salary: Optional[float] = 0.0
    bio: Optional[str] = ""

class SearchRequest(BaseModel):
    query: Optional[str] = ""
    location: Optional[str] = "Brasil"
    category: Optional[str] = "todos"
    shift: Optional[str] = "todos"
    contract: Optional[str] = "todos"
    strict_level: Optional[bool] = True
    sources: Optional[List[str]] = ["jobspy"]
    min_match: Optional[int] = 0

class FavoriteRequest(BaseModel):
    job: Dict[str, Any]

# API Endpoints
@app.get("/api/catalog")
def api_get_catalog():
    """Returns preset options for categories, roles, skills, shifts, and contracts."""
    return {
        "categories": JOB_CATEGORIES,
        "shifts": SHIFT_OPTIONS,
        "contracts": CONTRACT_OPTIONS,
        "experience_levels": EXPERIENCE_LEVELS
    }

@app.get("/api/profile")
def api_get_profile():
    return get_profile()

@app.post("/api/profile")
def api_update_profile(profile_data: ProfileUpdate):
    updated = update_profile(profile_data.dict())
    return {"message": "Perfil atualizado com sucesso!", "profile": updated}

@app.post("/api/search")
def api_search_jobs(req: SearchRequest):
    user_prof = get_profile()
    
    # Priority for query:
    search_query = req.query.strip()
    if not search_query:
        if user_prof.get("roles_list"):
            search_query = user_prof["roles_list"][0]
        else:
            search_query = "Assistente"

    search_location = req.location or user_prof.get("location") or "Brasil"
    category = req.category if req.category != "todos" else user_prof.get("category", "todos")
    shift = req.shift or "todos"
    contract = req.contract or "todos"
    strict = req.strict_level if req.strict_level is not None else bool(user_prof.get("strict_level_filter", True))

    # 1. Fetch raw jobs
    raw_jobs = search_all_sources(
        query=search_query,
        location=search_location,
        category=category,
        shift=shift,
        contract=contract,
        sources=req.sources or ["jobspy", "remotive"],
        limit=35
    )

    # 2. Score, filter seniority conflicts, and rank
    ranked_jobs = score_and_rank_jobs(
        jobs=raw_jobs, 
        profile=user_prof, 
        strict_level=strict
    )

    # 3. Filter by minimum match score if specified
    if req.min_match and req.min_match > 0:
        ranked_jobs = [j for j in ranked_jobs if j.get("match_score", 0) >= req.min_match]

    return {
        "query": search_query,
        "location": search_location,
        "category": category,
        "shift": shift,
        "contract": contract,
        "strict_level": strict,
        "total_found": len(ranked_jobs),
        "jobs": ranked_jobs
    }

@app.get("/api/favorites")
def api_list_favorites():
    favs = list_favorite_jobs()
    return {"total": len(favs), "favorites": favs}

@app.post("/api/favorites")
def api_save_favorite(req: FavoriteRequest):
    success = save_favorite_job(req.job)
    if not success:
        raise HTTPException(status_code=400, detail="Erro ao salvar vaga favorita.")
    return {"message": "Vaga salva nos favoritos com sucesso!"}

@app.delete("/api/favorites/{job_id}")
def api_delete_favorite(job_id: str):
    delete_favorite_job(job_id)
    return {"message": "Vaga removida dos favoritos."}

@app.get("/api/stats")
def api_get_stats():
    profile = get_profile()
    favs = list_favorite_jobs()
    return {
        "candidate_name": profile.get("full_name") or "Candidato",
        "category": profile.get("category", "geral"),
        "skills_count": len(profile.get("skills_list", [])),
        "favorites_count": len(favs),
        "target_level": profile.get("experience_level", "junior")
    }

# Mount Frontend static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
