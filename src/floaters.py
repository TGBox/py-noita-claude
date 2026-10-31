"""Floating damage numbers above wounded bodies (pure logic, drawn by the HUD)."""

from __future__ import annotations

from dataclasses import dataclass

from src.body import PLAYER_TEAM, Body

LIFETIME = 0.9  # seconds a number stays visible
RISE = 22.0  # px per second
MIN_INTERVAL = 0.25  # seconds between numbers for the same body (burning ticks add up)
MAX_FLOATERS = 60


@dataclass
class Floater:
    x: float
    y: float
    text: str
    player: bool  # damage to the player is shown in a different colour
    age: float = 0.0

    @property
    def alpha(self) -> float:
        return max(0.0, 1.0 - self.age / LIFETIME)


class FloatingNumbers:
    def __init__(self) -> None:
        self.items: list[Floater] = []
        self._cooldown: dict[int, float] = {}

    def update(self, bodies: list[Body], dt: float) -> None:
        for item in self.items:
            item.age += dt
            item.y -= RISE * dt
        self.items = [item for item in self.items if item.age < LIFETIME]
        alive_ids = set()
        for body in bodies:
            key = id(body)
            alive_ids.add(key)
            wait = self._cooldown.get(key, 0.0) - dt
            self._cooldown[key] = wait
            if wait > 0 or body.damage_taken < 1.0:
                continue
            amount = round(body.damage_taken)
            body.damage_taken = 0.0
            self._cooldown[key] = MIN_INTERVAL
            if len(self.items) < MAX_FLOATERS:
                cx = body.x + body.width / 2
                self.items.append(Floater(cx, body.y - 4, str(amount), body.team == PLAYER_TEAM))
        self._cooldown = {k: v for k, v in self._cooldown.items() if k in alive_ids}

    def clear(self) -> None:
        self.items.clear()
        self._cooldown.clear()
