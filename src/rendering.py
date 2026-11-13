"""Draws the visible part of the world into an 8-bit pygame surface.

The Rust core writes palette indices (``(material * VARIANTS + grain) * LIGHT_LEVELS +
light``) for the camera rectangle into a buffer that the surface shares, so no
per-pixel Python work happens per frame. Lighting is a soft light map from glowing
materials and dynamic lights. Fire and acid flicker by cycling palette entries.
"""

from __future__ import annotations

import math
import random

import pygame

from src import materials as mat
from src import native
from src.chunks import Chunk
from src.enemies import Creature
from src.flask import CAPACITY as FLASK_CAPACITY
from src.flask import Flask, ThrownFlask
from src.loot import Pickup
from src.materials import (
    GLOW,
    LIBRARY,
    LIGHT_LEVELS,
    MATERIALS,
    OPAQUE,
    VARIANTS,
    build_palette,
    shade,
    variant_color,
)
from src.perks import PERK_BY_KEY

PERK_KEYS = tuple(PERK_BY_KEY)
from src.projectiles import Projectile
from src.settings import VIEW_HEIGHT, VIEW_WIDTH
from src.spells import CATALOG, Block, Category
from src.sprite_render import SheetCache
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
        self._grain_size = (0, 0)
        self._fit_grain(world)
        self._buffer = bytearray(view_width * view_height)
        self._buffer_view = native.byte_view(self._buffer)
        self._flicker = random.Random()
        self.surface = pygame.image.frombuffer(self._buffer, (view_width, view_height), "P")
        self.surface.set_palette(build_palette())
        self._palette_generation = mat.GENERATION

    def _fit_grain(self, world: World) -> None:
        """The grain texture covers the whole world; rebuild it when the size changes."""
        if self._grain_size != (world.width, world.height):
            self._grain = make_grain(world.width, world.height)
            self._grain_view = native.byte_view(self._grain)
            self._grain_size = (world.width, world.height)

    def refresh(
        self,
        world: World,
        camera_x: int,
        camera_y: int,
        lights: list[tuple[float, float, float, float]] | None = None,
        ambient: float = 1.0,
    ) -> None:
        """Render the view whose top-left world cell is (camera_x, camera_y).

        ``lights`` are (x, y, radius, intensity) in world pixels; glowing materials
        light themselves. With ``ambient=1`` and no lights everything is fully lit.
        """
        self._fit_grain(world)
        if self._palette_generation != mat.GENERATION:  # another universe's material set
            self.surface.set_palette(build_palette())
            self._palette_generation = mat.GENERATION
        native.render_lit(
            native.byte_view(world.grid),
            self._grain_view,
            self._buffer_view,
            world.width,
            camera_x,
            camera_y,
            self.view_width,
            self.view_height,
            VARIANTS,
            LIGHT_LEVELS,
            GLOW,
            lights or [],
            ambient,
            OPAQUE,
        )
        choice = self._flicker.choice
        top = LIGHT_LEVELS - 1
        if not (mat.has("fire") and mat.has("acid")):
            return
        for variant in range(VARIANTS):
            fire = (mat.FIRE * VARIANTS + variant) * LIGHT_LEVELS + top
            acid = (mat.ACID * VARIANTS + variant) * LIGHT_LEVELS + top
            self.surface.set_palette_at(fire, choice(FIRE_TONES))
            self.surface.set_palette_at(acid, choice(ACID_TONES))


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
    "knochensplitter": (226, 214, 190),
    "zahnbohrer": (240, 232, 214),
    "blutegel": (110, 18, 24),
    "teleportbolzen": (200, 120, 230),
    "knochensaege": (226, 220, 200),
    "sporenmine": (164, 128, 160),
    "fressgeschwuer": (60, 20, 40),
    "knochenspeer": (236, 226, 204),
    "mikrofunke": (255, 240, 200),
    "knochenbombe": (214, 202, 176),
    "nadelregen": (236, 226, 204),
    "grabklaue": (240, 232, 214),
}


