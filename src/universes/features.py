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


def shape(world: Any, key: str, rng: random.Random, keep: Keep) -> dict[str, Any]:
    """Build the solid signature features of ``key``; returns state for ``flood``.

    The first two ``keep`` circles are spawn and exit: after the big carving they get a
    ledge to stand on, so nobody starts or ends on a floating leftover of the caves."""
    builder = _SHAPERS.get(key)
    if builder is None:
        return {}
    cells = _Cells(world, keep)
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
    """Registratur (left third): shelf boards across the open caves, with gaps to pass."""
    board = _id("aktendeckel")
    for y in range(c.h // 8, c.h - 20, 34):
        x = BORDER
        while x < c.w // 3:
            length, gap = rng.randint(18, 28), rng.randint(12, 18)
            probes = (x, x + length // 2)
            if all(c.air(xx, y) and c.air(xx, y - 6) and c.air(xx, y + 6) for xx in probes):
                c.rect(x, y, x + length, y + 2, board, only={mat.AIR})
            x += length + gap
    return {}


def _shape_glibbria(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """Open sky between floating jelly islands, sugar-glaze platforms in the air."""
    glaze, red = _id("zuckerguss"), _id("glibber_rot")
    for _ in range(5):
        cx, cy = rng.randint(c.w // 8, c.w * 7 // 8), rng.randint(c.h // 6, c.h * 3 // 5)
        rx, ry = rng.randint(110, 190), rng.randint(55, 90)
        c.ellipse(cx, cy, rx, ry, mat.AIR)
        for _ in range(3):
            px = cx + rng.randint(-rx * 2 // 3, rx * 2 // 3)
            py = cy + rng.randint(-ry // 3, ry * 2 // 3)
            left, right = px - rng.randint(12, 22), px + rng.randint(12, 22)
            c.rect(left, py, right, py + 3, glaze, only={mat.AIR})
    for _ in range(14):  # raspberry jelly lumps on the islands
        x, y = rng.randint(BORDER, c.w - BORDER), rng.randint(BORDER, c.h * 4 // 5)
        if c.solid(x, y):
            c.ellipse(x, y, rng.randint(6, 14), rng.randint(5, 10), red, only={_id("glibber")})
    return {}


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
SHORE_GAP = 14  # open air above the sea (cells)
WATER_LINE = 0.36  # Abtei: water below this share of the height


def flood(world: Any, key: str, rng: random.Random, keep: Keep, state: dict[str, Any]) -> None:
    """Pour the signature liquids of ``key`` (after the paths were guaranteed)."""
    c = _Cells(world, keep)
    if key == "fleischwelt":
        _pools(c, rng, c.h // 3, c.h * 2 // 3, _id("acid"), 9, (5, 9))
        _pools(c, rng, c.h // 3, c.h * 2 // 3, _id("tallow"), 3, (3, 5))
    elif key == "aktenhalde":
        _pools(c, rng, c.h // 3, c.h, _id("tinte"), 8, (6, 10), x0=c.w * 2 // 3)
    elif key == "glibbria":
        _sea(c, int(c.h * SEA_LEVEL), _id("brausesirup"))
        _pools(c, rng, c.h // 4, int(c.h * SEA_LEVEL), _id("kaugummi"), 5, (3, 5))
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
) -> None:
    floors = c.floors(x0, y0, c.w, y1, step=5)
    rng.shuffle(floors)
    for x, y in floors[:count]:
        c.pool(x, y, rng.randint(*depth), liquid)


def _sea(c: _Cells, line: int, liquid: int) -> None:
    """Everything below ``line`` becomes ``liquid`` (a sea the islands float above), with a
    band of open air right above it so the shore line reads as a coast."""
    for y in range(max(line - SHORE_GAP, BORDER), c.h - BORDER):
        row = y * c.w
        value = liquid if y >= line else mat.AIR
        for x in range(BORDER, c.w - BORDER):
            if c.g[row + x] != mat.BEDROCK and not c.kept(x, y):
                if y >= line or mat.KIND[c.g[row + x]] != mat.LIQUID:
                    c.g[row + x] = value


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

