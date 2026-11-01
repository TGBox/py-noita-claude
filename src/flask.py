"""Phiolen (flasks): carry a liquid, pour it out, suck it up, drink it or throw it.

Like Noita's potions, a flask holds up to ``CAPACITY`` cells of one liquid. Only
liquids fit; pouring places real cells into the world, so everything the liquid
does there (dousing fire, eating flesh, ...) happens through the simulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src import materials as mat
from src.body import Body
from src.materials import AIR, BEDROCK, KIND, LIQUID, NAME_DE, STOPS_PROJECTILE
from src.world import World, disc_offsets

CAPACITY = 300  # cells
POUR_RATE = 150.0  # cells per second
ABSORB_RATE = 300.0  # cells per second
ABSORB_RADIUS = 7
REACH = 60.0  # how far from the player a flask can pour or suck (px)
SIP = 30  # cells used up by one drink
BLOOD_HEAL = 6.0  # per sip, only with the "Blutsauger" perk
THROW_SPEED = 260.0
SPRAY_SPEED = (150.0, 230.0)  # px/s: poured liquid squirts away from the body
SPRAY_SPREAD = 0.16  # radians
SPRAY_GRAVITY = 420.0
SPRAY_LIFETIME = 3.0
THROW_GRAVITY = 420.0
SHATTER_RADIUS_PER_CELL = 0.06  # splash radius grows with the content

# What a sip does: (heal, damage) per sip and a German description, by material key.
DRINK_EFFECTS: dict[str, tuple[float, float, str]] = {
    "blood": (0.0, 0.0, "Blut. Es schmeckt nach Eisen, heilen kann es dich nicht."),
    "acid": (0.0, 25.0, "Die Säure verätzt dich von innen!"),
    "tallow": (0.0, 0.0, "Fettig. Du fühlst dich schwer."),
    "mucus": (2.0, 0.0, "Zäh und kalt. Das Brennen lässt nach."),
    "pus": (0.0, 0.0, "Eiter. Dir wird übel, das Gift brennt in den Adern."),
    "magma": (0.0, 40.0, "Glutblut! Es verbrennt dich von innen."),
    "water": (0.0, 0.0, "Wasser. Erfrischend langweilig."),
    "oil": (0.0, 0.0, "Öl. Du fühlst dich geschmiert."),
    "tinte": (0.0, 0.0, "Tinte. Deine Zunge ist jetzt blau."),
    "stempelfarbe": (0.0, 0.0, "Stempelfarbe. Du fühlst dich genehmigt."),
    "siegellack": (0.0, 5.0, "Siegellack. Dein Mund ist jetzt versiegelt."),
    "fluxschnaps": (0.0, 0.0, "Flux-Schnaps. Die Welt dreht sich ein bisschen."),
}


class Flask:
    """A flask's content is stored by material **key**, so it survives universe changes.

    ``material`` is the id of that key in the active material set (or its stand-in).
    """

    def __init__(
        self,
        material: int | str | None = None,
        amount: float = 0,
        *,
        liquid: str | None = None,
        capacity: float = CAPACITY,
    ) -> None:
        self.key: str | None = None
        self.capacity: float = float(capacity)
        self.material = liquid if liquid is not None else material
        self.amount = int(amount)

    @property
    def material(self) -> int | None:
        return None if self.key is None else mat.id_of(self.key)

    @material.setter
    def material(self, value: int | str | None) -> None:
        if value is None or isinstance(value, str):
            self.key = value
        else:
            self.key = mat.key_of(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Flask):
            return NotImplemented
        return (self.key, self.amount) == (other.key, other.amount)

    def __repr__(self) -> str:
        return f"Flask({self.key!r}, {self.amount})"

    @property
    def empty(self) -> bool:
        return self.amount <= 0 or self.key is None

    @property
    def label_de(self) -> str:
        if self.empty:
            return "Leere Phiole"
        return f"Phiole: {self.name_de} ({round(100 * self.amount / CAPACITY)} %)"

    @property
    def name_de(self) -> str:
        if self.key is None:
            return ""
        spec = mat.LIBRARY.get(self.key)
        return spec.name_de if spec else NAME_DE[self.material]

    def _drain(self, cells: int) -> None:
        self.amount = max(0, self.amount - cells)
        if self.amount == 0:
            self.material = None

    def spray(self, x: float, y: float, angle: float, budget: float, rng) -> list[Droplet]:
        """Squirt up to ``budget`` cells out as flying droplets from (x, y) towards ``angle``.

        The droplets fly away from the body and only turn into liquid where they land,
        so pouring never drowns the one holding the flask.
        """
        if self.empty:
            return []
        count = min(self.amount, int(budget))
        drops = []
        for _ in range(count):
            a = angle + rng.uniform(-SPRAY_SPREAD, SPRAY_SPREAD)
            speed = rng.uniform(*SPRAY_SPEED)
            drops.append(Droplet(self.material, x, y, math.cos(a) * speed, math.sin(a) * speed))
        self._drain(count)
        return drops

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

    def drink(self, body: Body, blood_heals: bool = False) -> str:
        """Take a sip. Returns a German message (empty if nothing happened).

        Like in Noita, blood only heals with a perk (``blood_heals``): healing is rare.
        """
        if self.empty:
            return ""
        key = self.key
        heal, damage, message = DRINK_EFFECTS.get(key, (0.0, 0.0, "Es schmeckt nach nichts."))
        if key == "blood" and blood_heals:
            heal, message = BLOOD_HEAL, "Das Blut stillt deine Wunden."
        share = min(1.0, self.amount / SIP)
        body.hp = min(body.max_hp, body.hp + heal * share)
        if damage:
            body.hurt(damage * share, f"Getrunken: {self.name_de}")
        if key == "magma":
            body.burning = 3.0
        else:
            body.wet = max(body.wet, 3.0)
            body.burning = 0.0
        if key == "pus":
            body.poisoned = 8.0
        elif key == "blood":
            body.poisoned = 0.0  # fresh blood flushes the poison out
        self._drain(SIP)
        return message


@dataclass
class Droplet:
    """One squirted cell of liquid in flight; it becomes a world cell where it lands."""

    material: int
    x: float
    y: float
    vx: float
    vy: float
    age: float = 0.0
    alive: bool = True

    def update(self, world: World, dt: float, avoid: Body | None = None) -> None:
        """Fly; on landing put the liquid into the world (never inside ``avoid``)."""
        self.age += dt
        self.vy += SPRAY_GRAVITY * dt
        steps = max(1, int(math.hypot(self.vx, self.vy) * dt) + 1)
        for _ in range(steps):
            nx, ny = self.x + self.vx * dt / steps, self.y + self.vy * dt / steps
            if world.get(int(nx), int(ny)) != AIR or self.age >= SPRAY_LIFETIME:
                self.alive = False
                x, y = int(self.x), int(self.y)
                for up in range(6):  # pile up on what is already lying there
                    if avoid is not None and avoid.contains(x, y - up):
                        break  # never into the body that poured it
                    if world.get(x, y - up) == AIR:
                        world.set_cell(x, y - up, self.material)
                        break
                return
            self.x, self.y = nx, ny


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
