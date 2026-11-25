"""Phase U integration verification across all Phase 3 subsystems and 24 universes."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.authority import Wanted
from src.bosses.cloita_null import CloitaNullBoss
from src.fabricator import discounted_gold
from src.gadgets import GadgetManager
from src.patentamt import PATENTAMT_CLOITAS, PatentamtHub, PatentArchive
from src.player import Player
from src.quest_patentamt import PatentamtQuest
from src.tv_engine import WATCH_BUFF_THRESHOLD_SEC, TVEngine
from src.universes.catalog_phase3 import all_catalog_universes
from src.workshop import ALL_STATIONS, STATIONS
from tools.sprites_patentamt import build_patentamt_sprites
from tools.sprites_phase3 import build_phase3_sprites


def test_u01_full_24_universe_catalog_and_workshop_invariants() -> None:
    catalog = all_catalog_universes()
    assert len(catalog) == 24
    assert len(STATIONS) == 12
    assert "ws_tv" in ALL_STATIONS
    assert "ws_statistik_wand" in ALL_STATIONS
    # Every alternate Cloita is a distinct character, never Klonita.
    assert len(PATENTAMT_CLOITAS) == 4
    assert all("klonita" not in c.key.lower() for c in PATENTAMT_CLOITAS.values())


def test_u02_end_to_end_phase3_gameplay_loop() -> None:
    player = Player(40, 40)
    player.gold = 200
    wanted = Wanted()
    wanted.add(3.0, "Forschungsunfall")

    # 1. Watch TV and redeem teleshopping promo code.
    tv = TVEngine()
    tv.turn_on()
    tv.step(WATCH_BUFF_THRESHOLD_SEC + 1.0, player)
    assert player.tv_buff is not None
    run_stub = SimpleNamespace(tv_promo_discount=0.0, tv_promo_single_use=True)
    ok_promo, _ = tv.redeem_promo_code("RABATT-42-GLIBBER", run_stub)
    assert ok_promo is True
    assert discounted_gold(100, run_stub) == 58

    # 2. Equip gadget and claim Patent-Alibi C-404.
    gadgets = GadgetManager()
    gadgets.equip("gadget_kolben_libelle", player)
    assert gadgets.activate(player)["activated"] is True

    hub = PatentamtHub()
    hub.enter_district("kassenschalter")
    archive = PatentArchive()
    ok_alibi, _ = archive.purchase_alibi(player, wanted)
    assert ok_alibi is True
    assert wanted.alibi_active is True

    # 3. Complete Cloita-Null quest and unlock Titan-Aktenkoffer.
    quest = PatentamtQuest()
    assert quest.sabotage_stamp(3) == "duell_bereit"
    boss = CloitaNullBoss()
    for i in range(4):
        boss.destroy_capacitor(i)
    boss.hurt(500.0)
    reward = quest.resolve_boss_fight(boss)
    assert reward is not None
    assert reward["name_de"] == "Titan-Aktenkoffer-Blaster"


def test_u03_phase3_procedural_sprites_generate_cleanly(tmp_path: Path) -> None:
    patentamt_paths = build_patentamt_sprites(root=tmp_path)
    phase3_paths = build_phase3_sprites(root=tmp_path)
    assert len(patentamt_paths) == 4  # 2 sheets * (png + json)
    assert len(phase3_paths) == 144  # 12 universes * (4 natives + 2 bosses) * (png + json)
    for p in patentamt_paths + phase3_paths:
        assert p.exists()
        assert p.stat().st_size > 0
