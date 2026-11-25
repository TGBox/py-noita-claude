"""Phase M03 Performance & Parallel World Transition Stability Audit."""

from __future__ import annotations

import random
import time

from src import materials as mat
from src.body import Body
from src.parallel_worlds import ParallelWorldManager
from src.projectiles import MAX_PROJECTILES, ProjectileSystem
from src.universes.catalog_expansion import EXPANSION_GENERATORS, EXPANSION_UNIVERSES
from src.wand import Wand, WandSpec
from src.world import World


def test_m03_parallel_world_transitions_and_projectile_budget_performance() -> None:
    try:
        world = World(240, 140, seed=9)
        mgr = ParallelWorldManager()
        bodies = [Body(40, 40, 8, 12, 100.0) for _ in range(5)]

        t0 = time.perf_counter()
        for step in range(4):
            state = mgr.enter_parallel(42, 1 if step % 2 == 0 else -1, world, bodies)
            assert state.parallel_klonita is not None
        # Also verify every expansion universe generator stays crisp
        for u in EXPANSION_UNIVERSES:
            EXPANSION_GENERATORS[u.key](world, random.Random(3), 3)
        elapsed_gen = time.perf_counter() - t0
        assert elapsed_gen < 3.0

        # Mass larpa + split cascade stays capped at <= MAX_PROJECTILES
        mat.activate(mat.DEFAULT_SET)
        w = Wand(WandSpec("Perf", ("split_dekade", "mod_larpa_chaos", "sporenball"), mana_max=2000.0))
        ps = ProjectileSystem()
        ps.spawn(w.cast(), 120.0, 70.0, 0.0)
        t1 = time.perf_counter()
        for _ in range(90):
            ps.update(world, 1 / 60, (200.0, 70.0), ())
            assert len(ps.items) <= MAX_PROJECTILES
        elapsed_sim = time.perf_counter() - t1
        assert elapsed_sim < 2.0
    finally:
        mat.activate(mat.DEFAULT_SET)
