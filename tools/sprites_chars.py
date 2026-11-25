"""Contract V8: Character, companion, authority agent, evil self, and trader sprite builders (Cards B01..B05)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from tools.palette import make_ramp
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_segment_line,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

# ---------------------------------------------------------------------------
# Color ramps (Bible 04)
# ---------------------------------------------------------------------------

DARK_INK = (24, 20, 32, 255)
WHITE_PX = (248, 248, 255, 255)

# Cloita & Klonita
HAIR_ORANGE = make_ramp((230, 118, 42))
SKIN = make_ramp((238, 196, 166))
LAB_COAT = make_ramp((218, 222, 232))
PURPLE_SWEATER = make_ramp((132, 68, 162))
DARK_BOOT = make_ramp((54, 48, 62))
FLUX_CYAN = make_ramp((82, 236, 224))
KLONITA_PINK = make_ramp((235, 130, 175))
KLONITA_DENIM = make_ramp((95, 118, 172))
HEART_RED = make_ramp((220, 56, 72))
LANTERN_VIOLET = make_ramp((190, 95, 245))

# Authority agents
SUIT_DARK = make_ramp((68, 74, 88))
SHIRT_WHITE = make_ramp((226, 228, 236))
TIE_RED = make_ramp((192, 46, 54))
MASK_PALE = make_ramp((212, 214, 224))
CASE_BROWN = make_ramp((146, 94, 52))
BRASS_GOLD = make_ramp((218, 174, 56))
SHIELD_GLASS = make_ramp((125, 205, 235))
WOOD_STAMP = make_ramp((168, 112, 62))

# Evil selves & Ober-Cloita
GOLD_ARMOR = make_ramp((232, 182, 54))
ROYAL_CAPE = make_ramp((164, 34, 52))
PURE_ROBE = make_ramp((230, 234, 244))
CYBER_STEEL = make_ramp((110, 122, 138))
LASER_RED = make_ramp((236, 56, 56))
CABLE_BLUE = make_ramp((64, 152, 228))
VOID_VIOLET = make_ramp((142, 76, 198))

# Workshop traders
FLESH_PINK = make_ramp((216, 116, 126))
BOWLER_BLACK = make_ramp((54, 50, 62))
BINDER_BLUE = make_ramp((78, 112, 184))
PAPER_CREAM = make_ramp((236, 228, 206))
JELLY_GREEN = make_ramp((78, 210, 108))
STRAW_YELLOW = make_ramp((230, 196, 86))
ANT_RED = make_ramp((184, 58, 48))
TRENCH_GREY = make_ramp((92, 94, 104))
SHROOM_PURPLE = make_ramp((166, 74, 178))
NEON_GILL = make_ramp((92, 236, 196))
ROBE_BROWN = make_ramp((132, 86, 54))
FISH_TEAL = make_ramp((82, 168, 184))


def _seal_mark(c: PixelCanvas, cx: int, cy: int) -> None:
    """Draw a miniature Authority eye seal."""
    c.set_px(cx - 1, cy, MASK_PALE.shadow)
    c.set_px(cx + 1, cy, MASK_PALE.shadow)
    c.set_px(cx, cy - 1, MASK_PALE.shadow)
    c.set_px(cx, cy + 1, MASK_PALE.shadow)
    c.set_px(cx, cy, LASER_RED.light)


# ---------------------------------------------------------------------------
# Card B01: Cloita (spielerin)
# ---------------------------------------------------------------------------


def _draw_char_frame(
    offset_y: int = 0,
    *,
    cast_arm: bool = False,
    stride: int = 0,
    hurt: bool = False,
    dead: bool = False,
    hair_bob: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(22, 26)
    if dead:
        # Fallen horizontally with goggles knocked aside
        draw_shaded_rect(c, 3, 18, 16, 22, LAB_COAT)
        draw_shaded_rect(c, 4, 19, 8, 21, PURPLE_SWEATER)
        draw_shaded_ellipse(c, 16, 19, 3, 3, HAIR_ORANGE)
        draw_shaded_rect(c, 15, 18, 17, 20, SKIN)
        draw_shaded_rect(c, 2, 19, 4, 22, DARK_BOOT)
        draw_shaded_rect(c, 16, 14, 19, 16, FLUX_CYAN)
        apply_dark_outline(c)
        return c

    y0 = 2 + offset_y
    # Legs & heavy boots
    if stride > 0:
        draw_shaded_rect(c, 4, y0 + 16, 8, y0 + 21, DARK_BOOT)
        draw_shaded_rect(c, 13, y0 + 16, 17, y0 + 20, DARK_BOOT)
    elif stride < 0:
        draw_shaded_rect(c, 5, y0 + 16, 8, y0 + 20, DARK_BOOT)
        draw_shaded_rect(c, 12, y0 + 15, 16, y0 + 21, DARK_BOOT)
    else:
        draw_shaded_rect(c, 7, y0 + 16, 10, y0 + 21, DARK_BOOT)
        draw_shaded_rect(c, 11, y0 + 16, 14, y0 + 21, DARK_BOOT)

    # Lab coat flaring behind when striding
    coat_left = 4 if stride > 0 else (6 if stride == 0 else 7)
    coat_right = 15 if stride >= 0 else 17
    draw_shaded_rect(c, coat_left, y0 + 9, coat_right, y0 + 17, LAB_COAT)
    # Burn hole at coat hem
    c.set_px(coat_left + 1, y0 + 16, DARK_INK)
    c.set_px(coat_left + 2, y0 + 16, (90, 50, 40, 255))
    # Purple sweater underneath & cyan flask in breast pocket
    draw_shaded_rect(c, 9, y0 + 9, 12, y0 + 15, PURPLE_SWEATER)
    c.set_px(13, y0 + 11, FLUX_CYAN.highlight)
    c.set_px(13, y0 + 12, FLUX_CYAN.mid)

    # Wild orange hair & antenna strand
    draw_shaded_ellipse(c, 10, y0 + 5, 5, 4, HAIR_ORANGE)
    draw_segment_line(c, 10, y0 + 2, 12 + hair_bob, max(1, y0 - 2), HAIR_ORANGE.highlight, 1)
    # Face
    draw_shaded_rect(c, 8, y0 + 4, 13, y0 + 8, SKIN)
    if hurt:
        c.set_px(9, y0 + 6, DARK_INK)
        c.set_px(12, y0 + 6, DARK_INK)
    else:
        c.set_px(9, y0 + 6, DARK_INK)
        c.set_px(12, y0 + 6, DARK_INK)
        c.set_px(10, y0 + 7, (175, 100, 90, 255))
        c.set_px(11, y0 + 7, (175, 100, 90, 255))

    # Goggles: lowered over eyes when casting, pushed up on forehead otherwise
    goggle_y = y0 + 5 if cast_arm else y0 + 3
    draw_shaded_rect(c, 8, goggle_y, 10, goggle_y + 1, FLUX_CYAN)
    draw_shaded_rect(c, 11, goggle_y, 13, goggle_y + 1, FLUX_CYAN)
    c.set_px(9, goggle_y, WHITE_PX)
    c.set_px(12, goggle_y, WHITE_PX)

    # Arms
    if cast_arm:
        draw_shaded_rect(c, 14, y0 + 10, 19, y0 + 12, LAB_COAT)
        c.set_px(19, y0 + 11, SKIN.light)
    elif stride != 0:
        arm_x = 14 if stride > 0 else 4
        draw_shaded_rect(c, arm_x, y0 + 10, arm_x + 4, y0 + 12, LAB_COAT)
    else:
        draw_shaded_rect(c, 14, y0 + 10, 15, y0 + 14, LAB_COAT)

    apply_dark_outline(c)
    return c


def build_player_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/spielerin.{png,json} (Card B01)."""
    idle_frames = [
        _draw_char_frame(0, hair_bob=0),
        _draw_char_frame(0, hair_bob=1),
        _draw_char_frame(-1, hair_bob=0),
        _draw_char_frame(0, hair_bob=-1),
    ]
    walk_frames = [
        _draw_char_frame(0, stride=0),
        _draw_char_frame(-1, stride=1, hair_bob=1),
        _draw_char_frame(0, stride=0),
        _draw_char_frame(-1, stride=-1, hair_bob=-1),
    ]
    jump_frames = [
        _draw_char_frame(-2, stride=1),
        _draw_char_frame(-1, stride=0),
    ]
    fall_frames = [
        _draw_char_frame(1, cast_arm=True, stride=-1),
        _draw_char_frame(2, cast_arm=True, stride=0),
    ]
    cast_frames = [
        _draw_char_frame(0, cast_arm=True),
        _draw_char_frame(-1, cast_arm=True, hair_bob=1),
        _draw_char_frame(0, cast_arm=True),
    ]
    hurt_frames = [_draw_char_frame(1, hurt=True), _draw_char_frame(0, hurt=True)]
    dead_frames = [_draw_char_frame(dead=True)]

    anims = {
        "idle": idle_frames,
        "walk": walk_frames,
        "jump": jump_frames,
        "fall": fall_frames,
        "cast": cast_frames,
        "hurt": hurt_frames,
        "dead": dead_frames,
    }
    glow = [{"offset": [14, 12], "color": [120, 235, 225], "radius": 12}]
    png_path, json_path = save_sheet(
        "charaktere",
        "spielerin",
        anims,
        anchor=(11, 24),
        fps={"idle": 6.0, "walk": 8.0, "cast": 10.0, "hurt": 8.0},
        glow=glow,
        out_dir=out_dir,
    )
    return [png_path, json_path]


