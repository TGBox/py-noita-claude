"""Contract V8: Mid-boss and end-boss sprite builders (Cards B15..B19)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from tools.palette import ENTITY_PALETTES, UNIVERSE_PALETTES
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

# ---------------------------------------------------------------------------
# Mid-Bosses (Cards B15, B16)
# ---------------------------------------------------------------------------


def _draw_pfuetzenwurm(
    offset_y: int = 0, coil_shift: int = 0, mouth_open: bool = False
) -> PixelCanvas:
    c = PixelCanvas(32, 28)
    pal = UNIVERSE_PALETTES["fleischwelt"]
    # Coiled serpentine puddle worm in flesh puddle
    draw_shaded_ellipse(c, 16, 21 + offset_y, 14, 5, pal["primary"])
    # Coiling segments rising up
    draw_shaded_ellipse(c, 11 + coil_shift, 15 + offset_y, 7, 6, pal["secondary"])
    # Worm head with acidic maw
    draw_shaded_ellipse(c, 21 - coil_shift, 10 + offset_y, 8, 6, pal["accent"])
    if mouth_open:
        draw_shaded_ellipse(c, 24 - coil_shift, 10 + offset_y, 4, 3, pal["glow"])
        c.set_px(25 - coil_shift, 10 + offset_y, (255, 255, 255, 255))
    else:
        c.set_px(24 - coil_shift, 8 + offset_y, pal["glow"].highlight)
    apply_dark_outline(c)
    return c


def _draw_aktenwolf(offset_y: int = 0, leg_stride: int = 0, howling: bool = False) -> PixelCanvas:
    c = PixelCanvas(32, 28)
    pal = UNIVERSE_PALETTES["aktenhalde"]
    # Four-legged paper/folder beast with sharp dossier teeth and bristling mane
    # Quadruped torso
    draw_shaded_rect(c, 6, 10 + offset_y, 22, 18 + offset_y, pal["primary"])
    # Wolf head with pointed ears
    head_y = 6 + offset_y - (2 if howling else 0)
    draw_shaded_ellipse(c, 24, head_y + 4, 6, 5, pal["secondary"])
    # Pointed ears
    c.set_px(23, head_y, pal["accent"].highlight)
    c.set_px(26, head_y, pal["accent"].highlight)
    # Glowing red hunter eye
    c.set_px(26, head_y + 3, pal["glow"].highlight)
    # Paper-shredder teeth / snout
    draw_shaded_rect(c, 27, head_y + 4, 30, head_y + 7, pal["accent"])
    # 4 legs walking
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 5 - leg_stride),
            18 + offset_y,
            min(30, 8 - leg_stride),
            26 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 10 + leg_stride),
            18 + offset_y,
            min(30, 13 + leg_stride),
            26 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 16 - leg_stride),
            18 + offset_y,
            min(30, 19 - leg_stride),
            26 + offset_y,
            pal["secondary"],
        )
        draw_shaded_rect(
            c,
            max(1, 21 + leg_stride),
            18 + offset_y,
            min(30, 24 + leg_stride),
            26 + offset_y,
            pal["secondary"],
        )
    else:
        draw_shaded_rect(c, 6, 18 + offset_y, 10, 26 + offset_y, pal["secondary"])
        draw_shaded_rect(c, 18, 18 + offset_y, 22, 26 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


def _draw_manege_clown(offset_y: int = 0, jiggle: int = 0, honk: bool = False) -> PixelCanvas:
    c = PixelCanvas(30, 32)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Pear-shaped bouncy jelly circus clown with giant clown ruffle collar and cone party hat
    # Cone party hat
    draw_shaded_rect(c, 13, 2 + offset_y, 17, 7 + offset_y, pal["accent"])
    c.set_px(15, 1 + offset_y, (255, 255, 255, 255))
    # Head with clown makeup & red bulb nose
    draw_shaded_ellipse(c, 15, 11 + offset_y, 7, 5, pal["glow"])
    c.set_px(15, 11 + offset_y, (230, 30, 30, 255))  # red nose
    c.set_px(12, 10 + offset_y, (30, 30, 30, 255))
    c.set_px(18, 10 + offset_y, (30, 30, 30, 255))
    # Giant frilly collar
    draw_shaded_ellipse(c, 15, 16 + offset_y, 12 + jiggle, 3, pal["secondary"])
    # Big wide bulbous jelly body
    draw_shaded_ellipse(c, 15, 23 + offset_y, 10 - jiggle, 7, pal["primary"])
    if honk:
        c.set_px(15, 11 + offset_y, (255, 220, 0, 255))
    apply_dark_outline(c)
    return c


def _draw_harzgeneral(
    offset_y: int = 0, leg_stride: int = 0, claw_open: bool = False
) -> PixelCanvas:
    c = PixelCanvas(32, 30)
    pal = UNIVERSE_PALETTES["kruemelreich"]
    # Heavy armored ant commander with golden epaulets and huge resin cannon claw
    # Torso & abdomen
    draw_shaded_ellipse(c, 11, 16 + offset_y, 7, 5, pal["primary"])
    draw_shaded_ellipse(c, 21, 14 + offset_y, 6, 5, pal["primary"])
    # Pickelhaube / bicorne general hat
    draw_shaded_rect(c, 16, 4 + offset_y, 27, 9 + offset_y, pal["secondary"])
    c.set_px(21, 3 + offset_y, (255, 215, 0, 255))
    # Giant amber resin claw
    claw_shift = 2 if claw_open else 0
    draw_shaded_rect(c, 22, 11 + offset_y - claw_shift, 29, 17 + offset_y + claw_shift, pal["glow"])
    # Sturdy legs with noticeable stride width
    if leg_stride != 0:
        draw_shaded_rect(
            c,
            max(1, 2 - leg_stride),
            22 + offset_y,
            min(30, 6 - leg_stride),
            28 + offset_y,
            pal["accent"],
        )
        draw_shaded_rect(
            c,
            max(1, 18 + leg_stride),
            22 + offset_y,
            min(30, 22 + leg_stride),
            28 + offset_y,
            pal["accent"],
        )
    else:
        draw_shaded_rect(c, 6, 22 + offset_y, 18, 28 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def _draw_sporenherz(offset_y: int = 0, pulse: int = 0, emit_spores: bool = False) -> PixelCanvas:
    c = PixelCanvas(32, 32)
    pal = UNIVERSE_PALETTES["sporenklub"]
    # Pulsating spore heart hung from fungal tendrils with weeping mushroom tubes
    # Hanging mycelium roots on top
    for rx in (8, 12, 16, 20, 24):
        draw_shaded_rect(c, rx, 1 + offset_y, rx + 1, 8 + offset_y, pal["accent"])
    # Great central mushroom heart dome
    draw_shaded_ellipse(c, 16, 17 + offset_y, 11 + pulse, 10 + pulse, pal["primary"])
    # Glowing neon fungal gills on bottom
    draw_shaded_ellipse(c, 16, 21 + offset_y, 8 + pulse, 5, pal["glow"])
    if emit_spores:
        c.set_px(16, 24 + offset_y, (255, 255, 255, 255))
        c.set_px(12, 22 + offset_y, (255, 255, 255, 255))
        c.set_px(20, 22 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_glockenwaechter(
    offset_y: int = 0, swing: int = 0, clapper_strike: bool = False
) -> PixelCanvas:
    c = PixelCanvas(30, 32)
    pal = UNIVERSE_PALETTES["abtei"]
    # Ancient armored church bell sentinel with dangling ropes and stone armor
    # Suspension yoke / stone crown on top
    draw_shaded_rect(c, 10, 3 + offset_y, 20, 7 + offset_y, pal["secondary"])
    # Massive bronze church bell (trapezoid / conical dome)
    draw_shaded_rect(c, 7 + swing, 7 + offset_y, 23 + swing, 22 + offset_y, pal["primary"])
    draw_shaded_ellipse(c, 15 + swing, 22 + offset_y, 8, 3, pal["accent"])
    # Dangling clapper & glowing rune
    clapper_x = 15 + swing * 2 + (2 if clapper_strike else -2)
    draw_shaded_rect(
        c, max(1, clapper_x - 1), 23 + offset_y, min(28, clapper_x + 2), 28 + offset_y, pal["glow"]
    )
    if clapper_strike:
        c.set_px(clapper_x, 27 + offset_y, (255, 255, 200, 255))
    apply_dark_outline(c)
    return c


def _draw_warden(offset_y: int = 0, arm_swing: int = 0, siren_on: bool = False) -> PixelCanvas:
    c = PixelCanvas(30, 32)
    pal = ENTITY_PALETTES["authority"]
    # Heavy bureaucratic warden golem with flashing siren and filing cabinet chest
    # Flashing siren on head
    c.set_px(15, 2 + offset_y, (255, 50, 50, 255) if siren_on else (150, 20, 20, 255))
    c.set_px(14, 3 + offset_y, pal["glow"].highlight)
    c.set_px(16, 3 + offset_y, pal["glow"].highlight)
    # Steel filing head & visor
    draw_shaded_rect(c, 11, 4 + offset_y, 19, 10 + offset_y, pal["secondary"])
    draw_shaded_rect(c, 12, 7 + offset_y, 18, 8 + offset_y, pal["glow"])
    # Heavy steel cabinet body
    draw_shaded_rect(c, 8, 11 + offset_y, 22, 24 + offset_y, pal["primary"])
    # Handle / lock details
    c.set_px(15, 14 + offset_y, pal["accent"].highlight)
    c.set_px(15, 19 + offset_y, pal["accent"].highlight)
    # Stamping steam arms
    draw_shaded_rect(c, 4, 12 + offset_y - arm_swing, 7, 22 + offset_y - arm_swing, pal["accent"])
    draw_shaded_rect(c, 23, 12 + offset_y + arm_swing, 26, 22 + offset_y + arm_swing, pal["accent"])
    # Massive tank-like treads / legs
    draw_shaded_rect(c, 7, 25 + offset_y, 23, 29 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


def build_mid_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<mid_boss>.{png,json} for all 9 mid-bosses + warden (Cards B15, B16)."""
    boss_specs = [
        ("pfuetzenwurm", "fleischwelt", _draw_pfuetzenwurm),
        ("aktenwolf", "aktenhalde", _draw_aktenwolf),
        ("manege_clown", "glibbria", _draw_manege_clown),
        ("harzgeneral", "kruemelreich", _draw_harzgeneral),
        ("sporenherz", "sporenklub", _draw_sporenherz),
        ("glockenwaechter", "abtei", _draw_glockenwaechter),
        ("warden", "aktenhalde", _draw_warden),
    ]

    paths: list[Path] = []
    for boss_key, u_key, draw_fn in boss_specs:
        pal = UNIVERSE_PALETTES.get(u_key, ENTITY_PALETTES["authority"])
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
        glow = [{"offset": [15, 15], "color": list(pal["glow"].highlight[:3]), "radius": 16}]
        p, j = save_sheet(
            "bosse",
            boss_key,
            anims,
            anchor=(15, 27),
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
    pal = UNIVERSE_PALETTES["fleischwelt"]
    # Beating heart hanging from aorta veins, dripping blood
    # Massive aorta root tubes branching upwards
    for ax in (16, 20, 24, 28, 32):
        draw_shaded_rect(c, ax, 2 + offset_y, ax + 2, 12 + offset_y, pal["accent"])
    # Two great ventricles / heart lobes forming anatomical heart shape
    r = 13 + beat_pulse
    draw_shaded_ellipse(c, 18, 22 + offset_y, r, r + 2, pal["primary"])
    draw_shaded_ellipse(c, 30, 22 + offset_y, r, r + 2, pal["primary"])
    # Heart apex pointing down
    draw_shaded_ellipse(c, 24, 32 + offset_y, 11 + beat_pulse, 9 + beat_pulse, pal["secondary"])
    # Pulsing glowing veins / core
    if action:
        draw_shaded_rect(c, 20, 22 + offset_y, 28, 30 + offset_y, pal["glow"])
        c.set_px(24, 26 + offset_y, (255, 255, 255, 255))
    else:
        c.set_px(24, 25 + offset_y, pal["glow"].highlight)
    apply_dark_outline(c)
    return c


def _draw_oberstempler(offset_y: int = 0, arm_shift: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["aktenhalde"]
    # Bureaucrat titan made of stacked mahogany desks, clock face, massive stamp hammer arms
    # Clock face head on top
    draw_shaded_ellipse(c, 24, 9 + offset_y, 8, 8, pal["accent"])
    c.set_px(24, 9 + offset_y, (255, 215, 0, 255))  # clock center
    c.set_px(24, 6 + offset_y, (40, 40, 40, 255))  # hands
    c.set_px(27, 9 + offset_y, (40, 40, 40, 255))
    # Massive stacked desk torso (wide rectangular tiered block)
    draw_shaded_rect(c, 10, 18 + offset_y, 38, 34 + offset_y, pal["primary"])
    # Drawers & brass handles
    draw_shaded_rect(c, 14, 22 + offset_y, 34, 24 + offset_y, pal["secondary"])
    c.set_px(24, 23 + offset_y, pal["glow"].highlight)
    draw_shaded_rect(c, 14, 28 + offset_y, 34, 30 + offset_y, pal["secondary"])
    c.set_px(24, 29 + offset_y, pal["glow"].highlight)
    # Giant stamp arms hanging on sides
    draw_shaded_rect(c, 4, 16 + offset_y - arm_shift, 9, 38 + offset_y - arm_shift, pal["accent"])
    draw_shaded_rect(c, 39, 16 + offset_y + arm_shift, 44, 38 + offset_y + arm_shift, pal["accent"])
    # Sturdy desk pedestal feet
    draw_shaded_rect(c, 12, 35 + offset_y, 18, 43 + offset_y, pal["secondary"])
    draw_shaded_rect(c, 30, 35 + offset_y, 36, 43 + offset_y, pal["secondary"])
    if action:
        draw_shaded_rect(c, 4, 36 + offset_y - arm_shift, 9, 41 + offset_y - arm_shift, pal["glow"])
    apply_dark_outline(c)
    return c


def _draw_mutter_glibber(offset_y: int = 0, ripple: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Colossal gelatinous queen jelly mount with floating crown and internal embryonic blobs
    # Golden crown floating on jelly top
    draw_shaded_rect(c, 18, 5 + offset_y, 30, 11 + offset_y, pal["accent"])
    c.set_px(20, 4 + offset_y, (255, 215, 0, 255))
    c.set_px(24, 3 + offset_y, (255, 255, 255, 255))
    c.set_px(28, 4 + offset_y, (255, 215, 0, 255))
    # Colossal sprawling jelly mass (wide semi-dome)
    draw_shaded_ellipse(c, 24, 28 + offset_y, 20 + ripple, 14 - ripple, pal["primary"])
    draw_shaded_ellipse(c, 24, 24 + offset_y, 15 + ripple, 10, pal["glow"])
    # Embryonic baby jelly floating inside
    draw_shaded_ellipse(c, 18, 27 + offset_y, 4, 4, pal["secondary"])
    draw_shaded_ellipse(c, 30, 27 + offset_y, 4, 4, pal["secondary"])
    if action:
        draw_shaded_ellipse(c, 24, 26 + offset_y, 7, 7, pal["accent"])
        c.set_px(24, 26 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_dj_myzel(offset_y: int = 0, beat_bounce: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["sporenklub"]
    # Towering mushroom DJ behind two giant vinyl turntables and neon speaker stacks
    # Massive mushroom cap with headphones
    draw_shaded_ellipse(c, 24, 12 + offset_y, 17, 8, pal["primary"])
    # DJ Headphone arc
    draw_shaded_rect(c, 9, 7 + offset_y, 39, 10 + offset_y, pal["accent"])
    draw_shaded_rect(c, 8, 10 + offset_y, 11, 15 + offset_y, pal["glow"])
    draw_shaded_rect(c, 37, 10 + offset_y, 40, 15 + offset_y, pal["glow"])
    # Stem body behind desk
    draw_shaded_rect(c, 20, 18 + offset_y, 28, 30 + offset_y, pal["secondary"])
    # Giant DJ mixing console / turntables in front
    draw_shaded_rect(c, 6, 28 + offset_y, 42, 40 + offset_y, pal["primary"])
    # Left turntable platter
    draw_shaded_ellipse(c, 15, 34 + offset_y, 7, 4, pal["accent"])
    c.set_px(15, 34 + offset_y, pal["glow"].highlight)
    # Right turntable platter
    draw_shaded_ellipse(c, 33, 34 + offset_y, 7, 4, pal["accent"])
    c.set_px(33, 34 + offset_y, pal["glow"].highlight)
    if action:
        draw_shaded_rect(c, 21, 31 + offset_y, 27, 36 + offset_y, pal["glow"])
        c.set_px(24, 33 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_ameisenkoenigin(offset_y: int = 0, crawl: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["kruemelreich"]
    # Gigantic bloated queen ant with royal crown, segmented egg-laying abdomen
    # Royal crown on ant head
    draw_shaded_rect(c, 31, 9 + offset_y, 40, 14 + offset_y, pal["accent"])
    c.set_px(33, 8 + offset_y, (255, 215, 0, 255))
    c.set_px(36, 7 + offset_y, (255, 255, 255, 255))
    c.set_px(39, 8 + offset_y, (255, 215, 0, 255))
    # Head & giant mandibles
    draw_shaded_ellipse(c, 35, 18 + offset_y, 7, 6, pal["secondary"])
    draw_shaded_rect(c, 41, 16 + offset_y, 46, 21 + offset_y, pal["accent"])
    # Mid-body thorax
    draw_shaded_ellipse(c, 26, 22 + offset_y, 6, 6, pal["primary"])
    # Huge elongated egg-bloated abdomen on left
    draw_shaded_ellipse(c, 13, 27 + offset_y, 11, 9, pal["primary"])
    draw_shaded_ellipse(c, 13, 27 + offset_y, 7, 6, pal["glow"])
    # Many crawling legs beneath
    if crawl != 0:
        draw_shaded_rect(c, 18 - crawl, 33 + offset_y, 22 - crawl, 42 + offset_y, pal["secondary"])
        draw_shaded_rect(c, 28 + crawl, 33 + offset_y, 32 + crawl, 42 + offset_y, pal["secondary"])
    else:
        draw_shaded_rect(c, 19, 33 + offset_y, 31, 42 + offset_y, pal["secondary"])
    if action:
        draw_shaded_rect(c, 42, 17 + offset_y, 46, 20 + offset_y, pal["glow"])
        c.set_px(45, 18 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_abt_kieme(offset_y: int = 0, robe_flutter: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["abtei"]
    # Ancient venerable fish abbot in towering papal miter on a floating stone pulpit
    # Towering bishop/papal miter (tall pointed hat with golden cross)
    draw_shaded_rect(c, 21, 2 + offset_y, 27, 12 + offset_y, pal["accent"])
    c.set_px(24, 6 + offset_y, (255, 215, 0, 255))
    c.set_px(23, 7 + offset_y, (255, 215, 0, 255))
    c.set_px(25, 7 + offset_y, (255, 215, 0, 255))
    # Fish abbot head with flowing white barbels and glass bowl helmet
    draw_shaded_ellipse(c, 24, 16 + offset_y, 8, 6, pal["secondary"])
    c.set_px(21, 15 + offset_y, pal["glow"].highlight)
    # Towering monastic ceremonial robe with organ pipe back
    draw_shaded_rect(
        c, 17 - robe_flutter, 21 + offset_y, 31 + robe_flutter, 33 + offset_y, pal["primary"]
    )
    for opx in (18, 22, 26, 30):
        draw_shaded_rect(c, opx, 10 + offset_y, opx + 1, 21 + offset_y, pal["accent"])
    # Floating pulpit base (carved stone boat/chalice)
    draw_shaded_ellipse(c, 24, 38 + offset_y, 14, 5, pal["secondary"])
    draw_shaded_rect(c, 14, 34 + offset_y, 34, 38 + offset_y, pal["primary"])
    if action:
        draw_shaded_rect(c, 22, 24 + offset_y, 26, 28 + offset_y, pal["glow"])
        c.set_px(24, 26 + offset_y, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_trampolinwal(offset_y: int = 0, fin_flap: int = 0, action: bool = False) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["glibbria"]
    # Immense floating jelly whale with trampoline back and candy blowhole
    # Giant streamlined whale body
    draw_shaded_ellipse(c, 24, 24 + offset_y, 19, 11, pal["primary"])
    # Trampoline taut skin on whale back
    draw_shaded_rect(c, 12, 14 + offset_y, 36, 17 + offset_y, pal["accent"])
    c.set_px(24, 15 + offset_y, (255, 255, 255, 255))
    # Fluked whale tail on left
    draw_shaded_ellipse(c, 6, 22 + offset_y - fin_flap, 4, 7, pal["secondary"])
    # Pectoral flipper
    draw_shaded_ellipse(c, 28, 30 + offset_y + fin_flap, 6, 4, pal["secondary"])
    # Smiling whale eye
    c.set_px(37, 23 + offset_y, pal["glow"].highlight)
    apply_dark_outline(c)
    return c


def _draw_kirchenkrake(
    offset_y: int = 0, tentacle_wave: int = 0, action: bool = False
) -> PixelCanvas:
    c = PixelCanvas(48, 48)
    pal = UNIVERSE_PALETTES["abtei"]
    # Colossal abyssal kraken with cathedral bell helmet and candelabra tentacles
    # Grand cathedral bell dome helmet
    draw_shaded_rect(c, 16, 5 + offset_y, 32, 18 + offset_y, pal["accent"])
    c.set_px(24, 4 + offset_y, (255, 215, 0, 255))
    # Central cephalopod body & glowing ancient eyes
    draw_shaded_ellipse(c, 24, 23 + offset_y, 12, 8, pal["primary"])
    c.set_px(19, 23 + offset_y, pal["glow"].highlight)
    c.set_px(29, 23 + offset_y, pal["glow"].highlight)
    # Huge writhing tentacles holding lit candles
    for i, tx in enumerate((8, 15, 24, 33, 40)):
        shift = tentacle_wave if i % 2 == 0 else -tentacle_wave
        draw_shaded_rect(
            c, tx + shift, 28 + offset_y, tx + shift + 2, 42 + offset_y, pal["secondary"]
        )
        # Candle flame at tip
        c.set_px(tx + shift + 1, 27 + offset_y, (255, 200, 50, 255))
    apply_dark_outline(c)
    return c


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    end_boss_specs = [
        ("weltenherz", "fleischwelt", _draw_weltenherz),
        ("oberstempler", "aktenhalde", _draw_oberstempler),
        ("mutter_glibber", "glibbria", _draw_mutter_glibber),
        ("dj_myzel", "sporenklub", _draw_dj_myzel),
        ("ameisenkoenigin", "kruemelreich", _draw_ameisenkoenigin),
        ("abt_kieme", "abtei", _draw_abt_kieme),
    ]

    paths: list[Path] = []
    for boss_key, u_key, draw_fn in end_boss_specs:
        pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["fleischwelt"])
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
        glow = [{"offset": [24, 24], "color": list(pal["glow"].highlight[:3]), "radius": 24}]
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
    for k, u_key, draw_fn in (
        ("trampolinwal", "glibbria", _draw_trampolinwal),
        ("kirchenkrake", "abtei", _draw_kirchenkrake),
    ):
        pal = UNIVERSE_PALETTES[u_key]
        idle = [draw_fn(y, 0, False) for y in (0, 1, 0, -1)]
        walk = [
            draw_fn(0, 0, False),
            draw_fn(-1, 3, False),
            draw_fn(0, 0, False),
            draw_fn(1, -3, False),
        ]
        anims = {"idle": idle, "walk": walk}
        glow = [{"offset": [24, 24], "color": list(pal["glow"].highlight[:3]), "radius": 20}]
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
