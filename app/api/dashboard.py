"""
Dashboard Statistics API
📁 app/api/dashboard.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.models import FacebookAccount, Task, TaskStatus, AccountStatus
from app.models.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    total_accounts_result = await db.execute(select(func.count()).select_from(FacebookAccount))
    total_accounts = total_accounts_result.scalar()
    
    active_accounts_result = await db.execute(
        select(func.count()).where(FacebookAccount.status == AccountStatus.ACTIVE)
    )
    active_accounts = active_accounts_result.scalar()
    
    tasks_today_result = await db.execute(
        select(func.count()).where(Task.created_at >= today_start)
    )
    total_tasks_today = tasks_today_result.scalar()
    
    completed_today_result = await db.execute(
        select(func.count()).where(
            and_(Task.created_at >= today_start, Task.status == TaskStatus.COMPLETED)
        )
    )
    completed_today = completed_today_result.scalar()
    
    failed_today_result = await db.execute(
        select(func.count()).where(
            and_(Task.created_at >= today_start, Task.status == TaskStatus.FAILED)
        )
    )
    failed_today = failed_today_result.scalar()
    
    if total_tasks_today > 0:
        success_rate = (completed_today / total_tasks_today) * 100
    else:
        success_rate = 0.0
    
    health_result = await db.execute(
        select(func.avg(FacebookAccount.fingerprint_health_score))
    )
    avg_health = health_result.scalar() or 0.0
    
    queue_result = await db.execute(
        select(func.count()).where(
            Task.status.in_([TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING])
        )
    )
    queue_length = queue_result.scalar()
    
    return DashboardStats(
        total_accounts=total_accounts,
        active_accounts=active_accounts,
        total_tasks_today=total_tasks_today,
        completed_tasks_today=completed_today,
        failed_tasks_today=failed_today,
        success_rate=round(success_rate, 2),
        avg_fingerprint_health=round(avg_health, 2),
        queue_length=queue_length,
        active_workers=4,
    )