import os
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.job_pipeline import generate_application_draft, run_job_search

router = APIRouter(prefix="/api", tags=["jobs"])

class JobSearchRequest(BaseModel):
    role: str
    location: str = "Remote"
    experience: str = "mid"
    resume_text: str = ""

class JobSearchResponse(BaseModel):
    summary: str
    matches: List[dict]

class ApplyRequest(BaseModel):
    role: str
    company: str
    job_title: str
    resume_text: str = ""

class ApplyResponse(BaseModel):
    cover_letter: str
    next_steps: List[str]

@router.post("/search", response_model=JobSearchResponse)
def search_jobs(payload: JobSearchRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")
    try:
        result = run_job_search(payload.role, payload.location, payload.experience, payload.resume_text)
        return JobSearchResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/apply", response_model=ApplyResponse)
def apply_to_job(payload: ApplyRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")
    try:
        result = generate_application_draft(
            payload.role,
            payload.company,
            payload.job_title,
            payload.resume_text,
        )
        return ApplyResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
