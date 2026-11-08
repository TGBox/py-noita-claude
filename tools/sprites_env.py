"""Contract V8: Workshop station, prop, and particle sprite builders (Cards B28..B31)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from tools.palette import UNIVERSE_PALETTES, make_ramp
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

# Station dimensions (Bible 07):
# ws_portal: 40x48
# ws_werkbank: 48x28
# ws_fabrikator: 40x40
# ws_liege: 48x24
# ws_haendler: 72x32
# ws_zapfhahn: 16x24

WOOD_RAMP = make_ramp((130, 85, 45))
METAL_RAMP = make_ramp((120, 130, 145))
BRASS_RAMP = make_ramp((190, 150, 45))
PORTAL_RAMP = make_ramp((80, 140, 220))
CLOTH_RAMP = make_ramp((160, 50, 60))
GLOW_RAMP = make_ramp((100, 220, 240))
FLESH_RAMP = make_ramp((170, 70, 80))


def _draw_ws_portal(active: bool = False, frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(40, 48)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Outer stone/metal arch
    draw_shaded_rect(c, 2, 4, 37, 47, METAL_RAMP)
    draw_shaded_ellipse(c, 20, 14, 18, 12, BRASS_RAMP)
    # Portal inner cavity
    draw_shaded_rect(c, 8, 14, 31, 47, PORTAL_RAMP if active else pal["primary"])
    draw_shaded_ellipse(c, 20, 18, 12, 10, pal["glow"] if active else pal["secondary"])
    # Shimmer/pulse
    if active:
        pulse_r = (frame % 3) * 2 + 6
        draw_shaded_ellipse(c, 20, 26, pulse_r, pulse_r + 4, GLOW_RAMP)
    apply_dark_outline(c)
    return c


def _draw_ws_werkbank(active: bool = False, frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(48, 28)
    # Sturdy wooden workbench tabletop
    draw_shaded_rect(c, 2, 6, 45, 14, WOOD_RAMP)
    # Metal legs
    draw_shaded_rect(c, 4, 14, 10, 27, METAL_RAMP)
    draw_shaded_rect(c, 37, 14, 43, 27, METAL_RAMP)
    draw_shaded_rect(c, 8, 22, 39, 25, WOOD_RAMP)
    # Tools on top (vise, hammer/blueprints)
    draw_shaded_rect(c, 6, 2, 12, 6, METAL_RAMP)
    draw_shaded_rect(c, 20, 3, 30, 6, BRASS_RAMP)
    if active:
        # Spark or light
        c.set_px(24 + frame, 3, (255, 240, 120, 255))
        c.set_px(25 + frame, 4, (255, 180, 50, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_fabrikator(active: bool = False, frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(40, 40)
    # Big smoking industrial casing
    draw_shaded_rect(c, 4, 10, 35, 39, METAL_RAMP)
    # Funnel / hopper on top
    draw_shaded_rect(c, 10, 2, 29, 10, BRASS_RAMP)
    # Output hatch at the bottom
    draw_shaded_rect(c, 12, 26, 27, 36, make_ramp((50, 55, 65)))
    # Indicator lights / smoke
    c.set_px(8, 14, (240, 50, 50, 255) if not active else (50, 240, 80, 255))
    c.set_px(8, 18, (240, 200, 50, 255))
    if active:
        # Steam / smoke puff from funnel
        c.set_px(16 + (frame % 2) * 4, 0, (210, 210, 220, 200))
        c.set_px(18 + (frame % 3) * 2, 1, (230, 230, 240, 220))
    apply_dark_outline(c)
    return c


def _draw_ws_liege(active: bool = False, frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(48, 24)
    # Medical examination couch
    draw_shaded_rect(c, 4, 6, 43, 14, CLOTH_RAMP)
    # Pillow / headrest
    draw_shaded_rect(c, 34, 4, 43, 8, make_ramp((200, 70, 80)))
    # Metal base and stand legs
    draw_shaded_rect(c, 8, 14, 12, 23, METAL_RAMP)
    draw_shaded_rect(c, 35, 14, 39, 23, METAL_RAMP)
    draw_shaded_rect(c, 10, 18, 37, 21, METAL_RAMP)
    # Restraint straps or bio-monitors
    draw_shaded_rect(c, 16, 5, 18, 14, make_ramp((40, 30, 30)))
    draw_shaded_rect(c, 26, 5, 28, 14, make_ramp((40, 30, 30)))
    if active:
        # Glowing bio-fluids or monitor pulse
        c.set_px(22 + (frame % 4), 8, (120, 240, 180, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_haendler(active: bool = False, frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(72, 32)
    # Wide trader stall counter
    draw_shaded_rect(c, 4, 12, 67, 31, WOOD_RAMP)
    # Striped awning / roof over stall
    draw_shaded_rect(c, 2, 2, 69, 10, CLOTH_RAMP)
    for x in range(6, 68, 12):
        draw_shaded_rect(c, x, 2, x + 5, 10, BRASS_RAMP)
    # Pillars supporting the awning
    draw_shaded_rect(c, 4, 10, 7, 14, WOOD_RAMP)
    draw_shaded_rect(c, 64, 10, 67, 14, WOOD_RAMP)
    # Goods / scales on counter
    draw_shaded_ellipse(c, 22, 12, 6, 4, BRASS_RAMP)
    draw_shaded_ellipse(c, 50, 12, 8, 5, make_ramp((60, 140, 70)))
    if active:
        c.set_px(35 + (frame % 3) * 2, 11, (255, 220, 60, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_zapfhahn(active: bool = False, frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 24)
    # Wooden barrel / wall tap mount
    draw_shaded_rect(c, 2, 2, 13, 23, WOOD_RAMP)
    # Brass tap extending forward
    draw_shaded_rect(c, 6, 8, 12, 12, BRASS_RAMP)
    draw_shaded_rect(c, 10, 12, 13, 16, BRASS_RAMP)
    # Drip tray
    draw_shaded_rect(c, 4, 20, 13, 23, METAL_RAMP)
    if active:
        # Liquid drop falling
        drop_y = 15 + (frame % 3) * 2
        c.set_px(11, drop_y, (100, 220, 255, 255))
    apply_dark_outline(c)
    return c


def build_env_prop_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build umgebung/<key>.{png,json} for stations and environment props (Cards B28..B30)."""
    produced: list[Path] = []

    # B28 Stations (6):
    builders_b28 = [
        ("ws_portal", _draw_ws_portal),
        ("ws_werkbank", _draw_ws_werkbank),
        ("ws_fabrikator", _draw_ws_fabrikator),
        ("ws_liege", _draw_ws_liege),
        ("ws_haendler", _draw_ws_haendler),
        ("ws_zapfhahn", _draw_ws_zapfhahn),
    ]

    for key, builder in builders_b28:
        idle_frames = [builder(active=False, frame=i) for i in range(2)]
        use_frames = [builder(active=True, frame=i) for i in range(3)]
        w, h = idle_frames[0].width, idle_frames[0].height
        png, json_path = save_sheet(
            "umgebung",
            key,
            {"idle": idle_frames, "use": use_frames},
            anchor=(w // 2, h // 2),
            out_dir=out_dir,
        )
        produced.extend([png, json_path])

    return produced


def build_particle_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build partikel/<key>.{png,json} for all 12 particle sheets (Card B31)."""
    raise NotImplementedError("Card B31")
