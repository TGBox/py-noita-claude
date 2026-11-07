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
