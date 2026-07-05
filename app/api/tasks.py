"""
Task Management API Endpoints
📁 app/api/tasks.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.models import Task, TaskStatus, TaskType
from app.models.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.workers.task_worker import execute_task

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create and queue a new automation task."""
    
    db_task = Task(
        account_id=task.account_id,
        task_type=TaskType(task.task_type),
        payload=task.payload,
        natural_instruction=task.natural_instruction,
        scheduled_at=task.scheduled_at,
        max_retries=task.max_retries,
        status=TaskStatus.PENDING,
    )
    
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    
    if not task.scheduled_at:
        result = execute_task.delay(db_task.id)
        db_task.celery_task_id = result.id
        db_task.status = TaskStatus.QUEUED
        await db.commit()
    
    return db_task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: str = None,
    account_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List tasks with optional filtering."""
    
    query = select(Task)
    
    if status:
        query = query.where(Task.status == TaskStatus(status))
    if account_id:
        query = query.where(Task.account_id == account_id)
    
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    total_result = await db.execute(select(func.count()).select_from(Task))
    total = total_result.scalar()
    
    pending = len([t for t in tasks if t.status == TaskStatus.PENDING])
    running = len([t for t in tasks if t.status == TaskStatus.RUNNING])
    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    failed = len([t for t in tasks if t.status == TaskStatus.FAILED])
    
    return TaskListResponse(
        tasks=tasks, total=total,
        pending=pending, running=running,
        completed=completed, failed=failed
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get task details."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Cancel a pending or queued task."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    
    task.status = TaskStatus.CANCELLED
    await db.commit()
    
    return {"message": "Task cancelled"}