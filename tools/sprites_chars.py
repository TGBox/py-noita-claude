"""Contract V8: Character, companion, authority agent, evil self, and trader sprite builders (Cards B01..B05)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT


def build_player_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/spielerin.{png,json} (Card B01)."""
    raise NotImplementedError("Card B01")


def build_klonita_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/klonita.{png,json} (Card B02)."""
    raise NotImplementedError("Card B02")


def build_agent_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/agent_*.{png,json} (Card B03)."""
    raise NotImplementedError("Card B03")


def build_evil_and_hq_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/boese_* and ober_cloita sheets (Card B04)."""
    raise NotImplementedError("Card B04")


def build_trader_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/npc_*.{png,json} (Card B05)."""
    raise NotImplementedError("Card B05")

