"""Contract V17: the evil selves, final boss, echoes and the Empress bargain (Cards F07, F08)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..run import Run
    from ..wand import Wand

EVIL_SELVES: tuple[str, ...] = (
    "boese_kaiserin",
    "boese_gute",
    "boese_omega",
)
EVIL_HP: dict[str, int] = {"boese_kaiserin": 3500, "boese_gute": 3200, "boese_omega": 3800}
ECHO_HP_FACTOR = 0.30
ECHO_DEPTHS: tuple[int, int] = (3, 5)
ECHO_GOLD = 100


def final_evil_self(run: Run) -> str:
    """The run's final boss: run.plan.evil_self."""
    raise NotImplementedError("Card F07")


def echo_for_depth(run: Run, depth: int) -> str | None:
    """The echo waiting in the secret room at depth 3 or 5, else None."""
    raise NotImplementedError("Card F07")


def signature_wand_for_evil_self(species: str) -> Wand:
    """The evil self's own weapon, dropped after the final fight."""
    raise NotImplementedError("Card F07")


def apply_empress_bargain(run: Run, accepted: bool) -> None:
    """Accepting the Empress's offer ends the run with the bad ending."""
    raise NotImplementedError("Card F07")
