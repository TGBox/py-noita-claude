"""Phase M02 Alchemy & Shift Verification across all 12 material sets."""

from __future__ import annotations

import random

from src import materials as mat
from src.alchemy_advanced import Cauldron, SecretAlchemyEngine
from src.reality_shift import MAX_SHIFTS_PER_RUN, SHIFT_COOLDOWN, RealityShiftManager
from src.world import World


def test_m02_alchemy_budget_and_shift_integrity_across_sets() -> None:
    try:
        for set_key, mset in mat.SETS.items():
            mat.validate(mset)
            mat.activate(mset)
            assert mat.MATERIAL_COUNT <= mat.MAX_MATERIALS, set_key

            recipes = SecretAlchemyEngine.recipes_for_seed(1234, mat.KEYS)
            assert set(recipes.schutztonikum_zutaten).issubset(set(mat.KEYS))
            assert set(recipes.midas_schmelze_zutaten).issubset(set(mat.KEYS))

            cauldron = Cauldron()
            for ing in recipes.midas_schmelze_zutaten:
                assert cauldron.add_reagent(ing, 25)
            cauldron.ignite()
            assert cauldron.update(5.1, recipes) == "gold_vein"

            world = World(40, 40, seed=1)
            mgr = RealityShiftManager()
            src_mat = next(k for k in mat.KEYS if k not in ("air", "bedrock"))
            dst_mat = next(k for k in mat.KEYS if k not in ("air", "bedrock", src_mat))
            world.fill_rect(10, 10, 16, 16, mat.MAT_ID[src_mat])
            rec = mgr.trigger_shift(
                world,
                random.Random(1),
                active_keys=mat.KEYS,
                elapsed_time=0.0,
                source_override=src_mat,
                target_override=dst_mat,
            )
            assert rec is not None and world.count(mat.MAT_ID[src_mat]) == 0
            assert len(mgr.shifts) <= MAX_SHIFTS_PER_RUN
            assert mgr.can_shift(SHIFT_COOLDOWN - 1.0) is False
    finally:
        mat.REALITY_ALIASES.clear()
        mat.activate(mat.DEFAULT_SET)
