"""Procedural sprite sheets for Phase 3 satire universes, Cloita-Null, and absurd natives."""

from __future__ import annotations

import os
from pathlib import Path

import pygame

from src.sprite_render import ASSET_ROOT
from src.universes.catalog_phase3 import PHASE3_UNIVERSES
from tools.palette import PaletteRamp, make_ramp
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

DARK_INK = (24, 20, 32, 255)
WHITE_PX = (248, 248, 255, 255)

PHASE3_RAMPS: dict[str, tuple[PaletteRamp, PaletteRamp, PaletteRamp]] = {
    "anatomie_park": (make_ramp((186, 76, 86)), make_ramp((152, 224, 78)), make_ramp((236, 222, 198))),
    "pastell_hoelle": (make_ramp((246, 174, 212)), make_ramp((192, 232, 255)), make_ramp((252, 236, 134))),
    "klonenberg_welt": (make_ramp((212, 152, 134)), make_ramp((124, 156, 196)), make_ramp((108, 90, 76))),
    "talent_kosmos": (make_ramp((92, 82, 128)), make_ramp((252, 222, 92)), make_ramp((224, 112, 196))),
    "antrags_labyrinth": (make_ramp((186, 180, 162)), make_ramp((164, 88, 184)), make_ramp((112, 118, 128))),
    "krawatten_planet": (make_ramp((132, 140, 152)), make_ramp((146, 52, 86)), make_ramp((82, 54, 34))),
    "klo_paradies": (make_ramp((234, 242, 248)), make_ramp((116, 218, 242)), make_ramp((236, 208, 104))),
    "matroschka_simulation": (make_ramp((78, 144, 176)), make_ramp((108, 232, 196)), make_ramp((214, 246, 232))),
    "kollektiv_buerokratie": (make_ramp((164, 138, 76)), make_ramp((214, 228, 124)), make_ramp((64, 58, 138))),
    "unsterblichkeits_resort": (make_ramp((224, 234, 242)), make_ramp((255, 142, 96)), make_ramp((112, 212, 226))),
    "schroedinger_kammer": (make_ramp((176, 138, 96)), make_ramp((156, 118, 246)), make_ramp((236, 226, 255))),
    "kater_bunker": (make_ramp((84, 88, 98)), make_ramp((224, 192, 68)), make_ramp((144, 148, 138))),
}


def _draw_phase3_actor(
    variant: int,
    ramps: tuple[PaletteRamp, PaletteRamp, PaletteRamp],
    size: int,
    y_bob: int,
) -> PixelCanvas:
    primary, accent, detail = ramps
    c = PixelCanvas(size, size)
    cx = size // 2
    cy = size // 2 + y_bob
    rx = max(4, size // 3 - (variant % 2))
    ry = max(4, size // 3 - ((variant + 1) % 2))
    draw_shaded_ellipse(c, cx, cy, rx, ry, primary)
    draw_shaded_rect(c, cx - rx // 2, cy - ry + 2, max(4, rx), 3, accent)
    c.set_px(cx - 2, cy - 1, WHITE_PX)
    c.set_px(cx + 2, cy - 1, WHITE_PX)
    c.set_px(cx - 2, cy, DARK_INK)
    c.set_px(cx + 2, cy, DARK_INK)
    c.set_px(cx, cy + ry // 2, detail.highlight)
    apply_dark_outline(c)
    return c


def build_phase3_sprites(root: Path = ASSET_ROOT) -> list[Path]:
    """Generate native, mid-boss, and boss sprite sheets for all 12 Phase 3 universes."""
    if not pygame.get_init():
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()

    out_paths: list[Path] = []
    for universe in PHASE3_UNIVERSES:
        ramps = PHASE3_RAMPS[universe.key]
        for idx, actor_key in enumerate(universe.natives):
            frames = [_draw_phase3_actor(idx, ramps, 20, bob) for bob in (0, 1)]
            out_paths.extend(
                save_sheet("actors", actor_key, {"idle": frames}, anchor=(10, 19), out_dir=root)
            )
        for idx, boss_key in enumerate((universe.mid_boss, universe.boss)):
            if not boss_key:
                continue
            frames = [_draw_phase3_actor(idx + 2, ramps, 32, bob) for bob in (0, 1)]
            out_paths.extend(
                save_sheet("actors", boss_key, {"idle": frames}, anchor=(16, 31), out_dir=root)
            )
    return out_paths
