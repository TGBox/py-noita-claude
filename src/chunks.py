"""Rigid chunks: tissue that an explosion cut loose moves as one solid body.

Like Noita's physics terrain, a detached piece keeps its shape and becomes a rigid
body with a centre of mass, a velocity, an angle and a spin. It falls, is pushed
away by the blast, rotates freely, bounces off what it hits (contacts away from
the centre of mass make it spin, so overhanging pieces topple off ledges) and
crushes what it lands on. Once it lies still it turns back into terrain.

Collision and motion run on the cell grid: every sub-step the body's cells are
rotated around its centre of mass and tested against the world.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src import native
from src.body import Body
from src.materials import BEDROCK, KIND, MATERIAL_COUNT, POWDER, SOLID
from src.world import World

SEARCH_MARGIN = 3.0  # search window = blast radius * this
MIN_CELLS = 6  # smaller bits are handled by crumbling
MAX_CELLS = 900  # bigger pieces stay put (they are probably not really loose)
GRAVITY = 420.0
MAX_SPEED = 360.0
MAX_SPIN = 8.0  # rad/s
RESTITUTION = 0.25  # share of the impact speed that bounces back
FRICTION = 0.75  # sideways speed kept per impact
SPIN_DAMPING = 0.85  # spin kept per impact
TORQUE = 1.2  # how strongly off-centre contacts make it spin
REST_TIME = 0.25  # seconds it must lie still before it turns back into terrain
MAX_LIFETIME = 10.0  # safety: settle whatever is still moving after this long
CRUSH_DAMAGE = 0.5  # per cell of the chunk, applied once to each body it lands on
MAX_CHUNKS = 24
BLAST_PUSH = 160.0  # px/s sideways for a one-cell chunk (bigger ones move less)
CORPSE_HEIGHT = 3  # flat, so remains never block a passage (the player steps over them)
SNAP_ANGLE = math.radians(18)  # settling this close to a right angle snaps to it
CONTACT_SPIN_DAMPING = 6.0  # per second while touching the ground
RESTING_IMPACT = 40.0  # px/s: slower contacts count as lying, not hitting


@dataclass
class Chunk:
    cells: list[tuple[int, int, int]]  # (x, y, material) in world coordinates
    vy: float = 0.0
    vx: float = 0.0
    omega: float = 0.0  # spin in rad/s (positive = clockwise on screen)
    resting: bool = False
    hit: set[int] = field(default_factory=set)
    x: float = 0.0  # centre of mass
    y: float = 0.0
    angle: float = 0.0
    shape: list[tuple[float, float, int]] = field(default_factory=list)  # offsets at angle 0
    still: float = 0.0
    age: float = 0.0
    inertia: float = 1.0

    def __post_init__(self) -> None:
        if not self.shape and self.cells:
            n = len(self.cells)
            self.x = sum(x for x, _y, _m in self.cells) / n + 0.5
            self.y = sum(y for _x, y, _m in self.cells) / n + 0.5
            self.shape = [(x + 0.5 - self.x, y + 0.5 - self.y, m) for x, y, m in self.cells]
            self.inertia = sum(ox * ox + oy * oy for ox, oy, _m in self.shape) / n + 1.0
            # the original grid, for mass-preserving rasterisation at any angle
            self._origin = (self.x, self.y)
            self._grid = {(x, y): m for x, y, m in self.cells}

    @property
    def size(self) -> int:
        return len(self.shape)

    @property
    def radius(self) -> float:
        if not hasattr(self, "_radius"):
            self._radius = math.sqrt(max(ox * ox + oy * oy for ox, oy, _m in self.shape))
        return self._radius

    def place(self, x: float, y: float, angle: float) -> list[tuple[int, int, int]]:
        """The body's cells for a given pose (rotation around the centre of mass).

        Every target cell looks up which original cell rotates onto it, so the shape
        keeps its mass and has no holes at any angle.
        """
        if abs(angle) < 1e-9:
            dx, dy = x - self._origin[0], y - self._origin[1]
            ix, iy = round(dx), round(dy)
            if abs(dx - ix) < 1e-9 and abs(dy - iy) < 1e-9:
                return [(gx + ix, gy + iy, m) for (gx, gy), m in self._grid.items()]
        c, s = math.cos(angle), math.sin(angle)
        ox0, oy0 = self._origin
        r = int(self.radius) + 2
        cells = []
        grid = self._grid
        for py in range(math.floor(y) - r, math.floor(y) + r + 1):
            for px in range(math.floor(x) - r, math.floor(x) + r + 1):
                ux, uy = px + 0.5 - x, py + 0.5 - y  # inverse rotation back to the shape
                gx = math.floor(ox0 + ux * c + uy * s)
                gy = math.floor(oy0 - ux * s + uy * c)
                m = grid.get((gx, gy))
                if m is not None:
                    cells.append((px, py, m))
        return cells


RIGID = [2 if m == BEDROCK else int(KIND[m] == SOLID) for m in range(MATERIAL_COUNT)]


def find_loose(world: World, cx: int, cy: int, radius: int) -> list[list[tuple[int, int]]]:
    """Solid groups near (cx, cy) that no longer touch the rest of the cave (Rust core)."""
    reach = int(radius * SEARCH_MARGIN) + 2
    groups = native.loose_groups(
        native.byte_view(world.grid), world.width, world.height, RIGID, (cx, cy),
        radius + 2, reach, MIN_CELLS, MAX_CELLS,
    )  # fmt: skip
    w = world.width
    return [[(i % w, i // w) for i in group] for group in groups]


def _solid(world: World, x: int, y: int) -> bool:
    if not (0 <= x < world.width and 0 <= y < world.height):
        return True
    cell = world.grid[y * world.width + x]
    return cell == BEDROCK or KIND[cell] in (SOLID, POWDER)


class FallingChunks:
    def __init__(self) -> None:
        self.items: list[Chunk] = []

    def clear(self) -> None:
        self.items.clear()

    def drop_corpse(self, world: World, x: int, y: int, width: int, material: int) -> None:
        """A dead creature's remains: a flat lump that falls and stays (Noita's corpses)."""
        if len(self.items) >= MAX_CHUNKS:
            return
        cells = []
        for dy in range(CORPSE_HEIGHT):
            inset = 1 if dy in (0, CORPSE_HEIGHT - 1) else 0
            for dx in range(inset, width - inset):
                if not _solid(world, x + dx, y + dy):
                    cells.append((x + dx, y + dy, material))
        if cells:
            self.items.append(Chunk(cells))

    def detach(self, world: World, cx: int, cy: int, radius: int) -> int:
        """Cut loose every free-hanging piece around a blast. Returns how many broke off."""
        added = 0
        for group in find_loose(world, cx, cy, radius):
            if len(self.items) >= MAX_CHUNKS:
                break
            cells = [(x, y, world.get(x, y)) for x, y in group]
            for x, y, _material in cells:
                world.set_cell(x, y, 0)
            chunk = Chunk(cells)
            # the blast shoves it away from the crater and sets it spinning
            dx, dy = chunk.x - cx, chunk.y - cy
            distance = math.hypot(dx, dy) or 1.0
            push = BLAST_PUSH / max(1.0, len(group) ** 0.5)
            chunk.vx = dx / distance * push
            chunk.vy = dy / distance * push * 0.5 - push * 0.2
            chunk.omega = max(-MAX_SPIN, min(MAX_SPIN, dx / distance * push / max(4.0, chunk.radius)))
            self.items.append(chunk)
            added += 1
        return added

    def update(self, world: World, dt: float, bodies: list[Body]) -> list[Chunk]:
        """Move every rigid chunk; returns the ones that came to rest this update."""
        landed = []
        for chunk in self.items:
            chunk.age += dt
            self._simulate(world, chunk, dt, bodies)
            if chunk.resting:
                self._settle(world, chunk)
                landed.append(chunk)
        self.items = [chunk for chunk in self.items if not chunk.resting]
        return landed

    # ------------------------------------------------------------------ physics

    def _simulate(self, world: World, chunk: Chunk, dt: float, bodies: list[Body]) -> None:
        chunk.vy = min(MAX_SPEED, chunk.vy + GRAVITY * dt)
        travel = (abs(chunk.vx) + abs(chunk.vy)) * dt + abs(chunk.omega) * dt * chunk.radius
        steps = max(1, min(12, math.ceil(travel)))
        h = dt / steps
        contact = False
        for _ in range(steps):
            nx, ny = chunk.x + chunk.vx * h, chunk.y + chunk.vy * h
            nangle = chunk.angle + chunk.omega * h
            cells = chunk.place(nx, ny, nangle)
            hits = [(x, y) for x, y, _m in cells if _solid(world, x, y)]
            if not hits:
                chunk.x, chunk.y, chunk.angle, chunk.cells = nx, ny, nangle, cells
                self._crush(chunk, bodies)
                continue
            contact = True
            # a body resting on a point can still turn about it: try the rotation alone
            if chunk.omega:
                for lift in (0, -1):
                    turned = chunk.place(chunk.x, chunk.y + lift, nangle)
                    if not any(_solid(world, x, y) for x, y, _m in turned):
                        chunk.y += lift
                        chunk.angle, chunk.cells = nangle, turned
                        break
            self._collide(chunk, hits)
            break
        if contact:  # rolling friction: a body lying on the ground stops rocking
            chunk.omega *= max(0.0, 1.0 - CONTACT_SPIN_DAMPING * dt)
        speed = abs(chunk.vx) + abs(chunk.vy)
        quarter = math.pi / 2
        squared = abs(chunk.angle - round(chunk.angle / quarter) * quarter) < SNAP_ANGLE
        spin_limit = 4.0 if squared else 2.5  # nearly flat bodies may still wobble a little
        if speed < 30 and abs(chunk.omega) < spin_limit and self._supported(world, chunk):
            chunk.still += dt
        else:
            chunk.still = 0.0
        if chunk.still >= REST_TIME or chunk.age > MAX_LIFETIME or chunk.y > world.height:
            chunk.resting = True

    def _collide(self, chunk: Chunk, hits: list[tuple[int, int]]) -> None:
        """Impulse response: bounce, friction, and spin from off-centre contacts."""
        hx = sum(x + 0.5 for x, _y in hits) / len(hits)
        hy = sum(y + 0.5 for _x, y in hits) / len(hits)
        lever_x, lever_y = hx - chunk.x, hy - chunk.y
        own = {(x, y) for x, y, _m in chunk.cells}
        vertical = sum(1 for x, y in hits if (x, y - 1) in own or (x, y + 1) in own)
        sideways = sum(1 for x, y in hits if (x - 1, y) in own or (x + 1, y) in own)
        if vertical >= sideways or abs(chunk.vy) >= abs(chunk.vx):  # floor or ceiling
            impact = chunk.vy
            chunk.vy = -chunk.vy * RESTITUTION
            chunk.vx *= FRICTION
            # pushed up at a point left of the centre: the right side keeps falling.
            # Gentle resting contacts only spin it if it really hangs off its support.
            if abs(impact) > RESTING_IMPACT:
                chunk.omega += -lever_x * impact * TORQUE / chunk.inertia
        else:  # a wall
            impact = chunk.vx
            chunk.vx = -chunk.vx * RESTITUTION
            chunk.omega += lever_y * impact * TORQUE / chunk.inertia
        if abs(chunk.vy) < 8:
            chunk.vy = 0.0
        chunk.omega = max(-MAX_SPIN, min(MAX_SPIN, chunk.omega * SPIN_DAMPING))
        if abs(chunk.omega) < 0.05:
            chunk.omega = 0.0

    @staticmethod
    def _supported(world: World, chunk: Chunk) -> bool:
        """Resting on something, with the centre of mass above its support."""
        own = {(x, y) for x, y, _m in chunk.cells}
        support = [
            x for x, y, _m in chunk.cells if (x, y + 1) not in own and _solid(world, x, y + 1)
        ]
        if not support:
            return False
        if min(support) - 2 <= chunk.x <= max(support) + 3:
            return True
        # clearly hanging over an edge: tip it towards the overhang and let it fall
        chunk.omega += 1.5 if chunk.x > max(support) else -1.5
        return False

    def _crush(self, chunk: Chunk, bodies: list[Body]) -> None:
        if chunk.vy < 60:
            return
        bottom: dict[int, int] = {}
        for x, y, _m in chunk.cells:
            bottom[x] = max(bottom.get(x, y), y)
        for body in bodies:
            if body.dead or id(body) in chunk.hit:
                continue
            if any(body.contains(x + 0.5, y + 1.5) for x, y in bottom.items()):
                chunk.hit.add(id(body))
                body.hurt(min(60.0, CRUSH_DAMAGE * chunk.size), "Herabstürzendes Gewebe")

    @staticmethod
    def _settle(world: World, chunk: Chunk) -> None:
        """Turn the body back into terrain (snapped upright if it is nearly square)."""
        chunk.resting = True
        quarter = math.pi / 2
        nearest = round(chunk.angle / quarter) * quarter
        if abs(chunk.angle - nearest) < SNAP_ANGLE:
            for lift in (0, -1, -2, -3):
                snapped = chunk.place(chunk.x, chunk.y + lift, nearest)
                if not any(_solid(world, x, y) for x, y, _m in snapped):
                    chunk.cells = snapped
                    break
        for x, y, material in chunk.cells:
            if 0 <= x < world.width and 0 <= y < world.height and world.get(x, y) != BEDROCK:
                world.set_cell(x, y, material, force=True)
