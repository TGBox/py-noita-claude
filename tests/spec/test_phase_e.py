from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

# Bible 07 "Stationen": key -> (name, width, height)
BIBLE_STATIONS = {
    "ws_portal": ("Portalrahmen", 40, 48),
    "ws_werkbank": ("Werkbank", 48, 28),
    "ws_fabrikator": ("Fabrikator", 40, 40),
    "ws_liege": ("Experimentierliege", 48, 24),
    "ws_haendler": ("Händlerplatz", 72, 32),
    "ws_zapfhahn": ("Schnapszapfanlage", 16, 24),
    "ws_automat": ("Physik-o-Mat", 24, 36),
    "ws_schiessstand": ("Schießstand", 64, 24),
    "ws_archiv": ("Archivschrank", 24, 32),
    "ws_couch": ("Klonitas Couch", 40, 18),
    "ws_shredder": ("Akten-Schredder", 16, 20),
    "ws_well": ("Flaschen-Brunnen", 16, 18),
}


def test_e01_workshop_generator_and_stations() -> None:
    from src.workshop import STATIONS, WORKSHOP_SIZE, generate_workshop, station_at
    from src.world import World

    assert WORKSHOP_SIZE == (640, 360)
    assert set(STATIONS) == set(BIBLE_STATIONS)
    for key, (name, width, height) in BIBLE_STATIONS.items():
        st = STATIONS[key]
        assert st.name == name and st.sprite_key == key
        assert (st.rect[2] - st.rect[0], st.rect[3] - st.rect[1]) == (width, height)
    layout = generate_workshop(World(*WORKSHOP_SIZE))
    assert layout.stations["ws_fabricator"].key == "ws_fabrikator"
    for key, st in STATIONS.items():
        cx = (st.rect[0] + st.rect[2]) // 2
        cy = (st.rect[1] + st.rect[3]) // 2
        found = station_at(layout, cx, cy)
        assert found is not None and found.key == key
    assert len(layout.trader_slots) == 2


def test_e02_economy_formulas() -> None:
    from src.economy import (
        boss_gold,
        crate_gold,
        creature_gold,
        experiment_reroll_price,
        fabricator_gold,
        mid_boss_gold,
        module_price,
        pile_gold,
        weapon_price,
    )

    rng = random.Random(1)
    for rank, (low, high) in {1: (5, 10), 2: (10, 18), 3: (18, 30)}.items():
        for _ in range(50):
            assert low <= creature_gold(rank, rng) <= high
            assert 10 * rank <= pile_gold(rank, rng) <= 40 * rank
            assert 20 * rank <= crate_gold(rank, rng) <= 60 * rank
    assert [creature_gold(r, rng, big=True) for r in (1, 2, 3)] == [40, 70, 110]
    assert [mid_boss_gold(r) for r in (1, 2, 3)] == [40, 70, 110]
    assert [boss_gold(r) for r in (1, 2, 3)] == [200, 350, 500]
    assert module_price(1, 2) == 75  # 50 * (1 + 0.25 * 2)
    assert module_price(1, 2) < module_price(2, 2) < module_price(3, 2)
    assert [weapon_price(s) for s in (1, 2, 3)] == [160, 230, 300]
    assert fabricator_gold(1, 2) == round(75 * 0.7)
    assert [experiment_reroll_price(i) for i in range(3)] == [100, 200, 400]


def test_e03_gold_drops_for_veins_and_bosses() -> None:
    from src.materials import MAT_ID
    from src.run import Run

    run = Run(seed=3)
    run.pickups.clear()
    px, py = int(run.player.x), int(run.player.y)
    run.world.fill_rect(px + 10, py - 4, px + 16, py + 4, MAT_ID["gold_vein"])
    run.world.explode(px + 13, py, 6)
    run.update(0.016, None)
    assert any(p.kind == "gold" for p in run.pickups)

    run = Run(seed=3, universe_key="sporenklub", boss_slot=True)
    run.pickups.clear()
    boss = next(c for c in run.enemies.creatures if c.species == "dj_myzel")
    boss.body.hp = 0.0
    run.update(0.016, None)
    gold = sum(p.amount for p in run.pickups if p.kind == "gold")
    assert gold >= 200  # rank of the first universe is 1 -> boss gold 200


def test_e04_all_6_traders_and_offer_generation() -> None:
    from src.spells import BLOCKS, Category
    from src.traders import TRADERS, generate_offers, traders_for_workshop
    from src.universes.catalog import UNIVERSES

    assert len(TRADERS) == 6
    homes = {spec.home_universe for spec in TRADERS.values()}
    assert homes == set(UNIVERSES.keys())
    rng = random.Random(4)
    for key, spec in TRADERS.items():
        offers = generate_offers(spec, 2, rng)
        assert len(offers) == 4
        for o in offers:
            if key == "npc_kuester":
                assert o.kind == "wand" and o.blessing in ("mana_max", "recharge", "capacity")
                continue
            block = BLOCKS[o.key]
            assert not block.retired
            if key == "npc_magenhaendler":
                assert block.category is Category.PAYLOAD
                assert o.key in ("sekret_blut", "sekret_saeure", "sekret_glut")
            elif key == "npc_sachbearbeiterin":
                assert block.category is Category.TRIGGER
            elif key == "npc_glibberhaendler":
                assert block.category is Category.MODIFIER
            elif key == "npc_dj":
                assert block.category is Category.FORM
            elif key == "npc_ameisenhehler":
                assert o.sample_cost == (("probe_zuckerkristall", 2),)
    names = [t.name for t in traders_for_workshop(["fleischwelt", "aktenhalde", "glibbria"])]
    assert names == ["Wobbel", "Frau Abheft"]
    assert traders_for_workshop([]) == []


