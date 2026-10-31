"""The world grid and the player-facing operations on it.

The per-tick simulation runs in the Rust core (``src/native.py``); this class owns
the buffers and implements the small, local operations (painting, explosions,
collision queries) in Python.
"""

from __future__ import annotations

import random
from functools import lru_cache
from math import isqrt

from src.materials import (
    AIR,
    BEDROCK,
    BLOCKS_BODY,
    BURN_RANGE,
    DEBRIS,
    EMPTY,
    FIRE,
    FLAME,
    FLAMMABILITY,
    GAS,
    HARDNESS,
    HARDNESS_SHRINK,
    KIND,
    LIFE_RANGE,
    LIQUID,
    POWDER,
    SINEW,
    SOLID,
    SPARK,
)
from src.native import Core

CHUNK_SHIFT = 4
CHUNK_SIZE = 1 << CHUNK_SHIFT
CHUNK_MASK = CHUNK_SIZE - 1
BORDER = 2  # thickness of the indestructible frame around the world

Rect = tuple[int, int, int, int]  # x0, y0, x1, y1 (end exclusive)


@lru_cache(maxsize=64)
def disc_offsets(radius: int) -> tuple[tuple[int, int], ...]:
    """Offsets of all cells within a (slightly rounded) disc of the given radius."""
    limit = radius * radius + radius
    return tuple(
        (dx, dy)
        for dy in range(-radius, radius + 1)
        for dx in range(-radius, radius + 1)
        if dx * dx + dy * dy <= limit
    )


