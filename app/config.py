
import os

base_dir = "/mnt/agents/output/bot-book-popy-v2"
os.makedirs(base_dir, exist_ok=True)

# ============================================================
# PART 1: CONFIGURATION & ENVIRONMENT
# ============================================================
# 📁 app/config.py

config_py = r'''"""
BOT-BOOK-POPY Configuration Module
=====================================
Centralized configuration loaded from environment variables.
All paths are resolved relative to project root for portability.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# ── Base Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROFILES_DIR = DATA_DIR / "profiles"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
LOGS_DIR = DATA_DIR / "logs"

# Auto-create directories
for d in [DATA_DIR, PROFILES_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Database ────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/botbook.db")

# ── Redis / Celery ────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", "300"))
CELERY_WORKER_CONCURRENCY = int(os.getenv("CELERY_WORKER_CONCURRENCY", "4"))

# ── Server ──────────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "bot-book-popy-secret-key-change-in-production")

# ── CORS ──────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ── Stealth Engine ──────────────────────────────────────────
USER_AGENT_POOL: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

VIEWPORT_PROFILES = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 720},
]

LOCALE_POOL = [
    "en-US", "en-GB", "es-ES", "fr-FR", "de-DE",
    "it-IT", "pt-BR", "nl-NL", "pl-PL", "ru-RU",
]

TIMEZONE_POOL = [
    "America/New_York", "America/Los_Angeles", "America/Chicago",
    "Europe/London", "Europe/Paris", "Europe/Berlin",
    "Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney",
]

HARDWARE_CONCURRENCY_POOL = [4, 6, 8, 12, 16]
DEVICE_MEMORY_POOL = [4, 8, 16, 32]

# ── Humanoid Module ───────────────────────────────────────
MIN_DELAY_MS = int(os.getenv("MIN_DELAY_MS", "500"))
MAX_DELAY_MS = int(os.getenv("MAX_DELAY_MS", "3000"))
TYPING_SPEED_MIN = float(os.getenv("TYPING_SPEED_MIN", "0.05"))
TYPING_SPEED_MAX = float(os.getenv("TYPING_SPEED_MAX", "0.25"))
TYPING_ERROR_RATE = float(os.getenv("TYPING_ERROR_RATE", "0.02"))
MOUSE_OVERSHOOT_CHANCE = float(os.getenv("MOUSE_OVERSHOOT_CHANCE", "0.15"))

# ── Facebook ────────────────────────────────────────────────
FB_BASE_URL = "https://www.facebook.com"
FB_LOGIN_URL = f"{FB_BASE_URL}/login"
FB_HOME_URL = f"{FB_BASE_URL}/"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY_BASE = float(os.getenv("RETRY_DELAY_BASE", "2.0"))

# ── Proxy ───────────────────────────────────────────────────
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False").lower() == "true"
PROXY_ROTATION_INTERVAL = int(os.getenv("PROXY_ROTATION_INTERVAL", "300"))

# ── Logging ───────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# ── Security ────────────────────────────────────────────────
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", None)

# ── CAPTCHA ─────────────────────────────────────────────────
CAPTCHA_SOLVER_ENABLED = os.getenv("CAPTCHA_SOLVER_ENABLED", "False").lower() == "true"
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY", "")

# ── Notifications ───────────────────────────────────────────
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
NOTIFY_ON_FAILURE = os.getenv("NOTIFY_ON_FAILURE", "True").lower() == "true"
NOTIFY_ON_CHECKPOINT = os.getenv("NOTIFY_ON_CHECKPOINT", "True").lower() == "true"
'''

os.makedirs(f"{base_dir}/app", exist_ok=True)
with open(f"{base_dir}/app/config.py", "w") as f:
    f.write(config_py)

print("✅ Part 1: app/config.py — Configuration module created")
