"""Contract V17: 3 Evil Selves encounters, signature wands, and Empress bargain (Cards F07, F08)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..run import Run
    from ..spells import Wand

EVIL_SELVES: tuple[str, ...] = (
    "boese_kaiserin",
    "boese_gute",
    "boese_omega",
)


def evil_self_for_depth(depth: int) -> str | None:
    """Return the evil self species for depth 2, 3, or 4, else None."""
    raise NotImplementedError("Card F07")


def signature_wand_for_evil_self(species: str) -> Wand:
    """Create the signature Wand dropped by the given evil self species."""
    raise NotImplementedError("Card F07")


def apply_empress_bargain(run: Run, accepted: bool) -> None:
    """Apply the Empress bargain outcome on run."""
    raise NotImplementedError("Card F07")

