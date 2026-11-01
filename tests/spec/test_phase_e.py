from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def test_e01_workshop_generator_and_stations() -> None:
    from src.workshop import STATIONS, WORKSHOP_SIZE, generate_workshop, station_at
    from src.world import World

    assert WORKSHOP_SIZE == (640, 360)
    assert len(STATIONS) >= 10
    w = World(*WORKSHOP_SIZE)
    layout = generate_workshop(w)
    for key, st in layout.stations.items():
        cx = (st.rect[0] + st.rect[2]) // 2
        cy = (st.rect[1] + st.rect[3]) // 2
        found = station_at(layout, cx, cy)
        assert found is not None and found.key == key


def test_e02_economy_formulas() -> None:
    from src.economy import (
        crate_gold,
        creature_gold,
        mid_boss_gold,
        module_price,
        pile_gold,
        reroll_price,
        weapon_price,
    )

    rng = random.Random(1)
    assert creature_gold(50.0, 1, rng) >= 1
    assert pile_gold(1, rng) >= 5
    assert crate_gold(1, rng) >= 10
    assert mid_boss_gold(2) == 75
    assert module_price(1, 1) < module_price(2, 1) < module_price(3, 1)
    assert weapon_price(1, 1) < weapon_price(2, 1) < weapon_price(3, 1)
    assert reroll_price(0) == 20 and reroll_price(1) == 40 and reroll_price(2) == 80


def test_e03_gold_drops_for_veins_and_mid_bosses() -> None:
    from src.economy import mid_boss_gold
    from src.materials import MAT_ID
    from src.run import Run

    assert mid_boss_gold(2) == 75
    run = Run(seed=3)
    px, py = int(run.player.x), int(run.player.y)
    run.world.fill_rect(px + 10, py - 4, px + 16, py + 4, MAT_ID["gold_vein"])
    run.world.explode(px + 13, py, 6)
    run.update(0.016, None)
    assert any(p.kind == "gold" for p in run.pickups)


def test_e04_all_6_traders_and_offer_generation() -> None:
    from src.traders import TRADERS, generate_offers
    from src.universes.catalog import UNIVERSES

    assert len(TRADERS) == 6
    rng = random.Random(4)
    for t_key, spec in TRADERS.items():
        assert spec.home_universe in UNIVERSES
        offers = generate_offers(spec, depth=2, rng=rng, universe_sample_key="probe_ameisenduft")
        assert len(offers) == 4
        if t_key == "npc_ameisenhehler":
            assert any(len(o.sample_cost) > 0 for o in offers)
        elif t_key == "npc_kuester":
            assert any(o.blessed for o in offers if o.kind == "wand")


def test_e05_trader_buy_and_quirks() -> None:
    from src.run import Run
    from src.traders import TRADERS, buy_offer, generate_offers

    rng = random.Random(5)
    run = Run(seed=5)
    run.gold = 500
    sachbearbeiterin = TRADERS["npc_sachbearbeiterin"]
    offers = generate_offers(sachbearbeiterin, 1, rng)
    ok, _ = buy_offer(run, sachbearbeiterin, offers[0])
    assert ok is True
    assert run.player.body.stamped_good >= 25.0


def test_e06_fabricator_recipes_and_limits() -> None:
    from src.fabricator import MAX_BUILDS_PER_VISIT, Fabricator, build_cost
    from src.spells import BLOCKS

    assert MAX_BUILDS_PER_VISIT == 3
    for block in BLOCKS.values():
        rec = build_cost(block.key)
        assert rec.gold > 0 and len(rec.samples) >= 1

    fab = Fabricator()
    rec_spark = build_cost("spark")
    samples = {k: need * 5 for k, need in rec_spark.samples}
    ok, _ = fab.can_build("spark", unlocked_blueprints=set(), gold=999, sample_counts=samples)
    assert ok is True


def test_e07_physik_o_mat_part1() -> None:
    from src.minigames.physik_o_mat import make_physik_puzzle

    for pk in ("lava_water", "acid_gold"):
        mg = make_physik_puzzle(pk, seed=1)
        mg.step(0.1, action="use")
        for _ in range(120):
            res = mg.step(0.1)
            if res is not None:
                break
        assert mg.result is not None and mg.result.won is True


def test_e08_physik_o_mat_part2() -> None:
    from src.minigames.physik_o_mat import PUZZLE_KEYS, make_physik_puzzle

    assert len(PUZZLE_KEYS) >= 4
    for pk in PUZZLE_KEYS:
        mg = make_physik_puzzle(pk, seed=1)
        mg.step(0.1, action="use")
        for _ in range(120):
            res = mg.step(0.1)
            if res is not None:
                break
        assert mg.result is not None and mg.result.won is True


def test_e09_schiessstand_minigame() -> None:
    from src.minigames.schiessstand import SchiessstandMinigame

    smg = SchiessstandMinigame(seed=1)
    for target in list(smg.targets):
        if not target.is_authority_dummy:
            smg.step(0.05, action="shoot", cursor=(int(target.x), int(target.y)))
    assert smg.result is not None and smg.result.won is True


def test_e10_workshop_mode_and_direct_stations() -> None:
    from src.run import Run

    run = Run(seed=10)
    run.enter_workshop()
    assert run.in_workshop is True
    assert run.workshop_layout is not None


def test_e11_portal_select_menu_and_choose_next_universe() -> None:
    from src.run import Run

    run = Run(seed=11)
    run.enter_workshop()
    run.choose_next_universe(0)
    assert run.in_workshop is False


def test_e12_fabricator_menu_and_craft_in_run() -> None:
    from src.fabricator import build_cost
    from src.run import Run

    run = Run(seed=12)
    run.enter_workshop()
    rec = build_cost("spark")
    run.gold = 999
    for sk, count in rec.samples:
        run.inventory.add_sample(sk, count * 2)
    ok, _ = run.craft_selected_recipe("spark")
    assert ok is True


def test_e13_trader_menu_and_reroll_in_run() -> None:
    from src.run import Run

    run = Run(seed=13)
    run.enter_workshop()
    run.gold = 500
    assert len(run.trader_offers) == 4
    ok, _ = run.buy_trader_offer(0)
    assert ok is True
    assert run.reroll_trader_offers() is True


def test_e14_minigame_integration_in_run() -> None:
    from src.minigames.schiessstand import SchiessstandMinigame
    from src.run import Run

    run = Run(seed=14)
    run.enter_workshop()
    run.active_minigame = SchiessstandMinigame(seed=1)
    run.menu_mode = "minigame"
    for target in list(run.active_minigame.targets):
        if not target.is_authority_dummy:
            run.step_minigame(0.05, action="shoot", cursor=(int(target.x), int(target.y)))
    assert run.next_boost != ""


def test_e15_workshop_target_dummy() -> None:
    from src.run import Run

    run = Run(seed=15)
    run.enter_workshop()
    assert any(c.stance in ("peaceful", "passive") for c in run.enemies.creatures)
