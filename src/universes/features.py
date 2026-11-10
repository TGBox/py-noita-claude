"""Signature terrain of the six MVP universes on top of the organism caves (bible 03).

The organism generator builds the caves (proven in play); this module gives every
universe the few things that make it recognisable. It works in two phases:

- ``shape`` runs right after the caves exist: it carves and builds solid features
  (islands, the kitchen floor, the dance floor, the bell tower ...). Arenas and the
  quest giver are chosen afterwards on the final terrain.
- ``flood`` runs after the paths are guaranteed: it pours the liquids (syrup sea,
  flooded nave, ink lakes, acid pools) that the player swims or wades through.

``keep`` lists (x, y, radius) circles that stay untouched: spawn, anchor point,
arenas, quest giver. All writes go straight into ``world.grid`` (the native core
views that buffer); the caller wakes the world afterwards.
"""

from __future__ import annotations

import math
import random
from typing import Any

from src import materials as mat
from src.world import BORDER

Keep = list[tuple[int, int, int]]
SKIN = 6  # Aktenhalde: burnable paper only this deep behind any open cell


class _Cells:
    """Small helper around the world buffer (bounds, solid test, keep-out circles)."""

    def __init__(self, world: Any, keep: Keep) -> None:
        self.w, self.h, self.g = world.width, world.height, world.grid
        self.keep = keep
        self.level: Any = None

    def inside(self, x: int, y: int) -> bool:
        return BORDER <= x < self.w - BORDER and BORDER <= y < self.h - BORDER

    def get(self, x: int, y: int) -> int:
        return self.g[y * self.w + x] if self.inside(x, y) else mat.BEDROCK

    def put(self, x: int, y: int, value: int) -> None:
        """Write a cell; keep circles only refuse matter (carving air buries nobody)."""
        if self.inside(x, y) and (value == mat.AIR or not self.kept(x, y)):
            self.g[y * self.w + x] = value

    def kept(self, x: int, y: int) -> bool:
        return any((x - kx) ** 2 + (y - ky) ** 2 < r * r for kx, ky, r in self.keep)

    def solid(self, x: int, y: int) -> bool:
        return mat.KIND[self.get(x, y)] in (mat.SOLID, mat.POWDER)

    def air(self, x: int, y: int) -> bool:
        return self.inside(x, y) and self.get(x, y) == mat.AIR

    def ellipse(
        self, cx: int, cy: int, rx: int, ry: int, value: int, only: set[int] | None = None
    ) -> None:
        for y in range(cy - ry, cy + ry + 1):
            dy = (y - cy) / max(1, ry)
            half = int(rx * math.sqrt(max(0.0, 1 - dy * dy)))
            for x in range(cx - half, cx + half + 1):
                if only is None or self.get(x, y) in only:
                    self.put(x, y, value)

    def rect(
        self, x0: int, y0: int, x1: int, y1: int, value: int, only: set[int] | None = None
    ) -> None:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if only is None or self.get(x, y) in only:
                    self.put(x, y, value)

    def floors(self, x0: int, y0: int, x1: int, y1: int, step: int = 3) -> list[tuple[int, int]]:
        """Air cells with solid ground right below (every ``step``-th column)."""
        found = []
        for x in range(max(BORDER, x0), min(self.w - BORDER, x1), step):
            for y in range(max(BORDER, y0), min(self.h - BORDER - 1, y1)):
                if self.air(x, y) and self.solid(x, y + 1):
                    found.append((x, y))
        return found

    def ceilings(self, x0: int, y0: int, x1: int, y1: int, step: int = 3) -> list[tuple[int, int]]:
        """Air cells with solid rock right above."""
        found = []
        for x in range(max(BORDER, x0), min(self.w - BORDER, x1), step):
            for y in range(max(BORDER + 1, y0), min(self.h - BORDER, y1)):
                if self.air(x, y) and self.solid(x, y - 1):
                    found.append((x, y))
        return found

    def pool(self, x: int, y: int, depth: int, liquid: int) -> None:
        """Fill the hollow around floor cell (x, y) up to ``depth`` cells with ``liquid``."""
        level = y - depth + 1
        for dx in (1, -1):
            cx = x if dx == 1 else x - 1
            while self.inside(cx, y) and self.air(cx, y) and abs(cx - x) < depth * 6:
                fy = y
                while fy + 1 < self.h - BORDER and self.air(cx, fy + 1) and fy - y < depth:
                    fy += 1
                if not self.solid(cx, fy + 1):
                    break  # the hollow is open below here: stop instead of leaking
                for yy in range(max(level, BORDER), fy + 1):
                    if self.air(cx, yy):
                        self.put(cx, yy, liquid)
                cx += dx


def _id(key: str) -> int:
    return mat.MAT_ID[key]


# --------------------------------------------------------------------------- shape


def shape(
    world: Any, key: str, rng: random.Random, keep: Keep, level: Any = None
) -> dict[str, Any]:
    """Build the solid signature features of ``key``; returns state for ``flood``.

    The first two ``keep`` circles are spawn and exit: after the big carving they get a
    ledge to stand on, so nobody starts or ends on a floating leftover of the caves."""
    builder = _SHAPERS.get(key)
    if builder is None:
        return {}
    cells = _Cells(world, keep)
    cells.level = level  # the organism level under the features (spawn, exit, arena, vault)
    state = builder(cells, rng)
    ledge = _id(PERCH.get(key, "rock"))
    for x, y, r in keep[:2]:
        _perch(cells, x, y, r, ledge)
    return state


