"""Contract V8: Weapon part, spell icon, sample, and pickup sprite builders (Cards B20..B27)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT


def build_weapon_part_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build waffen/<part_key>.{png,json} for all 10 weapon parts (Card B20)."""
    raise NotImplementedError("Card B20")


def build_spell_icon_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build zauber/<block_key>.{png,json} for all spell blocks (Cards B21..B24)."""
    raise NotImplementedError("Cards B21..B24")


def build_item_icon_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build gegenstaende/<key>.{png,json} for all samples, gold sizes, and pickups (Cards B25..B27)."""
    raise NotImplementedError("Cards B25..B27")

