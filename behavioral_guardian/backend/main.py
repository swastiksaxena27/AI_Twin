"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from behavioral_guardian.backend.routers import alerts, analyze, analytics, auth, history, reauth, risk, session, trust, users
from behavioral_guardian.backend.routers import settings as settings_router
from behavioral_guardian.config.settings import API_PREFIX
from behavioral_guardian.database.connection import init_db
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)

app = FastAPI(title="AI Behavioral Guardian", version="0.1.0")

# Allow the React frontend (dev server on :5173, or any local origin) to call
# this API directly from the browser. Without this, every fetch() call from
# the frontend is blocked by CORS even though curl/server-to-server calls work fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database at import time to ensure tables are created
# in serverless environments where startup/lifespan events are bypassed.
try:
    init_db()
    logger.info("Database initialized successfully at startup")
except Exception as e:
    logger.error("Failed to initialize database at startup: %s", e)


@app.on_event("startup")
def on_startup() -> None:
    """Startup event (kept for compatibility)."""
    logger.info("Backend started")


api_router = app.router
for module in (analyze, trust, risk, alerts, history, reauth, session, auth, users, settings_router, analytics):
    app.include_router(module.router, prefix=API_PREFIX)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
