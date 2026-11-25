"""Procedural shaded sprite sheets for the 6 expansion universes (Phase J)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from src.universes.catalog_expansion import EXPANSION_UNIVERSES
from tools.palette import PaletteRamp, make_ramp
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_segment_line,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

DARK_INK = (24, 20, 32, 255)
WHITE_PX = (248, 248, 255, 255)

UNIVERSE_RAMPS: dict[str, tuple[PaletteRamp, PaletteRamp, PaletteRamp]] = {
    "schrott": (make_ramp((145, 92, 62)), make_ramp((122, 134, 152)), make_ramp((255, 138, 46))),
    "kuchen": (make_ramp((232, 184, 114)), make_ramp((238, 128, 178)), make_ramp((188, 96, 36))),
    "spule": (make_ramp((198, 116, 62)), make_ramp((86, 224, 248)), make_ramp((78, 92, 118))),
    "uhrwerkwueste": (make_ramp((212, 174, 58)), make_ramp((176, 214, 232)), make_ramp((132, 92, 48))),
    "suppenmeer": (make_ramp((224, 186, 78)), make_ramp((236, 124, 52)), make_ramp((92, 178, 94))),
    "freizeitpark": (make_ramp((232, 74, 136)), make_ramp((92, 206, 244)), make_ramp((242, 204, 68))),
}


def _draw_expansion_actor(
    variant: int,
    ramps: tuple[PaletteRamp, PaletteRamp, PaletteRamp],
    size: int,
    stride: int,
    y_bob: int,
) -> PixelCanvas:
    primary, accent, detail = ramps
    c = PixelCanvas(size, size)
    cx = size // 2
    cy = size // 2 + y_bob
    rx = max(4, size // 3 - (variant % 2))
    ry = max(4, size // 3 - ((variant + 1) % 2))
    draw_shaded_ellipse(c, cx, cy, rx, ry, primary)
    draw_shaded_ellipse(c, cx - (1 if variant % 2 == 0 else 0), cy - 2, max(2, rx // 2), max(2, ry // 2), accent)
    draw_shaded_rect(c, cx - rx // 2, cy - ry - 2, cx + rx // 2, cy - ry + 1, detail)
    # Articulated appendages moving outward on stride frames
    arm_reach = 3 + abs(stride)
    draw_segment_line(c, cx - rx + 1, cy, max(2, cx - rx - arm_reach), cy + stride, detail.light, 2)
    draw_segment_line(c, cx + rx - 1, cy, min(size - 3, cx + rx + arm_reach), cy - stride, detail.light, 2)
    draw_segment_line(c, cx - 3, cy + ry - 1, max(2, cx - 4 - stride), min(size - 2, cy + ry + 3), detail.mid, 2)
    draw_segment_line(c, cx + 3, cy + ry - 1, min(size - 3, cx + 4 + stride), min(size - 2, cy + ry + 3), detail.mid, 2)
    c.set_px(cx - 2, cy - 2, WHITE_PX)
    c.set_px(cx + 2, cy - 2, WHITE_PX)
    c.set_px(cx - 2, cy - 1, DARK_INK)
    c.set_px(cx + 2, cy - 1, DARK_INK)
    apply_dark_outline(c)
    return c


def build_expansion_creature_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build shaded sprites for all 24 expansion creatures, 6 mid-bosses & 6 bosses (Phase J)."""
    paths: list[Path] = []
    for u in EXPANSION_UNIVERSES:
        ramps = UNIVERSE_RAMPS[u.key]
        for idx, species in enumerate(u.natives):
            idle = [_draw_expansion_actor(idx, ramps, 20, 0, y) for y in (0, 1, 0, -1)]
            walk = [_draw_expansion_actor(idx, ramps, 20, s, y) for s, y in ((0, 0), (3, -1), (0, 0), (-3, 1))]
            p, j = save_sheet(
                "kreaturen_erweiterung",
                species,
                {"idle": idle, "walk": walk},
                anchor=(10, 18),
                fps={"idle": 4.0, "walk": 6.0},
                out_dir=out_dir,
            )
            paths.extend([p, j])

        for boss_idx, (boss_key, size) in enumerate(((u.mid_boss, 32), (u.boss, 44))):
            idle = [_draw_expansion_actor(boss_idx + 4, ramps, size, 0, y) for y in (0, 1, 0, -1)]
            walk = [_draw_expansion_actor(boss_idx + 4, ramps, size, s, y) for s, y in ((0, 0), (3, -1), (0, 0), (-3, 1))]
            p, j = save_sheet(
                "bosse_erweiterung",
                boss_key,
                {"idle": idle, "walk": walk},
                anchor=(size // 2, size - 4),
                fps={"idle": 4.0, "walk": 6.0},
                out_dir=out_dir,
            )
            paths.extend([p, j])

    return paths
