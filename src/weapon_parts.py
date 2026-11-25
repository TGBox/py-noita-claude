"""Contract V8b: Modular weapon parts and placement layout (Card A23)."""

from __future__ import annotations

import zlib
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


DECOR_CHOICES: tuple[str, ...] = ("antenne", "wackelauge", "gluehbirne", "schraubenzieher")
PART_WIDTH: dict[str, int] = {
    "griff_pistole": 5,
    "griff_kurbel": 6,
    "griff_handschuh": 7,
    "gehaeuse_kurz": 10,
    "gehaeuse_mittel": 14,
    "gehaeuse_lang": 18,
    "tank_klein": 5,
    "tank_mittel": 7,
    "tank_gross": 9,
    "lauf_einfach": 8,
    "lauf_doppel": 10,
    "lauf_dreifach": 12,
}  # fmt: skip  (parts not listed advance by 6 px)
PART_OFFSET_Y: dict[str, int] = {"griff": 3, "tank": -2, "zier": -4}


@dataclass(frozen=True)
class WeaponPartPlacement:
    part_key: str
    offset_x: int
    offset_y: int


def parts_for(wand: Wand) -> list[str]:
    """Select [grip, core, ..., tip] part keys for wand based on its stats and blocks."""
    spec = wand.spec
    slots = spec.capacity or len(spec.blocks)
    if slots <= 4:
        housing = "kurz"
    elif slots <= 8:
        housing = "mittel"
    else:
        housing = "lang"
    barrel = {1: "einfach", 2: "doppel"}.get(spec.casts, "dreifach")
    if spec.spread < 0.05:
        muzzle = "spitz"
    elif spec.spread < 0.12:
        muzzle = "trichter"
    else:
        muzzle = "sieb"
    if spec.mana_max < 150:
        tank = "klein"
    elif spec.mana_max < 300:
        tank = "mittel"
    else:
        tank = "gross"
    if spec.cast_delay < 0.1:
        grip = "pistole"
    elif spec.cast_delay < 0.25:
        grip = "kurbel"
    else:
        grip = "handschuh"
    if spec.shuffle:
        decor = "klebeband"
    else:
        decor = DECOR_CHOICES[zlib.crc32(spec.name_de.encode()) % len(DECOR_CHOICES)]
    return [
        f"griff_{grip}",
        f"gehaeuse_{housing}",
        f"tank_{tank}",
        f"zier_{decor}",
        f"lauf_{barrel}",
        f"muendung_{muzzle}",
    ]


def layout_for(wand: Wand) -> list[WeaponPartPlacement]:
    """Return ordered WeaponPartPlacement entries with ascending offset_x."""
    placements: list[WeaponPartPlacement] = []
    x = 0
    for key in parts_for(wand):
        placements.append(WeaponPartPlacement(key, x, PART_OFFSET_Y.get(key.split("_")[0], 0)))
        x += PART_WIDTH.get(key, 6)
    return placements


PHASE3_WEAPON_ALIASES: dict[str, str] = {
    "waffe_titan_koffer": "waffe_patent_koffer",
}

PHASE3_WEAPONS: dict[str, dict[str, object]] = {
    "waffe_patent_koffer": {
        "name_de": "Titan-Aktenkoffer-Blaster",
        "alias_de": "Revolver-Patentkoffer",
        "damage": 48.0,
        "spread": 0.04,
        "cast_delay": 0.22,
        "mana_cost": 18,
        "casts": 3,
        "special": "klingende_akten_salve",
        "quote_de": "Abgelehnte Anträge fliegen mit Mach 2.",
    },
}


def get_phase3_weapon(key: str) -> dict[str, object]:
    """Resolve a Phase 3 reward weapon definition by key or alias."""
    resolved = PHASE3_WEAPON_ALIASES.get(key, key)
    if resolved not in PHASE3_WEAPONS:
        raise KeyError(f"Unbekannte Phase-3-Waffe: {key}")
    return dict(PHASE3_WEAPONS[resolved])
