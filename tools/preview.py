"""Generate 4x magnified sprite-sheet previews for visual inspection."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.sprite_render import ASSET_ROOT
from src.sprites import load_sheet_meta

BG_COLOR = (54, 58, 66)
TEXT_COLOR = (232, 236, 244)
SUB_COLOR = (168, 174, 186)


def _row_frames(sheet: pygame.Surface, fw: int, fh: int, row: int, count: int) -> list[pygame.Surface]:
    return [sheet.subsurface((i * fw, row * fh, fw, fh)) for i in range(count)]


def build_preview(category: str, out_path: Path, scale: int = 4) -> Path:
    """Render all sprite sheets in assets/sprites/<category> into a magnified overview PNG."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()

    folder = ASSET_ROOT / category
    json_files = sorted(folder.glob("*.json"))
    font = pygame.font.SysFont("consolas,dejavusansmono,arial", 13)
    sub_font = pygame.font.SysFont("consolas,dejavusansmono,arial", 11)

    rows: list[tuple[str, str, list[pygame.Surface]]] = []
    label_w = 180
    pad_x = 12
    pad_y = 8
    gap = 6
    max_row_w = 0
    total_h = pad_y

    for jpath in json_files:
        ppath = jpath.with_suffix(".png")
        if not ppath.is_file():
            continue
        meta = load_sheet_meta(jpath)
        sheet = pygame.image.load(str(ppath))
        fw, fh = meta.frame_size
        idle_spec = meta.anims.get("idle") or next(iter(meta.anims.values()))
        motion_key = next((k for k in ("walk", "fly", "talk") if k in meta.anims), "idle")
        motion_spec = meta.anims[motion_key]

        frames = _row_frames(sheet, fw, fh, idle_spec.row, 1)
        frames.extend(_row_frames(sheet, fw, fh, motion_spec.row, motion_spec.frames))
        scaled = [pygame.transform.scale(f, (fw * scale, fh * scale)) for f in frames]
        row_w = label_w + len(scaled) * (fw * scale + gap) + pad_x
        max_row_w = max(max_row_w, row_w)
        total_h += max(36, fh * scale) + pad_y
        rows.append((jpath.stem, f"idle | {motion_key}", scaled))

    surf = pygame.Surface((max(400, max_row_w), max(100, total_h)))
    surf.fill(BG_COLOR)
    y = pad_y
    for name, subtitle, scaled in rows:
        surf.blit(font.render(name, True, TEXT_COLOR), (pad_x, y + 2))
        surf.blit(sub_font.render(subtitle, True, SUB_COLOR), (pad_x, y + 18))
        x = label_w
        row_h = max(36, scaled[0].get_height())
        for idx, frame in enumerate(scaled):
            surf.blit(frame, (x, y + (row_h - frame.get_height()) // 2))
            x += frame.get_width() + gap + (6 if idx == 0 else 0)
        y += row_h + pad_y

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(out_path))
    return out_path


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        build_preview(sys.argv[1], Path(sys.argv[2]))
    else:
        for cat, out in (
            ("charaktere", Path("tasks/kartenlauf/vorschau-charaktere.png")),
            ("kreaturen", Path("tasks/kartenlauf/vorschau-kreaturen.png")),
            ("bosse", Path("tasks/kartenlauf/vorschau-bosse.png")),
        ):
            build_preview(cat, out)
