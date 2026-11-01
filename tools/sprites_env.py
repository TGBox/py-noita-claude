"""Contract V8: Workshop station, prop, and particle sprite builders (Cards B28..B31)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT


def build_env_prop_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build umgebung/<key>.{png,json} for stations and environment props (Cards B28..B30)."""
    raise NotImplementedError("Cards B28..B30")


def build_particle_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build partikel/<key>.{png,json} for all 12 particle sheets (Card B31)."""
    raise NotImplementedError("Card B31")