# ---------------------------------------------------------------------------
# Card B02: Klonita (klonita)
# ---------------------------------------------------------------------------


def _draw_klonita_frame(
    offset_y: int = 0,
    arm_pose: int = 0,
    foot_kick: int = 0,
    knocked: bool = False,
) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    if knocked:
        # Sitting down with tiny yellow stars spinning overhead
        draw_shaded_ellipse(c, 10, 16, 5, 4, KLONITA_DENIM)
        draw_shaded_rect(c, 6, 12, 13, 16, KLONITA_PINK)
        draw_shaded_ellipse(c, 10, 8, 4, 4, HAIR_ORANGE)
        draw_shaded_rect(c, 8, 8, 12, 11, SKIN)
        c.set_px(6, 3, BRASS_GOLD.highlight)
        c.set_px(13, 3, BRASS_GOLD.highlight)
        c.set_px(10, 2, BRASS_GOLD.light)
        apply_dark_outline(c)
        return c

    y0 = 2 + offset_y
    # Bunny-ear slippers
    if foot_kick > 0:
        draw_shaded_rect(c, 4, y0 + 16, 8, y0 + 19, SHIRT_WHITE)
        draw_shaded_rect(c, 12, y0 + 15, 16, y0 + 18, SHIRT_WHITE)
        c.set_px(5, y0 + 15, KLONITA_PINK.light)
        c.set_px(15, y0 + 14, KLONITA_PINK.light)
    elif foot_kick < 0:
        draw_shaded_rect(c, 5, y0 + 15, 8, y0 + 18, SHIRT_WHITE)
        draw_shaded_rect(c, 11, y0 + 16, 15, y0 + 19, SHIRT_WHITE)
    else:
        draw_shaded_rect(c, 6, y0 + 16, 9, y0 + 19, SHIRT_WHITE)
        draw_shaded_rect(c, 11, y0 + 16, 14, y0 + 19, SHIRT_WHITE)
        c.set_px(7, y0 + 15, KLONITA_PINK.light)
        c.set_px(12, y0 + 15, KLONITA_PINK.light)

    # Blue dungarees & pink knit sweater with red heart
    draw_shaded_rect(c, 6, y0 + 12, 13, y0 + 17, KLONITA_DENIM)
    draw_shaded_rect(c, 6, y0 + 9, 13, y0 + 13, KLONITA_PINK)
    c.set_px(9, y0 + 11, HEART_RED.light)
    c.set_px(10, y0 + 11, HEART_RED.light)
    c.set_px(9, y0 + 12, HEART_RED.mid)

    # Combed orange hair & pink bow
    draw_shaded_ellipse(c, 10, y0 + 5, 5, 4, HAIR_ORANGE)
    draw_shaded_rect(c, 6, y0 + 1, 9, y0 + 3, KLONITA_PINK)
    draw_shaded_rect(c, 11, y0 + 1, 13, y0 + 3, KLONITA_PINK)
    # Warm smiling face with big shiny eyes
    draw_shaded_rect(c, 7, y0 + 4, 12, y0 + 8, SKIN)
    c.set_px(8, y0 + 5, DARK_INK)
    c.set_px(11, y0 + 5, DARK_INK)
    c.set_px(8, y0 + 6, WHITE_PX)
    c.set_px(11, y0 + 6, WHITE_PX)
    c.set_px(9, y0 + 7, HEART_RED.light)
    c.set_px(10, y0 + 7, HEART_RED.light)
    # Faint clone scar on neck
    c.set_px(10, y0 + 8, SKIN.shadow)

    # Arms + floating violet lantern
    if arm_pose > 0:
        draw_shaded_rect(c, 2, y0 + 8, 6, y0 + 11, KLONITA_PINK)
        draw_shaded_rect(c, 13, y0 + 7, 17, y0 + 10, KLONITA_PINK)
        draw_shaded_ellipse(c, 17, y0 + 12, 2, 2, LANTERN_VIOLET)
    elif arm_pose < 0:
        draw_shaded_rect(c, 3, y0 + 11, 6, y0 + 13, KLONITA_PINK)
        draw_shaded_rect(c, 13, y0 + 11, 16, y0 + 13, KLONITA_PINK)
        draw_shaded_ellipse(c, 17, y0 + 14, 2, 2, LANTERN_VIOLET)
    else:
        draw_shaded_rect(c, 4, y0 + 10, 6, y0 + 13, KLONITA_PINK)
        draw_shaded_rect(c, 13, y0 + 10, 15, y0 + 13, KLONITA_PINK)
        draw_shaded_ellipse(c, 16, y0 + 13, 2, 2, LANTERN_VIOLET)

    apply_dark_outline(c)
    return c


