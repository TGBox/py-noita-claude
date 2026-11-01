"""Contract V4: Faction hostility matrix and dynamic grudges (Card A11)."""

from __future__ import annotations

FACTIONS: tuple[str, ...] = (
    "spieler",
    "wildnis",
    "schrott",
    "pilze",
    "parasiten",
    "behoerde",
    "backwerk",
    "tiefsee",
    "insekten",
    "automaten",
    "zirkus",
    "haendler",
    "boese_ichs",
)

HATE_MATRIX: dict[str, frozenset[str]] = {}


def are_hostile(
    faction_a: str,
    faction_b: str,
    grudges: set[tuple[str, str]] | None = None,
) -> bool:
    """Return True if faction_a and faction_b are hostile by default or via grudges."""
    raise NotImplementedError("Card A11")


def record_grudge(
    grudges: set[tuple[str, str]],
    faction_a: str,
    faction_b: str,
) -> None:
    """Record a symmetric blood feud between faction_a and faction_b."""
    raise NotImplementedError("Card A11")

