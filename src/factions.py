"""Contract V4: Faction hostility matrix and dynamic grudges (Card A11)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.enemies import Creature

SPIELER = "spieler"
WILDNIS = "wildnis"
HAENDLER = "haendler"
BEHOERDE = "behoerde"
BOESE_ICHS = "boese_ichs"

UNIVERSE_FACTIONS: dict[str, str] = {
    "fleischwelt": "parasiten",
    "aktenhalde": "akten",
    "glibbria": "gelee",
    "kruemelreich": "insekten",
    "sporenklub": "pilze",
    "abtei": "tiefsee",
}
NATIVE_FACTIONS: tuple[str, ...] = tuple(UNIVERSE_FACTIONS.values())

FACTIONS: tuple[str, ...] = (SPIELER, WILDNIS, HAENDLER, BEHOERDE, BOESE_ICHS, *NATIVE_FACTIONS)

# Card A11: fill in literally from contract V4.
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


def hostile(a: Creature, b: Creature, grudges: set[tuple[str, str]] | None = None) -> bool:
    """Creature vs. creature: faction rule plus species-level grudges (Contract V4)."""
    raise NotImplementedError("Card A11")
