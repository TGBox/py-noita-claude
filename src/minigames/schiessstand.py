"""Contract V20: the shooting range minigame (Card E09)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from . import NEXT_BOOST_KEYS, Minigame, MinigameResult


@dataclass
class ShootingTarget:
    x: float
    y: float
    kind: str
    visible_time: float
    hit: bool = False


class SchiessstandMinigame(Minigame):
    key: str = "schiessstand"
    title_de: str = "Schießstand"
    stake: int = 20
    time_limit: float = 30.0

    def __init__(self, seed: int = 0) -> None:
        super().__init__(seed=seed)
        self.targets: list[ShootingTarget] = []
        self.score: int = 0
        self._elapsed: float = 0.0

        rng = random.Random(seed)
        kinds = ["agent"] * 24 + ["klonita"] * 6
        rng.shuffle(kinds)

        for kind in kinds:
            x = rng.uniform(20.0, 140.0)
            y = rng.uniform(30.0, 90.0)
            vis = 1.5
            self.targets.append(ShootingTarget(x=x, y=y, kind=kind, visible_time=vis))

    def on_action(self, action: str, cursor: tuple[int, int]) -> None:
        if action == "shoot":
            cx, cy = cursor
            hit_radius = 8.0
            for t in self.targets:
                if not t.hit:
                    dist = math.hypot(t.x - cx, t.y - cy)
                    if dist <= hit_radius:
                        t.hit = True
                        if t.kind == "agent":
                            self.score += 1
                        elif t.kind == "klonita":
                            self.score -= 3
                        break

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

        self._elapsed += dt
        if self._elapsed >= self.time_limit:
            rng = random.Random(self.seed)
            won = self.score >= 8
            reward_gold = self.stake * 2 if self.score >= 14 else 0
            boost = rng.choice(NEXT_BOOST_KEYS) if won else ""
            msg = f"Ergebnis: {self.score} Punkte!" if won else f"Verloren ({self.score} Punkte)."
            self.result = MinigameResult(
                completed=True,
                won=won,
                reward_gold=reward_gold,
                next_boost=boost,
                message_de=msg,
            )
            return self.result

        return None
