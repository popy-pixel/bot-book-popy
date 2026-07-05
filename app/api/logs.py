"""
Activity Logs API
📁 app/api/logs.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.models import ActivityLog
from app.models.schemas import LogResponse, LogListResponse

router = APIRouter()


@router.get("/", response_model=LogListResponse)
async def list_logs(
    account_id: int = None,
    task_id: int = None,
    level: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List activity logs with filtering."""
    
    query = select(ActivityLog).order_by(ActivityLog.timestamp.desc())
    
    if account_id:
        query = query.where(ActivityLog.account_id == account_id)
    if task_id:
        query = query.where(ActivityLog.task_id == task_id)
    if level:
        query = query.where(ActivityLog.log_level == level)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    total_result = await db.execute(select(func.count()).select_from(ActivityLog))
    total = total_result.scalar()
    
    return LogListResponse(logs=logs, total=total)


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific log entry."""
    log = await db.get(ActivityLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log