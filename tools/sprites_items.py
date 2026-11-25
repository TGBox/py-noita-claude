"""Contract V8: Weapon part, spell icon, sample, and pickup sprite builders (Cards B20..B27)."""

from __future__ import annotations

from pathlib import Path

from src.icons import icon_pixels
from src.samples import SAMPLES
from src.spells import BLOCKS
from src.sprite_render import ASSET_ROOT
from src.weapon_parts import WEAPON_PART_KEYS
from tools.palette import PaletteRamp, make_ramp
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_segment_line,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)

METAL_RAMP = make_ramp((125, 135, 150))
DARK_METAL_RAMP = make_ramp((75, 82, 95))
BRASS_RAMP = make_ramp((195, 155, 55))
WOOD_RAMP = make_ramp((135, 88, 48))
GLASS_RAMP = make_ramp((155, 200, 220))
FLUX_RAMP = make_ramp((80, 235, 220))
RUBBER_RAMP = make_ramp((170, 75, 95))
GOLD_RAMP = make_ramp((235, 185, 50))
PAPER_RAMP = make_ramp((225, 215, 190))
TAPE_RAMP = make_ramp((215, 195, 80))
EYE_WHITE_RAMP = make_ramp((230, 230, 235))
BLUEPRINT_RAMP = make_ramp((55, 115, 205))
LIFE_RAMP = make_ramp((80, 215, 110))
SHARD_RAMP = make_ramp((150, 220, 235))
COCOON_RAMP = make_ramp((155, 95, 115))
PORTAL_RAMP = make_ramp((115, 95, 220))


# ---------------------------------------------------------------------------
# Card B20: Weapon parts (waffen/)
# ---------------------------------------------------------------------------


