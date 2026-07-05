"""
Account Management API Endpoints
📁 app/api/accounts.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.models import FacebookAccount, AccountStatus
from app.models.schemas import AccountCreate, AccountUpdate, AccountResponse, AccountListResponse
from app.core.stealth_engine import get_stealth_engine

router = APIRouter()


@router.post("/", response_model=AccountResponse)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_db)):
    """Create a new Facebook account with auto-generated fingerprint."""
    
    stealth = get_stealth_engine()
    fingerprint = stealth.generate_profile()
    
    db_account = FacebookAccount(
        name=account.name,
        email=account.email,
        password_encrypted=account.password,
        proxy_url=account.proxy_url,
        proxy_type=account.proxy_type or "http",
        fingerprint_profile={
            "user_agent": fingerprint.user_agent,
            "platform": fingerprint.platform,
            "viewport": fingerprint.viewport,
            "hardware_concurrency": fingerprint.hardware_concurrency,
            "timezone": fingerprint.timezone,
            "profile_hash": fingerprint.profile_hash,
        },
        user_agent=fingerprint.user_agent,
        status=AccountStatus.INACTIVE,
        daily_action_limit=account.daily_action_limit,
        notes=account.notes,
    )
    
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    
    return db_account


@router.get("/", response_model=AccountListResponse)
async def list_accounts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all Facebook accounts."""
    
    result = await db.execute(
        select(FacebookAccount).offset(skip).limit(limit)
    )
    accounts = result.scalars().all()
    
    total_result = await db.execute(select(func.count()).select_from(FacebookAccount))
    total = total_result.scalar()
    
    return AccountListResponse(accounts=accounts, total=total)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific account."""
    
    account = await db.get(FacebookAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, update: AccountUpdate, 
                         db: AsyncSession = Depends(get_db)):
    """Update an account."""
    
    account = await db.get(FacebookAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    await db.commit()
    await db.refresh(account)
    
    return account


@router.delete("/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an account."""
    
    account = await db.get(FacebookAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    await db.delete(account)
    await db.commit()
    
    return {"message": "Account deleted successfully"}


@router.post("/{account_id}/test-login")
async def test_login(account_id: int, db: AsyncSession = Depends(get_db)):
    """Test login for an account."""
    
    from app.workers.task_worker import execute_task
    from app.models.models import Task, TaskType, TaskStatus
    
    account = await db.get(FacebookAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    task = Task(
        account_id=account_id,
        task_type=TaskType.LOGIN,
        payload={
            "email": account.email,
            "password": account.password_encrypted,
        },
        status=TaskStatus.QUEUED,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    result = execute_task.delay(task.id)
    
    return {"task_id": task.id, "celery_task_id": result.id, "status": "queued"}