def block_color(block: Block) -> tuple[int, int, int]:
    """Colour of a block's node: payloads show their material."""
    if block.material is not None:
        return LIBRARY[block.material].color
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
        size = 3 if index == wand.next_block else 2
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
        elif key == "knochensplitter":
            canvas.fill(FORM_COLORS[key], (x, y, 2, 1))
        elif key == "zahnbohrer":
            speed = math.hypot(p.vx, p.vy) or 1.0
            ux, uy = p.vx / speed, p.vy / speed
            pygame.draw.polygon(
                canvas,
                FORM_COLORS[key],
                [(x + ux * 4, y + uy * 4), (x - uy * 2, y + ux * 2), (x + uy * 2, y - ux * 2)],
            )
        elif key == "blutegel":
            wiggle = int(math.sin(p.age * 20) * 1.5)
            pygame.draw.ellipse(canvas, FORM_COLORS[key], (x - 3, y - 1 + wiggle, 6, 3))
            canvas.fill((200, 40, 40), (x + 1, y + wiggle, 1, 1))
        elif key == "teleportbolzen":
            pygame.draw.circle(canvas, FORM_COLORS[key], (x, y), 2)
            canvas.fill((255, 230, 255), (x, y, 1, 1))
        elif key == "knochensaege":
            turn = p.age * 30
            pygame.draw.circle(canvas, (120, 110, 96), (x, y), 3)
            for k in range(4):
                a = turn + k * math.pi / 2
                canvas.fill(
                    FORM_COLORS[key], (x + round(math.cos(a) * 3), y + round(math.sin(a) * 3), 1, 1)
                )
        elif key == "sporenmine":
            pygame.draw.circle(canvas, FORM_COLORS[key], (x, y), 2)
            if int(p.age * 3) % 2:
                canvas.fill((255, 90, 90), (x, y - 1, 1, 1))
        elif key == "fressgeschwuer":
            radius = 4 + math.sin(p.age * 12)
            pygame.draw.circle(canvas, FORM_COLORS[key], (x, y), radius)
            pygame.draw.circle(canvas, (150, 40, 70), (x, y), radius, 1)
        elif key == "knochenspeer":
            speed = math.hypot(p.vx, p.vy) or 1.0
            tail = (x - p.vx / speed * 9, y - p.vy / speed * 9)
            pygame.draw.line(canvas, FORM_COLORS[key], tail, (x, y), 2)
        elif key == "feuerball":
            radius = 3 + (int(p.age * 20) % 2)
            pygame.draw.circle(canvas, (255, 150, 40), (x, y), radius)
            pygame.draw.circle(canvas, (255, 230, 150), (x, y), radius - 2)
        elif key == "knochenbombe":
            pygame.draw.circle(canvas, FORM_COLORS[key], (x, y), 4)
            pygame.draw.circle(canvas, (120, 110, 96), (x, y), 4, 1)
            if int(p.age * 10) % 2:
                canvas.fill((255, 80, 60), (x, y - 4, 1, 1))
        elif key in ("mikrofunke", "nadelregen"):
            canvas.fill(FORM_COLORS[key], (x, y, 1, 1))
        elif key == "leuchtkugel":
            glow = 2 + (int(p.age * 4) % 2)
            pygame.draw.circle(canvas, (255, 240, 180), (x, y), glow)
            canvas.fill((255, 255, 255), (x, y, 1, 1))
        elif key == "wandlungsdruese":
            hue = int(p.age * 30) % 3
            canvas.fill(((200, 80, 220), (80, 200, 220), (220, 200, 80))[hue], (x - 1, y - 1, 3, 3))
        elif key in ("tauschdruese", "kettenfunke"):
            color = (150, 200, 255) if key == "kettenfunke" else (220, 160, 255)
            canvas.fill(color, (x - 1, y, 3, 1))
            canvas.fill(color, (x, y - 1, 1, 3))
        elif key == "klumpen":
            material = p.material if p.material is not None else mat.BLOOD
            pygame.draw.circle(canvas, MATERIALS[material].color, (x, y), 2)
        else:
            color = FORM_COLORS.get(key, (255, 255, 255))
            if p.material is not None:
                color = MATERIALS[p.material].color
            canvas.fill(color, (x - 1, y - 1, 3, 3))


# ---------------------------------------------------------------- creatures

CREATURE_SPRITES: dict[str, tuple[tuple[str, ...], ...]] = {
    # Fleischmade: two crawl frames
    "made": (
        (
            "..pppppp..",
            ".pPpPpPpp.",
            "pPpPpPpPpm",
            "pPpPpPpPpm",
            ".pPpPpPpp.",
            "..pppppp..",
        ),
        (
            "..........",
            "..pppppp..",
            ".pPpPpPppm",
            "pPpPpPpPpm",
            "pPpPpPpPp.",
            ".pppppppp.",
        ),
    ),
    # Gallenschwärmer: wings up / wings down
    "schwaermer": (
        (
            "ww.....ww",
            ".ww...ww.",
            "..bbbbb..",
            ".bbBbbbbe",
            "..bbbbb..",
            "...b.b...",
            ".........",
        ),
        (
            ".........",
            "..bbbbb..",
            "wbbBbbbbe",
            "ww.bbb.ww",
            "w.......w",
            "...b.b...",
            ".........",
        ),
    ),
}
CREATURE_SPRITES["knochenspeier"] = (
    (
        "..kkkk..",
        ".kkKKkk.",
        "kkKKKKkk",
        "kkKddKkk",
        "kkKddKkk",
        ".kkKKkk.",
        "..k..k..",
    ),
    (
        "..kkkk..",
        ".kkKKkk.",
        "kkKddKkk",
        "kkddddkk",
        "kkKddKkk",
        ".kkKKkk.",
        "..k..k..",
    ),
)
CREATURE_SPRITES["sporenblase"] = (
    (
        "...sss...",
        ".ssSsSss.",
        ".sSsssSs.",
        "ssssSssss",
        "sSsssssSs",
        "ssssSssss",
        ".sSsssSs.",
        ".ssSsSss.",
        "...sss...",
    ),
    (
        ".........",
        "...sss...",
        ".ssSsSss.",
        "ssSsssSss",
        "sssssSsss",
        "ssSsssSss",
        ".ssSsSss.",
        "...sss...",
        ".........",
    ),
)
CREATURE_SPRITES["brandmade"] = (
    (
        "..oooooo..",
        ".oOoOoOoo.",
        "oOyOyOyOom",
        "oOoOoOoOom",
        ".oOoOoOoo.",
        "..oooooo..",
    ),
    (
        "..........",
        "..oooooo..",
        ".oOyOyOoom",
        "oOoOoOoOom",
        "oOoOoOoOo.",
        ".oooooooo.",
    ),
)
CREATURE_SPRITES["saeurespucker"] = (
    (
        "....bbb....",
        "..bbBBBbb..",
        ".bBbbbbbBe.",
        "bbBbbbbbBbg",
        "bBbbBBBbbBg",
        ".bbBbbbBbb.",
        "..bbbbbbb..",
        ".b.b...b.b.",
        "b...b.b...b",
    ),
    (
        "...........",
        "....bbb....",
        "..bbBBBbbe.",
        ".bBbbbbbBbg",
        "bbBbbbbbBbg",
        "bBbbBBBbbB.",
        ".bbbbbbbbb.",
        "..b.b.b.b..",
        ".b..b.b..b.",
    ),
)
CREATURE_SPRITES["egel"] = (
    (
        ".rrrr..",
        "rRrRrrd",
        "rrRrRrd",
        ".rrrr..",
    ),
    (
        "..rrr..",
        ".rRrRrd",
        "rrRrRrd",
        "rrrr...",
    ),
)
CREATURE_SPRITES["augenblase"] = (
    (
        "...ppppp...",
        "..pPPPPPp..",
        ".pPwwwwwPp.",
        "pPwwwiiwwPp",
        "pPwwiddiwPp",
        "pPwwiddiwPp",
        "pPwwwiiwwPp",
        ".pPwwwwwPp.",
        "..pPPPPPp..",
        "...p.p.p...",
        "..p..p..p..",
    ),
    (
        "...ppppp...",
        "..pPPPPPp..",
        ".pPwwwwwPp.",
        "pPwwwwwwwPp",
        "pPwwwiiwwPp",
        "pPwwiddiwPp",
        "pPwwwiiwwPp",
        ".pPwwwwwPp.",
        "..pPPPPPp..",
        "..p..p..p..",
        "...p.p.p...",
    ),
)
CREATURE_SPRITES["schleimkriecher"] = (
    (
        "....yyyyyyyy....",
        "..yyYyyYyyYyyy..",
        ".yYyyyyyyyyyyYy.",
        "yyyyYyyYyyyYyyde",
        "yYyyyyyyyyyyyyyd",
        "yyyYyyyYyyyYyyyy",
        ".yyyyyyyyyyyyyy.",
        "..YyYyYyYyYyYy..",
        "................",
    ),
    (
        "................",
        "...yyyyyyyyyy...",
        ".yyYyyYyyYyyyyy.",
        "yYyyyyyyyyyyyYde",
        "yyyyYyyYyyyYyyyd",
        "yYyyyyyyyyyyyyyy",
        "yyyYyyyYyyyYyyyy",
        ".YyYyYyYyYyYyYy.",
        "................",
    ),
)
CREATURE_SPRITES["nervenknoten"] = (
    (
        "n...n...n",
        ".n..n..n.",
        "..nNNNn..",
        "nnNyeyNnn",
        "..NeeeN..",
        "nnNyeyNnn",
        "..nNNNn..",
        ".n..n..n.",
        "n...n...n",
    ),
    (
        "....n....",
        "n...n...n",
        ".nnNNNnn.",
        "..NyeyN..",
        "nnNeeeNnn",
        "..NyeyN..",
        ".nnNNNnn.",
        "n...n...n",
        "....n....",
    ),
)
for _key, _skin in (("talgsack", "t"), ("saeuresack", "a"), ("sporensack", "s")):
    CREATURE_SPRITES[_key] = (
        (
            "...vv...",
            "..vvvv..",
            ".XxxxxX.",
            "XxxXxxxX",
            "XxxxxXxX",
            "XxXxxxxX",
            "XxxxXxxX",
            ".XxxxxX.",
            "..XXXX..",
        ),
        (
            "...vv...",
            "..vvvv..",
            ".XxxxxX.",
            "XxxxXxxX",
            "XxXxxxxX",
            "XxxxxXxX",
            "XxxXxxxX",
            ".XxxxxX.",
            "..XXXX..",
        ),
    )
    CREATURE_SPRITES[_key] = tuple(
        tuple(row.replace("x", _skin).replace("X", _skin.upper()) for row in frame)
        for frame in CREATURE_SPRITES[_key]
    )
