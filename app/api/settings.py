"""
Settings Management API
📁 app/api/settings.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models.models import GlobalSettings
from app.models.schemas import SettingsResponse, SettingsUpdate

router = APIRouter()


@router.get("/", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get global settings."""
    
    result = await db.execute(select(GlobalSettings).limit(1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = GlobalSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


@router.put("/", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    """Update global settings."""
    
    result = await db.execute(select(GlobalSettings).limit(1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = GlobalSettings()
        db.add(settings)
    
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return settings