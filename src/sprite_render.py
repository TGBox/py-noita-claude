"""Contract V6: Sprite sheet cache, frame blitting, and glow extraction (Card A18)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .sprites import Animator, SheetMeta

ASSET_ROOT: Path = Path(__file__).resolve().parent.parent / "assets" / "sprites"


class SheetCache:
    def __init__(self, root: Path = ASSET_ROOT) -> None:
        self.root: Path = root
        self._cache: dict[tuple[str, str], tuple[pygame.Surface, SheetMeta]] = {}

    def get(self, category: str, name: str) -> tuple[pygame.Surface, SheetMeta]:
        """Return cached (Surface, SheetMeta) for category/name, with headless fallback."""
        key = (category, name)
        if key in self._cache:
            return self._cache[key]

        # Construct paths
        json_path = self.root / category / f"{name}.json"
        png_path = self.root / category / f"{name}.png"

        # Try to load from files
        try:
            from .sprites import load_sheet_meta

            if png_path.exists() and json_path.exists():
                meta = load_sheet_meta(json_path)
                sheet = pygame.image.load(png_path).convert_alpha()
                result = (sheet, meta)
            else:
                # Fallback: create a deterministic test surface
                sheet = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.rect(sheet, (255, 255, 255, 255), (0, 0, 16, 16), 1)
                pygame.draw.line(sheet, (255, 0, 0, 255), (0, 0), (16, 16), 1)
                pygame.draw.line(sheet, (255, 0, 0, 255), (16, 0), (0, 16), 1)

                # Create a simple meta with one frame
                from .sprites import AnimSpec, SheetMeta

                meta = SheetMeta(
                    frame_size=(16, 16), anchor=(8, 8), anims={"idle": AnimSpec(0, 1)}, glow=()
                )
                result = (sheet, meta)
        except (FileNotFoundError, pygame.error, json.JSONDecodeError):
            # Fallback in case of any error
            sheet = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.rect(sheet, (255, 255, 255, 255), (0, 0, 16, 16), 1)
            pygame.draw.line(sheet, (255, 0, 0, 255), (0, 0), (16, 16), 1)
            pygame.draw.line(sheet, (255, 0, 0, 255), (16, 0), (0, 16), 1)

            from .sprites import AnimSpec, SheetMeta

            meta = SheetMeta(
                frame_size=(16, 16), anchor=(8, 8), anims={"idle": AnimSpec(0, 1)}, glow=()
            )
            result = (sheet, meta)

        self._cache[key] = result
        return result


def blit_frame(
    target: pygame.Surface,
    sheet: pygame.Surface,
    meta: SheetMeta,
    animator: Animator,
    world_x: float,
    world_y: float,
    cam_x: float,
    cam_y: float,
    *,
    flip_x: bool = False,
    angle_deg: float = 0.0,
    flash: float = 0.0,
    tint: tuple[int, int, int] | None = None,
) -> None:
    """Blit the current animator frame anchored at (world_x - cam_x, world_y - cam_y)."""
    # Calculate screen position
    screen_x = world_x - cam_x
    screen_y = world_y - cam_y

    # Get frame rectangle from animator
    rect = animator.frame_rect()

    # Extract frame from sheet
    frame = sheet.subsurface(rect)

    # Apply flip if needed
    if flip_x:
        frame = pygame.transform.flip(frame, True, False)

    # Apply rotation if needed
    if angle_deg != 0.0:
        frame = pygame.transform.rotate(frame, angle_deg)

    # Calculate position with anchor offset
    anchor_x, anchor_y = meta.anchor
    draw_x = screen_x - anchor_x
    draw_y = screen_y - anchor_y

    # Flash and tint work on a copy (the frame is a view into the cached sheet) and only
    # change colour, never alpha: transparent pixels must stay transparent.
    if flash > 0.0 or tint is not None:
        frame = frame.copy()
    if flash > 0.0:
        lift = int(255 * min(1.0, flash))
        frame.fill((lift, lift, lift, 0), special_flags=pygame.BLEND_RGBA_ADD)
    if tint is not None:
        frame.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)

    # Blit to target
    target.blit(frame, (draw_x, draw_y))


def glow_points(
    meta: SheetMeta,
    world_x: float,
    world_y: float,
    flip_x: bool = False,
) -> list[tuple[float, float, tuple[int, int, int], int]]:
    """Return world-space glow tuples (wx, wy, color, radius) for meta.glow."""
    points = []
    _anchor_x, _anchor_y = meta.anchor

    for glow_point in meta.glow:
        offset_x, offset_y = glow_point.offset

        # Apply flip effect to X offset
        if flip_x:
            offset_x = -offset_x

        # Calculate world position
        wx = world_x + offset_x
        wy = world_y + offset_y

        points.append((wx, wy, glow_point.color, glow_point.radius))

    return points
