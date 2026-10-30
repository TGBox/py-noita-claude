"""Draws the visible part of the world into an 8-bit pygame surface.

The Rust core writes palette indices (``material * VARIANTS + grain``) for the
camera rectangle into a buffer that the surface shares, so no per-pixel Python
work happens per frame. Fire and acid are animated by cycling palette entries.
"""

from __future__ import annotations

import math
import random

import pygame

from src import native
from src.materials import ACID, BLOOD, FIRE, MATERIALS, VARIANTS, build_palette
from src.projectiles import Projectile
from src.spells import Block, Category
from src.texture import make_grain
from src.wand import Wand
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
    "h": (84, 70, 80),
    "f": (196, 182, 168),
    "e": (230, 40, 40),
    "c": (104, 84, 96),
    "d": (66, 52, 62),
    "l": (50, 40, 48),
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


# ------------------------------------------------------------------ entities

ARM_FLESH = (150, 84, 86)
NODE_FLESH_MIX = 0.35  # how much flesh colour is mixed into the block nodes
ARM_TIP_READY = (255, 196, 150)
ARM_TIP_IDLE = (90, 52, 54)
CATEGORY_COLORS = {
    Category.FORM: (226, 214, 184),
    Category.MODIFIER: (150, 84, 172),
    Category.TRIGGER: (232, 196, 70),
    Category.PAYLOAD: (200, 40, 40),
}
FORM_COLORS = {
    "funke": (255, 226, 170),
    "nadel": (236, 226, 204),
    "gallenblase": (150, 172, 60),
}


def block_color(block: Block) -> tuple[int, int, int]:
    """Colour of a block's node: payloads show their material."""
    if block.material is not None:
        return MATERIALS[block.material].color
    return CATEGORY_COLORS[block.category]


def draw_augmentation(
    canvas: pygame.Surface,
    shoulder: tuple[float, float],
    angle: float,
    wand: Wand,
) -> None:
    """Draw the active wand as a fleshy arm growth whose nodes are its blocks."""
    count = len(wand.blocks)
    length = 7 + count * 1.5
    dx, dy = math.cos(angle), math.sin(angle)
    tip = (shoulder[0] + dx * length, shoulder[1] + dy * length)
    pygame.draw.line(canvas, ARM_FLESH, shoulder, tip, 2)
    for index, block in enumerate(wand.blocks):
        t = (index + 1) / (count + 1)
        x, y = int(shoulder[0] + dx * length * t), int(shoulder[1] + dy * length * t)
        size = 3 if index == wand.index and not wand.recharging else 2
        color = _mix(block_color(block), ARM_FLESH, NODE_FLESH_MIX)
        canvas.fill(color, (x - size // 2, y - size // 2, size, size))
    tip_color = ARM_TIP_READY if wand.ready else ARM_TIP_IDLE
    canvas.fill(tip_color, (int(tip[0]) - 1, int(tip[1]) - 1, 2, 2))


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


def draw_projectiles(
    canvas: pygame.Surface, projectiles: list[Projectile], cam_x: int, cam_y: int
) -> None:
    for p in projectiles:
        x, y = int(p.x) - cam_x, int(p.y) - cam_y
        key = p.form.key
        if key == "nadel":
            speed = math.hypot(p.vx, p.vy) or 1.0
            tail = (x - p.vx / speed * 5, y - p.vy / speed * 5)
            pygame.draw.line(canvas, FORM_COLORS[key], tail, (x, y))
        elif key == "gallenblase":
            pygame.draw.circle(canvas, FORM_COLORS[key], (x, y), 3)
            if int(p.age * 8) % 2:
                canvas.fill((255, 80, 60), (x, y - 1, 1, 1))
        elif key == "klumpen":
            material = p.material if p.material is not None else BLOOD
            pygame.draw.circle(canvas, MATERIALS[material].color, (x, y), 2)
        else:
            color = FORM_COLORS.get(key, (255, 255, 255))
            if p.material is not None:
                color = MATERIALS[p.material].color
            canvas.fill(color, (x - 1, y - 1, 3, 3))
