"""Contract V8: Regular creature sprite builders across all 9 universes (Cards B06..B14)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from src.universes.catalog import ALL_UNIVERSES
from tools.palette import UNIVERSE_PALETTES
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

# ---------------------------------------------------------------------------
# Sporenklub (Card B07): tuersteherpilz, sporenschnorrer, sporenwerfer, leuchtmotte
# ---------------------------------------------------------------------------


def _draw_tuersteherpilz(offset_y: int = 0, arm_action: int = 0, stomp: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 28)
    pal = UNIVERSE_PALETTES["sporenklub"]
    # Very tall bouncer mushroom body: long muscular torso (18x24 bibel)
    draw_shaded_rect(c, 5, 8 + offset_y, 17, 24 + offset_y, pal["secondary"])
    # Broad red/spotted fly agaric cap on top
    draw_shaded_ellipse(c, 11, 5 + offset_y, 10, 4, pal["primary"])
    # Sunglasses
    draw_shaded_rect(c, 7, 5 + offset_y, 15, 7 + offset_y, pal["secondary"])
    c.set_px(8, 6 + offset_y, (18, 14, 24, 255))
    c.set_px(14, 6 + offset_y, (18, 14, 24, 255))
    # Lamellae beard
    draw_shaded_rect(c, 6, 8 + offset_y, 16, 11 + offset_y, pal["accent"])
    # Clipboard on left arm / muscular shield
    draw_shaded_rect(c, 1, 10 + offset_y, 5, 18 + offset_y, pal["glow"])
    # Right muscular arm pushing
    draw_shaded_rect(
        c, 16 + arm_action, 11 + offset_y, 21 + arm_action, 16 + offset_y, pal["secondary"]
    )
    # Stomp legs at bottom
    if stomp != 0:
        draw_shaded_rect(
            c, max(1, 4 - stomp), 24 + offset_y, min(20, 9 - stomp), 27 + offset_y, pal["primary"]
        )
        draw_shaded_rect(
            c, max(1, 13 + stomp), 24 + offset_y, min(20, 18 + stomp), 27 + offset_y, pal["primary"]
        )
    else:
        draw_shaded_rect(c, 6, 24 + offset_y, 16, 27 + offset_y, pal["primary"])
    apply_dark_outline(c)
    return c


def _draw_sporenschnorrer(
    offset_y: int = 0, leg_stride: int = 0, hand_reach: int = 0
) -> PixelCanvas:
    c = PixelCanvas(12, 20)
    pal = UNIVERSE_PALETTES["sporenklub"]
    # Very thin, hunchback stalk (width 4)
    draw_shaded_rect(c, 4, 8 + offset_y, 8, 17 + offset_y, pal["primary"])
    # Small pointed crooked hood & glowing bald spot
    draw_shaded_ellipse(c, 6, 4 + offset_y, 3, 3, pal["secondary"])
    c.set_px(6, 2 + offset_y, pal["glow"].highlight)
    # Long grasping fingers reaching far out to the side
    draw_shaded_rect(c, 7 + hand_reach, 10 + offset_y, 11 + hand_reach, 13 + offset_y, pal["glow"])
    # Long thin spindly legs
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 3 - leg_stride),
            17 + offset_y,
            min(10, 5 - leg_stride),
            19 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 7 + leg_stride),
            17 + offset_y,
            min(10, 9 + leg_stride),
            19 + offset_y,
            pal["secondary"],
        )
    else:
        draw_shaded_rect(c, 4, 17 + offset_y, 8, 19 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


def _draw_sporenwerfer(offset_y: int = 0, squash: int = 0, charge: bool = False) -> PixelCanvas:
    c = PixelCanvas(24, 16)
    pal = UNIVERSE_PALETTES["sporenklub"]
    # Very squat wide pear-shaped belly (width 18, height 9)
    draw_shaded_ellipse(c, 12, 10 + offset_y + squash, 9, 4, pal["primary"])
    # Wide flat catapult cap on top
    cw = 8 - (1 if charge else 0)
    draw_shaded_ellipse(c, 12, 4 + offset_y + squash, cw, 2, pal["secondary"])
    # Glowing turquoise spore chamber
    draw_shaded_rect(c, 10, 2 + offset_y + squash, 14, 5 + offset_y + squash, pal["glow"])
    c.set_px(12, 3 + offset_y + squash, (150, 255, 255, 255))
    # Wide splayed root feet
    if squash != 0:
        draw_shaded_rect(c, 2, 13 + offset_y + squash, 22, 15 + offset_y, pal["accent"])
    else:
        draw_shaded_rect(c, 4, 13 + offset_y, 20, 15 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def _draw_leuchtmotte(offset_y: int = 0, wing_spread: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 16)
    pal = UNIVERSE_PALETTES["sporenklub"]
    # Fluffy moth body
    draw_shaded_ellipse(c, 8, 8 + offset_y, 3, 5, pal["secondary"])
    # Disco facet eyes
    c.set_px(7, 5 + offset_y, pal["glow"].highlight)
    c.set_px(9, 5 + offset_y, pal["glow"].highlight)
    # Feathery antennae
    c.set_px(6, 3 + offset_y, pal["accent"].light)
    c.set_px(10, 3 + offset_y, pal["accent"].light)
    # Wide neon flutter wings
    wy = 7 + offset_y
    wx1 = max(1, 4 - wing_spread)
    wx2 = min(15, 12 + wing_spread)
    draw_shaded_rect(c, wx1, wy - 3, 6, wy + 3, pal["glow"])
    draw_shaded_rect(c, 10, wy - 3, wx2, wy + 3, pal["primary"])
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Fleischwelt (Card B08): fleischmade, blutegel, saeurespucker, zottenwurm
# 4 distinctive species: maggot, leech, acid spitter, villi worm
# ---------------------------------------------------------------------------


def _draw_fleischmade(offset_y: int = 0, worm_inch: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 14)
    pal = UNIVERSE_PALETTES["fleischwelt"]
    # Plump segmented maggot body
    x1 = max(2, 3 + worm_inch)
    x2 = min(18, 17 - worm_inch)
    draw_shaded_ellipse(
        c, 10, 7 + offset_y, (x2 - x1) // 2 + 1, 4 - (1 if worm_inch > 1 else 0), pal["primary"]
    )
    # Tiny stubby feet
    draw_shaded_rect(c, 5, 11 + offset_y, 15, 12 + offset_y, pal["secondary"])
    # Gaping human-teeth mouth on right
    draw_shaded_rect(c, x2 - 3, 5 + offset_y, x2, 9 + offset_y, pal["accent"])
    c.set_px(x2 - 1, 6 + offset_y, (255, 255, 255, 255))
    c.set_px(x2 - 1, 8 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_blutegel(
    offset_y: int = 0, suction_pulse: int = 0, vertical: bool = False
) -> PixelCanvas:
    c = PixelCanvas(16, 16)
    pal = UNIVERSE_PALETTES["fleischwelt"]
    if vertical:
        # Hanging ceiling leech (vertical)
        draw_shaded_rect(c, 6, 2 + offset_y, 10, 13 + offset_y + suction_pulse, pal["primary"])
        # Circular suction disk at bottom
        draw_shaded_ellipse(c, 8, 13 + offset_y + suction_pulse, 4, 2, pal["glow"])
    else:
        # Horizontal swimming/writhing leech
        draw_shaded_rect(c, 2, 6 + offset_y, 13 + suction_pulse, 10 + offset_y, pal["primary"])
        # Suction ring head on right
        draw_shaded_ellipse(c, 13 + suction_pulse, 8 + offset_y, 2, 4, pal["glow"])
    apply_dark_outline(c)
    return c


def _draw_saeurespucker(offset_y: int = 0, sac_puff: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 18)
    pal = UNIVERSE_PALETTES["fleischwelt"]
    # Swollen polyp stalk
    draw_shaded_rect(c, 5, 9 + offset_y, 13, 16 + offset_y, pal["secondary"])
    # Puffed acid throat sac (glows yellow-green)
    draw_shaded_ellipse(c, 9, 7 + offset_y, 5 + sac_puff, 4 + sac_puff, pal["glow"])
    # Funnel spout mouth pointing up-right
    draw_shaded_rect(c, 11, 3 + offset_y - sac_puff, 15, 6 + offset_y, pal["primary"])
    c.set_px(13, 4 + offset_y - sac_puff, pal["accent"].highlight)
    apply_dark_outline(c)
    return c


def _draw_zottenwurm(offset_y: int = 0, wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 14)
    pal = UNIVERSE_PALETTES["fleischwelt"]
    # Long segmented intestinal villi worm
    for seg in range(4):
        sx = 4 + seg * 4
        sy = 7 + offset_y + (wave if seg % 2 == 0 else -wave)
        draw_shaded_ellipse(c, sx, sy, 3, 4, pal["primary"])
        # Sensory hairs on top of segments
        c.set_px(sx, max(1, sy - 5), pal["accent"].light)
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Aktenhalde (Card B09): aktenfresser, stempler, paragraphenreiter, kaffeegolem
# ---------------------------------------------------------------------------


def _draw_aktenfresser(offset_y: int = 0, mouth_open: int = 0, foot_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 20)
    pal = UNIVERSE_PALETTES["aktenhalde"]
    # Crumpled stack of folders with zipper mouth
    draw_shaded_rect(
        c, 4, 5 + offset_y - mouth_open, 18, 11 + offset_y - mouth_open, pal["primary"]
    )
    draw_shaded_rect(
        c, 4, 11 + offset_y + mouth_open, 18, 16 + offset_y + mouth_open, pal["secondary"]
    )
    # Paperclip teeth inside open drawer
    if mouth_open > 0:
        c.set_px(7, 11 + offset_y, (220, 220, 220, 255))
        c.set_px(14, 11 + offset_y, (220, 220, 220, 255))
        # Yellow post-it tongue
        draw_shaded_rect(c, 9, 11 + offset_y, 12, 13 + offset_y, pal["glow"])
    # Tiny folder feet
    draw_shaded_rect(
        c,
        max(2, 5 - foot_stride),
        16 + offset_y + mouth_open,
        min(20, 8 - foot_stride),
        18 + offset_y,
        pal["accent"],
    )
    draw_shaded_rect(
        c,
        max(2, 14 + foot_stride),
        16 + offset_y + mouth_open,
        min(20, 17 + foot_stride),
        18 + offset_y,
        pal["accent"],
    )
    apply_dark_outline(c)
    return c


def _draw_stempler(offset_y: int = 0, stamp_lift: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 22)
    pal = UNIVERSE_PALETTES["aktenhalde"]
    # Bent hunchback body of ink pad sponges
    draw_shaded_rect(c, 4, 9 + offset_y, 11, 17 + offset_y, pal["primary"])
    # Glasses on nose tip
    draw_shaded_ellipse(c, 6, 6 + offset_y, 3, 3, pal["secondary"])
    c.set_px(8, 6 + offset_y, pal["glow"].highlight)
    # Huge wooden stamp arm held on right
    draw_shaded_rect(
        c, 11, 5 + offset_y - stamp_lift, 14, 15 + offset_y - stamp_lift, pal["accent"]
    )
    c.set_px(12, 15 + offset_y - stamp_lift, (200, 40, 40, 255))  # red ink bottom
    # Thin spidery legs
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 4 - leg_stride),
            17 + offset_y,
            min(14, 6 - leg_stride),
            20 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 9 + leg_stride),
            17 + offset_y,
            min(14, 11 + leg_stride),
            20 + offset_y,
            pal["secondary"],
        )
    else:
        draw_shaded_rect(c, 5, 17 + offset_y, 10, 20 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


def _draw_paragraphenreiter(offset_y: int = 0, wing_flutter: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 22)
    pal = UNIVERSE_PALETTES["aktenhalde"]
    # Winged law book mount (flapping pages)
    wy = 14 + offset_y
    draw_shaded_rect(
        c, max(1, 2 - wing_flutter), wy, min(19, 18 + wing_flutter), wy + 4, pal["secondary"]
    )
    # Bureaucrat rider on top
    draw_shaded_rect(c, 7, 7 + offset_y, 13, 14 + offset_y, pal["primary"])
    # Brass paragraph horn in hands (glowing)
    draw_shaded_rect(c, 13, 5 + offset_y, 17, 8 + offset_y, pal["glow"])
    c.set_px(16, 5 + offset_y, (255, 215, 0, 255))
    apply_dark_outline(c)
    return c


def _draw_kaffeegolem(offset_y: int = 0, steam_bubble: int = 0, stomp: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 24)
    pal = UNIVERSE_PALETTES["aktenhalde"]
    # Clunky coffee machine chassis on filing cabinet legs
    draw_shaded_rect(c, 4, 8 + offset_y, 18, 18 + offset_y, pal["primary"])
    # Seething glass jug head on top with hot steam
    draw_shaded_ellipse(c, 11, 5 + offset_y, 5, 3, pal["secondary"])
    c.set_px(11, 2 + offset_y - steam_bubble, pal["glow"].highlight)  # steam puff
    # Stomp filing cabinet legs
    if stomp != 0:
        draw_shaded_rect(
            c, max(1, 3 - stomp), 18 + offset_y, min(20, 8 - stomp), 22 + offset_y, pal["accent"]
        )
        draw_shaded_rect(
            c, max(1, 14 + stomp), 18 + offset_y, min(20, 19 + stomp), 22 + offset_y, pal["accent"]
        )
    else:
        draw_shaded_rect(c, 5, 18 + offset_y, 17, 22 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Versunkene Abtei (Card B11): moenchsfisch, orgelaal, glockenqualle, korallenwaechter
# ---------------------------------------------------------------------------


def _draw_moenchsfisch(offset_y: int = 0, fin_flutter: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 18)
    pal = UNIVERSE_PALETTES["abtei"]
    # Brown monk hooded robe
    draw_shaded_rect(c, 3, 7 + offset_y, 13, 16 + offset_y, pal["primary"])
    # Scale tonsure head
    draw_shaded_ellipse(c, 8, 4 + offset_y, 4, 3, pal["secondary"])
    # Folded praying fins / bubble mouth
    draw_shaded_rect(c, 9, 8 + offset_y, 14, 11 + offset_y, pal["glow"])
    # Fin flutter underneath
    if fin_flutter != 0:
        c.set_px(max(1, 2 - fin_flutter), 14 + offset_y, pal["accent"].light)
    apply_dark_outline(c)
    return c


def _draw_orgelaal(offset_y: int = 0, pipe_shift: int = 0) -> PixelCanvas:
    c = PixelCanvas(28, 10)
    pal = UNIVERSE_PALETTES["abtei"]
    # Long organ pipe eel body (segmented metallic pipes)
    for p in range(5):
        h = 5 + (p % 3)
        draw_shaded_rect(c, 3 + p * 4, 8 + offset_y - h, 6 + p * 4, 8 + offset_y, pal["primary"])
    # Bellows mouth on right head
    draw_shaded_ellipse(c, 24, 5 + offset_y + pipe_shift, 3, 3, pal["accent"])
    c.set_px(25, 5 + offset_y + pipe_shift, pal["glow"].highlight)
    apply_dark_outline(c)
    return c


def _draw_glockenqualle(offset_y: int = 0, tentacle_pulse: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 20)
    pal = UNIVERSE_PALETTES["abtei"]
    # Translucent jellyfish bell (spherical dome)
    draw_shaded_ellipse(c, 8, 7 + offset_y, 6, 5, pal["primary"])
    # Bronze clapper in bell center (glows)
    draw_shaded_rect(c, 7, 7 + offset_y, 9, 10 + offset_y, pal["accent"])
    c.set_px(8, 9 + offset_y, (255, 215, 0, 255))
    # Pulsing glowing tentacles hanging down
    ty = 12 + offset_y
    for tx in (4, 7, 9, 12):
        draw_shaded_rect(
            c,
            tx,
            ty,
            tx + 1,
            ty + 5 + (tentacle_pulse if tx % 2 == 0 else -tentacle_pulse),
            pal["glow"],
        )
    apply_dark_outline(c)
    return c


def _draw_korallenwaechter(
    offset_y: int = 0, shield_raise: int = 0, claw_walk: int = 0
) -> PixelCanvas:
    c = PixelCanvas(20, 22)
    pal = UNIVERSE_PALETTES["abtei"]
    # Hermit crab in broken church rosette window
    draw_shaded_ellipse(c, 9, 11 + offset_y, 6, 6, pal["primary"])
    # Candle stump on back (glows with flame)
    draw_shaded_rect(c, 8, 2 + offset_y, 11, 6 + offset_y, pal["glow"])
    c.set_px(9, 1 + offset_y, (255, 200, 50, 255))
    # Stained glass shield arm on right
    draw_shaded_rect(
        c, 14, 7 + offset_y - shield_raise, 18, 16 + offset_y - shield_raise, pal["accent"]
    )
    # Crab claws/legs
    if claw_walk != 0:
        draw_shaded_rect(
            c,
            max(1, 3 - claw_walk),
            17 + offset_y,
            min(18, 6 - claw_walk),
            20 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 12 + claw_walk),
            17 + offset_y,
            min(18, 15 + claw_walk),
            20 + offset_y,
            pal["secondary"],
        )
    else:
        draw_shaded_rect(c, 5, 17 + offset_y, 13, 20 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Krümelreich (Card B12): ameisenkrieger, blattlaus, arbeiterameise, harzspucker
# ---------------------------------------------------------------------------


def _draw_ameisenkrieger(offset_y: int = 0, spear_jab: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 16)
    pal = UNIVERSE_PALETTES["kruemelreich"]
    # Red warrior ant body: thorax & abdomen
    draw_shaded_ellipse(c, 6, 9 + offset_y, 4, 3, pal["primary"])
    draw_shaded_ellipse(c, 12, 8 + offset_y, 3, 3, pal["primary"])
    # Thimble helmet & huge mandibles
    draw_shaded_rect(c, 11, 4 + offset_y, 15, 7 + offset_y, pal["secondary"])
    draw_shaded_rect(c, 14, 8 + offset_y, 18, 10 + offset_y, pal["accent"])
    # Toothpick spear in hand
    draw_shaded_rect(c, 12 + spear_jab, 2 + offset_y, 19 + spear_jab, 4 + offset_y, pal["glow"])
    # Chitin legs
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 3 - leg_stride),
            12 + offset_y,
            min(18, 5 - leg_stride),
            15 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 10 + leg_stride),
            12 + offset_y,
            min(18, 12 + leg_stride),
            15 + offset_y,
            pal["secondary"],
        )
    else:
        draw_shaded_rect(c, 4, 12 + offset_y, 14, 15 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


def _draw_blattlaus(offset_y: int = 0, crawl: int = 0) -> PixelCanvas:
    c = PixelCanvas(14, 12)
    pal = UNIVERSE_PALETTES["kruemelreich"]
    # Very round plump droplet aphid
    draw_shaded_ellipse(c, 7, 6 + offset_y, 5, 4, pal["glow"])
    # Milk droplets pattern
    c.set_px(7, 4 + offset_y, (255, 255, 255, 255))
    c.set_px(8, 4 + offset_y, (255, 255, 255, 255))
    draw_shaded_rect(c, 5, 6 + offset_y, 9, 8 + offset_y, pal["accent"])
    # Tiny stubby legs
    draw_shaded_rect(
        c, max(1, 3 - crawl), 10 + offset_y, min(12, 5 - crawl), 11 + offset_y, pal["primary"]
    )
    draw_shaded_rect(
        c, max(1, 9 + crawl), 10 + offset_y, min(12, 11 + crawl), 11 + offset_y, pal["primary"]
    )
    apply_dark_outline(c)
    return c


def _draw_arbeiterameise(offset_y: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 16)
    pal = UNIVERSE_PALETTES["kruemelreich"]
    # Ant body
    draw_shaded_ellipse(c, 6, 9 + offset_y, 3, 3, pal["primary"])
    draw_shaded_ellipse(c, 11, 8 + offset_y, 3, 3, pal["primary"])
    # Bottle-cap basket on back
    draw_shaded_rect(c, 4, 3 + offset_y, 10, 7 + offset_y, pal["secondary"])
    c.set_px(7, 4 + offset_y, (255, 215, 0, 255))
    # Quick legs
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 3 - leg_stride),
            12 + offset_y,
            min(16, 5 - leg_stride),
            15 + offset_y,
            pal["accent"],
        )
        draw_shaded_rect(
            c,
            max(1, 10 + leg_stride),
            12 + offset_y,
            min(16, 12 + leg_stride),
            15 + offset_y,
            pal["accent"],
        )
    else:
        draw_shaded_rect(c, 4, 12 + offset_y, 13, 15 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def _draw_harzspucker(offset_y: int = 0, amber_glow: bool = False, recoil: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 16)
    pal = UNIVERSE_PALETTES["kruemelreich"]
    # Squat heavy artillery ant body
    draw_shaded_rect(c, 4, 7 + offset_y, 16, 13 + offset_y, pal["primary"])
    # Amber resin nozzle on back (glows intensely)
    draw_shaded_rect(c, 3, 3 + offset_y, 8, 7 + offset_y, pal["glow"])
    if amber_glow:
        c.set_px(5, 4 + offset_y, (255, 200, 50, 255))
    # Heavy braced legs
    if recoil != 0:
        draw_shaded_rect(c, 2, 13 + offset_y, 6, 15 + offset_y, pal["secondary"])
        draw_shaded_rect(c, 14, 13 + offset_y, 18, 15 + offset_y, pal["secondary"])
    else:
        draw_shaded_rect(c, 4, 13 + offset_y, 16, 15 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


# ---------------------------------------------------------------------------
# Glibbria (Card B14): huepfling, glibberteiler, zuckerwatte_wolke, konfetti_kanone
# ---------------------------------------------------------------------------


def _draw_huepfling(offset_y: int = 0, squash: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 16)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Round bouncy glassy jelly ball
    draw_shaded_ellipse(c, 8, 8 + offset_y + squash, 5 + squash, 5 - squash, pal["glow"])
    # Big googly eyes & dimpled smile
    c.set_px(6, 6 + offset_y + squash, (40, 40, 40, 255))
    c.set_px(10, 6 + offset_y + squash, (40, 40, 40, 255))
    # Strawberry floating inside
    c.set_px(8, 9 + offset_y + squash, (220, 30, 30, 255))
    apply_dark_outline(c)
    return c


def _draw_glibberteiler(offset_y: int = 0, shake: int = 0) -> PixelCanvas:
    c = PixelCanvas(20, 16)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Angry red-green jelly blob with small teeth & angry brows
    draw_shaded_ellipse(c, 10, 8 + offset_y, 7, 5, pal["primary"])
    # Angry eyebrows & small teeth
    draw_shaded_rect(c, 6 + shake, 5 + offset_y, 14 + shake, 7 + offset_y, pal["accent"])
    c.set_px(8, 9 + offset_y, (255, 255, 255, 255))
    c.set_px(12, 9 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_zuckerwatte_wolke(offset_y: int = 0, puff: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 18)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Floating fluffy pink/blue cotton candy cloud with sleepy eyes
    draw_shaded_ellipse(c, 11, 9 + offset_y, 8 + puff, 6, pal["primary"])
    draw_shaded_ellipse(c, 7, 8 + offset_y, 4, 4, pal["glow"])
    # Sleepy eyes
    c.set_px(9, 8 + offset_y, (80, 80, 120, 255))
    c.set_px(13, 8 + offset_y, (80, 80, 120, 255))
    apply_dark_outline(c)
    return c


def _draw_konfetti_kanone(
    offset_y: int = 0, fuse_spark: int = 0, leg_stride: int = 0
) -> PixelCanvas:
    c = PixelCanvas(18, 18)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Walking party-hat cannon on rubber feet
    draw_shaded_rect(c, 5, 6 + offset_y, 13, 13 + offset_y, pal["primary"])
    # Fuse on top sparking
    c.set_px(9, 3 + offset_y, pal["glow"].highlight)
    c.set_px(9 + fuse_spark, 2 + offset_y, (255, 220, 50, 255))
    # Colorful cannon muzzle on right
    draw_shaded_rect(c, 13, 7 + offset_y, 16, 11 + offset_y, pal["accent"])
    # Rubber bouncy feet
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 4 - leg_stride),
            13 + offset_y,
            min(16, 7 - leg_stride),
            16 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 10 + leg_stride),
            13 + offset_y,
            min(16, 13 + leg_stride),
            16 + offset_y,
            pal["secondary"],
        )
    else:
        draw_shaded_rect(c, 5, 13 + offset_y, 12, 16 + offset_y, pal["secondary"])
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
        pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["sporenklub"])

        for spawn in u.creatures:
            species = spawn.species

            if species == "tuersteherpilz":
                idle = [_draw_tuersteherpilz(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_tuersteherpilz(0, 0, 0),
                    _draw_tuersteherpilz(-1, 0, 3),
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
                    _draw_sporenwerfer(-1, 3),
                    _draw_sporenwerfer(0, 0),
                    _draw_sporenwerfer(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_sporenwerfer(-1, 0, True), _draw_sporenwerfer(0, 0, True)],
                    "attack": [_draw_sporenwerfer(1, 0, False), _draw_sporenwerfer(0, 0, False)],
                    "hurt": [_draw_sporenwerfer(1), _draw_sporenwerfer(0)],
                }
                glow = [{"offset": [9, 5], "color": list(pal["glow"].highlight[:3]), "radius": 12}]
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
                glow = [{"offset": [8, 8], "color": list(pal["glow"].highlight[:3]), "radius": 14}]
            elif species == "fleischmade":
                idle = [_draw_fleischmade(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_fleischmade(0, 0),
                    _draw_fleischmade(0, 3),
                    _draw_fleischmade(0, 0),
                    _draw_fleischmade(0, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_fleischmade(-1, 1), _draw_fleischmade(0, 2)],
                    "attack": [_draw_fleischmade(1, 3), _draw_fleischmade(0, 0)],
                    "hurt": [_draw_fleischmade(1), _draw_fleischmade(0)],
                    "burrow_out": [_draw_fleischmade(2), _draw_fleischmade(0)],
                }
                glow = []
            elif species == "blutegel":
                idle = [_draw_blutegel(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_blutegel(0, 0),
                    _draw_blutegel(-1, 3),
                    _draw_blutegel(0, 0),
                    _draw_blutegel(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_blutegel(-1, 1), _draw_blutegel(0, 2)],
                    "attack": [_draw_blutegel(1, 3), _draw_blutegel(0, 0)],
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
                    "windup": [_draw_saeurespucker(-1, 2), _draw_saeurespucker(0, 3)],
                    "attack": [_draw_saeurespucker(1, 0), _draw_saeurespucker(0, 0)],
                    "hurt": [_draw_saeurespucker(1), _draw_saeurespucker(0)],
                }
                glow = [{"offset": [9, 7], "color": list(pal["glow"].highlight[:3]), "radius": 12}]
            elif species == "zottenwurm":
                idle = [_draw_zottenwurm(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_zottenwurm(0, 0),
                    _draw_zottenwurm(-1, 3),
                    _draw_zottenwurm(0, 0),
                    _draw_zottenwurm(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_zottenwurm(-1, 1), _draw_zottenwurm(0, 2)],
                    "attack": [_draw_zottenwurm(1, 3), _draw_zottenwurm(0, 0)],
                    "hurt": [_draw_zottenwurm(1), _draw_zottenwurm(0)],
                }
                glow = []
            elif species == "aktenfresser":
                idle = [_draw_aktenfresser(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_aktenfresser(0, 0, 0),
                    _draw_aktenfresser(-1, 0, 3),
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
                    _draw_stempler(-1, 0, 3),
                    _draw_stempler(0, 0, 0),
                    _draw_stempler(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_stempler(-1, 3), _draw_stempler(0, 4)],
                    "attack": [_draw_stempler(1, -1), _draw_stempler(0, 0)],
                    "hurt": [_draw_stempler(1), _draw_stempler(0)],
                    "stamp": [_draw_stempler(-2, 4), _draw_stempler(2, -2)],
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
                glow = [{"offset": [15, 6], "color": list(pal["glow"].highlight[:3]), "radius": 12}]
            elif species == "kaffeegolem":
                idle = [_draw_kaffeegolem(y) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_kaffeegolem(0, 0, 0),
                    _draw_kaffeegolem(-1, 0, 4),
                    _draw_kaffeegolem(0, 0, 0),
                    _draw_kaffeegolem(1, 0, -4),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_kaffeegolem(-1, 2), _draw_kaffeegolem(0, 3)],
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
                    _draw_moenchsfisch(1, -2),
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
                    _draw_orgelaal(-1, 3),
                    _draw_orgelaal(0, 0),
                    _draw_orgelaal(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_orgelaal(-1, 1), _draw_orgelaal(0, 2)],
                    "attack": [_draw_orgelaal(1, 3), _draw_orgelaal(0, 0)],
                    "hurt": [_draw_orgelaal(1), _draw_orgelaal(0)],
                    "swim": [_draw_orgelaal(y, 0) for y in (-1, 0, 1, 0)],
                }
                glow = []
            elif species == "glockenqualle":
                idle = [_draw_glockenqualle(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_glockenqualle(0, 0),
                    _draw_glockenqualle(-1, 3),
                    _draw_glockenqualle(0, 0),
                    _draw_glockenqualle(1, -2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_glockenqualle(-1, 1), _draw_glockenqualle(0, 2)],
                    "attack": [_draw_glockenqualle(1, 3), _draw_glockenqualle(0, 0)],
                    "hurt": [_draw_glockenqualle(1), _draw_glockenqualle(0)],
                }
                glow = [{"offset": [8, 8], "color": list(pal["glow"].highlight[:3]), "radius": 14}]
            elif species == "korallenwaechter":
                idle = [_draw_korallenwaechter(y, 0, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_korallenwaechter(0, 0, 0),
                    _draw_korallenwaechter(-1, 0, 3),
                    _draw_korallenwaechter(0, 0, 0),
                    _draw_korallenwaechter(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_korallenwaechter(-1, 3), _draw_korallenwaechter(0, 4)],
                    "attack": [_draw_korallenwaechter(1, 0), _draw_korallenwaechter(0, 0)],
                    "hurt": [_draw_korallenwaechter(1), _draw_korallenwaechter(0)],
                }
                glow = [{"offset": [9, 3], "color": list(pal["glow"].highlight[:3]), "radius": 10}]
            elif species == "ameisenkrieger":
                idle = [_draw_ameisenkrieger(y, 0, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_ameisenkrieger(0, 0, 0),
                    _draw_ameisenkrieger(-1, 0, 3),
                    _draw_ameisenkrieger(0, 0, 0),
                    _draw_ameisenkrieger(1, 0, -3),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_ameisenkrieger(-1, 2), _draw_ameisenkrieger(0, 3)],
                    "attack": [_draw_ameisenkrieger(1, 4), _draw_ameisenkrieger(0, 0)],
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
                    _draw_harzspucker(-1, False, 2),
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
                glow = [{"offset": [5, 5], "color": list(pal["glow"].highlight[:3]), "radius": 12}]
            elif species == "huepfling":
                idle = [_draw_huepfling(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_huepfling(0, 0),
                    _draw_huepfling(-2, -2),
                    _draw_huepfling(0, 0),
                    _draw_huepfling(2, 2),
                ]
                anims = {
                    "idle": idle,
                    "walk": walk,
                    "windup": [_draw_huepfling(-1, -1), _draw_huepfling(0, 0)],
                    "attack": [_draw_huepfling(2, 2), _draw_huepfling(0, 0)],
                    "hurt": [_draw_huepfling(1), _draw_huepfling(0)],
                    "squash": [_draw_huepfling(2, 2), _draw_huepfling(-2, -2)],
                }
                glow = []
            elif species == "glibberteiler":
                idle = [_draw_glibberteiler(y, 0) for y in (0, 1, 0, -1)]
                walk = [
                    _draw_glibberteiler(0, 0),
                    _draw_glibberteiler(-1, 3),
                    _draw_glibberteiler(0, 0),
                    _draw_glibberteiler(1, -2),
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
