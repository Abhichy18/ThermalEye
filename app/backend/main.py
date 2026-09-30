"""ThermalEye — Master Production FastAPI Application.

AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources.
SIH 2026 | Problem Statement: SIH26162YELLOW
SIH PROBLEM STATEMENT: "26162"
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Add project root to sys.path
ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.config import DATA_OUT_BASE, REGIONS, REGION
from app.backend.api.clusters import router as clusters_router
from app.backend.api.pipeline import router as pipeline_router
from app.backend.api.memos import router as memos_router
from app.backend.api.audio import router as audio_router
from app.backend.api.feedback import router as feedback_router
from app.backend.api.ledger import router as ledger_router
from app.backend.api.citizen import router as citizen_router
from app.backend.api.sentinel import router as sentinel_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown hooks."""
    print("[server] ThermalEye API backend initialized successfully.")
    print(f"[server] Active default region: {REGION.upper()} | Configured regions: {list(REGIONS.keys())}")
    DATA_OUT_BASE.mkdir(parents=True, exist_ok=True)
    yield
    print("[server] ThermalEye backend shutdown complete.")


app = FastAPI(
    title="ThermalEye Intelligence API",
    description="Autonomous Multi-Agent AI System for Satellite-Based Industrial Fire & Persistent Thermal Source Triage (SIH 2026)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Static Outputs (PDF Memos & Audio Advisories) ──
if not DATA_OUT_BASE.exists():
    DATA_OUT_BASE.mkdir(parents=True, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=str(DATA_OUT_BASE)), name="outputs")

# ── Register API Routers ──
api_routers = [
    clusters_router,
    pipeline_router,
    memos_router,
    audio_router,
    feedback_router,
    ledger_router,
    citizen_router,
    sentinel_router,
]

for r in api_routers:
    app.include_router(r, prefix="/api")


@app.get("/health", tags=["System"])
def health_check():
    """System health check and environmental status."""
    return {
        "status": "HEALTHY",
        "service": "ThermalEye Intelligence Platform",
        "version": "1.0.0",
        "default_region": REGION,
        "supported_regions": list(REGIONS.keys()),
        "endpoints": {
            "docs": "/docs",
            "clusters": "/api/clusters",
            "pipeline_stream": "/api/pipeline/stream",
            "citizen_feed": "/api/citizen/feed",
            "ledger": "/api/ledger"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler guaranteeing JSON error formatting."""
    print(f"[server-error] Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": str(exc),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
