"""Contract V17: the evil selves, final boss, echoes and the Empress bargain (Cards F07, F08)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.wand import Wand, WandSpec

if TYPE_CHECKING:
    from ..run import Run

EVIL_SELVES: tuple[str, ...] = (
    "boese_kaiserin",
    "boese_gute",
    "boese_omega",
)
EVIL_HP: dict[str, int] = {"boese_kaiserin": 3500, "boese_gute": 3200, "boese_omega": 3800}
ECHO_HP_FACTOR = 0.30
ECHO_DEPTHS: tuple[int, int] = (3, 5)
ECHO_GOLD = 100

# name, blocks, mana_max, recharge (Bibel 05: every evil self has her own weapon)
SIGNATURE_WANDS: dict[str, tuple[str, tuple[str, ...], int, float]] = {
    "boese_kaiserin": (
        "Kaiserliches Zepter", ("beschleunigung", "sprengkraft", "nadelregen"), 180, 0.22,
    ),
    "boese_gute": ("Heiligenschein-Gerte", ("zielsuche", "leuchtkugel", "kettenfunke"), 200, 0.18),
    "boese_omega": ("Omega-Armkanone", ("dreifach", "zielsuche", "feuerball"), 260, 0.30),
}  # fmt: skip


def final_evil_self(run: Run) -> str:
    """The run's final boss: run.plan.evil_self."""
    return run.plan.evil_self


def echo_for_depth(run: Run, depth: int) -> str | None:
    """The echo waiting in the secret room at depth 3 or 5, else None."""
    if depth not in ECHO_DEPTHS:
        return None
    others = [key for key in EVIL_SELVES if key != final_evil_self(run)]
    return others[ECHO_DEPTHS.index(depth)]


def signature_wand_spec(species: str) -> WandSpec:
    name, blocks, mana_max, recharge = SIGNATURE_WANDS[species]
    return WandSpec(
        name, blocks, mana_max=mana_max, mana_regen=70, cast_delay=0.12, recharge=recharge,
        capacity=len(blocks) + 3,
    )  # fmt: skip


def signature_wand_for_evil_self(species: str) -> Wand:
    """The evil self's own weapon, dropped after the final fight."""
    return Wand(signature_wand_spec(species))


def apply_empress_bargain(run: Run, accepted: bool) -> None:
    """Accepting the Empress's offer ends the run with the bad ending."""
    if not accepted:
        return  # the fight goes on
    run.ending = "boese"
    run.outcome = "bad_ending"  # ends the run like "dead"
    run.victory = False
    run.records.discover("ending", "boese")
