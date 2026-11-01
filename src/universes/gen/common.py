"""Contract V9: Common topology and room/arena placement helpers (Card A25)."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World


def region_bands(
    width: int,
    height: int,
    topology: str,
) -> list[tuple[int, int, int, int]]:
    """Return 3 (x0, y0, x1, y1) bounding boxes for topology."""
    raise NotImplementedError("Card A25")


def carve_room(
    world: World,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    wall_mat: int | None = None,
) -> tuple[int, int, int, int]:
    """Carve an air room and return its (x0, y0, x1, y1) rect."""
    raise NotImplementedError("Card A25")


def carve_tunnel(
    world: World,
    start: tuple[int, int],
    end: tuple[int, int],
    radius: int = 4,
) -> None:
    """Carve a continuous air corridor from start to end."""
    raise NotImplementedError("Card A25")


def fill_basin(
    world: World,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    liquid_mat: int,
) -> None:
    """Fill a lower basin area with liquid_mat."""
    raise NotImplementedError("Card A25")


def place_trader_nook(
    world: World,
    rect: tuple[int, int, int, int],
    rng: random.Random,
) -> tuple[int, int, int, int]:
    """Carve a sheltered trader nook inside rect and return its (x0, y0, x1, y1)."""
    raise NotImplementedError("Card A25")


def place_challenge_shrine(
    world: World,
    rect: tuple[int, int, int, int],
    rng: random.Random,
) -> tuple[int, int, int, int]:
    """Carve a challenge shrine chamber inside rect and return its (x0, y0, x1, y1)."""
    raise NotImplementedError("Card A25")


def place_boss_arenas(
    world: World,
    mid_rect: tuple[int, int, int, int],
    boss_rect: tuple[int, int, int, int],
    rng: random.Random,
) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    """Carve mid-boss and end-boss arenas and return (mid_boss_arena, boss_arena)."""
    raise NotImplementedError("Card A25")


def scatter_props(
    world: World,
    rect: tuple[int, int, int, int],
    prop_keys: tuple[str, ...],
    count: int,
    rng: random.Random,
) -> list[tuple[str, int, int]]:
    """Place destructible props on floor surfaces inside rect."""
    raise NotImplementedError("Card A25")