def test_e05_trader_buy_and_quirks() -> None:
    from src.economy import module_price
    from src.run import Run
    from src.spells import BLOCKS
    from src.traders import TRADERS, buy_offer, generate_offers

    rng = random.Random(5)
    run = Run(seed=5)
    run.gold = 500
    abheft = TRADERS["npc_sachbearbeiterin"]
    offer = generate_offers(abheft, 1, rng)[0]
    assert offer.gold_cost == module_price(BLOCKS[offer.key].rarity_tier, 1) + 10
    ok, _ = buy_offer(run, abheft, offer)
    assert ok is True and run.gold == 500 - offer.gold_cost

    karl = TRADERS["npc_ameisenhehler"]
    offer = generate_offers(karl, 1, rng)[0]
    ((sample_key, count),) = offer.sample_cost
    run.inventory.add_sample(sample_key, count)
    gold = run.gold
    ok, _ = buy_offer(run, karl, offer, use_samples=True)
    assert ok is True and run.gold == gold and run.inventory.sample_count(sample_key) == 0

    run.gold = 0
    ok, msg = buy_offer(run, abheft, generate_offers(abheft, 1, rng)[0])
    assert ok is False and msg == "Zu wenig Gold."


def test_e06_fabricator_recipes_and_limits() -> None:
    from src.fabricator import MAX_BUILDS_PER_VISIT, Fabricator, build_cost
    from src.run import Run
    from src.spells import BLOCKS, Category

    assert MAX_BUILDS_PER_VISIT == 3
    for block in BLOCKS.values():
        rec = build_cost(block.key)
        assert rec.gold > 0
        expected = 2 if block.category is Category.TRIGGER else 1
        assert rec.universe_samples == expected
        assert (rec.blueprint_shards == 1) == (block.rarity_tier == 3)
        assert (len(rec.special_samples) > 0) == (block.rarity_tier >= 2)

    run = Run(seed=6)
    run.gold = 9999
    run.inventory.add_sample("probe_gallenstein", 20)
    fab = Fabricator()
    ok, _ = fab.can_build(run, "funke")
    assert ok is False  # no blueprint yet
    run.records.discover("blueprint", "funke")
    for _ in range(MAX_BUILDS_PER_VISIT):
        ok, _ = fab.craft(run, "funke")
        assert ok is True
    assert fab.can_build(run, "funke")[0] is False
    fab.reset_visit()
    assert fab.can_build(run, "funke")[0] is True


def _solve(puzzle_key: str):
    from src.minigames.physik_o_mat import make_physik_puzzle, solve_actions

    mg = make_physik_puzzle(puzzle_key, seed=1)
    for action, cursor in solve_actions(puzzle_key):
        mg.step(0.1, action=action, cursor=cursor)
    for _ in range(150):
        if mg.step(0.1) is not None:
            break
    return mg


def test_e07_physik_o_mat_part1() -> None:
    from src.minigames.physik_o_mat import make_physik_puzzle

    for key in ("glas_fuellen", "vase_retten", "kerze_zuenden", "ameisenstrasse"):
        mg = _solve(key)
        assert mg.result is not None and mg.result.won is True, key
    idle = make_physik_puzzle("glas_fuellen", seed=1)
    for _ in range(400):
        if idle.step(0.1) is not None:
            break
    assert idle.result is not None and idle.result.won is False


def test_e08_physik_o_mat_part2() -> None:
    from src.minigames import NEXT_BOOST_KEYS
    from src.minigames.physik_o_mat import PUZZLE_KEYS

    assert len(PUZZLE_KEYS) == 7 and "electricity_water" not in PUZZLE_KEYS
    for key in PUZZLE_KEYS:
        mg = _solve(key)
        res = mg.result
        assert res is not None and res.won is True, key
        assert res.reward_gold == 60 or res.reward_sample or res.next_boost in NEXT_BOOST_KEYS


def test_e09_schiessstand_minigame() -> None:
    from src.minigames import NEXT_BOOST_KEYS
    from src.minigames.schiessstand import SchiessstandMinigame

    smg = SchiessstandMinigame(seed=1)
    assert smg.stake == 20 and smg.time_limit == 30.0
    kinds = [t.kind for t in smg.targets]
    assert kinds.count("agent") == 24 and kinds.count("klonita") == 6
    for t in smg.targets:
        if t.kind == "agent":
            smg.step(0.0, action="shoot", cursor=(int(t.x), int(t.y)))
    while smg.step(0.5) is None:
        pass
    assert smg.result is not None and smg.result.next_boost in NEXT_BOOST_KEYS

    bad = SchiessstandMinigame(seed=1)
    klonita = next(t for t in bad.targets if t.kind == "klonita")
    bad.step(0.0, action="shoot", cursor=(int(klonita.x), int(klonita.y)))
    assert bad.score == -3


