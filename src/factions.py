"""Contract V4: Faction hostility matrix and dynamic grudges (Card A11)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.enemies import Creature

SPIELER = "spieler"
WILDNIS = "wildnis"  # Standard für Kreaturen ohne Universum (Sandbox, Alt-Kreaturen)
HAENDLER = "haendler"
BEHOERDE = "behoerde"  # Agenten, Ober-Cloita, Rat
BOESE_ICHS = "boese_ichs"

UNIVERSE_FACTIONS: dict[str, str] = {  # Universum -> Fraktion seiner Einheimischen
    "fleischwelt": "parasiten",
    "aktenhalde": "akten",
    "glibbria": "gelee",
    "kruemelreich": "insekten",
    "sporenklub": "pilze",
    "abtei": "tiefsee",
}
NATIVE_FACTIONS: tuple[str, ...] = tuple(UNIVERSE_FACTIONS.values())

FACTIONS: tuple[str, ...] = (SPIELER, WILDNIS, HAENDLER, BEHOERDE, BOESE_ICHS, *NATIVE_FACTIONS)

_EVERYONE = frozenset(FACTIONS)
HATE_MATRIX: dict[str, frozenset[str]] = {
    SPIELER: frozenset({BEHOERDE, BOESE_ICHS}),
    WILDNIS: frozenset({BEHOERDE, BOESE_ICHS}),
    HAENDLER: frozenset({BEHOERDE, BOESE_ICHS}),
    BEHOERDE: _EVERYONE - {BEHOERDE, BOESE_ICHS},
    BOESE_ICHS: _EVERYONE - {BOESE_ICHS, BEHOERDE},
    **{
        f: frozenset({BEHOERDE, BOESE_ICHS, *(set(NATIVE_FACTIONS) - {f})}) for f in NATIVE_FACTIONS
    },
}


def are_hostile(
    faction_a: str,
    faction_b: str,
    grudges: set[tuple[str, str]] | None = None,
) -> bool:
    """True if a and b fight each other by default (HATE_MATRIX) or via a recorded grudge."""
    if faction_a == faction_b:
        return False
    if grudges is not None and (faction_a, faction_b) in grudges:
        return True
    if faction_b in HATE_MATRIX.get(faction_a, frozenset()):
        return True
    if faction_a in HATE_MATRIX.get(faction_b, frozenset()):
        return True
    # Unbekannte Fraktionsschlüssel verhalten sich wie "wildnis"
    # We need to avoid recursion by checking if we've already resolved these factions
    resolved_a = faction_a if faction_a in FACTIONS else WILDNIS
    resolved_b = faction_b if faction_b in FACTIONS else WILDNIS
    if resolved_a != faction_a or resolved_b != faction_b:
        # At least one faction was unknown, so check the resolved versions
        return are_hostile(resolved_a, resolved_b, grudges)
    return False


def record_grudge(
    grudges: set[tuple[str, str]],
    faction_a: str,
    faction_b: str,
) -> None:
    """Record a symmetric grudge: adds (a, b) and (b, a); ignores a == b."""
    if faction_a == faction_b:
        return
    grudges.add((faction_a, faction_b))
    grudges.add((faction_b, faction_a))


def hostile(a: Creature, b: Creature, grudges: set[tuple[str, str]] | None = None) -> bool:
    """Creature vs. creature: faction rule, plus species-level grudges (collateral damage)."""
    if (
        a is b
        or a.spec.prop
        or b.spec.prop
        or a.spec.haltung == "trader"
        or b.spec.haltung == "trader"
    ):
        return False
    return are_hostile(a.spec.faction, b.spec.faction, grudges)
