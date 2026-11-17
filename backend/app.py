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
from .scraper import search_all_sources
from .matcher import score_and_rank_jobs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_hunter")

app = FastAPI(
    title="Job-Hunter API",
    description="Motor de busca de vagas com cálculo inteligente de compatibilidade",
    version="1.0.0"
)

# Enable CORS for development
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
    logger.info("Database initialized successfully.")

# Path to frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Pydantic Schemas
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = ""
    desired_roles: Optional[str] = ""
    skills: Optional[str] = ""
    experience_level: Optional[str] = "junior"
    education: Optional[str] = ""
    location: Optional[str] = ""
    remote_only: Optional[bool] = False
    min_salary: Optional[float] = 0.0
    bio: Optional[str] = ""

class SearchRequest(BaseModel):
    query: Optional[str] = ""
    location: Optional[str] = "Brasil"
    sources: Optional[List[str]] = ["remotive", "arbeitnow", "jobspy"]
    min_match: Optional[int] = 0

class FavoriteRequest(BaseModel):
    job: Dict[str, Any]

# API Endpoints
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
    
    # If query is blank, use user's desired roles or top skills
    search_query = req.query.strip()
    if not search_query:
        if user_prof.get("roles_list"):
            search_query = user_prof["roles_list"][0]
        elif user_prof.get("skills_list"):
            search_query = user_prof["skills_list"][0]
        else:
            search_query = "Python"

    search_location = req.location or user_prof.get("location") or "Brasil"
    
    # 1. Fetch jobs from selected sources
    raw_jobs = search_all_sources(
        query=search_query,
        location=search_location,
        sources=req.sources or ["remotive", "arbeitnow", "jobspy"],
        limit=30
    )

    # 2. Score and rank jobs according to user profile
    ranked_jobs = score_and_rank_jobs(raw_jobs, user_prof)

    # 3. Filter by minimum match threshold if provided
    if req.min_match and req.min_match > 0:
        ranked_jobs = [j for j in ranked_jobs if j.get("match_score", 0) >= req.min_match]

    return {
        "query": search_query,
        "location": search_location,
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