CREATURE_SPRITES["gestaltwandler"] = (
    (
        "...nnnn...",
        "..nyyyyn..",
        ".nyNyyNyn.",
        "nyyyeeyyyn",
        "nyNyeeyNyn",
        "nyyyyyyyyn",
        ".nyNyyNyn.",
        "..nyyyyn..",
        "...n..n...",
        "..n....n..",
    ),
    (
        "...nnnn...",
        "..nyyyyn..",
        ".nyyNNyyn.",
        "nyNyeeyNyn",
        "nyyyeeyyyn",
        "nyNyyyyNyn",
        ".nyyNNyyn.",
        "..nyyyyn..",
        "..n....n..",
        "...n..n...",
    ),
)
CREATURE_COLORS = {
    "p": (214, 190, 170),
    "P": (168, 136, 124),
    "m": (120, 20, 30),
    "w": (176, 186, 176),
    "b": (112, 140, 52),
    "B": (78, 100, 36),
    "e": (232, 52, 40),
    "d": (30, 10, 12),
    "k": (190, 178, 150),
    "K": (150, 138, 112),
    "s": (164, 128, 160),
    "S": (124, 90, 130),
    "o": (196, 110, 60),
    "O": (150, 64, 30),
    "y": (180, 174, 118),
    "Y": (140, 134, 88),
    "r": (96, 20, 28),
    "R": (60, 10, 18),
    "g": (180, 230, 60),
    "i": (150, 40, 40),
    "n": (190, 140, 150),
    "N": (140, 90, 110),
    "t": (206, 184, 128),
    "T": (156, 134, 88),
    "a": (150, 206, 60),
    "A": (98, 140, 34),
    "v": (120, 60, 70),
}
FLASH_COLOR = (255, 255, 255)
HEALTH_BAR = (200, 30, 36)
RIM_COLOR = (255, 226, 214, 120)  # a thin light outline: creatures stay visible in the dark
EYE_GLOW = (255, 120, 90)
FRAME_RATES = {
    "made": 6.0, "schwaermer": 18.0, "knochenspeier": 1.5, "sporenblase": 3.0,
    "brandmade": 8.0, "saeurespucker": 4.0, "egel": 12.0, "augenblase": 1.2,
    "schleimkriecher": 2.5, "nervenknoten": 3.0,
    "talgsack": 1.0, "saeuresack": 1.0, "sporensack": 1.0, "gestaltwandler": 3.0,
}  # fmt: skip


