"""Contract V20: the 7 Physik-o-Mat puzzles (Cards E07, E08)."""

from __future__ import annotations

from . import Minigame

PUZZLE_KEYS: tuple[str, ...] = (
    "glas_fuellen",
    "vase_retten",
    "kerze_zuenden",
    "ameisenstrasse",
    "lava_water",
    "acid_gold",
    "oil_fire",
)


def make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame:
    """Create a Physik-o-Mat puzzle."""
    raise NotImplementedError("Cards E07, E08")


def solve_actions(puzzle_key: str) -> list[tuple[str, tuple[int, int]]]:
    """Fixed solution (action, cursor) for tests and the playtest bot."""
    raise NotImplementedError("Cards E07, E08")
