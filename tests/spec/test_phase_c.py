from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

pygame.init()


def _check_universe_creatures(u_key: str) -> None:
    from src.enemies import SPECIES, EnemyManager
    from src.factions import UNIVERSE_FACTIONS
    from src.player import Player
    from src.universes.catalog import ALL_UNIVERSES
    from src.world import World

    u = ALL_UNIVERSES[u_key]
    w = World(160, 120)
    p = Player(80.0, 60.0)
    em = EnemyManager()

    for spawn in u.creatures:
        assert spawn.species in SPECIES, f"Missing species {spawn.species} for {u_key}"
        c = em.spawn(spawn.species, 40.0, 60.0)
        assert c.spec.drops_sample in (*u.samples, u.sample_key)
        assert c.spec.faction == UNIVERSE_FACTIONS[u.key]
        if spawn.species == "blattlaus":
            assert c.giver is True

    projs: list = []
    for _ in range(20):
        em.update(1.0 / 60.0, w, p, projs)


def test_c01_creatures_fleischwelt() -> None:
    _check_universe_creatures("fleischwelt")


def test_c02_creatures_aktenhalde() -> None:
    _check_universe_creatures("aktenhalde")


def test_c03_creatures_glibbria() -> None:
    _check_universe_creatures("glibbria")


def test_c04_creatures_kruemelreich() -> None:
    _check_universe_creatures("kruemelreich")


def test_c05_creatures_sporenklub() -> None:
    _check_universe_creatures("sporenklub")


def test_c06_creatures_abtei() -> None:
    _check_universe_creatures("abtei")


def test_c09_big_creatures() -> None:
    from src.enemies import SPECIES, EnemyManager

    em = EnemyManager()
    for k, faction in (("trampolinwal", "gelee"), ("kirchenkrake", "tiefsee")):
        assert k in SPECIES
        assert SPECIES[k].faction == faction
        em.spawn(k, 40.0, 60.0)

    # Kirchenkrake: noise meter (+40 per noise, -10 per second, wakes at 100).
    fast = EnemyManager()
    krake = fast.spawn("kirchenkrake", 100.0, 100.0)
    out: list[tuple[str, dict[str, object]]] = []
    for _ in range(3):
        fast.on_noise(110.0, 100.0, 200.0, out)
    assert ("creature_woke", {"species": "kirchenkrake"}) in out

    slow = EnemyManager()
    krake = slow.spawn("kirchenkrake", 100.0, 100.0)
    out = []
    for _ in range(3):
        slow.on_noise(110.0, 100.0, 200.0, out)
        krake.noise_level = max(0.0, krake.noise_level - 10.0 * 5.0)  # 5 s of decay
    assert not any(ev[0] == "creature_woke" for ev in out)


def test_c10_mid_bosses_part1() -> None:
    from src.enemies import SPECIES

    for k in ("pfuetzenwurm", "aktenwolf", "manege_clown", "harzgeneral", "sporenherz"):
        assert k in SPECIES
        assert SPECIES[k].is_mid_boss is True
        assert SPECIES[k].sample_chance == pytest.approx(1.0)


def test_c11_mid_bosses_part2() -> None:
    from src.enemies import SPECIES
    from src.universes.catalog import UNIVERSES

    assert "glockenwaechter" in SPECIES
    assert len(UNIVERSES) == 6
    for u in UNIVERSES.values():
        assert u.mid_boss in SPECIES
        assert SPECIES[u.mid_boss].is_mid_boss is True


def test_c12_mvp_end_bosses() -> None:
    from src.enemies import SPECIES
    from src.universes.catalog import UNIVERSES

    for u in UNIVERSES.values():
        assert u.boss in SPECIES
        spec = SPECIES[u.boss]
        assert spec.is_boss is True
        assert spec.drops_sample == "probe_kern"


def test_c14_agents_evil_selves_and_ober_cloita() -> None:
    from src.enemies import SPECIES

    for k in (
        "agent_streife",
        "agent_sachbearbeiter",
        "agent_drohne",
        "agent_vollstrecker",
        "agent_abteilungsleiter",
        "boese_kaiserin",
        "boese_gute",
        "boese_omega",
        "ober_cloita",
    ):
        assert k in SPECIES


def test_c15_creature_projectile_status_effects() -> None:
    from src.enemies import EnemyManager
    from src.player import Player
    from src.projectiles import Projectile, update_projectiles
    from src.world import World

    w = World(80, 80)
    p = Player(40.0, 40.0)
    em = EnemyManager()

    p1 = Projectile(
        x=p.x,
        y=p.y,
        vx=0.0,
        vy=0.0,
        damage=2.0,
        from_player=False,
        owner_species="agent_sachbearbeiter",
    )
    update_projectiles([p1], 0.016, w, p, em, [], [])
    assert p.body.stamped_bad >= 5.0

    p2 = Projectile(
        x=p.x, y=p.y, vx=0.0, vy=0.0, damage=2.0, from_player=False, owner_species="harzspucker"
    )
    update_projectiles([p2], 0.016, w, p, em, [], [])
    assert p.body.sticky >= 3.0


def test_c16_creature_death_drops_and_split_in_run() -> None:
    from src.run import Run

    run = Run(seed=16)
    run.enemies.creatures.clear()
    run.pickups.clear()

    c = run.enemies.spawn("glibberteiler", run.player.x + 25.0, run.player.y)
    c.body.hp = 0.0
    run.update(0.016, None)

    assert any(p.kind == "gold" for p in run.pickups)
    splits = [cr for cr in run.enemies.creatures if cr.species == "glibberteiler"]
    assert len(splits) == 2
    assert all(cr.generation == 1 for cr in splits)


def test_c17_elemental_weakness_and_resistance() -> None:
    from src.enemies import SPECIES

    assert SPECIES["sporenwerfer"].weak_material == "fire"
    assert SPECIES["saeurespucker"].resist_material == "acid"
