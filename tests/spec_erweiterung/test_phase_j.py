"""Phase J Spec Tests (J01-J08): 6 Expansion Universes, Secondary Events & Electricity Puzzle."""

from __future__ import annotations

import json
import random
from pathlib import Path

from src import materials as mat
from src.events import ALL_EVENTS, EVENTS, EXPANSION_EVENTS, SECONDARY_EVENT_KEYS
from src.minigames.physik_o_mat import (
    ALL_PUZZLE_KEYS,
    EXPANSION_PUZZLE_KEYS,
    PUZZLE_KEYS,
    make_physik_puzzle,
    solve_actions,
)
from src.rules import EXPANSION_RULE_KEYS, RULE_KEYS, Rule
from src.universes.catalog import UNIVERSES
from src.universes.catalog_expansion import (
    EXPANSION_ACTIVE,
    EXPANSION_BY_KEY,
    EXPANSION_GENERATORS,
    EXPANSION_SAMPLES,
    EXPANSION_UNIVERSES,
    combined_universes,
)
from src.world import World
from tools.sprites_creatures_expansion import build_expansion_creature_sheets


def test_j01_to_j06_expansion_universes_materials_rules_and_generation() -> None:
    try:
        assert EXPANSION_ACTIVE is True
        assert len(UNIVERSES) == 6  # MVP unchanged
        assert len(EXPANSION_UNIVERSES) == 6
        assert len(combined_universes(True)) == 12
        assert len(RULE_KEYS) == 6  # MVP unchanged
        assert len(EXPANSION_RULE_KEYS) == 6

        for u in EXPANSION_UNIVERSES:
            assert u.key in EXPANSION_BY_KEY
            assert u.material_set in mat.SETS
            mset = mat.SETS[u.material_set]
            mat.validate(mset)
            mat.activate(mset)
            assert mat.MATERIAL_COUNT <= mat.MAX_MATERIALS
            assert u.event in ALL_EVENTS and u.event in EXPANSION_EVENTS
            assert all(sk in EXPANSION_SAMPLES for sk in u.samples)

            r1, r2, r3 = Rule.make(u.rule, 1), Rule.make(u.rule, 2), Rule.make(u.rule, 3)
            assert (r1.rank, r2.rank, r3.rank) == (1, 2, 3)

            world = World(160, 120, seed=7)
            lvl = EXPANSION_GENERATORS[u.key](world, random.Random(7), 2)
            assert lvl.universe_key == u.key
            assert lvl.spawn != lvl.exit
            assert not world.rect_blocked(lvl.spawn[0], lvl.spawn[1], 8, 14)
    finally:
        mat.activate(mat.DEFAULT_SET)


def test_j01_to_j06_expansion_sprites(tmp_path: Path) -> None:
    created = build_expansion_creature_sheets(tmp_path)
    assert len(created) == (24 + 12) * 2
    for jpath in (p for p in created if p.suffix == ".json"):
        meta = json.loads(jpath.read_text(encoding="utf-8"))
        assert "idle" in meta["anims"] and "walk" in meta["anims"]


def test_j07_secondary_events_registered() -> None:
    assert len(EVENTS) == 6  # MVP invariant kept intact
    assert len(SECONDARY_EVENT_KEYS) == 8
    for key in SECONDARY_EVENT_KEYS:
        spec = EXPANSION_EVENTS[key]
        assert spec.duration > 0 and spec.name


def test_j08_electricity_water_puzzle_solvable_and_not_idle() -> None:
    assert "electricity_water" in EXPANSION_PUZZLE_KEYS
    assert "electricity_water" in ALL_PUZZLE_KEYS
    assert "electricity_water" not in PUZZLE_KEYS  # MVP invariant kept intact

    idle = make_physik_puzzle("electricity_water", seed=4)
    for _ in range(25):
        idle.step(0.5)
        if idle.finished:
            break
    assert not (idle.finished and idle.result and idle.result.won)

    game = make_physik_puzzle("electricity_water", seed=4)
    for action, cursor in solve_actions("electricity_water"):
        game.on_action(action, cursor)
        game.step(0.25)
    for _ in range(30):
        if game.finished:
            break
        game.step(0.25)
    assert game.finished and game.result and game.result.won
