"""Procedural sprite generator for Patentamt NPCs, props, and desk surfaces."""

from __future__ import annotations

import os
from pathlib import Path

import pygame

from src.sprite_render import ASSET_ROOT
from tools.palette import make_ramp
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

DARK_INK = (24, 20, 32, 255)


def build_patentamt_sprites(root: Path = ASSET_ROOT) -> list[Path]:
    """Generate desk/incubator props and alternate Cloita office sprites."""
    if not pygame.get_init():
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()

    out_paths: list[Path] = []
    beige_ramp = make_ramp((214, 198, 162))
    coat_ramp = make_ramp((188, 208, 224))
    teal_ramp = make_ramp((94, 186, 178))

    # 2-frame idle sheet for alternate Cloita office worker.
    frames: list[PixelCanvas] = []
    for bob in (0, 1):
        c = PixelCanvas(20, 24)
        draw_shaded_rect(c, 5, 8 + bob, 10, 11, coat_ramp)
        draw_shaded_ellipse(c, 10, 6 + bob, 4, 4, beige_ramp)
        draw_shaded_rect(c, 12, 11 + bob, 4, 3, teal_ramp)
        c.set_px(9, 6 + bob, DARK_INK)
        c.set_px(11, 6 + bob, DARK_INK)
        apply_dark_outline(c)
        frames.append(c)

    out_paths.extend(save_sheet("actors", "cloita_amt", {"idle": frames}, anchor=(10, 23), out_dir=root))

    # Prop: office filing cabinet & clone incubator.
    prop_frames: list[PixelCanvas] = []
    for i in range(2):
        c = PixelCanvas(16, 20)
        draw_shaded_rect(c, 2, 2, 12, 16, teal_ramp if i else beige_ramp)
        draw_shaded_rect(c, 4, 5, 8, 3, coat_ramp)
        draw_shaded_rect(c, 4, 10, 8, 3, coat_ramp)
        apply_dark_outline(c)
        prop_frames.append(c)

    out_paths.extend(
        save_sheet("props", "patentamt_props", {"idle": prop_frames}, anchor=(8, 19), out_dir=root)
    )
    return out_paths
