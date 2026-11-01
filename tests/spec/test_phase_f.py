from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

pygame.init()


def test_f01_authority_wanted_and_agent_species() -> None:
    from src.authority import Wanted, agent_species_for_stars

    w = Wanted()
    assert w.stars == 0
    assert w.on_cells_destroyed(1000) is True
    assert w.level == pytest.approx(0.5)
    w.add(2.0, "Händler angegriffen")
    assert w.stars == 2
    assert len(agent_species_for_stars(w.stars)) == 2
    w.on_workshop()
    assert w.level == pytest.approx(2.0)


def test_f02_authority_crimes_and_agent_spawns_in_run() -> None:
    from src.authority import spawn_agents
    from src.run import Run

    run = Run(seed=2)
    run.wanted.add(2.0, "Test")
    spawned = spawn_agents(run)
    assert len(spawned) == 2


def _check_boss_script(species: str) -> None:
    from src.bosses import make_boss_script
    from src.enemies import EnemyManager
    from src.run import Run

    run = Run(seed=3)
    em = EnemyManager()
    boss = em.spawn(species, 100.0, 100.0)
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


def test_f03_boss_script_framework() -> None:
    from src.universes.catalog import UNIVERSES

    first_boss = next(iter(UNIVERSES.values())).boss
    _check_boss_script(first_boss)


def test_f04_boss_scripts_pack1() -> None:
    for k in ("weltenherz", "dj_myzel"):
        _check_boss_script(k)


def test_f05_boss_scripts_pack2() -> None:
    for k in ("oberstempler", "abt_kieme"):
        _check_boss_script(k)


def test_f06_boss_scripts_pack3_and_all_mvp_bosses() -> None:
    from src.universes.catalog import UNIVERSES

    for u in UNIVERSES.values():
        _check_boss_script(u.boss)


def test_f07_evil_selves_and_signature_wands() -> None:
    from src.bosses.evil_selves import (
        EVIL_SELVES,
        evil_self_for_depth,
        signature_wand_for_evil_self,
    )

    assert evil_self_for_depth(2) == "boese_kaiserin"
    assert evil_self_for_depth(3) == "boese_gute"
    assert evil_self_for_depth(4) == "boese_omega"
    for sp in EVIL_SELVES:
        wand = signature_wand_for_evil_self(sp)
        assert len(wand.blocks) >= 2


def test_f08_empress_bargain_in_run() -> None:
    from src.bosses.evil_selves import apply_empress_bargain
    from src.run import Run

    run = Run(seed=8)
    max_hp_before = run.player.body.max_hp
    apply_empress_bargain(run, accepted=True)
    assert run.gold >= 100
    assert run.wanted.level >= 2.0
    assert run.player.body.max_hp < max_hp_before


def test_f09_headquarters_controller_and_ober_cloita() -> None:
    from src.bosses.headquarters import HQ_STAGES, can_enter_headquarters
    from src.run import Run

    assert HQ_STAGES == ("anhoerung", "boese_ichs", "ober_cloita")
    run = Run(seed=9)
    assert not can_enter_headquarters(run)
    run.badges = 3
    assert can_enter_headquarters(run)


def test_f10_enter_headquarters_in_run() -> None:
    from src.run import Run

    run = Run(seed=10)
    run.badges = 3
    run.enter_headquarters()
    assert run.in_headquarters is True


def test_f11_klonita_lines_database() -> None:
    from src.klonita_lines import LINES, line_for
    from src.universes.catalog import UNIVERSES

    for u in UNIVERSES.values():
        topic = f"enter_{u.key}"
        assert topic in LINES
        assert isinstance(line_for(topic, random.Random(1)), str)


def test_f12_klonita_fsm_and_auto_triggers() -> None:
    from src.klonita import AUTO_TRIGGERS, Klonita
    from src.run import Run

    assert len(AUTO_TRIGGERS) == 5
    run = Run(seed=12)
    k = Klonita(x=run.player.x, y=run.player.y)
    assert k.toggle() == "dismissed"
    msg = k.on_trigger("player_low_hp", run)
    assert msg is not None and k.state == "follow"

    assert k.take_damage(999.0) is True
    assert k.state == "knocked"
    k.update(5.2, run)
    assert k.state == "follow" and k.hp == k.max_hp


def test_f13_klonita_assists_and_quirks() -> None:
    from src.klonita import Klonita
    from src.run import Run

    run = Run(seed=13)
    k = Klonita(x=run.player.x, y=run.player.y)
    run.inventory.add_sample("probe_gallenstein", 6)
    assert k.trigger_quirk("sample_nibble", run) is True
    assert k.quirk_used_in_universe is True
    assert k.trigger_quirk("sample_nibble", run) is False


def test_f14_klonita_and_speech_bubbles_in_run() -> None:
    from src.run import Run

    run = Run(seed=14)
    run.say("Klonita", "Hallo!", run.player.x, run.player.y)
    assert len(run.bubbles) >= 1
