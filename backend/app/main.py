from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Routers
from app.routers.health import router as health_router
from app.routers.applications import router as applications_router
from app.routers.auth import router as auth_router



app = FastAPI(title=settings.app_name)

# CORS (allow your future frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(applications_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix) 

# Create tables on startup (TEMPORARY; later replace with Alembic migrations)


@app.get("/")
def root():
    return {"message": "Job Tracker API is running", "docs": "/docs"}