PERCH = {
    "fleischwelt": "bone",
    "aktenhalde": "aktendeckel",
    "glibbria": "zuckerguss",
    "kruemelreich": "kruemel",
    "sporenklub": "pilzhut",
    "abtei": "mauerwerk",
}


def _perch(c: _Cells, x: int, y: int, r: int, ledge: int) -> None:
    """Give the body at (x, y) ground: a ledge right under it if the carving left air."""
    for fy in range(y, y + r + 4):
        if c.solid(x, fy):
            return  # standing on something already
    feet = y + r // 2 + 3  # just below the feet of a body centred at (x, y)
    for yy in range(feet, feet + 4):
        for xx in range(x - 16, x + 17):
            if c.inside(xx, yy) and c.get(xx, yy) == mat.AIR:
                c.g[yy * c.w + xx] = ledge


def _shape_fleischwelt(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """Schlund: rows of enamel teeth on the cave ceilings and floors of the upper third."""
    enamel = _id("enamel")
    band = c.h // 3
    for x, y in c.ceilings(0, 0, c.w, band, step=7):
        if rng.random() < 0.55:
            _tooth(c, x, y, 1, rng.randint(4, 9), enamel)
    for x, y in c.floors(0, 0, c.w, band, step=9):
        if rng.random() < 0.3:
            _tooth(c, x, y, -1, rng.randint(3, 6), enamel)
    return {}


def _tooth(c: _Cells, x: int, y: int, direction: int, length: int, value: int) -> None:
    """A pointed tooth growing from (x, y) downwards (1) or upwards (-1)."""
    for k in range(length):
        half = max(0, (length - k) // 3)
        for dx in range(-half, half + 1):
            if c.air(x + dx, y + k * direction):
                c.put(x + dx, y + k * direction, value)


def _shape_aktenhalde(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """Registratur, Grossraumbuero and Archivkeller (bible 03) on top of the paper caves.

    - Registratur (left third): shelf boards across the open caves, loaded with stacks of
      files (burnable cover and fuel).
    - Grossraumbuero (middle third): the Sitzungssaal, a flat hall with conference tables
      and galleries (the mid-boss arena), and desks on the cave floors around it.
    - Two Rohrpost shafts between the thirds: fast ways up and down with rest ledges.
    - Aktenschraenke everywhere: small lockers in the walls behind a paper door (burn or
      dig it open); the caller puts loot into ``state["caches"]``.
    """
    board, paper = _id("aktendeckel"), _id("papier")
    third = c.w // 3
    hall = _conference_hall(c, rng, third + 26, 2 * third - 26, board, paper)
    for x in (third, 2 * third):
        _tube(c, x + rng.randint(-8, 8), c.h // 9, c.h - c.h // 9, board, avoid=hall)
    for y in range(c.h // 8, c.h - 20, 34):
        x = BORDER
        while x < third - 12:
            length, gap = rng.randint(18, 28), rng.randint(12, 18)
            probes = (x, x + length // 2)
            if all(c.air(xx, y) and c.air(xx, y - 6) and c.air(xx, y + 6) for xx in probes):
                c.rect(x, y, x + length, y + 2, board, only={mat.AIR})
                for _ in range(rng.randint(1, 2)):  # stacks of files on the board
                    sx, wide = x + rng.randint(1, length - 7), rng.randint(3, 6)
                    c.rect(sx, y - rng.randint(3, 8), sx + wide, y, paper, only={mat.AIR})
            x += length + gap
    _desks(c, rng, third + 12, 2 * third - 12, board, paper, hall)
    state: dict[str, Any] = {"caches": _lockers(c, rng, board, paper, hall)}
    if hall is not None:
        state["mid_arena"] = hall
    return state


HALL_SIZE = (208, 62)  # Sitzungssaal interior (cells): well below one screen (640 x 360)
GLAZE_STONES = 18  # Glibbria: sugar-glaze stepping stones between the islands
TUBE_WIDTH = 14  # Rohrpost shaft interior
LOCKER_SIZE = (14, 10)  # Aktenschrank interior
LOCKERS = 7
# Aktenhalde "Brandabschnitte": ink-paper lines cut the paper into sections (cells)
FIREBREAK_CELL = (160, 120)
FIREBREAK_THICKNESS = 3


def _conference_hall(
    c: _Cells, rng: random.Random, x0: int, x1: int, board: int, paper: int
) -> tuple[int, int, int, int] | None:
    """Carve the Sitzungssaal where the caves are most open (so it becomes a junction),
    away from spawn and exit. Paper floor on cardboard, tables and two galleries."""
    wide, high = min(HALL_SIZE[0], x1 - x0), HALL_SIZE[1]
    if wide < 120:
        return None
    best, best_open = None, -1.0
    for _ in range(24):
        left = rng.randint(x0, x1 - wide)
        top = rng.randint(c.h // 6, c.h - c.h // 6 - high)
        cx, cy = left + wide // 2, top + high // 2
        if any(abs(cx - kx) < wide // 2 + r + 30 and abs(cy - ky) < high // 2 + r + 30
               for kx, ky, r in c.keep):  # fmt: skip
            continue
        if c.keep and math.dist((cx, cy), c.keep[0][:2]) < c.w * 0.28:
            continue  # the mid-boss lives here: not right next to the start
        probes = [(x, y) for y in range(top, top + high, 6) for x in range(left, left + wide, 6)]
        cells = [c.air(x, y) for x, y in probes]
        share = sum(cells) / len(cells)
        if share > best_open:
            best, best_open = (left, top), share
    if best is None:
        return None
    left, top = best
    right, floor = left + wide, top + high
    c.rect(left, top, right, floor, mat.AIR)
    c.rect(left - 2, floor + 2, right + 2, floor + 5, board)  # cardboard under ...
    c.rect(left - 2, floor, right + 2, floor + 2, paper)  # ... a paper floor that can burn
    c.rect(left - 2, top - 3, right + 2, top, board, only=_solids())  # ceiling beam
    tables = max(2, wide // 62)
    for i in range(tables):  # conference tables: hop on, fight from, hide behind
        tx = left + (i + 1) * wide // (tables + 1) + rng.randint(-6, 6)
        half = rng.randint(11, 15)
        c.rect(tx - half, floor - 10, tx + half, floor - 8, board)
        for leg in (tx - half + 2, tx + half - 4):
            c.rect(leg, floor - 8, leg + 2, floor, board)
        if rng.random() < 0.7:  # a stack of files on the table
            sx = tx + rng.randint(-half + 2, half - 7)
            c.rect(sx, floor - 10 - rng.randint(3, 6), sx + rng.randint(3, 5), floor - 10, paper)
    for side, gy in ((0, floor - 27), (1, floor - 27), (0, floor - 44), (1, floor - 44)):
        length = rng.randint(34, 50) if gy == floor - 27 else rng.randint(22, 32)
        gx = left if side == 0 else right - length
        c.rect(gx, gy, gx + length, gy + 2, board)  # galleries along both walls
    return (left, top, right, floor)


def _solids() -> set[int]:
    return {i for i, kind in enumerate(mat.KIND) if kind in (mat.SOLID, mat.POWDER)}


def _in_rect(rect: tuple[int, int, int, int] | None, x: int, y: int, pad: int = 0) -> bool:
    return rect is not None and (
        rect[0] - pad <= x < rect[2] + pad and rect[1] - pad <= y < rect[3] + pad
    )


def _tube(
    c: _Cells, x: int, y0: int, y1: int, board: int,
    avoid: tuple[int, int, int, int] | None = None,
) -> None:  # fmt: skip
    """A Rohrpost shaft: a straight vertical way through the paper with cardboard walls
    (only where there was paper: caves it crosses stay open) and rest ledges for
    levitating up."""
    half = TUBE_WIDTH // 2
    solid = _solids() - {mat.BEDROCK}
    for y in range(y0, y1):
        if _in_rect(avoid, x, y, half + 4):
            continue
        for wx in (*range(x - half - 2, x - half), *range(x + half, x + half + 2)):
            if c.get(wx, y) in solid:
                c.put(wx, y, board)
        c.rect(x - half, y, x + half, y + 1, mat.AIR)
        if (y - y0) % 30 == 29:
            left = ((y - y0) // 30) % 2 == 0
            lx = x - half if left else x + half - 5
            c.rect(lx, y, lx + 5, y + 2, board)


def _desks(
    c: _Cells, rng: random.Random, x0: int, x1: int, board: int, paper: int,
    hall: tuple[int, int, int, int] | None,
) -> None:  # fmt: skip
    """Grossraumbuero: desks on the cave floors (small platforms, some with files)."""
    floors = c.floors(x0, BORDER, x1, c.h - BORDER, step=11)
    rng.shuffle(floors)
    placed: list[tuple[int, int]] = []
    for x, y in floors:
        if len(placed) >= 16:
            break
        if _in_rect(hall, x, y, 12):
            continue
        if any(abs(x - px) < 40 and abs(y - py) < 24 for px, py in placed):
            continue
        room = [(xx, yy) for xx in range(x - 9, x + 10, 3) for yy in range(y - 30, y - 6, 4)]
        if not all(c.air(xx, yy) for xx, yy in room):
            continue  # needs room for the desk and a standing body on it
        feet = [next((d for d in range(1, 8) if c.solid(lx, y + d)), 0) for lx in (x - 8, x + 8)]
        if not all(feet):
            continue  # too steep for a desk
        c.rect(x - 9, y - 9, x + 10, y - 7, board)
        for leg, drop in zip((x - 8, x + 7), feet, strict=True):
            c.rect(leg, y - 7, leg + 2, y + drop, board, only={mat.AIR})
        if rng.random() < 0.5:
            sx = x + rng.randint(-7, 3)
            c.rect(sx, y - 9 - rng.randint(2, 5), sx + rng.randint(3, 5), y - 9, paper)
        placed.append((x, y))


def _lockers(
    c: _Cells, rng: random.Random, board: int, paper: int,
    hall: tuple[int, int, int, int] | None,
) -> list[tuple[int, int]]:  # fmt: skip
    """Aktenschraenke: cardboard boxes inside the paper walls right next to a cave, closed
    by a paper door towards the cave. Returns the floor centre inside each locker."""
    wide, high = LOCKER_SIZE
    found: list[tuple[int, int]] = []
    for _ in range(4000):
        if len(found) >= LOCKERS:
            break
        x, y = rng.randint(BORDER + 8, c.w - BORDER - wide - 8), rng.randint(40, c.h - 40 - high)
        box = (x - 2, y - 2, x + wide + 2, y + high + 2)
        if any(abs(x - fx) < 150 and abs(y - fy) < 110 for fx, fy in found):
            continue
        if _in_rect(hall, x + wide // 2, y + high // 2, 30):
            continue
        # the door must not sit on a firebreak line (ink paper does not burn)
        if any((yy % FIREBREAK_CELL[1]) < FIREBREAK_THICKNESS for yy in range(y + 1, y + high)):
            continue
        cells = [(xx, yy) for yy in range(box[1], box[3], 2) for xx in range(box[0], box[2], 2)]
        if any(c.get(xx, yy) != paper or c.kept(xx, yy) for xx, yy in cells):
            continue
        side = rng.choice((-1, 1))
        edge = box[0] if side == -1 else box[2] - 1
        gap = next((d for d in range(1, 7) if c.air(edge + side * d, y + high - 2)), 0)
        if not gap or not all(c.air(edge + side * gap, yy) for yy in range(y + 2, y + high)):
            continue
        cave = edge + side * gap
        if any((xx % FIREBREAK_CELL[0]) < FIREBREAK_THICKNESS
               for xx in range(min(edge, cave) - 2, max(edge, cave) + 3)):  # fmt: skip
            continue
        c.rect(*box, board)
        c.rect(x, y, x + wide, y + high, mat.AIR)
        door = edge if side == -1 else edge - 1  # the two frame columns facing the cave
        c.rect(door, y + 1, door + 2, y + high, paper)
        found.append((x + wide // 2, y + high - 1))
    return found


def _shape_glibbria(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """Floating jelly islands over the syrup sea (bible 03) instead of jelly caves.

    The organism caves are wiped (only the treasure vault survives as a lump); then:
    a start island under the spawn, a bowl island as mid-boss arena ("Gelee-Schuessel"),
    an exit island far from the start (in a boss slot: the boss bowl), islands on several
    heights to bounce between, a few big ones with a chewing-gum cave and a cache inside,
    domes rising out of the sea as shores, and sugar-glaze stepping stones.
    """
    jelly, red, glaze = _id("glibber"), _id("glibber_rot"), _id("zuckerguss")
    line = int(c.h * SEA_LEVEL)
    level = c.level
    vault = getattr(level, "vault", None)
    lump = _save_lump(c, vault, 56, 36) if vault else None
    table = bytes(mat.BEDROCK if i == mat.BEDROCK else mat.AIR for i in range(256))
    for y in range(BORDER, c.h - BORDER):
        c.g[y * c.w : (y + 1) * c.w] = c.g[y * c.w : (y + 1) * c.w].translate(table)
    keep, c.keep = c.keep, []  # islands are built below feet: nobody gets buried
    boxes: list[tuple[int, int, int, int]] = []
    if lump:
        boxes.append((vault[0] - 56, vault[1] - 36, vault[0] + 56, vault[1] + 36))

    def free(cx: int, top: int, rx: int, depth: int) -> bool:
        box = (cx - rx - 22, top - 44, cx + rx + 22, top + depth + 20)
        if box[0] < BORDER + 4 or box[2] > c.w - BORDER - 4 or box[1] < BORDER + 4:
            return False
        return not any(box[0] < o[2] and o[0] < box[2] and box[1] < o[3] and o[1] < box[3]
                       for o in boxes)  # fmt: skip

    def add(cx: int, top: int, rx: int, depth: int, flat: bool = False) -> None:
        boxes.append((cx - rx, top - 24, cx + rx, top + depth))
        _island(c, rng, cx, top, rx, depth, jelly, flat)

    state: dict[str, Any] = {"caches": []}
    sx, sy = (keep[0][0], keep[0][1] + 9) if keep else (c.w // 2, c.h // 5)  # spawn feet
    add(sx + rng.randint(-20, 20), sy, rng.randint(64, 80), rng.randint(30, 36), flat=True)
    far = 1 if sx < c.w // 2 else -1  # the side with more room: exit there, mid-boss opposite
    if abs(sx - c.w // 2) < c.w // 8:
        far = rng.choice((-1, 1))
    boss_slot = getattr(level, "arena", None) is not None
    for side, radius, role in ((-far, 95, "mid"), (far, 120 if boss_slot else 60, "exit")):
        for _ in range(60):
            cx = c.w // 2 + side * rng.randint(int(c.w * 0.2), int(c.w * 0.38))
            top = rng.randint(int(c.h * 0.42), line - 110)
            if not free(cx, top, radius, 48):
                continue
            if role == "exit" and not boss_slot:
                add(cx, top, radius, 34, flat=True)
                state["exit"] = (cx, top - 12)
            else:
                add(cx, top, radius, 48, flat=True)
                floor = _bowl(c, cx, top, radius)
                rect = (cx - radius + 16, floor - 60, cx + radius - 16, floor)
                if role == "mid":
                    state["mid_arena"] = rect
                else:  # the boss waits in the bowl, the anchor point is behind it
                    state["arena"] = (cx, floor - 30)
                    state["exit"] = (cx, floor - 12)
            break
    if "exit" in state and len(keep) > 1:
        keep[1] = (*state["exit"], keep[1][2])
    tiers = (0.2, 0.37, 0.54, 0.7)
    columns = list(enumerate(range(90, c.w - 90, 135)))
    rng.shuffle(columns)
    for column, x0 in columns:
        for tier in tiers:
            if rng.random() < 0.12:
                continue
            caves = len(state["caches"])  # at least two gum caves, at most four
            big = caves < 2 or (caves < 4 and rng.random() < 0.2)
            rx = rng.randint(86, 104) if big else rng.randint(44, 78)
            depth = rng.randint(50, 58) if big else rng.randint(22, 40)
            cx = x0 + rng.randint(-30, 30)
            top = int(c.h * tier) + (column % 2) * 58 + rng.randint(-26, 26)
            if top > line - 75 or not free(cx, top, rx, depth):
                continue
            add(cx, top, rx, depth)
            if big:
                state["caches"].append(_gum_cave(c, rng, cx, top, rx))
    for _ in range(40):  # Sirupkueste: domes rising out of the sea, the way back up
        rx, ry = rng.randint(80, 130), rng.randint(50, 70)
        cx, peak = rng.randint(BORDER + rx, c.w - BORDER - rx), line - int(ry * 0.55)
        if free(cx, peak, rx, ry):
            boxes.append((cx - rx, peak - 24, cx + rx, c.h))
            c.ellipse(cx, line + int(ry * 0.45), rx, ry, jelly)
    stones = 0
    for _ in range(400):  # sugar-glaze stepping stones in the gaps (hard: no bounce)
        x, y = rng.randint(40, c.w - 40), rng.randint(90, line - 60)
        length = rng.randint(18, 30)
        if stones < GLAZE_STONES and free(x, y, length // 2 + 30, 3):
            stones += 1
            boxes.append((x - length // 2, y - 24, x + length // 2, y + 3))
            c.rect(x - length // 2, y, x + length // 2, y + 3, glaze)
    for _ in range(60):  # raspberry jelly lumps
        x, y = rng.randint(BORDER, c.w - BORDER), rng.randint(BORDER, line)
        if c.get(x, y) == jelly:
            c.ellipse(x, y, rng.randint(6, 14), rng.randint(5, 10), red, only={jelly})
    if lump:
        _restore_lump(c, lump)
    sirup = _id("brausesirup")  # the sea is part of the terrain: arenas never end up in it
    sea = bytes(sirup if i == mat.AIR else i for i in range(256))
    for y in range(line, c.h - BORDER):
        c.g[y * c.w : (y + 1) * c.w] = c.g[y * c.w : (y + 1) * c.w].translate(sea)
    c.keep = keep
    for kx, ky, _r in keep[:2]:  # room for the body at spawn and anchor point
        c.rect(kx - 7, ky - 12, kx + 8, ky + 9, mat.AIR)
    return state


def _island(
    c: _Cells, rng: random.Random, cx: int, top: int, rx: int, depth: int, value: int,
    flat: bool = False,
) -> None:  # fmt: skip
    """A floating island: gently hilly top (flat on request), rounded belly."""
    p1, p2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    for x in range(cx - rx, cx + rx + 1):
        t = (x - cx) / rx
        edge = math.sqrt(max(0.0, 1 - t * t))
        hill = 0.0 if flat else 3.5 * math.sin(x * 0.06 + p1) + 1.5 * math.sin(x * 0.17 + p2)
        y0 = top + round(hill * edge + (1 - edge) * 8)
        y1 = top + round(depth * edge**0.7) + 2
        for y in range(y0, y1):
            c.put(x, y, value)


def _bowl(c: _Cells, cx: int, top: int, radius: int) -> int:
    """Carve the "Gelee-Schuessel" into a flat island: a wide floor between jelly rims.
    Returns the floor row."""
    floor = top + 22
    half = radius - 16
    jelly = _id("glibber")
    for side in (-1, 1):  # raised rims: the bowl's bouncing walls
        c.ellipse(cx + side * (half + 7), top - 2, 9, 14, jelly)
    for y in range(top - 12, floor):
        inset = max(0, 6 - (floor - y)) * 2  # rounded corners at the floor
        c.rect(cx - half + inset, y, cx + half - inset, y + 1, mat.AIR)
    return floor


def _gum_cave(c: _Cells, rng: random.Random, cx: int, top: int, rx: int) -> tuple[int, int]:
    """Kaugummi-Hoehle inside a big island: a shaft from the top, chewing gum on the floor
    and a sugar pedestal in the middle. Returns where the cache lies."""
    cy, half = top + 27, int(rx * 0.45)
    c.ellipse(cx, cy, half, 13, mat.AIR)
    shaft = cx + rng.choice((-1, 1)) * int(half * 0.6)
    c.rect(shaft - 7, top - 10, shaft + 7, cy, mat.AIR)
    c.rect(cx - half, cy + 9, cx + half, cy + 14, _id("kaugummi"), only={mat.AIR})
    c.rect(cx - 6, cy + 8, cx + 7, cy + 14, _id("zuckerguss"))
    return (cx, cy + 7)


def _save_lump(c: _Cells, centre: tuple[int, int], rx: int, ry: int) -> list[tuple[int, int, int]]:
    """Remember the cells of an ellipse (the treasure vault) across the wipe."""
    cx, cy = centre
    cells = []
    for y in range(cy - ry, cy + ry + 1):
        half = int(rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2)))
        for x in range(cx - half, cx + half + 1):
            if c.inside(x, y):
                cells.append((x, y, c.g[y * c.w + x]))
    return cells


def _restore_lump(c: _Cells, cells: list[tuple[int, int, int]]) -> None:
    for x, y, value in cells:
        c.g[y * c.w + x] = value


def _shape_kruemelreich(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """Above: a kitchen floor of tiles with giant crumbs, sugar and a pea, furnished with
    a cookie table and chairs, a tiled wall cabinet and the fridge's dark underside to
    climb on. Below the tiles: the ant colony in the caves."""
    tile, crumb, sugar = _id("fliese"), _id("kruemel"), _id("zucker")
    fluff, brosel, pea = _id("staubfluse"), _id("brosel"), _id("rock")
    air = {mat.AIR}
    floor = int(c.h * 0.42)
    c.rect(BORDER, BORDER, c.w - BORDER, floor, mat.AIR)  # the open kitchen
    x = BORDER
    while x < c.w - BORDER:  # tiles with holes where crumbs fell through
        span = rng.randint(140, 220)
        c.rect(x, floor, min(x + span, c.w - BORDER), floor + 6, tile)
        x += span + rng.randint(22, 30)
    fridge_x = int(c.w * 0.62)
    fy = int(c.h * 0.14)
    c.rect(fridge_x, fy, c.w - BORDER, fy + 12, tile)  # the fridge's underside ...
    c.rect(fridge_x, fy + 12, fridge_x + 10, floor - 46, tile)  # ... its kick plate
    for _ in range(9):  # dust bunnies under the fridge
        fx = rng.randint(fridge_x + 20, c.w - 20)
        rx, ry = rng.randint(7, 13), rng.randint(4, 7)
        c.ellipse(fx, floor - ry, rx, ry, fluff, only=air)
    # wall cabinet on the left: tiled shelves from the floor up to the ceiling
    shelf_w = rng.randint(110, 140)
    c.rect(BORDER, BORDER, BORDER + 8, floor, tile, only=air)
    for y in range(floor - 44, BORDER + 20, -44):
        c.rect(BORDER, y, BORDER + shelf_w, y + 4, tile, only=air)
        c.rect(BORDER + 18, y - 10, BORDER + 26, y, sugar, only=air)  # a sugar box
    # the table: a cookie top on two legs, crumbs and a plate on it, chairs beside
    tx = rng.randint(int(c.w * 0.24), int(c.w * 0.44))
    top = floor - 112
    half = rng.randint(100, 130)
    c.rect(tx - half, top, tx + half, top + 8, crumb, only=air)
    for leg in (tx - half + 10, tx + half - 18):
        c.rect(leg, top + 8, leg + 8, floor, crumb, only=air)
    c.rect(tx - 30, top - 3, tx + 30, top, tile, only=air)  # the plate
    for side in (-1, 1):
        sx = tx + side * (half + 34)
        seat = floor - 54
        c.rect(sx - 24, seat, sx + 24, seat + 6, crumb, only=air)
        for leg in (sx - 22, sx + 18):
            c.rect(leg, seat + 6, leg + 4, floor, crumb, only=air)
        back = sx + side * 22
        c.rect(min(back, back + side * 5), seat - 62, max(back, back + side * 5), seat, crumb,
               only=air)  # fmt: skip
    for _ in range(12):  # giant crumbs on the open floor, some piled up
        cx = rng.randint(30, c.w - 30)
        rx, ry = rng.randint(14, 36), rng.randint(10, 24)
        c.ellipse(cx, floor - ry + 3, rx, ry, crumb, only=air)
        if rng.random() < 0.4:
            c.ellipse(cx + rng.randint(-10, 10), floor - 2 * ry, rx * 2 // 3, ry * 2 // 3, crumb,
                      only=air)  # fmt: skip
    for band in (70, 130, 190, 240):  # crumb ledges: a way up in every height band
        for _ in range(2):
            lx = rng.randint(c.w // 6, c.w - 140)
            ly = floor - band + rng.randint(-10, 10)
            if ly > fy + 24:
                c.rect(lx, ly, lx + rng.randint(40, 80), ly + 6, crumb, only=air)
    for _ in range(24):  # sugar grains
        sx, size = rng.randint(30, c.w - 30), rng.randint(4, 9)
        c.rect(sx, floor - size, sx + size, floor, sugar, only=air)
    px = rng.randint(fridge_x - 140, fridge_x - 40)  # the pea rolled towards the fridge
    c.ellipse(px, floor - 24, 24, 24, pea, only=air)
    for i in range(6):  # colony chambers, the last one is the queen's
        r = 46 if i == 5 else rng.randint(20, 32)
        cx = rng.randint(80, c.w - 80) if i < 5 else c.w // 2 + rng.randint(-200, 200)
        cy = rng.randint(floor + 60, c.h - 60)
        c.ellipse(cx, cy, r, int(r * 0.7), mat.AIR)
        c.rect(cx - r, cy + int(r * 0.7) - 4, cx + r, cy + int(r * 0.7) + 1, brosel, only=air)
    return {"floor": floor}


def _shape_sporenklub(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """The dance floor: a big cavern with a flat cap floor, galleries along its walls,
    glowing mushrooms hanging from the roof as stepping stones, a DJ booth in the
    middle, speaker towers at its ends and cups that ``flood`` fills with neon juice."""
    cap, stem, glow = _id("pilzhut"), _id("pilzfleisch"), _id("leuchtsporen")
    air = {mat.AIR}
    cx, cy = c.w // 2, c.h // 2
    rx, ry = int(c.w * 0.30), int(c.h * 0.13)
    c.ellipse(cx, cy, rx, ry, mat.AIR)
    floor = cy + ry // 2

    def half_width(y: int) -> int:
        dy = (y - cy) / ry
        return int(rx * math.sqrt(max(0.0, 1 - dy * dy)))

    for y in range(floor, cy + ry + 1):  # flat floor of caps inside the cavern
        half = half_width(y)
        for x in range(cx - half, cx + half + 1):
            c.put(x, y, cap)
    for side in (-1, 1):  # galleries along the walls, a glowing pile at each lip
        for lift in (44, 88):
            y = floor - lift
            edge = cx + side * (half_width(y) + 6)
            lip = edge - side * rng.randint(56, 84)
            c.rect(min(edge, lip), y, max(edge, lip), y + 4, cap)
            c.rect(lip - 3, y - 3, lip + 4, y, glow, only=air)
    for i, x in enumerate(range(cx - rx // 2, cx + rx // 2 + 1, rx // 4)):  # hanging caps
        y = floor - (58 if i % 2 else 100)
        roof = y
        while roof > BORDER and not c.solid(x, roof - 1):
            roof -= 1
        c.rect(x - 2, roof, x + 3, y, stem)
        width = rng.randint(18, 26)
        c.ellipse(x, y, width, 4, cap)
        c.rect(x - width // 2, y - 6, x - width // 2 + 5, y - 3, glow, only=air)
    for side in (-1, 1):  # speaker towers
        tx = cx + side * int(rx * 0.78)
        c.rect(tx - 8, floor - 70, tx + 8, floor, cap)
        c.rect(tx - 12, floor - 74, tx + 12, floor - 70, cap)
    c.rect(cx - 30, floor - 14, cx + 30, floor, cap)  # the DJ booth
    for gx in (cx - 22, cx + 16):
        c.rect(gx, floor - 18, gx + 6, floor - 14, glow, only=air)
    cups = []
    for x in range(cx - int(rx * 0.6), cx + int(rx * 0.6), 56):
        if abs(x - cx) < 44:
            continue  # the booth stands here
        c.rect(x - 6, floor - 6, x - 4, floor, cap)
        c.rect(x + 4, floor - 6, x + 6, floor, cap)
        cups.append((x, floor - 1))
        sx = x + 28  # a small mushroom stool between two cups
        if abs(sx - cx) >= 44 and rng.random() < 0.6:
            height = rng.randint(16, 30)
            c.rect(sx - 2, floor - height, sx + 2, floor, stem, only=air)
            c.ellipse(sx, floor - height, 10, 3, cap, only=air)
    return {"cups": cups}


def _shape_abtei(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """Dry bell tower on top with the great bell and candles, stained glass in the nave,
    air chapels that the flood leaves dry, algae in the crypt."""
    bronze, wax = _id("glockenbronze"), _id("kerzenwachs")
    glass, algae = _id("buntglas"), _id("algen")
    bx, by = c.w // 2, int(c.h * 0.13)
    c.ellipse(bx, by, 70, 46, mat.AIR)
    for k in range(28):  # the bell, hanging from the chamber's roof
        half = 6 + k * 2 // 3
        c.rect(bx - half, by - 34 + k, bx + half + 1, by - 33 + k, bronze)
    c.rect(bx - 2, by - 6, bx + 3, by + 2, bronze)  # clapper
    for x, y in c.floors(0, 0, c.w, c.h // 3, step=37):
        if rng.random() < 0.5:
            c.rect(x, y - 6, x + 3, y + 1, wax, only={mat.AIR})
    walls = 0
    for x, y in c.ceilings(0, c.h // 3, c.w, c.h * 2 // 3, step=41):
        if walls < 14 and rng.random() < 0.5:
            c.rect(x - 4, y - 14, x + 4, y - 1, glass, only={_id("mauerwerk")})
            walls += 1
    chapels = []
    for _ in range(5):
        cx, cy = rng.randint(80, c.w - 80), rng.randint(int(c.h * 0.45), int(c.h * 0.8))
        rx, ry = rng.randint(24, 34), rng.randint(18, 26)
        c.ellipse(cx, cy, rx, ry, mat.AIR)
        chapels.append((cx, cy, rx, ry))
    for x, y in c.floors(0, c.h * 2 // 3, c.w, c.h, step=5):
        if rng.random() < 0.35:
            c.rect(x, y - rng.randint(2, 5), x + 2, y + 1, algae, only={mat.AIR})
    return {"chapels": chapels}


_SHAPERS = {
    "fleischwelt": _shape_fleischwelt,
    "aktenhalde": _shape_aktenhalde,
    "glibbria": _shape_glibbria,
    "kruemelreich": _shape_kruemelreich,
    "sporenklub": _shape_sporenklub,
    "abtei": _shape_abtei,
}


# --------------------------------------------------------------------------- flood


SEA_LEVEL = 0.86  # Glibbria: syrup sea below this share of the height
WATER_LINE = 0.36  # Abtei: water below this share of the height


def flood(world: Any, key: str, rng: random.Random, keep: Keep, state: dict[str, Any]) -> None:
    """Pour the signature liquids of ``key`` (after the paths were guaranteed)."""
    c = _Cells(world, keep)
    if key == "fleischwelt":
        _pools(c, rng, c.h // 3, c.h * 2 // 3, _id("acid"), 9, (5, 9))
        _pools(c, rng, c.h // 3, c.h * 2 // 3, _id("tallow"), 3, (3, 5))
    elif key == "aktenhalde":
        third = c.w // 3  # Archivkeller: ink lakes; Grossraumbuero: stamp pads to drink from
        _pools(c, rng, c.h // 3, c.h, _id("tinte"), 8, (6, 10), x0=2 * third)
        _pools(c, rng, BORDER, c.h, _id("stempelfarbe"), 3, (3, 4), x0=third, x1=2 * third)
    elif key == "glibbria":
        # the syrup sea is built in shape(); here only gum puddles on the islands
        _pools(c, rng, c.h // 6, int(c.h * SEA_LEVEL) - 20, _id("kaugummi"), 4, (2, 3))
    elif key == "kruemelreich":
        _pools(c, rng, state.get("floor", c.h // 2), c.h, _id("honig"), 4, (4, 7))
    elif key == "sporenklub":
        juice = _id("neonsaft")
        for x, y in state.get("cups", []):
            c.rect(x - 3, y - 4, x + 4, y + 1, juice, only={mat.AIR})
        _pools(c, rng, c.h * 2 // 3, c.h, juice, 4, (3, 5))
    elif key == "abtei":
        chapels = state.get("chapels", [])

        def dry(x: int, y: int) -> bool:
            return any(
                ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 for cx, cy, rx, ry in chapels
            )

        _flood_below(c, int(c.h * WATER_LINE), mat.WATER, skip=dry)


def _pools(
    c: _Cells,
    rng: random.Random,
    y0: int,
    y1: int,
    liquid: int,
    count: int,
    depth: tuple[int, int],
    x0: int = 0,
    x1: int | None = None,
) -> None:
    floors = c.floors(x0, y0, c.w if x1 is None else x1, y1, step=5)
    rng.shuffle(floors)
    for x, y in floors[:count]:
        c.pool(x, y, rng.randint(*depth), liquid)


def _flood_below(c: _Cells, line: int, liquid: int, skip: Any = None) -> None:
    for y in range(max(line, BORDER), c.h - BORDER):
        row = y * c.w
        for x in range(BORDER, c.w - BORDER):
            if c.g[row + x] == mat.AIR and not c.kept(x, y) and not (skip and skip(x, y)):
                c.g[row + x] = liquid


# ------------------------------------------------------------------ paper skin


def paper_skin(world: Any, paper: int, core: int, depth: int = SKIN) -> int:
    """Aktenhalde: paper deeper than ``depth`` cells behind any open cell becomes the
    non-burning ``core`` (ink-soaked stacks). A fire then eats the paper lining of the
    caves instead of the whole universe. Returns how many cells changed.

    Works row-wise on big integers with one byte per cell (fast without numpy)."""
    w, h, g = world.width, world.height, world.grid
    solid = (mat.SOLID, mat.POWDER)
    kinds = list(mat.KIND)
    open_table = bytes(1 if i < len(kinds) and kinds[i] not in solid else 0 for i in range(256))
    paper_table = bytes(1 if i == paper else 0 for i in range(256))
    full = int.from_bytes(b"\x01" * w, "little")
    near = []
    for y in range(h):
        m = int.from_bytes(g[y * w : (y + 1) * w].translate(open_table), "little")
        for _ in range(depth):
            m |= (m << 8) | (m >> 8)
        near.append(m & full)
    for _ in range(depth):
        near = [near[y] | (near[y - 1] if y else 0) | (near[y + 1] if y + 1 < h else 0)
                for y in range(h)]  # fmt: skip
    changed = 0
    for y in range(h):
        row = g[y * w : (y + 1) * w]
        deep = int.from_bytes(row.translate(paper_table), "little") & (full ^ near[y])
        if deep:
            value = int.from_bytes(row, "little") - deep * paper + deep * core
            g[y * w : (y + 1) * w] = value.to_bytes(w, "little")
            changed += bin(deep).count("1")
    return changed

