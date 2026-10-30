"""Wand and spark bolt projectiles."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.materials import STOPS_PROJECTILE
from src.world import World

BOLT_SPEED = 520.0  # px/s
BOLT_LIFETIME = 1.5  # seconds
BOLT_RADIUS = 9  # explosion radius in cells
WAND_COOLDOWN = 0.2  # seconds between shots


@dataclass
class Bolt:
    """A spark bolt that explodes on the first solid, powder or liquid it touches."""

    x: float
    y: float
    vx: float
    vy: float
    ttl: float = BOLT_LIFETIME
    alive: bool = True

    def update(self, world: World, dt: float) -> bool:
        """Move the bolt. Returns True if it exploded this update."""
        dx, dy = self.vx * dt, self.vy * dt
        steps = max(1, int(math.hypot(dx, dy)) + 1)
        for _ in range(steps):
            self.x += dx / steps
            self.y += dy / steps
            ix, iy = int(self.x), int(self.y)
            if STOPS_PROJECTILE[world.get(ix, iy)]:
                world.explode(ix, iy, BOLT_RADIUS)
                self.alive = False
                return True
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False
        return False


class Wand:
    """Fires bolts towards a target with a cooldown."""

    def __init__(self) -> None:
        self.cooldown = 0.0

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)

    def try_fire(self, origin: tuple[float, float], target: tuple[float, float]) -> Bolt | None:
        """Create a bolt if the wand is ready and the target is not on top of the origin."""
        if self.cooldown > 0:
            return None
        dx, dy = target[0] - origin[0], target[1] - origin[1]
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return None
        self.cooldown = WAND_COOLDOWN
        return Bolt(origin[0], origin[1], dx / length * BOLT_SPEED, dy / length * BOLT_SPEED)
