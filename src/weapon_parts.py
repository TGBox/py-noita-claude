"""Contract V8b: Modular weapon parts and placement layout (Card A23)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .wand import Wand

WEAPON_PART_KEYS: tuple[str, ...] = (
    "griff_pistole",
    "griff_kurbel",
    "griff_handschuh",
    "gehaeuse_kurz",
    "gehaeuse_mittel",
    "gehaeuse_lang",
    "tank_klein",
    "tank_mittel",
    "tank_gross",
    "lauf_einfach",
    "lauf_doppel",
    "lauf_dreifach",
    "muendung_spitz",
    "muendung_trichter",
    "muendung_sieb",
    "zier_klebeband",
    "zier_antenne",
    "zier_wackelauge",
    "zier_gluehbirne",
    "zier_schraubenzieher",
)
PART_ORDER: tuple[str, ...] = ("griff", "gehaeuse", "tank", "zier", "lauf", "muendung")


@dataclass(frozen=True)
class WeaponPartPlacement:
    part_key: str
    offset_x: int
    offset_y: int


def parts_for(wand: Wand) -> list[str]:
    """Select [grip, core, ..., tip] part keys for wand based on its stats and blocks."""
    raise NotImplementedError("Card A23")


def layout_for(wand: Wand) -> list[WeaponPartPlacement]:
    """Return ordered WeaponPartPlacement entries with ascending offset_x."""
    raise NotImplementedError("Card A23")
