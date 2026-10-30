"""Turns the world grid into a pygame surface without numpy.

Each cell becomes ``material * VARIANTS + noise`` (a palette index). The packing is
done with big-int arithmetic on the whole grid at once, which is far faster than a
per-cell Python loop. The result is shared with an 8-bit paletted pygame surface.
"""

from __future__ import annotations

import random

import pygame

from src.materials import FIRE, LAVA, VARIANTS, build_palette
from src.world import World

FIRE_TONES = ((255, 220, 90), (255, 160, 40), (240, 100, 25), (255, 190, 60))
LAVA_TONES = ((255, 120, 20), (235, 80, 15), (255, 150, 40), (210, 60, 10))


class WorldRenderer:
    """Keeps an 8-bit surface in sync with ``world.grid``."""

    def __init__(self, world: World) -> None:
        self._size = len(world.grid)
        rng = random.Random(7)
        mask = bytes(b % VARIANTS for b in range(256))
        noise = rng.randbytes(self._size).translate(mask)
        self._noise = int.from_bytes(noise, "little")
        self._buffer = bytearray(self._size)
        self._flicker = random.Random()
        self.surface = pygame.image.frombuffer(self._buffer, (world.width, world.height), "P")
        self.surface.set_palette(build_palette())

    def refresh(self, world: World) -> None:
        """Re-pack the grid into palette indices and animate fire and lava."""
        packed = int.from_bytes(world.grid, "little") * VARIANTS + self._noise
        self._buffer[:] = packed.to_bytes(self._size, "little")
        for variant in range(VARIANTS):
            self.surface.set_palette_at(FIRE * VARIANTS + variant, self._flicker.choice(FIRE_TONES))
            self.surface.set_palette_at(LAVA * VARIANTS + variant, self._flicker.choice(LAVA_TONES))
