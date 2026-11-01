"""Contract V8: Regular creature sprite builders across all 9 universes (Cards B06..B14)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT


def build_creature_sheets(
    out_dir: Path = ASSET_ROOT,
    universe_key: str | None = None,
) -> list[Path]:
    """Build kreaturen/<species>.{png,json} for universe_key (or all universes if None)."""
    raise NotImplementedError("Cards B06..B14")

