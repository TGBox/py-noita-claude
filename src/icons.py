"""Procedural 16x16 pixel icons for every building block (no pygame needed).

Each icon is a frame in the colour of the block's category with a glyph that shows
what the block does (a bomb, a drill, a ring of shots, an eye for homing, ...),
tinted by the material it carries. ``icon_pixels`` returns rows of RGB tuples or
``None`` for transparent pixels; the renderer turns them into cached surfaces.
"""

from __future__ import annotations

import math
import re
from functools import cache
from itertools import pairwise

from src.materials import FLAME, GAS, LIBRARY, LIQUID, POWDER
from src.spells import CATALOG, Block, Category, Trigger

SIZE = 16
Color = tuple[int, int, int]
Grid = list[list[Color | None]]

FRAME_COLORS: dict[Category, Color] = {
    Category.FORM: (196, 180, 150),
    Category.MODIFIER: (142, 88, 170),
    Category.TRIGGER: (214, 172, 64),
    Category.PAYLOAD: (186, 44, 52),
}
BACKGROUND: Color = (26, 13, 17)
GLYPH_COLORS: dict[Category, Color] = {
    Category.FORM: (238, 226, 200),
    Category.MODIFIER: (196, 150, 228),
    Category.TRIGGER: (246, 214, 110),
    Category.PAYLOAD: (220, 60, 60),
}
_TIER = re.compile(r"_(\d)$")


def _mix(a: Color, b: Color, t: float) -> Color:
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


class _Canvas:
    def __init__(self, main: Color) -> None:
        self.grid: Grid = [[None] * SIZE for _ in range(SIZE)]
        self.main = main
        self.light = _mix(main, (255, 255, 255), 0.5)
        self.dark = _mix(main, (0, 0, 0), 0.45)

    def dot(self, x: float, y: float, color: Color | None = None) -> None:
        ix, iy = round(x), round(y)
        if 2 <= ix < SIZE - 2 and 2 <= iy < SIZE - 2:
            self.grid[iy][ix] = color or self.main

    def line(self, x0: float, y0: float, x1: float, y1: float, color: Color | None = None) -> None:
        steps = max(1, round(max(abs(x1 - x0), abs(y1 - y0))))
        for k in range(steps + 1):
            t = k / steps
            self.dot(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, color)

    def disc(self, cx: float, cy: float, r: float, color: Color | None = None) -> None:
        for y in range(SIZE):
            for x in range(SIZE):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                    self.dot(x, y, color)

    def ring(self, cx: float, cy: float, r: float, color: Color | None = None) -> None:
        for k in range(32):
            a = k / 32 * math.tau
            self.dot(cx + math.cos(a) * r, cy + math.sin(a) * r, color)

    def shaded_disc(self, cx: float, cy: float, r: float) -> None:
        self.disc(cx, cy, r, self.dark)
        self.disc(cx - 0.4, cy - 0.4, r - 0.8)
        self.dot(cx - r / 2, cy - r / 2, self.light)


# ------------------------------------------------------------------- glyphs


def _orb(c: _Canvas) -> None:
    c.dot(3, 12, c.dark)
    c.dot(4, 11, c.dark)
    c.dot(5, 10)
    c.shaded_disc(8.5, 7.5, 3)


def _needle(c: _Canvas) -> None:
    c.line(3, 12, 11, 4, c.dark)
    c.line(4, 12, 12, 4)
    c.dot(12, 3, c.light)
    c.dot(13, 3, c.light)


def _spear(c: _Canvas) -> None:
    c.line(2, 8, 11, 8)
    c.line(2, 9, 10, 9, c.dark)
    c.line(10, 5, 13, 8, c.light)
    c.line(10, 11, 13, 8, c.light)


def _bomb(c: _Canvas) -> None:
    c.shaded_disc(7, 9, 4)
    c.line(9, 5, 11, 3, c.dark)
    c.dot(12, 2, (255, 230, 150))
    c.dot(12, 3, (255, 160, 60))


