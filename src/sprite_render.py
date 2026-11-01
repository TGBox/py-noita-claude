"""Contract V6: Sprite sheet cache, frame blitting, and glow extraction (Card A18)."""

from __future__ import annotations

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
        raise NotImplementedError("Card A18")


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
    raise NotImplementedError("Card A18")


def glow_points(
    meta: SheetMeta,
    world_x: float,
    world_y: float,
    flip_x: bool = False,
) -> list[tuple[float, float, tuple[int, int, int], int]]:
    """Return world-space glow tuples (wx, wy, color, radius) for meta.glow."""
    raise NotImplementedError("Card A18")

