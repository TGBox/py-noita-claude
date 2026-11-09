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
        if self.inside(x, y) and not self.kept(x, y):
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
    """Build the solid signature features of ``key``; returns state for ``flood``."""
    builder = _SHAPERS.get(key)
    return builder(_Cells(world, keep), rng) if builder else {}


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
    """Above: a kitchen floor of tiles with giant crumbs, sugar and a pea; the fridge's
    dark underside on the right. Below the tiles: the ant colony in the caves."""
    tile, crumb, sugar = _id("fliese"), _id("kruemel"), _id("zucker")
    fluff, brosel, pea = _id("staubfluse"), _id("brosel"), _id("rock")
    floor = int(c.h * 0.42)
    c.rect(BORDER, BORDER, c.w - BORDER, floor, mat.AIR)  # the open kitchen
    x = BORDER
    while x < c.w - BORDER:  # tiles with holes where crumbs fell through
        span = rng.randint(140, 220)
        c.rect(x, floor, min(x + span, c.w - BORDER), floor + 6, tile)
        x += span + rng.randint(22, 30)
    fridge_x = int(c.w * 0.58)
    c.rect(fridge_x, int(c.h * 0.14), c.w - BORDER, int(c.h * 0.14) + 10, tile)
    for _ in range(9):  # dust bunnies under the fridge
        fx = rng.randint(fridge_x + 10, c.w - 20)
        rx, ry = rng.randint(7, 13), rng.randint(4, 7)
        c.ellipse(fx, floor - ry, rx, ry, fluff, only={mat.AIR})
    for _ in range(14):  # giant crumbs on the open floor, some piled up
        cx = rng.randint(30, c.w - 30)
        rx, ry = rng.randint(14, 40), rng.randint(10, 28)
        c.ellipse(cx, floor - ry + 3, rx, ry, crumb, only={mat.AIR})
        if rng.random() < 0.4:
            c.ellipse(cx + rng.randint(-10, 10), floor - 2 * ry, rx * 2 // 3, ry * 2 // 3, crumb,
                      only={mat.AIR})  # fmt: skip
    for _ in range(3):  # crumb-and-sugar ledges to climb towards the fridge
        lx, ly = rng.randint(40, c.w - 120), rng.randint(int(c.h * 0.16), floor - 60)
        c.rect(lx, ly, lx + rng.randint(50, 90), ly + 6, crumb, only={mat.AIR})
    for _ in range(24):  # sugar grains
        sx, size = rng.randint(30, c.w - 30), rng.randint(4, 9)
        c.rect(sx, floor - size, sx + size, floor, sugar, only={mat.AIR})
    px = rng.randint(c.w // 6, fridge_x - 60)  # the pea
    c.ellipse(px, floor - 24, 24, 24, pea, only={mat.AIR})
    for i in range(6):  # colony chambers, the last one is the queen's
        r = 46 if i == 5 else rng.randint(20, 32)
        cx = rng.randint(80, c.w - 80) if i < 5 else c.w // 2 + rng.randint(-200, 200)
        cy = rng.randint(floor + 60, c.h - 60)
        c.ellipse(cx, cy, r, int(r * 0.7), mat.AIR)
        c.rect(cx - r, cy + int(r * 0.7) - 4, cx + r, cy + int(r * 0.7) + 1, brosel, only={mat.AIR})
    return {"floor": floor}


def _shape_sporenklub(c: _Cells, rng: random.Random) -> dict[str, Any]:
    """The dance floor: one huge cavern with a flat cap floor, speaker towers at its ends
    and cups along the floor that ``flood`` fills with glowing neon juice."""
    cap = _id("pilzhut")
    cx, cy = c.w // 2, c.h // 2
    rx, ry = int(c.w * 0.32), int(c.h * 0.17)
    c.ellipse(cx, cy, rx, ry, mat.AIR)
    floor = cy + ry // 2
    for y in range(floor, cy + ry + 1):  # flat floor of caps inside the cavern
        dy = (y - cy) / ry
        half = int(rx * math.sqrt(max(0.0, 1 - dy * dy)))
        for x in range(cx - half, cx + half + 1):
            c.put(x, y, cap)
    for side in (-1, 1):  # speaker towers
        tx = cx + side * int(rx * 0.78)
        c.rect(tx - 8, floor - 70, tx + 8, floor, cap)
        c.rect(tx - 12, floor - 74, tx + 12, floor - 70, cap)
    cups = []
    for x in range(cx - int(rx * 0.6), cx + int(rx * 0.6), 56):
        c.rect(x - 6, floor - 6, x - 4, floor, cap)
        c.rect(x + 4, floor - 6, x + 6, floor, cap)
        cups.append((x, floor - 1))
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
