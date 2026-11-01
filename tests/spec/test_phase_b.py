from __future__ import annotations

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


def test_b01_player_sheet(tmp_path: Path) -> None:
    from tools.sprites_chars import build_player_sheet

    build_player_sheet(tmp_path)
    _assert_sheet_quality(tmp_path, "charaktere", "spielerin")


def test_b02_klonita_sheet(tmp_path: Path) -> None:
    from tools.sprites_chars import build_klonita_sheet

    build_klonita_sheet(tmp_path)
    _assert_sheet_quality(tmp_path, "charaktere", "klonita")


def test_b03_agent_sheets(tmp_path: Path) -> None:
    from tools.sprites_chars import build_agent_sheets

    build_agent_sheets(tmp_path)
    for k in ("agent_sachbearbeiter", "agent_vollstrecker", "agent_abteilungsleiter"):
        _assert_sheet_quality(tmp_path, "charaktere", k)


def test_b04_evil_and_hq_sheets(tmp_path: Path) -> None:
    from tools.sprites_chars import build_evil_and_hq_sheets

    build_evil_and_hq_sheets(tmp_path)
    for k in ("boese_kaiserin", "boese_gute", "boese_omega", "ober_cloita"):
        _assert_sheet_quality(tmp_path, "charaktere", k)


def test_b05_trader_sheets(tmp_path: Path) -> None:
    from tools.sprites_chars import build_trader_sheets

    build_trader_sheets(tmp_path)
    for k in (
        "npc_magenhaendler",
        "npc_sachbearbeiterin",
        "npc_glibberhaendler",
        "npc_ameisenhehler",
        "npc_dj",
        "npc_kuester",
    ):
        _assert_sheet_quality(tmp_path, "charaktere", k)


def _check_creature_sheets_for_universe(tmp_path: Path, u_key: str) -> None:
    from src.universes.catalog import ALL_UNIVERSES
    from tools.sprites_creatures import build_creature_sheets

    build_creature_sheets(tmp_path, universe_key=u_key)
    for sp in ALL_UNIVERSES[u_key].creatures:
        _assert_sheet_quality(tmp_path, "kreaturen", sp.species)


def test_b06_creature_sheets_schrott(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "schrott")


def test_b07_creature_sheets_sporenklub(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "sporenklub")


def test_b08_creature_sheets_fleischwelt(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "fleischwelt")


def test_b09_creature_sheets_aktenhalde(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "aktenhalde")


def test_b10_creature_sheets_kuchen(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "kuchen")


def test_b11_creature_sheets_abtei(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "abtei")


def test_b12_creature_sheets_kruemelreich(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "kruemelreich")


def test_b13_creature_sheets_spule(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "spule")


def test_b14_creature_sheets_glibbria(tmp_path: Path) -> None:
    _check_creature_sheets_for_universe(tmp_path, "glibbria")


def test_b15_mid_bosses_part1(tmp_path: Path) -> None:
    from tools.sprites_bosses import build_mid_boss_sheets

    build_mid_boss_sheets(tmp_path)
    for k in ("gabelstapler_krabbe", "sporenherz", "pfuetzenwurm", "aktenwolf", "marzipan_ritter"):
        _assert_sheet_quality(tmp_path, "bosse", k)


def test_b16_mid_bosses_part2(tmp_path: Path) -> None:
    from tools.sprites_bosses import build_mid_boss_sheets

    build_mid_boss_sheets(tmp_path)
    for k in ("glockenwaechter", "harzgeneral", "spulenmeister", "manege_clown", "warden"):
        _assert_sheet_quality(tmp_path, "bosse", k)