def build_klonita_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/klonita.{png,json} (Card B02)."""
    idle_frames = [
        _draw_klonita_frame(0, 0, 0),
        _draw_klonita_frame(-1, 1, 0),
        _draw_klonita_frame(0, 0, 0),
        _draw_klonita_frame(1, -1, 0),
    ]
    fly_frames = [
        _draw_klonita_frame(0, 0, 0),
        _draw_klonita_frame(-2, 1, 1),
        _draw_klonita_frame(-1, 0, 0),
        _draw_klonita_frame(0, -1, -1),
    ]
    assist_frames = [_draw_klonita_frame(0, 1, 0), _draw_klonita_frame(-1, 1, 1), _draw_klonita_frame(0, 0, 0)]
    quirk_frames = [_draw_klonita_frame(0, -1, 0), _draw_klonita_frame(1, 1, -1), _draw_klonita_frame(0, 0, 0)]
    knocked_frames = [_draw_klonita_frame(knocked=True), _draw_klonita_frame(offset_y=1, knocked=True)]

    anims = {
        "idle": idle_frames,
        "fly": fly_frames,
        "assist": assist_frames,
        "quirk": quirk_frames,
        "knocked": knocked_frames,
    }
    glow = [{"offset": [16, 13], "color": [200, 100, 255], "radius": 14}]
    png_path, json_path = save_sheet(
        "charaktere",
        "klonita",
        anims,
        anchor=(10, 22),
        fps={"idle": 5.0, "fly": 8.0, "assist": 8.0, "quirk": 6.0, "knocked": 6.0},
        glow=glow,
        out_dir=out_dir,
    )
    return [png_path, json_path]


# ---------------------------------------------------------------------------
# Card B03: Authority agents (agent_*)
# ---------------------------------------------------------------------------


def _draw_agent_sachbearbeiter_frame(
    offset_y: int = 0,
    arm_swing: int = 0,
    leg_stride: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    y0 = 2 + offset_y
    # Legs
    if leg_stride > 0:
        draw_shaded_rect(c, 4, y0 + 15, 7, y0 + 20, DARK_BOOT)
        draw_shaded_rect(c, 12, y0 + 15, 15, y0 + 19, DARK_BOOT)
    elif leg_stride < 0:
        draw_shaded_rect(c, 5, y0 + 15, 8, y0 + 19, DARK_BOOT)
        draw_shaded_rect(c, 11, y0 + 15, 15, y0 + 20, DARK_BOOT)
    else:
        draw_shaded_rect(c, 6, y0 + 15, 8, y0 + 20, DARK_BOOT)
        draw_shaded_rect(c, 10, y0 + 15, 12, y0 + 20, DARK_BOOT)

    # Dark grey suit, white shirt & red tie
    draw_shaded_rect(c, 5, y0 + 8, 13, y0 + 16, SUIT_DARK)
    draw_shaded_rect(c, 8, y0 + 8, 10, y0 + 13, SHIRT_WHITE)
    draw_segment_line(c, 9, y0 + 9, 9, y0 + 13, TIE_RED.mid, 1)

    # Authority mask with eye seal & fedora hat
    draw_shaded_ellipse(c, 9, y0 + 5, 3, 3, MASK_PALE)
    _seal_mark(c, 10, y0 + 5)
    draw_shaded_rect(c, 4, y0 + 2, 14, y0 + 3, SUIT_DARK)
    draw_shaded_rect(c, 6, y0, 12, y0 + 2, SUIT_DARK)

    # Briefcase swinging outward on walk
    case_x = 13 + arm_swing
    draw_shaded_rect(c, max(1, case_x), y0 + 11, min(18, case_x + 4), y0 + 16, CASE_BROWN)
    c.set_px(min(18, case_x + 2), y0 + 11, BRASS_GOLD.highlight)
    apply_dark_outline(c)
    return c


def _draw_agent_drohne_frame(offset_y: int = 0, prop_state: int = 0, scan: bool = False) -> PixelCanvas:
    c = PixelCanvas(20, 16)
    y0 = 4 + offset_y
    # Propeller shaft & spinning blades (width changes dramatically in walk)
    draw_shaded_rect(c, 9, y0 - 2, 10, y0, SUIT_DARK)
    if prop_state == 0:
        draw_shaded_rect(c, 3, y0 - 3, 16, y0 - 2, MASK_PALE)
    elif prop_state == 1:
        draw_shaded_rect(c, 6, y0 - 3, 13, y0 - 2, MASK_PALE)
    else:
        draw_shaded_rect(c, 2, y0 - 3, 17, y0 - 2, BRASS_GOLD)

    # Flying leather briefcase body with brass corners
    draw_shaded_rect(c, 4, y0, 15, y0 + 8, CASE_BROWN)
    c.set_px(4, y0, BRASS_GOLD.highlight)
    c.set_px(15, y0, BRASS_GOLD.highlight)
    c.set_px(4, y0 + 8, BRASS_GOLD.highlight)
    c.set_px(15, y0 + 8, BRASS_GOLD.highlight)
    # Red camera eye + optional spotlight beam
    draw_shaded_ellipse(c, 10, y0 + 4, 2, 2, MASK_PALE)
    c.set_px(10, y0 + 4, LASER_RED.highlight)
    if scan:
        draw_segment_line(c, 12, y0 + 4, 18, y0 + 6, LASER_RED.light, 1)
    apply_dark_outline(c)
    return c


def _draw_agent_vollstrecker_frame(
    offset_y: int = 0,
    pose: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(24, 26)
    y0 = 2 + offset_y
    # Heavy boots
    if pose > 0:
        draw_shaded_rect(c, 6, y0 + 17, 10, y0 + 22, DARK_BOOT)
        draw_shaded_rect(c, 14, y0 + 16, 18, y0 + 21, DARK_BOOT)
    elif pose < 0:
        draw_shaded_rect(c, 7, y0 + 16, 11, y0 + 21, DARK_BOOT)
        draw_shaded_rect(c, 13, y0 + 17, 17, y0 + 22, DARK_BOOT)
    else:
        draw_shaded_rect(c, 7, y0 + 17, 11, y0 + 22, DARK_BOOT)
        draw_shaded_rect(c, 13, y0 + 17, 17, y0 + 22, DARK_BOOT)

    # Wide armoured trenchcoat
    draw_shaded_rect(c, 6, y0 + 7, 17, y0 + 18, SUIT_DARK)
    draw_shaded_rect(c, 10, y0 + 8, 13, y0 + 15, SHIRT_WHITE)
    c.set_px(11, y0 + 10, TIE_RED.mid)
    # Helmet + visor + glowing shoulder lamp
    draw_shaded_rect(c, 8, y0 + 1, 15, y0 + 6, MASK_PALE)
    draw_shaded_rect(c, 9, y0 + 3, 14, y0 + 4, DARK_BOOT)
    draw_shaded_ellipse(c, 17, y0 + 7, 1, 1, BRASS_GOLD)
    c.set_px(17, y0 + 7, WHITE_PX)

    # Left translucent riot shield
    sy = y0 + (6 if pose <= 0 else 4)
    draw_shaded_rect(c, 2, sy, 5, sy + 11, SHIELD_GLASS)
    c.set_px(3, sy + 2, WHITE_PX)
    # Right giant wooden stamp weapon
    st_x = 18 if pose == 0 else (20 if pose > 0 else 17)
    st_y = y0 + (8 if pose <= 0 else 5)
    draw_shaded_rect(c, st_x, st_y, min(22, st_x + 3), st_y + 7, WOOD_STAMP)
    draw_shaded_rect(c, st_x - 1, st_y + 6, min(22, st_x + 4), st_y + 8, BRASS_GOLD)
    apply_dark_outline(c)
    return c


def _draw_agent_abteilungsleiter_frame(
    offset_y: int = 0,
    wave: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(26, 28)
    y0 = 3 + offset_y
    # Floating dark executive robe with flared coattails
    flare = 2 if wave > 0 else (0 if wave == 0 else 1)
    draw_shaded_rect(c, 8 - flare, y0 + 8, 17 + flare, y0 + 20, SUIT_DARK)
    draw_shaded_rect(c, 11, y0 + 9, 14, y0 + 17, SHIRT_WHITE)
    draw_segment_line(c, 12, y0 + 10, 12, y0 + 16, TIE_RED.mid, 1)
    # Trailing coat hems
    draw_shaded_rect(c, 7 - flare, y0 + 19, 10, y0 + 23, SUIT_DARK)
    draw_shaded_rect(c, 15, y0 + 19, 18 + flare, y0 + 23, SUIT_DARK)

    # Mask + gold paragraph crown
    draw_shaded_ellipse(c, 12, y0 + 5, 4, 3, MASK_PALE)
    _seal_mark(c, 12, y0 + 5)
    draw_shaded_rect(c, 9, y0, 15, y0 + 2, BRASS_GOLD)
    c.set_px(10, y0 - 1, BRASS_GOLD.highlight)
    c.set_px(12, y0 - 1, WHITE_PX)
    c.set_px(14, y0 - 1, BRASS_GOLD.highlight)

    # Dual floating stamps oscillating vertically/outward
    ly = y0 + (10 - wave * 3)
    ry = y0 + (10 + wave * 3)
    draw_shaded_rect(c, 2, ly, 6, ly + 5, WOOD_STAMP)
    draw_shaded_rect(c, 19, ry, 23, ry + 5, WOOD_STAMP)
    c.set_px(4, ly + 4, BRASS_GOLD.highlight)
    c.set_px(21, ry + 4, BRASS_GOLD.highlight)
    apply_dark_outline(c)
    return c


def build_agent_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/agent_*.{png,json} (Card B03)."""
    paths: list[Path] = []

    sb_idle = [_draw_agent_sachbearbeiter_frame(y) for y in (0, 1, 0, -1)]
    sb_walk = [
        _draw_agent_sachbearbeiter_frame(0, arm_swing=0, leg_stride=0),
        _draw_agent_sachbearbeiter_frame(-1, arm_swing=2, leg_stride=1),
        _draw_agent_sachbearbeiter_frame(0, arm_swing=0, leg_stride=0),
        _draw_agent_sachbearbeiter_frame(-1, arm_swing=-2, leg_stride=-1),
    ]
    sb_anims = {
        "idle": sb_idle,
        "walk": sb_walk,
        "windup": [_draw_agent_sachbearbeiter_frame(-1, 2), _draw_agent_sachbearbeiter_frame(0, 3)],
        "attack": [_draw_agent_sachbearbeiter_frame(1, 3), _draw_agent_sachbearbeiter_frame(0, 0)],
        "hurt": [_draw_agent_sachbearbeiter_frame(1), _draw_agent_sachbearbeiter_frame(0)],
        "dead": [_draw_agent_sachbearbeiter_frame(2)],
    }
    for name in ("agent_sachbearbeiter", "agent_streife"):
        p, j = save_sheet(
            "charaktere",
            name,
            sb_anims,
            anchor=(10, 22),
            fps={"idle": 5.0, "walk": 8.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
            out_dir=out_dir,
        )
        paths.extend([p, j])

    dr_anims = {
        "idle": [_draw_agent_drohne_frame(y, p) for y, p in ((0, 0), (-1, 1), (0, 2), (1, 1))],
        "walk": [_draw_agent_drohne_frame(0, 0), _draw_agent_drohne_frame(-1, 1), _draw_agent_drohne_frame(0, 2), _draw_agent_drohne_frame(1, 1)],
        "windup": [_draw_agent_drohne_frame(-1, 2, scan=True), _draw_agent_drohne_frame(-1, 1, scan=True)],
        "attack": [_draw_agent_drohne_frame(0, 2, scan=True), _draw_agent_drohne_frame(1, 0, scan=False)],
        "hurt": [_draw_agent_drohne_frame(1, 1), _draw_agent_drohne_frame(2, 0)],
        "dead": [_draw_agent_drohne_frame(3, 1)],
    }
    p, j = save_sheet(
        "charaktere",
        "agent_drohne",
        dr_anims,
        anchor=(10, 13),
        fps={"idle": 6.0, "walk": 10.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=[{"offset": [10, 8], "color": [255, 55, 55], "radius": 12}],
        out_dir=out_dir,
    )
    paths.extend([p, j])

    vs_anims = {
        "idle": [_draw_agent_vollstrecker_frame(y, 0) for y in (0, 1, 0, -1)],
        "walk": [
            _draw_agent_vollstrecker_frame(0, 0),
            _draw_agent_vollstrecker_frame(-1, 1),
            _draw_agent_vollstrecker_frame(0, 0),
            _draw_agent_vollstrecker_frame(-1, -1),
        ],
        "windup": [_draw_agent_vollstrecker_frame(-1, 1), _draw_agent_vollstrecker_frame(0, 1)],
        "attack": [_draw_agent_vollstrecker_frame(1, -1), _draw_agent_vollstrecker_frame(0, 0)],
        "hurt": [_draw_agent_vollstrecker_frame(1, 0), _draw_agent_vollstrecker_frame(0, 0)],
        "dead": [_draw_agent_vollstrecker_frame(2, 0)],
    }
    p, j = save_sheet(
        "charaktere",
        "agent_vollstrecker",
        vs_anims,
        anchor=(12, 24),
        fps={"idle": 5.0, "walk": 7.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        out_dir=out_dir,
    )
    paths.extend([p, j])

    al_anims = {
        "idle": [_draw_agent_abteilungsleiter_frame(y, 0) for y in (0, -1, 0, 1)],
        "walk": [
            _draw_agent_abteilungsleiter_frame(0, 0),
            _draw_agent_abteilungsleiter_frame(-1, 1),
            _draw_agent_abteilungsleiter_frame(0, 0),
            _draw_agent_abteilungsleiter_frame(-1, -1),
        ],
        "fly": [_draw_agent_abteilungsleiter_frame(y, 1) for y in (-1, -2, -1, 0)],
        "windup": [_draw_agent_abteilungsleiter_frame(-1, 1), _draw_agent_abteilungsleiter_frame(-2, -1)],
        "attack": [_draw_agent_abteilungsleiter_frame(0, 1), _draw_agent_abteilungsleiter_frame(1, 0)],
        "hurt": [_draw_agent_abteilungsleiter_frame(1, 0), _draw_agent_abteilungsleiter_frame(0, 0)],
        "dead": [_draw_agent_abteilungsleiter_frame(2, 0)],
    }
    p, j = save_sheet(
        "charaktere",
        "agent_abteilungsleiter",
        al_anims,
        anchor=(13, 26),
        fps={"idle": 5.0, "walk": 7.0, "fly": 7.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=[{"offset": [13, 3], "color": [255, 215, 0], "radius": 14}],
        out_dir=out_dir,
    )
    paths.extend([p, j])

    return paths


# ---------------------------------------------------------------------------
# Card B04: Evil selves & Ober-Cloita
# ---------------------------------------------------------------------------


def _draw_boese_kaiserin_frame(offset_y: int = 0, stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 28)
    y0 = 2 + offset_y
    # Billowing red royal cape behind
    cape_reach = 2 if stride > 0 else (5 if stride < 0 else 3)
    draw_shaded_rect(c, cape_reach, y0 + 11, 11, y0 + 22, ROYAL_CAPE)
    # Golden boots
    if stride > 0:
        draw_shaded_rect(c, 7, y0 + 19, 10, y0 + 24, GOLD_ARMOR)
        draw_shaded_rect(c, 15, y0 + 18, 19, y0 + 23, GOLD_ARMOR)
    elif stride < 0:
        draw_shaded_rect(c, 8, y0 + 18, 11, y0 + 23, GOLD_ARMOR)
        draw_shaded_rect(c, 14, y0 + 19, 18, y0 + 24, GOLD_ARMOR)
    else:
        draw_shaded_rect(c, 9, y0 + 19, 12, y0 + 24, GOLD_ARMOR)
        draw_shaded_rect(c, 14, y0 + 19, 17, y0 + 24, GOLD_ARMOR)

    # Golden armor torso with authority seal
    draw_shaded_rect(c, 8, y0 + 10, 17, y0 + 20, GOLD_ARMOR)
    _seal_mark(c, 13, y0 + 14)
    # Giant orange hair tower + crown with antenna
    draw_shaded_ellipse(c, 12, y0 + 5, 4, 4, HAIR_ORANGE)
    draw_shaded_rect(c, 10, y0 + 5, 15, y0 + 9, SKIN)
    c.set_px(11, y0 + 7, LASER_RED.light)
    c.set_px(14, y0 + 7, LASER_RED.light)
    draw_shaded_rect(c, 9, y0 + 1, 16, y0 + 3, GOLD_ARMOR)
    draw_segment_line(c, 13, y0, 13, max(0, y0 - 2), FLUX_CYAN.highlight, 1)
    apply_dark_outline(c)
    return c


def _draw_boese_gute_frame(offset_y: int = 0, pose: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 26)
    y0 = 3 + offset_y
    # Glowing cyan flux halo hovering above head
    draw_shaded_ellipse(c, 12, y0 + 1, 6, 2, FLUX_CYAN)
    c.set_px(12, y0 + 1, WHITE_PX)
    # Floating white cultist robe with gold trim & flapping sleeves
    hem_w = 2 if pose != 0 else 0
    draw_shaded_rect(c, 7 - hem_w, y0 + 11, 16 + hem_w, y0 + 21, PURE_ROBE)
    draw_shaded_rect(c, 7 - hem_w, y0 + 20, 16 + hem_w, y0 + 21, GOLD_ARMOR)
    _seal_mark(c, 12, y0 + 15)
    # Raised/lowered blessing arms
    arm_y = y0 + (8 if pose > 0 else (12 if pose < 0 else 10))
    draw_shaded_rect(c, 3, arm_y, 7, arm_y + 3, PURE_ROBE)
    draw_shaded_rect(c, 16, arm_y, 20, arm_y + 3, PURE_ROBE)
    # Orange hair & pale smiling face with empty black eyes
    draw_shaded_ellipse(c, 12, y0 + 6, 4, 4, HAIR_ORANGE)
    draw_shaded_rect(c, 9, y0 + 6, 14, y0 + 10, SKIN)
    c.set_px(10, y0 + 7, DARK_INK)
    c.set_px(13, y0 + 7, DARK_INK)
    c.set_px(11, y0 + 9, HEART_RED.mid)
    c.set_px(12, y0 + 9, HEART_RED.mid)
    apply_dark_outline(c)
    return c


def _draw_boese_omega_frame(offset_y: int = 0, stride: int = 0, drone_y: int = 0) -> PixelCanvas:
    c = PixelCanvas(26, 26)
    y0 = 3 + offset_y
    # Cybernetic legs
    if stride > 0:
        draw_shaded_rect(c, 5, y0 + 16, 9, y0 + 21, CYBER_STEEL)
        draw_shaded_rect(c, 14, y0 + 15, 18, y0 + 20, CYBER_STEEL)
    elif stride < 0:
        draw_shaded_rect(c, 6, y0 + 15, 10, y0 + 20, CYBER_STEEL)
        draw_shaded_rect(c, 13, y0 + 16, 17, y0 + 21, CYBER_STEEL)
    else:
        draw_shaded_rect(c, 7, y0 + 16, 10, y0 + 21, CYBER_STEEL)
        draw_shaded_rect(c, 13, y0 + 16, 16, y0 + 21, CYBER_STEEL)

    # Half-robot torso
    draw_shaded_rect(c, 7, y0 + 9, 11, y0 + 17, LAB_COAT)
    draw_shaded_rect(c, 12, y0 + 9, 16, y0 + 17, CYBER_STEEL)
    _seal_mark(c, 14, y0 + 13)
    # Head: orange hair left, steel + red laser eye + blue cables right
    draw_shaded_rect(c, 7, y0 + 3, 11, y0 + 8, HAIR_ORANGE)
    draw_shaded_rect(c, 9, y0 + 4, 11, y0 + 8, SKIN)
    draw_shaded_rect(c, 12, y0 + 3, 16, y0 + 8, CYBER_STEEL)
    c.set_px(14, y0 + 5, LASER_RED.highlight)
    draw_segment_line(c, 15, y0 + 3, 18, y0 + 1, CABLE_BLUE.light, 1)
    # Arm cannon extending right
    cannon_y = y0 + (10 if stride >= 0 else 12)
    draw_shaded_rect(c, 16, cannon_y, 23, cannon_y + 4, CYBER_STEEL)
    c.set_px(23, cannon_y + 2, LASER_RED.highlight)
    # Orbiting mini-drone left
    draw_shaded_ellipse(c, 3, y0 + 6 + drone_y, 2, 2, CYBER_STEEL)
    c.set_px(3, y0 + 6 + drone_y, LASER_RED.light)
    apply_dark_outline(c)
    return c


def _draw_ober_cloita_frame(offset_y: int = 0, wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(34, 34)
    y0 = 3 + offset_y
    # Swirling void/flux base vortex
    vortex_w = 10 + abs(wave) * 2
    draw_shaded_ellipse(c, 17, y0 + 26, vortex_w, 4, VOID_VIOLET)
    draw_shaded_ellipse(c, 17, y0 + 25, vortex_w - 3, 2, FLUX_CYAN)

    # Fused Cloita body tower
    draw_shaded_rect(c, 11, y0 + 12, 23, y0 + 25, LAB_COAT)
    draw_shaded_rect(c, 14, y0 + 14, 20, y0 + 22, ROYAL_CAPE)
    _seal_mark(c, 17, y0 + 18)

    # Four oscillating weapon arms (cannon, stamp, flux beams)
    ly = y0 + (13 - wave * 3)
    ry = y0 + (13 + wave * 3)
    draw_shaded_rect(c, 2, ly, 10, ly + 4, CYBER_STEEL)
    c.set_px(2, ly + 2, LASER_RED.highlight)
    draw_shaded_rect(c, 24, ry, 31, ry + 4, GOLD_ARMOR)
    c.set_px(31, ry + 2, FLUX_CYAN.highlight)
    draw_shaded_rect(c, 4, y0 + 20 + wave * 2, 10, y0 + 23 + wave * 2, WOOD_STAMP)
    draw_shaded_rect(c, 24, y0 + 20 - wave * 2, 30, y0 + 23 - wave * 2, PURPLE_SWEATER)

    # Side Cloita heads + central crowned head + halo
    draw_shaded_ellipse(c, 9, y0 + 9, 3, 3, HAIR_ORANGE)
    draw_shaded_rect(c, 8, y0 + 8, 10, y0 + 10, SKIN)
    draw_shaded_ellipse(c, 25, y0 + 9, 3, 3, HAIR_ORANGE)
    draw_shaded_rect(c, 24, y0 + 8, 26, y0 + 10, SKIN)
    draw_shaded_ellipse(c, 17, y0 + 7, 4, 4, HAIR_ORANGE)
    draw_shaded_rect(c, 15, y0 + 6, 19, y0 + 10, SKIN)
    c.set_px(16, y0 + 8, LASER_RED.highlight)
    c.set_px(18, y0 + 8, FLUX_CYAN.highlight)
    draw_shaded_rect(c, 13, y0 + 2, 21, y0 + 4, GOLD_ARMOR)
    draw_shaded_ellipse(c, 17, y0, 6, 1, FLUX_CYAN)
    apply_dark_outline(c)
    return c


def build_evil_and_hq_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/boese_* and ober_cloita sheets (Card B04)."""
    paths: list[Path] = []

    k_anims = {
        "idle": [_draw_boese_kaiserin_frame(y, 0) for y in (0, 1, 0, -1)],
        "walk": [
            _draw_boese_kaiserin_frame(0, 0),
            _draw_boese_kaiserin_frame(-1, 1),
            _draw_boese_kaiserin_frame(0, 0),
            _draw_boese_kaiserin_frame(-1, -1),
        ],
        "windup": [_draw_boese_kaiserin_frame(-1, 1), _draw_boese_kaiserin_frame(0, -1)],
        "attack": [_draw_boese_kaiserin_frame(1, 1), _draw_boese_kaiserin_frame(0, 0)],
        "hurt": [_draw_boese_kaiserin_frame(1, 0), _draw_boese_kaiserin_frame(0, 0)],
        "dead": [_draw_boese_kaiserin_frame(3, 0)],
    }
    p, j = save_sheet(
        "charaktere",
        "boese_kaiserin",
        k_anims,
        anchor=(12, 26),
        fps={"idle": 5.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=[{"offset": [12, 3], "color": [255, 215, 0], "radius": 12}],
        out_dir=out_dir,
    )
    paths.extend([p, j])

    g_anims = {
        "idle": [_draw_boese_gute_frame(y, 0) for y in (0, 1, 0, -1)],
        "walk": [
            _draw_boese_gute_frame(0, 0),
            _draw_boese_gute_frame(-1, 1),
            _draw_boese_gute_frame(0, 0),
            _draw_boese_gute_frame(0, -1),
        ],
        "windup": [_draw_boese_gute_frame(-1, 1), _draw_boese_gute_frame(0, 1)],
        "attack": [_draw_boese_gute_frame(1, -1), _draw_boese_gute_frame(0, 0)],
        "hurt": [_draw_boese_gute_frame(1, 0), _draw_boese_gute_frame(0, 0)],
        "dead": [_draw_boese_gute_frame(3, 0)],
    }
    p, j = save_sheet(
        "charaktere",
        "boese_gute",
        g_anims,
        anchor=(12, 24),
        fps={"idle": 5.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=[{"offset": [12, 3], "color": [120, 240, 225], "radius": 14}],
        out_dir=out_dir,
    )
    paths.extend([p, j])

    o_anims = {
        "idle": [_draw_boese_omega_frame(y, 0, d) for y, d in ((0, 0), (1, 1), (0, 0), (-1, -1))],
        "walk": [
            _draw_boese_omega_frame(0, 0, 0),
            _draw_boese_omega_frame(-1, 1, -2),
            _draw_boese_omega_frame(0, 0, 0),
            _draw_boese_omega_frame(-1, -1, 2),
        ],
        "windup": [_draw_boese_omega_frame(-1, 0, -1), _draw_boese_omega_frame(0, 0, -2)],
        "attack": [_draw_boese_omega_frame(1, 1, 1), _draw_boese_omega_frame(0, 0, 0)],
        "hurt": [_draw_boese_omega_frame(1, 0, 0), _draw_boese_omega_frame(0, 0, 0)],
        "dead": [_draw_boese_omega_frame(3, 0, 1)],
    }
    p, j = save_sheet(
        "charaktere",
        "boese_omega",
        o_anims,
        anchor=(13, 24),
        fps={"idle": 5.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=[{"offset": [23, 14], "color": [255, 50, 50], "radius": 12}],
        out_dir=out_dir,
    )
    paths.extend([p, j])

    oc_anims = {
        "idle": [_draw_ober_cloita_frame(y, 0) for y in (0, 1, 0, -1)],
        "walk": [
            _draw_ober_cloita_frame(0, 0),
            _draw_ober_cloita_frame(-1, 1),
            _draw_ober_cloita_frame(0, 0),
            _draw_ober_cloita_frame(-1, -1),
        ],
        "windup": [_draw_ober_cloita_frame(-1, 1), _draw_ober_cloita_frame(0, -1)],
        "attack": [_draw_ober_cloita_frame(1, 1), _draw_ober_cloita_frame(0, 0)],
        "hurt": [_draw_ober_cloita_frame(1, 0), _draw_ober_cloita_frame(0, 0)],
        "dead": [_draw_ober_cloita_frame(2, 0)],
    }
    p, j = save_sheet(
        "charaktere",
        "ober_cloita",
        oc_anims,
        anchor=(17, 31),
        fps={"idle": 5.0, "walk": 7.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=[{"offset": [17, 4], "color": [120, 235, 255], "radius": 16}],
        out_dir=out_dir,
    )
    paths.extend([p, j])

    return paths


# ---------------------------------------------------------------------------
# Card B05: Workshop traders (npc_*)
# ---------------------------------------------------------------------------


def _draw_magenhaendler_frame(offset_y: int = 0, wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 24)
    y0 = 2 + offset_y
    # Walking curved stomach sac
    draw_shaded_ellipse(c, 12, y0 + 13, 6, 7, FLESH_PINK)
    # Tentacle arms waving
    draw_segment_line(c, 6, y0 + 12, 2, y0 + 14 - wave * 2, FLESH_PINK.light, 2)
    draw_segment_line(c, 18, y0 + 12, 21, y0 + 10 + wave * 2, FLESH_PINK.light, 2)
    # Black bowler hat + gold monocle & chain
    draw_shaded_rect(c, 7, y0 + 5, 16, y0 + 6, BOWLER_BLACK)
    draw_shaded_ellipse(c, 12, y0 + 3, 4, 3, BOWLER_BLACK)
    draw_shaded_ellipse(c, 14, y0 + 10, 2, 2, BRASS_GOLD)
    c.set_px(14, y0 + 10, SHIELD_GLASS.highlight)
    draw_segment_line(c, 15, y0 + 12, 16, y0 + 15, BRASS_GOLD.mid, 1)
    c.set_px(9, y0 + 10, DARK_INK)
    apply_dark_outline(c)
    return c


def _draw_sachbearbeiterin_frame(offset_y: int = 0, stamp: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 26)
    y0 = 2 + offset_y
    # Tall blue ring binder with white spine label & cream papers sticking out top
    draw_shaded_rect(c, 5, y0 + 4, 15, y0 + 21, BINDER_BLUE)
    draw_shaded_rect(c, 7, y0 + 2, 13, y0 + 4, PAPER_CREAM)
    draw_shaded_rect(c, 7, y0 + 14, 13, y0 + 19, PAPER_CREAM)
    # Gold glasses
    draw_shaded_rect(c, 6, y0 + 8, 9, y0 + 10, BRASS_GOLD)
    draw_shaded_rect(c, 11, y0 + 8, 14, y0 + 10, BRASS_GOLD)
    c.set_px(7, y0 + 9, DARK_INK)
    c.set_px(12, y0 + 9, DARK_INK)
    # Sleeve protector & wooden stamp hand
    draw_shaded_rect(c, 15, y0 + 12 - stamp, 19, y0 + 15 - stamp, SUIT_DARK)
    draw_shaded_rect(c, 17, y0 + 15 - stamp, 20, y0 + 17 - stamp, WOOD_STAMP)
    apply_dark_outline(c)
    return c


def _draw_glibberhaendler_frame(offset_y: int = 0, hop: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 22)
    y0 = 3 + offset_y - hop
    # Translucent green jelly cube with rounded corners & items floating inside
    draw_shaded_rect(c, 4, y0 + 6, 19, y0 + 17, JELLY_GREEN)
    c.set_px(7, y0 + 13, BRASS_GOLD.highlight)
    c.set_px(8, y0 + 14, BRASS_GOLD.mid)
    c.set_px(15, y0 + 14, HEART_RED.light)
    c.set_px(16, y0 + 13, FLUX_CYAN.highlight)
    # Happy eyes
    c.set_px(9, y0 + 10, DARK_INK)
    c.set_px(14, y0 + 10, DARK_INK)
    c.set_px(11, y0 + 11, DARK_INK)
    c.set_px(12, y0 + 11, DARK_INK)
    # Yellow straw hat with red ribbon
    draw_shaded_rect(c, 2, y0 + 4, 21, y0 + 5, STRAW_YELLOW)
    draw_shaded_rect(c, 6, y0 + 1, 17, y0 + 4, STRAW_YELLOW)
    draw_shaded_rect(c, 6, y0 + 3, 17, y0 + 4, TIE_RED)
    apply_dark_outline(c)
    return c


def _draw_ameisenhehler_frame(offset_y: int = 0, coat_open: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 24)
    y0 = 2 + offset_y
    # Red ant head, antennae & dark sunglasses
    draw_shaded_ellipse(c, 12, y0 + 5, 4, 3, ANT_RED)
    draw_segment_line(c, 10, y0 + 2, 7, y0, ANT_RED.mid, 1)
    draw_segment_line(c, 14, y0 + 2, 17, y0, ANT_RED.mid, 1)
    draw_shaded_rect(c, 9, y0 + 4, 15, y0 + 5, DARK_BOOT)
    # Grey trenchcoat opening wide during talk/offer to reveal contraband
    flap = coat_open * 2
    draw_shaded_rect(c, 6 - flap, y0 + 9, 17 + flap, y0 + 20, TRENCH_GREY)
    draw_shaded_rect(c, 8, y0 + 8, 15, y0 + 10, TRENCH_GREY)
    if coat_open > 0:
        draw_shaded_rect(c, 9, y0 + 11, 14, y0 + 18, DARK_BOOT)
        c.set_px(10, y0 + 13, FLUX_CYAN.highlight)
        c.set_px(13, y0 + 15, BRASS_GOLD.highlight)
        c.set_px(11, y0 + 17, HEART_RED.light)
    apply_dark_outline(c)
    return c


def _draw_dj_frame(offset_y: int = 0, bounce: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 24)
    y0 = 2 + offset_y
    # Mushroom stalk & glowing cyan gills
    draw_shaded_rect(c, 9, y0 + 10, 14, y0 + 20, PAPER_CREAM)
    draw_shaded_rect(c, 7, y0 + 8, 16, y0 + 10, NEON_GILL)
    # Purple mushroom cap
    draw_shaded_ellipse(c, 12, y0 + 5, 8, 4, SHROOM_PURPLE)
    c.set_px(8, y0 + 4, NEON_GILL.highlight)
    c.set_px(15, y0 + 4, NEON_GILL.highlight)
    # Big black/red headphones on sides of cap
    draw_shaded_rect(c, 2, y0 + 4 - bounce, 5, y0 + 10 - bounce, DARK_BOOT)
    draw_shaded_rect(c, 18, y0 + 4 - bounce, 21, y0 + 10 - bounce, DARK_BOOT)
    c.set_px(3, y0 + 7 - bounce, TIE_RED.light)
    c.set_px(20, y0 + 7 - bounce, TIE_RED.light)
    # Turntable disc in front
    draw_shaded_rect(c, 6, y0 + 17, 17, y0 + 20, SUIT_DARK)
    c.set_px(10 + bounce, y0 + 18, FLUX_CYAN.highlight)
    apply_dark_outline(c)
    return c


def _draw_kuester_frame(offset_y: int = 0, staff_sway: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 26)
    y0 = 2 + offset_y
    # Brown monk robe with rope belt
    draw_shaded_rect(c, 5, y0 + 9, 14, y0 + 22, ROBE_BROWN)
    draw_shaded_rect(c, 5, y0 + 16, 14, y0 + 17, PAPER_CREAM)
    # Round glass diving helmet & brass collar with teal fish inside
    draw_shaded_ellipse(c, 9, y0 + 5, 5, 4, SHIELD_GLASS)
    draw_shaded_ellipse(c, 9, y0 + 5, 3, 2, FISH_TEAL)
    c.set_px(11, y0 + 5, DARK_INK)
    c.set_px(7, y0 + 3, WHITE_PX)
    draw_shaded_rect(c, 5, y0 + 8, 13, y0 + 10, BRASS_GOLD)
    # Tall golden crozier staff on the right
    sx = 17 + staff_sway
    draw_segment_line(c, sx, y0 + 3, sx, y0 + 22, BRASS_GOLD.mid, 1)
    draw_shaded_ellipse(c, sx, y0 + 2, 2, 2, BRASS_GOLD)
    apply_dark_outline(c)
    return c


def build_trader_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/npc_*.{png,json} (Card B05)."""
    paths: list[Path] = []

    def _pack(
        name: str,
        fn,
        anchor: tuple[int, int],
        glow: list[dict[str, object]],
    ) -> None:
        anims = {
            "idle": [fn(y, 0) for y in (0, 1, 0, -1)],
            "talk": [fn(0, 1), fn(-1, 2), fn(0, 0)],
            "offer": [fn(0, 2), fn(-1, 2)],
            "hurt": [fn(1, 0), fn(0, 0)],
        }
        p, j = save_sheet(
            "charaktere",
            name,
            anims,
            anchor=anchor,
            fps={"idle": 4.0, "talk": 8.0, "offer": 6.0, "hurt": 8.0},
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p, j])

    _pack("npc_magenhaendler", _draw_magenhaendler_frame, (12, 22), [{"offset": [14, 10], "color": [230, 185, 70], "radius": 10}])
    _pack("npc_sachbearbeiterin", _draw_sachbearbeiterin_frame, (11, 24), [{"offset": [10, 10], "color": [180, 210, 255], "radius": 10}])
    _pack("npc_glibberhaendler", _draw_glibberhaendler_frame, (12, 20), [{"offset": [12, 12], "color": [100, 235, 130], "radius": 12}])
    _pack("npc_ameisenhehler", _draw_ameisenhehler_frame, (12, 22), [{"offset": [12, 14], "color": [120, 235, 225], "radius": 10}])
    _pack("npc_dj", _draw_dj_frame, (12, 22), [{"offset": [12, 10], "color": [92, 236, 196], "radius": 14}])
    _pack("npc_kuester", _draw_kuester_frame, (11, 24), [{"offset": [9, 6], "color": [140, 215, 245], "radius": 12}])

    return paths
