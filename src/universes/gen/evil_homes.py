"""Contract V17 section 2: home worlds of the three evil selves (Card F18)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
    from ...worldgen import Level

HOME_SIZE: tuple[int, int] = (1280, 720)


def generate_evil_home(world: World, species: str, seed: int) -> Level:
    """Build the home world of ``species`` (one of EVIL_SELVES)."""
    raise NotImplementedError("Card F18")
