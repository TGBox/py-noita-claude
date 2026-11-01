from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def _check_universe_generator(u_key: str) -> None:
    from src.materials import MAT_ID
    from src.universes.catalog import ALL_UNIVERSES
    from src.universes.gen import GENERATORS, generate_universe
    from src.world import World

    assert u_key in GENERATORS
    u = ALL_UNIVERSES[u_key]
    w = World(320, 200)
    lvl = generate_universe(w, u, 1, 42)

    assert lvl.universe_key == u.key
    assert [r[0] for r in lvl.regions] == [r.key for r in u.regions]
    sx, sy = lvl.spawn
    ex, ey = lvl.exit_point
    assert w.get(sx, sy) == MAT_ID["air"]
    assert w.get(ex, ey) == MAT_ID["air"]
    for rect in (lvl.mid_boss_arena, lvl.boss_arena):
        assert 0 <= rect[0] < rect[2] <= w.width
        assert 0 <= rect[1] < rect[3] <= w.height


def test_d01_generator_fleischwelt() -> None:
    _check_universe_generator("fleischwelt")


def test_d02_generator_aktenhalde() -> None:
    _check_universe_generator("aktenhalde")


def test_d03_generator_glibbria() -> None:
    _check_universe_generator("glibbria")


def test_d04_generator_kruemelreich() -> None:
    _check_universe_generator("kruemelreich")


def test_d05_generator_sporenklub() -> None:
    _check_universe_generator("sporenklub")


def test_d06_generator_abtei() -> None:
    _check_universe_generator("abtei")


def test_d07_generator_pool_schrott() -> None:
    _check_universe_generator("schrott")


def test_d08_generator_pool_kuchen() -> None:
    _check_universe_generator("kuchen")


def test_d09_generator_pool_spule() -> None:
    _check_universe_generator("spule")


def test_d10_worldgen_dispatch_and_boss_spawns() -> None:
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    run = Run(seed=10, universe_key="sporenklub")
    u = UNIVERSES["sporenklub"]
    assert run.level.universe_key == "sporenklub"
    species_alive = {c.species for c in run.enemies.creatures}
    assert u.mid_boss in species_alive
    assert u.boss in species_alive


def test_d11_universe_events_part1() -> None:
    from src.events import EVENTS, Event, pick_event
    from src.run import Run

    assert len(EVENTS) >= 6
    run = Run(seed=11)
    for key, spec in list(EVENTS.items())[:5]:
        ev = Event(spec=spec, remaining=spec.duration)
        ev.on_start(run)
        ev.tick(1.0, run)
        data = ev.to_data()
        restored = Event.from_data(data)
        assert restored is not None and restored.spec.key == key
        ev.on_end(run)
        assert ev.active is False

    rng = random.Random(42)
    picked = [pick_event("fleischwelt", 1, rng) for _ in range(30)]
    assert any(p is not None for p in picked)


def test_d12_universe_events_part2() -> None:
    from src.events import EVENTS, Event
    from src.run import Run

    assert len(EVENTS) >= 9
    run = Run(seed=12)
    for spec in EVENTS.values():
        ev = Event(spec=spec, remaining=spec.duration)
        ev.on_start(run)
        ev.tick(1.0, run)
        ev.on_end(run)
        assert ev.active is False


def test_d13_all_6_challenges() -> None:
    from src.challenges import CHALLENGES, Challenge
    from src.run import Run

    assert set(CHALLENGES.keys()) == {
        "pacifist",
        "no_gold",
        "speed_run",
        "no_damage",
        "kill_streak",
        "dry_feet",
    }
    run = Run(seed=13)
    ch = Challenge(spec=CHALLENGES["pacifist"])
    ch.activate()
    ch.on_event(
        "leave_universe", {"universe": "fleischwelt", "depth": 1, "destination": "workshop"}, run
    )
    assert ch.completed is True


def test_d14_challenge_shrine_and_reward_in_run() -> None:
    from src.challenges import CHALLENGES, Challenge
    from src.run import Run

    run = Run(seed=14)
    ch = Challenge(spec=CHALLENGES["pacifist"])
    ch.activate()
    ch.completed = True
    gold_before = run.gold
    ch.pay_reward(run)
    assert run.gold == gold_before + CHALLENGES["pacifist"].reward_gold
    assert ch.reward_paid is True


def test_d15_playtest_bot_single_universe() -> None:
    from src.bot import run_bot

    rep = run_bot("fleischwelt", seed=1, max_seconds=10.0)
    assert rep.universe_key == "fleischwelt"
    assert rep.ticks > 0
    assert rep.errors == []


def test_d16_playtest_bot_full_run() -> None:
    from src.bot import run_full

    full = run_full(seed=1, max_seconds_per_stage=6.0)
    assert len(full) >= 1
    assert all(r.errors == [] for r in full)
