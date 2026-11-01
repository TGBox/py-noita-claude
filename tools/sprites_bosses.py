"""Contract V8: Mid-boss and end-boss sprite builders (Cards B15..B19)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT


def build_mid_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<mid_boss>.{png,json} for all 9 mid-bosses + warden (Cards B15, B16)."""
    raise NotImplementedError("Cards B15, B16")


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    raise NotImplementedError("Cards B17..B19")