def _burst(c: _Canvas, size: float = 5) -> None:
    for k in range(8):
        a = k / 8 * math.tau
        long = size if k % 2 == 0 else size * 0.6
        c.line(7.5, 7.5, 7.5 + math.cos(a) * long, 7.5 + math.sin(a) * long)
    c.disc(7.5, 7.5, 1.5, c.light)


def _pellets(c: _Canvas, count: int) -> None:
    rng = [(4, 5), (9, 4), (12, 8), (6, 9), (10, 11), (4, 12), (8, 7), (12, 12), (3, 8),
           (11, 5), (7, 12), (6, 3)]  # fmt: skip
    for x, y in rng[: max(3, min(count, len(rng)))]:
        c.dot(x, y)
        c.dot(x + 1, y, c.dark)
        c.dot(x, y - 1, c.light)


def _drill(c: _Canvas) -> None:
    for y in range(4, 12):
        width = 10 - abs(y - 7.5) * 2.2
        c.line(3, y, 3 + width, y, c.main if y % 2 else c.dark)
    c.dot(13, 7, c.light)
    c.dot(13, 8, c.light)


def _swirl(c: _Canvas) -> None:
    c.ring(7.5, 7.5, 5, c.dark)
    c.ring(7.5, 7.5, 3)
    c.disc(7.5, 7.5, 1, c.light)


def _chain(c: _Canvas) -> None:
    points = [(3, 3), (8, 7), (5, 9), (12, 13)]
    for (x0, y0), (x1, y1) in pairwise(points):
        c.line(x0, y0, x1, y1)
        c.line(x0 + 1, y0, x1 + 1, y1, c.light)


def _mine(c: _Canvas) -> None:
    c.shaded_disc(7.5, 8, 3)
    for dx, dy in ((0, -5), (0, 5), (-5, 0), (5, 0), (3.5, 3.5), (-3.5, -3.5), (3.5, -3.5), (-3.5, 3.5)):
        c.dot(7.5 + dx, 8 + dy, c.light)


def _light(c: _Canvas) -> None:
    c.disc(7.5, 7.5, 2.5, c.light)
    for k in range(8):
        a = k / 8 * math.tau
        c.line(7.5 + math.cos(a) * 4, 7.5 + math.sin(a) * 4, 7.5 + math.cos(a) * 5.5, 7.5 + math.sin(a) * 5.5)


def _lob(c: _Canvas) -> None:
    for k in range(9):
        t = k / 8
        c.dot(2 + t * 9, 12 - math.sin(t * math.pi) * 8, c.dark if k % 2 else c.main)
    c.shaded_disc(11.5, 10.5, 2)


def _saw(c: _Canvas) -> None:
    c.ring(7.5, 7.5, 3.5)
    c.disc(7.5, 7.5, 1, c.dark)
    for k in range(6):
        a = k / 6 * math.tau
        c.dot(7.5 + math.cos(a) * 5, 7.5 + math.sin(a) * 5, c.light)


def _bubble(c: _Canvas) -> None:
    c.ring(7.5, 8, 4)
    c.dot(6, 6, c.light)
    c.dot(6, 7, c.light)
    c.dot(11, 3, c.dark)


def _fang(c: _Canvas) -> None:
    c.line(4, 3, 7, 12)
    c.line(5, 3, 8, 12, c.light)
    c.line(11, 3, 9, 12, c.dark)
    c.line(4, 3, 11, 3)


def _question(c: _Canvas) -> None:
    for x, y in ((5, 4), (6, 3), (7, 3), (8, 3), (9, 4), (9, 5), (8, 6), (7, 7), (7, 8), (7, 11)):
        c.dot(x, y)
        c.dot(x + 1, y, c.dark)


def _swap(c: _Canvas) -> None:
    c.line(3, 5, 12, 5)
    c.line(10, 3, 12, 5)
    c.line(3, 10, 12, 10, c.light)
    c.line(3, 10, 5, 12, c.light)


def _wave(c: _Canvas) -> None:
    for k in range(12):
        x = 2 + k
        c.dot(x, 8 + math.sin(k / 11 * math.tau) * 3)
        c.dot(x, 9 + math.sin(k / 11 * math.tau) * 3, c.dark)


