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


def _draw_mid_boss_frame(
    boss_key: str,
    u_key: str,
    offset_y: int = 0,
    action: bool = False,
) -> PixelCanvas:
    pal = UNIVERSE_PALETTES.get(u_key, ENTITY_PALETTES.get("authority", UNIVERSE_PALETTES["fleischwelt"]))
    w, h = 32, 32

    c = PixelCanvas(w, h)
    
    # Large boss body
    draw_shaded_rect(c, 5, 8 + offset_y, 27, 26 + offset_y, pal["primary"])
    # Head / core ellipse
    draw_shaded_ellipse(c, 16, 12 + offset_y, 8, 7, pal["secondary"])
    # Crest / prominent horns or markings
    draw_shaded_rect(c, 10, 6 + offset_y, 22, 10 + offset_y, pal["accent"])
    
    # Action / glow features
    if action:
        draw_shaded_rect(c, 12, 18 + offset_y, 20, 24 + offset_y, pal["glow"])
        c.set_px(16, 21 + offset_y, (255, 255, 255, 255))
    else:
        c.set_px(16, 12 + offset_y, pal["glow"].highlight)

    apply_dark_outline(c)
    return c


def build_mid_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<mid_boss>.{png,json} for all 9 mid-bosses + warden (Cards B15, B16)."""
    # Boss to universe mapping for all 6 MVP universes + warden
    boss_map = [
        ("pfuetzenwurm", "fleischwelt"),
        ("aktenwolf", "aktenhalde"),
        ("manege_clown", "glibbria"),
        ("harzgeneral", "kruemelreich"),
        ("sporenherz", "sporenklub"),
        ("glockenwaechter", "abtei"),
        ("warden", "aktenhalde"),
    ]

    paths: list[Path] = []
    for boss_key, u_key in boss_map:
        pal = UNIVERSE_PALETTES.get(u_key, ENTITY_PALETTES["authority"])
        idle = [_draw_mid_boss_frame(boss_key, u_key, y) for y in (0, 1, 0, -1)]
        walk = [_draw_mid_boss_frame(boss_key, u_key, y) for y in (0, -1, 0, 1)]
        windup = [_draw_mid_boss_frame(boss_key, u_key, -1, True), _draw_mid_boss_frame(boss_key, u_key, 0, True)]
        attack = [_draw_mid_boss_frame(boss_key, u_key, 1, True), _draw_mid_boss_frame(boss_key, u_key, 0, False)]
        hurt = [_draw_mid_boss_frame(boss_key, u_key, 1), _draw_mid_boss_frame(boss_key, u_key, 0)]

        anims = {
            "idle": idle,
            "walk": walk,
            "windup": windup,
            "attack": attack,
            "hurt": hurt,
        }
        glow = [{"offset": [16, 16], "color": list(pal["glow"].highlight[:3]), "radius": 16}]
        p, j = save_sheet(
            "bosse",
            boss_key,
            anims,
            anchor=(16, 28),
            fps={"idle": 4.0, "walk": 6.0, "windup": 6.0, "attack": 8.0, "hurt": 8.0},
            glow=glow,
            out_dir=out_dir,
        )
        paths.extend([p, j])

    return paths


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    raise NotImplementedError("Cards B17..B19")


def build_end_boss_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build bosse/<end_boss>.{png,json} and part sheets for all 9 end-bosses (Cards B17..B19)."""
    raise NotImplementedError("Cards B17..B19")

