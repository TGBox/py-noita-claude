"""Draws the visible part of the world into an 8-bit pygame surface.

The Rust core writes palette indices (``material * VARIANTS + grain``) for the
camera rectangle into a buffer that the surface shares, so no per-pixel Python
work happens per frame. Fire and acid are animated by cycling palette entries.
"""

from __future__ import annotations

import random

import pygame

from src import native
from src.materials import ACID, FIRE, VARIANTS, build_palette
from src.texture import make_grain
from src.world import World

FIRE_TONES = ((255, 214, 120), (255, 150, 40), (226, 84, 24), (255, 186, 70))
ACID_TONES = ((140, 196, 40), (156, 214, 52), (124, 180, 34), (170, 222, 70))

# Player sprite (facing right): h hood, f face, e eye, c cloak, d cloak fold, l legs.
PLAYER_SPRITE = (
    "..hhhh..",
    ".hhhhhh.",
    "hhhhhhhh",
    "hhffffhh",
    "hhfffehh",
    "hhffffhh",
    ".hhffhh.",
    ".cccccc.",
    "cccccccc",
    "ccdccccc",
    "ccdcccdc",
    "ccdcccdc",
    "cccccccc",
    "ccdcccdc",
    ".cccccc.",
    ".cccccc.",
    ".ll..ll.",
    ".ll..ll.",
)
SPRITE_COLORS = {
    "h": (52, 40, 48),
    "f": (176, 160, 146),
    "e": (220, 36, 36),
    "c": (70, 50, 60),
    "d": (42, 30, 38),
    "l": (34, 24, 30),
}


class WorldRenderer:
    """Keeps an 8-bit view surface in sync with the camera rectangle of a world."""

    def __init__(self, world: World, view_width: int, view_height: int) -> None:
        self.view_width = view_width
        self.view_height = view_height
        self._grain = make_grain(world.width, world.height)
        self._grain_view = native.byte_view(self._grain)
        self._buffer = bytearray(view_width * view_height)
        self._buffer_view = native.byte_view(self._buffer)
        self._flicker = random.Random()
        self.surface = pygame.image.frombuffer(self._buffer, (view_width, view_height), "P")
        self.surface.set_palette(build_palette())

    def refresh(self, world: World, camera_x: int, camera_y: int) -> None:
        """Render the view whose top-left world cell is (camera_x, camera_y)."""
        native.render(
            native.byte_view(world.grid),
            self._grain_view,
            self._buffer_view,
            world.width,
            camera_x,
            camera_y,
            self.view_width,
            self.view_height,
            VARIANTS,
        )
        choice = self._flicker.choice
        for variant in range(VARIANTS):
            self.surface.set_palette_at(FIRE * VARIANTS + variant, choice(FIRE_TONES))
            self.surface.set_palette_at(ACID * VARIANTS + variant, choice(ACID_TONES))


def build_player_sprites() -> tuple[pygame.Surface, pygame.Surface]:
    """Return the player sprite facing right and facing left."""
    height, width = len(PLAYER_SPRITE), len(PLAYER_SPRITE[0])
    right = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(PLAYER_SPRITE):
        for x, key in enumerate(row):
            if key in SPRITE_COLORS:
                right.set_at((x, y), SPRITE_COLORS[key])
    return right, pygame.transform.flip(right, True, False)
