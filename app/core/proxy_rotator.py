
# ============================================================
# PART 6: PROXY ROTATOR & CAPTCHA SOLVER
# ============================================================
# 📁 app/core/proxy_rotator.py
# 📁 app/core/captcha_solver.py

proxy_rotator_py = r'''"""
BOT-BOOK-POPY Proxy Rotator
============================
Manages proxy pools with health checking, rotation, and failover.

Features:
- Proxy health monitoring (latency, success rate)
- Automatic rotation per request or per session
- Geographic distribution tracking
- Blacklist management for failed proxies
- Bandwidth usage tracking
"""

import asyncio
import random
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.config import PROXY_ENABLED, PROXY_ROTATION_INTERVAL

logger = logging.getLogger(__name__)


@dataclass
class ProxyEntry:
    """Represents a single proxy with health metrics."""
    url: str
    type: str = "http"
    country: str = "unknown"
    latency_ms: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    is_blacklisted: bool = False
    blacklist_reason: Optional[str] = None
    blacklist_until: Optional[datetime] = None
    bandwidth_used_mb: float = 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total

    @property
    def is_available(self) -> bool:
        if self.is_blacklisted and self.blacklist_until:
            if datetime.utcnow() < self.blacklist_until:
                return False
            self.is_blacklisted = False
        return True


class ProxyRotator:
    """
    Intelligent proxy rotation system.

    Strategies:
    - "round_robin": Cycle through proxies in order
    - "random": Random selection
    - "weighted": Prefer proxies with higher success rates
    - "least_used": Prefer least recently used proxies
    - "geographic": Rotate by geographic region
    """

    def __init__(self, strategy: str = "weighted"):
        self.proxies: List[ProxyEntry] = []
        self.strategy = strategy
        self._index = 0
        self._lock = asyncio.Lock()
        self._health_check_task = None

    def add_proxy(self, url: str, proxy_type: str = "http", country: str = "unknown") -> None:
        """Add a proxy to the pool."""
        entry = ProxyEntry(url=url, type=proxy_type, country=country)
        self.proxies.append(entry)
        logger.info(f"Added proxy: {url} ({country})")

    def add_proxies_from_string(self, proxy_string: str) -> None:
        """Add multiple proxies from a comma-separated string."""
        for proxy in proxy_string.split(","):
            proxy = proxy.strip()
            if proxy:
                self.add_proxy(proxy)

    async def get_proxy(self, account_id: Optional[int] = None) -> Optional[ProxyEntry]:
        """Get the next proxy based on rotation strategy."""
        async with self._lock:
            available = [p for p in self.proxies if p.is_available]
            if not available:
                return None

            if self.strategy == "round_robin":
                proxy = available[self._index % len(available)]
                self._index += 1

            elif self.strategy == "random":
                proxy = random.choice(available)

            elif self.strategy == "weighted":
                # Weight by success rate + recency
                weights = []
                for p in available:
                    weight = p.success_rate * 100
                    if p.last_used:
                        hours_since = (datetime.utcnow() - p.last_used).total_seconds() / 3600
                        weight += hours_since * 10  # Prefer unused proxies
                    weights.append(max(weight, 1))
                proxy = random.choices(available, weights=weights, k=1)[0]

            elif self.strategy == "least_used":
                proxy = min(available, key=lambda p: p.last_used or datetime.min)

            else:
                proxy = available[0]

            proxy.last_used = datetime.utcnow()
            return proxy

    async def report_success(self, proxy_url: str) -> None:
        """Report successful proxy usage."""
        for p in self.proxies:
            if p.url == proxy_url:
                p.success_count += 1
                break

    async def report_failure(self, proxy_url: str, reason: str) -> None:
        """Report proxy failure and potentially blacklist."""
        for p in self.proxies:
            if p.url == proxy_url:
                p.failure_count += 1
                # Blacklist if failure rate is too high
                if p.success_rate < 0.3 and (p.success_count + p.failure_count) > 5:
                    p.is_blacklisted = True
                    p.blacklist_reason = reason
                    p.blacklist_until = datetime.utcnow() + timedelta(hours=1)
                    logger.warning(f"Blacklisted proxy {proxy_url}: {reason}")
                break

    async def health_check(self, test_url: str = "https://www.google.com") -> Dict[str, Any]:
        """Check health of all proxies."""
        results = {"checked": 0, "healthy": 0, "unhealthy": 0}

        async with aiohttp.ClientSession() as session:
            for proxy in self.proxies:
                if proxy.is_blacklisted:
                    continue

                try:
                    start = datetime.utcnow()
                    async with session.get(
                        test_url,
                        proxy=proxy.url,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        latency = (datetime.utcnow() - start).total_seconds() * 1000
                        proxy.latency_ms = latency
                        proxy.last_checked = datetime.utcnow()
                        proxy.success_count += 1
                        results["healthy"] += 1
                except Exception as e:
                    proxy.failure_count += 1
                    proxy.last_checked = datetime.utcnow()
                    results["unhealthy"] += 1
                    logger.debug(f"Proxy health check failed for {proxy.url}: {e}")

                results["checked"] += 1

        return results

    async def start_health_monitor(self, interval_seconds: int = 300):
        """Start background health monitoring."""
        while True:
            await asyncio.sleep(interval_seconds)
            await self.health_check()

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        total = len(self.proxies)
        available = len([p for p in self.proxies if p.is_available])
        blacklisted = len([p for p in self.proxies if p.is_blacklisted])
        avg_latency = sum(p.latency_ms for p in self.proxies if p.latency_ms > 0) / max(1, len([p for p in self.proxies if p.latency_ms > 0]))

        return {
            "total": total,
            "available": available,
            "blacklisted": blacklisted,
            "avg_latency_ms": round(avg_latency, 2),
            "strategy": self.strategy,
        }


# Singleton
_proxy_rotator = None


def get_proxy_rotator() -> ProxyRotator:
    global _proxy_rotator
    if _proxy_rotator is None:
        _proxy_rotator = ProxyRotator()
    return _proxy_rotator
'''