def test_b17_end_bosses_part1(tmp_path: Path) -> None:
    from src.procbody import RIG_LAYOUTS
    from tools.sprites_bosses import build_end_boss_sheets

    build_end_boss_sheets(tmp_path)
    for k in ("schrottpresse", "muttermyzel", "pfuetzenkoenig"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        assert k in RIG_LAYOUTS


def test_b18_end_bosses_part2(tmp_path: Path) -> None:
    from src.procbody import RIG_LAYOUTS
    from tools.sprites_bosses import build_end_boss_sheets

    build_end_boss_sheets(tmp_path)
    for k in ("oberamtsrat", "hochzeitstorte", "abt_nautilus"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        assert k in RIG_LAYOUTS


def test_b19_end_bosses_part3(tmp_path: Path) -> None:
    from src.procbody import RIG_LAYOUTS
    from tools.sprites_bosses import build_end_boss_sheets

    build_end_boss_sheets(tmp_path)
    for k in ("koenigin_mandibula", "transformator", "zirkusdirektor"):
        _assert_sheet_quality(tmp_path, "bosse", k)
        assert k in RIG_LAYOUTS


def test_b20_weapon_parts(tmp_path: Path) -> None:
    from src.weapon_parts import WEAPON_PART_KEYS
    from tools.sprites_items import build_weapon_part_sheets

    build_weapon_part_sheets(tmp_path)
    for k in WEAPON_PART_KEYS:
        _assert_sheet_quality(tmp_path, "waffen", k)


def test_b21_spell_icons_forms(tmp_path: Path) -> None:
    from src.spells import BLOCKS, FORM
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k, b in BLOCKS.items():
        if b.kind == FORM:
            _assert_sheet_quality(tmp_path, "zauber", k)


def test_b22_spell_icons_MOD(tmp_path: Path) -> None:
    from src.spells import BLOCKS, MOD
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k, b in BLOCKS.items():
        if b.kind == MOD:
            _assert_sheet_quality(tmp_path, "zauber", k)


def test_b23_spell_icons_payload(tmp_path: Path) -> None:
    from src.spells import BLOCKS, PAYLOAD
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k, b in BLOCKS.items():
        if b.kind == PAYLOAD:
            _assert_sheet_quality(tmp_path, "zauber", k)


def test_b24_spell_icons_triggers(tmp_path: Path) -> None:
    from src.spells import BLOCKS
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k in BLOCKS:
        _assert_sheet_quality(tmp_path, "zauber", k)


def test_b25_item_icons_part1(tmp_path: Path) -> None:
    from tools.sprites_items import build_item_icon_sheets

    build_item_icon_sheets(tmp_path)
    for k in (
        "gold_klein",
        "gold_mittel",
        "gold_gross",
        "stab",
        "modul",
        "gabe",
        "flasche_voll",
        "flasche_leer",
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
        "beutekiste",
        "dienstmarke",
        "formular_stempel",
        "portal_stein",
    ):
        _assert_sheet_quality(tmp_path, "gegenstaende", k)


def test_b27_sample_icons(tmp_path: Path) -> None:
    from src.samples import SAMPLES
    from tools.sprites_items import build_item_icon_sheets

    build_item_icon_sheets(tmp_path)
    assert len(SAMPLES) >= 12
    for k in SAMPLES:
        _assert_sheet_quality(tmp_path, "gegenstaende", k)


def test_b28_env_station_sheets_part1(tmp_path: Path) -> None:
    from tools.sprites_env import build_env_prop_sheets

    build_env_prop_sheets(tmp_path)
    for k in ("ws_portal", "ws_fabricator", "ws_trader", "ws_couch", "ws_physik_o_mat"):
        _assert_sheet_quality(tmp_path, "umgebung", k)


def test_b29_env_station_sheets_part2(tmp_path: Path) -> None:
    from tools.sprites_env import build_env_prop_sheets

    build_env_prop_sheets(tmp_path)
    for k in ("ws_schiessstand", "ws_archive", "ws_shredder", "ws_well", "ws_workbench"):
        _assert_sheet_quality(tmp_path, "umgebung", k)


def test_b30_env_destructible_props(tmp_path: Path) -> None:
    from tools.sprites_env import build_env_prop_sheets

    build_env_prop_sheets(tmp_path)
    for k in (
        "explosionsfass",
        "schrott_ventil",
        "sporen_knolle",
        "pilz_laterne",
        "saeure_behaelter",
        "magen_zotte",
        "akten_regal",
        "amt_uhr",
        "kuchen_kerze",
        "abtei_glocke",
        "ameisen_kokon",
        "spule_isolator",
        "glibber_ballon",
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
