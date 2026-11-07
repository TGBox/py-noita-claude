"""Contract V9: Common topology and room/arena placement helpers (Card A25)."""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from src import materials as mat
from src.world import BORDER

if TYPE_CHECKING:
    from src.world import World

Rect = tuple[int, int, int, int]

TRADER_SIZE = (24, 16)
SHRINE_SIZE = (20, 14)
MID_ARENA_SIZE = (56, 36)
BOSS_ARENA_SIZE = (72, 44)


def region_bands(
    width: int,
    height: int,
    topology: str,
) -> list[Rect]:
    """Return 3 (x0, y0, x1, y1) bounding boxes for topology."""
    w, h = width, height
    if topology in ("vertical", "vertical_3"):  # three layers stacked top to bottom
        bands = [(0, 0, w, h // 3), (0, h // 3, w, 2 * h // 3), (0, 2 * h // 3, w, h)]
    elif topology in ("horizontal", "horizontal_3"):  # three strips from left to right
        bands = [(0, 0, w // 3, h), (w // 3, 0, 2 * w // 3, h), (2 * w // 3, 0, w, h)]
    elif topology == "concentric":  # nested boxes, outermost first
        bands = [
            (0, 0, w, h),
            (w // 6, h // 6, 5 * w // 6, 5 * h // 6),
            (w // 3, h // 3, 2 * w // 3, 2 * h // 3),
        ]
    elif topology == "columns":  # full-height columns separated by thin walls
        gap = max(1, w // 60)
        bands = [(0, 0, w // 3 - gap, h), (w // 3, 0, 2 * w // 3 - gap, h), (2 * w // 3, 0, w, h)]
    elif topology == "top_split":  # two halves on top, one wide band below
        bands = [(0, 0, w // 2, h // 2), (w // 2, 0, w, h // 2), (0, h // 2, w, h)]
    elif topology == "islands":  # three separate islands at different heights
        bands = [
            (0, h // 4, w // 3 - 1, 3 * h // 4),
            (w // 3, 0, 2 * w // 3 - 1, h // 2),
            (2 * w // 3, h // 2, w, h),
        ]
    else:
        return region_bands(width, height, "vertical")
    return [(x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)) for x0, y0, x1, y1 in bands]


def _clamp(world: World, x0: int, y0: int, x1: int, y1: int) -> Rect:
    """Keep a rectangle inside the world's bedrock frame, never empty."""
    lo_x, hi_x = BORDER + 1, max(BORDER + 2, world.width - BORDER - 1)
    lo_y, hi_y = BORDER + 1, max(BORDER + 2, world.height - BORDER - 1)
    x0, x1 = max(lo_x, min(x0, hi_x - 1)), max(lo_x + 1, min(x1, hi_x))
    y0, y1 = max(lo_y, min(y0, hi_y - 1)), max(lo_y + 1, min(y1, hi_y))
    return (x0, y0, max(x1, x0 + 1), max(y1, y0 + 1))


def carve_room(
    world: World,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    wall_mat: int | None = None,
) -> Rect:
    """Carve an air room and return its (x0, y0, x1, y1) rect."""
    x0, y0, x1, y1 = _clamp(world, x0, y0, x1, y1)
    if wall_mat is not None:  # a one-cell shell around the room
        world.fill_rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, wall_mat)
    world.fill_rect(x0, y0, x1, y1, mat.AIR)
    return (x0, y0, x1, y1)


def carve_tunnel(
    world: World,
    start: tuple[int, int],
    end: tuple[int, int],
    radius: int = 4,
) -> None:
    """Carve a continuous air corridor from start to end."""
    steps = max(1, int(math.hypot(end[0] - start[0], end[1] - start[1]) / max(1, radius // 2)))
    for k in range(steps + 1):
        t = k / steps
        x = round(start[0] + (end[0] - start[0]) * t)
        y = round(start[1] + (end[1] - start[1]) * t)
        world.fill_disc(x, y, radius, mat.AIR)


def fill_basin(
    world: World,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    liquid_mat: int,
) -> None:
    """Fill a lower basin area with liquid_mat (air cells in the lower half only)."""
    x0, y0, x1, y1 = _clamp(world, x0, y0, x1, y1)
    for y in range((y0 + y1) // 2, y1):
        for x in range(x0, x1):
            if world.get(x, y) == mat.AIR:
                world.set_cell(x, y, liquid_mat)


def _place_room(
    world: World,
    rect: Rect,
    size: tuple[int, int],
    rng: random.Random,
) -> Rect:
    """Carve a room of (at most) ``size`` at a random spot inside ``rect``."""
    x0, y0, x1, y1 = _clamp(world, *rect)
    width, height = min(size[0], x1 - x0), min(size[1], y1 - y0)
    left = rng.randint(x0, max(x0, x1 - width))
    top = rng.randint(y0, max(y0, y1 - height))
    return carve_room(world, left, top, left + width, top + height)


def place_trader_nook(
    world: World,
    rect: Rect,
    rng: random.Random,
) -> Rect:
    """Carve a sheltered trader nook inside rect and return its (x0, y0, x1, y1)."""
    return _place_room(world, rect, TRADER_SIZE, rng)


def place_challenge_shrine(
    world: World,
    rect: Rect,
    rng: random.Random,
) -> Rect:
    """Carve a challenge shrine chamber inside rect and return its (x0, y0, x1, y1)."""
    return _place_room(world, rect, SHRINE_SIZE, rng)


def place_boss_arenas(
    world: World,
    mid_rect: Rect,
    boss_rect: Rect,
    rng: random.Random,
) -> tuple[Rect, Rect]:
    """Carve mid-boss and end-boss arenas and return (mid_boss_arena, boss_arena)."""
    mid = _place_room(world, mid_rect, MID_ARENA_SIZE, rng)
    boss = _place_room(world, boss_rect, BOSS_ARENA_SIZE, rng)
    return mid, boss


def scatter_props(
    world: World,
    rect: Rect,
    prop_keys: tuple[str, ...],
    count: int,
    rng: random.Random,
) -> list[tuple[str, int, int]]:
    """Place destructible props on floor surfaces (air above solid ground) inside rect."""
    if not prop_keys:
        return []
    x0, y0, x1, y1 = _clamp(world, *rect)
    props: list[tuple[str, int, int]] = []
    for _ in range(count * 40):
        if len(props) >= count:
            break
        x, y = rng.randint(x0, x1 - 1), rng.randint(y0, y1 - 2)
        floor = mat.KIND[world.get(x, y + 1)] in (mat.SOLID, mat.POWDER)
        if world.get(x, y) == mat.AIR and floor:
            props.append((rng.choice(prop_keys), x, y))
    return props