# ── captcha_solver.py ───────────────────────────────────────
captcha_solver_py = r'''"""
BOT-BOOK-POPY CAPTCHA Solver
=============================
Detects and handles various CAPTCHA challenges.

Supported CAPTCHA types:
- reCAPTCHA v2/v3
- hCaptcha
- Facebook native checkpoints
- Image-based challenges

Integration points for external solvers:
- 2captcha
- Anti-Captcha
- CapSolver
- Manual solving via WebSocket notification
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from playwright.async_api import Page

from app.config import CAPTCHA_SOLVER_ENABLED, CAPTCHA_API_KEY

logger = logging.getLogger(__name__)


class CaptchaType(Enum):
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    FACEBOOK_CHECKPOINT = "facebook_checkpoint"
    IMAGE_CHALLENGE = "image_challenge"
    UNKNOWN = "unknown"


@dataclass
class CaptchaChallenge:
    type: CaptchaType
    selector: Optional[str] = None
    site_key: Optional[str] = None
    page_url: Optional[str] = None
    iframe_url: Optional[str] = None
    screenshot_path: Optional[str] = None


class CaptchaDetector:
    """Detects CAPTCHA challenges on a page."""

    CAPTCHA_SELECTORS = {
        CaptchaType.RECAPTCHA_V2: [
            '.g-recaptcha',
            '[data-sitekey]',
            'iframe[src*="recaptcha"]',
            '#recaptcha-anchor',
        ],
        CaptchaType.HCAPTCHA: [
            '.h-captcha',
            'iframe[src*="hcaptcha"]',
            '[data-hcaptcha-widget-id]',
        ],
        CaptchaType.FACEBOOK_CHECKPOINT: [
            '[data-testid="checkpoint_title"]',
            'div[role="main"] h2:has-text("Security Check")',
            'form[action*="checkpoint"]',
            'input[name="approvals_code"]',
        ],
    }

    async def detect(self, page: Page) -> Optional[CaptchaChallenge]:
        """Scan page for CAPTCHA challenges."""
        for captcha_type, selectors in self.CAPTCHA_SELECTORS.items():
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        site_key = None
                        if captcha_type == CaptchaType.RECAPTCHA_V2:
                            site_key = await element.get_attribute("data-sitekey")

                        return CaptchaChallenge(
                            type=captcha_type,
                            selector=selector,
                            site_key=site_key,
                            page_url=page.url,
                        )
                except Exception:
                    continue

        # Check for Facebook security checkpoint by URL
        if "checkpoint" in page.url.lower():
            return CaptchaChallenge(
                type=CaptchaType.FACEBOOK_CHECKPOINT,
                page_url=page.url,
            )

        return None


class CaptchaSolver:
    """
    Handles CAPTCHA solving with multiple backends.

    Solving strategies:
    1. External API (2captcha, Anti-Captcha, CapSolver)
    2. Browser automation (click challenges)
    3. Manual solving via WebSocket notification
    4. Fallback: pause and alert operator
    """

    def __init__(self):
        self.detector = CaptchaDetector()
        self.api_key = CAPTCHA_API_KEY
        self.enabled = CAPTCHA_SOLVER_ENABLED

    async def solve(self, page: Page, challenge: CaptchaChallenge) -> bool:
        """
        Attempt to solve a CAPTCHA challenge.
        Returns True if solved, False otherwise.
        """
        if not self.enabled:
            logger.warning("CAPTCHA solver is disabled. Manual intervention required.")
            return False

        logger.info(f"Attempting to solve {challenge.type.value} CAPTCHA")

        if challenge.type == CaptchaType.FACEBOOK_CHECKPOINT:
            return await self._solve_facebook_checkpoint(page, challenge)

        if challenge.type in (CaptchaType.RECAPTCHA_V2, CaptchaType.HCAPTCHA):
            return await self._solve_external_api(page, challenge)

        # Unknown type - try generic approach
        return await self._solve_generic(page, challenge)

    async def _solve_facebook_checkpoint(self, page: Page, challenge: CaptchaChallenge) -> bool:
        """Handle Facebook security checkpoint."""
        logger.info("Facebook checkpoint detected - requires manual intervention")

        # Take screenshot for operator
        screenshot_path = f"data/screenshots/captcha_{asyncio.get_event_loop().time()}.png"
        await page.screenshot(path=screenshot_path)

        # TODO: Send WebSocket notification to operator
        # TODO: Wait for manual code input

        # For now, log and return False
        logger.warning(f"Checkpoint screenshot saved: {screenshot_path}")
        return False

    async def _solve_external_api(self, page: Page, challenge: CaptchaChallenge) -> bool:
        """Solve using external CAPTCHA solving service."""
        if not self.api_key:
            logger.warning("No CAPTCHA API key configured")
            return False

        # TODO: Implement 2captcha/Anti-Captcha API integration
        # This would:
        # 1. Send site_key + page_url to API
        # 2. Poll for solution
        # 3. Inject solution into page
        # 4. Submit form

        logger.info("External CAPTCHA solving not yet implemented")
        return False

    async def _solve_generic(self, page: Page, challenge: CaptchaChallenge) -> bool:
        """Generic fallback solver."""
        logger.warning(f"No specific solver for {challenge.type.value}")
        return False

    async def wait_and_solve(self, page: Page, timeout: int = 30) -> bool:
        """
        Wait for CAPTCHA to appear and attempt to solve it.
        Returns True if no CAPTCHA or solved successfully.
        """
        challenge = await self.detector.detect(page)
        if not challenge:
            return True  # No CAPTCHA detected

        return await self.solve(page, challenge)


# Singleton
_captcha_solver = None


def get_captcha_solver() -> CaptchaSolver:
    global _captcha_solver
    if _captcha_solver is None:
        _captcha_solver = CaptchaSolver()
    return _captcha_solver
'''

os.makedirs(f"{base_dir}/app/core", exist_ok=True)
with open(f"{base_dir}/app/core/proxy_rotator.py", "w") as f:
    f.write(proxy_rotator_py)
with open(f"{base_dir}/app/core/captcha_solver.py", "w") as f:
    f.write(captcha_solver_py)

print("✅ Part 6: Additional Core Modules created")
print("   📁 app/core/proxy_rotator.py  — Proxy health-check + rotation")
print("   📁 app/core/captcha_solver.py  — CAPTCHA detection & solving")