def _draw_griff_pistole() -> PixelCanvas:
    c = PixelCanvas(6, 8)
    draw_shaded_rect(c, 1, 1, 4, 2, METAL_RAMP)
    draw_shaded_rect(c, 1, 2, 3, 6, WOOD_RAMP)
    c.set_px(4, 3, BRASS_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_griff_kurbel() -> PixelCanvas:
    c = PixelCanvas(7, 8)
    draw_shaded_rect(c, 1, 1, 4, 5, METAL_RAMP)
    draw_segment_line(c, 3, 3, 5, 5, BRASS_RAMP.mid, 1)
    draw_shaded_rect(c, 4, 5, 5, 6, BRASS_RAMP)
    c.set_px(2, 2, METAL_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_griff_handschuh() -> PixelCanvas:
    c = PixelCanvas(8, 8)
    draw_shaded_rect(c, 1, 1, 6, 3, RUBBER_RAMP)
    draw_shaded_rect(c, 2, 3, 5, 6, RUBBER_RAMP)
    c.set_px(1, 2, BRASS_RAMP.light)
    c.set_px(6, 2, BRASS_RAMP.light)
    apply_dark_outline(c)
    return c


def _draw_gehaeuse(width: int) -> PixelCanvas:
    c = PixelCanvas(width, 7)
    draw_shaded_rect(c, 1, 1, width - 2, 5, METAL_RAMP)
    draw_shaded_rect(c, 2, 2, width - 3, 4, DARK_METAL_RAMP)
    for rx in range(3, width - 2, 4):
        c.set_px(rx, 2, BRASS_RAMP.highlight)
        c.set_px(rx, 4, BRASS_RAMP.mid)
    apply_dark_outline(c)
    return c


def _draw_tank(w: int, h: int) -> PixelCanvas:
    c = PixelCanvas(w, h)
    draw_shaded_rect(c, 1, 1, w - 2, h - 2, FLUX_RAMP)
    draw_shaded_rect(c, 1, 1, w - 2, 1, BRASS_RAMP)
    draw_shaded_rect(c, 1, h - 2, w - 2, h - 2, BRASS_RAMP)
    c.set_px(2, 2, GLASS_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_lauf_einfach() -> PixelCanvas:
    c = PixelCanvas(8, 6)
    draw_shaded_rect(c, 1, 2, 6, 3, METAL_RAMP)
    c.set_px(2, 2, METAL_RAMP.highlight)
    c.set_px(6, 2, BRASS_RAMP.light)
    apply_dark_outline(c)
    return c


def _draw_lauf_doppel() -> PixelCanvas:
    c = PixelCanvas(10, 7)
    draw_shaded_rect(c, 1, 1, 8, 2, METAL_RAMP)
    draw_shaded_rect(c, 1, 4, 8, 5, METAL_RAMP)
    draw_shaded_rect(c, 2, 2, 3, 4, BRASS_RAMP)
    apply_dark_outline(c)
    return c


def _draw_lauf_dreifach() -> PixelCanvas:
    c = PixelCanvas(12, 8)
    for y in (1, 3, 5):
        draw_shaded_rect(c, 1, y, 10, y + 1, METAL_RAMP)
    draw_shaded_rect(c, 3, 1, 4, 6, BRASS_RAMP)
    draw_shaded_rect(c, 8, 1, 9, 6, BRASS_RAMP)
    apply_dark_outline(c)
    return c


def _draw_muendung_spitz() -> PixelCanvas:
    c = PixelCanvas(7, 6)
    draw_shaded_rect(c, 1, 1, 3, 4, BRASS_RAMP)
    draw_shaded_rect(c, 3, 2, 5, 3, METAL_RAMP)
    c.set_px(5, 2, FLUX_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_muendung_trichter() -> PixelCanvas:
    c = PixelCanvas(7, 8)
    draw_shaded_rect(c, 1, 2, 3, 5, METAL_RAMP)
    draw_shaded_rect(c, 3, 1, 5, 6, BRASS_RAMP)
    c.set_px(5, 3, DARK_METAL_RAMP.shadow)
    c.set_px(5, 4, DARK_METAL_RAMP.shadow)
    apply_dark_outline(c)
    return c


def _draw_muendung_sieb() -> PixelCanvas:
    c = PixelCanvas(7, 8)
    draw_shaded_rect(c, 1, 1, 5, 6, METAL_RAMP)
    draw_shaded_rect(c, 4, 1, 5, 6, BRASS_RAMP)
    c.set_px(5, 2, DARK_METAL_RAMP.shadow)
    c.set_px(5, 4, DARK_METAL_RAMP.shadow)
    c.set_px(5, 5, DARK_METAL_RAMP.shadow)
    apply_dark_outline(c)
    return c


def _draw_zier_klebeband() -> PixelCanvas:
    c = PixelCanvas(7, 7)
    draw_shaded_rect(c, 1, 2, 5, 4, TAPE_RAMP)
    draw_segment_line(c, 1, 1, 5, 5, TAPE_RAMP.light, 1)
    draw_segment_line(c, 1, 5, 5, 1, TAPE_RAMP.mid, 1)
    apply_dark_outline(c)
    return c


def _draw_zier_antenne() -> PixelCanvas:
    c = PixelCanvas(7, 9)
    draw_shaded_rect(c, 2, 6, 4, 7, METAL_RAMP)
    draw_segment_line(c, 3, 2, 3, 6, METAL_RAMP.light, 1)
    draw_shaded_ellipse(c, 3, 2, 1, 1, FLUX_RAMP)
    apply_dark_outline(c)
    return c


def _draw_zier_wackelauge() -> PixelCanvas:
    c = PixelCanvas(7, 7)
    draw_shaded_ellipse(c, 3, 3, 2, 2, EYE_WHITE_RAMP)
    c.set_px(4, 3, (20, 20, 30, 255))
    c.set_px(3, 2, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_zier_gluehbirne() -> PixelCanvas:
    c = PixelCanvas(7, 9)
    draw_shaded_ellipse(c, 3, 3, 2, 2, GOLD_RAMP)
    draw_shaded_rect(c, 2, 6, 4, 7, METAL_RAMP)
    c.set_px(3, 2, (255, 255, 220, 255))
    apply_dark_outline(c)
    return c


def _draw_zier_schraubenzieher() -> PixelCanvas:
    c = PixelCanvas(9, 6)
    draw_shaded_rect(c, 1, 1, 4, 4, RUBBER_RAMP)
    draw_shaded_rect(c, 5, 2, 7, 3, METAL_RAMP)
    c.set_px(7, 2, METAL_RAMP.highlight)
    apply_dark_outline(c)
    return c


_WEAPON_PART_BUILDERS = {
    "griff_pistole": _draw_griff_pistole,
    "griff_kurbel": _draw_griff_kurbel,
    "griff_handschuh": _draw_griff_handschuh,
    "gehaeuse_kurz": lambda: _draw_gehaeuse(10),
    "gehaeuse_mittel": lambda: _draw_gehaeuse(14),
    "gehaeuse_lang": lambda: _draw_gehaeuse(18),
    "tank_klein": lambda: _draw_tank(6, 7),
    "tank_mittel": lambda: _draw_tank(8, 8),
    "tank_gross": lambda: _draw_tank(10, 9),
    "lauf_einfach": _draw_lauf_einfach,
    "lauf_doppel": _draw_lauf_doppel,
    "lauf_dreifach": _draw_lauf_dreifach,
    "muendung_spitz": _draw_muendung_spitz,
    "muendung_trichter": _draw_muendung_trichter,
    "muendung_sieb": _draw_muendung_sieb,
    "zier_klebeband": _draw_zier_klebeband,
    "zier_antenne": _draw_zier_antenne,
    "zier_wackelauge": _draw_zier_wackelauge,
    "zier_gluehbirne": _draw_zier_gluehbirne,
    "zier_schraubenzieher": _draw_zier_schraubenzieher,
}


def build_weapon_part_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build waffen/<part_key>.{png,json} for all 20 weapon parts (Card B20)."""
    produced: list[Path] = []
    for key in WEAPON_PART_KEYS:
        canvas = _WEAPON_PART_BUILDERS[key]()
        glow: list[dict[str, object]] | None = None
        if key.startswith("tank_"):
            glow = [{"offset": [0, 0], "color": [80, 235, 220], "radius": 10}]
        elif key == "zier_gluehbirne":
            glow = [{"offset": [0, -1], "color": [255, 220, 120], "radius": 10}]
        png, json_path = save_sheet(
            "waffen",
            key,
            {"idle": [canvas]},
            anchor=(canvas.width // 2, canvas.height // 2),
            glow=glow,
            out_dir=out_dir,
        )
        produced.extend([png, json_path])
    return produced


# ---------------------------------------------------------------------------
# Cards B21..B24: Spell icons (zauber/)
# ---------------------------------------------------------------------------


def build_spell_icon_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build zauber/<block_key>.{png,json} for all spell blocks (Cards B21..B24)."""
    produced: list[Path] = []
    for key in list(BLOCKS.keys()):
        rows = icon_pixels(key)
        canvas = PixelCanvas(16, 16)
        set_px = canvas.surface.set_at
        for y, row in enumerate(rows):
            for x, color in enumerate(row):
                if color is not None:
                    set_px((x, y), (color[0], color[1], color[2], 255))
        png, json_path = save_sheet(
            "zauber",
            key,
            {"idle": [canvas]},
            anchor=(8, 8),
            out_dir=out_dir,
        )
        produced.extend([png, json_path])
    return produced


# ---------------------------------------------------------------------------
# Cards B25..B27: Pickups and samples (gegenstaende/)
# ---------------------------------------------------------------------------


def _draw_gold_muenze() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_ellipse(c, 6, 6, 4, 4, GOLD_RAMP)
    c.set_px(5, 4, (255, 250, 190, 255))
    c.set_px(6, 6, BRASS_RAMP.shadow)
    apply_dark_outline(c)
    return c


def _draw_gold_haufen(count: int) -> PixelCanvas:
    c = PixelCanvas(12, 12)
    coords = [(4, 8), (7, 8), (5, 5), (8, 6), (6, 3)][:count]
    for cx, cy in coords:
        draw_shaded_ellipse(c, cx, cy, 2, 2, GOLD_RAMP)
    c.set_px(5, 4, (255, 250, 200, 255))
    apply_dark_outline(c)
    return c


def _draw_waffe_item() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 4, 9, 6, METAL_RAMP)
    draw_shaded_rect(c, 2, 6, 4, 9, WOOD_RAMP)
    draw_shaded_rect(c, 5, 3, 7, 5, FLUX_RAMP)
    c.set_px(10, 5, BRASS_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_modul_item() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 2, 9, 9, DARK_METAL_RAMP)
    draw_shaded_rect(c, 3, 3, 8, 6, FLUX_RAMP)
    c.set_px(4, 8, GOLD_RAMP.light)
    c.set_px(6, 8, GOLD_RAMP.light)
    c.set_px(8, 8, GOLD_RAMP.light)
    apply_dark_outline(c)
    return c


def _draw_experiment_item() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 4, 3, 7, 9, GLASS_RAMP)
    draw_shaded_rect(c, 4, 5, 7, 9, LIFE_RAMP)
    draw_shaded_rect(c, 5, 1, 6, 3, METAL_RAMP)
    c.set_px(5, 10, METAL_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_kolben(full: bool) -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_ellipse(c, 6, 7, 4, 4, GLASS_RAMP)
    draw_shaded_rect(c, 5, 2, 6, 4, GLASS_RAMP)
    draw_shaded_rect(c, 5, 1, 6, 2, WOOD_RAMP)
    if full:
        draw_shaded_ellipse(c, 6, 8, 3, 2, make_ramp((185, 50, 65)))
    c.set_px(4, 6, (240, 250, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_lebenskapsel(frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 3, 2, 8, 9, GLASS_RAMP)
    ramp = LIFE_RAMP if frame % 2 == 0 else make_ramp((110, 240, 140))
    draw_shaded_rect(c, 4, 4, 7, 8, ramp)
    draw_shaded_rect(c, 4, 1, 7, 2, METAL_RAMP)
    draw_shaded_rect(c, 4, 9, 7, 10, METAL_RAMP)
    apply_dark_outline(c)
    return c


def _draw_kokon() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_ellipse(c, 6, 6, 4, 5, COCOON_RAMP)
    draw_segment_line(c, 3, 4, 8, 5, COCOON_RAMP.shadow, 1)
    draw_segment_line(c, 3, 7, 8, 8, COCOON_RAMP.highlight, 1)
    apply_dark_outline(c)
    return c


def _draw_auge() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_ellipse(c, 6, 6, 4, 4, EYE_WHITE_RAMP)
    draw_shaded_ellipse(c, 6, 6, 2, 2, make_ramp((95, 190, 230)))
    c.set_px(6, 6, (20, 15, 30, 255))
    c.set_px(5, 5, (255, 255, 255, 255))
    apply_dark_outline(c)
    return c


def _draw_wuerfel() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 2, 9, 9, PAPER_RAMP)
    for px, py in ((4, 4), (7, 4), (6, 6), (4, 8), (7, 8)):
        c.set_px(px, py, (35, 30, 45, 255))
    apply_dark_outline(c)
    return c


def _draw_erinnerungssplitter(frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(12, 12)
    ramp = SHARD_RAMP if frame % 2 == 0 else FLUX_RAMP
    draw_shaded_ellipse(c, 6, 6, 3, 4, ramp)
    draw_segment_line(c, 4, 3, 8, 8, (245, 255, 255, 255), 1)
    c.set_px(6, 5, (210, 175, 235, 255))
    apply_dark_outline(c)
    return c


def _draw_bauplan_splitter() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 2, 9, 9, BLUEPRINT_RAMP)
    draw_segment_line(c, 3, 4, 8, 4, (235, 245, 255, 255), 1)
    draw_segment_line(c, 4, 6, 7, 8, (235, 245, 255, 255), 1)
    c.set_px(9, 2, (0, 0, 0, 0))
    apply_dark_outline(c)
    return c


def _draw_fundkiste() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 3, 9, 9, WOOD_RAMP)
    draw_shaded_rect(c, 2, 3, 9, 4, BRASS_RAMP)
    c.set_px(5, 6, GOLD_RAMP.highlight)
    c.set_px(6, 6, GOLD_RAMP.highlight)
    apply_dark_outline(c)
    return c


def _draw_dienstausweis() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 3, 9, 8, PAPER_RAMP)
    draw_shaded_rect(c, 3, 4, 5, 6, BLUEPRINT_RAMP)
    c.set_px(7, 5, (200, 45, 50, 255))
    c.set_px(8, 6, (200, 45, 50, 255))
    apply_dark_outline(c)
    return c


def _draw_formular_stempel() -> PixelCanvas:
    c = PixelCanvas(12, 12)
    draw_shaded_rect(c, 2, 2, 9, 9, PAPER_RAMP)
    draw_shaded_ellipse(c, 7, 7, 2, 2, make_ramp((205, 50, 55)))
    draw_segment_line(c, 3, 4, 8, 4, DARK_METAL_RAMP.mid, 1)
    apply_dark_outline(c)
    return c


def _draw_wackelportal(frame: int = 0) -> PixelCanvas:
    c = PixelCanvas(16, 20)
    dx = 1 if frame % 2 else -1
    draw_shaded_ellipse(c, 8 + dx, 10, 6, 8, PORTAL_RAMP)
    draw_shaded_ellipse(c, 8, 10, 3, 5, FLUX_RAMP)
    draw_shaded_rect(c, 5, 2, 10, 4, GOLD_RAMP)
    apply_dark_outline(c)
    return c


def _sample_ramp(key: str) -> PaletteRamp:
    return make_ramp(SAMPLES[key].color)


def _draw_sample_icon(key: str) -> PixelCanvas:
    c = PixelCanvas(12, 12)
    ramp = _sample_ramp(key)
    if key == "probe_gallenstein":
        draw_shaded_ellipse(c, 6, 6, 4, 3, ramp)
        c.set_px(4, 4, ramp.highlight)
        c.set_px(8, 7, ramp.shadow)
    elif key == "probe_wucherung":
        draw_shaded_rect(c, 3, 2, 8, 9, GLASS_RAMP)
        draw_shaded_ellipse(c, 6, 6, 2, 3, ramp)
        c.set_px(5, 5, ramp.highlight)
    elif key == "probe_stempelkissen":
        draw_shaded_rect(c, 2, 4, 9, 8, METAL_RAMP)
        draw_shaded_rect(c, 3, 5, 8, 7, ramp)
    elif key == "probe_formular":
        draw_shaded_rect(c, 2, 2, 8, 8, ramp)
        draw_shaded_rect(c, 4, 4, 9, 9, PAPER_RAMP)
        c.set_px(7, 7, (210, 45, 50, 255))
    elif key == "probe_glibberkern":
        draw_shaded_ellipse(c, 6, 6, 4, 4, ramp)
        c.set_px(4, 4, (255, 255, 255, 255))
    elif key == "probe_brauseperle":
        draw_shaded_ellipse(c, 6, 7, 3, 3, ramp)
        c.set_px(4, 3, GLASS_RAMP.highlight)
        c.set_px(7, 2, GLASS_RAMP.highlight)
    elif key == "probe_zuckerkristall":
        draw_shaded_rect(c, 3, 3, 8, 8, ramp)
        draw_segment_line(c, 3, 3, 8, 8, (255, 255, 255, 255), 1)
    elif key == "probe_ameisenduft":
        draw_shaded_ellipse(c, 6, 7, 3, 3, GLASS_RAMP)
        draw_shaded_ellipse(c, 6, 7, 2, 2, ramp)
        draw_shaded_rect(c, 5, 2, 6, 4, WOOD_RAMP)
    elif key == "probe_leuchtspore":
        draw_shaded_rect(c, 3, 2, 8, 9, GLASS_RAMP)
        draw_shaded_ellipse(c, 6, 6, 2, 2, ramp)
        c.set_px(6, 5, (255, 255, 255, 255))
    elif key == "probe_plattennadel":
        draw_segment_line(c, 2, 9, 9, 2, ramp.mid, 2)
        draw_segment_line(c, 3, 9, 9, 3, ramp.light, 1)
        c.set_px(9, 2, ramp.highlight)
        c.set_px(8, 3, ramp.rim)
        c.set_px(2, 9, METAL_RAMP.shadow)
        c.set_px(3, 8, ramp.shadow)
    elif key == "probe_glockensplitter":
        draw_shaded_ellipse(c, 6, 6, 4, 2, ramp)
        draw_shaded_rect(c, 4, 4, 7, 7, ramp)
    elif key == "probe_kerzenstumpf":
        draw_shaded_rect(c, 4, 4, 7, 9, ramp)
        c.set_px(5, 2, GOLD_RAMP.highlight)
        c.set_px(5, 6, (30, 25, 35, 255))
        c.set_px(6, 6, (30, 25, 35, 255))
    elif key == "probe_knochen":
        draw_shaded_ellipse(c, 3, 8, 2, 2, ramp)
        draw_shaded_ellipse(c, 8, 3, 2, 2, ramp)
        draw_segment_line(c, 3, 8, 8, 3, ramp.mid, 2)
        draw_segment_line(c, 4, 8, 8, 4, ramp.shadow, 1)
        c.set_px(6, 5, (185, 95, 105, 255))
        c.set_px(5, 6, (185, 95, 105, 255))
    elif key == "probe_aether":
        draw_shaded_ellipse(c, 6, 6, 3, 3, ramp)
        c.set_px(3, 3, ramp.highlight)
        c.set_px(9, 8, ramp.highlight)
    elif key == "probe_schatten":
        draw_shaded_ellipse(c, 6, 6, 4, 3, ramp)
        draw_segment_line(c, 3, 7, 9, 4, DARK_METAL_RAMP.highlight, 1)
    elif key == "probe_gold":
        draw_shaded_ellipse(c, 6, 6, 3, 3, ramp)
        c.set_px(4, 4, (255, 255, 210, 255))
        c.set_px(8, 8, (255, 255, 210, 255))
    else:  # probe_kern
        draw_shaded_ellipse(c, 6, 6, 4, 4, ramp)
        draw_shaded_ellipse(c, 6, 6, 2, 2, GOLD_RAMP)
    apply_dark_outline(c)
    return c


def build_item_icon_sheets(out_dir: Path = ASSET_ROOT) -> list[Path]:
    """Build gegenstaende/<key>.{png,json} for all samples, gold sizes, and pickups (Cards B25..B27)."""
    produced: list[Path] = []

    single_items = {
        "gold_muenze": (_draw_gold_muenze, None),
        "gold_haufen_s": (lambda: _draw_gold_haufen(2), None),
        "gold_haufen_m": (lambda: _draw_gold_haufen(3), None),
        "gold_haufen_l": (lambda: _draw_gold_haufen(5), None),
        "waffe": (_draw_waffe_item, None),
        "modul": (_draw_modul_item, None),
        "experiment": (_draw_experiment_item, None),
        "kolben_voll": (lambda: _draw_kolben(True), None),
        "kolben_leer": (lambda: _draw_kolben(False), None),
        "kokon": (_draw_kokon, None),
        "auge": (_draw_auge, [{"offset": [0, 0], "color": [120, 210, 240], "radius": 12}]),
        "wuerfel": (_draw_wuerfel, None),
        "bauplan_splitter": (_draw_bauplan_splitter, None),
        "fundkiste": (_draw_fundkiste, None),
        "dienstausweis": (_draw_dienstausweis, None),
        "formular_stempel": (_draw_formular_stempel, None),
    }

    for key, (builder, glow) in single_items.items():
        canvas = builder()
        png, json_path = save_sheet(
            "gegenstaende",
            key,
            {"idle": [canvas]},
            anchor=(canvas.width // 2, canvas.height // 2),
            glow=glow,
            out_dir=out_dir,
        )
        produced.extend([png, json_path])

    animated_items = {
        "lebenskapsel": (
            [_draw_lebenskapsel(0), _draw_lebenskapsel(1)],
            [{"offset": [0, 0], "color": [90, 240, 120], "radius": 14}],
        ),
        "erinnerungssplitter": (
            [_draw_erinnerungssplitter(0), _draw_erinnerungssplitter(1)],
            [{"offset": [0, 0], "color": [160, 230, 255], "radius": 14}],
        ),
        "wackelportal": (
            [_draw_wackelportal(0), _draw_wackelportal(1)],
            [{"offset": [0, 0], "color": [140, 110, 245], "radius": 18}],
        ),
    }

    for key, (frames, glow) in animated_items.items():
        w, h = frames[0].width, frames[0].height
        png, json_path = save_sheet(
            "gegenstaende",
            key,
            {"idle": frames},
            anchor=(w // 2, h // 2),
            glow=glow,
            out_dir=out_dir,
        )
        produced.extend([png, json_path])

    glowing_samples = {
        "probe_leuchtspore": [{"offset": [0, 0], "color": [124, 232, 178], "radius": 10}],
        "probe_aether": [{"offset": [0, 0], "color": [164, 214, 255], "radius": 10}],
        "probe_kern": [{"offset": [0, 0], "color": [255, 96, 132], "radius": 12}],
    }
    for key in SAMPLES:
        canvas = _draw_sample_icon(key)
        png, json_path = save_sheet(
            "gegenstaende",
            key,
            {"idle": [canvas]},
            anchor=(6, 6),
            glow=glowing_samples.get(key),
            out_dir=out_dir,
        )
        produced.extend([png, json_path])

    return produced
