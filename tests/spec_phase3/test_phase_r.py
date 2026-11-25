"""Tests for Phase R first 6 satirical universes (R01-R06)."""

from __future__ import annotations

import random

from src import materials as mat
from src.events import ALL_EVENTS, EVENTS
from src.rules import RULE_KEYS, Rule
from src.universes.catalog import UNIVERSES
from src.universes.catalog_phase3 import (
    PHASE3_GENERATORS,
    PHASE3_R_UNIVERSES,
    PHASE3_SAMPLES,
)
from src.world import World


def test_r01_to_r06_universes_registered_and_mvp_untouched() -> None:
    assert len(UNIVERSES) == 6
    assert len(RULE_KEYS) == 6
    assert len(EVENTS) == 6
    assert len(PHASE3_R_UNIVERSES) == 6

    expected = {
        "anatomie_park",
        "pastell_hoelle",
        "klonenberg_welt",
        "talent_kosmos",
        "antrags_labyrinth",
        "krawatten_planet",
    }
    assert {u.key for u in PHASE3_R_UNIVERSES} == expected

    for u in PHASE3_R_UNIVERSES:
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


def test_r_universes_generate_valid_worlds_without_healing_exploit() -> None:
    # Ensure erdbeernektar is strictly non-healing.
    nectar = mat.LIBRARY["erdbeernektar"]
    assert "heilt nie" in nectar.description_de.lower()

    world = World(96, 72)
    rng = random.Random(2026)
    try:
        for u in PHASE3_R_UNIVERSES:
            lvl = PHASE3_GENERATORS[u.key](world, rng, 1)
            assert lvl.universe_key == u.key
            assert len(lvl.regions) == 3
            assert lvl.spawn != lvl.exit
    finally:
        mat.activate(mat.DEFAULT_SET)
