"""
BOT-BOOK-POPY Task Worker
=========================
Celery tasks that execute Facebook automation actions.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from celery import Task

from app.workers.celery_app import celery_app
from app.models.database import AsyncSessionLocal
from app.models.models import Task as TaskModel, TaskStatus, ActivityLog
from app.core.browser_manager import get_browser_manager
from app.services.facebook_actions import FacebookActions, FacebookActionError

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base Celery task with database session management."""
    
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


@celery_app.task(base=DatabaseTask, bind=True, max_retries=3)
def execute_task(self, task_id: int) -> Dict[str, Any]:
    """Main Celery task executor."""
    return asyncio.run(_execute_task_async(self, task_id))


async def _execute_task_async(celery_task, task_id: int) -> Dict[str, Any]:
    """Async implementation of task execution."""
    
    async with AsyncSessionLocal() as db:
        try:
            task = await db.get(TaskModel, task_id)
            if not task:
                return {"success": False, "error": "Task not found"}
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            task.celery_task_id = celery_task.request.id
            await db.commit()
            
            account = task.account
            
            browser_manager = await get_browser_manager()
            
            session = await browser_manager.get_session(account.id)
            if not session:
                session = await browser_manager.create_session(
                    account_id=account.id,
                    user_agent=account.user_agent,
                    proxy_url=account.proxy_url,
                    cookies_json=account.cookies_json,
                    headless=True,
                )
            
            fb_actions = FacebookActions(browser_manager)
            
            result = await _execute_by_type(fb_actions, account.id, task)
            
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.result_data = result
            if not result.get("success"):
                task.error_message = result.get("message", "Unknown error")
            
            await db.commit()
            
            await _create_log(db, account.id, task.id, "INFO", 
                            f"Task completed: {result.get('message', 'Success')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            
            task = await db.get(TaskModel, task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.retry_count += 1
                task.error_message = str(e)
                
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.RETRYING
                    execute_task.apply_async(args=[task_id], countdown=60 * task.retry_count)
                
                await db.commit()
            
            await _create_log(db, task.account_id if task else None, task_id, 
                            "ERROR", f"Task failed: {str(e)}")
            
            try:
                raise self.retry(exc=e, countdown=60)
            except Exception:
                return {"success": False, "error": str(e)}


async def _execute_by_type(fb_actions: FacebookActions, account_id: int, 
                           task: TaskModel) -> Dict[str, Any]:
    """Route task to appropriate action handler."""
    
    task_type = task.task_type.value
    payload = task.payload or {}
    
    if task_type == "login":
        return await fb_actions.login(
            account_id,
            payload.get("email", ""),
            payload.get("password", "")
        )
    
    elif task_type == "post":
        return await fb_actions.create_post(
            account_id,
            payload.get("text", ""),
            payload.get("image_path")
        )
    
    elif task_type == "comment":
        return await fb_actions.comment_on_post(
            account_id,
            payload.get("post_url", ""),
            payload.get("text", "")
        )
    
    elif task_type == "like":
        return await fb_actions.like_post(
            account_id,
            payload.get("post_url", "")
        )
    
    elif task_type == "reply":
        return await fb_actions.reply_to_comments(
            account_id,
            payload.get("post_url", ""),
            payload.get("text", ""),
            payload.get("filter_positive", False)
        )
    
    elif task_type == "scroll_feed":
        return await fb_actions.scroll_feed(
            account_id,
            payload.get("scrolls", 5)
        )
    
    elif task_type == "bulk_action":
        results = []
        for sub_task in payload.get("sub_tasks", []):
            sub_result = await _execute_by_type(fb_actions, account_id, 
                                                 type('obj', (object,), {
                                                     'task_type': type('enum', (), {'value': sub_task.get("type")})(),
                                                     'payload': sub_task.get("payload", {})
                                                 })())
            results.append(sub_result)
        
        return {
            "success": all(r.get("success") for r in results),
            "results": results
        }
    
    else:
        if task.natural_instruction:
            return await fb_actions.execute_natural_instruction(
                account_id, task.natural_instruction
            )
        
        return {"success": False, "error": f"Unknown task type: {task_type}"}


async def _create_log(db, account_id: int, task_id: int,
                      level: str, message: str) -> None:
    """Create an activity log entry."""
    log = ActivityLog(
        account_id=account_id,
        task_id=task_id,
        log_level=level,
        message=message,
    )
    db.add(log)
    await db.commit()