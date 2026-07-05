"""
BOT-BOOK-POPY FastAPI Application
=================================
Main application entry point with WebSocket support.
📁 app/main.py
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, DEBUG
from app.models.database import init_db
from app.core.browser_manager import get_browser_manager
from app.api import accounts, tasks, dashboard, settings, websocket, logs

# Configure logging
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting BOT-BOOK-POPY...")
    await init_db()
    await get_browser_manager()
    logger.info("BOT-BOOK-POPY started successfully!")
    
    yield
    
    logger.info("Shutting down BOT-BOOK-POPY...")
    browser_manager = await get_browser_manager()
    await browser_manager.shutdown()
    logger.info("BOT-BOOK-POPY shutdown complete.")


app = FastAPI(
    title="BOT-BOOK-POPY",
    description="Advanced Facebook Automation Framework",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])

# WebSocket
app.include_router(websocket.router, prefix="/ws")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    return {"message": "BOT-BOOK-POPY API", "version": "2.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}