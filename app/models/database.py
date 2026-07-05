
# ============================================================
# PART 2: DATABASE MODELS & SCHEMAS
# ============================================================
# 📁 app/models/database.py
# 📁 app/models/models.py
# 📁 app/models/schemas.py

# ── database.py ───────────────────────────────────────────
database_py = r'''"""
BOT-BOOK-POPY Database Module
==============================
SQLAlchemy async database setup with Alembic migration support.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import DATABASE_URL

# Convert sqlite:// to sqlite+aiosqlite:// for async support
_db_url = DATABASE_URL
if _db_url.startswith("sqlite:///") and "+aiosqlite" not in _db_url:
    _db_url = _db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    _db_url,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in _db_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db():
    """FastAPI dependency to get DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
'''

