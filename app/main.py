from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.jobs import router as jobs_router
from app.routes.ui import router as ui_router

app = FastAPI(title="CrewAI Job Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(ui_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
