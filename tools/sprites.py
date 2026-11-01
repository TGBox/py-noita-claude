"""Contract V8: Procedural pixel-canvas primitives and sheet exporter (Cards A22, B36)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from src.sprite_render import ASSET_ROOT

if TYPE_CHECKING:
    from .palette import PaletteRamp


class PixelCanvas:
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.surface: pygame.Surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def set_px(self, x: int, y: int, rgba: tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.surface.set_at((x, y), rgba)

    def get_px(self, x: int, y: int) -> tuple[int, int, int, int]:
        if 0 <= x < self.width and 0 <= y < self.height:
            c = self.surface.get_at((x, y))
            return (c.r, c.g, c.b, c.a)
        return (0, 0, 0, 0)


def draw_shaded_ellipse(
    canvas: PixelCanvas,
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    ramp: PaletteRamp,
) -> None:
    """Draw a top-left-lit shaded ellipse onto canvas using ramp."""
    raise NotImplementedError("Card A22")


def draw_shaded_rect(
    canvas: PixelCanvas,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    ramp: PaletteRamp,
) -> None:
    """Draw a shaded rectangle onto canvas using ramp."""
    raise NotImplementedError("Card A22")


def draw_segment_line(
    canvas: PixelCanvas,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    rgba: tuple[int, int, int, int],
    thickness: int = 1,
) -> None:
    """Draw a line segment onto canvas."""
    raise NotImplementedError("Card A22")


def apply_dark_outline(canvas: PixelCanvas) -> None:
    """Add a 1px dark outline around all non-transparent pixels."""
    raise NotImplementedError("Card A22")


def add_dither(canvas: PixelCanvas, intensity: int = 8) -> None:
    """Apply subtle ordered dithering to opaque pixels."""
    raise NotImplementedError("Card A22")


def save_sheet(
    category: str,
    name: str,
    frames: dict[str, list[PixelCanvas]],
    *,
    anchor: tuple[int, int],
    fps: dict[str, float] | None = None,
    loops: dict[str, bool] | None = None,
    next_anims: dict[str, str] | None = None,
    glow: list[dict[str, object]] | None = None,
    out_dir: Path = ASSET_ROOT,
) -> tuple[Path, Path]:
    """Export sprite sheet PNG and JSON sidecar under out_dir/category/name.{png,json}."""
    raise NotImplementedError("Card A22")


def build_all(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Generate all procedural sprite sheets and JSON metadata files."""
    raise NotImplementedError("Card B36")