def outline_cells(rows: tuple[str, ...]) -> list[tuple[int, int]]:
    """Empty cells next to a sprite's pixels (in a frame one pixel larger on every side)."""
    height, width = len(rows), len(rows[0])
    filled = {
        (x, y)
        for y, row in enumerate(rows)
        for x, code in enumerate(row)
        if code in CREATURE_COLORS
    }
    cells = []
    for y in range(-1, height + 1):
        for x in range(-1, width + 1):
            if (x, y) in filled:
                continue
            if any((x + dx, y + dy) in filled for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                cells.append((x + 1, y + 1))
    return cells


def build_creature_sprites() -> dict[tuple, pygame.Surface]:
    """Pre-render every (species, frame, facing right, flashing) combination.

    ``(species, frame, facing right, "rim")`` holds the light outline drawn behind the
    sprite, so dark creatures stand out against dark tissue (like in Noita).
    """
    sprites: dict[tuple, pygame.Surface] = {}
    for key, frames in CREATURE_SPRITES.items():
        for index, rows in enumerate(frames):
            for flashing in (False, True):
                surface = pygame.Surface((len(rows[0]), len(rows)), pygame.SRCALPHA)
                for y, row in enumerate(rows):
                    for x, code in enumerate(row):
                        if code in CREATURE_COLORS:
                            surface.set_at(
                                (x, y), FLASH_COLOR if flashing else CREATURE_COLORS[code]
                            )
                sprites[(key, index, True, flashing)] = surface
                sprites[(key, index, False, flashing)] = pygame.transform.flip(surface, True, False)
            rim = pygame.Surface((len(rows[0]) + 2, len(rows) + 2), pygame.SRCALPHA)
            for x, y in outline_cells(rows):
                rim.set_at((x, y), RIM_COLOR)
            sprites[(key, index, True, "rim")] = rim
            sprites[(key, index, False, "rim")] = pygame.transform.flip(rim, True, False)
    return sprites


def draw_creatures(
    canvas: pygame.Surface,
    sprites: dict[tuple[str, int, bool, bool], pygame.Surface] | None,
    creatures: list[Creature],
    cam_x: int,
    cam_y: int,
    visible: set[int] | None = None,
    sheet_cache: SheetCache | None = None,
) -> None:
    from src.procbody import RIG_LAYOUTS, ProcRig
    from src.sprite_render import blit_frame
    from src.sprites import Animator

    for creature in creatures:
        if visible is not None and id(creature) not in visible:
            continue  # hidden behind tissue
        key = creature.spec.key
        x, y = creature.x - cam_x, creature.y - cam_y

        # Sprite sheets and rigs where the sheet files exist; otherwise the legacy drawing
        if sheet_cache is not None and _has_sheets(sheet_cache, creature):
            facing_right = creature.facing >= 0
            is_windup = getattr(creature, "state", "") == "windup"
            flash = 1.0 if is_windup else (1.0 if getattr(creature, "flash", 0.0) > 0.0 else 0.0)

            anim_state = (
                getattr(creature, "anim_state", None) or getattr(creature, "state", None) or "idle"
            )

            # Boss with multi-part rig
            if key in RIG_LAYOUTS:
                rig = getattr(creature, "rig", None)
                if rig is None:
                    rig = ProcRig(RIG_LAYOUTS[key])
                for _part_key, wx, wy, sheet_name in rig.world_parts(
                    creature.x, creature.y, flip_x=not facing_right
                ):
                    category = _rig_category(sheet_cache, sheet_name)
                    sheet, meta = sheet_cache.get(category, sheet_name)
                    st = anim_state if anim_state in meta.anims else "idle"
                    anim = Animator(meta, st)
                    blit_frame(
                        canvas,
                        sheet,
                        meta,
                        anim,
                        wx,
                        wy,
                        cam_x,
                        cam_y,
                        flip_x=not facing_right,
                        flash=flash,
                    )
            else:
                sheet, meta = sheet_cache.get(_sheet_category(creature, sheet_cache), key)
                st = anim_state if anim_state in meta.anims else "idle"
                anim = Animator(meta, st)
                blit_frame(
                    canvas,
                    sheet,
                    meta,
                    anim,
                    creature.center[0],
                    creature.center[1],
                    cam_x,
                    cam_y,
                    flip_x=not facing_right,
                    flash=flash,
                )

            if creature.hp < creature.max_hp:
                width = max(1, round(creature.width * creature.hp / creature.max_hp))
                canvas.fill(HEALTH_BAR, (x, y - 3, width, 1))
            continue

        # Legacy software fallback
        if key == "magenwurm":
            _draw_worm(canvas, creature, x, y)
            continue
        if key == "herz":
            _draw_heart(canvas, creature, x, y)
            continue
        if key == "brutmutter":
            _draw_brood_mother(canvas, creature, x, y)
            continue
        if key == "knochenfresser":
            _draw_bone_eater(canvas, creature, x, y)
            continue
        if key == "atem":
            _draw_breath(canvas, creature, x, y)
            continue
        if sprites is not None and key in CREATURE_SPRITES and key in FRAME_RATES:
            frame = int(creature.age * FRAME_RATES[key]) % len(CREATURE_SPRITES[key])
            facing = creature.facing > 0
            rim = sprites.get((key, frame, facing, "rim"))
            if rim is not None:
                canvas.blit(rim, (x - 1, y - 1))
            sprite = sprites.get((key, frame, facing, creature.flash > 0))
            if sprite is not None:
                canvas.blit(sprite, (x, y))
        else:  # no sheet and no legacy sprite: never leave a creature invisible
            _draw_placeholder(canvas, creature, x, y)
        if creature.hp < creature.max_hp:
            width = max(1, round(creature.width * creature.hp / creature.max_hp))
            canvas.fill(HEALTH_BAR, (x, y - 3, width, 1))


PLACEHOLDER_FILL = (190, 70, 170)
PLACEHOLDER_EDGE = (40, 10, 40)


SHEET_CATEGORIES = ("kreaturen", "bosse", "charaktere", "umgebung")  # umgebung: the dummy


def _sheet_category(creature: Creature, cache: SheetCache | None = None) -> str:
    """Folder of the creature's sheet: the first one that holds it (mid-bosses are not
    flagged as bosses but live in bosse/), else a guess from the key."""
    key = creature.spec.key
    if cache is not None:
        for category in SHEET_CATEGORIES:
            if _has_file(cache, category, key):
                return category
    if key.startswith(("agent_", "boese_")) or key == "ober_cloita":
        return "charaktere"
    return "bosse" if getattr(creature.spec, "boss", False) else "kreaturen"


def _has_file(cache: SheetCache, category: str, name: str) -> bool:
    return (cache.root / category / f"{name}.png").is_file()


def _rig_category(cache: SheetCache, name: str) -> str:
    return "bosse" if _has_file(cache, "bosse", name) else "kreaturen"


def _has_sheets(cache: SheetCache, creature: Creature) -> bool:
    """True if every sheet this creature is drawn from exists on disk."""
    from src.procbody import RIG_LAYOUTS

    key = creature.spec.key
    if key in RIG_LAYOUTS:
        return all(
            _has_file(cache, _rig_category(cache, part.sheet_name), part.sheet_name)
            for part in RIG_LAYOUTS[key].parts
        )
    return _has_file(cache, _sheet_category(creature, cache), key)


def _draw_placeholder(canvas: pygame.Surface, creature: Creature, x: int, y: int) -> None:
    rect = pygame.Rect(x, y, max(2, creature.width), max(2, creature.height))
    canvas.fill(PLACEHOLDER_FILL, rect)
    pygame.draw.rect(canvas, PLACEHOLDER_EDGE, rect, 1)


WORM_SKIN = (150, 168, 92)
WORM_DARK = (96, 114, 58)
WORM_MOUTH = (60, 10, 14)
TEETH = (230, 220, 190)
HEART_DARK = (110, 14, 26)
HEART_LIGHT = (176, 34, 48)
VEIN = (70, 20, 60)


def _draw_worm(canvas: pygame.Surface, worm: Creature, x: int, y: int) -> None:
    """Segmented body undulating behind a toothed mouth."""
    cy = y + worm.height / 2
    head_x = x + (worm.width - 6 if worm.facing > 0 else 6)
    flash = worm.flash > 0
    segments = 7
    for index in range(segments - 1, -1, -1):
        t = index / (segments - 1)
        sx = head_x - worm.facing * t * (worm.width - 10)
        sy = cy + math.sin(worm.age * 9 - index * 0.9) * 2.5
        radius = 6 - 3 * t
        color = FLASH_COLOR if flash else (WORM_SKIN if index % 2 else WORM_DARK)
        pygame.draw.circle(canvas, color, (sx, sy), radius)
    mouth_x = head_x + worm.facing * 3
    pygame.draw.circle(canvas, WORM_MOUTH, (mouth_x, cy), 3)
    for k in (-2, 0, 2):
        canvas.fill(TEETH, (int(mouth_x + worm.facing * 2), int(cy + k), 1, 1))


def _draw_heart(canvas: pygame.Surface, heart: Creature, x: int, y: int) -> None:
    """A pulsing heart with veins; beats faster when wounded."""
    health = heart.hp / heart.max_hp
    beat = math.sin(heart.age * (5 + 6 * (1 - health))) ** 8
    scale = 1.0 + 0.08 * beat
    cx, cy = x + heart.width / 2, y + heart.height / 2
    w, h = heart.width * scale, heart.height * scale
    dark = FLASH_COLOR if heart.flash > 0 else HEART_DARK
    pygame.draw.circle(canvas, dark, (cx - w * 0.22, cy - h * 0.15), w * 0.3)
    pygame.draw.circle(canvas, dark, (cx + w * 0.2, cy - h * 0.12), w * 0.32)
    pygame.draw.polygon(
        canvas,
        dark,
        [
            (cx - w * 0.5, cy - h * 0.1),
            (cx + w * 0.5, cy - h * 0.05),
            (cx + w * 0.05, cy + h * 0.5),
        ],
    )
    pygame.draw.circle(canvas, HEART_LIGHT, (cx + w * 0.12, cy - h * 0.22), w * 0.12)
    for k in range(4):  # veins
        start = (cx - w * 0.3 + k * w * 0.18, cy - h * 0.3)
        end = (cx - w * 0.15 + k * w * 0.1, cy + h * 0.25)
        pygame.draw.line(canvas, VEIN, start, end)
    pygame.draw.rect(canvas, (90, 70, 80), (cx - 4, y - 8, 8, 10))  # aorta stump


def _draw_bone_eater(canvas: pygame.Surface, eater: Creature, x: int, y: int) -> None:
    """A segmented maw of grinding jaws."""
    flash = eater.flash > 0
    cy = y + eater.height / 2
    head_x = x + (eater.width - 9 if eater.facing > 0 else 9)
    for index in range(5, -1, -1):
        sx = head_x - eater.facing * index * 4
        sy = cy + math.sin(eater.age * 7 - index) * 2
        radius = 9 - index
        color = FLASH_COLOR if flash else ((196, 184, 156) if index % 2 else (150, 138, 112))
        pygame.draw.circle(canvas, color, (sx, sy), radius)
    grind = math.sin(eater.age * 16) * 2
    for k in range(-3, 4, 2):
        tip = (head_x + eater.facing * (10 + abs(k)), cy + k * 2 + grind * (1 if k > 0 else -1))
        pygame.draw.line(canvas, TEETH, (head_x + eater.facing * 5, cy + k * 2), tip)
    pygame.draw.circle(canvas, (40, 8, 12), (head_x + eater.facing * 3, cy), 3)


def _draw_breath(canvas: pygame.Surface, breath: Creature, x: int, y: int) -> None:
    """Two lung lobes that swell while inhaling and collapse when breathing out."""
    flash = breath.flash > 0
    swell = 1.15 if breath.inhaling else 0.95 + 0.05 * math.sin(breath.age * 3)
    cx, cy = x + breath.width / 2, y + breath.height / 2
    w, h = breath.width * 0.5 * swell, breath.height * swell
    lobe = FLASH_COLOR if flash else (196, 120, 130)
    dark = (130, 64, 76)
    for side in (-1, 1):
        rect = (cx + side * w * 0.55 - w / 2, cy - h / 2, w, h)
        pygame.draw.ellipse(canvas, dark, (rect[0] - 1, rect[1] - 1, rect[2] + 2, rect[3] + 2))
        pygame.draw.ellipse(canvas, lobe, rect)
        for k in range(3):  # bronchi
            pygame.draw.line(
                canvas,
                dark,
                (cx, cy - h * 0.3),
                (cx + side * w * (0.3 + k * 0.2), cy + h * (k * 0.15)),
            )
    pygame.draw.rect(canvas, (160, 140, 150), (cx - 2, y - 8, 4, 12))  # windpipe
    if breath.inhaling:
        for k in range(4):  # air rushing in
            a = breath.age * 5 + k * 1.6
            r = 30 - (breath.age * 40 + k * 7) % 25
            canvas.fill(
                (200, 190, 180), (int(cx + math.cos(a) * r), int(cy + math.sin(a) * r), 1, 1)
            )


BROOD_SKIN = (128, 104, 96)
BROOD_DARK = (84, 60, 62)
BROOD_SAC = (170, 150, 92)
BROOD_EMBRYO = (70, 36, 40)
BROOD_EYE = (210, 190, 120)


def _draw_brood_mother(canvas: pygame.Surface, mother: Creature, x: int, y: int) -> None:
    """A swollen sac body carrying egg sacs, dangling tendrils below."""
    flash = mother.flash > 0
    cx, cy = x + mother.width / 2, y + mother.height / 2
    breath = 1.0 + 0.05 * math.sin(mother.age * 3)
    for k in range(5):  # tendrils
        tx = x + 5 + k * (mother.width - 10) / 4
        sway = math.sin(mother.age * 4 + k) * 3
        pygame.draw.line(canvas, BROOD_DARK, (tx, cy + 6), (tx + sway, y + mother.height + 6), 2)
    body = FLASH_COLOR if flash else BROOD_SKIN
    w, h = mother.width * breath, mother.height * 0.8 * breath
    pygame.draw.ellipse(canvas, BROOD_DARK, (cx - w / 2 - 1, cy - h / 2 - 1, w + 2, h + 2))
    pygame.draw.ellipse(canvas, body, (cx - w / 2, cy - h / 2, w, h))
    for k, (ox, oy) in enumerate(((-0.28, 0.05), (0.0, 0.18), (0.27, 0.02))):  # egg sacs
        sx, sy = cx + ox * mother.width, cy + oy * mother.height
        radius = 4.5 + math.sin(mother.age * 2 + k * 2) * 0.8
        pygame.draw.circle(canvas, BROOD_SAC, (sx, sy), radius)
        pygame.draw.circle(canvas, BROOD_EMBRYO, (sx + 0.5, sy + 0.5), radius * 0.45)
    eye_x = cx + mother.facing * mother.width * 0.3
    pygame.draw.circle(canvas, BROOD_EYE, (eye_x, cy - h * 0.25), 2.5)
    canvas.fill((20, 6, 8), (int(eye_x), int(cy - h * 0.25), 1, 1))


# ------------------------------------------------------------------- items

EXIT_COLOR = (40, 6, 12)
EXIT_RIM = (150, 40, 52)
EXIT_CLOSED = (70, 60, 64)


PEARL_COLOR = (190, 20, 36)
PEARL_GLINT = (255, 200, 200)


GLASS = (196, 210, 214)
COCOON = (170, 150, 120)
COCOON_DARK = (110, 88, 70)


def draw_flask(canvas: pygame.Surface, flask: Flask, x: int, y: int) -> None:
    """A small bottle; the liquid level shows how full it is."""
    pygame.draw.rect(canvas, GLASS, (x - 3, y - 6, 7, 7), 1)
    canvas.fill(GLASS, (x - 1, y - 9, 3, 3))
    if not flask.empty:
        level = max(1, round(5 * flask.amount / FLASK_CAPACITY))
        canvas.fill(MATERIALS[flask.material].color, (x - 2, y - level, 5, level))


KLONITA_FALLBACK = (176, 120, 230)  # a lilac blob if her sheet is missing


def klonita_anim(klonita: object) -> str:
    """Which row of her sheet fits her state right now."""
    state = getattr(klonita, "state", "follow")
    if state in ("knocked", "assist", "quirk"):
        return state
    moving = abs(getattr(klonita, "vx", 0.0)) > 6.0 or abs(getattr(klonita, "vy", 0.0)) > 6.0
    return "fly" if moving else "idle"


def draw_klonita(
    canvas: pygame.Surface,
    sheet_cache: object,
    klonita: object,
    animator: object | None,
    cam_x: float,
    cam_y: float,
    time: float = 0.0,
) -> object | None:
    """Draw Klonita (and where she points) onto ``canvas``; returns the animator to keep.

    ``klonita.x/y`` is her centre; her sheet is anchored at the feet."""
    from src.sprite_render import blit_frame
    from src.sprites import Animator

    if klonita is None or getattr(klonita, "state", "") == "dismissed":
        return animator
    x, y = float(klonita.x), float(klonita.y)
    pointing = getattr(klonita, "pointing", None)
    if pointing is not None and getattr(klonita, "point_timer", 0.0) > 0:
        px, py = int(pointing[0] - cam_x), int(pointing[1] - cam_y)
        radius = 5 + int(2 * math.sin(time * 8))
        pygame.draw.circle(canvas, (230, 200, 255), (px, py), radius, 1)
        pygame.draw.line(canvas, (200, 160, 240), (int(x - cam_x), int(y - cam_y)), (px, py), 1)
    try:
        sheet, meta = sheet_cache.get("charaktere", "klonita")  # type: ignore[attr-defined]
        anim = klonita_anim(klonita)
        anim = anim if anim in meta.anims else "idle"
        if animator is None or getattr(animator, "meta", None) is not meta:
            animator = Animator(meta, anim)
        animator.play(anim)
        animator.update(1 / 60)
        blit_frame(
            canvas, sheet, meta, animator, x, y + meta.frame_size[1] / 2 - 2, cam_x, cam_y,
            flip_x=getattr(klonita, "facing", 1) < 0,
        )  # fmt: skip
    except (KeyError, ValueError, AttributeError, TypeError, OSError, pygame.error):
        sx, sy = int(x - cam_x), int(y - cam_y)
        pygame.draw.circle(canvas, KLONITA_FALLBACK, (sx, sy), 5)
        pygame.draw.circle(canvas, (30, 16, 40), (sx - 2 * getattr(klonita, "facing", 1), sy - 1), 1)
    return animator


def draw_chunks(canvas: pygame.Surface, chunks: list[Chunk], cam_x: int, cam_y: int) -> None:
    """Falling tissue: drawn cell by cell in its material's colour (slightly lit)."""
    width, height = VIEW_WIDTH, VIEW_HEIGHT
    for chunk in chunks:
        for x, y, material in chunk.cells:
            sx, sy = x - cam_x, y - cam_y
            if 0 <= sx < width and 0 <= sy < height:
                canvas.fill(CHUNK_COLORS[material], (sx, sy, 1, 1))


CHUNK_COLORS: list[tuple[int, int, int]] = []


def _chunk_colors() -> None:
    CHUNK_COLORS[:] = [shade(variant_color(m, 1), LIGHT_LEVELS - 2) for m in MATERIALS]


mat.subscribe(_chunk_colors)


def draw_droplets(canvas: pygame.Surface, droplets: list, cam_x: int, cam_y: int) -> None:
    """Squirted liquid in flight."""
    for drop in droplets:
        x, y = int(drop.x) - cam_x, int(drop.y) - cam_y
        if 0 <= x < VIEW_WIDTH and 0 <= y < VIEW_HEIGHT:
            canvas.fill(MATERIALS[drop.material].color, (x, y, 1, 1))


def draw_thrown_flasks(
    canvas: pygame.Surface, thrown: list[ThrownFlask], cam_x: int, cam_y: int
) -> None:
    for item in thrown:
        draw_flask(canvas, item.flask, int(item.x) - cam_x, int(item.y) - cam_y + 4)


NEW_MARK = (255, 236, 150)


def draw_pickups(
    canvas: pygame.Surface,
    pickups: list[Pickup],
    cam_x: int,
    cam_y: int,
    known: set[str] | None = None,
) -> None:
    """Items in the world; blocks not yet in the Kodex sparkle (``known`` = Kodex)."""
    for item in pickups:
        if not item.seen:
            continue
        x, y = int(item.x) - cam_x, int(item.y) - cam_y
        bob = round(math.sin(item.age * 3) * 1.5)
        if item.pearls:
            for k in range(min(4, 1 + item.pearls // 8)):
                px, py = x - 2 + (k % 2) * 3, y - 2 - (k // 2) * 2
                canvas.fill(PEARL_COLOR, (px, py, 2, 2))
            if int(item.age * 2) % 3 == 0:
                canvas.fill(PEARL_GLINT, (x - 2, y - 3, 1, 1))
            continue
        if item.perk is not None:
            color = PERK_BY_KEY[item.perk].color
            radius = 4 + math.sin(item.age * 4)
            pygame.draw.circle(canvas, color, (x, y + bob), radius)
            pygame.draw.circle(canvas, (255, 240, 230), (x - 1, y - 1 + bob), 1)
            continue
        if item.flask is not None:
            draw_flask(canvas, item.flask, x, y + bob)
            continue
        if item.heart:
            beat = 1 if math.sin(item.age * 7) > 0.6 else 0
            pygame.draw.circle(canvas, HEART_DARK, (x - 2, y - 4 + bob), 2 + beat)
            pygame.draw.circle(canvas, HEART_DARK, (x + 2, y - 4 + bob), 2 + beat)
            pygame.draw.polygon(
                canvas, HEART_LIGHT, [(x - 4, y - 3 + bob), (x + 4, y - 3 + bob), (x, y + 1 + bob)]
            )
            continue
        if item.portal:
            for k in range(3):
                radius = 9 - k * 3 + math.sin(item.age * 3 + k) * 1.5
                color = ((120, 200, 230), (190, 120, 230), (240, 240, 255))[k]
                pygame.draw.circle(canvas, color, (x, y), max(1, radius), 1)
            continue
        if item.reroll:
            spin = item.age * 2
            for k in range(3):
                a = spin + k * 2.1
                color = PERK_BY_KEY[PERK_KEYS[(int(item.age) + k) % len(PERK_KEYS)]].color
                pygame.draw.circle(
                    canvas, color, (x + math.cos(a) * 4, y + bob + math.sin(a) * 4), 2
                )
            pygame.draw.circle(canvas, (90, 30, 40), (x, y + bob), 2)
            continue
        if item.eye:
            look = math.sin(item.age * 0.8) * 1.5
            pygame.draw.circle(canvas, (232, 222, 206), (x, y + bob), 5)
            pygame.draw.circle(canvas, (170, 30, 40), (x + look, y + bob), 3)
            pygame.draw.circle(canvas, (10, 4, 6), (x + look, y + bob), 1)
            pygame.draw.circle(canvas, (120, 40, 50), (x, y + bob), 5, 1)
            continue
        if item.cocoon:
            sway = math.sin(item.age * 1.5) * 1.5
            pygame.draw.ellipse(canvas, COCOON, (x - 5 + sway, y - 13, 10, 13))
            pygame.draw.ellipse(canvas, COCOON_DARK, (x - 5 + sway, y - 13, 10, 13), 1)
            pygame.draw.line(canvas, COCOON_DARK, (x - 2 + sway, y - 10), (x + 2 + sway, y - 4))
            continue
        if item.wand is not None:
            pygame.draw.line(canvas, ARM_FLESH, (x - 5, y - 2 + bob), (x + 5, y - 4 + bob), 2)
            for k, key in enumerate(item.wand.blocks[:5]):
                color = _mix(block_color(CATALOG[key]), ARM_FLESH, NODE_FLESH_MIX)
                canvas.fill(color, (x - 4 + k * 2, y - 3 + bob - k // 3, 2, 2))
        elif item.block in CATALOG:  # gold, samples & co. carry no block
            color = block_color(CATALOG[item.block])
            unknown = known is not None and item.block not in known
            if unknown:  # a pulsing golden frame and a spark: something new
                glow = 0.5 + 0.5 * math.sin(item.age * 6)
                frame = _mix(NEW_MARK, (90, 60, 30), 1 - glow)
                pygame.draw.rect(canvas, frame, (x - 4, y - 7 + bob, 9, 9), 1)
                canvas.fill(NEW_MARK, (x, y - 10 + bob - round(glow), 1, 2))
            pygame.draw.rect(canvas, (30, 16, 20), (x - 3, y - 6 + bob, 7, 7))
            canvas.fill(color, (x - 2, y - 5 + bob, 5, 5))


def draw_exit(
    canvas: pygame.Surface,
    centre: tuple[int, int],
    is_open: bool,
    age: float,
    cam_x: int,
    cam_y: int,
) -> None:
    """The way down: a pulsing sphincter that only opens when the depth is cleared."""
    x, y = centre[0] - cam_x, centre[1] - cam_y
    pulse = 1 + 0.15 * math.sin(age * 4)
    rim = EXIT_RIM if is_open else EXIT_CLOSED
    pygame.draw.circle(canvas, rim, (x, y), 11 * pulse)
    pygame.draw.circle(canvas, EXIT_COLOR, (x, y), (8 if is_open else 3) * pulse)


# ------------------------------------------------------------------ status

DRIP_COLOR = (150, 20, 30)


def draw_status(canvas: pygame.Surface, body, cam_x: int, cam_y: int, rng: random.Random) -> None:
    """Flames on burning bodies, drips on wet ones."""
    x, y = body.x - cam_x, body.y - cam_y
    if body.burning > 0:
        for _ in range(4):
            fx = x + rng.randrange(body.width)
            fy = y + rng.randrange(max(1, body.height // 2)) - 2
            canvas.fill(rng.choice(FIRE_TONES), (fx, fy, 1, 1 + rng.randrange(2)))
    elif body.wet > 0 and rng.random() < 0.3:
        canvas.fill(DRIP_COLOR, (x + rng.randrange(body.width), y + body.height, 1, 1))
    if body.oily > 0 and rng.random() < 0.25:  # a greasy sheen
        canvas.fill(
            MATERIALS[mat.TALLOW].color,
            (x + rng.randrange(body.width), y + rng.randrange(body.height), 1, 1),
        )
    if body.slimed > 0 and rng.random() < 0.4:
        canvas.fill(
            MATERIALS[mat.MUCUS].color, (x + rng.randrange(body.width), y + body.height - 1, 1, 2)
        )


class Renderer:
    """High-level run renderer facade for world and HUD (Card B32; HUD parts G01/G02)."""

    def __init__(self, screen: pygame.Surface) -> None:
        from src.sprite_render import SheetCache

        self.screen = screen
        self.sheet_cache = SheetCache()
        self.hud = None

    def draw(self, run: object) -> None:
        """Render the run state: world, creatures, pickups, player, klonita, and HUD."""
        from src.hud import Hud, HudState
        from src.sprite_render import blit_frame
        from src.sprites import Animator
        from src.viewport import Viewport

        screen = self.screen
        sw, sh = screen.get_size()

        # Determine camera position
        player = getattr(run, "player", None)
        if player is not None:
            cam_x = int(player.x - sw // 2)
            cam_y = int(player.y - sh // 2)
        else:
            cam_x, cam_y = 0, 0

        # 1. World chunks
        chunks = getattr(run, "chunks", None)
        if chunks is not None and hasattr(chunks, "items"):
            draw_chunks(screen, chunks.items, cam_x, cam_y)

        # 2. Pickups
        pickups = getattr(run, "pickups", None)
        if pickups is not None:
            known = getattr(run, "known_blocks", None)
            draw_pickups(screen, pickups, cam_x, cam_y, known)

        # 3. Creatures (safe fallback)
        enemies = getattr(run, "enemies", None)
        if enemies is not None and hasattr(enemies, "creatures"):
            try:
                draw_creatures(
                    screen, None, enemies.creatures, cam_x, cam_y, sheet_cache=self.sheet_cache
                )
            except (KeyError, ValueError, AttributeError, pygame.error):
                pass

        # 4. Player sprite
        if player is not None:
            try:
                sheet, meta = self.sheet_cache.get("charaktere", "spielerin")
                if player.dead:
                    anim_state = "dead"
                elif getattr(player, "damage_taken", 0) > 0:
                    anim_state = "hurt"
                elif getattr(player, "vy", 0.0) < -1.0:
                    anim_state = "jump"
                elif getattr(player, "vy", 0.0) > 1.0:
                    anim_state = "fall"
                elif abs(getattr(player, "vx", 0.0)) > 0.5:
                    anim_state = "walk"
                else:
                    anim_state = "idle"

                anim_state = anim_state if anim_state in meta.anims else "idle"
                facing_right = (
                    getattr(player, "facing", 1) >= 0 if hasattr(player, "facing") else True
                )
                animator = Animator(meta, anim_state)
                blit_frame(
                    screen,
                    sheet,
                    meta,
                    animator,
                    player.x,
                    player.y,
                    cam_x,
                    cam_y,
                    flip_x=not facing_right,
                )
            except (KeyError, ValueError, AttributeError, pygame.error):
                pass

        # 5. Klonita
        self.klonita_animator = draw_klonita(
            screen, self.sheet_cache, getattr(run, "klonita", None),
            getattr(self, "klonita_animator", None), cam_x, cam_y,
        )  # fmt: skip

        # 6. HUD
        try:
            if not pygame.font.get_init():
                pygame.font.init()
            if self.hud is None:
                self.hud = Hud()
            vp = Viewport(sw, sh)
            vp.resize(sw, sh)
            depth_name = getattr(getattr(run, "depth", None), "name_de", "")
            state = HudState(
                player=player,
                inventory=getattr(run, "inventory", None),
                depth_name=depth_name,
                depth_number=getattr(run, "next_depth_number", 1),
                depth_total=getattr(run, "depth_total", 6),
                fps=60.0,
            )
            self.hud.draw(screen, vp, state)
        except (KeyError, ValueError, AttributeError, pygame.error):
            pass

        # 7. Speech bubbles and the boss banner (Card G02)
        from src.hud import draw_boss_banner, draw_speech_bubbles
        from src import ui

        draw_speech_bubbles(screen, ui.font(12), getattr(run, "bubbles", []), cam_x, cam_y)
        draw_boss_banner(screen, ui.font(18, bold=True), getattr(run, "boss_banner", None))
