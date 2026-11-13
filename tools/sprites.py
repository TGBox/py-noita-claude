"""Contract V8: Procedural pixel-canvas primitives and sheet exporter (Cards A22, B36)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from src.sprite_render import ASSET_ROOT
from tools.palette import OUTLINE_DARK

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


def _shade(ramp: PaletteRamp, light: float, radius2: float) -> tuple[int, int, int, int]:
    """Pick a ramp stop for a top-left light (light > 0 faces the light source)."""
    if radius2 > 0.7 and light > 0.1:
        return ramp.rim
    if light > 0.45:
        return ramp.highlight
    if light > 0.1:
        return ramp.light
    if light > -0.3:
        return ramp.mid
    return ramp.shadow


def draw_shaded_ellipse(
    canvas: PixelCanvas,
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    ramp: PaletteRamp,
) -> None:
    """Draw a top-left-lit shaded ellipse onto canvas using ramp."""
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / max(rx, 1), (y - cy) / max(ry, 1)
            radius2 = nx * nx + ny * ny
            if radius2 > 1.0:
                continue
            canvas.set_px(x, y, _shade(ramp, -(nx + ny) * 0.5, radius2))


def draw_shaded_rect(
    canvas: PixelCanvas,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    ramp: PaletteRamp,
) -> None:
    """Draw a shaded rectangle onto canvas using ramp."""
    width, height = max(x1 - x0, 1), max(y1 - y0, 1)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            nx, ny = (x - x0) / width * 2 - 1, (y - y0) / height * 2 - 1
            canvas.set_px(x, y, _shade(ramp, -(nx + ny) * 0.5, max(abs(nx), abs(ny)) ** 2))


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
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    x, y = x0, y0
    half = thickness // 2
    while True:
        for oy in range(thickness):
            for ox in range(thickness):
                canvas.set_px(x + ox - half, y + oy - half, rgba)
        if x == x1 and y == y1:
            break
        doubled = 2 * err
        if doubled >= dy:
            err += dy
            x += sx
        if doubled <= dx:
            err += dx
            y += sy


def apply_dark_outline(canvas: PixelCanvas) -> None:
    """Add a 1px dark outline around all non-transparent pixels."""
    opaque = {
        (x, y)
        for y in range(canvas.height)
        for x in range(canvas.width)
        if canvas.get_px(x, y)[3] > 0
    }
    for x, y in opaque:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in opaque:
                canvas.set_px(nx, ny, OUTLINE_DARK)


def add_dither(canvas: PixelCanvas, intensity: int = 8) -> None:
    """Apply subtle ordered dithering to opaque pixels."""
    bayer = ((0, 2), (3, 1))
    for y in range(canvas.height):
        for x in range(canvas.width):
            r, g, b, a = canvas.get_px(x, y)
            if a == 0:
                continue
            shift = int((bayer[y & 1][x & 1] - 1.5) / 1.5 * intensity)
            canvas.set_px(x, y, tuple(max(0, min(255, v + shift)) for v in (r, g, b)) + (a,))  # type: ignore[arg-type]


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
    fps = fps or {}
    loops = loops or {}
    next_anims = next_anims or {}
    first = next(iter(frames.values()))[0]
    frame_w, frame_h = first.width, first.height
    columns = max(len(row) for row in frames.values())
    sheet = pygame.Surface((frame_w * columns, frame_h * len(frames)), pygame.SRCALPHA)
    anims: dict[str, dict[str, object]] = {}
    for row_index, (anim, row) in enumerate(frames.items()):
        for col, canvas in enumerate(row):
            sheet.blit(canvas.surface, (col * frame_w, row_index * frame_h))
        anims[anim] = {
            "row": row_index,
            "frames": len(row),
            "fps": fps.get(anim, 8.0),
            "loop": loops.get(anim, True),
            "next_anim": next_anims.get(anim, "idle"),
        }
    folder = out_dir / category
    folder.mkdir(parents=True, exist_ok=True)
    png_path, json_path = folder / f"{name}.png", folder / f"{name}.json"
    pygame.image.save(sheet, str(png_path))
    meta = {
        "frame_size": [frame_w, frame_h],
        "anchor": list(anchor),
        "anims": anims,
        "glow": glow or [],
    }
    json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return png_path, json_path


def build_all(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Generate all procedural sprite sheets and JSON metadata files."""
    raise NotImplementedError("Card B36")
