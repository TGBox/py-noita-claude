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


def _draw_klonita_frame(offset_y: int = 0, lantern_wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(18, 22)
    pal = ENTITY_PALETTES["klonita"]
    # Floating hem robe
    draw_shaded_rect(c, 3, 9 + offset_y, 14, 19 + offset_y, pal["primary"])
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
    idle_frames = [_draw_klonita_frame(y, w) for y, w in ((0, 0), (-1, 1), (0, 0), (1, -1))]
    fly_frames = [_draw_klonita_frame(y, 0) for y in (-1, -2, -1, 0)]
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


def _draw_agent_sachbearbeiter_frame(offset_y: int = 0, arm_action: bool = False) -> PixelCanvas:
    c = PixelCanvas(20, 24)
    pal = ENTITY_PALETTES["authority"]
    # Grey suit body
    draw_shaded_rect(c, 4, 10 + offset_y, 16, 21, pal["primary"])
    # Head with fedora/visor
    draw_shaded_ellipse(c, 10, 6 + offset_y, 5, 5, pal["secondary"])
    # Red tie or badge accent
    draw_shaded_rect(c, 9, 11 + offset_y, 11, 15 + offset_y, pal["accent"])
    c.set_px(10, 11 + offset_y, (220, 50, 50, 255))
    if arm_action:
        draw_shaded_rect(c, 14, 11 + offset_y, 18, 14 + offset_y, pal["secondary"])
        c.set_px(17, 12 + offset_y, pal["glow"].highlight)
    else:
        c.set_px(15, 13 + offset_y, pal["secondary"].mid)
    apply_dark_outline(c)
    return c


def _draw_agent_vollstrecker_frame(offset_y: int = 0, shield_pos: int = 0) -> PixelCanvas:
    c = PixelCanvas(22, 26)
    pal = ENTITY_PALETTES["authority"]
    # Heavy trenchcoat body
    draw_shaded_rect(c, 4, 10 + offset_y, 18, 23, pal["primary"])
    # Armored helmet/head
    draw_shaded_ellipse(c, 11, 6 + offset_y, 6, 5, pal["secondary"])
    # Visor slit glow
    draw_shaded_rect(c, 8, 6 + offset_y, 14, 8 + offset_y, pal["glow"])
    # Briefcase shield on arm
    bx = 13 + shield_pos
    draw_shaded_rect(c, bx, 11 + offset_y, bx + 5, 18 + offset_y, pal["accent"])
    c.set_px(bx + 2, 11 + offset_y, pal["secondary"].shadow)
    apply_dark_outline(c)
    return c


def _draw_agent_abteilungsleiter_frame(offset_y: int = 0, float_wave: int = 0) -> PixelCanvas:
    c = PixelCanvas(24, 28)
    pal = ENTITY_PALETTES["authority"]
    # Floating robe / formal authority mantle
    draw_shaded_rect(c, 5, 12 + offset_y, 19, 25 + offset_y, pal["primary"])
    # Head / mask
    draw_shaded_ellipse(c, 12, 8 + offset_y, 5, 5, pal["secondary"])
    # Crown / golden § symbol on head
    draw_shaded_rect(c, 9 + float_wave, 2 + offset_y, 15 + float_wave, 5 + offset_y, pal["glow"])
    c.set_px(12 + float_wave, 3 + offset_y, (255, 215, 0, 255))
    # Glowing legal scroll or aura hands
    draw_shaded_rect(c, 2, 14 + offset_y, 6, 18 + offset_y, pal["accent"])
    draw_shaded_rect(c, 18, 14 + offset_y, 22, 18 + offset_y, pal["accent"])
    apply_dark_outline(c)
    return c


def build_agent_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/agent_*.{png,json} (Card B03)."""
    paths: list[Path] = []

    # 1. agent_sachbearbeiter (also aliased/copied for agent_streife if needed)
    sb_idle = [_draw_agent_sachbearbeiter_frame(y) for y in (0, 1, 0, -1)]
    sb_walk = [_draw_agent_sachbearbeiter_frame(y) for y in (0, -1, 0, 1, 0, -1)]
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

    # 2. agent_vollstrecker
    vs_idle = [_draw_agent_vollstrecker_frame(y, 0) for y in (0, 1, 0, -1)]
    vs_walk = [_draw_agent_vollstrecker_frame(y, 0) for y in (0, -1, 0, 1)]
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
        anchor=(11, 24),
        fps={"idle": 5.0, "walk": 7.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        out_dir=out_dir,
    )
    paths.extend([p, j])

    # 3. agent_abteilungsleiter
    al_idle = [
        _draw_agent_abteilungsleiter_frame(y, w) for y, w in ((0, 0), (-1, 1), (0, 0), (1, -1))
    ]
    al_fly = [_draw_agent_abteilungsleiter_frame(y, 0) for y in (-1, -2, -1, 0)]
    al_windup = [
        _draw_agent_abteilungsleiter_frame(-1, 0),
        _draw_agent_abteilungsleiter_frame(-2, 1),
    ]
    al_attack = [_draw_agent_abteilungsleiter_frame(0, 1), _draw_agent_abteilungsleiter_frame(1, 0)]
    al_hurt = [_draw_agent_abteilungsleiter_frame(1, 0), _draw_agent_abteilungsleiter_frame(0, 0)]
    al_dead = [_draw_agent_abteilungsleiter_frame(2, 0)]
    al_anims = {
        "idle": al_idle,
        "fly": al_fly,
        "windup": al_windup,
        "attack": al_attack,
        "hurt": al_hurt,
        "dead": al_dead,
    }
    glow = [{"offset": [12, 3], "color": [255, 215, 0], "radius": 14}]
    p, j = save_sheet(
        "charaktere",
        "agent_abteilungsleiter",
        al_anims,
        anchor=(12, 26),
        fps={"idle": 5.0, "fly": 7.0, "windup": 6.0, "attack": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow,
        out_dir=out_dir,
    )
    paths.extend([p, j])

    return paths


def build_evil_and_hq_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build charaktere/boese_* and ober_cloita sheets (Card B04)."""
    paths: list[Path] = []

    # 1. Evil selves: boese_kaiserin, boese_gute, boese_omega
    # Use palette keys evil_kaiserin, evil_gute, evil_omega with player frame shape but darker/distorted
    evil_configs = [
        ("boese_kaiserin", "evil_kaiserin", (220, 50, 50)),
        ("boese_gute", "evil_gute", (50, 220, 50)),
        ("boese_omega", "evil_omega", (220, 220, 50)),
    ]

    for sheet_name, pal_key, glow_col in evil_configs:
        idle_frames = [_draw_char_frame(pal_key, y) for y in (0, 1, 0, -1)]
        walk_frames = [_draw_char_frame(pal_key, y) for y in (0, -1, 0, 1, 0, -1)]
        jump_frames = [_draw_char_frame(pal_key, -2), _draw_char_frame(pal_key, -1)]
        fall_frames = [_draw_char_frame(pal_key, 1), _draw_char_frame(pal_key, 2)]
        cast_frames = [
            _draw_char_frame(pal_key, cast_arm=True),
            _draw_char_frame(pal_key, -1, cast_arm=True),
            _draw_char_frame(pal_key, cast_arm=True),
        ]
        hurt_frames = [_draw_char_frame(pal_key, 1), _draw_char_frame(pal_key, 0)]
        dead_frames = [_draw_char_frame(pal_key, 3)]

        anims = {
            "idle": idle_frames,
            "walk": walk_frames,
            "jump": jump_frames,
            "fall": fall_frames,
            "cast": cast_frames,
            "hurt": hurt_frames,
            "dead": dead_frames,
        }
        glow = [{"offset": [14, 12], "color": list(glow_col), "radius": 12}]
        p, j = save_sheet(
            "charaktere",
            sheet_name,
            anims,
            anchor=(10, 22),
            fps={
                "idle": 6.0,
                "walk": 8.0,
                "jump": 6.0,
                "fall": 6.0,
                "cast": 10.0,
                "hurt": 8.0,
                "dead": 1.0,
            },
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p, j])

    # 2. ober_cloita: Evil/bureaucratic Klonita variant
    pal_hq = ENTITY_PALETTES["ober_cloita"]

    def _draw_cloita_frame(offset_y: int = 0, staff_rot: int = 0) -> PixelCanvas:
        c = PixelCanvas(20, 24)
        # Bureaucratic dark robe
        draw_shaded_rect(c, 4, 10 + offset_y, 16, 21, pal_hq["primary"])
        # Head / veil
        draw_shaded_ellipse(c, 10, 6 + offset_y, 5, 5, pal_hq["secondary"])
        # High crown/tiara
        draw_shaded_rect(c, 7, 2 + offset_y, 13, 5 + offset_y, pal_hq["glow"])
        c.set_px(10, 3 + offset_y, (255, 215, 0, 255))
        # Floating command sigil / quill staff
        draw_shaded_rect(
            c, 14 + staff_rot, 8 + offset_y, 17 + staff_rot, 19 + offset_y, pal_hq["accent"]
        )
        apply_dark_outline(c)
        return c

    cloita_idle = [_draw_cloita_frame(y, w) for y, w in ((0, 0), (-1, 1), (0, 0), (1, -1))]
    cloita_fly = [_draw_cloita_frame(y, 0) for y in (-1, -2, -1, 0)]
    cloita_cast = [_draw_cloita_frame(0, 1), _draw_cloita_frame(-1, 2), _draw_cloita_frame(0, 1)]
    cloita_hurt = [_draw_cloita_frame(1, 0), _draw_cloita_frame(0, 0)]
    cloita_dead = [_draw_cloita_frame(3, 0)]

    cloita_anims = {
        "idle": cloita_idle,
        "fly": cloita_fly,
        "cast": cloita_cast,
        "hurt": cloita_hurt,
        "dead": cloita_dead,
    }
    glow = [{"offset": [10, 4], "color": [220, 220, 255], "radius": 14}]
    p, j = save_sheet(
        "charaktere",
        "ober_cloita",
        cloita_anims,
        anchor=(10, 22),
        fps={"idle": 5.0, "fly": 8.0, "cast": 10.0, "hurt": 8.0, "dead": 1.0},
        glow=glow,
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