def _blade(c: _Canvas) -> None:
    for k in range(10):
        a = -1.2 + k / 9 * 2.4
        c.dot(6 + math.cos(a) * 6, 8 + math.sin(a) * 6, c.light)
        c.dot(6 + math.cos(a) * 5, 8 + math.sin(a) * 5)


def _arrows(c: _Canvas, count: int) -> None:
    count = max(2, min(count, 5))
    for k in range(count):
        y = 3 + k * (10 / max(1, count - 1)) if count > 1 else 8
        c.line(3, y, 11, y)
        c.dot(12, y, c.light)
        c.dot(10, y - 1, c.dark)
        c.dot(10, y + 1, c.dark)


def _ring_of(c: _Canvas, count: int) -> None:
    count = max(3, min(count, 12))
    for k in range(count):
        a = k / count * math.tau
        c.dot(7.5 + math.cos(a) * 5, 7.5 + math.sin(a) * 5, c.light if k == 0 else c.main)
    c.disc(7.5, 7.5, 1, c.dark)


def _fan(c: _Canvas, count: int) -> None:
    count = max(2, min(count, 7))
    for k in range(count):
        a = -0.8 + 1.6 * k / max(1, count - 1)
        c.line(3, 8, 3 + math.cos(a) * 10, 8 + math.sin(a) * 10)
    c.dot(3, 8, c.light)


def _eye(c: _Canvas) -> None:
    for x in range(3, 13):
        h = math.sqrt(max(0.0, 1 - ((x - 7.5) / 5) ** 2)) * 3
        c.dot(x, 8 - h, c.main)
        c.dot(x, 8 + h, c.main)
    c.disc(7.5, 8, 1.6, c.dark)
    c.dot(7, 7, c.light)


def _arrow_up(c: _Canvas) -> None:
    c.line(7.5, 13, 7.5, 3)
    c.line(4, 6, 7.5, 3, c.light)
    c.line(11, 6, 7.5, 3, c.light)


def _arrow_down(c: _Canvas) -> None:
    c.line(7.5, 3, 7.5, 11)
    c.line(4, 8, 7.5, 12, c.light)
    c.line(11, 8, 7.5, 12, c.light)
    c.line(5, 13, 10, 13, c.dark)


def _chevrons(c: _Canvas, double: bool) -> None:
    starts = (3, 8) if double else (5,)
    for x in starts:
        c.line(x, 3, x + 4, 7.5)
        c.line(x, 12, x + 4, 7.5, c.light)
    if not double:
        c.line(11, 4, 11, 11, c.dark)


def _plus(c: _Canvas) -> None:
    c.line(7.5, 3, 7.5, 12)
    c.line(3, 7.5, 12, 7.5)
    c.line(8.5, 3, 8.5, 12, c.dark)


def _hourglass(c: _Canvas) -> None:
    c.line(4, 3, 11, 3, c.light)
    c.line(4, 12, 11, 12, c.light)
    c.line(4, 3, 11, 12)
    c.line(11, 3, 4, 12)
    c.dot(7.5, 10, c.dark)
    c.dot(7.5, 11, c.dark)


def _bounce(c: _Canvas) -> None:
    points = [(2, 4), (5, 12), (8, 5), (11, 12), (13, 8)]
    for (x0, y0), (x1, y1) in pairwise(points):
        c.line(x0, y0, x1, y1)
    c.line(2, 13, 13, 13, c.dark)


def _scatter(c: _Canvas) -> None:
    for x, y in ((3, 8), (6, 5), (6, 11), (9, 3), (9, 8), (9, 13), (12, 6), (12, 10)):
        c.dot(x, y, c.light if x == 3 else c.main)


def _bolt(c: _Canvas) -> None:
    points = [(10, 2), (5, 8), (9, 8), (5, 13)]
    for (x0, y0), (x1, y1) in pairwise(points):
        c.line(x0, y0, x1, y1)
    c.dot(10, 2, c.light)


def _cycle(c: _Canvas) -> None:
    for k in range(22):
        a = k / 28 * math.tau
        c.dot(7.5 + math.cos(a) * 4.5, 7.5 + math.sin(a) * 4.5)
    c.line(12, 7, 12, 9, c.light)
    c.line(10, 8, 12, 9, c.light)


