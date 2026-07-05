screenshot_utils_py = r'''"""
BOT-BOOK-POPY Screenshot Utilities
===================================
Enhanced screenshot capture with annotations and metadata.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from app.config import SCREENSHOTS_DIR


class ScreenshotAnnotator:
    """Annotates screenshots with metadata overlays."""

    def __init__(self):
        self.font = None
        if PIL_AVAILABLE:
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except Exception:
                self.font = ImageFont.load_default()

    def annotate(self, image_path: str, metadata: Dict[str, Any]) -> str:
        """Add metadata overlay to screenshot."""
        if not PIL_AVAILABLE:
            return image_path

        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)

            # Semi-transparent overlay at bottom
            overlay_height = 60
            draw.rectangle(
                [(0, img.height - overlay_height), (img.width, img.height)],
                fill=(0, 0, 0, 180)
            )

            # Text
            text = f"Account: {metadata.get('account_id', 'N/A')} | "
            text += f"Action: {metadata.get('action', 'N/A')} | "
            text += f"Time: {datetime.utcnow().strftime('%H:%M:%S')}"

            draw.text((10, img.height - overlay_height + 10), text,
                     fill=(255, 255, 255), font=self.font)

            # Save annotated version
            annotated_path = str(Path(image_path).with_suffix('')) + "_annotated.png"
            img.save(annotated_path)
            return annotated_path

        except Exception:
            return image_path


def generate_screenshot_path(account_id: int, action: str) -> str:
    """Generate a standardized screenshot path."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"acc_{account_id}_{action}_{timestamp}.png"
    return str(SCREENSHOTS_DIR / filename)
'''

validators_py = r'''"""
BOT-BOOK-POPY Validators
=========================
Input validation helpers.
"""

import re
from typing import Optional


class Validators:
    """Input validation utilities."""

    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PROXY_REGEX = re.compile(
        r'^(http|https|socks4|socks5)://'
        r'(?:([^:@]+):([^@]+)@)?'
        r'([^:/]+):(\d+)$'
    )
    URL_REGEX = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        return bool(cls.EMAIL_REGEX.match(email))

    @classmethod
    def is_valid_proxy(cls, proxy_url: str) -> bool:
        return bool(cls.PROXY_REGEX.match(proxy_url))

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        return bool(cls.URL_REGEX.match(url))

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize a string for use as a filename."""
        return re.sub(r'[^\w\-_.]', '_', filename)

    @classmethod
    def validate_facebook_url(cls, url: str) -> bool:
        """Check if URL is a valid Facebook URL."""
        return "facebook.com" in url.lower() or "fb.com" in url.lower()
'''

os.makedirs(f"{base_dir}/app/utils", exist_ok=True)
with open(f"{base_dir}/app/utils/crypto.py", "w") as f:
    f.write(crypto_py)
with open(f"{base_dir}/app/utils/logger.py", "w") as f:
    f.write(logger_py)
with open(f"{base_dir}/app/utils/screenshot_utils.py", "w") as f:
    f.write(screenshot_utils_py)
with open(f"{base_dir}/app/utils/validators.py", "w") as f:
    f.write(validators_py)