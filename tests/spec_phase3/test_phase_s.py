"""Tests for Phase S last 6 satirical universes (S01-S06)."""

from __future__ import annotations

import random

from src import materials as mat
from src.events import ALL_EVENTS
from src.rules import Rule
from src.universes.catalog_phase3 import (
    PHASE3_FACTIONS,
    PHASE3_GENERATORS,
    PHASE3_S_UNIVERSES,
    PHASE3_SAMPLES,
    PHASE3_UNIVERSES,
)
from src.world import World


def test_s01_to_s06_universes_registered_and_complete() -> None:
    assert len(PHASE3_S_UNIVERSES) == 6
    assert len(PHASE3_UNIVERSES) == 12
    assert len(PHASE3_SAMPLES) == 24
    assert len(PHASE3_FACTIONS) == 12

    expected = {
        "klo_paradies",
        "matroschka_simulation",
        "kollektiv_buerokratie",
        "unsterblichkeits_resort",
        "schroedinger_kammer",
        "kater_bunker",
    }
    assert {u.key for u in PHASE3_S_UNIVERSES} == expected

    for u in PHASE3_S_UNIVERSES:
        assert u.ready is True
        assert len(u.natives) == 4
        assert u.event in ALL_EVENTS
        assert u.material_set in mat.SETS
        assert len(mat.SETS[u.material_set].keys()) <= 21
        assert u.sample_key in PHASE3_SAMPLES
        for rank in (1, 2, 3):
            rule = Rule.make(u.rule, rank)
            assert rule.rank == rank
            assert rule.name_de != "Keine Regel"


def test_s_universes_generate_valid_worlds_and_respect_healing_rule() -> None:
    heilquell = mat.LIBRARY["heilquell_wasser"]
    assert "keine lebenspunkte" in heilquell.description_de.lower()

    world = World(96, 72)
    rng = random.Random(3033)
    try:
        for u in PHASE3_S_UNIVERSES:
            lvl = PHASE3_GENERATORS[u.key](world, rng, 2)
            assert lvl.universe_key == u.key
            assert len(lvl.regions) == 3
            assert lvl.boss_arena is not None
    finally:
        mat.activate(mat.DEFAULT_SET)