def _drop(c: _Canvas) -> None:
    for y in range(3, 13):
        r = (y - 3) * 0.75 if y <= 8 else math.sqrt(max(0.0, 3.8**2 - (y - 8.6) ** 2))
        c.line(7.5 - r, y, 7.5 + r, y, c.main if y < 11 else c.dark)
    c.dot(6, 8, c.light)
    c.dot(6, 9, c.light)


def _cloud(c: _Canvas) -> None:
    for cx, cy, r in ((5, 9, 2.5), (9, 7, 3), (11, 10, 2)):
        c.disc(cx, cy, r)
    c.dot(8, 5, c.light)
    c.line(4, 12, 12, 12, c.dark)


def _flame(c: _Canvas) -> None:
    for y in range(3, 13):
        r = (y - 3) / 10 * 4
        sway = math.sin(y * 0.9) * 0.8
        c.line(7.5 - r + sway, y, 7.5 + r + sway, y, c.main if y < 10 else c.dark)
    c.line(7.5, 8, 7.5, 11, c.light)


def _pile(c: _Canvas) -> None:
    for row in range(5):
        y = 12 - row * 2
        for x in range(4 + row, 12 - row, 2):
            c.dot(x, y)
            c.dot(x + 1, y + 1, c.dark)
    c.dot(7, 4, c.light)


def _chunk(c: _Canvas) -> None:
    for y in range(5, 12):
        c.line(4, y, 11, y)
    c.line(4, 5, 11, 5, c.light)
    c.line(11, 5, 11, 11, c.dark)
    c.line(4, 11, 11, 11, c.dark)


def _core(c: _Canvas) -> None:
    c.ring(7.5, 7.5, 5, c.dark)
    c.shaded_disc(7.5, 7.5, 2.5)


