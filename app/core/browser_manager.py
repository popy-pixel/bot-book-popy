
# ============================================================
# PART 5: BROWSER MANAGER (Isolated Contexts) — FIXED
# ============================================================
# 📁 app/core/browser_manager.py
# 
# CRITICAL FIX: Playwright's `browser.new_context()` does NOT accept
# `user_data_dir`. Persistent storage requires `launch_persistent_context()`.
# We use `launch_persistent_context()` per account for true isolation.
# See: playwright.dev/python/docs/api/class-browsertype

browser_manager_py = r'''"""
BOT-BOOK-POPY Browser Manager
==============================
Manages isolated Playwright browser contexts for each Facebook account.

CRITICAL DESIGN PRINCIPLES:
1. ZERO LEAKAGE: Each account gets its own user_data_dir via launch_persistent_context
2. FINGERPRINT ISOLATION: Each account has a unique, coherent fingerprint
3. PROXY ISOLATION: Each account can use a different proxy
4. COOKIE PERSISTENCE: Cookies are saved and restored per account
5. SESSION WARM-UP: Each new session performs human-like warm-up

This is the foundation of the anti-detection architecture.
Without proper isolation, Facebook can link accounts via:
- Shared browser storage (cookies, localStorage, IndexedDB)
- Shared fingerprint properties
- Shared IP addresses
- Shared TLS session tickets

IMPORTANT: We use `chromium.launch_persistent_context()` instead of
`browser.new_context()` because `new_context()` does NOT support user_data_dir.
Persistent contexts are required for:
- Cookie persistence across sessions
- localStorage / IndexedDB isolation
- Service worker isolation
- Login session persistence
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from playwright.async_api import async_playwright, BrowserContext, Page

from app.config import PROFILES_DIR, SCREENSHOTS_DIR, FB_BASE_URL
from app.core.stealth_engine import get_stealth_engine, FingerprintProfile
from app.core.humanoid import get_humanoid_engine

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """
    Represents an active browser session for a specific account.
    
    When using persistent context, the context IS the browser.
    Closing the context closes the browser automatically.
    """
    account_id: int
    context: BrowserContext  # Persistent context (also acts as browser)
    page: Page
    profile: FingerprintProfile
    humanoid: Any
    created_at: datetime
    last_activity: datetime
    is_logged_in: bool = False
    profile_dir: Path = None

    @property
    def is_active(self) -> bool:
        """Check if the session is still usable."""
        try:
            # Persistent context pages check
            return len(self.context.pages) > 0
        except Exception:
            return False


class BrowserManager:
    """
    Central manager for all browser sessions.

    Architecture:
    - Each account gets ONE active session at a time
    - Sessions are created on-demand and cached
    - Idle sessions are closed after timeout to save resources
    - All sessions are completely isolated from each other

    Isolation Layers:
    1. Process level: Each persistent context is a separate Chromium process
    2. Profile level: Each account has its own user_data_dir
    3. Context level: Each account has its own persistent BrowserContext
    4. Network level: Each account can use a different proxy
    5. Fingerprint level: Each account has unique browser fingerprint
    """

    def __init__(self):
        self._sessions: Dict[int, BrowserSession] = {}
        self._playwright = None
        self._lock = asyncio.Lock()
        self._cleanup_task = None

    async def initialize(self):
        """Initialize the Playwright instance."""
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            logger.info("Playwright initialized")

        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def create_session(
        self,
        account_id: int,
        user_agent: Optional[str] = None,
        proxy_url: Optional[str] = None,
        cookies_json: Optional[str] = None,
        headless: bool = True,
    ) -> BrowserSession:
        """
        Create a new isolated browser session for an account.

        Uses `launch_persistent_context()` for TRUE isolation:
        - Unique user_data_dir per account
        - Persistent cookies, localStorage, IndexedDB
        - Separate browser process
        - No shared state between accounts
        """
        async with self._lock:
            # Close existing session if any
            if account_id in self._sessions:
                await self.close_session(account_id)

            # Generate unique profile directory
            profile_dir = PROFILES_DIR / f"account_{account_id}"
            profile_dir.mkdir(parents=True, exist_ok=True)

            # Generate stealth fingerprint
            stealth_engine = get_stealth_engine()
            fingerprint = stealth_engine.generate_profile(user_agent)

            # Build browser launch args
            args = stealth_engine.get_browser_args(fingerprint)

            # Proxy configuration
            proxy_config = None
            if proxy_url:
                proxy_config = {"server": proxy_url}

            # Build context options (for persistent context)
            context_options = stealth_engine.get_context_options(fingerprint)

            # ── CRITICAL: Use launch_persistent_context for true isolation ──
            # browser.new_context() does NOT support user_data_dir
            # launch_persistent_context creates a persistent browser context
            # with its own user_data_dir, cookies, localStorage, etc.
            persistent_context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=headless,
                args=args,
                proxy=proxy_config,
                # Pass context options that persistent context accepts
                viewport=context_options.get("viewport"),
                screen=context_options.get("screen"),
                user_agent=context_options.get("user_agent"),
                locale=context_options.get("locale"),
                timezone_id=context_options.get("timezone_id"),
                geolocation=context_options.get("geolocation"),
                permissions=context_options.get("permissions"),
                color_scheme=context_options.get("color_scheme"),
                has_touch=context_options.get("has_touch"),
                is_mobile=context_options.get("is_mobile"),
                java_script_enabled=context_options.get("java_script_enabled"),
                extra_http_headers=context_options.get("extra_http_headers"),
                # Security settings
                accept_downloads=True,
                bypass_csp=False,
                ignore_https_errors=False,
            )

            # Apply stealth script to ALL pages in context
            stealth_script = stealth_engine.get_stealth_script(fingerprint)
            await persistent_context.add_init_script(stealth_script)

            # Get or create initial page
            pages = persistent_context.pages
            if pages:
                page = pages[0]
            else:
                page = await persistent_context.new_page()

            # Restore cookies if provided (persistent context may already have them)
            if cookies_json:
                try:
                    cookies = json.loads(cookies_json)
                    await persistent_context.add_cookies(cookies)
                    logger.info(f"Restored {len(cookies)} cookies for account {account_id}")
                except Exception as e:
                    logger.warning(f"Failed to restore cookies for account {account_id}: {e}")

            # Initialize humanoid engine
            humanoid = get_humanoid_engine(f"account_{account_id}")

            # Create session
            now = datetime.utcnow()
            session = BrowserSession(
                account_id=account_id,
                context=persistent_context,
                page=page,
                profile=fingerprint,
                humanoid=humanoid,
                created_at=now,
                last_activity=now,
                profile_dir=profile_dir,
            )

            self._sessions[account_id] = session
            logger.info(
                f"Created persistent browser session for account {account_id} "
                f"with profile {fingerprint.profile_hash} @ {profile_dir}"
            )

            return session

    async def get_session(self, account_id: int) -> Optional[BrowserSession]:
        """Get an existing session or None if not found/inactive."""
        session = self._sessions.get(account_id)
        if session and session.is_active:
            session.last_activity = datetime.utcnow()
            return session
        # Clean up stale session reference
        if session and not session.is_active:
            self._sessions.pop(account_id, None)
        return None

    async def close_session(self, account_id: int) -> None:
        """Close a specific account's browser session."""
        async with self._lock:
            session = self._sessions.pop(account_id, None)
            if session:
                try:
                    # Save cookies before closing
                    cookies = await session.context.cookies()
                    cookies_path = session.profile_dir / "cookies.json"
                    with open(cookies_path, "w") as f:
                        json.dump(cookies, f)

                    # Close persistent context (this closes the browser too)
                    await session.context.close()
                    logger.info(f"Closed browser session for account {account_id}")
                except Exception as e:
                    logger.error(f"Error closing session for account {account_id}: {e}")

    async def close_all_sessions(self) -> None:
        """Close all active browser sessions."""
        account_ids = list(self._sessions.keys())
        for account_id in account_ids:
            await self.close_session(account_id)

    async def take_screenshot(self, account_id: int,
                               name: Optional[str] = None) -> str:
        """Take a screenshot of the current page."""
        session = await self.get_session(account_id)
        if not session:
            raise ValueError(f"No active session for account {account_id}")

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"account_{account_id}_{name or 'screenshot'}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        await session.page.screenshot(path=str(filepath), full_page=False)
        logger.info(f"Screenshot saved: {filepath}")

        return str(filepath)

    async def get_page_content(self, account_id: int) -> str:
        """Get the current page HTML content."""
        session = await self.get_session(account_id)
        if not session:
            raise ValueError(f"No active session for account {account_id}")

        return await session.page.content()

    async def navigate(self, account_id: int, url: str,
                       wait_until: str = "networkidle") -> None:
        """Navigate to a URL with human-like behavior."""
        session = await self.get_session(account_id)
        if not session:
            raise ValueError(f"No active session for account {account_id}")

        await session.humanoid.random_delay(300, 800, context="click")
        await session.page.goto(url, wait_until=wait_until)
        session.last_activity = datetime.utcnow()

        # Session warm-up on first navigation
        await session.humanoid.session_warmup(session.page)

    async def execute_action(self, account_id: int, action: str,
                             **kwargs) -> Any:
        """
        Execute a humanoid action on the page.

        Actions: click, type, scroll, move_mouse, hover, reading_pause
        """
        session = await self.get_session(account_id)
        if not session:
            raise ValueError(f"No active session for account {account_id}")

        humanoid = session.humanoid
        page = session.page

        if action == "click":
            selector = kwargs.get("selector")
            x, y = kwargs.get("x"), kwargs.get("y")
            await humanoid.human_click(page, selector=selector, x=x, y=y)

        elif action == "type":
            text = kwargs.get("text", "")
            selector = kwargs.get("selector")
            await humanoid.human_typing(page, text, selector=selector)

        elif action == "scroll":
            direction = kwargs.get("direction", "down")
            amount = kwargs.get("amount")
            await humanoid.human_scroll(page, direction=direction, amount=amount)

        elif action == "move_mouse":
            x = kwargs.get("x", 0)
            y = kwargs.get("y", 0)
            speed = kwargs.get("speed_profile", "medium")
            await humanoid.natural_mouse_move(page, x, y, speed)

        elif action == "hover":
            selector = kwargs.get("selector")
            if selector:
                await humanoid.natural_mouse_move_to_element(page, selector)

        elif action == "reading_pause":
            min_time = kwargs.get("min_time", 2.0)
            max_time = kwargs.get("max_time", 8.0)
            await humanoid.simulate_reading(page, min_time, max_time)

        session.last_activity = datetime.utcnow()
        return {"status": "success", "action": action}

    async def get_cookies(self, account_id: int) -> List[Dict[str, Any]]:
        """Get current cookies from the session."""
        session = await self.get_session(account_id)
        if not session:
            return []

        return await session.context.cookies()

    async def save_cookies(self, account_id: int) -> str:
        """Save cookies to file and return JSON string."""
        cookies = await self.get_cookies(account_id)
        return json.dumps(cookies)

    async def _cleanup_loop(self):
        """Background task to close idle sessions."""
        while True:
            await asyncio.sleep(300)  # Check every 5 minutes

            now = datetime.utcnow()
            to_close = []

            for account_id, session in self._sessions.items():
                idle_time = (now - session.last_activity).total_seconds()
                if idle_time > 1800:  # 30 minutes idle timeout
                    to_close.append(account_id)

            for account_id in to_close:
                logger.info(f"Closing idle session for account {account_id}")
                await self.close_session(account_id)

    async def shutdown(self):
        """Graceful shutdown of all sessions."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        await self.close_all_sessions()

        if self._playwright:
            await self._playwright.stop()
            logger.info("Playwright stopped")


# Singleton instance
_browser_manager = None


async def get_browser_manager() -> BrowserManager:
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
        await _browser_manager.initialize()
    return _browser_manager
'''

with open(f"{base_dir}/app/core/browser_manager.py", "w") as f:
    f.write(browser_manager_py)

print("✅ Part 5: app/core/browser_manager.py — Browser Manager created")
print("   • FIXED: Uses launch_persistent_context() for true isolation")
print("   • Per-account user_data_dir with persistent cookies/storage")
print("   • Automatic idle session cleanup")
print("   • Screenshot capture system")
print("   • No shared state between accounts")
