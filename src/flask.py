"""Phiolen (flasks): carry a liquid, pour it out, suck it up, drink it or throw it.

Like Noita's potions, a flask holds up to ``CAPACITY`` cells of one liquid. Only
liquids fit; pouring places real cells into the world, so everything the liquid
does there (dousing fire, eating flesh, ...) happens through the simulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.body import Body
from src.materials import (
    ACID,
    AIR,
    BEDROCK,
    BLOOD,
    KIND,
    LIQUID,
    MAGMA,
    MUCUS,
    NAME_DE,
    PUS,
    STOPS_PROJECTILE,
    TALLOW,
)
from src.world import World, disc_offsets

CAPACITY = 300  # cells
POUR_RATE = 150.0  # cells per second
ABSORB_RATE = 300.0  # cells per second
ABSORB_RADIUS = 7
REACH = 60.0  # how far from the player a flask can pour or suck (px)
SIP = 30  # cells used up by one drink
THROW_SPEED = 260.0
THROW_GRAVITY = 420.0
SHATTER_RADIUS_PER_CELL = 0.06  # splash radius grows with the content

# What a sip does: (heal, damage) per sip and a German description.
DRINK_EFFECTS: dict[int, tuple[float, float, str]] = {
    BLOOD: (8.0, 0.0, "Blut stillt deine Wunden ein wenig."),
    ACID: (0.0, 25.0, "Die Säure verätzt dich von innen!"),
    TALLOW: (0.0, 0.0, "Fettig. Du fühlst dich schwer."),
    MUCUS: (2.0, 0.0, "Zäh und kalt. Das Brennen lässt nach."),
    PUS: (0.0, 0.0, "Eiter. Dir wird übel, das Gift brennt in den Adern."),
    MAGMA: (0.0, 40.0, "Glutblut! Es verbrennt dich von innen."),
}


@dataclass
class Flask:
    material: int | None = None
    amount: int = 0

    @property
    def empty(self) -> bool:
        return self.amount <= 0 or self.material is None

    @property
    def label_de(self) -> str:
        if self.empty:
            return "Leere Phiole"
        return f"Phiole: {NAME_DE[self.material]} ({round(100 * self.amount / CAPACITY)} %)"

    def _drain(self, cells: int) -> None:
        self.amount = max(0, self.amount - cells)
        if self.amount == 0:
            self.material = None

    def pour(self, world: World, x: float, y: float, angle: float, budget: float) -> int:
        """Spill up to ``budget`` cells in a short arc towards ``angle``. Returns cells placed."""
        if self.empty:
            return 0
        placed = 0
        count = min(self.amount, int(budget))
        for k in range(count):
            for attempt in range(4):  # look a little further if the spot is taken
                spread = ((k + attempt) % 5 - 2) * 0.08
                distance = 3 + (k % 3) + attempt * 2
                px = int(x + math.cos(angle + spread) * distance)
                py = int(y + math.sin(angle + spread) * distance)
                if world.get(px, py) == AIR:
                    world.set_cell(px, py, self.material)
                    placed += 1
                    break
        self._drain(placed)
        return placed

    def absorb(self, world: World, cx: int, cy: int, budget: float) -> int:
        """Suck liquid cells around (cx, cy) into the flask. Returns cells taken."""
        if self.amount >= CAPACITY:
            return 0
        taken = 0
        limit = min(int(budget), CAPACITY - self.amount)
        for dx, dy in disc_offsets(ABSORB_RADIUS):
            if taken >= limit:
                break
            x, y = cx + dx, cy + dy
            cell = world.get(x, y)
            if KIND[cell] != LIQUID or cell == BEDROCK:
                continue
            if self.material is None:
                self.material = cell
            if cell != self.material:
                continue  # one liquid per flask
            world.set_cell(x, y, AIR)
            taken += 1
        self.amount += taken
        return taken

    def drink(self, body: Body) -> str:
        """Take a sip. Returns a German message (empty if nothing happened)."""
        if self.empty:
            return ""
        heal, damage, message = DRINK_EFFECTS.get(self.material, (0.0, 0.0, "Es schmeckt nach nichts."))
        share = min(1.0, self.amount / SIP)
        body.hp = min(body.max_hp, body.hp + heal * share)
        if damage:
            body.hurt(damage * share)
        if self.material == MAGMA:
            body.burning = 3.0
        else:
            body.wet = max(body.wet, 3.0)
            body.burning = 0.0
        if self.material == PUS:
            body.poisoned = 8.0
        elif self.material == BLOOD:
            body.poisoned = 0.0  # fresh blood flushes the poison out
        self._drain(SIP)
        return message


@dataclass
class ThrownFlask:
    """A flask in flight; it shatters on the first wall or creature it hits."""

    flask: Flask
    x: float
    y: float
    vx: float
    vy: float
    alive: bool = True

    @classmethod
    def throw(cls, flask: Flask, x: float, y: float, angle: float) -> ThrownFlask:
        return cls(flask, x, y, math.cos(angle) * THROW_SPEED, math.sin(angle) * THROW_SPEED - 40)

    def update(self, world: World, dt: float, bodies: list[Body]) -> bool:
        """Fly; returns True when the flask shattered this update."""
        self.vy += THROW_GRAVITY * dt
        steps = max(1, int(math.hypot(self.vx, self.vy) * dt))
        for _ in range(steps):
            nx, ny = self.x + self.vx * dt / steps, self.y + self.vy * dt / steps
            hit_body = any(not b.dead and b.contains(nx, ny) for b in bodies)
            if hit_body or STOPS_PROJECTILE[world.get(int(nx), int(ny))]:
                self.shatter(world)
                return True
            self.x, self.y = nx, ny
        return False

    def shatter(self, world: World) -> None:
        self.alive = False
        flask = self.flask
        if not flask.empty:
            radius = max(2, round(math.sqrt(flask.amount) * SHATTER_RADIUS_PER_CELL * 10))
            world.splash(int(self.x), int(self.y), radius, flask.material)
        flask.material, flask.amount = None, 0
