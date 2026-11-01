"""Contract V9: Universe generator registry and dispatcher (Card A25, D01..D09)."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
    from ...worldgen import Level
    from ..model import Universe

GENERATORS: dict[str, Callable[[World, Universe, int, int], Level]] = {}


def generate_universe(world: World, universe: Universe, depth: int, seed: int) -> Level:
    """Generate a universe level using the registered generator for universe.key."""
    raise NotImplementedError("Card A25")

