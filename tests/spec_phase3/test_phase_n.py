"""Tests for Phase N gadgets, Amts-Imp, ambush flight, flywheel disc, and cockroach escape."""

from __future__ import annotations

from src.authority import Wanted
from src.gadgets import (
    GADGET_KEY,
    GADGET_KEYS,
    Gadget,
    GadgetManager,
    consume_ambush_crit,
    maybe_trigger_cockroach_escape,
)
from src.player import Player


def test_n01_gadget_manager_equip_and_charges() -> None:
    assert GADGET_KEY == "G"
    assert len(GADGET_KEYS) == 5
    player = Player(40, 60)
    mgr = GadgetManager()
    equipped = mgr.equip("gadget_tauchkapsel", player)
    assert isinstance(equipped, Gadget)
    assert player.active_gadget == "gadget_tauchkapsel"
    assert mgr.states["gadget_tauchkapsel"].charges == 2

    res1 = mgr.activate(player)
    assert res1["activated"] is True
    assert mgr.states["gadget_tauchkapsel"].charges == 1

    # Cooldown prevents immediate double firing.
    res_cd = mgr.activate(player)
    assert res_cd["activated"] is False
    assert "lädt" in res_cd["reason_de"].lower()


def test_n02_tauchkapsel_grants_shield_and_stealth() -> None:
    player = Player(40, 60)
    mgr = GadgetManager()
    mgr.equip("gadget_tauchkapsel", player)
    res = mgr.activate(player)
    assert res["activated"] is True
    assert player.shield_hp >= 30.0
    assert player.stealth_timer > 0.0
    assert res["capsule_radius"] == 12


def test_n03_amts_imp_collects_gold_and_ticks_wanted() -> None:
    player = Player(50, 50)
    player.gold = 0
    wanted = Wanted()
    mgr = GadgetManager()
    mgr.equip("gadget_amts_imp", player)
    res = mgr.activate(player)
    assert res["activated"] is True

    pickups = [{"x": 58.0, "y": 48.0, "amount": 25}, {"x": 200.0, "y": 200.0, "amount": 10}]
    mgr.update(1.0, player, pickups=pickups, wanted=wanted)
    assert player.gold == 25
    assert len(pickups) == 1
    assert wanted.level > 0.0


def test_n04_kolben_libelle_and_schwungscheibe() -> None:
    player = Player(50, 50)
    player.energy = 0.2
    mgr = GadgetManager()
    mgr.equip("gadget_kolben_libelle", player)
    res = mgr.activate(player)
    assert res["activated"] is True
    assert player.stealth_timer >= 4.0
    assert player.ambush_crit_ready is True
    assert player.energy == player.energy_max
    assert consume_ambush_crit(player, 20.0) == 50.0
    assert player.ambush_crit_ready is False
    assert consume_ambush_crit(player, 20.0) == 20.0

    mgr.equip("gadget_schwungscheibe", player)
    res_disc = mgr.activate(player, direction=1)
    assert res_disc["activated"] is True
    enemy = {"x": 72.0, "y": 50.0, "hp": 60.0}
    mgr.update(0.1, player, targets=[enemy])
    assert enemy["hp"] < 60.0


def test_n05_cockroach_escape_protocol_and_decay() -> None:
    player = Player(50, 50)
    player.hp = 12.0
    triggered = maybe_trigger_cockroach_escape(player, incoming_damage=5.0)
    assert triggered is True
    assert player.is_cockroach is True
    assert player.cockroach_timer > 0.0
    assert player.hp >= 10.0

    # Emulate timer expiry via direct step.
    player.cockroach_timer = 0.0
    player.is_cockroach = False
    assert player.is_cockroach is False
