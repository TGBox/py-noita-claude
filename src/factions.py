"""Contract V4: Faction hostility matrix and dynamic grudges (Card A11)."""

from __future__ import annotations

FACTIONS: tuple[str, ...] = (
    "spieler",
    "wildnis",
    "fleischwelt",
    "aktenhalde",
    "glibbria",
    "kruemelreich",
    "sporenklub",
    "abtei",
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


class Grudges(set[tuple[str, str]]):
    """Dynamic blood-feud set between factions (Contract V4)."""

    def mark(self, faction_a: str, faction_b: str) -> None:
        record_grudge(self, faction_a, faction_b)

    def hated(self, faction_a: str, faction_b: str) -> bool:
        return (faction_a, faction_b) in self or (faction_b, faction_a) in self


def hostile(
    faction_a: str,
    faction_b: str,
    grudges: set[tuple[str, str]] | None = None,
) -> bool:
    """Alias for are_hostile (Contract V4)."""
    return are_hostile(faction_a, faction_b, grudges)


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
