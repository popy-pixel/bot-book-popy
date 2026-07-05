logger_py = r'''"""
BOT-BOOK-POPY Logger
=====================
Structured JSON logging for production observability.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

from app.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "account_id"):
            log_data["account_id"] = record.account_id
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


def setup_logging():
    """Configure application logging."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if LOG_FORMAT == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # File handler
    log_file = LOGS_DIR / "botbook.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(JSONFormatter())

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
'''