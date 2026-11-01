"""Contract V20: 8 Physik-o-Mat material puzzles (Cards E07, E08)."""

from __future__ import annotations

from . import Minigame

PUZZLE_KEYS: tuple[str, ...] = (
    "lava_water",
    "acid_gold",
    "oil_fire",
    "electricity_water",
    "glas_fuellen",
    "vase_retten",
    "kerze_zuenden",
    "ameisenstrasse",
)


def make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame:
    """Create a Physik-o-Mat puzzle Minigame instance."""
    raise NotImplementedError("Cards E07, E08")
