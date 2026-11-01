from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def test_e01_workshop_generator_and_10_stations() -> None:
    from src.workshop import STATIONS, WORKSHOP_SIZE, generate_workshop, station_at
    from src.world import World

    assert WORKSHOP_SIZE == (640, 360)
    assert len(STATIONS) == 10
    w = World(*WORKSHOP_SIZE)
    layout = generate_workshop(w)
    for key, st in layout.stations.items():
        cx = (st.rect[0] + st.rect[2]) // 2
        cy = (st.rect[1] + st.rect[3]) // 2
        found = station_at(layout, cx, cy)
        assert found is not None and found.key == key


def test_e02_and_e03_economy_formulas_and_gold_veins() -> None:
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


def test_e04_and_e05_all_6_traders_and_quirks() -> None:
    from src.run import Run
    from src.traders import TRADERS, buy_offer, generate_offers

    assert len(TRADERS) == 6
    rng = random.Random(4)
    for t_key, spec in TRADERS.items():
        offers = generate_offers(spec, depth=2, rng=rng, universe_sample_key="probe_harz")
        assert len(offers) == 4
        if t_key == "npc_ameisenhehler":
            assert any(len(o.sample_cost) > 0 for o in offers)
        elif t_key == "npc_kuester":
            assert any(o.blessed for o in offers if o.kind == "wand")

    run = Run(seed=5)
    run.gold = 500
    kroll = TRADERS["npc_sachbearbeiterin"]
    offers = generate_offers(kroll, 1, rng)
    ok, _ = buy_offer(run, kroll, offers[0])
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


def test_e07_to_e09_minigames_physik_and_schiessstand() -> None:
    from src.minigames.physik_o_mat import PUZZLE_KEYS, make_physik_puzzle
    from src.minigames.schiessstand import SchiessstandMinigame

    assert len(PUZZLE_KEYS) == 4
    for pk in PUZZLE_KEYS:
        mg = make_physik_puzzle(pk, seed=1)
        mg.step(0.1, action="use")
        for _ in range(120):
            res = mg.step(0.1)
            if res is not None:
                break
        assert mg.result is not None and mg.result.won is True

    smg = SchiessstandMinigame(seed=1)
    for target in list(smg.targets):
        if not target.is_authority_dummy:
            smg.step(0.05, action="shoot", cursor=(int(target.x), int(target.y)))
    assert smg.result is not None and smg.result.won is True


def test_e10_to_e15_workshop_flow_menus_and_dummy() -> None:
    from src.run import Run

    run = Run(seed=15)
    run.enter_workshop()
    assert run.in_workshop is True
    assert run.workshop_layout is not None

    # Dummy check
    assert any(c.stance == "peaceful" for c in run.enemies.creatures)
    run.choose_next_universe(0)
    assert run.in_workshop is False
