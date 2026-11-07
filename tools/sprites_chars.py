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


def _draw_char_frame(
    palette_key: str,
    offset_y: int = 0,
    cast_arm: bool = False,
    arm_swing: int = 0,
    leg_stride: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    pal = ENTITY_PALETTES.get(palette_key, ENTITY_PALETTES["spielerin"])
    # Cloak / coat body
    draw_shaded_rect(c, 5, 10 + offset_y, 15, 19 + offset_y, pal["primary"])
    # Legs / hem opening showing movement
    if leg_stride != 0:
        # One leg extended forward, one back
        lx1 = 10 - leg_stride
        lx2 = 10 + leg_stride
        draw_shaded_rect(
            c, max(1, lx1 - 2), 19 + offset_y, min(18, lx1 + 2), 22 + offset_y, pal["secondary"]
        )
        draw_shaded_rect(
            c, max(1, lx2 - 2), 19 + offset_y, min(18, lx2 + 2), 22 + offset_y, pal["secondary"]
        )
    else:
        draw_shaded_rect(c, 7, 19 + offset_y, 13, 22 + offset_y, pal["secondary"])
    # Hood / head
    draw_shaded_ellipse(c, 10, 6 + offset_y, 5, 5, pal["secondary"])
    # Face visor / shadow inside hood
    draw_shaded_rect(c, 7, 6 + offset_y, 13, 8 + offset_y, pal["accent"])
    # Casting arm / wand or arms swinging
    if cast_arm:
        draw_shaded_rect(c, 14, 11 + offset_y, 18, 14 + offset_y, pal["secondary"])
        c.set_px(18, 12 + offset_y, (255, 255, 255, 255))
    elif arm_swing != 0:
        draw_shaded_rect(
            c, 10 + arm_swing, 11 + offset_y, 13 + arm_swing + 2, 15 + offset_y, pal["secondary"]
        )
        c.set_px(10 + arm_swing, 13 + offset_y, pal["accent"].light)
    else:
        c.set_px(15, 13 + offset_y, pal["accent"].light)
    apply_dark_outline(c)
    return c


def build_player_sheet(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/spielerin.{png,json} (Card B01)."""
    idle_frames = [_draw_char_frame("spielerin", y) for y in (0, 1, 0, -1)]
    walk_frames = [
        _draw_char_frame("spielerin", 0, leg_stride=0, arm_swing=0),
        _draw_char_frame("spielerin", -1, leg_stride=4, arm_swing=4),
        _draw_char_frame("spielerin", 0, leg_stride=0, arm_swing=0),
        _draw_char_frame("spielerin", 1, leg_stride=-4, arm_swing=-4),
    ]
    jump_frames = [
        _draw_char_frame("spielerin", -2, leg_stride=2),
        _draw_char_frame("spielerin", -1, leg_stride=1),
    ]
    fall_frames = [
        _draw_char_frame("spielerin", 1, leg_stride=2),
        _draw_char_frame("spielerin", 2, leg_stride=0),
    ]
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


def _draw_klonita_frame(
    offset_y: int = 0,
    lantern_wave: int = 0,
    hem_flutter: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(18, 22)
    pal = ENTITY_PALETTES["klonita"]
    # Floating hem robe with flutter
    x1 = max(1, 3 - hem_flutter)
    x2 = min(17, 14 + hem_flutter)
    draw_shaded_rect(c, x1, 9 + offset_y, x2, 19 + offset_y, pal["primary"])
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
    idle_frames = [_draw_klonita_frame(y, w, 0) for y, w in ((0, 0), (-1, 1), (0, 0), (1, -1))]
    fly_frames = [
        _draw_klonita_frame(0, 0, 0),
        _draw_klonita_frame(-2, 1, 3),
        _draw_klonita_frame(-1, 0, 0),
        _draw_klonita_frame(0, -1, -2),
    ]
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


def _draw_agent_drohne_frame(offset_y: int = 0, prop_rot: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 18)
    pal = ENTITY_PALETTES["authority"]
    # Propeller on top
    px = 9
    py = 2 + offset_y
    draw_shaded_rect(
        c, max(2, px - 6 + prop_rot), py, min(16, px + 6 - prop_rot), py + 1, pal["secondary"]
    )
    c.set_px(px, py + 1, pal["primary"].shadow)
    # Flying briefcase body (10x8)
    draw_shaded_rect(c, 4, 4 + offset_y, 14, 12 + offset_y, pal["primary"])
    # Metal latches and corners
    c.set_px(4, 5 + offset_y, pal["accent"].highlight)
    c.set_px(13, 5 + offset_y, pal["accent"].highlight)
    # Camera eye / lens in center (glows)
    draw_shaded_ellipse(c, 9, 8 + offset_y, 3, 3, pal["secondary"])
    draw_shaded_rect(c, 8, 7 + offset_y, 10, 9 + offset_y, pal["glow"])
    c.set_px(9, 8 + offset_y, (255, 50, 50, 255))
    apply_dark_outline(c)
    return c


def _draw_agent_sachbearbeiter_frame(
    offset_y: int = 0,
    arm_action: bool = False,
    arm_swing: int = 0,
    leg_stride: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    pal = ENTITY_PALETTES["authority"]
    # Slim grey suit body
    draw_shaded_rect(c, 6, 10 + offset_y, 14, 19 + offset_y, pal["primary"])
    # Head with fedora hat (wider brim for distinct silhouette)
    draw_shaded_rect(c, 5, 5 + offset_y, 15, 6 + offset_y, pal["secondary"])
    draw_shaded_rect(c, 7, 2 + offset_y, 13, 5 + offset_y, pal["primary"])
    # Mask with seal / single optic eye
    draw_shaded_rect(c, 8, 7 + offset_y, 12, 9 + offset_y, pal["glow"])
    c.set_px(10, 8 + offset_y, (180, 220, 255, 255))
    # Red tie
    c.set_px(10, 11 + offset_y, (220, 50, 50, 255))
    c.set_px(10, 12 + offset_y, (220, 50, 50, 255))
    # Legs
    if leg_stride != 0:
        lx1 = 10 - leg_stride
        lx2 = 10 + leg_stride
        draw_shaded_rect(
            c, max(1, lx1 - 1), 19 + offset_y, min(18, lx1 + 2), 22 + offset_y, pal["secondary"]
        )
        draw_shaded_rect(
            c, max(1, lx2 - 1), 19 + offset_y, min(18, lx2 + 2), 22 + offset_y, pal["secondary"]
        )
    else:
        draw_shaded_rect(c, 8, 19 + offset_y, 12, 22 + offset_y, pal["secondary"])
    if arm_action:
        draw_shaded_rect(c, 14, 11 + offset_y, 18, 14 + offset_y, pal["secondary"])
        c.set_px(17, 12 + offset_y, pal["glow"].highlight)
    elif arm_swing != 0:
        draw_shaded_rect(
            c, 10 + arm_swing, 12 + offset_y, 13 + arm_swing + 2, 16 + offset_y, pal["secondary"]
        )
    else:
        # Briefcase held in hand at side
        draw_shaded_rect(c, 13, 14 + offset_y, 18, 19 + offset_y, pal["accent"])
        c.set_px(15, 13 + offset_y, pal["secondary"].mid)
    apply_dark_outline(c)
    return c


def _draw_agent_vollstrecker_frame(
    offset_y: int = 0,
    shield_pos: int = 0,
    leg_stride: int = 0,
    shoulder_tilt: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(24, 26)
    pal = ENTITY_PALETTES["authority"]
    # Heavy broad trenchcoat body with massive pauldrons (width 18)
    draw_shaded_rect(c, 3, 9 + offset_y, 21, 21 + offset_y, pal["primary"])
    # Heavy armored block helmet
    draw_shaded_rect(c, 8, 3 + offset_y, 16, 8 + offset_y, pal["secondary"])
    # Heavy shoulder lamp / searchlight on left shoulder
    draw_shaded_rect(
        c, 2, 5 + offset_y + shoulder_tilt, 6, 9 + offset_y + shoulder_tilt, pal["glow"]
    )
    c.set_px(4, 7 + offset_y + shoulder_tilt, (255, 255, 180, 255))
    # Visor slit glow (horizontal slit)
    draw_shaded_rect(c, 9, 6 + offset_y, 15, 7 + offset_y, pal["glow"])
    # Heavy stomp legs
    if leg_stride != 0:
        lx1 = 11 - leg_stride
        lx2 = 11 + leg_stride
        draw_shaded_rect(
            c, max(1, lx1 - 2), 21 + offset_y, min(22, lx1 + 3), 24 + offset_y, pal["secondary"]
        )
        draw_shaded_rect(
            c, max(1, lx2 - 2), 21 + offset_y, min(22, lx2 + 3), 24 + offset_y, pal["secondary"]
        )
    else:
        draw_shaded_rect(c, 6, 21 + offset_y, 16, 24 + offset_y, pal["secondary"])
    # Massive heavy stamp / riot shield on right side
    bx = 16 + shield_pos
    draw_shaded_rect(c, min(22, bx), 9 + offset_y, min(23, bx + 6), 20 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def _draw_agent_abteilungsleiter_frame(
    offset_y: int = 0,
    float_wave: int = 0,
    mantle_spread: int = 0,
) -> PixelCanvas:
    c = PixelCanvas(26, 28)
    pal = ENTITY_PALETTES["authority"]
    # Floating robe / formal authority mantle with billowing wings
    m1 = max(1, 4 - mantle_spread)
    m2 = min(24, 21 + mantle_spread)
    draw_shaded_rect(c, m1, 12 + offset_y, m2, 25 + offset_y, pal["primary"])
    # Head / mask
    draw_shaded_ellipse(c, 13, 8 + offset_y, 5, 5, pal["secondary"])
    # Huge Crown / golden § symbol on head (high vertical silhouette)
    draw_shaded_rect(c, 10 + float_wave, 1 + offset_y, 16 + float_wave, 5 + offset_y, pal["glow"])
    c.set_px(13 + float_wave, 3 + offset_y, (255, 215, 0, 255))
    # Glowing legal scroll or aura hands
    draw_shaded_rect(c, 2, 14 + offset_y, 6, 18 + offset_y, pal["accent"])
    draw_shaded_rect(c, 19, 14 + offset_y, 23, 18 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def build_agent_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/agent_*.{png,json} (Card B03)."""
    paths: list[Path] = []

    # 1. agent_sachbearbeiter & agent_streife
    sb_idle = [_draw_agent_sachbearbeiter_frame(y) for y in (0, 1, 0, -1)]
    sb_walk = [
        _draw_agent_sachbearbeiter_frame(0, arm_swing=0, leg_stride=0),
        _draw_agent_sachbearbeiter_frame(-1, arm_swing=3, leg_stride=3),
        _draw_agent_sachbearbeiter_frame(0, arm_swing=0, leg_stride=0),
        _draw_agent_sachbearbeiter_frame(1, arm_swing=-3, leg_stride=-3),
    ]
    sb_windup = [
        _draw_agent_sachbearbeiter_frame(-1, True),
        _draw_agent_sachbearbeiter_frame(0, True),
    ]
    sb_attack = [
        _draw_agent_sachbearbeiter_frame(1, True),
        _draw_agent_sachbearbeiter_frame(0, False),
    ]
    sb_hurt = [_draw_agent_sachbearbeiter_frame(1), _draw_agent_sachbearbeiter_frame(0)]
    sb_dead = [_draw_agent_sachbearbeiter_frame(2)]
    sb_anims = {
        "idle": sb_idle,
        "walk": sb_walk,
        "windup": sb_windup,
        "attack": sb_attack,
        "hurt": sb_hurt,
        "dead": sb_dead,
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

    # 2. agent_drohne (flying drone)
    dr_idle = [_draw_agent_drohne_frame(y, p) for y, p in ((0, 0), (-1, 2), (0, 0), (1, -2))]
    dr_walk = [
        _draw_agent_drohne_frame(0, 0),
        _draw_agent_drohne_frame(-1, 3),
        _draw_agent_drohne_frame(0, -1),
        _draw_agent_drohne_frame(1, -3),
    ]
    dr_windup = [_draw_agent_drohne_frame(-1, 1), _draw_agent_drohne_frame(-2, 2)]
    dr_attack = [_draw_agent_drohne_frame(0, 3), _draw_agent_drohne_frame(1, 0)]
    dr_hurt = [_draw_agent_drohne_frame(1, 0), _draw_agent_drohne_frame(2, 0)]
    dr_dead = [_draw_agent_drohne_frame(3, 0)]
    dr_anims = {
        "idle": dr_idle,
        "walk": dr_walk,
        "windup": dr_windup,
        "attack": dr_attack,
        "hurt": dr_hurt,
        "dead": dr_dead,
    }
    glow_dr = [{"offset": [9, 8], "color": [255, 50, 50], "radius": 12}]
    p, j = save_sheet(
        "charaktere",
        "agent_drohne",
        dr_anims,
        anchor=(9, 14),
        fps={"idle": 6.0, "walk": 8.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow_dr,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    # 3. agent_vollstrecker
    vs_idle = [_draw_agent_vollstrecker_frame(y, 0) for y in (0, 1, 0, -1)]
    vs_walk = [
        _draw_agent_vollstrecker_frame(0, 0, leg_stride=0, shoulder_tilt=0),
        _draw_agent_vollstrecker_frame(-1, 2, leg_stride=4, shoulder_tilt=2),
        _draw_agent_vollstrecker_frame(0, 0, leg_stride=0, shoulder_tilt=0),
        _draw_agent_vollstrecker_frame(1, -2, leg_stride=-4, shoulder_tilt=-1),
    ]
    vs_windup = [_draw_agent_vollstrecker_frame(-1, -1), _draw_agent_vollstrecker_frame(0, -1)]
    vs_attack = [_draw_agent_vollstrecker_frame(1, 2), _draw_agent_vollstrecker_frame(0, 1)]
    vs_hurt = [_draw_agent_vollstrecker_frame(1, 0), _draw_agent_vollstrecker_frame(0, 0)]
    vs_dead = [_draw_agent_vollstrecker_frame(2, 0)]
    vs_anims = {
        "idle": vs_idle,
        "walk": vs_walk,
        "windup": vs_windup,
        "attack": vs_attack,
        "hurt": vs_hurt,
        "dead": vs_dead,
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

    # 4. agent_abteilungsleiter
    al_idle = [
        _draw_agent_abteilungsleiter_frame(y, w, 0) for y, w in ((0, 0), (-1, 1), (0, 0), (1, -1))
    ]
    al_fly = [_draw_agent_abteilungsleiter_frame(y, 0, 0) for y in (-1, -2, -1, 0)]
    al_walk = [
        _draw_agent_abteilungsleiter_frame(0, 0, 0),
        _draw_agent_abteilungsleiter_frame(-1, 1, 3),
        _draw_agent_abteilungsleiter_frame(0, 0, 0),
        _draw_agent_abteilungsleiter_frame(1, -1, -2),
    ]
    al_windup = [
        _draw_agent_abteilungsleiter_frame(-1, 0),
        _draw_agent_abteilungsleiter_frame(-2, 1),
    ]
    al_attack = [_draw_agent_abteilungsleiter_frame(0, 1), _draw_agent_abteilungsleiter_frame(1, 0)]
    al_hurt = [_draw_agent_abteilungsleiter_frame(1, 0), _draw_agent_abteilungsleiter_frame(0, 0)]
    al_dead = [_draw_agent_abteilungsleiter_frame(2, 0)]
    al_anims = {
        "idle": al_idle,
        "walk": al_walk,
        "fly": al_fly,
        "windup": al_windup,
        "attack": al_attack,
        "hurt": al_hurt,
        "dead": al_dead,
    }
    glow = [{"offset": [13, 3], "color": [255, 215, 0], "radius": 14}]
    p, j = save_sheet(
        "charaktere",
        "agent_abteilungsleiter",
        al_anims,
        anchor=(13, 26),
        fps={
            "idle": 5.0,
            "walk": 7.0,
            "fly": 7.0,
            "windup": 6.0,
            "attack": 10.0,
            "hurt": 8.0,
            "dead": 1.0,
        },
        glow=glow,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    return paths


def _draw_boese_kaiserin_frame(offset_y: int = 0, leg_stride: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 28)
    pal = ENTITY_PALETTES["evil_kaiserin"]
    # Gold armor & red imperial cloak
    draw_shaded_rect(c, 4, 12 + offset_y, 18, 24 + offset_y, pal["primary"])
    # Head
    draw_shaded_ellipse(c, 11, 8 + offset_y, 4, 4, pal["secondary"])
    # Tower hair style & crown with antenna (distinctive high silhouette)
    draw_shaded_rect(c, 9, 2 + offset_y, 13, 7 + offset_y, pal["secondary"])
    draw_shaded_rect(c, 7, 5 + offset_y, 15, 7 + offset_y, pal["accent"])
    c.set_px(11, 1 + offset_y, (255, 215, 0, 255))  # antenna tip
    # Legs
    if leg_stride != 0:
        lx1 = 11 - leg_stride
        lx2 = 11 + leg_stride
        draw_shaded_rect(
            c, max(1, lx1 - 1), 24 + offset_y, min(20, lx1 + 2), 26 + offset_y, pal["accent"]
        )
        draw_shaded_rect(
            c, max(1, lx2 - 1), 24 + offset_y, min(20, lx2 + 2), 26 + offset_y, pal["accent"]
        )
    else:
        draw_shaded_rect(c, 9, 24 + offset_y, 13, 26 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def _draw_boese_gute_frame(offset_y: int = 0, robe_flutter: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 26)
    pal = ENTITY_PALETTES["evil_gute"]
    # White/green cultist flowing robe (billowing float)
    rx1 = max(1, 4 - robe_flutter)
    rx2 = min(20, 17 + robe_flutter)
    draw_shaded_rect(c, rx1, 10 + offset_y, rx2, 23 + offset_y, pal["primary"])
    # Head with empty smile
    draw_shaded_ellipse(c, 11, 7 + offset_y, 5, 5, pal["secondary"])
    draw_shaded_rect(c, 9, 7 + offset_y, 13, 9 + offset_y, pal["accent"])
    # Glowing flux halo hovering above head
    draw_shaded_rect(c, 6, 1 + offset_y, 16, 3 + offset_y, pal["glow"])
    c.set_px(11, 2 + offset_y, (100, 255, 100, 255))
    apply_dark_outline(c)
    return c


def _draw_boese_omega_frame(
    offset_y: int = 0, leg_stride: int = 0, arm_aim: int = 0
) -> PixelCanvas:
    c = PixelCanvas(24, 24)
    pal = ENTITY_PALETTES["evil_omega"]
    # Half-robot cyborg body
    draw_shaded_rect(c, 6, 9 + offset_y, 18, 20 + offset_y, pal["primary"])
    # Head: hair on left, cables/metal on right
    draw_shaded_ellipse(c, 12, 5 + offset_y, 4, 4, pal["secondary"])
    draw_shaded_rect(c, 13, 3 + offset_y, 17, 7 + offset_y, pal["accent"])
    # Red danger sensor eye
    c.set_px(14, 5 + offset_y, (255, 30, 30, 255))
    # Arm cannon extending to right
    draw_shaded_rect(c, 18, 10 + offset_y + arm_aim, 23, 14 + offset_y + arm_aim, pal["glow"])
    c.set_px(22, 12 + offset_y + arm_aim, (255, 255, 100, 255))
    # Legs (metal struts)
    if leg_stride != 0:
        lx1 = 12 - leg_stride
        lx2 = 12 + leg_stride
        draw_shaded_rect(
            c, max(1, lx1 - 1), 20 + offset_y, min(22, lx1 + 2), 23 + offset_y, pal["secondary"]
        )
        draw_shaded_rect(
            c, max(1, lx2 - 1), 20 + offset_y, min(22, lx2 + 2), 23 + offset_y, pal["secondary"]
        )
    else:
        draw_shaded_rect(c, 9, 20 + offset_y, 15, 23 + offset_y, pal["secondary"])
    apply_dark_outline(c)
    return c


def _draw_ober_cloita_frame(offset_y: int = 0, swirl: int = 0) -> PixelCanvas:
    c = PixelCanvas(32, 32)
    pal = ENTITY_PALETTES["ober_cloita"]
    # Massive multi-cloita tower / flux fusion body
    draw_shaded_rect(c, 6, 12 + offset_y, 26, 29 + offset_y, pal["primary"])
    # Main crowned head
    draw_shaded_ellipse(c, 16, 8 + offset_y, 6, 6, pal["secondary"])
    # High composite crown of kaiserin + halo of gute
    draw_shaded_rect(c, 10, 2 + offset_y, 22, 4 + offset_y, pal["glow"])
    draw_shaded_rect(c, 13, 4 + offset_y, 19, 7 + offset_y, pal["accent"])
    c.set_px(16, 1 + offset_y, (255, 215, 0, 255))
    # Swirling extra arms / weapon appendages
    draw_shaded_rect(
        c, max(1, 2 + swirl), 14 + offset_y, min(30, 8 + swirl), 20 + offset_y, pal["accent"]
    )
    draw_shaded_rect(
        c, max(1, 24 - swirl), 14 + offset_y, min(30, 30 - swirl), 20 + offset_y, pal["secondary"]
    )
    apply_dark_outline(c)
    return c


def build_evil_and_hq_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/boese_* and ober_cloita sheets (Card B04)."""
    paths: list[Path] = []

    # 1. boese_kaiserin
    k_idle = [_draw_boese_kaiserin_frame(y) for y in (0, 1, 0, -1)]
    k_walk = [
        _draw_boese_kaiserin_frame(0, 0),
        _draw_boese_kaiserin_frame(-1, 3),
        _draw_boese_kaiserin_frame(0, 0),
        _draw_boese_kaiserin_frame(1, -3),
    ]
    k_anims = {
        "idle": k_idle,
        "walk": k_walk,
        "windup": [_draw_boese_kaiserin_frame(-1), _draw_boese_kaiserin_frame(0)],
        "attack": [_draw_boese_kaiserin_frame(1), _draw_boese_kaiserin_frame(0)],
        "hurt": [_draw_boese_kaiserin_frame(1), _draw_boese_kaiserin_frame(0)],
        "dead": [_draw_boese_kaiserin_frame(3)],
    }
    glow_k = [{"offset": [11, 2], "color": [255, 215, 0], "radius": 12}]
    p, j = save_sheet(
        "charaktere",
        "boese_kaiserin",
        k_anims,
        anchor=(11, 25),
        fps={"idle": 5.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow_k,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    # 2. boese_gute
    g_idle = [_draw_boese_gute_frame(y, 0) for y in (0, 1, 0, -1)]
    g_walk = [
        _draw_boese_gute_frame(0, 0),
        _draw_boese_gute_frame(-1, 3),
        _draw_boese_gute_frame(0, 0),
        _draw_boese_gute_frame(1, -2),
    ]
    g_anims = {
        "idle": g_idle,
        "walk": g_walk,
        "windup": [_draw_boese_gute_frame(-1, 1), _draw_boese_gute_frame(0, 1)],
        "attack": [_draw_boese_gute_frame(1, 2), _draw_boese_gute_frame(0, 0)],
        "hurt": [_draw_boese_gute_frame(1, 0), _draw_boese_gute_frame(0, 0)],
        "dead": [_draw_boese_gute_frame(3, 0)],
    }
    glow_g = [{"offset": [11, 2], "color": [100, 255, 100], "radius": 14}]
    p, j = save_sheet(
        "charaktere",
        "boese_gute",
        g_anims,
        anchor=(11, 23),
        fps={"idle": 5.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow_g,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    # 3. boese_omega
    o_idle = [_draw_boese_omega_frame(y, 0, 0) for y in (0, 1, 0, -1)]
    o_walk = [
        _draw_boese_omega_frame(0, 0, 0),
        _draw_boese_omega_frame(-1, 3, 2),
        _draw_boese_omega_frame(0, 0, 0),
        _draw_boese_omega_frame(1, -3, -1),
    ]
    o_anims = {
        "idle": o_idle,
        "walk": o_walk,
        "windup": [_draw_boese_omega_frame(-1, 0, 1), _draw_boese_omega_frame(0, 0, 2)],
        "attack": [_draw_boese_omega_frame(1, 0, 3), _draw_boese_omega_frame(0, 0, 0)],
        "hurt": [_draw_boese_omega_frame(1, 0, 0), _draw_boese_omega_frame(0, 0, 0)],
        "dead": [_draw_boese_omega_frame(3, 0, 0)],
    }
    glow_o = [{"offset": [22, 12], "color": [255, 50, 50], "radius": 12}]
    p, j = save_sheet(
        "charaktere",
        "boese_omega",
        o_anims,
        anchor=(12, 22),
        fps={"idle": 5.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow_o,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    # 4. ober_cloita
    oc_idle = [_draw_ober_cloita_frame(y, 0) for y in (0, 1, 0, -1)]
    oc_walk = [
        _draw_ober_cloita_frame(0, 0),
        _draw_ober_cloita_frame(-1, 3),
        _draw_ober_cloita_frame(0, 0),
        _draw_ober_cloita_frame(1, -2),
    ]
    oc_anims = {
        "idle": oc_idle,
        "walk": oc_walk,
        "windup": [_draw_ober_cloita_frame(-1, 1), _draw_ober_cloita_frame(0, 2)],
        "attack": [_draw_ober_cloita_frame(1, 3), _draw_ober_cloita_frame(0, 0)],
        "hurt": [_draw_ober_cloita_frame(1, 0), _draw_ober_cloita_frame(0, 0)],
        "dead": [_draw_ober_cloita_frame(3, 0)],
    }
    glow_oc = [{"offset": [16, 3], "color": [220, 220, 255], "radius": 16}]
    p, j = save_sheet(
        "charaktere",
        "ober_cloita",
        oc_anims,
        anchor=(16, 28),
        fps={"idle": 5.0, "walk": 7.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow_oc,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    return paths


def build_trader_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/npc_*.{png,json} (Card B05)."""
    from tools.palette import UNIVERSE_PALETTES

    paths: list[Path] = []

    # Map trader to respective universe palette
    trader_map = [
        ("npc_magenhaendler", "fleischwelt"),
        ("npc_sachbearbeiterin", "aktenhalde"),
        ("npc_glibberhaendler", "glibbria"),
        ("npc_ameisenhehler", "kruemelreich"),
        ("npc_dj", "sporenklub"),
        ("npc_kuester", "abtei"),
    ]

    for trader_name, u_key in trader_map:
        pal = UNIVERSE_PALETTES[u_key]

        def _draw_trader_frame(offset_y: int = 0, item_active: bool = False, p=pal) -> PixelCanvas:
            c = PixelCanvas(20, 24)
            # Body / robe / stall keeper
            draw_shaded_rect(c, 4, 10 + offset_y, 16, 21, p["primary"])
            # Head / hood / hat
            draw_shaded_ellipse(c, 10, 6 + offset_y, 5, 5, p["secondary"])
            # Face / eyes / feature
            draw_shaded_rect(c, 8, 6 + offset_y, 12, 8 + offset_y, p["accent"])
            # Wares / hands holding item
            draw_shaded_rect(c, 6, 13 + offset_y, 14, 16 + offset_y, p["glow"])
            if item_active:
                c.set_px(10, 14 + offset_y, (255, 255, 255, 255))
            else:
                c.set_px(10, 14 + offset_y, p["secondary"].mid)
            apply_dark_outline(c)
            return c

        idle_frames = [_draw_trader_frame(y) for y in (0, 1, 0, -1)]
        talk_frames = [_draw_trader_frame(y, True) for y in (0, -1, 0, 1)]
        offer_frames = [_draw_trader_frame(0, True), _draw_trader_frame(-1, True)]

        anims = {
            "idle": idle_frames,
            "talk": talk_frames,
            "offer": offer_frames,
        }
        glow = [{"offset": [10, 14], "color": list(pal["glow"].highlight[:3]), "radius": 10}]
        p_path, j_path = save_sheet(
            "charaktere",
            trader_name,
            anims,
            anchor=(10, 22),
            fps={"idle": 4.0, "talk": 8.0, "offer": 6.0},
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p_path, j_path])

    return paths
