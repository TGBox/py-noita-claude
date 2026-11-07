"""Contract V8: Mid-boss and end-boss sprite builders (Cards B15..B19)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from tools.palette import UNIVERSE_PALETTES, ENTITY_PALETTES
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


def _draw_pfuetzenwurm(offset_y: int = 0, coil_shift: int = 0, mouth_open: bool = False) -> PixelCanvas:
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
        draw_shaded_rect(c, max(1, 5 - leg_stride), 18 + offset_y, min(30, 8 - leg_stride), 26 + offset_y, pal["secondary"])
        draw_shaded_rect(c, max(1, 10 + leg_stride), 18 + offset_y, min(30, 13 + leg_stride), 26 + offset_y, pal["secondary"])
        draw_shaded_rect(c, max(1, 16 - leg_stride), 18 + offset_y, min(30, 19 - leg_stride), 26 + offset_y, pal["secondary"])
        draw_shaded_rect(c, max(1, 21 + leg_stride), 18 + offset_y, min(30, 24 + leg_stride), 26 + offset_y, pal["secondary"])
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


def _draw_harzgeneral(offset_y: int = 0, leg_stride: int = 0, claw_open: bool = False) -> PixelCanvas:
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
        draw_shaded_rect(c, max(1, 2 - leg_stride), 22 + offset_y, min(30, 6 - leg_stride), 28 + offset_y, pal["accent"])
        draw_shaded_rect(c, max(1, 18 + leg_stride), 22 + offset_y, min(30, 22 + leg_stride), 28 + offset_y, pal["accent"])
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


def _draw_glockenwaechter(offset_y: int = 0, swing: int = 0, clapper_strike: bool = False) -> PixelCanvas:
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
    draw_shaded_rect(c, max(1, clapper_x - 1), 23 + offset_y, min(28, clapper_x + 2), 28 + offset_y, pal["glow"])
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


def _draw_end_boss_frame(
    boss_key: str,
    u_key: str,
    offset_y: int = 0,
    action: bool = False,
) -> PixelCanvas:
    pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["fleischwelt"])
    w, h = 48, 48

    c = PixelCanvas(w, h)
    
    # Large monolithic end-boss body
    draw_shaded_rect(c, 8, 10 + offset_y, 40, 38 + offset_y, pal["primary"])
    # Head / core chamber
    draw_shaded_ellipse(c, 24, 18 + offset_y, 12, 10, pal["secondary"])
    # Outer carapace / ornaments
    draw_shaded_rect(c, 14, 8 + offset_y, 34, 14 + offset_y, pal["accent"])
    
    # Glow pulsating core / attack focus
    if action:
        draw_shaded_rect(c, 18, 22 + offset_y, 30, 32 + offset_y, pal["glow"])
        c.set_px(24, 27 + offset_y, (255, 255, 255, 255))
    else:
        c.set_px(24, 18 + offset_y, pal["glow"].highlight)

    apply_dark_outline(c)
    return c


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    end_boss_map = [
        ("weltenherz", "fleischwelt"),
        ("oberstempler", "aktenhalde"),
        ("mutter_glibber", "glibbria"),
        ("dj_myzel", "sporenklub"),
        ("ameisenkoenigin", "kruemelreich"),
        ("abt_kieme", "abtei"),
    ]

    paths: list[Path] = []
    for boss_key, u_key in end_boss_map:
        pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["fleischwelt"])
        idle = [_draw_end_boss_frame(boss_key, u_key, y) for y in (0, 1, 0, -1)]
        walk = [_draw_end_boss_frame(boss_key, u_key, y) for y in (0, -1, 0, 1)]
        windup = [_draw_end_boss_frame(boss_key, u_key, -1, True), _draw_end_boss_frame(boss_key, u_key, 0, True)]
        attack = [_draw_end_boss_frame(boss_key, u_key, 1, True), _draw_end_boss_frame(boss_key, u_key, 0, False)]
        hurt = [_draw_end_boss_frame(boss_key, u_key, 1), _draw_end_boss_frame(boss_key, u_key, 0)]

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
    for k, u_key in (("trampolinwal", "glibbria"), ("kirchenkrake", "abtei")):
        pal = UNIVERSE_PALETTES[u_key]
        idle = [_draw_end_boss_frame(k, u_key, y) for y in (0, 1, 0, -1)]
        walk = [_draw_end_boss_frame(k, u_key, y) for y in (0, -1, 0, 1)]
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


def _draw_end_boss_frame(
    boss_key: str,
    u_key: str,
    offset_y: int = 0,
    action: bool = False,
) -> PixelCanvas:
    pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["fleischwelt"])
    w, h = 48, 48

    c = PixelCanvas(w, h)
    
    # Large monolithic end-boss body
    draw_shaded_rect(c, 8, 10 + offset_y, 40, 38 + offset_y, pal["primary"])
    # Head / core chamber
    draw_shaded_ellipse(c, 24, 18 + offset_y, 12, 10, pal["secondary"])
    # Outer carapace / ornaments
    draw_shaded_rect(c, 14, 8 + offset_y, 34, 14 + offset_y, pal["accent"])
    
    # Glow pulsating core / attack focus
    if action:
        draw_shaded_rect(c, 18, 22 + offset_y, 30, 32 + offset_y, pal["glow"])
        c.set_px(24, 27 + offset_y, (255, 255, 255, 255))
    else:
        c.set_px(24, 18 + offset_y, pal["glow"].highlight)

    apply_dark_outline(c)
    return c


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    end_boss_map = [
        ("weltenherz", "fleischwelt"),
        ("oberstempler", "aktenhalde"),
        ("mutter_glibber", "glibbria"),
        ("dj_myzel", "sporenklub"),
        ("ameisenkoenigin", "kruemelreich"),
        ("abt_kieme", "abtei"),
    ]

    paths: list[Path] = []
    for boss_key, u_key in end_boss_map:
        pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["fleischwelt"])
        idle = [_draw_end_boss_frame(boss_key, u_key, y) for y in (0, 1, 0, -1)]
        walk = [_draw_end_boss_frame(boss_key, u_key, y) for y in (0, -1, 0, 1)]
        windup = [_draw_end_boss_frame(boss_key, u_key, -1, True), _draw_end_boss_frame(boss_key, u_key, 0, True)]
        attack = [_draw_end_boss_frame(boss_key, u_key, 1, True), _draw_end_boss_frame(boss_key, u_key, 0, False)]
        hurt = [_draw_end_boss_frame(boss_key, u_key, 1), _draw_end_boss_frame(boss_key, u_key, 0)]

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
    for k, u_key in (("trampolinwal", "glibbria"), ("kirchenkrake", "abtei")):
        pal = UNIVERSE_PALETTES[u_key]
        idle = [_draw_end_boss_frame(k, u_key, y) for y in (0, 1, 0, -1)]
        walk = [_draw_end_boss_frame(k, u_key, y) for y in (0, -1, 0, 1)]
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

