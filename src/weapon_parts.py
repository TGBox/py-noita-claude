"""Contract V8b: Modular weapon parts and placement layout (Card A23)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .spells import Wand

WEAPON_PART_KEYS: tuple[str, ...] = (
    "griff_holz",
    "griff_eisen",
    "griff_knochen",
    "kern_rubin",
    "kern_spule",
    "kern_auge",
    "kern_leere",
    "spitz_prisma",
    "spitz_gabel",
    "spitz_zahn",
)


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

