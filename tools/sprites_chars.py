"""Contract V8: Character, companion, authority agent, evil self, and trader sprite builders (Cards B01..B05)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from tools.palette import ENTITY_PALETTES
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)


def _draw_char_frame(palette_key: str, offset_y: int = 0, cast_arm: bool = False) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    pal = ENTITY_PALETTES.get(palette_key, ENTITY_PALETTES["spielerin"])
    # Cloak / coat body
    draw_shaded_rect(c, 4, 10 + offset_y, 16, 21, pal["primary"])
    # Hood / head
    draw_shaded_ellipse(c, 10, 6 + offset_y, 5, 5, pal["secondary"])
    # Face visor / shadow inside hood
    draw_shaded_rect(c, 7, 6 + offset_y, 13, 8 + offset_y, pal["accent"])
    # Casting arm / wand or hands
    if cast_arm:
        draw_shaded_rect(c, 14, 11 + offset_y, 18, 14 + offset_y, pal["secondary"])
        c.set_px(18, 12 + offset_y, (255, 255, 255, 255))
    else:
        c.set_px(15, 13 + offset_y, pal["accent"].light)
    apply_dark_outline(c)
    return c


def build_player_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/spielerin.{png,json} (Card B01)."""
    idle_frames = [_draw_char_frame("spielerin", y) for y in (0, 1, 0, -1)]
    walk_frames = [_draw_char_frame("spielerin", y) for y in (0, -1, 0, 1, 0, -1)]
    jump_frames = [_draw_char_frame("spielerin", -2), _draw_char_frame("spielerin", -1)]
    fall_frames = [_draw_char_frame("spielerin", 1), _draw_char_frame("spielerin", 2)]
    cast_frames = [
        _draw_char_frame("spielerin", cast_arm=True),
        _draw_char_frame("spielerin", -1, cast_arm=True),
        _draw_char_frame("spielerin", cast_arm=True),
    ]
    hurt_frames = [_draw_char_frame("spielerin", 1), _draw_char_frame("spielerin", 0)]
    dead_frames = [_draw_char_frame("spielerin", 3)]

    anims = {
        "idle": idle_frames,
        "walk": walk_frames,
        "jump": jump_frames,
        "fall": fall_frames,
        "cast": cast_frames,
        "hurt": hurt_frames,
        "dead": dead_frames,
    }
    glow = [{"offset": [14, 12], "color": [220, 220, 255], "radius": 12}]
    png_path, json_path = save_sheet(
        "charaktere",
        "spielerin",
        anims,
        anchor=(10, 22),
        fps={"idle": 6.0, "walk": 8.0, "cast": 10.0, "hurt": 8.0},
        glow=glow,
        out_dir=out_dir,
    )
    return [png_path, json_path]


def _draw_klonita_frame(offset_y: int = 0, lantern_wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 22)
    pal = ENTITY_PALETTES["klonita"]
    # Floating hem robe
    draw_shaded_rect(c, 3, 9 + offset_y, 14, 19 + offset_y, pal["primary"])
    # Head
    draw_shaded_ellipse(c, 9, 6 + offset_y, 4, 4, pal["secondary"])
    # Crooked witch hat
    draw_shaded_rect(c, 2, 4 + offset_y, 15, 6 + offset_y, pal["secondary"])
    draw_shaded_rect(
        c, 5 + lantern_wave, 1 + offset_y, 11 + lantern_wave, 4 + offset_y, pal["primary"]
    )
    # Purple glowing lantern
    draw_shaded_rect(c, 12, 11 + offset_y, 16, 15 + offset_y, pal["accent"])
    c.set_px(14, 13 + offset_y, (200, 100, 255, 255))
    apply_dark_outline(c)
    return c


def build_klonita_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/klonita.{png,json} (Card B02)."""
    idle_frames = [_draw_klonita_frame(y, w) for y, w in ((0, 0), (-1, 1), (0, 0), (1, -1))]
    fly_frames = [_draw_klonita_frame(y, 0) for y in (-1, -2, -1, 0)]
    assist_frames = [_draw_klonita_frame(0, w) for w in (1, 2, 1)]
    quirk_frames = [_draw_klonita_frame(y, w) for y, w in ((0, -1), (1, -2), (0, 0))]
    knocked_frames = [_draw_klonita_frame(2, -1), _draw_klonita_frame(3, 0)]

    anims = {
        "idle": idle_frames,
        "fly": fly_frames,
        "assist": assist_frames,
        "quirk": quirk_frames,
        "knocked": knocked_frames,
    }
    glow = [{"offset": [14, 13], "color": [200, 100, 255], "radius": 14}]
    png_path, json_path = save_sheet(
        "charaktere",
        "klonita",
        anims,
        anchor=(9, 20),
        fps={"idle": 5.0, "fly": 8.0, "assist": 8.0, "quirk": 6.0, "knocked": 6.0},
        glow=glow,
        out_dir=out_dir,
    )
    return [png_path, json_path]


def build_agent_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/agent_*.{png,json} (Card B03)."""
    raise NotImplementedError("Card B03")


def build_evil_and_hq_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/boese_* and ober_cloita sheets (Card B04)."""
    raise NotImplementedError("Card B04")


def build_trader_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/npc_*.{png,json} (Card B05)."""
    raise NotImplementedError("Card B05")
