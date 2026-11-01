from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

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


@pytest.mark.parametrize(
    ("card_id", "u_key"),
    [
        ("b06", "schrott"),
        ("b07", "myzel"),
        ("b08", "magen"),
        ("b09", "amt"),
        ("b10", "kuchen"),
        ("b11", "abtei"),
        ("b12", "ameisen"),
        ("b13", "spule"),
        ("b14", "glibber"),
    ],
)
def test_b06_to_b14_creature_sheets(tmp_path: Path, card_id: str, u_key: str) -> None:
    from src.universes.catalog import UNIVERSES
    from tools.sprites_creatures import build_creature_sheets

    build_creature_sheets(tmp_path, universe_key=u_key)
    for sp in UNIVERSES[u_key].creatures:
        _assert_sheet_quality(tmp_path, "kreaturen", sp.species)


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


def test_b21_to_b24_spell_icons(tmp_path: Path) -> None:
    from src.spells import BLOCKS
    from tools.sprites_items import build_spell_icon_sheets

    build_spell_icon_sheets(tmp_path)
    for k in BLOCKS:
        _assert_sheet_quality(tmp_path, "zauber", k)


def test_b25_to_b27_item_and_sample_icons(tmp_path: Path) -> None:
    from src.samples import SAMPLES
    from tools.sprites_items import build_item_icon_sheets

    build_item_icon_sheets(tmp_path)
    for k in SAMPLES:
        _assert_sheet_quality(tmp_path, "gegenstaende", k)
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


def test_b28_to_b31_env_and_particles(tmp_path: Path) -> None:
    from src.workshop import STATIONS
    from tools.sprites_env import build_env_prop_sheets, build_particle_sheets

    build_env_prop_sheets(tmp_path)
    build_particle_sheets(tmp_path)
    for st in STATIONS.values():
        _assert_sheet_quality(tmp_path, "umgebung", st.sprite_key)
    for p in ("funken", "flamme", "eis_splitter", "saeure_tropfen", "sporen_wolke", "blitz_bogen"):
        _assert_sheet_quality(tmp_path, "partikel", p)


def test_b32_to_b35_renderer_integration() -> None:
    from src.rendering import Renderer
    from src.run import Run

    screen = pygame.Surface((640, 360))
    renderer = Renderer(screen)
    run = Run(seed=32)
    renderer.draw(run)


def test_b36_build_all_sprites(tmp_path: Path) -> None:
    from tools.sprites import build_all

    written = build_all(out_dir=tmp_path)
    assert len(written) >= 120
