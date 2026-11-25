"""Contract V8: Mid-boss and end-boss sprite builders (Cards B15..B19)."""

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
# Color ramps (Bible 05)
# ---------------------------------------------------------------------------

DARK_INK = (24, 20, 32, 255)
WHITE_PX = (248, 248, 255, 255)

# Fleischwelt
BLOOD_RED = make_ramp((188, 34, 48))
FLESH_PINK = make_ramp((214, 102, 114))
FLESH_DEEP = make_ramp((126, 36, 48))
VEIN_BLUE = make_ramp((92, 74, 146))
ACID_GREEN = make_ramp((124, 238, 62))
MAGGOT_CREAM = make_ramp((226, 194, 166))

# Aktenhalde & Authority
PAPER_CREAM = make_ramp((234, 226, 204))
MANILA_TAN = make_ramp((206, 172, 108))
STEEL_CLIP = make_ramp((174, 184, 198))
SUIT_DARK = make_ramp((58, 64, 78))
WOOD_MAHOGANY = make_ramp((124, 58, 42))
WOOD_STAMP = make_ramp((166, 108, 58))
BRASS_GOLD = make_ramp((222, 176, 56))
STAMP_RED = make_ramp((208, 42, 54))
SIREN_BLUE = make_ramp((72, 152, 236))

# Glibbria (bright candy & jelly tones)
JELLY_PINK = make_ramp((236, 98, 154))
JELLY_CYAN = make_ramp((88, 224, 236))
JELLY_LIME = make_ramp((108, 224, 78))
SYRUP_BERRY = make_ramp((214, 52, 128))
CLOWN_RED = make_ramp((222, 48, 62))
CROWN_GOLD = make_ramp((242, 198, 64))
SHOE_BROWN = make_ramp((144, 82, 48))

# Kruemelreich
ANT_CRIMSON = make_ramp((176, 48, 44))
ANT_DARK = make_ramp((86, 32, 36))
MANDIBLE_IVORY = make_ramp((238, 226, 192))
AMBER_GOLD = make_ramp((242, 168, 42))
CRUMB_GOLD = make_ramp((224, 178, 84))
EGG_CREAM = make_ramp((244, 234, 198))
WING_CYAN = make_ramp((148, 228, 242))

# Sporenklub
CAP_RED = make_ramp((204, 46, 54))
MOTH_MAGENTA = make_ramp((212, 64, 168))
HOOD_PURPLE = make_ramp((124, 62, 166))
MUSH_STALK = make_ramp((222, 206, 178))
NEON_CYAN = make_ramp((72, 238, 232))
NEON_LIME = make_ramp((126, 236, 78))
SPORE_PINK = make_ramp((236, 102, 194))
MYCELIUM_TAN = make_ramp((178, 134, 82))
VEST_DARK = make_ramp((44, 42, 58))

# Versunkene Abtei
BRONZE_BELL = make_ramp((186, 146, 72))
BRONZE_VERDIGRIS = make_ramp((82, 152, 144))
ROBE_BROWN = make_ramp((128, 82, 52))
ROPE_TAN = make_ramp((198, 168, 112))
FISH_TEAL = make_ramp((76, 172, 186))
PIPE_SILVER = make_ramp((192, 202, 218))
STONE_MOSS = make_ramp((102, 128, 122))
KRAKEN_INDIGO = make_ramp((78, 92, 156))
FLAME_GOLD = make_ramp((248, 198, 66))
HYMNAL_RED = make_ramp((178, 44, 58))


# ---------------------------------------------------------------------------
# Mid-Bosses (Cards B15, B16)
# ---------------------------------------------------------------------------


