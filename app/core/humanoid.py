
# ============================================================
# PART 4: HUMANOID MODULE (Behavioral Emulation)
# ============================================================
# 📁 app/core/humanoid.py

humanoid_py = r'''"""
BOT-BOOK-POPY Humanoid Module
==============================
Advanced behavioral emulation that makes automation indistinguishable
from real human interaction.

Techniques Implemented:
1. Bezier curve mouse movements with variable speed
2. Natural scrolling with irregular speeds and micro-pauses
3. Human-like typing with variable speed, typos, and corrections
4. Random micro-interactions (hovers, small movements)
5. Context-aware delays with biological rhythm patterns
6. Attention simulation (reading pauses, re-reading)
7. Hand tremor simulation
8. Overshoot and correction behavior
9. Session warm-up simulation
10. Decision-making delays

Why this defeats behavioral detection:
- Facebook tracks mouse velocity profiles, acceleration curves, path shapes
- Real humans have: non-linear paths, variable speed, overshoots, hesitation
- Bots have: linear paths, constant speed, perfect accuracy, no micro-pauses
- This module replicates the biomechanics of human hand movement
"""

import random
import math
import asyncio
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import numpy as np

from app.config import (
    MIN_DELAY_MS, MAX_DELAY_MS,
    TYPING_SPEED_MIN, TYPING_SPEED_MAX, TYPING_ERROR_RATE,
    MOUSE_OVERSHOOT_CHANCE
)


@dataclass
class Point:
    x: float
    y: float


class HumanoidEngine:
    """
    Behavioral emulation engine that makes every action look human.

    Key Insight: Human movement is NOT random. It follows biomechanical patterns:
    - Fitts's Law: Movement time depends on distance and target size
    - Bell-shaped velocity profile: Slow start, fast middle, slow end
    - Overshoot: Humans often overshoot small targets and correct
    - Micro-corrections: Tiny adjustments near the target
    - Hand tremor: Small, high-frequency noise superimposed on movement
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        # Personal "hand characteristics" - consistent per session
        self.hand_tremor_amplitude = self.rng.uniform(0.3, 1.2)
        self.overshoot_tendency = self.rng.uniform(0.05, 0.25)
        self.hesitation_frequency = self.rng.uniform(0.1, 0.3)
        self.base_typing_wpm = self.rng.uniform(35, 75)

        self._movement_history: List[Dict[str, Any]] = []

    # ============================================================
    # DELAY SYSTEM
    # ============================================================

    async def random_delay(self, min_ms: Optional[int] = None,
                           max_ms: Optional[int] = None,
                           context: str = "general") -> None:
        """
        Generate a context-aware random delay.

        Different contexts have different delay distributions:
        - "page_load": Longer delays (simulating reading/scanning)
        - "typing": Short delays between keystrokes
        - "click": Medium delays (decision time)
        - "scroll": Very short delays
        - "form_submit": Longer delays (reviewing before submit)

        The delay follows a log-normal distribution (more realistic than uniform)
        because human reaction times are naturally skewed right.
        """
        min_val = min_ms or MIN_DELAY_MS
        max_val = max_ms or MAX_DELAY_MS

        context_multipliers = {
            "page_load": (1.5, 3.0),
            "typing": (0.1, 0.3),
            "click": (0.8, 1.5),
            "scroll": (0.2, 0.5),
            "form_submit": (2.0, 4.0),
            "hover": (0.3, 0.8),
            "general": (1.0, 1.0),
        }

        mult_low, mult_high = context_multipliers.get(context, (1.0, 1.0))

        mean = math.log((min_val + max_val) / 2)
        sigma = 0.5

        delay_ms = self.np_rng.lognormal(mean, sigma)
        delay_ms = max(min_val * mult_low, min(delay_ms, max_val * mult_high))

        # Add "biological rhythm" - humans have ~100ms micro-pauses
        if self.rng.random() < 0.3:
            delay_ms += self.rng.uniform(80, 150)

        await asyncio.sleep(delay_ms / 1000.0)

    async def thinking_delay(self, complexity: str = "medium") -> None:
        """
        Simulate thinking/reading time.
        Used before decisions like clicking "Post" or "Comment".
        """
        complexity_delays = {
            "low": (500, 1500),
            "medium": (1500, 4000),
            "high": (4000, 12000),
            "very_high": (8000, 25000),
        }

        min_ms, max_ms = complexity_delays.get(complexity, (1000, 3000))
        await self.random_delay(min_ms, max_ms, context="general")

    # ============================================================
    # MOUSE MOVEMENT (Bezier Curves)
    # ============================================================

    def _cubic_bezier(self, p0: Point, p1: Point, p2: Point, p3: Point,
                      steps: int) -> List[Point]:
        """
        Generate points along a cubic Bezier curve.

        Cubic Bezier formula:
        B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t) t^2 P2 + t^3 P3

        Control points P1, P2 create the curve shape.
        Randomized control points = unique path every time.
        """
        points = []
        for i in range(steps + 1):
            t = i / steps
            t_inv = 1 - t

            x = (t_inv ** 3) * p0.x + \
                3 * (t_inv ** 2) * t * p1.x + \
                3 * t_inv * (t ** 2) * p2.x + \
                (t ** 3) * p3.x

            y = (t_inv ** 3) * p0.y + \
                3 * (t_inv ** 2) * t * p1.y + \
                3 * t_inv * (t ** 2) * p2.y + \
                (t ** 3) * p3.y

            points.append(Point(x, y))

        return points

    def _generate_control_points(self, start: Point, end: Point,
                                  deviation: float = 0.3) -> Tuple[Point, Point]:
        """
        Generate randomized control points for Bezier curve.

        The control points are positioned perpendicular to the straight line
        between start and end, creating natural curved paths.
        """
        dx = end.x - start.x
        dy = end.y - start.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        perp_x = -dy / dist if dist > 0 else 0
        perp_y = dx / dist if dist > 0 else 0

        dev1 = self.rng.uniform(-deviation, deviation) * dist
        dev2 = self.rng.uniform(-deviation, deviation) * dist

        p1 = Point(
            start.x + dx * 0.25 + perp_x * dev1,
            start.y + dy * 0.25 + perp_y * dev1
        )
        p2 = Point(
            start.x + dx * 0.75 + perp_x * dev2,
            start.y + dy * 0.75 + perp_y * dev2
        )

        return p1, p2

    def _apply_hand_tremor(self, points: List[Point]) -> List[Point]:
        """
        Add hand tremor (small high-frequency noise) to movement path.

        Real human hands have involuntary tremor at ~8-12 Hz.
        This adds micro-jitter that makes paths look organic.
        """
        tremored = []
        for i, p in enumerate(points):
            progress = i / len(points)
            amplitude = self.hand_tremor_amplitude * (1 - progress * 0.7)

            noise_x = self.np_rng.normal(0, amplitude * 0.5)
            noise_y = self.np_rng.normal(0, amplitude * 0.5)

            tremored.append(Point(p.x + noise_x, p.y + noise_y))

        return tremored

    def _apply_overshoot(self, points: List[Point], target: Point) -> List[Point]:
        """
        Add overshoot behavior - humans often go past the target and correct.

        This is especially common with small targets or fast movements.
        The overshoot is followed by a smooth correction back to target.
        """
        if self.rng.random() > MOUSE_OVERSHOOT_CHANCE:
            return points

        last_point = points[-1]
        overshoot_x = target.x + self.rng.uniform(-15, 15)
        overshoot_y = target.y + self.rng.uniform(-15, 15)

        overshoot_point = Point(overshoot_x, overshoot_y)

        correction_points = self._cubic_bezier(
            overshoot_point,
            Point(overshoot_x + (target.x - overshoot_x) * 0.3,
                  overshoot_y + (target.y - overshoot_y) * 0.3),
            Point(target.x + (overshoot_x - target.x) * 0.1,
                  target.y + (overshoot_y - target.y) * 0.1),
            target,
            steps=8
        )

        return points + correction_points

    def _calculate_movement_speed(self, distance: float,
                                   speed_profile: str = "medium") -> int:
        """
        Calculate number of steps based on distance and speed profile.

        More steps = slower, more detailed movement.
        Fewer steps = faster, more direct movement.
        """
        speed_map = {
            "slowest": (40, 80),
            "slow": (25, 45),
            "medium": (15, 30),
            "fast": (8, 18),
            "fastest": (5, 10),
        }

        min_steps, max_steps = speed_map.get(speed_profile, (15, 30))
        base_steps = int(distance / 15)
        steps = self.rng.randint(min_steps, max_steps) + base_steps

        return min(steps, 150)

    async def natural_mouse_move(self, page, target_x: float, target_y: float,
                                  speed_profile: str = "medium",
                                  overshoot: bool = True) -> None:
        """
        Move mouse to target coordinates with human-like Bezier curve path.

        This is the core of behavioral evasion. Facebook tracks:
        - Path curvature (linear = bot)
        - Velocity profile (constant = bot)
        - Micro-pauses (none = bot)
        - Overshoot behavior (perfect accuracy = bot)

        This function defeats all of these checks.
        """
        current_pos = await page.evaluate(
            "() => ({ x: window.lastMouseX || 0, y: window.lastMouseY || 0 })"
        )
        start = Point(current_pos.get("x", 0), current_pos.get("y", 0))
        target = Point(target_x, target_y)

        dx = target.x - start.x
        dy = target.y - start.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 5:
            await page.mouse.move(target_x, target_y)
            return

        cp1, cp2 = self._generate_control_points(start, target)
        steps = self._calculate_movement_speed(distance, speed_profile)
        path = self._cubic_bezier(start, cp1, cp2, target, steps)
        path = self._apply_hand_tremor(path)

        if overshoot:
            path = self._apply_overshoot(path, target)

        for i, point in enumerate(path):
            await page.mouse.move(point.x, point.y)

            progress = i / len(path)
            speed_factor = 1 - 4 * (progress - 0.5) ** 2
            base_delay = 0.003 + (1 - speed_factor) * 0.008

            if self.rng.random() < self.hesitation_frequency:
                base_delay += self.rng.uniform(0.05, 0.2)

            await asyncio.sleep(base_delay)

        self._movement_history.append({
            "start": (start.x, start.y),
            "target": (target.x, target.y),
            "distance": distance,
            "steps": steps,
            "duration": steps * 0.005,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def natural_mouse_move_to_element(self, page, selector: str,
                                             speed_profile: str = "medium") -> None:
        """Move mouse to the center of an element with human-like path."""
        box = await page.evaluate(
            f"""() => {{
                const el = document.querySelector('{selector}');
                if (!el) return null;
                const rect = el.getBoundingClientRect();
                return {{
                    x: rect.left + rect.width / 2 + Math.random() * rect.width * 0.4 - rect.width * 0.2,
                    y: rect.top + rect.height / 2 + Math.random() * rect.height * 0.4 - rect.height * 0.2,
                }};
            }}"""
        )

        if box:
            await self.natural_mouse_move(page, box["x"], box["y"], speed_profile)

    async def micro_hover(self, page, x: float, y: float,
                          duration: float = 0.3) -> None:
        """
        Perform a micro-hover - small random movement near a point.
        Simulates the hand settling or adjusting position.
        """
        offset_x = self.rng.uniform(-20, 20)
        offset_y = self.rng.uniform(-20, 20)

        await page.mouse.move(x + offset_x, y + offset_y)
        await asyncio.sleep(duration)
        await page.mouse.move(x, y)

    # ============================================================
    # SCROLLING
    # ============================================================

    async def human_scroll(self, page, direction: str = "down",
                           amount: Optional[int] = None,
                           speed: str = "natural") -> None:
        """
        Scroll the page in a human-like manner.

        Human scrolling characteristics:
        - Irregular scroll amounts (not always same distance)
        - Variable speed (sometimes fast, sometimes slow)
        - Micro-pauses (reading, looking at content)
        - Occasional small up-scrolls while scrolling down (re-reading)
        - Momentum-based (flick and let it coast)
        """
        if amount is None:
            amount = self.rng.randint(200, 800)

        if direction == "up":
            amount = -amount

        scroll_speeds = {
            "slow": (50, 150),
            "natural": (150, 400),
            "fast": (400, 800),
        }

        step_size = scroll_speeds.get(speed, (150, 400))

        total_scrolled = 0
        while abs(total_scrolled) < abs(amount):
            step = self.rng.randint(*step_size)
            if direction == "up":
                step = -step

            remaining = amount - total_scrolled
            if abs(step) > abs(remaining):
                step = remaining

            await page.evaluate(f"window.scrollBy(0, {{step}})")
            total_scrolled += step

            delay = self.rng.uniform(0.05, 0.3)

            # Occasional reading pause (10% chance)
            if self.rng.random() < 0.1:
                delay += self.rng.uniform(0.5, 2.0)

            # Occasional micro-scroll back (5% chance)
            if self.rng.random() < 0.05 and abs(total_scrolled) > 100:
                back_step = self.rng.randint(30, 80)
                if direction == "up":
                    back_step = -back_step
                await page.evaluate(f"window.scrollBy(0, {{back_step}})")
                total_scrolled += back_step
                delay += self.rng.uniform(0.3, 1.0)

            await asyncio.sleep(delay)

    # ============================================================
    # TYPING
    # ============================================================

    async def human_typing(self, page, text: str, selector: Optional[str] = None,
                           element=None, typo_rate: float = TYPING_ERROR_RATE) -> str:
        """
        Type text with human-like characteristics.

        Human typing characteristics:
        - Variable speed (bursts of fast typing, then pauses)
        - Occasional typos and corrections
        - Pauses at punctuation
        - Slower at start of sentences
        - Faster in the middle of words

        Returns the final text that was typed.
        """
        if selector:
            await page.click(selector)
        elif element:
            await element.click()

        typed_text = []

        for i, char in enumerate(text):
            if char in ".,!?;:":
                base_delay = self.rng.uniform(0.15, 0.4)
            elif char == " ":
                base_delay = self.rng.uniform(0.08, 0.2)
            elif char.isupper():
                base_delay = self.rng.uniform(0.1, 0.25)
            else:
                base_delay = self.rng.uniform(TYPING_SPEED_MIN, TYPING_SPEED_MAX)

            if self.rng.random() < 0.03:
                base_delay += self.rng.uniform(0.3, 1.5)

            # Simulate typo
            if self.rng.random() < typo_rate and char.isalpha():
                wrong_char = self._get_typo_char(char)
                await page.keyboard.type(wrong_char)
                typed_text.append(wrong_char)

                await asyncio.sleep(self.rng.uniform(0.2, 0.6))
                await page.keyboard.press("Backspace")
                typed_text.pop()

                await asyncio.sleep(self.rng.uniform(0.1, 0.3))

            await page.keyboard.type(char)
            typed_text.append(char)

            await asyncio.sleep(base_delay)

        return "".join(typed_text)

    def _get_typo_char(self, char: str) -> str:
        """Generate a realistic typo for a character."""
        adjacent = {
            'a': 's', 's': 'a', 'd': 's', 'f': 'd', 'g': 'f', 'h': 'g',
            'j': 'h', 'k': 'j', 'l': 'k', 'q': 'w', 'w': 'q', 'e': 'w',
            'r': 'e', 't': 'r', 'y': 't', 'u': 'y', 'i': 'u', 'o': 'i',
            'p': 'o', 'z': 'x', 'x': 'z', 'c': 'x', 'v': 'c', 'b': 'v',
            'n': 'b', 'm': 'n',
        }

        lower_char = char.lower()
        if lower_char in adjacent and self.rng.random() < 0.7:
            typo = adjacent[lower_char]
            return typo.upper() if char.isupper() else typo

        return self.rng.choice("abcdefghijklmnopqrstuvwxyz")

    # ============================================================
    # CLICKING
    # ============================================================

    async def human_click(self, page, selector: Optional[str] = None,
                          x: Optional[float] = None, y: Optional[float] = None,
                          pre_delay: bool = True) -> None:
        """
        Perform a human-like click with natural pre-click behavior.

        Steps:
        1. Move mouse to target with natural path
        2. Micro-hover (settling)
        3. Small random delay (decision time)
        4. Click
        5. Brief pause after click
        """
        if pre_delay:
            await self.thinking_delay("low")

        if selector:
            box = await page.evaluate(
                f"""() => {{
                    const el = document.querySelector('{selector}');
                    if (!el) return null;
                    const rect = el.getBoundingClientRect();
                    return {{
                        x: rect.left + rect.width / 2 + (Math.random() - 0.5) * rect.width * 0.3,
                        y: rect.top + rect.height / 2 + (Math.random() - 0.5) * rect.height * 0.3,
                    }};
                }}"""
            )
            if box:
                await self.natural_mouse_move(page, box["x"], box["y"])
                x, y = box["x"], box["y"]

        if x is not None and y is not None:
            await self.micro_hover(page, x, y, duration=self.rng.uniform(0.1, 0.4))

        await asyncio.sleep(self.rng.uniform(0.05, 0.25))

        if selector:
            await page.click(selector)
        elif x is not None and y is not None:
            await page.mouse.click(x, y)

        await asyncio.sleep(self.rng.uniform(0.1, 0.3))

    # ============================================================
    # ATTENTION SIMULATION
    # ============================================================

    async def simulate_reading(self, page, min_time: float = 2.0,
                                max_time: float = 8.0) -> None:
        """
        Simulate reading a page or post.

        During "reading":
        - Occasional small mouse movements
        - Rare scrolls
        - No keyboard input
        - Variable attention (sometimes distracted)
        """
        duration = self.rng.uniform(min_time, max_time)
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < duration:
            action = self.rng.random()

            if action < 0.7:
                await asyncio.sleep(self.rng.uniform(0.5, 2.0))

            elif action < 0.85:
                viewport = await page.viewport_size
                if viewport:
                    rand_x = self.rng.uniform(100, viewport["width"] - 100)
                    rand_y = self.rng.uniform(100, viewport["height"] - 100)
                    await self.natural_mouse_move(page, rand_x, rand_y, speed_profile="slow")
                    await asyncio.sleep(self.rng.uniform(0.3, 1.0))

            elif action < 0.95:
                await self.human_scroll(page, direction="down", amount=self.rng.randint(100, 300))
                await asyncio.sleep(self.rng.uniform(0.5, 1.5))

            else:
                await asyncio.sleep(self.rng.uniform(1.0, 3.0))

    # ============================================================
    # SESSION WARM-UP
    # ============================================================

    async def session_warmup(self, page) -> None:
        """
        Perform initial session warm-up actions.

        When a real user opens Facebook:
        1. They don't immediately start clicking
        2. They look around, scroll a bit
        3. They might hover over some elements
        4. They take time to orient themselves
        """
        await asyncio.sleep(self.rng.uniform(1.0, 3.0))

        viewport = await page.viewport_size
        if viewport:
            for _ in range(self.rng.randint(2, 5)):
                x = self.rng.uniform(50, viewport["width"] - 50)
                y = self.rng.uniform(50, viewport["height"] - 50)
                await self.natural_mouse_move(page, x, y, speed_profile="slow")
                await asyncio.sleep(self.rng.uniform(0.5, 1.5))

        await self.human_scroll(page, direction="down", amount=self.rng.randint(300, 600))
        await asyncio.sleep(self.rng.uniform(0.5, 1.5))

        if self.rng.random() < 0.4:
            await self.human_scroll(page, direction="up", amount=self.rng.randint(100, 300))


_humanoid_engines: Dict[str, HumanoidEngine] = {}


def get_humanoid_engine(session_id: str = "default") -> HumanoidEngine:
    if session_id not in _humanoid_engines:
        _humanoid_engines[session_id] = HumanoidEngine(seed=hash(session_id) % (2**32))
    return _humanoid_engines[session_id]
'''

with open(f"{base_dir}/app/core/humanoid.py", "w") as f:
    f.write(humanoid_py)

print("✅ Part 4: app/core/humanoid.py — Humanoid Module created")
print("   • Bezier curve mouse movements with hand tremor")
print("   • Natural scrolling with reading pauses")
print("   • Human typing with typos & corrections")
print("   • Session warm-up simulation")
print("   • Attention/reading simulation")
