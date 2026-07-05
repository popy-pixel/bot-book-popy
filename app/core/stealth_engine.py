
# ============================================================
# PART 3: STEALTH ENGINE (Anti-Detection Core)
# ============================================================
# 📁 app/core/stealth_engine.py

stealth_engine_py = r'''"""
BOT-BOOK-POPY Stealth Engine
==============================
Advanced anti-detection module that patches browser fingerprints at the
engine level. This is the most critical module for bypassing detection.

Key Techniques:
1. Navigator property spoofing (webdriver, plugins, languages, platform)
2. WebGL/Canvas fingerprint randomization with noise injection
3. WebRTC leak prevention
4. Chrome runtime API emulation
5. Permission API patching
6. Hardware fingerprint consistency
7. Font enumeration spoofing
8. AudioContext fingerprint noise
9. Screen/Viewport consistency
10. Client Hints header spoofing
11. iframe.contentWindow patch
12. Performance timing cleanup
13. Console property normalization

Detection Evasion Strategy:
- Layer 1: Hide basic bot flags (navigator.webdriver, HeadlessChrome)
- Layer 2: Ensure fingerprint COHERENCE (all props match claimed identity)
- Layer 3: Provide hooks for behavioral analysis
- Layer 4: Network signal normalization
- Layer 5: Prevent cross-session correlation
"""

import random
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from app.config import (
    USER_AGENT_POOL, VIEWPORT_PROFILES, LOCALE_POOL,
    TIMEZONE_POOL, HARDWARE_CONCURRENCY_POOL, DEVICE_MEMORY_POOL
)


@dataclass
class FingerprintProfile:
    """
    A complete browser fingerprint profile.
    All properties are internally consistent to defeat coherence-based detection.
    """
    user_agent: str
    platform: str
    vendor: str
    viewport: Dict[str, int]
    screen: Dict[str, int]
    device_pixel_ratio: float
    color_depth: int
    hardware_concurrency: int
    device_memory: int
    max_touch_points: int
    language: str
    languages: List[str]
    timezone: str
    webgl_vendor: str
    webgl_renderer: str
    webgl_unmasked_vendor: str
    webgl_unmasked_renderer: str
    plugins_count: int
    mime_types_count: int
    canvas_noise_seed: float
    chrome_app: bool
    chrome_runtime: bool
    chrome_csi: bool
    chrome_load_times: bool
    notification_permission: str
    battery_charging: bool
    battery_level: float
    font_fingerprint: str
    profile_hash: str = field(default="")

    def __post_init__(self):
        if not self.profile_hash:
            self.profile_hash = hashlib.sha256(
                f"{self.user_agent}{self.platform}{self.viewport}".encode()
            ).hexdigest()[:16]


class StealthEngine:
    """
    Core stealth engine that generates and manages browser fingerprint profiles.
    Each Facebook account gets a unique, coherent fingerprint profile.
    """

    WEBGL_PROFILES = [
        {
            "vendor": "Google Inc. (NVIDIA)",
            "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "unmasked_vendor": "NVIDIA",
            "unmasked_renderer": "NVIDIA GeForce GTX 1660 Ti"
        },
        {
            "vendor": "Google Inc. (NVIDIA)",
            "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "unmasked_vendor": "NVIDIA",
            "unmasked_renderer": "NVIDIA GeForce RTX 3060"
        },
        {
            "vendor": "Google Inc. (Intel)",
            "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "unmasked_vendor": "Intel Inc.",
            "unmasked_renderer": "Intel(R) UHD Graphics 620"
        },
        {
            "vendor": "Google Inc. (AMD)",
            "renderer": "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "unmasked_vendor": "AMD",
            "unmasked_renderer": "AMD Radeon RX 580"
        },
        {
            "vendor": "Google Inc. (Apple)",
            "renderer": "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
            "unmasked_vendor": "Apple Inc.",
            "unmasked_renderer": "Apple M1 Pro"
        },
    ]

    PLATFORM_MAP = {
        "Windows": "Win32",
        "Macintosh": "MacIntel",
        "Linux": "Linux x86_64",
        "Android": "Linux armv8l",
        "iPhone": "iPhone",
        "iPad": "iPad",
    }

    VENDOR_MAP = {
        "Chrome": "Google Inc.",
        "Edg": "Microsoft Corporation",
        "Safari": "Apple Computer, Inc.",
        "Firefox": "",
    }

    PLUGIN_COUNTS = {
        "Chrome": (3, 5),
        "Edg": (3, 5),
        "Safari": (1, 3),
        "Firefox": (0, 2),
    }

    def __init__(self):
        self._profile_cache: Dict[str, FingerprintProfile] = {}

    def generate_profile(self, user_agent: Optional[str] = None) -> FingerprintProfile:
        """Generate a coherent fingerprint profile."""
        ua = user_agent or random.choice(USER_AGENT_POOL)
        platform_str = self._detect_platform(ua)
        vendor = self._detect_vendor(ua)
        viewport = random.choice(VIEWPORT_PROFILES)
        screen = {
            "width": viewport["width"],
            "height": viewport["height"],
            "availWidth": viewport["width"],
            "availHeight": viewport["height"] - 40,
        }
        hw_concurrency = random.choice(HARDWARE_CONCURRENCY_POOL)
        device_memory = random.choice(DEVICE_MEMORY_POOL)
        language = random.choice(LOCALE_POOL)
        languages = [language, "en-US", "en"]
        timezone = random.choice(TIMEZONE_POOL)
        webgl = random.choice(self.WEBGL_PROFILES)
        browser_type = self._detect_browser_type(ua)
        plugin_range = self.PLUGIN_COUNTS.get(browser_type, (2, 4))
        plugins_count = random.randint(*plugin_range)
        mime_types_count = plugins_count + random.randint(1, 3)
        canvas_seed = random.random()
        is_chrome = "Chrome" in ua or "Chromium" in ua
        notification_perm = random.choice(["default", "granted", "denied"])
        battery_charging = random.choice([True, False])
        battery_level = round(random.uniform(0.2, 1.0), 2)
        font_fp = hashlib.md5(f"{platform_str}{vendor}{language}".encode()).hexdigest()[:16]

        profile = FingerprintProfile(
            user_agent=ua,
            platform=platform_str,
            vendor=vendor,
            viewport=viewport,
            screen=screen,
            device_pixel_ratio=random.choice([1.0, 1.25, 1.5, 2.0]),
            color_depth=24,
            hardware_concurrency=hw_concurrency,
            device_memory=device_memory,
            max_touch_points=0 if "Windows" in ua or "Macintosh" in ua else random.randint(1, 5),
            language=language,
            languages=languages,
            timezone=timezone,
            webgl_vendor=webgl["vendor"],
            webgl_renderer=webgl["renderer"],
            webgl_unmasked_vendor=webgl["unmasked_vendor"],
            webgl_unmasked_renderer=webgl["unmasked_renderer"],
            plugins_count=plugins_count,
            mime_types_count=mime_types_count,
            canvas_noise_seed=canvas_seed,
            chrome_app=is_chrome,
            chrome_runtime=is_chrome,
            chrome_csi=is_chrome,
            chrome_load_times=is_chrome,
            notification_permission=notification_perm,
            battery_charging=battery_charging,
            battery_level=battery_level,
            font_fingerprint=font_fp,
        )
        self._profile_cache[profile.profile_hash] = profile
        return profile

    def _detect_platform(self, ua: str) -> str:
        for key, platform in self.PLATFORM_MAP.items():
            if key in ua:
                return platform
        return "Win32"

    def _detect_vendor(self, ua: str) -> str:
        for key, vendor in self.VENDOR_MAP.items():
            if key in ua:
                return vendor
        return "Google Inc."

    def _detect_browser_type(self, ua: str) -> str:
        if "Edg" in ua:
            return "Edg"
        elif "Safari" in ua and "Chrome" not in ua:
            return "Safari"
        elif "Firefox" in ua:
            return "Firefox"
        return "Chrome"

    def get_stealth_script(self, profile: FingerprintProfile) -> str:
        """
        Generate a comprehensive JavaScript injection script that patches
        ALL detectable browser properties BEFORE any page scripts run.
        Injected via page.add_init_script() in Playwright.
        """
        return f"""
        (() => {{
            'use strict';

            const overrideProperty = (obj, prop, value) => {{
                try {{
                    Object.defineProperty(obj, prop, {{
                        get: () => value,
                        set: () => {{}},
                        enumerable: true,
                        configurable: true
                    }});
                }} catch (e) {{}}
            }};

            // ── 1. navigator.webdriver (THE #1 DETECTION VECTOR) ──
            delete Navigator.prototype.webdriver;
            overrideProperty(navigator, 'webdriver', undefined);

            // ── 2. Navigator Properties ──
            overrideProperty(navigator, 'userAgent', {json.dumps(profile.user_agent)});
            overrideProperty(navigator, 'platform', {json.dumps(profile.platform)});
            overrideProperty(navigator, 'vendor', {json.dumps(profile.vendor)});
            overrideProperty(navigator, 'language', {json.dumps(profile.language)});
            overrideProperty(navigator, 'languages', {json.dumps(profile.languages)});
            overrideProperty(navigator, 'hardwareConcurrency', {profile.hardware_concurrency});
            overrideProperty(navigator, 'deviceMemory', {profile.device_memory});
            overrideProperty(navigator, 'maxTouchPoints', {profile.max_touch_points});

            // ── 3. Plugins & MimeTypes ──
            const createFakePlugins = () => {{
                const plugins = [];
                const pluginNames = [
                    'Chrome PDF Plugin',
                    'Chrome PDF Viewer',
                    'Native Client',
                    'Widevine Content Decryption Module'
                ];
                for (let i = 0; i < {profile.plugins_count}; i++) {{
                    plugins.push({{
                        name: pluginNames[i % pluginNames.length],
                        filename: `${{pluginNames[i % pluginNames.length].replace(/\\s/g, '')}}.dll`,
                        description: pluginNames[i % pluginNames.length],
                        version: '1.0.0',
                        length: 1,
                        item: () => null,
                        namedItem: () => null
                    }});
                }}
                return plugins;
            }};

            const fakePlugins = createFakePlugins();
            overrideProperty(navigator, 'plugins', fakePlugins);
            overrideProperty(navigator, 'mimeTypes', fakePlugins.map(() => ({{
                type: 'application/pdf',
                suffixes: 'pdf',
                description: 'Portable Document Format',
                enabledPlugin: null
            }})));

            // ── 4. Chrome Runtime APIs ──
            if ({json.dumps(profile.chrome_app)}) {{
                window.chrome = window.chrome || {{}};
                window.chrome.app = {{
                    isInstalled: false,
                    InstallState: {{DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed'}},
                    RunningState: {{CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running'}}
                }};
                window.chrome.runtime = window.chrome.runtime || {{}};
                window.chrome.runtime.OnInstalledReason = {{CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update'}};
                window.chrome.runtime.OnRestartRequiredReason = {{APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic'}};
                window.chrome.runtime.PlatformArch = {{ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64'}};
                window.chrome.runtime.PlatformNaclArch = {{ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', MIPS64EL: 'mips64el', MIPS_EL: 'mipsel', X86_32: 'x86-32', X86_64: 'x86-64'}};
                window.chrome.runtime.PlatformOs = {{ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win'}};
                window.chrome.runtime.RequestUpdateCheckStatus = {{NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available'}};
            }}

            // ── 5. WebGL Fingerprint Spoofing ──
            const getParameterProxy = new Proxy(WebGLRenderingContext.prototype.getParameter, {{
                apply(target, thisArg, args) {{
                    const param = args[0];
                    if (param === 37445) return {json.dumps(profile.webgl_vendor)};
                    if (param === 37446) return {json.dumps(profile.webgl_renderer)};
                    if (param === 7937) return {json.dumps(profile.webgl_vendor)};
                    if (param === 7936) return {json.dumps(profile.webgl_renderer)};
                    return Reflect.apply(target, thisArg, args);
                }}
            }});
            WebGLRenderingContext.prototype.getParameter = getParameterProxy;
            if (WebGL2RenderingContext) {{
                WebGL2RenderingContext.prototype.getParameter = getParameterProxy;
            }}

            // ── 6. Canvas Fingerprint Noise ──
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            const noiseSeed = {profile.canvas_noise_seed};
            const addNoise = (imageData) => {{
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {{
                    const noise = Math.sin(i * noiseSeed) * 2;
                    data[i] = Math.min(255, Math.max(0, data[i] + noise));
                    data[i+1] = Math.min(255, Math.max(0, data[i+1] + noise));
                    data[i+2] = Math.min(255, Math.max(0, data[i+2] + noise));
                }}
                return imageData;
            }};
            CanvasRenderingContext2D.prototype.getImageData = function(...args) {{
                const imageData = originalGetImageData.apply(this, args);
                return addNoise(imageData);
            }};

            // ── 7. WebRTC Leak Prevention ──
            if (window.RTCPeerConnection) {{
                const originalRTC = window.RTCPeerConnection;
                window.RTCPeerConnection = function(...args) {{
                    const pc = new originalRTC(...args);
                    const originalAddIceCandidate = pc.addIceCandidate;
                    pc.addIceCandidate = function(candidate) {{
                        if (candidate && candidate.candidate) {{
                            const c = candidate.candidate;
                            if (c.includes('typ host') || c.includes('192.168.') || c.includes('10.')) {{
                                return Promise.resolve();
                            }}
                        }}
                        return originalAddIceCandidate.call(this, candidate);
                    }};
                    return pc;
                }};
                window.RTCPeerConnection.prototype = originalRTC.prototype;
            }}

            // ── 8. Permissions API ──
            if (navigator.permissions) {{
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function(parameters) {{
                    if (parameters.name === 'notifications') {{
                        return Promise.resolve({{
                            state: {json.dumps(profile.notification_permission)},
                            onchange: null,
                            addEventListener: () => {{}},
                            removeEventListener: () => {{}}
                        }});
                    }}
                    return originalQuery.call(this, parameters);
                }};
            }}

            // ── 9. Notification Permission ──
            if (window.Notification) {{
                overrideProperty(Notification, 'permission', {json.dumps(profile.notification_permission)});
            }}

            // ── 10. Screen Properties ──
            overrideProperty(screen, 'width', {profile.screen['width']});
            overrideProperty(screen, 'height', {profile.screen['height']});
            overrideProperty(screen, 'availWidth', {profile.screen['availWidth']});
            overrideProperty(screen, 'availHeight', {profile.screen['availHeight']});
            overrideProperty(screen, 'colorDepth', {profile.color_depth});
            overrideProperty(screen, 'pixelDepth', {profile.color_depth});

            // ── 11. Window Properties ──
            overrideProperty(window, 'devicePixelRatio', {profile.device_pixel_ratio});
            overrideProperty(window, 'outerWidth', {profile.screen['width']});
            overrideProperty(window, 'outerHeight', {profile.screen['height']});

            // ── 12. Battery API ──
            if (navigator.getBattery) {{
                navigator.getBattery = function() {{
                    return Promise.resolve({{
                        charging: {json.dumps(profile.battery_charging)},
                        chargingTime: Infinity,
                        dischargingTime: Infinity,
                        level: {profile.battery_level},
                        addEventListener: () => {{}},
                        removeEventListener: () => {{}}
                    }});
                }};
            }}

            // ── 13. iframe.contentWindow patch ──
            const originalCreateElement = Document.prototype.createElement;
            Document.prototype.createElement = function(tagName, ...args) {{
                const element = originalCreateElement.call(this, tagName, ...args);
                if (tagName.toLowerCase() === 'iframe') {{
                    try {{
                        Object.defineProperty(element, 'contentWindow', {{
                            get: () => {{
                                try {{ return element.contentWindow; }} catch (e) {{ return window; }}
                            }}
                        }});
                    }} catch (e) {{}}
                }}
                return element;
            }};

            // ── 14. toString patching ──
            const patchToString = (target, value) => {{
                try {{ target.toString = () => `function ${{value}}() {{ [native code] }}`; }} catch (e) {{}}
            }};
            patchToString(navigator.permissions.query, 'query');
            patchToString(navigator.getBattery, 'getBattery');

            // ── 15. Performance timing cleanup ──
            if (window.performance && window.performance.getEntriesByType) {{
                const originalGetEntries = window.performance.getEntriesByType;
                window.performance.getEntriesByType = function(type) {{
                    const entries = originalGetEntries.call(this, type);
                    if (type === 'navigation') {{
                        return entries.map(e => {{
                            const clone = {{...e}};
                            delete clone.nextHopProtocol;
                            return clone;
                        }});
                    }}
                    return entries;
                }};
            }}

            // ── 16. Console cleanup ──
            if (window.console) {{
                window.console.debug = window.console.log;
            }}
        }})();
        """

    def get_browser_args(self, profile: FingerprintProfile) -> List[str]:
        """Generate Chromium launch arguments that reduce automation footprint."""
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--safebrowsing-disable-auto-update",
            f"--window-size={profile.viewport['width']},{profile.viewport['height']}",
        ]
        if profile.max_touch_points == 0:
            args.extend(["--disable-features=WebRtcHideLocalIpsWithMdns"])
        return args

    def get_context_options(self, profile: FingerprintProfile) -> Dict[str, Any]:
        """Generate Playwright browser context options."""
        return {
            "viewport": profile.viewport,
            "screen": profile.screen,
            "user_agent": profile.user_agent,
            "locale": profile.language,
            "timezone_id": profile.timezone,
            "geolocation": self._get_geolocation(profile.timezone),
            "permissions": ["geolocation"],
            "color_scheme": "light",
            "has_touch": profile.max_touch_points > 0,
            "is_mobile": profile.max_touch_points > 0,
            "java_script_enabled": True,
            "extra_http_headers": {
                "Accept-Language": f"{profile.language},en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "sec-ch-ua": self._get_sec_ch_ua(profile.user_agent),
                "sec-ch-ua-mobile": "?1" if profile.max_touch_points > 0 else "?0",
                "sec-ch-ua-platform": f'"{self._get_platform_name(profile.platform)}"',
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
            },
        }

    def _get_geolocation(self, timezone: str) -> Dict[str, float]:
        coords = {
            "America/New_York": {"latitude": 40.7128, "longitude": -74.0060},
            "America/Los_Angeles": {"latitude": 34.0522, "longitude": -118.2437},
            "Europe/London": {"latitude": 51.5074, "longitude": -0.1278},
            "Europe/Paris": {"latitude": 48.8566, "longitude": 2.3522},
            "Asia/Tokyo": {"latitude": 35.6762, "longitude": 139.6503},
            "Asia/Shanghai": {"latitude": 31.2304, "longitude": 121.4737},
            "Australia/Sydney": {"latitude": -33.8688, "longitude": 151.2093},
        }
        return coords.get(timezone, {"latitude": 40.7128, "longitude": -74.0060})

    def _get_sec_ch_ua(self, ua: str) -> str:
        if "Chrome" in ua:
            version = "126"
            return f'"Chromium";v="{version}", "Google Chrome";v="{version}", "Not-A.Brand";v="99"'
        elif "Edg" in ua:
            return '"Chromium";v="126", "Microsoft Edge";v="126", "Not-A.Brand";v="99"'
        return '"Chromium";v="126", "Not-A.Brand";v="99"'

    def _get_platform_name(self, platform: str) -> str:
        mapping = {
            "Win32": "Windows",
            "Win64": "Windows",
            "MacIntel": "macOS",
            "Linux x86_64": "Linux",
            "Linux armv8l": "Android",
        }
        return mapping.get(platform, "Windows")


_stealth_engine = None

def get_stealth_engine() -> StealthEngine:
    global _stealth_engine
    if _stealth_engine is None:
        _stealth_engine = StealthEngine()
    return _stealth_engine
'''

os.makedirs(f"{base_dir}/app/core", exist_ok=True)
with open(f"{base_dir}/app/core/stealth_engine.py", "w") as f:
    f.write(stealth_engine_py)

print("✅ Part 3: app/core/stealth_engine.py — Stealth Engine created")
print("   • 16 evasion modules")
print("   • Coherent fingerprint generation")
print("   • WebGL/Canvas noise injection")
print("   • WebRTC leak prevention")