class World:
    """Grid of materials; simulation is delegated to the Rust core."""

    def __init__(self, width: int, height: int, seed: int | None = None) -> None:
        self.width = width
        self.height = height
        size = width * height
        self.grid = bytearray(size)
        self.life = bytearray(size)
        self.chunks_x = (width + CHUNK_MASK) >> CHUNK_SHIFT
        self.chunks_y = (height + CHUNK_MASK) >> CHUNK_SHIFT
        self.active = bytearray(self.chunks_x * self.chunks_y)
        self.rng = random.Random(seed)
        self.frame = 0
        self._core = Core(
            width, height, self.rng.getrandbits(64), self.grid, self.life, self.active
        )
        self.reset()

    # ------------------------------------------------------------------ setup

    def reseed(self, seed: int) -> None:
        """Reseed both the Python and the native random generators."""
        self.rng.seed(seed)
        self._core.seed(self.rng.getrandbits(64))

    def reset(self, fill: int = AIR) -> None:
        """Clear the world to ``fill`` and rebuild the bedrock frame.

        Buffers are modified in place: the native core holds views of them.
        """
        w, h = self.width, self.height
        self.grid[:] = bytes([fill]) * (w * h)
        self.life[:] = bytes(w * h)
        bedrock_row = bytes([BEDROCK]) * w
        for y in range(h):
            if y < BORDER or y >= h - BORDER:
                self.grid[y * w : (y + 1) * w] = bedrock_row
            else:
                row = y * w
                self.grid[row : row + BORDER] = bedrock_row[:BORDER]
                self.grid[row + w - BORDER : row + w] = bedrock_row[:BORDER]
        self.wake_all()

    def mirror(self) -> None:
        """Flip the whole world left to right (for the mirror world)."""
        w = self.width
        for y in range(self.height):
            row = slice(y * w, (y + 1) * w)
            self.grid[row] = self.grid[row][::-1]
            self.life[row] = self.life[row][::-1]
        self.wake_all()

    def wake_all(self) -> None:
        """Mark every chunk as active."""
        self.active[:] = b"\x01" * len(self.active)

    def sleep_all(self) -> None:
        """Put every chunk to sleep (later changes wake their own chunks)."""
        self.active[:] = bytes(len(self.active))

    def wake(self, x: int, y: int) -> None:
        """Activate the chunk of cell (x, y) and the neighbour chunks its edge touches."""
        cx, cy = x >> CHUNK_SHIFT, y >> CHUNK_SHIFT
        lx, ly = x & CHUNK_MASK, y & CHUNK_MASK
        x_lo = cx - 1 if lx == 0 and cx > 0 else cx
        x_hi = cx + 1 if lx == CHUNK_MASK and cx + 1 < self.chunks_x else cx
        y_lo = cy - 1 if ly == 0 and cy > 0 else cy
        y_hi = cy + 1 if ly == CHUNK_MASK and cy + 1 < self.chunks_y else cy
        for b in range(y_lo, y_hi + 1):
            row = b * self.chunks_x
            for a in range(x_lo, x_hi + 1):
                self.active[row + a] = 1

    # --------------------------------------------------------------- accessors

    @property
    def active_chunks(self) -> int:
        """Number of chunks flagged for simulation."""
        return len(self.active) - self.active.count(0)

    def get(self, x: int, y: int) -> int:
        """Material at (x, y); anything outside the world counts as bedrock."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y * self.width + x]
        return BEDROCK

    def count(self, material: int) -> int:
        """Number of cells holding ``material``."""
        return self.grid.count(material)

    def _new_life(self, material: int) -> int:
        lo, hi = LIFE_RANGE[material]
        return self.rng.randint(lo, hi) if hi else 0

    def set_cell(self, x: int, y: int, material: int, *, force: bool = False) -> bool:
        """Set one cell and wake its surroundings. Bedrock is protected unless forced."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        i = y * self.width + x
        if self.grid[i] == BEDROCK and not force:
            return False
        self.grid[i] = material
        self.life[i] = self._new_life(material)
        self.wake(x, y)
        return True

    def fill_disc(self, cx: int, cy: int, radius: int, material: int) -> None:
        """Fast raw disc fill for world generation (no waking, bedrock frame kept)."""
        w, h = self.width, self.height
        value = bytes([material])
        limit = radius * radius + radius
        for dy in range(-radius, radius + 1):
            y = cy + dy
            if not BORDER <= y < h - BORDER:
                continue
            half = isqrt(limit - dy * dy)
            x0 = max(cx - half, BORDER)
            x1 = min(cx + half + 1, w - BORDER)
            if x1 > x0:
                self.grid[y * w + x0 : y * w + x1] = value * (x1 - x0)

    def rect_blocked(self, x: int, y: int, w: int, h: int) -> bool:
        """True if a w*h box at (x, y) overlaps anything a body cannot pass through."""
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            return True
        grid, width = self.grid, self.width
        for yy in range(y, y + h):
            row = yy * width
            for xx in range(x, x + w):
                if BLOCKS_BODY[grid[row + xx]]:
                    return True
        return False

    # ------------------------------------------------------------ player tools

    def paint(self, cx: int, cy: int, radius: int, material: int) -> None:
        """Sandbox brush. AIR erases; other materials fill free space."""
        rnd = self.rng.random
        sprinkle = KIND[material] in (POWDER, LIQUID, GAS, FLAME)
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            current = self.grid[y * self.width + x]
            if current == BEDROCK:
                continue
            if material == AIR:
                if current != AIR:
                    self.set_cell(x, y, AIR)
            elif KIND[current] in (EMPTY, GAS, FLAME) and (not sprinkle or rnd() < 0.4):
                self.set_cell(x, y, material)

    def explode(self, cx: int, cy: int, radius: int) -> int:
        """Blast a crater. Returns the number of destroyed solid/powder cells.

        Harder materials only break closer to the centre (see ``HARDNESS_SHRINK``):
        a small spark chips flesh but bounces off bone, enamel needs a big blast.
        """
        rnd = self.rng.random
        destroyed = 0
        outer = max(0, radius - 2) ** 2
        reach = [radius - shrink for shrink in HARDNESS_SHRINK]
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            current = self.grid[y * self.width + x]
            if current == BEDROCK:
                continue
            dist2 = dx * dx + dy * dy
            if KIND[current] in (SOLID, POWDER):
                limit = reach[HARDNESS[current]]
                if limit < 0 or dist2 > limit * limit:
                    continue  # too hard this far from the centre
            if FLAMMABILITY[current] and rnd() < 0.5:
                self.ignite(x, y)
            elif KIND[current] in (SOLID, POWDER):
                if dist2 <= (limit * 0.7) ** 2 or rnd() < 0.6:
                    debris, chance = DEBRIS[current]
                    self.set_cell(x, y, debris if rnd() < chance else AIR)
                    destroyed += 1
            elif current == AIR and dist2 > outer and rnd() < 0.12:
                self.set_cell(x, y, FIRE)
        return destroyed + self.crumble_loose(cx, cy, radius + 2)

    def electrify(self, cx: int, cy: int, radius: int) -> int:
        """Send a nerve current into the sinew around (cx, cy). Returns cells charged."""
        charged = 0
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if 0 <= x < self.width and 0 <= y < self.height and self.grid[y * self.width + x] == SINEW:
                self.set_cell(x, y, SPARK, force=True)
                charged += 1
        return charged

    def dig(self, cx: int, cy: int, radius: int, *, force: bool = False) -> int:
        """Bore a hole: solids and powders in the disc vanish (bedrock stays).

        Like a blast, a bore shrinks against harder materials; ``force`` clears
        everything but bedrock (used when the game itself opens a passage).
        """
        dug = 0
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            current = self.grid[y * self.width + x]
            if current == BEDROCK or KIND[current] not in (SOLID, POWDER):
                continue
            if not force:
                limit = radius - HARDNESS_SHRINK[HARDNESS[current]]
                if limit < 0 or dx * dx + dy * dy > limit * limit:
                    continue
            self.set_cell(x, y, AIR)
            dug += 1
        return dug

    @staticmethod
    def diggable(material: int, radius: int) -> bool:
        """Can a bore of this radius get through ``material`` at all?"""
        if material == BEDROCK or KIND[material] not in (SOLID, POWDER):
            return False
        return radius - HARDNESS_SHRINK[HARDNESS[material]] >= 0

    def crumble_loose(self, cx: int, cy: int, radius: int, passes: int = 12) -> int:
        """Break off loose solid fragments (cells with at most two solid neighbours).

        Explosions leave single pixels and thin splinters behind; those crumble into
        their debris (bone into dust, flesh into blood, ...) so they cannot snag bodies.
        Returns the number of crumbled cells.
        """
        w, h, grid = self.width, self.height, self.grid
        crumbled = 0
        for _ in range(passes):
            loose: list[tuple[int, int, int]] = []
            for y in range(max(1, cy - radius), min(h - 1, cy + radius + 1)):
                row = y * w
                for x in range(max(1, cx - radius), min(w - 1, cx + radius + 1)):
                    material = grid[row + x]
                    if KIND[material] != SOLID or HARDNESS[material] >= 3:
                        continue  # bedrock and enamel do not splinter
                    neighbours = 0
                    for ny in (row - w, row, row + w):
                        for nx in (x - 1, x, x + 1):
                            if KIND[grid[ny + nx]] == SOLID:
                                neighbours += 1
                    if neighbours - 1 <= 2:  # minus the cell itself
                        loose.append((x, y, material))
            if not loose:
                break
            for x, y, material in loose:
                debris, _chance = DEBRIS[material]
                self.set_cell(x, y, debris)
            crumbled += len(loose)
        return crumbled

    def splash(self, cx: int, cy: int, radius: int, material: int) -> int:
        """Fill free cells in a disc with ``material`` (a spell payload). Returns cells set.

        Liquids and powders fill the disc; gases and fire are sprinkled. Fire also
        ignites flammable cells it lands on.
        """
        rnd = self.rng.random
        sprinkle = KIND[material] in (GAS, FLAME)
        placed = 0
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            current = self.grid[y * self.width + x]
            if current == BEDROCK:
                continue
            if material == FIRE and FLAMMABILITY[current]:
                self.ignite(x, y)
                placed += 1
            elif KIND[current] in (EMPTY, GAS, FLAME) and (not sprinkle or rnd() < 0.6):
                self.set_cell(x, y, material)
                placed += 1
        return placed

    def ignite(self, x: int, y: int) -> None:
        """Turn the cell at (x, y) into fire that burns as long as its fuel would."""
        i = y * self.width + x
        lo, hi = BURN_RANGE[self.grid[i]]
        self.grid[i] = FIRE
        self.life[i] = self.rng.randint(lo, hi) if hi else self._new_life(FIRE)
        self.wake(x, y)

    # -------------------------------------------------------------- simulation

    def step(self, area: Rect | None = None) -> int:
        """Advance one tick. Only chunks overlapping ``area`` (cells) are simulated.

        Chunks outside the area keep their state and continue once they are inside
        again. Returns the number of simulated chunks.
        """
        self.frame += 1
        if area is None:
            return self._core.step(0, 0, self.chunks_x, self.chunks_y)
        x0, y0, x1, y1 = area
        return self._core.step(
            max(0, x0 >> CHUNK_SHIFT),
            max(0, y0 >> CHUNK_SHIFT),
            min(self.chunks_x, (x1 + CHUNK_MASK) >> CHUNK_SHIFT),
            min(self.chunks_y, (y1 + CHUNK_MASK) >> CHUNK_SHIFT),
        )