def test_e10_workshop_mode_and_direct_stations() -> None:
    from src.flask import Flask
    from src.run import Run
    from src.workshop import STATIONS

    run = Run(seed=10)
    run.player.body.hp = 1.0
    run.enter_workshop()
    assert run.in_workshop is True and run.workshop_layout is not None
    assert run.player.body.hp == run.player.body.max_hp

    def use(key: str) -> None:
        x0, y0, x1, y1 = STATIONS[key].rect
        run.player.x, run.player.y = (x0 + x1) / 2, (y0 + y1) / 2
        run.interact_station()

    run.flask = Flask(liquid="water", amount=0.0)
    run.gold = 15
    use("ws_zapfhahn")
    assert run.flask.key == "fluxschnaps" and run.gold == 5
    use("ws_well")
    assert run.flask.key == "water"
    run.player.body.hp = run.player.body.max_hp * 0.5
    use("ws_couch")
    healed = run.player.body.hp
    use("ws_couch")
    assert healed > run.player.body.max_hp * 0.5 and run.player.body.hp == healed
    use("ws_fabrikator")
    assert run.menu_mode == "fabricator"


def test_e11_portal_select_menu_and_choose_next_universe() -> None:
    from src.run import Run

    run = Run(seed=11)
    run.enter_workshop()
    offers = run.plan.offers()
    run.next_boost = "speed"
    run.choose_next_universe(1)
    assert run.in_workshop is False
    assert run.universe_key == offers[1].universe
    assert run.plan.visited == [offers[1].universe]


def test_e12_fabricator_menu_and_craft_in_run() -> None:
    from src.fabricator import build_cost
    from src.run import Run

    run = Run(seed=12)
    run.enter_workshop()
    run.gold = 999
    run.records.discover("blueprint", "funke")
    rec = build_cost("funke")
    run.inventory.add_sample("probe_gallenstein", rec.universe_samples * 2)
    ok, _ = run.craft_selected_recipe("funke")
    assert ok is True and run.fabricator.builds_this_visit == 1


def test_e13_trader_menu_and_purchase_in_run() -> None:
    from src.run import Run

    run = Run(seed=13)
    run.enter_workshop()
    assert run.traders == []
    for _ in range(2):
        run.choose_next_universe(0)
        run.enter_workshop()
    assert [t.home_universe for t in run.traders] == list(reversed(run.plan.visited))
    first = run.traders[0]
    assert len(run.trader_offers[first.key]) == 4
    run.gold = 5000
    ok, _ = run.buy_trader_offer(first.key, 0)
    assert ok is True and len(run.trader_offers[first.key]) == 3


def test_e14_minigame_integration_in_run() -> None:
    from src.run import Run
    from src.workshop import STATIONS

    run = Run(seed=14)
    run.enter_workshop()
    run.gold = 100
    x0, y0, x1, y1 = STATIONS["ws_schiessstand"].rect
    run.player.x, run.player.y = (x0 + x1) / 2, (y0 + y1) / 2
    run.interact_station()
    assert run.menu_mode == "minigame" and run.gold == 80
    for t in run.active_minigame.targets:
        if t.kind == "agent":
            run.step_minigame(0.0, action="shoot", cursor=(int(t.x), int(t.y)))
    while run.active_minigame is not None and run.active_minigame.result is None:
        run.step_minigame(0.5)
    assert run.next_boost != ""
    gold = run.gold
    run.menu_mode = ""
    run.interact_station()
    assert run.menu_mode != "minigame" and run.gold == gold  # one attempt per visit


def test_e15_workshop_target_dummy() -> None:
    from src.run import Run

    run = Run(seed=15)
    run.enter_workshop()
    dummy = next(c for c in run.enemies.creatures if c.species == "trainings_attrappe")
    assert dummy.spec.stance == "peaceful"


def test_e16_experiment_couch_offers_and_reroll() -> None:
    from src.run import Run
    from src.workshop import STATIONS

    run = Run(seed=16)
    run.enter_workshop()
    run.gold = 1000
    run.inventory.rerolls = 0
    x0, y0, x1, y1 = STATIONS["ws_liege"].rect
    run.player.x, run.player.y = (x0 + x1) / 2, (y0 + y1) / 2
    run.interact_station()
    assert run.menu_mode == "experiment" and len(set(run.experiment_offers)) == 3
    assert run.reroll_experiments() is True and run.gold == 900
    assert run.reroll_experiments() is True and run.gold == 700
    chosen = run.experiment_offers[0]
    assert run.pick_experiment(0) is True and chosen in run.perks
    assert run.pick_experiment(1) is False
