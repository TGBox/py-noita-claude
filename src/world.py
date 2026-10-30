"""Falling-sand cellular automaton (pure Python, no rendering dependencies).

The world is a flat ``bytearray`` of material ids. To stay fast without numpy the
grid is split into 16x16 chunks and only chunks that changed recently (or contain
fire, gas or lava) are simulated; everything else sleeps.
"""

from __future__ import annotations

import random
from functools import lru_cache

from src.materials import (
    AIR,
    BEDROCK,
    BLOCKS_BODY,
    BURN_RANGE,
    EMPTY,
    FALL_ALLOWED,
    FIRE,
    FLAMMABILITY,
    FLUIDITY,
    GAS,
    KIND,
    LAVA,
    LIFE_RANGE,
    LIQUID,
    OIL,
    POWDER,
    RISE_ALLOWED,
    SAND,
    SMOKE,
    STEAM,
    STONE,
    WATER,
    WOOD,
)

CHUNK_SHIFT = 4
CHUNK_SIZE = 1 << CHUNK_SHIFT
CHUNK_MASK = CHUNK_SIZE - 1
BORDER = 2  # thickness of the indestructible frame around the world
LAVA_SPEED = 0.2  # chance per frame that a lava cell tries to move

_NEIGHBORS = ((0, -1), (0, 1), (-1, 0), (1, 0))


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
    """Grid of materials plus the rules that make them move and react."""

    def __init__(self, width: int, height: int, seed: int | None = None) -> None:
        if width % 4 != 0:
            raise ValueError("width must be a multiple of 4")
        self.width = width
        self.height = height
        size = width * height
        self.grid = bytearray(size)
        self.life = bytearray(size)
        self.rng = random.Random(seed)
        self.frame = 0
        self._moved = bytearray(size)
        self._zeros = bytes(size)
        self._chunks_x = (width + CHUNK_SIZE - 1) >> CHUNK_SHIFT
        self._chunks_y = (height + CHUNK_SIZE - 1) >> CHUNK_SHIFT
        self._active: set[tuple[int, int]] = set()
        self.reset()

    # ------------------------------------------------------------------ setup

    def reset(self, fill: int = AIR) -> None:
        """Clear the world to ``fill`` and rebuild the bedrock frame.

        The underlying bytearrays are modified in place so that renderers holding
        a reference to ``grid`` stay valid.
        """
        size = self.width * self.height
        self.grid[:] = bytes([fill]) * size
        self.life[:] = self._zeros
        self._active.clear()
        w, h = self.width, self.height
        bedrock_row = bytes([BEDROCK]) * w
        for y in range(h):
            if y < BORDER or y >= h - BORDER:
                self.grid[y * w : (y + 1) * w] = bedrock_row
            else:
                for x in list(range(BORDER)) + list(range(w - BORDER, w)):
                    self.grid[y * w + x] = BEDROCK
        self.wake_all()

    def wake_all(self) -> None:
        """Mark every chunk as active."""
        self._active = {(cx, cy) for cx in range(self._chunks_x) for cy in range(self._chunks_y)}

    def sleep_all(self) -> None:
        """Put every chunk to sleep (cells changed later wake their own chunks)."""
        self._active.clear()

    def wake(self, x: int, y: int) -> None:
        """Activate the chunk of cell (x, y) and any chunk its neighbourhood touches."""
        cx, cy = x >> CHUNK_SHIFT, y >> CHUNK_SHIFT
        xs = [cx]
        ys = [cy]
        lx, ly = x & CHUNK_MASK, y & CHUNK_MASK
        if lx == 0:
            xs.append(cx - 1)
        elif lx == CHUNK_MASK:
            xs.append(cx + 1)
        if ly == 0:
            ys.append(cy - 1)
        elif ly == CHUNK_MASK:
            ys.append(cy + 1)
        active = self._active
        for a in xs:
            for b in ys:
                if 0 <= a < self._chunks_x and 0 <= b < self._chunks_y:
                    active.add((a, b))

    # --------------------------------------------------------------- accessors

    @property
    def active_chunks(self) -> int:
        """Number of chunks that will be simulated on the next step."""
        return len(self._active)

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

    def carve_disc(self, cx: int, cy: int, radius: int, material: int = AIR) -> None:
        """Raw disc fill used by world generation (replaces stone only, never wakes)."""
        grid, w = self.grid, self.width
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if BORDER <= x < w - BORDER and BORDER <= y < self.height - BORDER:
                i = y * w + x
                if grid[i] == STONE or material == STONE:
                    grid[i] = material

    def rect_blocked(self, x: int, y: int, w: int, h: int) -> bool:
        """True if a w*h box at (x, y) overlaps anything the player cannot walk through."""
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
        """Brush used by the sandbox tool. AIR erases; others fill free space."""
        rnd = self.rng.random
        sprinkle = KIND[material] in (POWDER, LIQUID, GAS) or material == FIRE
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            current = self.grid[y * self.width + x]
            if current == BEDROCK:
                continue
            if material == AIR:
                self.set_cell(x, y, AIR)
            elif KIND[current] in (EMPTY, GAS) or current == FIRE:
                if not sprinkle or rnd() < 0.4:
                    self.set_cell(x, y, material)

    def explode(self, cx: int, cy: int, radius: int) -> int:
        """Blast a crater. Returns the number of destroyed cells."""
        rnd = self.rng.random
        destroyed = 0
        inner = (radius * 0.7) ** 2
        outer = max(0, radius - 2) ** 2
        for dx, dy in disc_offsets(radius):
            x, y = cx + dx, cy + dy
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            current = self.grid[y * self.width + x]
            dist2 = dx * dx + dy * dy
            if current in (STONE, SAND, WOOD):
                if dist2 <= inner or rnd() < 0.6:
                    if current == WOOD and rnd() < 0.5:
                        self._ignite(x, y, current)
                    else:
                        self.set_cell(x, y, AIR)
                    destroyed += 1
            elif current == OIL:
                self._ignite(x, y, current)
            elif current == AIR and dist2 > outer and rnd() < 0.12:
                self.set_cell(x, y, FIRE)
        return destroyed

    # -------------------------------------------------------------- simulation

    def step(self) -> None:
        """Advance the simulation by one fixed tick."""
        self.frame += 1
        self._moved[:] = self._zeros
        active = sorted(self._active, key=lambda c: -c[1])
        self._active = set()
        for cx, cy in active:
            if self._update_chunk(cx, cy):
                self._active.add((cx, cy))

    def _update_chunk(self, cx: int, cy: int) -> bool:
        """Simulate one chunk bottom-up. Returns True if it must stay awake."""
        w = self.width
        grid = self.grid
        moved = self._moved
        rnd = self.rng.random
        x0 = cx << CHUNK_SHIFT
        x1 = min(x0 + CHUNK_SIZE, w)
        y0 = cy << CHUNK_SHIFT
        y1 = min(y0 + CHUNK_SIZE, self.height)
        columns = range(x0, x1) if self.frame & 1 else range(x1 - 1, x0 - 1, -1)
        keep = False
        for y in range(y1 - 1, y0 - 1, -1):
            row = y * w
            for x in columns:
                i = row + x
                m = grid[i]
                if m == AIR:
                    continue
                kind = KIND[m]
                if kind < POWDER or moved[i]:
                    continue
                if kind == POWDER:
                    self._fall(i, x, y, m, spread=0)
                elif kind == LIQUID:
                    if m == LAVA:
                        keep = True
                        if self._lava_react(i, x, y) or rnd() > LAVA_SPEED:
                            continue
                    self._fall(i, x, y, m, spread=FLUIDITY[m])
                elif kind == GAS:
                    keep = True
                    self._gas(i, x, y, m)
                else:
                    keep = True
                    self._flame(i, x, y)
        return keep

    def _swap(self, i: int, j: int, x1: int, y1: int, x2: int, y2: int) -> None:
        grid, life = self.grid, self.life
        grid[i], grid[j] = grid[j], grid[i]
        life[i], life[j] = life[j], life[i]
        self._moved[i] = 1
        self._moved[j] = 1
        self.wake(x1, y1)
        self.wake(x2, y2)

    def _fall(self, i: int, x: int, y: int, m: int, spread: int) -> None:
        """Powders and liquids: fall, slide diagonally, then (liquids) spread sideways."""
        w, grid = self.width, self.grid
        allowed = FALL_ALLOWED[m]
        below = i + w
        if y + 1 < self.height:
            if allowed[grid[below]]:
                self._swap(i, below, x, y, x, y + 1)
                return
            first = -1 if self.rng.random() < 0.5 else 1
            for dx in (first, -first):
                nx = x + dx
                if 0 <= nx < w and allowed[grid[below + dx]]:
                    self._swap(i, below + dx, x, y, nx, y + 1)
                    return
        if not spread:
            return
        row = y * w
        first = -1 if self.rng.random() < 0.5 else 1
        for dx in (first, -first):
            far = 0
            for k in range(1, spread + 1):
                nx = x + dx * k
                if not 0 <= nx < w:
                    break
                target = grid[row + nx]
                if target == AIR or KIND[target] == GAS:
                    far = k
                else:
                    break
            if far:
                self._swap(i, row + x + dx * far, x, y, x + dx * far, y)
                return

    def _gas(self, i: int, x: int, y: int, m: int) -> None:
        """Smoke and steam: rise, drift, and eventually dissipate."""
        w, grid, life = self.width, self.grid, self.life
        rnd = self.rng.random
        remaining = life[i] - 1
        if remaining <= 0:
            grid[i] = WATER if m == STEAM and rnd() < 0.3 else AIR
            life[i] = 0
            self.wake(x, y)
            return
        life[i] = remaining
        allowed = RISE_ALLOWED[m]
        roll = rnd()
        side = -1 if rnd() < 0.5 else 1
        if roll < 0.35:
            if y > 0 and allowed[grid[i - w]]:
                self._swap(i, i - w, x, y, x, y - 1)
            elif y > 0 and 0 <= x + side < w and allowed[grid[i - w + side]]:
                self._swap(i, i - w + side, x, y, x + side, y - 1)
        elif roll < 0.6 and 0 <= x + side < w and allowed[grid[i + side]]:
            self._swap(i, i + side, x, y, x + side, y)

    def _flame(self, i: int, x: int, y: int) -> None:
        """Fire: burn down, ignite flammable neighbours, get doused by water."""
        w, grid, life = self.width, self.grid, self.life
        rnd = self.rng.random
        remaining = life[i]
        if remaining <= 1:
            if rnd() < 0.25:
                grid[i] = SMOKE
                life[i] = self._new_life(SMOKE)
            else:
                grid[i] = AIR
                life[i] = 0
            self.wake(x, y)
            return
        life[i] = remaining - 1
        near_fuel = False
        above = -1
        for dx, dy in _NEIGHBORS:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < self.height):
                continue
            j = ny * w + nx
            target = grid[j]
            if target == WATER:
                grid[i] = AIR
                life[i] = 0
                grid[j] = STEAM
                life[j] = self._new_life(STEAM)
                self._moved[j] = 1
                self.wake(x, y)
                self.wake(nx, ny)
                return
            chance = FLAMMABILITY[target]
            if chance:
                near_fuel = True
                if rnd() < chance:
                    self._ignite(nx, ny, target)
            elif target == AIR and dy == -1:
                above = j
        if near_fuel or above < 0:
            return
        roll = rnd()
        if roll < 0.15:
            self._swap(i, above, x, y, x, y - 1)  # embers drift upwards
        elif roll < 0.18:
            grid[above] = SMOKE
            life[above] = self._new_life(SMOKE)
            self.wake(x, y - 1)

    def _lava_react(self, i: int, x: int, y: int) -> bool:
        """Lava meets water (turns to stone) or fuel (ignites it). True if lava was consumed."""
        w, grid, life = self.width, self.grid, self.life
        dx, dy = _NEIGHBORS[int(self.rng.random() * 4)]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < self.height):
            return False
        j = ny * w + nx
        target = grid[j]
        if target == WATER:
            grid[i] = STONE
            life[i] = 0
            grid[j] = STEAM
            life[j] = self._new_life(STEAM)
            self._moved[i] = 1
            self._moved[j] = 1
            self.wake(x, y)
            self.wake(nx, ny)
            return True
        chance = FLAMMABILITY[target]
        if chance and self.rng.random() < min(1.0, chance * 4):
            self._ignite(nx, ny, target)
        return False

    def _ignite(self, x: int, y: int, material: int) -> None:
        """Turn the burnable cell at (x, y) into fire."""
        i = y * self.width + x
        lo, hi = BURN_RANGE[material]
        self.grid[i] = FIRE
        self.life[i] = self.rng.randint(lo, hi)
        self._moved[i] = 1
        self.wake(x, y)
