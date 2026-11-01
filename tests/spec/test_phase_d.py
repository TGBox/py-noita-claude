from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

pygame.init()


@pytest.mark.parametrize(
    ("card_id", "u_key"),
    [
        ("d01", "schrott"),
        ("d02", "myzel"),
        ("d03", "magen"),
        ("d04", "amt"),
        ("d05", "kuchen"),
        ("d06", "abtei"),
        ("d07", "ameisen"),
        ("d08", "spule"),
        ("d09", "glibber"),
    ],
)
def test_d01_to_d09_universe_generators(card_id: str, u_key: str) -> None:
    from src.materials import MAT_ID
    from src.universes.catalog import UNIVERSES
    from src.universes.gen import GENERATORS, generate_universe
    from src.world import World

    assert u_key in GENERATORS
    u = UNIVERSES[u_key]
    w = World(320, 200)
    lvl = generate_universe(w, u, 1, 42)

    assert lvl.universe_key == u_key
    assert [r[0] for r in lvl.regions] == [r.key for r in u.regions]
    sx, sy = lvl.spawn
    ex, ey = lvl.exit_point
    assert w.get(sx, sy) == MAT_ID["air"]
    assert w.get(ex, ey) == MAT_ID["air"]
    for rect in (lvl.mid_boss_arena, lvl.boss_arena):
        assert 0 <= rect[0] < rect[2] <= w.width
        assert 0 <= rect[1] < rect[3] <= w.height


def test_d10_worldgen_dispatch_and_boss_spawns() -> None:
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    run = Run(seed=10, universe_key="myzel")
    u = UNIVERSES["myzel"]
    assert run.level.universe_key == "myzel"
    species_alive = {c.species for c in run.enemies.creatures}
    assert u.mid_boss in species_alive
    assert u.boss in species_alive


def test_d11_and_d12_all_9_secondary_events() -> None:
    from src.events import EVENTS, Event, pick_event
    from src.run import Run

    assert len(EVENTS) == 9
    run = Run(seed=12)
    for key, spec in EVENTS.items():
        ev = Event(spec=spec, remaining=spec.duration)
        ev.on_start(run)
        ev.tick(1.0, run)
        data = ev.to_data()
        restored = Event.from_data(data)
        assert restored is not None and restored.spec.key == key
        ev.on_end(run)
        assert ev.active is False

    rng = random.Random(42)
    picked = [pick_event("schrott", 1, rng) for _ in range(30)]
    assert any(p is not None for p in picked)


def test_d13_and_d14_all_6_challenges_and_shrine() -> None:
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
    run = Run(seed=14)
    ch = Challenge(spec=CHALLENGES["pacifist"])
    ch.activate()
    ch.on_event(
        "leave_universe", {"universe": "schrott", "depth": 1, "destination": "workshop"}, run
    )
    assert ch.completed is True

    gold_before = run.gold
    ch.pay_reward(run)
    assert run.gold == gold_before + CHALLENGES["pacifist"].reward_gold
    assert ch.reward_paid is True


def test_d15_and_d16_playtest_bot() -> None:
    from src.bot import run_bot, run_full

    rep = run_bot("schrott", seed=1, max_seconds=10.0)
    assert rep.universe_key == "schrott"
    assert rep.ticks > 0
    assert rep.errors == []

    full = run_full(seed=1, max_seconds_per_stage=6.0)
    assert len(full) >= 1
    assert all(r.errors == [] for r in full)