def _draw_pfuetzenwurm(
    offset_y: int = 0, coil_shift: int = 0, mouth_open: bool = False
) -> PixelCanvas:
    c = PixelCanvas(34, 28)
    y0 = 2 + offset_y
    # Bubbling crimson-and-acid flesh puddle base
    draw_shaded_ellipse(c, 16, y0 + 20, 13, 3, FLESH_DEEP)
    draw_shaded_ellipse(c, 16, y0 + 19, 10, 2, BLOOD_RED)
    c.set_px(7, y0 + 19, ACID_GREEN.highlight)
    c.set_px(24, y0 + 20, ACID_GREEN.light)
    # Muscular S-curved worm neck coiling upward
    lunge = 2 if coil_shift > 0 else (-2 if coil_shift < 0 else 0)
    tail_lift = -3 if coil_shift < 0 else 0
    draw_segment_line(c, 6, y0 + 18 + tail_lift, 9, y0 + 14, FLESH_PINK.shadow, 3)
    draw_shaded_ellipse(c, 10 + (lunge // 2), y0 + 14, 5, 4, FLESH_PINK)
    draw_shaded_ellipse(c, 14, y0 + 10 - max(0, lunge), 4, 3, BLOOD_RED)
    # Serrated worm head lunging right with glowing green acid spray
    hx = min(26, 21 + max(0, lunge))
    hy = max(5, y0 + 7 - (2 if lunge > 0 else 0))
    draw_shaded_ellipse(c, hx, hy, 5, 4, FLESH_PINK)
    c.set_px(hx + 1, hy - 2, ACID_GREEN.highlight)
    # Gap-tooth maw
    if mouth_open or lunge > 0:
        draw_shaded_rect(c, hx + 2, hy - 1, min(31, hx + 6), hy + 2, ACID_GREEN)
        c.set_px(min(31, hx + 5), hy - 1, WHITE_PX)
        c.set_px(min(31, hx + 5), hy + 2, WHITE_PX)
    else:
        c.set_px(hx + 4, hy, WHITE_PX)
        c.set_px(hx + 4, hy + 1, ACID_GREEN.light)
    if coil_shift > 0:
        c.set_px(min(32, hx + 6), hy - 2, ACID_GREEN.highlight)
    apply_dark_outline(c)
    return c


def _draw_aktenwolf(offset_y: int = 0, leg_stride: int = 0, howling: bool = False) -> PixelCanvas:
    c = PixelCanvas(34, 28)
    y0 = 2 + offset_y
    # Torn-page tail swishing left
    tail_y = y0 + 10 - (3 if leg_stride > 0 else (-2 if leg_stride < 0 else 0))
    draw_segment_line(c, 7, y0 + 12, 2, max(4, tail_y), PAPER_CREAM.light, 2)
    c.set_px(2, max(4, tail_y), STEEL_CLIP.highlight)
    # Folded manila & cream dossier quadruped body + bristling jagged page mane
    draw_shaded_rect(c, 7, y0 + 10, 22, y0 + 16, MANILA_TAN)
    draw_shaded_rect(c, 14, y0 + 8, 22, y0 + 13, PAPER_CREAM)
    for mx in (15, 18, 21):
        c.set_px(mx, y0 + 7, PAPER_CREAM.highlight)
    # Pointed paper wolf head, tab ears, red hunter eye, paperclip teeth
    head_y = y0 + 6 - (2 if howling else 0)
    draw_shaded_ellipse(c, 25, head_y + 3, 4, 4, MANILA_TAN)
    draw_segment_line(c, 23, head_y, 22, max(1, head_y - 3), PAPER_CREAM.highlight, 1)
    draw_segment_line(c, 26, head_y, 26, max(1, head_y - 3), PAPER_CREAM.highlight, 1)
    c.set_px(26, head_y + 2, STAMP_RED.highlight)
    draw_shaded_rect(c, 27, head_y + 3, 31, head_y + 5, PAPER_CREAM)
    c.set_px(29, head_y + 5, STEEL_CLIP.highlight)
    c.set_px(31, head_y + 5, STEEL_CLIP.highlight)
    # 4 articulated folder legs scissoring wide
    s = leg_stride
    draw_segment_line(c, 9, y0 + 16, max(2, 6 - s), y0 + 23, MANILA_TAN.shadow, 2)
    draw_segment_line(c, 12, y0 + 16, min(17, 13 + s), y0 + 23, PAPER_CREAM.mid, 2)
    draw_segment_line(c, 19, y0 + 16, max(14, 17 - s), y0 + 23, MANILA_TAN.shadow, 2)
    draw_segment_line(c, 22, y0 + 16, min(30, 25 + s), y0 + 23, PAPER_CREAM.mid, 2)
    apply_dark_outline(c)
    return c


def _draw_manege_clown(offset_y: int = 0, jiggle: int = 0, honk: bool = False) -> PixelCanvas:
    c = PixelCanvas(32, 32)
    y0 = 2 + offset_y
    # Striped cone party hat + white pom-pom
    draw_segment_line(c, 16, y0 + 1, 13, y0 + 6, CLOWN_RED.mid, 2)
    draw_segment_line(c, 16, y0 + 1, 19, y0 + 6, CROWN_GOLD.mid, 2)
    draw_shaded_rect(c, 13, y0 + 4, 19, y0 + 6, CLOWN_RED)
    c.set_px(16, y0, WHITE_PX)
    # Clown face with red bulb nose (flashes gold on honk)
    draw_shaded_ellipse(c, 16, y0 + 9, 4, 3, PAPER_CREAM)
    c.set_px(14, y0 + 8, SIREN_BLUE.mid)
    c.set_px(18, y0 + 8, SIREN_BLUE.mid)
    c.set_px(16, y0 + 10, CROWN_GOLD.highlight if honk else CLOWN_RED.highlight)
    # Giant ruffled cyan & yellow clown collar
    draw_shaded_ellipse(c, 16, y0 + 13, 8, 2, JELLY_CYAN)
    c.set_px(10, y0 + 13, CROWN_GOLD.highlight)
    c.set_px(22, y0 + 13, CROWN_GOLD.highlight)
    # Raspberry-pink jelly clown belly with colorful polka buttons
    draw_shaded_ellipse(c, 16, y0 + 19, 7, 5, JELLY_PINK)
    c.set_px(16, y0 + 17, JELLY_LIME.highlight)
    c.set_px(16, y0 + 20, JELLY_CYAN.highlight)
    # Juggling arms swinging opposite heights in walk
    la_y = max(3, y0 + 15 - jiggle * 2)
    ra_y = min(26, y0 + 15 + jiggle * 2)
    draw_segment_line(c, 9, y0 + 16, 4, la_y, JELLY_PINK.light, 2)
    draw_segment_line(c, 23, y0 + 16, 27, ra_y, JELLY_PINK.light, 2)
    draw_shaded_ellipse(c, 4, la_y, 2, 2, JELLY_LIME if honk else PAPER_CREAM)
    draw_shaded_ellipse(c, 27, ra_y, 2, 2, CROWN_GOLD if honk else PAPER_CREAM)
    # Big floppy red clown shoes striding wide (stay distinct when close)
    lx = 6 if jiggle > 0 else (10 if jiggle < 0 else 9)
    rx = 22 if jiggle > 0 else (18 if jiggle < 0 else 19)
    draw_shaded_rect(c, lx, y0 + 24, lx + 4, y0 + 26, CLOWN_RED)
    draw_shaded_rect(c, rx, y0 + 24, rx + 4, y0 + 26, CLOWN_RED)
    apply_dark_outline(c)
    return c


def _draw_harzgeneral(
    offset_y: int = 0, leg_stride: int = 0, claw_open: bool = False
) -> PixelCanvas:
    c = PixelCanvas(34, 30)
    y0 = 2 + offset_y
    # Segmented crimson abdomen left + golden epaulet thorax
    draw_shaded_ellipse(c, 7, y0 + 14, 5, 4, ANT_CRIMSON)
    draw_shaded_ellipse(c, 14, y0 + 12, 4, 4, ANT_DARK)
    draw_shaded_rect(c, 11, y0 + 8, 17, y0 + 10, AMBER_GOLD)
    # Armored commander head & Prussian pickelhaube with gold spike
    draw_shaded_ellipse(c, 20, y0 + 9, 4, 3, ANT_CRIMSON)
    draw_shaded_rect(c, 17, y0 + 4, 24, y0 + 7, ANT_DARK)
    draw_segment_line(c, 20, y0 + 4, 20, y0 + 1, AMBER_GOLD.highlight, 1)
    c.set_px(22, y0 + 9, MANDIBLE_IVORY.highlight)
    # Huge translucent amber resin cannon claw raised/opening on right
    reach = 2 if (claw_open or leg_stride > 0) else 0
    draw_shaded_ellipse(c, 26 + (reach // 2), y0 + 12 - reach, 5, 4, AMBER_GOLD)
    c.set_px(25, y0 + 10 - reach, WHITE_PX)
    if claw_open or leg_stride > 0:
        draw_segment_line(c, 27, y0 + 9 - reach, 31, y0 + 6 - reach, MANDIBLE_IVORY.highlight, 2)
        draw_segment_line(c, 27, y0 + 14 - reach, 31, y0 + 15, MANDIBLE_IVORY.light, 2)
    # Chitin commander legs striding wide
    s = leg_stride
    draw_segment_line(c, 8, y0 + 17, max(2, 4 - s), y0 + 24, ANT_DARK.shadow, 2)
    draw_segment_line(c, 14, y0 + 16, 14, y0 + 24, ANT_CRIMSON.mid, 2)
    draw_segment_line(c, 20, y0 + 15, min(30, 23 + s), y0 + 24, ANT_DARK.mid, 2)
    apply_dark_outline(c)
    return c


def _draw_sporenherz(offset_y: int = 0, pulse: int = 0, emit_spores: bool = False) -> PixelCanvas:
    c = PixelCanvas(32, 32)
    y0 = 2 + offset_y
    # 5 ceiling mycelium tendrils swaying slightly at top (no whole-body squash!)
    for idx, rx in enumerate((8, 12, 16, 20, 24)):
        top_sway = max(2, min(29, rx + (pulse // 2 if idx % 2 == 0 else -pulse // 2)))
        draw_segment_line(c, top_sway, y0, rx, y0 + 8, MYCELIUM_TAN.mid, 2)
    # Central fungal heart organ (steady size, zero squash cheat)
    draw_shaded_ellipse(c, 13, y0 + 13, 6, 6, HOOD_PURPLE)
    draw_shaded_ellipse(c, 19, y0 + 13, 6, 6, HOOD_PURPLE)
    draw_shaded_ellipse(c, 16, y0 + 18, 6, 5, SPORE_PINK)
    c.set_px(13, y0 + 11, NEON_CYAN.highlight)
    c.set_px(19, y0 + 11, NEON_CYAN.highlight)
    # Side waving fungal feeler tendrils shifting silhouette across walk
    flare = max(0, pulse)
    droop = max(0, -pulse)
    draw_segment_line(c, 8, y0 + 14, max(2, 4 - flare), y0 + 12 + droop * 2, NEON_LIME.mid, 2)
    draw_segment_line(c, 24, y0 + 14, min(29, 27 + flare), y0 + 12 + droop * 2, NEON_LIME.mid, 2)
    # Hanging weeping mushroom gill ribbons sweeping left/right underneath
    for i, gx in enumerate((10, 14, 18, 22)):
        dir_x = pulse if i < 2 else -pulse
        end_x = max(3, min(28, gx + dir_x * 2))
        end_y = min(29, y0 + 25 + (droop if i in (1, 2) else 0))
        draw_segment_line(c, gx, y0 + 20, end_x, end_y, NEON_CYAN.light, 1)
        c.set_px(end_x, end_y, NEON_LIME.highlight if emit_spores else SPORE_PINK.highlight)
    if emit_spores:
        c.set_px(16, y0 + 27, WHITE_PX)
        c.set_px(8, y0 + 24, NEON_LIME.highlight)
        c.set_px(24, y0 + 24, NEON_LIME.highlight)
    apply_dark_outline(c)
    return c


def _draw_glockenwaechter(
    offset_y: int = 0, swing: int = 0, clapper_strike: bool = False
) -> PixelCanvas:
    c = PixelCanvas(32, 32)
    y0 = 2 + offset_y
    # Carved stone suspension yoke at top
    draw_shaded_rect(c, 10, y0 + 1, 22, y0 + 5, STONE_MOSS)
    # Swinging bronze-and-verdigris bell dome + glowing cyan rune
    bx = 16 + (swing // 2)
    draw_shaded_rect(c, bx - 6, y0 + 5, bx + 6, y0 + 16, BRONZE_BELL)
    draw_shaded_ellipse(c, bx, y0 + 17, 9, 3, BRONZE_VERDIGRIS)
    c.set_px(bx, y0 + 10, NEON_CYAN.highlight)
    c.set_px(bx, y0 + 12, NEON_CYAN.light)
    c.set_px(bx - 1, y0 + 11, NEON_CYAN.light)
    c.set_px(bx + 1, y0 + 11, NEON_CYAN.light)
    # Flanking pull-ropes whipping outward in walk
    l_rope = max(2, 6 - abs(swing) - (2 if swing < 0 else 0))
    r_rope = min(29, 25 + abs(swing) + (2 if swing > 0 else 0))
    draw_segment_line(c, 10, y0 + 5, l_rope, y0 + 23, ROPE_TAN.light, 1)
    draw_segment_line(c, 22, y0 + 5, r_rope, y0 + 23, ROPE_TAN.light, 1)
    # Heavy swinging golden clapper + stone greaves
    cx = max(6, min(25, bx + swing + (2 if clapper_strike else 0)))
    draw_segment_line(c, bx, y0 + 18, cx, y0 + 25, FLAME_GOLD.mid, 2)
    draw_shaded_ellipse(c, cx, y0 + 25, 2, 2, FLAME_GOLD)
    if clapper_strike:
        c.set_px(cx, y0 + 27, WHITE_PX)
    apply_dark_outline(c)
    return c


def _draw_warden(offset_y: int = 0, arm_swing: int = 0, siren_on: bool = False) -> PixelCanvas:
    c = PixelCanvas(32, 32)
    y0 = 2 + offset_y
    # Flashing red/blue siren beacon + armored visor head
    c.set_px(16, y0, STAMP_RED.highlight if siren_on else SIREN_BLUE.highlight)
    draw_shaded_rect(c, 13, y0 + 1, 18, y0 + 3, STAMP_RED if siren_on else SIREN_BLUE)
    draw_shaded_rect(c, 11, y0 + 3, 20, y0 + 9, SUIT_DARK)
    draw_shaded_rect(c, 12, y0 + 5, 19, y0 + 6, STAMP_RED)
    # Two-drawer dark-steel filing cabinet torso with brass handles
    draw_shaded_rect(c, 9, y0 + 9, 22, y0 + 22, SUIT_DARK)
    draw_shaded_rect(c, 11, y0 + 11, 20, y0 + 15, STEEL_CLIP)
    draw_shaded_rect(c, 11, y0 + 17, 20, y0 + 21, STEEL_CLIP)
    c.set_px(15, y0 + 13, BRASS_GOLD.highlight)
    c.set_px(16, y0 + 13, BRASS_GOLD.highlight)
    c.set_px(15, y0 + 19, BRASS_GOLD.highlight)
    c.set_px(16, y0 + 19, BRASS_GOLD.highlight)
    # Pneumatic stamping arms swinging dramatically high vs low in walk
    l_shift = max(-4, min(4, arm_swing))
    r_shift = -l_shift
    draw_shaded_rect(c, 3, max(4, y0 + 10 - l_shift), 7, min(25, y0 + 19 - l_shift), STEEL_CLIP)
    draw_shaded_rect(c, 24, max(4, y0 + 10 - r_shift), 28, min(25, y0 + 19 - r_shift), STEEL_CLIP)
    c.set_px(5, min(25, y0 + 19 - l_shift), STAMP_RED.light)
    c.set_px(26, min(25, y0 + 19 - r_shift), STAMP_RED.light)
    # Heavy steel tank treads stepping out
    draw_shaded_rect(c, 7, y0 + 23, 13, y0 + 27, VEST_DARK)
    draw_shaded_rect(c, 18, y0 + 23, 24, y0 + 27, VEST_DARK)
    apply_dark_outline(c)
    return c


def build_mid_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<mid_boss>.{png,json} for all 9 mid-bosses + warden (Cards B15, B16)."""
    boss_specs = [
        ("pfuetzenwurm", list(ACID_GREEN.highlight[:3]), _draw_pfuetzenwurm),
        ("aktenwolf", list(STAMP_RED.highlight[:3]), _draw_aktenwolf),
        ("manege_clown", list(JELLY_CYAN.highlight[:3]), _draw_manege_clown),
        ("harzgeneral", list(AMBER_GOLD.highlight[:3]), _draw_harzgeneral),
        ("sporenherz", list(NEON_LIME.highlight[:3]), _draw_sporenherz),
        ("glockenwaechter", list(NEON_CYAN.highlight[:3]), _draw_glockenwaechter),
        ("warden", list(STAMP_RED.highlight[:3]), _draw_warden),
    ]

    paths: list[Path] = []
    for boss_key, glow_rgb, draw_fn in boss_specs:
        idle = [draw_fn(y, 0, False) for y in (0, 1, 0, -1)]
        walk = [
            draw_fn(0, 0, False),
            draw_fn(-1, 3, False),
            draw_fn(0, 0, False),
            draw_fn(1, -3, False),
        ]
        windup = [draw_fn(-1, 1, True), draw_fn(0, 2, True)]
        attack = [draw_fn(1, 3, True), draw_fn(0, 0, False)]
        hurt = [draw_fn(1, 0, False), draw_fn(0, 0, False)]

        anims = {
            "idle": idle,
            "walk": walk,
            "windup": windup,
            "attack": attack,
            "hurt": hurt,
        }
        first = idle[0]
        glow = [{"offset": [first.width // 2, first.height // 2], "color": glow_rgb, "radius": 16}]
        p, j = save_sheet(
            "bosse",
            boss_key,
            anims,
            anchor=(first.width // 2, first.height - 4),
            fps={"idle": 4.0, "walk": 6.0, "windup": 6.0, "attack": 8.0, "hurt": 8.0},
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p, j])

    return paths


# ---------------------------------------------------------------------------
# End-Bosses & Large Creatures (Cards B17, B18, B19)
# ---------------------------------------------------------------------------


def _draw_weltenherz(offset_y: int = 0, beat_pulse: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # 5 branching upper aorta arteries flexing asymmetrically (zero squash cheat!)
    for idx, (rx, tx, ty) in enumerate((
        (16, 10, 2),
        (20, 17, 1),
        (24, 24, 1),
        (28, 31, 1),
        (32, 38, 2),
    )):
        sway = beat_pulse if idx % 2 == 0 else -beat_pulse
        draw_segment_line(c, rx, y0 + 13, max(4, min(43, tx + sway)), y0 + ty, FLESH_DEEP.mid, 3)
        draw_segment_line(c, rx, y0 + 13, max(4, min(43, tx + sway)), y0 + ty, BLOOD_RED.light, 1)
    # Anatomical twin-chamber heart tapering to pointed apex
    draw_shaded_ellipse(c, 18, y0 + 19, 10, 10, BLOOD_RED)
    draw_shaded_ellipse(c, 30, y0 + 19, 10, 10, BLOOD_RED)
    draw_shaded_ellipse(c, 24, y0 + 28, 9, 8, FLESH_DEEP)
    draw_shaded_ellipse(c, 24, y0 + 34, 4, 4, BLOOD_RED)
    # Blue-violet surface veins & muscular valve flaps opening on side
    draw_segment_line(c, 15, y0 + 16, 20, y0 + 27, VEIN_BLUE.light, 1)
    draw_segment_line(c, 33, y0 + 16, 27, y0 + 28, VEIN_BLUE.light, 1)
    if beat_pulse != 0:
        draw_segment_line(c, 8, y0 + 20, max(3, 5 - abs(beat_pulse)), y0 + 23, FLESH_PINK.mid, 2)
        draw_segment_line(c, 40, y0 + 20, min(44, 42 + abs(beat_pulse)), y0 + 23, FLESH_PINK.mid, 2)
    # Glowing core pulse & dripping blood droplet at apex
    if action:
        draw_shaded_ellipse(c, 24, y0 + 23, 4, 4, ACID_GREEN)
        c.set_px(24, y0 + 23, WHITE_PX)
    else:
        c.set_px(24, y0 + 22, FLESH_PINK.highlight)
    drop_y = min(45, y0 + 40 + (abs(beat_pulse) % 3))
    c.set_px(24, drop_y, BLOOD_RED.highlight)
    c.set_px(24, drop_y - 1, BLOOD_RED.mid)
    apply_dark_outline(c)
    return c


def _draw_oberstempler(offset_y: int = 0, arm_shift: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Ornate antique brass wall-clock head with cream dial & dark clock hands
    draw_shaded_ellipse(c, 24, y0 + 8, 7, 7, BRASS_GOLD)
    draw_shaded_ellipse(c, 24, y0 + 8, 5, 5, PAPER_CREAM)
    draw_segment_line(c, 24, y0 + 8, 24, y0 + 5, DARK_INK, 1)
    draw_segment_line(c, 24, y0 + 8, 27, y0 + 9, STAMP_RED.mid, 1)
    # Massive tiered mahogany desk torso with drawers & gold handles
    draw_shaded_rect(c, 11, y0 + 16, 37, y0 + 32, WOOD_MAHOGANY)
    draw_shaded_rect(c, 10, y0 + 15, 38, y0 + 17, WOOD_STAMP)
    draw_shaded_rect(c, 14, y0 + 19, 34, y0 + 22, SUIT_DARK)
    draw_shaded_rect(c, 14, y0 + 25, 34, y0 + 28, SUIT_DARK)
    c.set_px(24, y0 + 20, BRASS_GOLD.highlight)
    c.set_px(24, y0 + 26, BRASS_GOLD.highlight)
    # Two gigantic wooden-and-red-ink stamp hammer arms alternating high/low
    l_dy = max(-4, min(4, arm_shift * 2))
    r_dy = -l_dy
    draw_shaded_rect(c, 4, max(6, y0 + 14 - l_dy), 8, min(33, y0 + 29 - l_dy), WOOD_STAMP)
    draw_shaded_rect(c, 3, min(35, y0 + 29 - l_dy), 9, min(38, y0 + 32 - l_dy), STAMP_RED)
    draw_shaded_rect(c, 40, max(6, y0 + 14 - r_dy), 44, min(33, y0 + 29 - r_dy), WOOD_STAMP)
    draw_shaded_rect(c, 39, min(35, y0 + 29 - r_dy), 45, min(38, y0 + 32 - r_dy), STAMP_RED)
    # Twin pedestal desk legs with wide gap
    draw_shaded_rect(c, 13, y0 + 33, 18, y0 + 42, WOOD_MAHOGANY)
    draw_shaded_rect(c, 30, y0 + 33, 35, y0 + 42, WOOD_MAHOGANY)
    if action:
        c.set_px(6, min(39, y0 + 33 - l_dy), WHITE_PX)
        c.set_px(42, min(39, y0 + 33 - r_dy), WHITE_PX)
    apply_dark_outline(c)
    return c


def _draw_mutter_glibber(offset_y: int = 0, ripple: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Jeweled golden crown tilting atop royal jelly mass
    c.set_px(20, y0 + 3, CROWN_GOLD.highlight)
    c.set_px(24, y0 + 2, JELLY_CYAN.highlight)
    c.set_px(28, y0 + 3, CROWN_GOLD.highlight)
    draw_shaded_rect(c, 19, y0 + 4, 29, y0 + 9, CROWN_GOLD)
    draw_shaded_rect(c, 21, y0 + 6, 27, y0 + 8, SYRUP_BERRY)
    # Colossal wide translucent strawberry-pink jelly dome (no brown, no squash cheat!)
    draw_shaded_ellipse(c, 24, y0 + 27, 19, 14, JELLY_PINK)
    draw_shaded_ellipse(c, 24, y0 + 23, 14, 9, JELLY_CYAN)
    c.set_px(14, y0 + 17, WHITE_PX)
    c.set_px(15, y0 + 16, WHITE_PX)
    # Surging side jelly wave crests / tendrils sweeping outward
    wave = abs(ripple)
    draw_shaded_ellipse(c, max(3, 5 - wave), y0 + 35 - (wave // 2), 3, 4, JELLY_PINK)
    draw_shaded_ellipse(c, min(44, 43 + wave), y0 + 35 - (wave // 2), 3, 4, JELLY_PINK)
    # Two miniature Huepflinge floating visibly inside her translucent belly
    draw_shaded_ellipse(c, 17, y0 + 28, 3, 3, JELLY_LIME)
    c.set_px(16, y0 + 27, DARK_INK)
    c.set_px(18, y0 + 27, DARK_INK)
    draw_shaded_ellipse(c, 31, y0 + 27, 3, 3, SYRUP_BERRY)
    c.set_px(30, y0 + 26, DARK_INK)
    c.set_px(32, y0 + 26, DARK_INK)
    if action:
        draw_shaded_ellipse(c, 24, y0 + 27, 4, 4, JELLY_LIME)
        c.set_px(24, y0 + 27, WHITE_PX)
    apply_dark_outline(c)
    return c


def _draw_dj_myzel(offset_y: int = 0, beat_bounce: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Towering spotted red mushroom cap + glowing neon-cyan headphones
    draw_shaded_ellipse(c, 24, y0 + 10, 15, 7, CAP_RED)
    for sx, sy in ((15, y0 + 8), (24, y0 + 6), (32, y0 + 9)):
        c.set_px(sx, sy, MUSH_STALK.highlight)
        c.set_px(sx + 1, sy, MUSH_STALK.light)
    draw_shaded_rect(c, 9, y0 + 4, 39, y0 + 6, NEON_CYAN)
    draw_shaded_rect(c, 7, y0 + 8, 10, y0 + 14, NEON_CYAN)
    draw_shaded_rect(c, 38, y0 + 8, 41, y0 + 14, NEON_CYAN)
    # Stalk torso & shades behind DJ booth
    draw_shaded_rect(c, 20, y0 + 17, 28, y0 + 25, MUSH_STALK)
    draw_shaded_rect(c, 20, y0 + 17, 28, y0 + 18, VEST_DARK)
    # DJ arms scratching records left/right in walk
    arm_y = max(16, y0 + 22 - abs(beat_bounce))
    draw_segment_line(c, 20, y0 + 20, 13 + beat_bounce, arm_y, MUSH_STALK.light, 2)
    draw_segment_line(c, 28, y0 + 20, 35 - beat_bounce, arm_y, MUSH_STALK.light, 2)
    # Wide dark-steel DJ mixing booth & speaker stacks with glowing turntables
    draw_shaded_rect(c, 6, y0 + 24, 42, y0 + 39, VEST_DARK)
    draw_shaded_rect(c, 3, y0 + 26, 6, y0 + 41, HOOD_PURPLE)
    draw_shaded_rect(c, 42, y0 + 26, 45, y0 + 41, HOOD_PURPLE)
    draw_shaded_ellipse(c, 15, y0 + 31, 6, 3, STEEL_CLIP)
    draw_shaded_ellipse(c, 33, y0 + 31, 6, 3, STEEL_CLIP)
    c.set_px(15, y0 + 31, MOTH_MAGENTA.highlight)
    c.set_px(33, y0 + 31, NEON_CYAN.highlight)
    # Animated neon equalizer bars in booth center
    eq = 2 if (action or beat_bounce != 0) else 0
    for ex, ramp in ((22, NEON_LIME), (24, SPORE_PINK), (26, NEON_CYAN)):
        draw_shaded_rect(c, ex, y0 + 31 - eq, ex + 1, y0 + 37, ramp)
    apply_dark_outline(c)
    return c


def _draw_ameisenkoenigin(offset_y: int = 0, crawl: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Enormous translucent amber-gold egg-bloated abdomen rising high on left
    draw_shaded_ellipse(c, 13, y0 + 22, 10, 9, ANT_CRIMSON)
    draw_shaded_ellipse(c, 13, y0 + 22, 7, 6, AMBER_GOLD)
    for ex, ey in ((10, y0 + 20), (15, y0 + 23), (12, y0 + 25)):
        draw_shaded_ellipse(c, ex, ey, 2, 1, EGG_CREAM)
    # Royal thorax with connected fluttering iridescent cyan wing buds
    draw_shaded_ellipse(c, 26, y0 + 18, 5, 5, ANT_DARK)
    wing_up = 2 if crawl > 0 else 0
    draw_segment_line(c, 26, y0 + 15, 23, max(7, y0 + 11 - wing_up), WING_CYAN.mid, 2)
    draw_shaded_ellipse(c, 22, max(6, y0 + 11 - wing_up), 5, 3, WING_CYAN)
    # Crowned queen ant head & giant ivory mandibles on right
    draw_shaded_ellipse(c, 35, y0 + 15, 6, 5, ANT_CRIMSON)
    draw_shaded_rect(c, 31, y0 + 7, 39, y0 + 11, CROWN_GOLD)
    c.set_px(32, y0 + 6, CROWN_GOLD.highlight)
    c.set_px(35, y0 + 5, WHITE_PX)
    c.set_px(38, y0 + 6, CROWN_GOLD.highlight)
    draw_segment_line(c, 40, y0 + 15, 45, y0 + 13 - (1 if action else 0), MANDIBLE_IVORY.highlight, 2)
    draw_segment_line(c, 40, y0 + 18, 45, y0 + 19 + (1 if action else 0), MANDIBLE_IVORY.light, 2)
    # 6 articulated chitin royal legs striding in walk
    for idx, (lx, rx) in enumerate(((18, 13), (26, 25), (34, 38))):
        step = crawl if idx % 2 == 0 else -crawl
        draw_segment_line(c, lx, y0 + 26, max(4, min(43, rx + step)), y0 + 38, ANT_DARK.mid, 2)
    apply_dark_outline(c)
    return c


def _draw_abt_kieme(offset_y: int = 0, robe_flutter: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Towering cream-and-gold papal miter with red trim & cross
    draw_shaded_rect(c, 20, y0 + 1, 28, y0 + 10, PAPER_CREAM)
    draw_shaded_rect(c, 20, y0 + 8, 28, y0 + 10, HYMNAL_RED)
    draw_segment_line(c, 24, y0 + 2, 24, y0 + 7, CROWN_GOLD.highlight, 1)
    draw_segment_line(c, 22, y0 + 4, 26, y0 + 4, CROWN_GOLD.highlight, 1)
    # Shining vertical organ pipes fanning behind his shoulders
    for idx, opx in enumerate((14, 17, 31, 34)):
        h = 9 + (idx % 2) * 3
        draw_shaded_rect(c, opx, y0 + 19 - h, opx + 2, y0 + 21, PIPE_SILVER)
        c.set_px(opx + 1, y0 + 19 - h, WHITE_PX)
    # Ancient scaly teal fish head with flowing white catfish barbels
    draw_shaded_ellipse(c, 24, y0 + 15, 6, 4, FISH_TEAL)
    c.set_px(21, y0 + 14, FLAME_GOLD.highlight)
    c.set_px(27, y0 + 14, FLAME_GOLD.highlight)
    draw_segment_line(c, 19, y0 + 17, 16, y0 + 21, WHITE_PX, 1)
    draw_segment_line(c, 29, y0 + 17, 32, y0 + 21, WHITE_PX, 1)
    # Ceremonial brown-and-gold vestment torso + bell-staff arm waving
    draw_shaded_rect(c, 17, y0 + 20, 31, y0 + 32, ROBE_BROWN)
    draw_shaded_rect(c, 22, y0 + 20, 26, y0 + 32, BRASS_GOLD)
    staff_x = min(43, 37 + abs(robe_flutter))
    draw_segment_line(c, 31, y0 + 24, staff_x, y0 + 16, BRASS_GOLD.light, 2)
    draw_shaded_ellipse(c, staff_x, y0 + 15, 2, 2, NEON_CYAN if action else FLAME_GOLD)
    # Floating carved mossy-stone chalice pulpit
    draw_shaded_rect(c, 14, y0 + 33, 34, y0 + 37, STONE_MOSS)
    draw_shaded_ellipse(c, 24, y0 + 39, 13, 4, BRONZE_VERDIGRIS)
    c.set_px(24, y0 + 42, NEON_CYAN.highlight)
    apply_dark_outline(c)
    return c


def _draw_trampolinwal(offset_y: int = 0, fin_flap: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Giant translucent pink-and-cyan jelly whale silhouette (never brown!)
    draw_shaded_ellipse(c, 25, y0 + 24, 17, 10, JELLY_PINK)
    # Taut cyan-and-gold trampoline mat along back
    draw_shaded_rect(c, 14, y0 + 13, 36, y0 + 16, JELLY_CYAN)
    draw_shaded_rect(c, 16, y0 + 14, 34, y0 + 15, CROWN_GOLD)
    # Syrup blowhole fountain jetting from top blowhole
    spray = abs(fin_flap)
    draw_segment_line(c, 32, y0 + 12, 30 - spray, max(2, y0 + 5 - spray), SYRUP_BERRY.light, 1)
    draw_segment_line(c, 32, y0 + 12, 34 + spray, max(2, y0 + 5 - spray), FLAME_GOLD.light, 1)
    c.set_px(30 - spray, max(2, y0 + 5 - spray), WHITE_PX)
    c.set_px(34 + spray, max(2, y0 + 5 - spray), JELLY_CYAN.highlight)
    # Translucent belly window showing eaten miniature BICYCLE and BROWN SHOE
    draw_shaded_ellipse(c, 26, y0 + 25, 11, 6, JELLY_CYAN)
    # Miniature bicycle (two silver wheels + red frame)
    c.set_px(18, y0 + 26, WHITE_PX)
    c.set_px(19, y0 + 27, DARK_INK)
    c.set_px(23, y0 + 26, WHITE_PX)
    c.set_px(24, y0 + 27, DARK_INK)
    draw_segment_line(c, 19, y0 + 26, 22, y0 + 23, CLOWN_RED.highlight, 1)
    draw_segment_line(c, 22, y0 + 23, 24, y0 + 26, CLOWN_RED.highlight, 1)
    # Miniature eaten brown shoe floating beside bicycle
    draw_shaded_rect(c, 29, y0 + 24, 33, y0 + 27, SHOE_BROWN)
    c.set_px(33, y0 + 27, PAPER_CREAM.light)
    # Friendly whale eye & smile
    c.set_px(38, y0 + 21, DARK_INK)
    c.set_px(39, y0 + 21, WHITE_PX)
    draw_segment_line(c, 36, y0 + 26, 40, y0 + 25, DARK_INK, 1)
    # Animated fluked whale tail left & pectoral flipper below
    draw_shaded_ellipse(c, 6, y0 + 22 - fin_flap, 4, 6, SYRUP_BERRY)
    draw_shaded_ellipse(c, 28, y0 + 35 + fin_flap, 6, 3, JELLY_PINK)
    if action:
        c.set_px(24, y0 + 13, WHITE_PX)
    apply_dark_outline(c)
    return c


def _draw_kirchenkrake(
    offset_y: int = 0, tentacle_wave: int = 0, action: bool = False
) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    y0 = 2 + offset_y
    # Grand bronze-and-verdigris cathedral bell dome helmet + gold cross finial
    draw_segment_line(c, 24, y0 + 1, 24, y0 + 4, CROWN_GOLD.highlight, 1)
    draw_segment_line(c, 22, y0 + 2, 26, y0 + 2, CROWN_GOLD.highlight, 1)
    draw_shaded_rect(c, 16, y0 + 5, 32, y0 + 16, BRONZE_BELL)
    draw_shaded_ellipse(c, 24, y0 + 16, 10, 3, BRONZE_VERDIGRIS)
    # Deep abyssal indigo cephalopod mantle & glowing ancient amber eyes
    draw_shaded_ellipse(c, 24, y0 + 22, 11, 6, KRAKEN_INDIGO)
    c.set_px(19, y0 + 21, FLAME_GOLD.highlight)
    c.set_px(29, y0 + 21, FLAME_GOLD.highlight)
    # 6 sinuous curved tentacles rooted cleanly in mantle holding CANDLES and HYMNALS
    roots = (15, 18, 22, 26, 30, 33)
    tips = (7, 13, 19, 27, 33, 39)
    for idx, (rx, tx) in enumerate(zip(roots, tips, strict=True)):
        shift = tentacle_wave if idx % 2 == 0 else -tentacle_wave
        tip_x = max(4, min(43, tx + shift))
        mid_x = (rx + tip_x) // 2
        draw_segment_line(c, rx, y0 + 25, mid_x, y0 + 33, KRAKEN_INDIGO.mid, 2)
        draw_segment_line(c, mid_x, y0 + 33, tip_x, y0 + 41, KRAKEN_INDIGO.mid, 2)
        if idx % 2 == 0:
            # Beeswax candle with warm golden flame
            draw_shaded_rect(c, tip_x - 1, y0 + 36, tip_x + 1, y0 + 40, PAPER_CREAM)
            c.set_px(tip_x, y0 + 34, FLAME_GOLD.highlight)
            c.set_px(tip_x, y0 + 35, STAMP_RED.light)
        else:
            # Red-and-gold trimmed hymnal book
            draw_shaded_rect(c, tip_x - 1, y0 + 37, tip_x + 2, y0 + 41, HYMNAL_RED)
            c.set_px(tip_x + 1, y0 + 38, CROWN_GOLD.highlight)
    if action:
        c.set_px(24, y0 + 21, NEON_CYAN.highlight)
    apply_dark_outline(c)
    return c


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    end_boss_specs = [
        ("weltenherz", list(BLOOD_RED.highlight[:3]), _draw_weltenherz),
        ("oberstempler", list(STAMP_RED.highlight[:3]), _draw_oberstempler),
        ("mutter_glibber", list(JELLY_CYAN.highlight[:3]), _draw_mutter_glibber),
        ("dj_myzel", list(NEON_CYAN.highlight[:3]), _draw_dj_myzel),
        ("ameisenkoenigin", list(AMBER_GOLD.highlight[:3]), _draw_ameisenkoenigin),
        ("abt_kieme", list(FLAME_GOLD.highlight[:3]), _draw_abt_kieme),
    ]

    paths: list[Path] = []
    for boss_key, glow_rgb, draw_fn in end_boss_specs:
        idle = [draw_fn(y, 0, False) for y in (0, 1, 0, -1)]
        walk = [
            draw_fn(0, 0, False),
            draw_fn(-1, 3, False),
            draw_fn(0, 0, False),
            draw_fn(1, -3, False),
        ]
        windup = [draw_fn(-1, 1, True), draw_fn(0, 2, True)]
        attack = [draw_fn(1, 3, True), draw_fn(0, 0, False)]
        hurt = [draw_fn(1, 0, False), draw_fn(0, 0, False)]

        anims = {
            "idle": idle,
            "walk": walk,
            "windup": windup,
            "attack": attack,
            "hurt": hurt,
        }
        glow = [{"offset": [24, 24], "color": glow_rgb, "radius": 24}]
        p, j = save_sheet(
            "bosse",
            boss_key,
            anims,
            anchor=(24, 40),
            fps={"idle": 3.0, "walk": 5.0, "windup": 5.0, "attack": 7.0, "hurt": 7.0},
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p, j])

    # Also build trampolinwal and kirchenkrake under kreaturen/ as tested in b19
    for k, glow_rgb, draw_fn in (
        ("trampolinwal", list(JELLY_PINK.highlight[:3]), _draw_trampolinwal),
        ("kirchenkrake", list(FLAME_GOLD.highlight[:3]), _draw_kirchenkrake),
    ):
        idle = [draw_fn(y, 0, False) for y in (0, 1, 0, -1)]
        walk = [
            draw_fn(0, 0, False),
            draw_fn(-1, 3, False),
            draw_fn(0, 0, False),
            draw_fn(1, -3, False),
        ]
        anims = {"idle": idle, "walk": walk}
        glow = [{"offset": [24, 24], "color": glow_rgb, "radius": 20}]
        p, j = save_sheet(
            "kreaturen",
            k,
            anims,
            anchor=(24, 40),
            fps={"idle": 3.0, "walk": 5.0},
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p, j])

    return paths
