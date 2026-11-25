from __future__ import annotations

import itertools
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def _assert_sheet_quality(out_dir: Path, category: str, name: str) -> None:
    from src.sprites import load_sheet_meta

    png_path = out_dir / category / f"{name}.png"
    json_path = out_dir / category / f"{name}.json"
    assert png_path.exists(), f"Missing {png_path}"
    assert json_path.exists(), f"Missing {json_path}"

    meta = load_sheet_meta(json_path)
    surf = pygame.image.load(str(png_path))
    fw, fh = meta.frame_size
    assert surf.get_width() >= fw and surf.get_height() >= fh

    colors: set[tuple[int, int, int]] = set()
    opaque = 0
    for y in range(fh):
        for x in range(fw):
            r, g, b, a = surf.get_at((x, y))
            if a > 0:
                opaque += 1
                colors.add((r, g, b))
    fill_ratio = opaque / float(fw * fh)
    assert fill_ratio >= 0.18, f"{category}/{name} fill ratio too low ({fill_ratio:.2f})"
    assert len(colors) >= 5, f"{category}/{name} has fewer than 5 colors ({len(colors)})"


def _normalised_mask(pts: list[tuple[int, int]], n: int = 16) -> set[tuple[int, int]]:
    assert pts, "empty frame"
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    w, h = max(xs) - x0 + 1, max(ys) - y0 + 1
    cells = set(pts)
    return {
        (i, j) for j in range(n) for i in range(n) if (x0 + i * w // n, y0 + j * h // n) in cells
    }


def _frame_masks(
    out_dir: Path, category: str, name: str, anim: str | None
) -> list[set[tuple[int, int]]]:
    from src.sprites import AnimSpec, load_sheet_meta

    meta = load_sheet_meta(out_dir / category / f"{name}.json")
    surf = pygame.image.load(str(out_dir / category / f"{name}.png"))
    if anim is None:
        spec = meta.anims.get("idle", AnimSpec(0, 1))
    else:
        assert anim in meta.anims, f"{category}/{name} has no '{anim}' animation"
        spec = meta.anims[anim]
    fw, fh = meta.frame_size
    masks = []
    for i in range(spec.frames):
        ox, oy = i * fw, spec.row * fh
        pts = [(x, y) for y in range(fh) for x in range(fw) if surf.get_at((ox + x, oy + y))[3] > 0]
        masks.append(_normalised_mask(pts))
    return masks


def _iou(a: set[tuple[int, int]], b: set[tuple[int, int]]) -> float:
    return len(a & b) / len(a | b)


def _assert_distinct_silhouettes(
    out_dir: Path, category: str, names: list[str] | tuple[str, ...], max_iou: float = 0.85
) -> None:
    """V8.3: every kind in a group has its own silhouette (first idle frame, normalised)."""
    masks = {n: _frame_masks(out_dir, category, n, None)[0] for n in names}
    for a, b in itertools.combinations(names, 2):
        overlap = _iou(masks[a], masks[b])
        assert overlap <= max_iou, f"{category}/{a} and {b} share a silhouette (IoU {overlap:.2f})"


def _assert_animated(out_dir: Path, category: str, name: str, anim: str = "walk") -> None:
    """V8.3: a motion animation changes the shape, it does not only shift or stretch one pose."""
    masks = _frame_masks(out_dir, category, name, anim)
    assert len(masks) >= 2, f"{category}/{name} '{anim}' needs at least 2 frames"
    worst = min(_iou(masks[0], m) for m in masks[1:])
    assert worst <= 0.92, f"{category}/{name} '{anim}' just shifts one pose (IoU {worst:.2f})"


def test_b01_player_sheet(tmp_path: Path) -> None:
    from tools.sprites_chars import build_player_sheet

    build_player_sheet(tmp_path)
    _assert_sheet_quality(tmp_path, "charaktere", "spielerin")
    _assert_animated(tmp_path, "charaktere", "spielerin", "walk")


def test_b02_klonita_sheet(tmp_path: Path) -> None:
    from tools.sprites_chars import build_klonita_sheet

    build_klonita_sheet(tmp_path)
    _assert_sheet_quality(tmp_path, "charaktere", "klonita")
    _assert_animated(tmp_path, "charaktere", "klonita", "fly")


def test_b03_agent_sheets(tmp_path: Path) -> None:
    from tools.sprites_chars import build_agent_sheets

    build_agent_sheets(tmp_path)
    agents = ("agent_streife", "agent_drohne", "agent_vollstrecker", "agent_abteilungsleiter")
    for k in ("agent_sachbearbeiter", *agents):
        _assert_sheet_quality(tmp_path, "charaktere", k)
    for k in agents:
        _assert_animated(tmp_path, "charaktere", k, "walk")
    _assert_distinct_silhouettes(tmp_path, "charaktere", agents, max_iou=0.9)


def test_b04_evil_and_hq_sheets(tmp_path: Path) -> None:
    from tools.sprites_chars import build_evil_and_hq_sheets

    build_evil_and_hq_sheets(tmp_path)
    evil = ("boese_kaiserin", "boese_gute", "boese_omega", "ober_cloita")
    for k in evil:
        _assert_sheet_quality(tmp_path, "charaktere", k)
        _assert_animated(tmp_path, "charaktere", k, "walk")
    _assert_distinct_silhouettes(tmp_path, "charaktere", evil, max_iou=0.9)


def test_b05_trader_sheets(tmp_path: Path) -> None:
    from tools.sprites_chars import build_trader_sheets

    build_trader_sheets(tmp_path)
    traders = (
        "npc_magenhaendler",
        "npc_sachbearbeiterin",
        "npc_glibberhaendler",
        "npc_ameisenhehler",
        "npc_dj",
        "npc_kuester",
    )
    for k in traders:
        _assert_sheet_quality(tmp_path, "charaktere", k)
    _assert_distinct_silhouettes(tmp_path, "charaktere", traders, max_iou=0.9)


def _check_creature_sheets_for_universe(tmp_path: Path, u_key: str) -> None:
    from src.universes.catalog import ALL_UNIVERSES
    from tools.sprites_creatures import build_creature_sheets

    build_creature_sheets(tmp_path, universe_key=u_key)
    species = [sp.species for sp in ALL_UNIVERSES[u_key].creatures]
    for k in species:
        _assert_sheet_quality(tmp_path, "kreaturen", k)
        _assert_animated(tmp_path, "kreaturen", k, "walk")
    _assert_distinct_silhouettes(tmp_path, "kreaturen", species)


def test_b07_creature_sheets_sporenklub(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "sporenklub")


def test_b08_creature_sheets_fleischwelt(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "fleischwelt")


def test_b09_creature_sheets_aktenhalde(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "aktenhalde")


def test_b11_creature_sheets_abtei(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "abtei")


def test_b12_creature_sheets_kruemelreich(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "kruemelreich")


def test_b14_creature_sheets_glibbria(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "glibbria")


def test_b15_mid_bosses_part1(tmp_path: Path) -> None:
    from tools.sprites_bosses import build_mid_boss_sheets

    build_mid_boss_sheets(tmp_path)
    part1 = ("pfuetzenwurm", "aktenwolf", "manege_clown")
    for k in part1:
        _assert_sheet_quality(tmp_path, "bosse", k)
        _assert_animated(tmp_path, "bosse", k, "walk")
    _assert_distinct_silhouettes(tmp_path, "bosse", part1)


def test_b16_mid_bosses_part2(tmp_path: Path) -> None:
    from src.universes.catalog import UNIVERSES
    from tools.sprites_bosses import build_mid_boss_sheets

    build_mid_boss_sheets(tmp_path)
    for k in ("harzgeneral", "sporenherz", "glockenwaechter", "warden"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        _assert_animated(tmp_path, "bosse", k, "walk")
    for u in UNIVERSES.values():
        _assert_sheet_quality(tmp_path, "bosse", u.mid_boss)
    mid_bosses = [*(u.mid_boss for u in UNIVERSES.values()), "warden"]
    _assert_distinct_silhouettes(tmp_path, "bosse", mid_bosses)


def test_b17_end_bosses_part1(tmp_path: Path) -> None:
    from src.procbody import RIG_LAYOUTS
    from tools.sprites_bosses import build_end_boss_sheets

    build_end_boss_sheets(tmp_path)
    for k in ("weltenherz", "oberstempler"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        assert k in RIG_LAYOUTS
    _assert_distinct_silhouettes(tmp_path, "bosse", ("weltenherz", "oberstempler"))


def test_b18_end_bosses_part2(tmp_path: Path) -> None:
    from src.procbody import RIG_LAYOUTS
    from tools.sprites_bosses import build_end_boss_sheets

    build_end_boss_sheets(tmp_path)
    for k in ("mutter_glibber", "dj_myzel"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        assert k in RIG_LAYOUTS
    end_bosses = ("weltenherz", "oberstempler", "mutter_glibber", "dj_myzel")
    _assert_distinct_silhouettes(tmp_path, "bosse", end_bosses)


def test_b19_end_bosses_part3(tmp_path: Path) -> None:
    from src.procbody import RIG_LAYOUTS
    from src.universes.catalog import UNIVERSES
    from tools.sprites_bosses import build_end_boss_sheets

    build_end_boss_sheets(tmp_path)
    for k in ("ameisenkoenigin", "abt_kieme"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        assert k in RIG_LAYOUTS
    for k in ("trampolinwal", "kirchenkrake"):
        _assert_sheet_quality(tmp_path, "kreaturen", k)
        assert k in RIG_LAYOUTS
    for u in UNIVERSES.values():
        _assert_sheet_quality(tmp_path, "bosse", u.boss)
        assert u.boss in RIG_LAYOUTS
    _assert_distinct_silhouettes(tmp_path, "bosse", [u.boss for u in UNIVERSES.values()])


def test_b20_weapon_parts(tmp_path: Path) -> None:
    from src.weapon_parts import WEAPON_PART_KEYS
    from tools.sprites_items import build_weapon_part_sheets

    build_weapon_part_sheets(tmp_path)
    for k in WEAPON_PART_KEYS:
        _assert_sheet_quality(tmp_path, "waffen", k)


def test_b21_spell_icons_forms(tmp_path: Path) -> None:
    from src.spells import BLOCKS, Category
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k, b in BLOCKS.items():
        if b.category == Category.FORM:
            _assert_sheet_quality(tmp_path, "zauber", k)


def test_b22_spell_icons_modifiers(tmp_path: Path) -> None:
    from src.spells import BLOCKS, Category
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k, b in BLOCKS.items():
        if b.category == Category.MODIFIER:
            _assert_sheet_quality(tmp_path, "zauber", k)


def test_b23_spell_icons_payloads(tmp_path: Path) -> None:
    from src.spells import BLOCKS, Category
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k, b in BLOCKS.items():
        if b.category == Category.PAYLOAD:
            _assert_sheet_quality(tmp_path, "zauber", k)


def test_b24_spell_icons_all_blocks(tmp_path: Path) -> None:
    from src.spells import BLOCKS
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    block_keys = list(BLOCKS.keys())  # BLOCKS is a tuple subclass: iterate the keys explicitly
    for k in block_keys:
        _assert_sheet_quality(tmp_path, "zauber", k)


def test_b25_item_icons_part1(tmp_path: Path) -> None:
    from tools.sprites_items import build_item_icon_sheets

    build_item_icon_sheets(tmp_path)
    for k in (
        "gold_muenze",
        "gold_haufen_s",
        "gold_haufen_m",
        "gold_haufen_l",
        "waffe",
        "modul",
        "experiment",
        "kolben_voll",
        "kolben_leer",
        "lebenskapsel",
        "kokon",
    ):
        _assert_sheet_quality(tmp_path, "gegenstaende", k)


def test_b26_item_icons_part2(tmp_path: Path) -> None:
    from tools.sprites_items import build_item_icon_sheets

    build_item_icon_sheets(tmp_path)
    for k in (
        "auge",
        "wuerfel",
        "erinnerungssplitter",
        "bauplan_splitter",
        "fundkiste",
        "dienstausweis",
        "formular_stempel",
        "wackelportal",
    ):
        _assert_sheet_quality(tmp_path, "gegenstaende", k)


def test_b27_sample_icons(tmp_path: Path) -> None:
    from src.samples import SAMPLES
    from tools.sprites_items import build_item_icon_sheets

    build_item_icon_sheets(tmp_path)
    assert len(SAMPLES) == 17
    for k in SAMPLES:
        _assert_sheet_quality(tmp_path, "gegenstaende", k)


def test_b28_env_station_sheets_part1(tmp_path: Path) -> None:
    from tools.sprites_env import build_env_prop_sheets

    build_env_prop_sheets(tmp_path)
    for k in (
        "ws_portal",
        "ws_werkbank",
        "ws_fabrikator",
        "ws_liege",
        "ws_haendler",
        "ws_zapfhahn",
    ):
        _assert_sheet_quality(tmp_path, "umgebung", k)


def test_b29_env_station_sheets_part2(tmp_path: Path) -> None:
    from src.workshop import STATIONS
    from tools.sprites_env import build_env_prop_sheets

    build_env_prop_sheets(tmp_path)
    for k in (
        "ws_automat",
        "ws_schiessstand",
        "ws_archiv",
        "ws_couch",
        "ws_shredder",
        "ws_well",
        "portal_headquarters",
        "trainings_attrappe",
    ):
        _assert_sheet_quality(tmp_path, "umgebung", k)
    for st in STATIONS.values():
        _assert_sheet_quality(tmp_path, "umgebung", st.sprite_key)


def test_b30_env_destructible_props(tmp_path: Path) -> None:
    from tools.sprites_env import build_env_prop_sheets

    build_env_prop_sheets(tmp_path)
    for k in (
        "explosionsfass",
        "saeure_behaelter",
        "magen_zotte",
        "akten_regal",
        "amt_uhr",
        "glibber_ballon",
        "ameisen_kokon",
        "sporen_knolle",
        "pilz_laterne",
        "abtei_glocke",
        "pruefungs_schrein",
        "geheim_altar",
        "gold_statue",
    ):
        _assert_sheet_quality(tmp_path, "umgebung", k)


def test_b31_particle_sheets(tmp_path: Path) -> None:
    from tools.sprites_env import build_particle_sheets

    build_particle_sheets(tmp_path)
    for p in ("funken", "flamme", "eis_splitter", "saeure_tropfen", "sporen_wolke", "blitz_bogen"):
        _assert_sheet_quality(tmp_path, "partikel", p)


def test_b32_renderer_sheet_cache_integration() -> None:
    from src.rendering import Renderer
    from src.sprite_render import SheetCache

    screen = pygame.Surface((640, 360))
    renderer = Renderer(screen)
    assert hasattr(renderer, "sheet_cache") and isinstance(renderer.sheet_cache, SheetCache)


def test_b33_renderer_player_klonita_and_wand() -> None:
    from src.rendering import Renderer
    from src.run import Run

    screen = pygame.Surface((640, 360))
    renderer = Renderer(screen)
    run = Run(seed=33)
    renderer.draw(run)
    assert hasattr(renderer, "sheet_cache")


def test_b34_renderer_creatures_and_boss_rigs() -> None:
    from src.rendering import Renderer
    from src.run import Run

    screen = pygame.Surface((640, 360))
    renderer = Renderer(screen)
    run = Run(seed=34)
    renderer.draw(run)
    assert hasattr(renderer, "sheet_cache")


def test_b35_renderer_pickups_and_props() -> None:
    from src.rendering import Renderer
    from src.run import Run

    screen = pygame.Surface((640, 360))
    renderer = Renderer(screen)
    run = Run(seed=35)
    renderer.draw(run)
    assert hasattr(renderer, "sheet_cache")


def test_b36_build_all_sprites(tmp_path: Path) -> None:
    from tools.sprites import build_all

    written = build_all(out_dir=tmp_path)
    assert len(written) >= 120
