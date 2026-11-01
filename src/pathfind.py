"""Contract V3: Grid A* pathfinding for walk, fly, and swim (Card A10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World

PATH_CACHE_TTL: float = 0.4
MAX_PATH_EXPANSIONS: int = 160


@dataclass
class PathCacheEntry:
    path: list[tuple[int, int]] = field(default_factory=list)
    goal: tuple[int, int] = (0, 0)
    updated_at: float = -999.0


def find_path(
    world: World,
    start: tuple[int, int],
    goal: tuple[int, int],
    loco: str,
    max_expansions: int = MAX_PATH_EXPANSIONS,
) -> list[tuple[int, int]]:
    """Compute a coarse grid path from start to goal cell for loco ('walk', 'fly', 'swim')."""
    raise NotImplementedError("Card A10")


def next_waypoint(
    world: World,
    start_x: float,
    start_y: float,
    goal_x: float,
    goal_y: float,
    loco: str,
    cache: PathCacheEntry,
    now: float = 0.0,
) -> tuple[float, float]:
    """Return the next world-pixel waypoint towards (goal_x, goal_y), updating cache if stale."""
    raise NotImplementedError("Card A10")

