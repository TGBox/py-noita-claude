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

    # Snack: +15 HP below 35 %, 45 s cooldown, never during a boss fight.
    run.enemies.creatures.clear()
    run.boss_script = None
    run.player.body.hp = run.player.body.max_hp * 0.30
    hp_before = run.player.body.hp
    k.update(0.016, run)
    assert run.player.body.hp == hp_before + 15.0
    assert k.cooldowns["snack"] == 45.0

    k.cooldowns["snack"] = 0.0
    run.boss_script = object()
    hp_before = run.player.body.hp
    k.update(0.016, run)
    assert run.player.body.hp == hp_before


def test_f14_klonita_and_speech_bubbles_in_run() -> None:
    from src.run import Run

    run = Run(seed=14)
    run.say("Klonita", "Hallo!", run.player.x, run.player.y)
    assert len(run.bubbles) >= 1


# ---------------------------------------------------------------------------
# F15–F17 — Klonitas Bibel-Aktionen & Macken (V21 Abschnitte 2b und 3)
# ---------------------------------------------------------------------------
def _with_stance(creature, stance: str):
    import dataclasses

    creature.spec = dataclasses.replace(creature.spec, stance=stance)
    return creature


def test_f15_calmed_creatures_and_dodge_charges() -> None:
    from src.enemies import EnemyManager, evaluate_stance
    from src.player import Player

    em = EnemyManager()
    c = em.spawn("made", 40.0, 40.0)
    assert c.calmed == 0.0 and c.dodge_charges == 0
    p = Player(42.0, 40.0)
    c.aggro = False
    assert evaluate_stance(c, p, em.creatures, stance_override="territorial")
    c.aggro = False
    c.calmed = 1.0
    assert not evaluate_stance(c, p, em.creatures, stance_override="territorial")
    c.aggro = True
    assert evaluate_stance(c, p, em.creatures, stance_override="territorial")


def test_f16_klonita_point_carry_hug() -> None:
    import dataclasses

    from src.klonita import Klonita
    from src.loot import Pickup
    from src.run import Run

    run = Run(seed=16)
    run.enemies.creatures.clear()
    run.pickups.clear()
    run.level = dataclasses.replace(run.level, secret=None)
    k = Klonita(x=run.player.x, y=run.player.y)

    run.pickups.append(Pickup(run.player.x + 100.0, run.player.y, kind="life_capsule"))
    assert k.helper_point(run) == (run.player.x + 100.0, run.player.y)
    assert k.pointing is not None and k.cooldowns["point"] == 60.0
    assert k.helper_point(run) is None

    run.pickups.clear()
    high = Pickup(run.player.x + 30.0, run.player.y - 90.0, kind="block", item_key="funke")
    run.pickups.append(high)
    assert k.helper_carry(run) is high
    assert (high.x, high.y) == (run.player.x, run.player.y)
    assert k.cooldowns["carry"] == 30.0

    calm = _with_stance(run.enemies.spawn("made", k.x + 30.0, k.y), "neutral")
    wild = _with_stance(run.enemies.spawn("made", k.x - 30.0, k.y), "hostile")
    assert k.helper_hug(run) == 1
    assert calm.calmed > 0.0 and wild.calmed == 0.0


def test_f17_klonita_tip_feed_warn() -> None:
    from src.klonita import QUIRKS, Klonita
    from src.run import Run

    assert len(QUIRKS) == 6
    run = Run(seed=17)
    run.enemies.creatures.clear()
    k = Klonita(x=run.player.x, y=run.player.y)

    _with_stance(run.enemies.spawn("made", k.x + 20.0, k.y), "trader")
    run.gold = 100
    assert k.trigger_quirk("tip_trader", run) is True
    assert 85 <= run.gold <= 95
    _with_stance(run.enemies.spawn("made", k.x + 10.0, k.y), "passive")
    assert k.trigger_quirk("feed_creature", run) is False  # only one quirk per universe

    k.quirk_used_in_universe = False
    run.enemies.creatures.clear()
    pet = _with_stance(run.enemies.spawn("made", k.x + 10.0, k.y), "passive")
    pet.hp = pet.max_hp * 0.5
    assert k.trigger_quirk("feed_creature", run) is True
    assert pet.hp == pytest.approx(pet.max_hp * 0.7)

    k.quirk_used_in_universe = False
    run.enemies.creatures.clear()
    foe = _with_stance(run.enemies.spawn("made", k.x + 60.0, k.y), "hostile")
    assert k.trigger_quirk("warn_enemy", run) is True
    assert foe.dodge_charges == 1
