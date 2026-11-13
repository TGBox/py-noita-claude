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
# ws_automat: 24x36
# ws_schiessstand: 64x24
# ws_archiv: 24x32
# ws_couch: 40x18
# ws_shredder: 16x20
# ws_well: 16x18
# portal_headquarters: 48x56
# trainings_attrappe: 20x28

WOOD_RAMP = make_ramp((130, 85, 45))
METAL_RAMP = make_ramp((120, 130, 145))
BRASS_RAMP = make_ramp((190, 150, 45))
PORTAL_RAMP = make_ramp((80, 140, 220))
CLOTH_RAMP = make_ramp((160, 50, 60))
GLOW_RAMP = make_ramp((100, 220, 240))
FLESH_RAMP = make_ramp((170, 70, 80))
STONE_RAMP = make_ramp((110, 115, 125))
WATER_RAMP = make_ramp((60, 150, 220))
COUCH_RAMP = make_ramp((90, 60, 120))


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


def _draw_ws_automat(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 24x36 arcade cabinet
    c = PixelCanvas(24, 36)
    draw_shaded_rect(c, 2, 4, 21, 35, METAL_RAMP)
    # Marquee top
    draw_shaded_rect(c, 3, 2, 20, 7, BRASS_RAMP)
    # Screen
    draw_shaded_rect(c, 4, 9, 19, 21, PORTAL_RAMP if active else make_ramp((30, 45, 60)))
    # Control panel / joystick
    draw_shaded_rect(c, 3, 22, 20, 26, WOOD_RAMP)
    c.set_px(8, 23, (240, 40, 40, 255))
    c.set_px(14, 24, (240, 240, 50, 255))
    c.set_px(17, 24, (50, 220, 80, 255))
    # Coin door
    draw_shaded_rect(c, 6, 28, 17, 34, make_ramp((40, 40, 45)))
    if active:
        # Screen glow animation
        c.set_px(10 + (frame % 3) * 2, 14, (255, 255, 255, 255))
        c.set_px(11, 15 + (frame % 2), (100, 240, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_schiessstand(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 64x24 shooting range counter & targets
    c = PixelCanvas(64, 24)
    # Wooden counter / booth
    draw_shaded_rect(c, 2, 10, 61, 23, WOOD_RAMP)
    # Back wall / target lane
    draw_shaded_rect(c, 4, 2, 59, 10, STONE_RAMP)
    # Targets on counter / background
    draw_shaded_ellipse(c, 16, 6, 4, 4, CLOTH_RAMP)
    draw_shaded_ellipse(c, 32, 5, 4, 4, BRASS_RAMP)
    draw_shaded_ellipse(c, 48, 6, 4, 4, CLOTH_RAMP)
    if active:
        # Swaying target or muzzle flash
        c.set_px(31 + (frame % 3), 4, (255, 240, 80, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_archiv(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 24x32 wooden filing cabinet
    c = PixelCanvas(24, 32)
    draw_shaded_rect(c, 2, 2, 21, 31, WOOD_RAMP)
    # 3 Drawer panels with brass handles
    for dy in (4, 13, 22):
        draw_shaded_rect(c, 4, dy, 19, dy + 7, make_ramp((110, 70, 35)))
        draw_shaded_rect(c, 10, dy + 3, 13, dy + 5, BRASS_RAMP)
    if active:
        # Top drawer slightly open / papers visible
        draw_shaded_rect(c, 6, 6, 17, 8, make_ramp((240, 235, 220)))
    apply_dark_outline(c)
    return c


def _draw_ws_couch(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 40x18 plush couch
    c = PixelCanvas(40, 18)
    # Backrest
    draw_shaded_rect(c, 2, 2, 37, 10, COUCH_RAMP)
    # Cushions / seat
    draw_shaded_rect(c, 4, 8, 35, 14, CLOTH_RAMP)
    # Armrests
    draw_shaded_ellipse(c, 4, 9, 3, 5, COUCH_RAMP)
    draw_shaded_ellipse(c, 35, 9, 3, 5, COUCH_RAMP)
    # Wooden feet
    draw_shaded_rect(c, 5, 14, 8, 17, WOOD_RAMP)
    draw_shaded_rect(c, 31, 14, 34, 17, WOOD_RAMP)
    if active:
        # Pillow depression / warm sparkle
        c.set_px(20 + frame, 9, (255, 230, 240, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_shredder(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 16x20 document shredder
    c = PixelCanvas(16, 20)
    # Waste bin
    draw_shaded_rect(c, 2, 7, 13, 19, make_ramp((60, 65, 75)))
    # Shredder head
    draw_shaded_rect(c, 1, 2, 14, 7, METAL_RAMP)
    # Feed slot
    draw_shaded_rect(c, 4, 3, 11, 4, make_ramp((20, 20, 25)))
    if active:
        # Paper feeding in / scraps
        c.set_px(7, 2, (250, 250, 250, 255))
        c.set_px(8, 8 + (frame % 3), (240, 240, 220, 255))
    apply_dark_outline(c)
    return c


def _draw_ws_well(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 16x18 stone fountain / well
    c = PixelCanvas(16, 18)
    # Stone basin
    draw_shaded_rect(c, 1, 6, 14, 17, STONE_RAMP)
    # Water surface
    draw_shaded_ellipse(c, 8, 8, 5, 3, WATER_RAMP)
    # Spout
    draw_shaded_rect(c, 6, 2, 9, 6, BRASS_RAMP)
    if active:
        # Water splashing
        c.set_px(8, 7 + (frame % 2), (200, 240, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_portal_headquarters(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 48x56 ornate grand portal to authority headquarters
    c = PixelCanvas(48, 56)
    # Heavy stone pillars & arch
    draw_shaded_rect(c, 2, 6, 45, 55, STONE_RAMP)
    draw_shaded_ellipse(c, 24, 16, 22, 14, BRASS_RAMP)
    # Inner gate
    draw_shaded_rect(c, 10, 16, 37, 55, make_ramp((30, 25, 45)))
    draw_shaded_ellipse(c, 24, 24, 14, 12, PORTAL_RAMP if active else make_ramp((60, 50, 80)))
    # Authority emblem / eye at top
    draw_shaded_ellipse(c, 24, 8, 6, 4, BRASS_RAMP)
    c.set_px(24, 8, (240, 50, 50, 255))
    if active:
        pulse_r = (frame % 3) * 3 + 8
        draw_shaded_ellipse(c, 24, 34, pulse_r, pulse_r + 4, GLOW_RAMP)
    apply_dark_outline(c)
    return c


def _draw_trainings_attrappe(active: bool = False, frame: int = 0) -> PixelCanvas:
    # 20x28 straw / wooden dummy on spring stand
    c = PixelCanvas(20, 28)
    # Base stand & spring
    draw_shaded_rect(c, 4, 24, 15, 27, WOOD_RAMP)
    draw_shaded_rect(c, 8, 19, 11, 24, METAL_RAMP)
    # Straw torso & dummy target
    draw_shaded_rect(c, 4, 7, 15, 19, make_ramp((170, 140, 75)))
    # Head / burlap sack
    draw_shaded_ellipse(c, 10, 4, 4, 4, make_ramp((180, 150, 85)))
    # Bullseye on chest
    c.set_px(10, 13, (240, 40, 40, 255))
    c.set_px(9, 13, (255, 255, 255, 255))
    c.set_px(11, 13, (255, 255, 255, 255))
    if active:
        # Wobble / hit effect
        c.set_px(6 + frame, 10, (255, 240, 100, 255))
    apply_dark_outline(c)
    return c


def build_env_prop_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build umgebung/<key>.{png,json} for stations and environment props (Cards B28..B30)."""
    produced: list[Path] = []

    # B28 & B29 Stations:
    builders = [
        ("ws_portal", _draw_ws_portal),
        ("ws_werkbank", _draw_ws_werkbank),
        ("ws_fabrikator", _draw_ws_fabrikator),
        ("ws_liege", _draw_ws_liege),
        ("ws_haendler", _draw_ws_haendler),
        ("ws_zapfhahn", _draw_ws_zapfhahn),
        ("ws_automat", _draw_ws_automat),
        ("ws_schiessstand", _draw_ws_schiessstand),
        ("ws_archiv", _draw_ws_archiv),
        ("ws_couch", _draw_ws_couch),
        ("ws_shredder", _draw_ws_shredder),
        ("ws_well", _draw_ws_well),
        ("portal_headquarters", _draw_portal_headquarters),
        ("trainings_attrappe", _draw_trainings_attrappe),
    ]

    for key, builder in builders:
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
