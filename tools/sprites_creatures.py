"""Contract V8: Regular creature sprite builders across all 9 universes (Cards B06..B14)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from src.universes.catalog import ALL_UNIVERSES
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
# Color ramps (Bible 05)
# ---------------------------------------------------------------------------

DARK_INK = (24, 20, 32, 255)
WHITE_PX = (248, 248, 255, 255)

# Sporenklub
CAP_RED = make_ramp((204, 46, 54))
MUSH_STALK = make_ramp((224, 206, 178))
GILL_CREAM = make_ramp((236, 224, 198))
VEST_DARK = make_ramp((48, 46, 62))
WOOD_CLIP = make_ramp((156, 102, 56))
SHROOM_PALE = make_ramp((192, 186, 174))
HOOD_PURPLE = make_ramp((126, 68, 168))
NEON_CYAN = make_ramp((72, 238, 232))
PUFF_OCHRE = make_ramp((182, 134, 72))
NEON_LIME = make_ramp((126, 236, 78))
SPORE_PINK = make_ramp((236, 98, 192))
MOTH_BODY = make_ramp((64, 52, 84))
MOTH_MAGENTA = make_ramp((218, 66, 176))
MOTH_GOLD = make_ramp((242, 206, 74))

# Fleischwelt
MAGGOT_CREAM = make_ramp((226, 194, 166))
FLESH_PINK = make_ramp((214, 102, 114))
FLESH_DEEP = make_ramp((148, 46, 58))
JAW_RED = make_ramp((186, 38, 48))
LEECH_DARK = make_ramp((92, 28, 44))
BLOOD_RED = make_ramp((196, 36, 52))
ACID_GREEN = make_ramp((124, 238, 62))
VILLUS_PINK = make_ramp((224, 122, 136))

# Aktenhalde
PAPER_CREAM = make_ramp((234, 226, 204))
MANILA_TAN = make_ramp((206, 172, 108))
STEEL_CLIP = make_ramp((178, 186, 198))
POSTIT_YELLOW = make_ramp((244, 218, 72))
WOOD_STAMP = make_ramp((164, 106, 58))
BRASS_GOLD = make_ramp((218, 174, 56))
STAMP_RED = make_ramp((208, 42, 54))
SUIT_DARK = make_ramp((58, 64, 78))
SHIRT_WHITE = make_ramp((228, 232, 240))
GLASS_TINT = make_ramp((156, 206, 226))
COFFEE_DARK = make_ramp((76, 44, 32))

# Versunkene Abtei
ROBE_BROWN = make_ramp((128, 82, 52))
ROPE_TAN = make_ramp((198, 168, 112))
FISH_TEAL = make_ramp((76, 172, 186))
EEL_BLUE = make_ramp((68, 118, 168))
PIPE_SILVER = make_ramp((188, 198, 214))
BELL_CYAN = make_ramp((88, 214, 228))
CORAL_ROSE = make_ramp((218, 104, 118))
STONE_MOSS = make_ramp((104, 128, 122))
GLASS_RUBY = make_ramp((216, 54, 78))
GLASS_SAPPHIRE = make_ramp((64, 128, 226))
FLAME_GOLD = make_ramp((248, 194, 64))

# Kruemelreich
ANT_CRIMSON = make_ramp((176, 48, 44))
ANT_DARK = make_ramp((92, 34, 38))
MANDIBLE_IVORY = make_ramp((238, 226, 192))
APHID_GREEN = make_ramp((104, 208, 84))
MILK_CREAM = make_ramp((238, 242, 246))
ANT_BROWN = make_ramp((158, 96, 54))
CRUMB_GOLD = make_ramp((224, 178, 84))
BEETLE_DARK = make_ramp((66, 60, 82))
AMBER_GOLD = make_ramp((242, 168, 42))

# Glibbria (bright candy & jelly tones)
JELLY_PINK = make_ramp((236, 98, 152))
JELLY_CYAN = make_ramp((92, 228, 236))
JELLY_LIME = make_ramp((106, 224, 78))
GOO_YELLOW = make_ramp((246, 226, 76))
COTTON_PINK = make_ramp((242, 146, 198))
COTTON_BLUE = make_ramp((122, 198, 246))
PARTY_BLUE = make_ramp((76, 128, 228))
PARTY_GOLD = make_ramp((242, 192, 62))


# ---------------------------------------------------------------------------
# Sporenklub (Card B07): tuersteherpilz, sporenschnorrer, sporenwerfer, leuchtmotte
# ---------------------------------------------------------------------------


def _draw_tuersteherpilz(offset_y: int = 0, arm_action: int = 0, stomp: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 28)
    y0 = 2 + offset_y
    # Muscular stalk torso & dark club vest
    draw_shaded_rect(c, 7, y0 + 8, 16, y0 + 20, MUSH_STALK)
    draw_shaded_rect(c, 8, y0 + 10, 15, y0 + 19, VEST_DARK)
    draw_shaded_rect(c, 10, y0 + 11, 13, y0 + 18, MUSH_STALK)
    # Lamellae gill collar
    draw_shaded_rect(c, 6, y0 + 7, 17, y0 + 9, GILL_CREAM)
    # Broad red fly agaric cap with cream spots
    draw_shaded_ellipse(c, 12, y0 + 4, 9, 4, CAP_RED)
    for sx, sy in ((6, y0 + 3), (11, y0 + 2), (16, y0 + 3), (14, y0 + 5), (8, y0 + 5)):
        c.set_px(sx, sy, GILL_CREAM.highlight)
        c.set_px(sx + 1, sy, GILL_CREAM.light)
    # Cool club sunglasses with highlight glint
    draw_shaded_rect(c, 7, y0 + 5, 16, y0 + 6, DARK_INK_RAMP := VEST_DARK)
    for px in range(7, 17):
        c.set_px(px, y0 + 5, DARK_INK)
        c.set_px(px, y0 + 6, DARK_INK)
    c.set_px(9, y0 + 5, WHITE_PX)
    c.set_px(14, y0 + 5, WHITE_PX)
    _ = DARK_INK_RAMP
    # Guest-list clipboard held on left
    clip_y = y0 + 10 - (1 if stomp > 0 else 0)
    draw_shaded_rect(c, 2, clip_y, 6, clip_y + 7, WOOD_CLIP)
    draw_shaded_rect(c, 3, clip_y + 1, 5, clip_y + 6, PAPER_CREAM)
    c.set_px(4, clip_y, STEEL_CLIP.highlight)
    # Heavy pushing bouncer arm on right
    ax = min(22, 19 + arm_action)
    draw_segment_line(c, 16, y0 + 12, ax, y0 + 11 - (1 if arm_action else 0), MUSH_STALK.mid, 2)
    draw_shaded_ellipse(c, ax, y0 + 11 - (1 if arm_action else 0), 2, 2, MUSH_STALK)
    # Thick striding boots
    l_foot = max(4, 7 - stomp)
    r_foot = min(18, 14 + stomp)
    draw_shaded_rect(c, l_foot, y0 + 20, l_foot + 3, y0 + 23, VEST_DARK)
    draw_shaded_rect(c, r_foot, y0 + 20, r_foot + 3, y0 + 23, VEST_DARK)
    apply_dark_outline(c)
    return c


def _draw_sporenschnorrer(
    offset_y: int = 0, leg_stride: int = 0, hand_reach: int = 0
) -> PixelCanvas:
    c = PixelCanvas(18, 22)
    y0 = 2 + offset_y
    # Hunched pale stalk body
    draw_shaded_rect(c, 5, y0 + 7, 9, y0 + 14, SHROOM_PALE)
    # Crooked purple cap hood & glowing neon-cyan bald spot
    draw_shaded_ellipse(c, 7, y0 + 4, 4, 3, HOOD_PURPLE)
    c.set_px(5, y0 + 2, HOOD_PURPLE.shadow)
    c.set_px(7, y0 + 2, NEON_CYAN.highlight)
    c.set_px(8, y0 + 2, NEON_CYAN.light)
    c.set_px(9, y0 + 5, NEON_CYAN.rim)
    # Long greedy grasping arm reaching right
    reach_x = min(16, 12 + hand_reach + (2 if leg_stride > 0 else 0))
    draw_segment_line(c, 9, y0 + 9, reach_x, y0 + 10, SHROOM_PALE.light, 1)
    c.set_px(reach_x, y0 + 9, SHROOM_PALE.highlight)
    c.set_px(reach_x, y0 + 11, SHROOM_PALE.highlight)
    # Thin wide-stepping spindly legs
    lx = max(2, 5 - leg_stride)
    rx = min(14, 9 + leg_stride)
    draw_segment_line(c, 6, y0 + 14, lx, y0 + 18, SHROOM_PALE.shadow, 1)
    draw_segment_line(c, 8, y0 + 14, rx, y0 + 18, SHROOM_PALE.mid, 1)
    c.set_px(max(2, lx - 1), y0 + 18, HOOD_PURPLE.mid)
    c.set_px(min(15, rx + 1), y0 + 18, HOOD_PURPLE.mid)
    apply_dark_outline(c)
    return c


def _draw_sporenwerfer(offset_y: int = 0, squash: int = 0, charge: bool = False) -> PixelCanvas:
    c = PixelCanvas(24, 18)
    y0 = 2 + offset_y
    # Squat barrel puffball belly tilted horizontally
    draw_shaded_ellipse(c, 11, y0 + 8, 8, 4, PUFF_OCHRE)
    # Open crater rim & glowing neon-lime / magenta spore mass
    rim_w = 5 - (1 if charge else 0)
    draw_shaded_ellipse(c, 12, y0 + 3, rim_w, 2, HOOD_PURPLE)
    draw_shaded_ellipse(c, 12, y0 + 2, max(2, rim_w - 2), 2, NEON_LIME)
    c.set_px(11, y0 + 1, SPORE_PINK.highlight)
    c.set_px(13, y0 + 2, NEON_CYAN.highlight)
    if charge:
        c.set_px(12, max(1, y0 - 1), NEON_LIME.highlight)
        c.set_px(15, y0, SPORE_PINK.highlight)
    # Little eyes & wide creeping root-legs
    c.set_px(15, y0 + 7, DARK_INK)
    c.set_px(17, y0 + 7, DARK_INK)
    spread = abs(squash) * 2
    draw_segment_line(c, 6, y0 + 11, max(2, 3 - spread), y0 + 14, PUFF_OCHRE.shadow, 2)
    draw_segment_line(c, 16, y0 + 11, min(21, 19 + spread), y0 + 14, PUFF_OCHRE.shadow, 2)
    draw_shaded_rect(c, 9, y0 + 12, 13, y0 + 14, PUFF_OCHRE)
    apply_dark_outline(c)
    return c


def _draw_leuchtmotte(offset_y: int = 0, wing_spread: int = 0) -> PixelCanvas:
    c = PixelCanvas(26, 18)
    y0 = 3 + offset_y
    # Wing flap angle: high V-up when wing_spread > 0, low down-swept when < 0
    up_shift = -3 if wing_spread > 0 else (2 if wing_spread < 0 else 0)
    span = 9 if wing_spread > 0 else (7 if wing_spread < 0 else 8)
    # Left & right iridescent neon wings
    draw_shaded_ellipse(c, max(5, 12 - span + 3), y0 + 5 + up_shift, 4, 3, MOTH_MAGENTA)
    draw_shaded_ellipse(c, min(20, 13 + span - 3), y0 + 5 + up_shift, 4, 3, MOTH_MAGENTA)
    draw_shaded_ellipse(c, max(6, 12 - span + 4), y0 + 9 + (up_shift // 2), 3, 2, NEON_CYAN)
    draw_shaded_ellipse(c, min(19, 13 + span - 4), y0 + 9 + (up_shift // 2), 3, 2, NEON_CYAN)
    # Gold disco eye-spots on upper wings
    c.set_px(max(4, 12 - span + 2), y0 + 5 + up_shift, MOTH_GOLD.highlight)
    c.set_px(min(21, 13 + span - 2), y0 + 5 + up_shift, MOTH_GOLD.highlight)
    # Fluffy central thorax & abdomen
    draw_shaded_ellipse(c, 13, y0 + 7, 2, 5, MOTH_BODY)
    c.set_px(12, y0 + 4, MOTH_GOLD.highlight)
    c.set_px(14, y0 + 4, MOTH_GOLD.highlight)
    # Feathery V antennae
    draw_segment_line(c, 12, y0 + 3, 9, max(1, y0 - 1), MOTH_GOLD.light, 1)
    draw_segment_line(c, 14, y0 + 3, 17, max(1, y0 - 1), MOTH_GOLD.light, 1)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Fleischwelt (Card B08): fleischmade, blutegel, saeurespucker, zottenwurm
# ---------------------------------------------------------------------------


def _draw_fleischmade(offset_y: int = 0, worm_inch: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 14)
    y0 = 4 + offset_y
    arch = 2 if worm_inch > 0 else 0
    stretch = 1 if worm_inch < 0 else 0
    # Segmented pale-pink maggot arching in middle during inchworm crawl
    segs = [
        (4 - stretch, y0 + 4, 3, 2, MAGGOT_CREAM),
        (8, y0 + 4 - arch, 3, 3, FLESH_PINK),
        (12, y0 + 4 - arch, 3, 3, MAGGOT_CREAM),
        (16 + stretch, y0 + 4, 3, 3, FLESH_PINK),
    ]
    for sx, sy, rx, ry, ramp in segs:
        draw_shaded_ellipse(c, sx, sy, rx, ry, ramp)
    # Tiny pink bristle feet on belly
    c.set_px(5 - stretch, y0 + 7, FLESH_DEEP.mid)
    c.set_px(10, y0 + 7 - (1 if arch else 0), FLESH_DEEP.mid)
    c.set_px(15 + stretch, y0 + 7, FLESH_DEEP.mid)
    # Crimson biting mouth & twin white teeth on right head
    hx = 18 + stretch
    draw_shaded_rect(c, hx - 1, y0 + 3, hx + 1, y0 + 5, JAW_RED)
    c.set_px(min(20, hx + 1), y0 + 3, WHITE_PX)
    c.set_px(min(20, hx + 1), y0 + 5, WHITE_PX)
    c.set_px(hx - 1, y0 + 2, DARK_INK)
    apply_dark_outline(c)
    return c


def _draw_blutegel(
    offset_y: int = 0, suction_pulse: int = 0, vertical: bool = False
) -> PixelCanvas:
    c = PixelCanvas(16, 22)
    if vertical:
        # Hanging ceiling leech with serrated suction disk at bottom
        y0 = 2 + offset_y
        draw_shaded_rect(c, 6, y0, 10, y0 + 13 + suction_pulse, LEECH_DARK)
        draw_shaded_rect(c, 7, y0 + 2, 8, y0 + 11 + suction_pulse, BLOOD_RED)
        draw_shaded_ellipse(c, 8, y0 + 14 + suction_pulse, 4, 2, FLESH_PINK)
        c.set_px(7, y0 + 15 + suction_pulse, WHITE_PX)
        c.set_px(9, y0 + 15 + suction_pulse, WHITE_PX)
    else:
        # Upright sinuous S-curved leech rearing with ringed suction mouth on top-right
        y0 = 2 + offset_y
        sway = 2 if suction_pulse > 0 else (-2 if suction_pulse < 0 else 0)
        draw_shaded_ellipse(c, 7, y0 + 15, 5, 3, LEECH_DARK)
        draw_shaded_ellipse(c, 5 + sway // 2, y0 + 11, 3, 3, BLOOD_RED)
        draw_shaded_ellipse(c, 9 + sway, y0 + 7, 3, 3, LEECH_DARK)
        # Wet crimson specular highlight ridge
        c.set_px(6 + sway // 2, y0 + 10, FLESH_PINK.highlight)
        c.set_px(8 + sway, y0 + 6, FLESH_PINK.highlight)
        # Open toothed sucker ring at head
        hx = min(13, max(4, 11 + sway))
        draw_shaded_ellipse(c, hx, y0 + 4, 3, 2, FLESH_PINK)
        c.set_px(hx, y0 + 4, JAW_RED.shadow)
        c.set_px(hx - 1, y0 + 3, WHITE_PX)
        c.set_px(hx + 1, y0 + 3, WHITE_PX)
    apply_dark_outline(c)
    return c


def _draw_saeurespucker(offset_y: int = 0, sac_puff: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 20)
    y0 = 2 + offset_y
    puff = max(-1, min(1, sac_puff))
    # Ribbed pink flesh sac & glowing toxic-green acid bladder window
    draw_shaded_ellipse(c, 9, y0 + 9, 5 + puff, 5, FLESH_PINK)
    draw_shaded_ellipse(c, 9, y0 + 9, 3 + max(0, puff), 3, ACID_GREEN)
    c.set_px(8, y0 + 8, ACID_GREEN.highlight)
    # Projecting acid nozzle on right
    nx = 18 + max(0, puff)
    draw_segment_line(c, 13, y0 + 7, min(20, nx), y0 + 4, FLESH_DEEP.mid, 2)
    c.set_px(min(20, nx), y0 + 4, ACID_GREEN.highlight)
    # Eyes & splayed stubby flesh legs stepping in walk
    c.set_px(12, y0 + 7, DARK_INK)
    c.set_px(14, y0 + 7, DARK_INK)
    stride = sac_puff * 2
    draw_shaded_rect(c, max(2, 4 - stride), y0 + 13, max(4, 7 - stride), y0 + 16, FLESH_DEEP)
    draw_shaded_rect(c, min(16, 12 + stride), y0 + 13, min(19, 15 + stride), y0 + 16, FLESH_DEEP)
    apply_dark_outline(c)
    return c


def _draw_zottenwurm(offset_y: int = 0, wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 18)
    y0 = 4 + offset_y
    # Rippling coral-pink intestinal villus worm fringed with tall waving fronds
    for seg in range(5):
        sx = 4 + seg * 4
        w = wave if seg % 2 == 0 else -wave
        sy = y0 + 7 + (1 if w > 0 else (-1 if w < 0 else 0))
        draw_shaded_ellipse(c, sx, sy, 3, 3, VILLUS_PINK if seg % 2 == 0 else FLESH_PINK)
        # Tall finger-villi hair fronds swaying above/below
        frond_x = max(2, min(21, sx + (1 if w > 0 else (-1 if w < 0 else 0))))
        draw_segment_line(c, sx, sy - 2, frond_x, max(1, sy - 6 - (abs(w) // 2)), VILLUS_PINK.light, 1)
        c.set_px(frond_x, max(1, sy - 6 - (abs(w) // 2)), MAGGOT_CREAM.highlight)
        c.set_px(sx, min(15, sy + 4), FLESH_DEEP.mid)
    # Blind mouth slit on right segment
    c.set_px(21, y0 + 7, JAW_RED.shadow)
    c.set_px(21, y0 + 8, JAW_RED.mid)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Aktenhalde (Card B09): aktenfresser, stempler, paragraphenreiter, kaffeegolem
# ---------------------------------------------------------------------------


def _draw_aktenfresser(offset_y: int = 0, mouth_open: int = 0, foot_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 18)
    y0 = 3 + offset_y
    jaw = max(1, mouth_open + (1 if foot_stride != 0 else 0))
    # Manila file spine on left
    draw_shaded_rect(c, 3, y0 + 4, 6, y0 + 11, MANILA_TAN)
    # Upper & lower gaping folder jaws
    top_y = max(1, y0 + 2 - jaw)
    bot_y = min(13, y0 + 9 + (jaw // 2))
    draw_shaded_rect(c, 5, top_y, 18, top_y + 4, PAPER_CREAM)
    draw_shaded_rect(c, 5, bot_y, 18, bot_y + 3, MANILA_TAN)
    # Glaring eyes on folder tab & yellow post-it tongue
    c.set_px(13, top_y + 1, DARK_INK)
    c.set_px(16, top_y + 1, DARK_INK)
    draw_shaded_rect(c, 9, top_y + 4, 15, bot_y, POSTIT_YELLOW)
    # Jagged silver paperclip teeth
    for tx in (8, 12, 16):
        c.set_px(tx, top_y + 4, STEEL_CLIP.highlight)
        c.set_px(tx + 1, bot_y, STEEL_CLIP.light)
    # Scuttling folded paper-corner feet
    lf = max(2, 5 - foot_stride)
    rf = min(18, 14 + foot_stride)
    draw_segment_line(c, 7, bot_y + 3, lf, y0 + 13, PAPER_CREAM.shadow, 1)
    draw_segment_line(c, 15, bot_y + 3, rf, y0 + 13, PAPER_CREAM.shadow, 1)
    apply_dark_outline(c)
    return c


def _draw_stempler(offset_y: int = 0, stamp_lift: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 26)
    y0 = 2 + offset_y - min(1, stamp_lift // 2)
    # Turned wooden knob & brass ferrule spire (distinct hourglass stamp silhouette)
    draw_shaded_ellipse(c, 10, max(2, y0 + 3), 4, 3, WOOD_STAMP)
    draw_shaded_rect(c, 8, y0 + 6, 12, y0 + 11, WOOD_STAMP)
    draw_shaded_rect(c, 7, y0 + 11, 13, y0 + 13, BRASS_GOLD)
    # Wide flat stamp base plate & red ink-pad cushion
    draw_shaded_rect(c, 3, y0 + 13, 17, y0 + 15, WOOD_STAMP)
    draw_shaded_rect(c, 3, y0 + 16, 17, y0 + 17, STAMP_RED)
    c.set_px(6, y0 + 18, STAMP_RED.light)
    c.set_px(14, y0 + 18, STAMP_RED.light)
    # Tiny round glasses peering from collar
    c.set_px(8, y0 + 8, STEEL_CLIP.highlight)
    c.set_px(11, y0 + 8, STEEL_CLIP.highlight)
    c.set_px(9, y0 + 8, DARK_INK)
    c.set_px(12, y0 + 8, DARK_INK)
    # Mechanical spring legs striding wide
    lx = max(2, 6 - leg_stride)
    rx = min(17, 14 + leg_stride)
    draw_segment_line(c, 7, y0 + 17, lx, min(24, y0 + 21), STEEL_CLIP.mid, 1)
    draw_segment_line(c, 13, y0 + 17, rx, min(24, y0 + 21), STEEL_CLIP.mid, 1)
    draw_shaded_rect(c, max(2, lx - 1), min(23, y0 + 21), lx + 1, min(24, y0 + 22), SUIT_DARK)
    draw_shaded_rect(c, max(2, rx - 1), min(23, y0 + 21), min(18, rx + 1), min(24, y0 + 22), SUIT_DARK)
    apply_dark_outline(c)
    return c


def _draw_paragraphenreiter(offset_y: int = 0, wing_flutter: int = 0) -> PixelCanvas:
    c = PixelCanvas(26, 24)
    y0 = 2 + offset_y
    tilt = 1 if wing_flutter > 0 else (-1 if wing_flutter < 0 else 0)
    # Ornate golden brass paragraph (§) mount with flapping paper wings
    draw_shaded_ellipse(c, 11, y0 + 10, 4, 3, BRASS_GOLD)
    draw_shaded_ellipse(c, 11, y0 + 16, 4, 3, BRASS_GOLD)
    draw_shaded_ellipse(c, 11, y0 + 13, 3, 2, PAPER_CREAM)
    # Paper wings flapping wide in walk
    wing_span = 4 + abs(wing_flutter)
    draw_shaded_rect(c, max(2, 6 - wing_span), y0 + 11 - tilt, 7, y0 + 14 - tilt, PAPER_CREAM)
    draw_shaded_rect(c, 15, y0 + 11 + tilt, min(22, 16 + wing_span), y0 + 14 + tilt, PAPER_CREAM)
    # Tiny suited bureaucrat rider with red tie & pen lance
    draw_shaded_rect(c, 9, y0 + 4, 13, y0 + 9, SUIT_DARK)
    draw_shaded_ellipse(c, 11, y0 + 3, 2, 2, PAPER_CREAM)
    c.set_px(11, y0 + 6, STAMP_RED.light)
    lance_x = min(24, 19 + abs(wing_flutter))
    draw_segment_line(c, 12, y0 + 7, lance_x, max(1, y0 + 2 - tilt), STEEL_CLIP.highlight, 1)
    c.set_px(lance_x, max(1, y0 + 2 - tilt), STAMP_RED.highlight)
    apply_dark_outline(c)
    return c


def _draw_kaffeegolem(offset_y: int = 0, steam_bubble: int = 0, stomp: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 28)
    y0 = 3 + offset_y
    # Top lid & rising white steam wisps
    draw_shaded_rect(c, 6, y0 + 2, 17, y0 + 5, SUIT_DARK)
    c.set_px(9, max(1, y0 - (abs(steam_bubble) % 2)), WHITE_PX)
    c.set_px(13, max(1, y0 - 1 + (abs(steam_bubble) % 2)), SHIRT_WHITE.highlight)
    # Chrome steel frame + translucent glass carafe with sloshing espresso
    draw_shaded_rect(c, 5, y0 + 5, 18, y0 + 18, STEEL_CLIP)
    draw_shaded_rect(c, 7, y0 + 7, 16, y0 + 15, GLASS_TINT)
    draw_shaded_rect(c, 7, y0 + 10, 16, y0 + 15, COFFEE_DARK)
    c.set_px(8, y0 + 8, WHITE_PX)
    c.set_px(15, y0 + 17, STAMP_RED.highlight)  # Power LED
    # Spout handle left & arm right swinging in stride
    swing = 2 if stomp > 0 else (-1 if stomp < 0 else 0)
    draw_segment_line(c, 5, y0 + 8, max(2, 2 - abs(swing)), y0 + 11, SUIT_DARK.mid, 2)
    draw_segment_line(c, 18, y0 + 9, min(22, 20 + swing), y0 + 12, STEEL_CLIP.mid, 2)
    # Heavy boxy legs striding
    lx = max(3, 6 - stomp)
    rx = min(17, 13 + stomp)
    draw_shaded_rect(c, lx, y0 + 18, lx + 3, y0 + 23, SUIT_DARK)
    draw_shaded_rect(c, rx, y0 + 18, rx + 3, y0 + 23, SUIT_DARK)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Versunkene Abtei (Card B11): moenchsfisch, orgelaal, glockenqualle, korallenwaechter
# ---------------------------------------------------------------------------


def _draw_moenchsfisch(offset_y: int = 0, fin_flutter: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    y0 = 2 + offset_y
    # Pointed brown monk hood & flowing robe with rope belt
    draw_shaded_ellipse(c, 10, y0 + 4, 4, 3, ROBE_BROWN)
    c.set_px(8, y0 + 1, ROBE_BROWN.shadow)
    draw_shaded_rect(c, 6, y0 + 7, 14, y0 + 16, ROBE_BROWN)
    draw_shaded_rect(c, 6, y0 + 11, 14, y0 + 12, ROPE_TAN)
    # Teal scaly fish face peering out of hood & gold eye
    draw_shaded_ellipse(c, 11, y0 + 5, 3, 2, FISH_TEAL)
    c.set_px(12, y0 + 4, FLAME_GOLD.highlight)
    c.set_px(14, y0 + 6, FISH_TEAL.light)
    # Small prayer scroll / censer held out right
    c.set_px(15, y0 + 9, ROPE_TAN.highlight)
    draw_shaded_rect(c, 14, y0 + 10, 17, y0 + 12, BRASS_GOLD)
    # Swishing teal fish tail protruding from under hem
    tail_x = max(3, min(16, 10 + fin_flutter))
    draw_shaded_ellipse(c, tail_x, y0 + 18, 3, 2, FISH_TEAL)
    c.set_px(max(2, tail_x - 3), y0 + 19, FISH_TEAL.light)
    c.set_px(min(18, tail_x + 3), y0 + 19, FISH_TEAL.light)
    apply_dark_outline(c)
    return c


def _draw_orgelaal(offset_y: int = 0, pipe_shift: int = 0) -> PixelCanvas:
    c = PixelCanvas(28, 16)
    y0 = 4 + offset_y
    # Long sinuous slate-blue eel body undulating across width
    for seg in range(6):
        sx = 3 + seg * 4
        wave = 1 if (seg + pipe_shift) % 2 == 0 else -1
        sy = y0 + 7 + (wave if pipe_shift != 0 else 0)
        draw_shaded_ellipse(c, sx, sy, 3, 2, EEL_BLUE)
        # Shining vertical silver/brass organ pipes along back
        if seg < 5:
            h = 4 + (seg % 3) + (1 if (pipe_shift > 0 and seg % 2 == 0) else 0)
            ramp = PIPE_SILVER if seg % 2 == 0 else BRASS_GOLD
            draw_shaded_rect(c, sx - 1, max(1, sy - h), sx + 1, sy - 1, ramp)
            c.set_px(sx, max(1, sy - h), ramp.highlight)
    # Eel head with golden eye & gaping snout on right
    hx = 24
    hy = y0 + 6 + (1 if pipe_shift > 0 else (-1 if pipe_shift < 0 else 0))
    draw_shaded_ellipse(c, hx, hy, 3, 3, FISH_TEAL)
    c.set_px(hx + 1, hy - 1, FLAME_GOLD.highlight)
    apply_dark_outline(c)
    return c


def _draw_glockenqualle(offset_y: int = 0, tentacle_pulse: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    y0 = 2 + offset_y
    # Bioluminescent cyan cathedral bell dome with brass rim & glowing clapper
    draw_shaded_ellipse(c, 10, y0 + 6, 6, 5, BELL_CYAN)
    draw_shaded_rect(c, 4, y0 + 9, 16, y0 + 10, BRASS_GOLD)
    draw_shaded_rect(c, 9, y0 + 7, 11, y0 + 11, FLAME_GOLD)
    c.set_px(8, y0 + 4, WHITE_PX)
    # Long trailing glowing tentacles swaying wide left/right in walk
    sway = tentacle_pulse
    for idx, tx in enumerate((5, 8, 12, 15)):
        dir_sway = sway if idx < 2 else -sway
        end_x = max(2, min(17, tx + dir_sway))
        end_y = y0 + 19 + (1 if idx in (1, 2) else 0)
        draw_segment_line(c, tx, y0 + 11, end_x, end_y, BELL_CYAN.light, 1)
        c.set_px(end_x, end_y, FLAME_GOLD.highlight)
    apply_dark_outline(c)
    return c


def _draw_korallenwaechter(
    offset_y: int = 0, shield_raise: int = 0, claw_walk: int = 0
) -> PixelCanvas:
    c = PixelCanvas(22, 26)
    y0 = 2 + offset_y
    # Beeswax candle + golden flame atop helm
    draw_shaded_rect(c, 9, y0 + 3, 11, y0 + 6, PAPER_CREAM)
    c.set_px(10, y0 + 1, FLAME_GOLD.highlight)
    c.set_px(10, y0 + 2, STAMP_RED.light)
    # Jagged coral-rose stone body with colorful stained-glass chest rosette
    draw_shaded_ellipse(c, 10, y0 + 12, 6, 6, CORAL_ROSE)
    draw_shaded_rect(c, 8, y0 + 10, 12, y0 + 14, STONE_MOSS)
    c.set_px(10, y0 + 12, FLAME_GOLD.highlight)
    c.set_px(9, y0 + 11, GLASS_RUBY.light)
    c.set_px(11, y0 + 11, GLASS_SAPPHIRE.light)
    c.set_px(9, y0 + 13, GLASS_SAPPHIRE.light)
    c.set_px(11, y0 + 13, GLASS_RUBY.light)
    # Coral halberd / stained-glass shield raised on right
    sh_y = y0 + 10 - shield_raise
    draw_segment_line(c, 17, sh_y - 4, 17, y0 + 17, STONE_MOSS.light, 1)
    draw_shaded_rect(c, 16, sh_y - 4, 19, sh_y + 1, GLASS_SAPPHIRE)
    # Crab-like stone legs marching wide
    lx = max(2, 5 - claw_walk)
    rx = min(18, 15 + claw_walk)
    draw_segment_line(c, 7, y0 + 17, lx, y0 + 22, STONE_MOSS.mid, 2)
    draw_segment_line(c, 13, y0 + 17, rx, y0 + 22, STONE_MOSS.mid, 2)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Kruemelreich (Card B12): ameisenkrieger, blattlaus, arbeiterameise, harzspucker
# ---------------------------------------------------------------------------


def _draw_ameisenkrieger(offset_y: int = 0, spear_jab: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 18)
    y0 = 2 + offset_y
    # 3 distinct segmented crimson soldier ant body (gaster, thorax, armored head)
    draw_shaded_ellipse(c, 5, y0 + 9, 3, 3, ANT_CRIMSON)
    draw_shaded_ellipse(c, 10, y0 + 8, 2, 2, ANT_DARK)
    draw_shaded_ellipse(c, 15, y0 + 7, 3, 3, ANT_CRIMSON)
    c.set_px(16, y0 + 6, FLAME_GOLD.highlight)
    # Serrated gleaming ivory mandibles & bent antennae
    jaw_open = 1 if (spear_jab > 0 or leg_stride != 0) else 0
    mand_x = min(22, 20 + spear_jab)
    draw_segment_line(c, 17, y0 + 7, mand_x, y0 + 5 - jaw_open, MANDIBLE_IVORY.highlight, 1)
    draw_segment_line(c, 17, y0 + 9, mand_x, y0 + 10 + jaw_open, MANDIBLE_IVORY.light, 1)
    draw_segment_line(c, 15, y0 + 4, 17, max(1, y0 + 1), ANT_DARK.mid, 1)
    # 6 chitin legs striding
    l1 = max(2, 4 - leg_stride)
    l2 = min(20, 14 + leg_stride)
    draw_segment_line(c, 8, y0 + 10, l1, y0 + 14, ANT_DARK.shadow, 1)
    draw_segment_line(c, 10, y0 + 10, 10, y0 + 14, ANT_DARK.mid, 1)
    draw_segment_line(c, 12, y0 + 10, l2, y0 + 14, ANT_DARK.mid, 1)
    apply_dark_outline(c)
    return c


def _draw_blattlaus(offset_y: int = 0, crawl: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 16)
    y0 = 2 + offset_y
    # Plump leaf-green pear-shaped aphid body with milk-droplet bucket marking
    draw_shaded_ellipse(c, 8, y0 + 7, 5, 4, APHID_GREEN)
    draw_shaded_ellipse(c, 13, y0 + 8, 2, 2, APHID_GREEN)
    # Milk-droplet mark on round back + twin cornicle tubes
    draw_shaded_rect(c, 6, y0 + 5, 9, y0 + 7, MILK_CREAM)
    c.set_px(7, y0 + 4, WHITE_PX)
    draw_segment_line(c, 4, y0 + 5, max(2, 2 - abs(crawl // 2)), max(1, y0 + 2), APHID_GREEN.shadow, 1)
    c.set_px(14, y0 + 7, DARK_INK)
    # Short pattering legs extending on stride
    l1 = max(2, 5 - crawl)
    l2 = min(16, 13 + crawl)
    draw_segment_line(c, 6, y0 + 11, l1, y0 + 12, APHID_GREEN.shadow, 1)
    draw_segment_line(c, 12, y0 + 11, l2, y0 + 12, APHID_GREEN.shadow, 1)
    apply_dark_outline(c)
    return c


def _draw_arbeiterameise(offset_y: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 22)
    y0 = 2 + offset_y
    # Oversized golden biscuit crumb hoisted high above thorax
    crumb_tilt = 1 if leg_stride > 0 else (-1 if leg_stride < 0 else 0)
    draw_shaded_ellipse(c, 10, y0 + 4 + crumb_tilt, 6, 4, CRUMB_GOLD)
    c.set_px(7, y0 + 3 + crumb_tilt, MANDIBLE_IVORY.highlight)
    c.set_px(12, y0 + 5 + crumb_tilt, WOOD_STAMP.mid)
    # Warm brown 3-segment worker ant carrying load
    draw_shaded_ellipse(c, 5, y0 + 12, 3, 2, ANT_BROWN)
    draw_shaded_ellipse(c, 10, y0 + 11, 2, 2, ANT_BROWN)
    draw_shaded_ellipse(c, 15, y0 + 12, 2, 2, ANT_BROWN)
    c.set_px(16, y0 + 11, DARK_INK)
    draw_segment_line(c, 11, y0 + 10, 9, y0 + 7, ANT_BROWN.shadow, 1)
    draw_segment_line(c, 13, y0 + 10, 14, y0 + 7, ANT_BROWN.shadow, 1)
    # Scurrying legs
    lx = max(2, 4 - leg_stride)
    rx = min(19, 16 + leg_stride)
    draw_segment_line(c, 8, y0 + 13, lx, y0 + 18, ANT_DARK.mid, 1)
    draw_segment_line(c, 11, y0 + 13, 11, y0 + 18, ANT_DARK.mid, 1)
    draw_segment_line(c, 14, y0 + 13, rx, y0 + 18, ANT_DARK.mid, 1)
    apply_dark_outline(c)
    return c


def _draw_harzspucker(offset_y: int = 0, amber_glow: bool = False, recoil: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 20)
    y0 = 2 + offset_y
    # Glowing translucent amber-gold resin tank abdomen tilted up-left
    draw_shaded_ellipse(c, 7, y0 + 7, 5, 4, AMBER_GOLD)
    c.set_px(5, y0 + 5, WHITE_PX if amber_glow else AMBER_GOLD.highlight)
    c.set_px(7, y0 + 6, FLAME_GOLD.highlight)
    # Low armored dark beetle head & forward spitter snout on right
    draw_shaded_ellipse(c, 14, y0 + 11, 3, 3, BEETLE_DARK)
    draw_shaded_rect(c, 16, y0 + 10, 19, y0 + 12, BEETLE_DARK)
    c.set_px(15, y0 + 10, FLAME_GOLD.highlight)
    if amber_glow:
        c.set_px(20, y0 + 11, AMBER_GOLD.highlight)
    # Braced splayed beetle legs stepping in walk
    lx = max(2, 5 - recoil)
    rx = min(19, 15 + recoil)
    draw_segment_line(c, 7, y0 + 11, lx, y0 + 15, BEETLE_DARK.shadow, 2)
    draw_segment_line(c, 13, y0 + 13, rx, y0 + 15, BEETLE_DARK.mid, 2)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Glibbria (Card B14): huepfling, glibberteiler, zuckerwatte_wolke, konfetti_kanone
# ---------------------------------------------------------------------------


def _draw_huepfling(offset_y: int = 0, squash: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 18)
    y0 = 2 + offset_y
    # Pointed teardrop strawberry-pink jelly dome with glossy cyan rim & strawberry core
    rx = 5 + (1 if squash > 0 else (-1 if squash < 0 else 0))
    ry = 4 + (1 if squash < 0 else 0)
    cy = y0 + 8
    draw_shaded_ellipse(c, 9, cy, rx, ry, JELLY_PINK)
    # Teardrop tip on top
    tip_y = max(1, cy - ry - 2)
    draw_segment_line(c, 9, tip_y, 9, cy - ry, JELLY_PINK.light, 2)
    c.set_px(9, tip_y, JELLY_CYAN.highlight)
    # Floating strawberry & leaf inside jelly
    c.set_px(9, cy + 1, CAP_RED.mid)
    c.set_px(8, cy + 1, CAP_RED.light)
    c.set_px(9, cy, JELLY_LIME.light)
    # Glossy shine & expressive eyes
    c.set_px(6, cy - 2, WHITE_PX)
    c.set_px(7, cy - 1, DARK_INK)
    c.set_px(11, cy - 1, DARK_INK)
    # Extending jelly drip feet on bounce/squash frames
    if squash < 0:
        draw_shaded_rect(c, 7, cy + ry, 8, min(16, cy + ry + 2), JELLY_PINK)
        draw_shaded_rect(c, 10, cy + ry, 11, min(16, cy + ry + 2), JELLY_PINK)
    elif squash > 0:
        draw_shaded_rect(c, 2, cy + 2, 4, cy + 4, JELLY_PINK)
        draw_shaded_rect(c, 14, cy + 2, 16, cy + 4, JELLY_PINK)
    apply_dark_outline(c)
    return c


def _draw_glibberteiler(offset_y: int = 0, split_gap: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 18)
    y0 = 3 + offset_y
    if split_gap >= 3:
        # Pulling apart into two sour-lime halves with glowing neon-yellow bridge
        shift = min(3, split_gap)
        draw_shaded_ellipse(c, max(5, 7 - shift), y0 + 7, 4, 4, JELLY_LIME)
        draw_shaded_ellipse(c, min(16, 14 + shift), y0 + 7, 4, 4, JELLY_LIME)
        draw_segment_line(c, 9, y0 + 7, 13, y0 + 7, GOO_YELLOW.highlight, 1)
        c.set_px(max(4, 6 - shift), y0 + 6, DARK_INK)
        c.set_px(min(17, 15 + shift), y0 + 6, DARK_INK)
    else:
        # Angry sour-lime jelly body with deep glowing split seam & pseudopod arms
        stretch = 1 if split_gap >= 2 else 0
        draw_shaded_rect(c, 4 - stretch, y0 + 4, 17 + stretch, y0 + 11, JELLY_LIME)
        draw_shaded_ellipse(c, 7 - stretch, y0 + 5, 3, 2, JELLY_LIME)
        draw_shaded_ellipse(c, 14 + stretch, y0 + 5, 3, 2, JELLY_LIME)
        # Glowing vertical division crack & gummy fangs
        for sy in range(y0 + 3, y0 + 12):
            c.set_px(10, sy, GOO_YELLOW.highlight if sy % 2 == 0 else JELLY_PINK.light)
            if stretch:
                c.set_px(11, sy, GOO_YELLOW.light)
        c.set_px(7 - stretch, y0 + 6, DARK_INK)
        c.set_px(14 + stretch, y0 + 6, DARK_INK)
        c.set_px(8 - stretch, y0 + 9, WHITE_PX)
        c.set_px(13 + stretch, y0 + 9, WHITE_PX)
        if split_gap != 0:
            draw_segment_line(c, 4 - stretch, y0 + 8, max(1, 2 - stretch), y0 + 12, JELLY_LIME.mid, 2)
            draw_segment_line(
                c, 17 + stretch, y0 + 8, min(20, 19 + stretch), y0 + 12, JELLY_LIME.mid, 2
            )
    apply_dark_outline(c)
    return c


def _draw_zuckerwatte_wolke(offset_y: int = 0, puff: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 20)
    y0 = 2 + offset_y
    # Rolled cream paper cone handle dangling underneath
    draw_segment_line(c, 12, y0 + 10, 12, y0 + 16, PAPER_CREAM.light, 2)
    c.set_px(12, y0 + 16, MANILA_TAN.mid)
    # Swirling pastel pink & baby-blue fluffy cotton-candy puffs
    drift = 2 if puff > 0 else (-1 if puff < 0 else 0)
    draw_shaded_ellipse(c, 12, y0 + 6, 7 + max(0, drift), 4, COTTON_PINK)
    draw_shaded_ellipse(c, max(5, 7 - abs(drift)), y0 + 7, 4, 3, COTTON_BLUE)
    draw_shaded_ellipse(c, min(18, 17 + abs(drift)), y0 + 7, 4, 3, COTTON_PINK)
    draw_shaded_ellipse(c, 12, y0 + 4, 4, 3, COTTON_BLUE)
    # Mischievous sleepy eyes & rosy swirl highlight
    c.set_px(9, y0 + 6, DARK_INK)
    c.set_px(10, y0 + 6, DARK_INK)
    c.set_px(14, y0 + 6, DARK_INK)
    c.set_px(15, y0 + 6, DARK_INK)
    c.set_px(8, y0 + 3, WHITE_PX)
    apply_dark_outline(c)
    return c


def _draw_konfetti_kanone(
    offset_y: int = 0, fuse_spark: int = 0, leg_stride: int = 0
) -> PixelCanvas:
    c = PixelCanvas(24, 20)
    y0 = 2 + offset_y
    kick = 1 if (fuse_spark > 0 or leg_stride > 0) else 0
    # Festive striped party-cannon barrel tilted up-right
    draw_shaded_rect(c, 6 - kick, y0 + 5, 16 - kick, y0 + 11, PARTY_BLUE)
    draw_shaded_rect(c, 9 - kick, y0 + 5, 11 - kick, y0 + 11, PARTY_GOLD)
    draw_shaded_rect(c, 13 - kick, y0 + 5, 15 - kick, y0 + 11, JELLY_PINK)
    # Flared brass muzzle on right & confetti burst pixels
    draw_shaded_rect(c, 16 - kick, y0 + 4, 19 - kick, y0 + 12, PARTY_GOLD)
    if fuse_spark > 0 or leg_stride != 0:
        c.set_px(min(22, 21 - kick), y0 + 5, JELLY_CYAN.highlight)
        c.set_px(min(22, 22 - kick), y0 + 8, JELLY_PINK.highlight)
        c.set_px(min(22, 20 - kick), y0 + 10, JELLY_LIME.highlight)
    # Lit fuse cord + spark on left breech
    fuse_x = max(2, 4 - kick - (fuse_spark % 2))
    draw_segment_line(c, 6 - kick, y0 + 7, fuse_x, y0 + 4, ROPE_TAN.mid, 1)
    c.set_px(fuse_x, y0 + 4, FLAME_GOLD.highlight)
    # Rolling carriage wheels (shift together so wheelbase never collapses)
    roll = max(-2, min(2, leg_stride))
    wx1 = 7 + roll
    wx2 = 15 + roll
    draw_shaded_ellipse(c, wx1, y0 + 14, 3, 2, WOOD_STAMP)
    draw_shaded_ellipse(c, wx2, y0 + 14, 3, 2, WOOD_STAMP)
    c.set_px(wx1, y0 + 14, PARTY_GOLD.highlight)
    c.set_px(wx2, y0 + 14, PARTY_GOLD.highlight)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Dispatcher & Sheet Builder
# ---------------------------------------------------------------------------


def build_creature_sheets(
    out_dir: Path = ASSET_ROOT,
    universe_key: str | None = None,
) -> list[Path]:
    """Build kreaturen/<species>.{png,json} for universe_key (or all universes if None)."""
    targets = [universe_key] if universe_key else list(ALL_UNIVERSES.keys())
    paths: list[Path] = []

    for u_key in targets:
        if u_key not in ALL_UNIVERSES:
            continue
        u = ALL_UNIVERSES[u_key]

        for spawn in u.creatures:
            species = spawn.species

            if species == "tuersteherpilz":
                idle = [_draw_tuersteherpilz(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_tuersteherpilz(0, 0, 0),
                    _draw_tuersteherpilz(-1, 2, 3),
                    _draw_tuersteherpilz(0, 0, 0),
                    _draw_tuersteherpilz(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_tuersteherpilz(-1, 1), _draw_tuersteherpilz(0, 2)],
                    "attack": [_draw_tuersteherpilz(1, 3), _draw_tuersteherpilz(0, 0)],
                    "hurt": [_draw_tuersteherpilz(1), _draw_tuersteherpilz(0)],
                }
                glow = []
            elif species == "sporenschnorrer":
                idle = [_draw_sporenschnorrer(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_sporenschnorrer(0, 0),
                    _draw_sporenschnorrer(-1, 3),
                    _draw_sporenschnorrer(0, 0),
                    _draw_sporenschnorrer(1, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_sporenschnorrer(-1, 0, 1), _draw_sporenschnorrer(0, 0, 2)],
                    "attack": [_draw_sporenschnorrer(1, 0, 3), _draw_sporenschnorrer(0, 0, 0)],
                    "hurt": [_draw_sporenschnorrer(1), _draw_sporenschnorrer(0)],
                }
                glow = []
            elif species == "sporenwerfer":
                idle = [_draw_sporenwerfer(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_sporenwerfer(0, 0),
                    _draw_sporenwerfer(-1, 2),
                    _draw_sporenwerfer(0, 0),
                    _draw_sporenwerfer(1, -1),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_sporenwerfer(-1, 0, True), _draw_sporenwerfer(0, 0, True)],
                    "attack": [_draw_sporenwerfer(1, 0, False), _draw_sporenwerfer(0, 0, False)],
                    "hurt": [_draw_sporenwerfer(1), _draw_sporenwerfer(0)],
                }
                glow = [{"offset": [12, 4], "color": list(NEON_LIME.highlight[:3]), "radius": 12}]
            elif species == "leuchtmotte":
                idle = [_draw_leuchtmotte(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_leuchtmotte(0, 0),
                    _draw_leuchtmotte(-1, 3),
                    _draw_leuchtmotte(0, 0),
                    _draw_leuchtmotte(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_leuchtmotte(-1, 1), _draw_leuchtmotte(0, 2)],
                    "attack": [_draw_leuchtmotte(1, 2), _draw_leuchtmotte(0, 0)],
                    "hurt": [_draw_leuchtmotte(1), _draw_leuchtmotte(0)],
                }
                glow = [{"offset": [13, 8], "color": list(MOTH_MAGENTA.highlight[:3]), "radius": 14}]
            elif species == "fleischmade":
                idle = [_draw_fleischmade(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_fleischmade(0, 0),
                    _draw_fleischmade(0, 2),
                    _draw_fleischmade(0, 0),
                    _draw_fleischmade(0, -1),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_fleischmade(-1, 1), _draw_fleischmade(0, 2)],
                    "attack": [_draw_fleischmade(1, 2), _draw_fleischmade(0, 0)],
                    "hurt": [_draw_fleischmade(1), _draw_fleischmade(0)],
                    "burrow_out": [_draw_fleischmade(2), _draw_fleischmade(0)],
                }
                glow = []
            elif species == "blutegel":
                idle = [_draw_blutegel(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_blutegel(0, 0),
                    _draw_blutegel(-1, 2),
                    _draw_blutegel(0, 0),
                    _draw_blutegel(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_blutegel(-1, 1), _draw_blutegel(0, 2)],
                    "attack": [_draw_blutegel(1, 2), _draw_blutegel(0, 0)],
                    "hurt": [_draw_blutegel(1), _draw_blutegel(0)],
                    "hang": [_draw_blutegel(0, 0, True), _draw_blutegel(1, 1, True)],
                    "latched": [_draw_blutegel(0, 2, False)],
                }
                glow = []
            elif species == "saeurespucker":
                idle = [_draw_saeurespucker(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_saeurespucker(0, 0),
                    _draw_saeurespucker(-1, 2),
                    _draw_saeurespucker(0, 0),
                    _draw_saeurespucker(1, -1),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_saeurespucker(-1, 2), _draw_saeurespucker(0, 2)],
                    "attack": [_draw_saeurespucker(1, 0), _draw_saeurespucker(0, 0)],
                    "hurt": [_draw_saeurespucker(1), _draw_saeurespucker(0)],
                }
                glow = [{"offset": [10, 10], "color": list(ACID_GREEN.highlight[:3]), "radius": 12}]
            elif species == "zottenwurm":
                idle = [_draw_zottenwurm(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_zottenwurm(0, 0),
                    _draw_zottenwurm(-1, 2),
                    _draw_zottenwurm(0, 0),
                    _draw_zottenwurm(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_zottenwurm(-1, 1), _draw_zottenwurm(0, 2)],
                    "attack": [_draw_zottenwurm(1, 2), _draw_zottenwurm(0, 0)],
                    "hurt": [_draw_zottenwurm(1), _draw_zottenwurm(0)],
                }
                glow = []
            elif species == "aktenfresser":
                idle = [_draw_aktenfresser(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_aktenfresser(0, 0, 0),
                    _draw_aktenfresser(-1, 1, 3),
                    _draw_aktenfresser(0, 0, 0),
                    _draw_aktenfresser(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_aktenfresser(-1, 1), _draw_aktenfresser(0, 2)],
                    "attack": [_draw_aktenfresser(1, 3), _draw_aktenfresser(0, 0)],
                    "hurt": [_draw_aktenfresser(1), _draw_aktenfresser(0)],
                    "dig": [_draw_aktenfresser(0, 2, 2), _draw_aktenfresser(1, 3, -1)],
                }
                glow = []
            elif species == "stempler":
                idle = [_draw_stempler(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_stempler(0, 0, 0),
                    _draw_stempler(-1, 1, 3),
                    _draw_stempler(0, 0, 0),
                    _draw_stempler(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_stempler(-1, 2), _draw_stempler(0, 3)],
                    "attack": [_draw_stempler(1, -1), _draw_stempler(0, 0)],
                    "hurt": [_draw_stempler(1), _draw_stempler(0)],
                    "stamp": [_draw_stempler(-1, 3), _draw_stempler(1, -1)],
                }
                glow = []
            elif species == "paragraphenreiter":
                idle = [_draw_paragraphenreiter(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_paragraphenreiter(0, 0),
                    _draw_paragraphenreiter(-1, 3),
                    _draw_paragraphenreiter(0, 0),
                    _draw_paragraphenreiter(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_paragraphenreiter(-1, 1), _draw_paragraphenreiter(0, 2)],
                    "attack": [_draw_paragraphenreiter(1, 3), _draw_paragraphenreiter(0, 0)],
                    "hurt": [_draw_paragraphenreiter(1), _draw_paragraphenreiter(0)],
                }
                glow = [{"offset": [19, 6], "color": list(BRASS_GOLD.highlight[:3]), "radius": 12}]
            elif species == "kaffeegolem":
                idle = [_draw_kaffeegolem(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_kaffeegolem(0, 0, 0),
                    _draw_kaffeegolem(-1, 1, 3),
                    _draw_kaffeegolem(0, 0, 0),
                    _draw_kaffeegolem(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_kaffeegolem(-1, 2), _draw_kaffeegolem(0, 2)],
                    "attack": [_draw_kaffeegolem(1, 0), _draw_kaffeegolem(0, 0)],
                    "hurt": [_draw_kaffeegolem(1), _draw_kaffeegolem(0)],
                }
                glow = []
            elif species == "moenchsfisch":
                idle = [_draw_moenchsfisch(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_moenchsfisch(0, 0),
                    _draw_moenchsfisch(-1, 3),
                    _draw_moenchsfisch(0, 0),
                    _draw_moenchsfisch(1, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_moenchsfisch(-1, 1), _draw_moenchsfisch(0, 2)],
                    "attack": [_draw_moenchsfisch(1, 3), _draw_moenchsfisch(0, 0)],
                    "hurt": [_draw_moenchsfisch(1), _draw_moenchsfisch(0)],
                }
                glow = []
            elif species == "orgelaal":
                idle = [_draw_orgelaal(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_orgelaal(0, 0),
                    _draw_orgelaal(-1, 2),
                    _draw_orgelaal(0, 0),
                    _draw_orgelaal(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_orgelaal(-1, 1), _draw_orgelaal(0, 2)],
                    "attack": [_draw_orgelaal(1, 2), _draw_orgelaal(0, 0)],
                    "hurt": [_draw_orgelaal(1), _draw_orgelaal(0)],
                    "swim": [_draw_orgelaal(y, idx % 2) for idx, y in enumerate((-1, 0, 1, 0))],
                }
                glow = []
            elif species == "glockenqualle":
                idle = [_draw_glockenqualle(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_glockenqualle(0, 0),
                    _draw_glockenqualle(-1, 3),
                    _draw_glockenqualle(0, 0),
                    _draw_glockenqualle(1, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_glockenqualle(-1, 1), _draw_glockenqualle(0, 2)],
                    "attack": [_draw_glockenqualle(1, 3), _draw_glockenqualle(0, 0)],
                    "hurt": [_draw_glockenqualle(1), _draw_glockenqualle(0)],
                }
                glow = [{"offset": [10, 9], "color": list(BELL_CYAN.highlight[:3]), "radius": 14}]
            elif species == "korallenwaechter":
                idle = [_draw_korallenwaechter(y, 0, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_korallenwaechter(0, 0, 0),
                    _draw_korallenwaechter(-1, 1, 3),
                    _draw_korallenwaechter(0, 0, 0),
                    _draw_korallenwaechter(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_korallenwaechter(-1, 3), _draw_korallenwaechter(0, 3)],
                    "attack": [_draw_korallenwaechter(1, 0), _draw_korallenwaechter(0, 0)],
                    "hurt": [_draw_korallenwaechter(1), _draw_korallenwaechter(0)],
                }
                glow = [{"offset": [10, 3], "color": list(FLAME_GOLD.highlight[:3]), "radius": 10}]
            elif species == "ameisenkrieger":
                idle = [_draw_ameisenkrieger(y, 0, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_ameisenkrieger(0, 0, 0),
                    _draw_ameisenkrieger(-1, 1, 3),
                    _draw_ameisenkrieger(0, 0, 0),
                    _draw_ameisenkrieger(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_ameisenkrieger(-1, 1), _draw_ameisenkrieger(0, 2)],
                    "attack": [_draw_ameisenkrieger(1, 3), _draw_ameisenkrieger(0, 0)],
                    "hurt": [_draw_ameisenkrieger(1), _draw_ameisenkrieger(0)],
                }
                glow = []
            elif species == "blattlaus":
                idle = [_draw_blattlaus(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_blattlaus(0, 0),
                    _draw_blattlaus(-1, 2),
                    _draw_blattlaus(0, 0),
                    _draw_blattlaus(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_blattlaus(-1), _draw_blattlaus(0)],
                    "attack": [_draw_blattlaus(1), _draw_blattlaus(0)],
                    "hurt": [_draw_blattlaus(1), _draw_blattlaus(0)],
                }
                glow = []
            elif species == "arbeiterameise":
                idle = [_draw_arbeiterameise(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_arbeiterameise(0, 0),
                    _draw_arbeiterameise(-1, 3),
                    _draw_arbeiterameise(0, 0),
                    _draw_arbeiterameise(1, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_arbeiterameise(-1), _draw_arbeiterameise(0)],
                    "attack": [_draw_arbeiterameise(1), _draw_arbeiterameise(0)],
                    "hurt": [_draw_arbeiterameise(1), _draw_arbeiterameise(0)],
                }
                glow = []
            elif species == "harzspucker":
                idle = [_draw_harzspucker(y, False, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_harzspucker(0, False, 0),
                    _draw_harzspucker(-1, False, 3),
                    _draw_harzspucker(0, False, 0),
                    _draw_harzspucker(1, False, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_harzspucker(-1, True), _draw_harzspucker(0, True)],
                    "attack": [_draw_harzspucker(1, True, 2), _draw_harzspucker(0, False, 0)],
                    "hurt": [_draw_harzspucker(1), _draw_harzspucker(0)],
                    "shoot": [_draw_harzspucker(0, True), _draw_harzspucker(1, True, 2)],
                }
                glow = [{"offset": [7, 8], "color": list(AMBER_GOLD.highlight[:3]), "radius": 12}]
            elif species == "huepfling":
                idle = [_draw_huepfling(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_huepfling(0, 0),
                    _draw_huepfling(-1, -1),
                    _draw_huepfling(0, 0),
                    _draw_huepfling(1, 1),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_huepfling(-1, -1), _draw_huepfling(0, 0)],
                    "attack": [_draw_huepfling(1, 1), _draw_huepfling(0, 0)],
                    "hurt": [_draw_huepfling(1), _draw_huepfling(0)],
                    "squash": [_draw_huepfling(1, 1), _draw_huepfling(-1, -1)],
                }
                glow = []
            elif species == "glibberteiler":
                idle = [_draw_glibberteiler(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_glibberteiler(0, 0),
                    _draw_glibberteiler(-1, 2),
                    _draw_glibberteiler(0, 0),
                    _draw_glibberteiler(1, -1),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_glibberteiler(-1, 1), _draw_glibberteiler(0, 2)],
                    "attack": [_draw_glibberteiler(1, 3), _draw_glibberteiler(0, 0)],
                    "hurt": [_draw_glibberteiler(1), _draw_glibberteiler(0)],
                    "split": [_draw_glibberteiler(0, 2), _draw_glibberteiler(1, 3)],
                }
                glow = []
            elif species == "zuckerwatte_wolke":
                idle = [_draw_zuckerwatte_wolke(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_zuckerwatte_wolke(0, 0),
                    _draw_zuckerwatte_wolke(-1, 3),
                    _draw_zuckerwatte_wolke(0, 0),
                    _draw_zuckerwatte_wolke(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_zuckerwatte_wolke(-1, 1), _draw_zuckerwatte_wolke(0, 2)],
                    "attack": [_draw_zuckerwatte_wolke(1, 2), _draw_zuckerwatte_wolke(0, 0)],
                    "hurt": [_draw_zuckerwatte_wolke(1), _draw_zuckerwatte_wolke(0)],
                }
                glow = []
            elif species == "konfetti_kanone":
                idle = [_draw_konfetti_kanone(y, 0, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_konfetti_kanone(0, 0, 0),
                    _draw_konfetti_kanone(-1, 2, 3),
                    _draw_konfetti_kanone(0, 0, 0),
                    _draw_konfetti_kanone(1, -1, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_konfetti_kanone(-1, 1), _draw_konfetti_kanone(0, 2)],
                    "attack": [_draw_konfetti_kanone(1, 3), _draw_konfetti_kanone(0, 0)],
                    "hurt": [_draw_konfetti_kanone(1), _draw_konfetti_kanone(0)],
                }
                glow = []
            else:
                continue

            first = idle[0]
            anchor = (first.width // 2, first.height - 2)

            p, j = save_sheet(
                "kreaturen",
                species,
                anims,
                anchor=anchor,
                fps={"idle": 4.0, "walk": 6.0, "windup": 6.0, "attack": 8.0, "hurt": 8.0},
                glow=glow,
                out_dir=out_dir,
            )
            paths.extend([p, j])

    return paths