def _trail(c: _Canvas) -> None:
    for x in (2, 4, 6):
        c.dot(x, 11 - x // 2, c.dark)
    c.shaded_disc(10, 6, 2.5)


def _pierce(c: _Canvas) -> None:
    c.line(9, 3, 9, 12, c.dark)
    c.line(2, 8, 12, 8)
    c.line(10, 6, 13, 8, c.light)
    c.line(10, 10, 13, 8, c.light)


def _nerve(c: _Canvas, trigger: Trigger | None) -> None:
    c.line(7.5, 13, 7.5, 7, c.dark)
    c.line(7.5, 8, 4, 5)
    c.line(7.5, 8, 11, 5)
    c.line(4, 5, 3, 3, c.dark)
    c.line(11, 5, 12, 3, c.dark)
    marker = c.light
    if trigger is Trigger.TIMER:
        c.ring(7.5, 4.5, 2, marker)
        c.dot(7.5, 4, marker)
    elif trigger is Trigger.END:
        c.line(6, 3, 9, 6, marker)
        c.line(9, 3, 6, 6, marker)
    elif trigger is Trigger.WET:
        c.dot(7.5, 3, marker)
        c.line(6.5, 4, 8.5, 4, marker)
        c.line(6.5, 5, 8.5, 5, marker)
    else:  # impact
        for dx, dy in ((0, -1.5), (0, 1.5), (-1.5, 0), (1.5, 0)):
            c.dot(7.5 + dx, 4.5 + dy, marker)
        c.dot(7.5, 4.5, marker)


# ------------------------------------------------------------------ choice


def _main_color(block: Block) -> Color:
    material = block.material if block.material is not None else block.trail
    if material is None:
        material = block.default_material
    if material is None:
        return GLYPH_COLORS[block.category]
    color = LIBRARY[material].color
    if sum(color) < 240:  # dark materials (smoke, blood) would vanish on the dark ground
        color = _mix(color, (255, 255, 255), 0.35)
    return color


def _draw_form(c: _Canvas, b: Block) -> None:
    if b.teleport:
        _swirl(c)
    elif b.polymorph:
        _question(c)
    elif b.swap:
        _swap(c)
    elif b.chain:
        _chain(c)
    elif b.mine:
        _mine(c)
    elif b.digs:
        _drill(c)
    elif b.light:
        _light(c)
    elif b.pellets > 1:
        _pellets(c, b.pellets)
    elif b.lifesteal:
        _fang(c)
    elif b.ricochet:
        _saw(c)
    elif b.bounces:
        _bomb(c)
    elif b.blast >= 9:
        _burst(c)
    elif b.gravity < 0:
        _bubble(c)
    elif b.pierce and b.lifetime <= 0.2:
        _blade(c)
    elif b.pierce:
        _spear(c)
    elif b.homing:
        _eye(c)
    elif b.speed <= 150:
        _wave(c)
    elif b.gravity >= 250:
        _lob(c)
    elif b.speed >= 650:
        _needle(c)
    else:
        _orb(c)


def _draw_modifier(c: _Canvas, b: Block) -> None:
    if b.multicast and b.formation >= 1.0:
        _ring_of(c, b.multicast)
    elif b.multicast and b.formation > 0.1:
        _fan(c, b.multicast)
    elif b.multicast:
        _arrows(c, b.multicast)
    elif b.material is not None:
        _core(c)
    elif b.trail is not None:
        _trail(c)
    elif b.homing:
        _eye(c)
    elif b.flip_gravity:
        _arrow_up(c)
    elif b.ignites:
        _flame(c)
    elif b.pierce:
        _pierce(c)
    elif b.blast_bonus:
        _burst(c, 3.5 + min(2.5, b.blast_bonus / 4))
    elif b.speed_factor != 1.0:
        _chevrons(c, b.speed_factor > 1.0)
    elif b.damage_bonus:
        _plus(c)
    elif b.lifetime_factor != 1.0:
        _hourglass(c)
    elif b.gravity_factor > 1.0:
        _arrow_down(c)
    elif b.gravity_factor < 1.0:
        _bubble(c)
    elif b.bounce_bonus:
        _bounce(c)
    elif b.spread_bonus:
        _scatter(c)
    elif b.recharge_bonus < 0:
        _cycle(c)
    elif b.cast_delay < 0:
        _bolt(c)
    elif b.mana < 0:
        _drop(c)
        c.line(11, 3, 13, 3, c.light)
        c.line(12, 2, 12, 4, c.light)
    else:
        _plus(c)


def _draw_payload(c: _Canvas, b: Block) -> None:
    kind = LIBRARY[b.material].kind if b.material is not None else LIQUID
    if kind == LIQUID:
        _drop(c)
    elif kind == GAS:
        _cloud(c)
    elif kind == FLAME:
        _flame(c)
    elif kind == POWDER:
        _pile(c)
    else:
        _chunk(c)


@cache
def icon_pixels(key: str) -> tuple[tuple[Color | None, ...], ...]:
    """The 16x16 icon of the block ``key``: rows of RGB (or None = transparent)."""
    block = CATALOG[key]
    frame = FRAME_COLORS[block.category]
    c = _Canvas(_main_color(block))
    if block.category is Category.FORM:
        _draw_form(c, block)
    elif block.category is Category.MODIFIER:
        _draw_modifier(c, block)
    elif block.category is Category.TRIGGER:
        _nerve(c, block.trigger)
    else:
        _draw_payload(c, block)
    tier = _TIER.search(block.key)
    if tier and block.category is Category.MODIFIER and not block.multicast:
        for k in range(min(4, int(tier.group(1)))):
            c.grid[13][3 + k * 2] = c.light
    rows: Grid = []
    shadow = _mix(frame, (0, 0, 0), 0.45)
    for y in range(SIZE):
        row: list[Color | None] = []
        for x in range(SIZE):
            corner = (x in (0, SIZE - 1)) and (y in (0, SIZE - 1))
            if corner:
                row.append(None)
            elif x in (0, SIZE - 1) or y in (0, SIZE - 1):
                row.append(frame if x == 0 or y == 0 else shadow)
            else:
                row.append(c.grid[y][x] or BACKGROUND)
        rows.append(row)
    return tuple(tuple(row) for row in rows)


def glyph_signature(key: str) -> tuple:
    """Shape of an icon without colours (to check that glyphs differ)."""
    return tuple(tuple(p is not None and p != BACKGROUND for p in row) for row in icon_pixels(key))
