"""Contract V20: the shooting range minigame (Card E09)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from . import NEXT_BOOST_KEYS, Minigame, MinigameResult

LANE_YS: tuple[float, ...] = (36.0, 64.0, 92.0)


@dataclass
class ShootingTarget:
    x: float
    y: float
    kind: str
    visible_time: float
    spawn_time: float = 0.0
    lane: int = 0
    hit: bool = False

    def is_visible(self, elapsed: float) -> bool:
        return not self.hit and self.spawn_time <= elapsed <= self.spawn_time + self.visible_time

    def pop_progress(self, elapsed: float) -> float:
        if elapsed < self.spawn_time:
            return 0.0
        return min(1.0, (elapsed - self.spawn_time) / 0.15)


class SchiessstandMinigame(Minigame):
    key: str = "schiessstand"
    title_de: str = "Schießstand"
    stake: int = 20
    time_limit: float = 30.0

    def __init__(self, seed: int = 0) -> None:
        super().__init__(seed=seed)
        self.targets: list[ShootingTarget] = []
        self.score: int = 0
        self.hits_agent: int = 0
        self.hits_klonita: int = 0
        self.shots: int = 0
        self.popups: list[dict[str, Any]] = []
        self._elapsed: float = 0.0

        rng = random.Random(seed)
        kinds = ["agent"] * 24 + ["klonita"] * 6
        rng.shuffle(kinds)

        # Spread 30 targets over 30 s across 3 lanes so 2-4 pop up at any moment.
        lane_slots = [(26.0, 50.0, 78.0, 106.0, 134.0)]
        slot_xs = lane_slots[0]
        for idx, kind in enumerate(kinds):
            lane = (idx + rng.randint(0, 2)) % len(LANE_YS)
            slot = (idx // len(LANE_YS) + lane) % len(slot_xs)
            x = slot_xs[slot] + rng.uniform(-6.0, 6.0)
            y = LANE_YS[lane] + rng.uniform(-2.0, 2.0)
            spawn_time = 0.35 + idx * 0.88 + rng.uniform(-0.15, 0.15)
            vis = max(1.6, 2.4 - idx * 0.025)
            self.targets.append(
                ShootingTarget(
                    x=x,
                    y=y,
                    kind=kind,
                    visible_time=vis,
                    spawn_time=max(0.0, spawn_time),
                    lane=lane,
                )
            )

    def _add_popup(self, text: str, x: float, y: float, color: tuple[int, int, int]) -> None:
        self.popups.append({"text": text, "x": x, "y": y, "color": color, "ttl": 0.65})

    def on_action(self, action: str, cursor: tuple[int, int]) -> None:
        if action != "shoot":
            return
        self.shots += 1
        cx, cy = cursor
        hit_radius = 10.0
        for t in self.targets:
            if t.is_visible(self._elapsed) and math.hypot(t.x - cx, t.y - cy) <= hit_radius:
                t.hit = True
                if t.kind == "agent":
                    self.score += 1
                    self.hits_agent += 1
                    self._add_popup("+1", t.x, t.y - 6.0, (120, 240, 140))
                else:
                    self.score -= 3
                    self.hits_klonita += 1
                    self._add_popup("-3!", t.x, t.y - 6.0, (245, 95, 95))
                return
        self._add_popup("•", float(cx), float(cy), (170, 160, 160))

    def _finish_round(self) -> MinigameResult:
        rng = random.Random(self.seed)
        won = self.score >= 8
        reward_gold = self.stake * 2 if self.score >= 14 else 0
        boost = rng.choice(NEXT_BOOST_KEYS) if won else ""
        msg = f"Ergebnis: {self.score} Punkte!" if won else f"Verloren ({self.score} Punkte)."
        self.finished = True
        self.result = MinigameResult(
            completed=True,
            won=won,
            reward_gold=reward_gold,
            next_boost=boost,
            message_de=msg,
        )
        return self.result

    def step(
        self,
        dt: float,
        action: str | None = None,
        cursor: tuple[int, int] = (80, 60),
    ) -> MinigameResult | None:
        if self.result is not None:
            return self.result

        if action:
            self.on_action(action, cursor)

        if dt > 0.0:
            self._elapsed += dt
            self.elapsed = self._elapsed
            for p in self.popups:
                p["ttl"] -= dt
                p["y"] -= 12.0 * dt
            self.popups = [p for p in self.popups if p["ttl"] > 0.0]

        all_done = all(
            t.hit or self._elapsed > t.spawn_time + t.visible_time for t in self.targets
        )
        if self._elapsed >= self.time_limit or all_done:
            return self._finish_round()

        return None
