from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

pygame.init()


def test_f01_and_f02_authority_wanted_and_agents() -> None:
    from src.authority import Wanted, agent_species_for_stars, spawn_agents
    from src.run import Run

    w = Wanted()
    assert w.stars == 0
    assert w.on_cells_destroyed(1000) is True
    assert w.level == pytest.approx(0.5)
    w.add(2.0, "Händler angegriffen")
    assert w.stars == 2
    assert len(agent_species_for_stars(w.stars)) == 2

    w.on_workshop()
    assert w.level == pytest.approx(2.0)

    run = Run(seed=2)
    run.wanted.add(2.0, "Test")
    spawned = spawn_agents(run)
    assert len(spawned) == 2


def test_f03_to_f06_all_9_boss_scripts() -> None:
    from src.bosses import make_boss_script
    from src.enemies import EnemyManager
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    run = Run(seed=6)
    em = EnemyManager()
    for u in UNIVERSES.values():
        boss = em.spawn(u.boss, 100.0, 100.0)
        script = make_boss_script(boss)
        assert script is not None
        assert len(script.phases) == 3

        boss.body.hp = boss.body.max_hp * 0.60
        script.update(0.1, run)
        assert script.phase == 1
        assert script.invuln_timer > 0.0

        script.invuln_timer = 0.0
        boss.body.hp = boss.body.max_hp * 0.25
        script.update(0.1, run)
        assert script.phase == 2


def test_f07_and_f08_evil_selves_and_empress_bargain() -> None:
    from src.bosses.evil_selves import (
        EVIL_SELVES,
        apply_empress_bargain,
        evil_self_for_depth,
        signature_wand_for_evil_self,
    )
    from src.run import Run

    assert evil_self_for_depth(2) == "boese_kaiserin"
    assert evil_self_for_depth(3) == "boese_gute"
    assert evil_self_for_depth(4) == "boese_omega"
    for sp in EVIL_SELVES:
        wand = signature_wand_for_evil_self(sp)
        assert len(wand.blocks) >= 2

    run = Run(seed=8)
    max_hp_before = run.player.body.max_hp
    apply_empress_bargain(run, accepted=True)
    assert run.gold >= 100
    assert run.wanted.level >= 2.0
    assert run.player.body.max_hp < max_hp_before


def test_f09_and_f10_headquarters_and_ober_cloita() -> None:
    from src.bosses.headquarters import HQ_STAGES, can_enter_headquarters
    from src.run import Run

    assert HQ_STAGES == ("anhoerung", "boese_ichs", "ober_cloita")
    run = Run(seed=10)
    assert not can_enter_headquarters(run)
    run.badges = 3
    assert can_enter_headquarters(run)

    run.enter_headquarters()
    assert run.in_headquarters is True


def test_f11_to_f14_klonita_and_speech_bubbles() -> None:
    import random

    from src.klonita import AUTO_TRIGGERS, Klonita
    from src.klonita_lines import LINES, line_for
    from src.run import Run

    assert len(AUTO_TRIGGERS) == 5
    assert "enter_schrott" in LINES
    assert isinstance(line_for("enter_schrott", random.Random(1)), str)

    run = Run(seed=14)
    k = Klonita(x=run.player.x, y=run.player.y)
    assert k.toggle() == "dismissed"
    msg = k.on_trigger("player_low_hp", run)
    assert msg is not None and k.state == "follow"

    assert k.take_damage(999.0) is True
    assert k.state == "knocked"
    k.update(5.2, run)
    assert k.state == "follow" and k.hp == k.max_hp

    run.say("Klonita", "Hallo!", run.player.x, run.player.y)
    assert len(run.bubbles) >= 1
