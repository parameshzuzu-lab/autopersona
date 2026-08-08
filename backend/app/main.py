import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.services.autonomous_scheduler import start_autonomous_scheduler, scheduler

logging.basicConfig(level=logging.INFO)

# httpx logs every request URL at INFO level. Gemini/OpenAI URLs embed the API key
# in the query string, so suppress httpx request logging to keep the key out of logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("AutoPersona-Main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Autonomous AI & Tech Persona Publishing Engine REST API with APScheduler 15-min background cycle."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes under both /api and /api/v1 for absolute convenience
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/api/v1")

frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database tables...")
    await init_db()
    logger.info("Starting autonomous 15-minute APScheduler job...")
    start_autonomous_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped cleanly.")

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "scheduler_running": scheduler.running
    }

@app.get("/", include_in_schema=False)
@app.get("/{requested_path:path}", include_in_schema=False)
async def serve_frontend(requested_path: str = ""):
    """Serve the built dashboard and return its entry point for client-side routes."""
    index_file = frontend_dist / "index.html"
    if not index_file.is_file():
        return {"detail": "Frontend build is not available."}

    requested_file = (frontend_dist / requested_path).resolve()
    if requested_path and frontend_dist in requested_file.parents and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(index_file)
