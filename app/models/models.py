# ── models.py ───────────────────────────────────────────
models_py = r'''"""
BOT-BOOK-POPY SQLAlchemy Models
================================
Core database models for accounts, tasks, logs, and settings.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, JSON, Enum, Float
)
from sqlalchemy.orm import relationship
from app.models.database import Base


class AccountStatus(str, enum.Enum):
    """Account lifecycle states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CHECKPOINT = "checkpoint"
    BANNED = "banned"
    COOLDOWN = "cooldown"


class TaskStatus(str, enum.Enum):
    """Task execution states."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskType(str, enum.Enum):
    """Supported automation actions."""
    POST = "post"
    COMMENT = "comment"
    LIKE = "like"
    REPLY = "reply"
    SHARE = "share"
    FRIEND_REQUEST = "friend_request"
    SCROLL_FEED = "scroll_feed"
    LOGIN = "login"
    LOGOUT = "logout"
    BULK_ACTION = "bulk_action"


class FacebookAccount(Base):
    """
    Represents a managed Facebook account with full isolation configuration.
    Each account gets its own browser profile directory for zero leakage.
    """
    __tablename__ = "facebook_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Unnamed Account")
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_encrypted = Column(Text, nullable=True)
    cookies_json = Column(Text, nullable=True)

    proxy_url = Column(String(500), nullable=True)
    proxy_type = Column(String(20), default="http")

    fingerprint_profile = Column(JSON, nullable=True)
    user_agent = Column(String(500), nullable=True)
    profile_dir = Column(String(500), nullable=True)

    status = Column(Enum(AccountStatus), default=AccountStatus.INACTIVE)
    last_activity = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)

    fingerprint_health_score = Column(Float, default=100.0)
    action_count_today = Column(Integer, default=0)
    daily_action_limit = Column(Integer, default=50)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)

    tasks = relationship("Task", back_populates="account", cascade="all, delete-orphan")
    logs = relationship("ActivityLog", back_populates="account", cascade="all, delete-orphan")


class Task(Base):
    """
    Represents an automation task queued for execution.
    Tasks are picked up by Celery workers and executed against specific accounts.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("facebook_accounts.id"), nullable=False)

    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    payload = Column(JSON, default=dict)
    natural_instruction = Column(Text, nullable=True)

    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    screenshot_path = Column(String(500), nullable=True)

    celery_task_id = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("FacebookAccount", back_populates="tasks")
    logs = relationship("ActivityLog", back_populates="task", cascade="all, delete-orphan")


class ActivityLog(Base):
    """
    Detailed activity log for auditing and debugging.
    Every significant action is logged with screenshots and context.
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("facebook_accounts.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    log_level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)

    url = Column(String(1000), nullable=True)
    selector = Column(String(500), nullable=True)
    action_taken = Column(String(100), nullable=True)

    screenshot_path = Column(String(500), nullable=True)
    page_source_snippet = Column(Text, nullable=True)

    fingerprint_snapshot = Column(JSON, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    account = relationship("FacebookAccount", back_populates="logs")
    task = relationship("Task", back_populates="logs")


class GlobalSettings(Base):
    """
    Global framework settings persisted in database.
    """
    __tablename__ = "global_settings"

    id = Column(Integer, primary_key=True)

    stealth_level = Column(String(20), default="high")
    enable_webgl_spoof = Column(Boolean, default=True)
    enable_canvas_noise = Column(Boolean, default=True)
    enable_webrtc_block = Column(Boolean, default=True)
    enable_font_randomization = Column(Boolean, default=True)

    humanoid_enabled = Column(Boolean, default=True)
    typing_simulation = Column(Boolean, default=True)
    mouse_simulation = Column(Boolean, default=True)
    scroll_simulation = Column(Boolean, default=True)

    global_daily_limit = Column(Integer, default=1000)
    per_account_daily_limit = Column(Integer, default=50)
    cooldown_between_actions = Column(Float, default=5.0)

    proxy_rotation_enabled = Column(Boolean, default=False)
    proxy_test_url = Column(String(500), default="https://www.google.com")

    webhook_url = Column(String(500), nullable=True)
    notify_on_failure = Column(Boolean, default=True)
    notify_on_checkpoint = Column(Boolean, default=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
'''