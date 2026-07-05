# ── schemas.py ───────────────────────────────────────────
schemas_py = r'''"""
BOT-BOOK-POPY Pydantic Schemas
===============================
Request/response models for API validation and serialization.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, EmailStr


# ── Account Schemas ────────────────────────────────────────

class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    proxy_url: Optional[str] = None
    proxy_type: Optional[str] = "http"
    notes: Optional[str] = None
    daily_action_limit: int = Field(default=50, ge=1, le=500)


class AccountCreate(AccountBase):
    password: Optional[str] = None
    cookies_json: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    cookies_json: Optional[str] = None
    proxy_url: Optional[str] = None
    proxy_type: Optional[str] = None
    status: Optional[str] = None
    daily_action_limit: Optional[int] = None
    notes: Optional[str] = None


class AccountResponse(AccountBase):
    id: int
    status: str
    last_activity: Optional[datetime] = None
    last_login: Optional[datetime] = None
    fingerprint_health_score: float
    action_count_today: int
    created_at: datetime
    updated_at: datetime
    user_agent: Optional[str] = None
    fingerprint_profile: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    accounts: List[AccountResponse]
    total: int


# ── Task Schemas ───────────────────────────────────────────

class TaskBase(BaseModel):
    account_id: int
    task_type: str = Field(
        ...,
        pattern="^(post|comment|like|reply|share|friend_request|scroll_feed|login|logout|bulk_action)$"
    )
    payload: Dict[str, Any] = Field(default_factory=dict)
    natural_instruction: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    max_retries: int = Field(default=3, ge=0, le=10)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    max_retries: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    celery_task_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    pending: int
    running: int
    completed: int
    failed: int


# ── Log Schemas ────────────────────────────────────────────

class LogResponse(BaseModel):
    id: int
    account_id: Optional[int] = None
    task_id: Optional[int] = None
    log_level: str
    message: str
    url: Optional[str] = None
    action_taken: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    logs: List[LogResponse]
    total: int


# ── Settings Schemas ───────────────────────────────────────

class SettingsResponse(BaseModel):
    id: int
    stealth_level: str
    enable_webgl_spoof: bool
    enable_canvas_noise: bool
    enable_webrtc_block: bool
    enable_font_randomization: bool
    humanoid_enabled: bool
    typing_simulation: bool
    mouse_simulation: bool
    scroll_simulation: bool
    global_daily_limit: int
    per_account_daily_limit: int
    cooldown_between_actions: float
    proxy_rotation_enabled: bool
    proxy_test_url: str
    notify_on_failure: bool
    notify_on_checkpoint: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    stealth_level: Optional[str] = None
    enable_webgl_spoof: Optional[bool] = None
    enable_canvas_noise: Optional[bool] = None
    enable_webrtc_block: Optional[bool] = None
    enable_font_randomization: Optional[bool] = None
    humanoid_enabled: Optional[bool] = None
    typing_simulation: Optional[bool] = None
    mouse_simulation: Optional[bool] = None
    scroll_simulation: Optional[bool] = None
    global_daily_limit: Optional[int] = None
    per_account_daily_limit: Optional[int] = None
    cooldown_between_actions: Optional[float] = None
    proxy_rotation_enabled: Optional[bool] = None
    proxy_test_url: Optional[str] = None
    notify_on_failure: Optional[bool] = None
    notify_on_checkpoint: Optional[bool] = None


# ── Dashboard Schemas ────────────────────────────────────

class DashboardStats(BaseModel):
    total_accounts: int
    active_accounts: int
    total_tasks_today: int
    completed_tasks_today: int
    failed_tasks_today: int
    success_rate: float
    avg_fingerprint_health: float
    queue_length: int
    active_workers: int


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
'''

os.makedirs(f"{base_dir}/app/models", exist_ok=True)
with open(f"{base_dir}/app/models/database.py", "w") as f:
    f.write(database_py)
with open(f"{base_dir}/app/models/models.py", "w") as f:
    f.write(models_py)
with open(f"{base_dir}/app/models/schemas.py", "w") as f:
    f.write(schemas_py)
