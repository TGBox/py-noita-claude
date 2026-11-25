"""Phase U performance budget benchmark for Phase 3 generators and runtime loops."""

from __future__ import annotations

import random
import time

from src import materials as mat
from src.authority import Wanted
from src.bosses.cloita_null import CloitaNullBoss
from src.gadgets import GadgetManager
from src.player import Player
from src.tv_engine import TVEngine
from src.universes.catalog_phase3 import PHASE3_GENERATORS, PHASE3_UNIVERSES
from src.world import World


def test_u05_phase3_worldgen_and_subsystems_within_budget() -> None:
    start = time.perf_counter()
    world = World(96, 72)
    rng = random.Random(9001)
    try:
        for u in PHASE3_UNIVERSES:
            PHASE3_GENERATORS[u.key](world, rng, 1)
    finally:
        mat.activate(mat.DEFAULT_SET)

    player = Player(40, 40)
    gadgets = GadgetManager()
    gadgets.equip("gadget_amts_imp", player)
    gadgets.activate(player)
    tv = TVEngine()
    tv.turn_on()
    wanted = Wanted()
    wanted.apply_patent_alibi()
    boss = CloitaNullBoss()

    for _ in range(100):
        gadgets.update(0.016, player, wanted=wanted)
        tv.step(0.016, player)
        wanted.step_alibi(0.016)
        boss.step(0.016)

    elapsed = time.perf_counter() - start
    assert elapsed < 3.0, f"Phase 3 benchmark too slow: {elapsed:.2f}s"
