"""Universes as data and the run plan through them (work package T3)."""

import itertools
import unittest

from src import materials as mat
from src.universes import BY_KEY, EVIL_SELVES, MID_BOSSES, UNIVERSES, RunPlan
from src.universes.model import SHAPES
from src.universes.plan import SLOTS


def _all_paths(plan_seed: int):
    """Every complete sequence of portal choices for one seed (depth-first)."""

    def walk(chosen: list[str]):
        plan = RunPlan(plan_seed)
        for key in chosen:
            plan.choose(key)
        if plan.finished:
            yield plan
            return
        offers = plan.offers()
        assert offers, f"seed {plan_seed}: dead end after {chosen}"
        for offer in offers:
            yield from walk([*chosen, offer.universe])

    yield from walk([])


class TestCatalog(unittest.TestCase):
    def test_six_mvp_universes_with_their_fields(self) -> None:
        self.assertEqual(len(UNIVERSES), 6)
        rules = set()
        for universe in UNIVERSES:
            self.assertIn(universe.shape, SHAPES)
            self.assertIn(universe.material_set, mat.SETS)
            self.assertTrue(universe.pitch_de and universe.name_de)
            self.assertGreaterEqual(len(universe.regions), 2)
            self.assertEqual(len(universe.samples), 2)
            self.assertTrue(0.0 < universe.ambient <= 1.0)
            rules.add(universe.rule)
        self.assertEqual(len(rules), 6)  # one main rule each, all different

    def test_world_sizes_follow_the_shapes(self) -> None:
        self.assertEqual(BY_KEY["aktenhalde"].size, (3072, 1024))
        self.assertEqual(BY_KEY["abtei"].size, (1280, 2560))
        self.assertEqual(BY_KEY["fleischwelt"].size, (2048, 1536))
        self.assertEqual(BY_KEY["glibbria"].size, (2560, 1280))

    def test_every_mid_boss_has_a_home_universe(self) -> None:
        homes = [home for rank in MID_BOSSES.values() for _, home in rank]
        self.assertEqual(sorted(homes), sorted(BY_KEY))
        self.assertEqual(set(MID_BOSSES), {1, 2, 3})


class TestRunPlan(unittest.TestCase):
    def test_every_choice_path_visits_six_universes_once_with_correct_ranks(self) -> None:
        for seed in range(12):
            for plan in _all_paths(seed):
                self.assertEqual(sorted(plan.visited), sorted(BY_KEY))
                ranks = [offer.rank for offer in plan.chosen]
                self.assertEqual(ranks, [1, 1, 2, 2, 3, 3])
                for index, offer in enumerate(plan.chosen):
                    if index % 2:  # boss slot: the rank's boss in its home
                        self.assertIn((offer.boss, offer.universe), MID_BOSSES[offer.rank])
                    else:
                        self.assertIsNone(offer.boss)
                bosses = [o.boss for o in plan.chosen if o.boss]
                self.assertEqual(len(bosses), 3)

    def test_free_slots_offer_two_universes_where_possible(self) -> None:
        plan = RunPlan(3)
        self.assertEqual(len(plan.offers()), 2)
        self.assertFalse(plan.boss_slot)
        plan.choose(0)
        self.assertTrue(plan.boss_slot)
        for offer in plan.offers():
            self.assertIsNotNone(offer.boss)

    def test_choosing_a_boss_home_on_a_free_slot_moves_the_fight(self) -> None:
        for seed in range(40):
            plan = RunPlan(seed)
            first = plan.offers()
            home = next((o for o in first if o.universe in ("aktenhalde", "glibbria")), None)
            if home is None:
                continue
            plan.choose(home.universe)
            self.assertIsNone(plan.current.boss)  # no fight there
            boss_offers = plan.offers()
            self.assertEqual(len(boss_offers), 1)
            self.assertNotEqual(boss_offers[0].universe, home.universe)
            return
        self.fail("no seed offered a rank-1 home first")

    def test_offers_are_stable_for_the_same_seed(self) -> None:
        a, b = RunPlan(77), RunPlan(77)
        for _ in range(SLOTS):
            self.assertEqual(a.offers(), b.offers())
            a.choose(0)
            b.choose(0)
        self.assertTrue(a.finished)
        self.assertEqual(a.offers(), [])
        self.assertIn(a.evil_self, EVIL_SELVES)

    def test_seeds_vary_the_route(self) -> None:
        firsts = {tuple(o.universe for o in RunPlan(seed).offers()) for seed in range(30)}
        self.assertGreater(len(firsts), 5)
        selves = {RunPlan(seed).evil_self for seed in range(30)}
        self.assertEqual(selves, set(EVIL_SELVES))

    def test_save_and_replay(self) -> None:
        plan = RunPlan(9)
        for _ in range(3):
            plan.choose(len(plan.offers()) - 1)
        again = RunPlan.from_data(plan.to_data())
        self.assertEqual(again.visited, plan.visited)
        self.assertEqual(again.offers(), plan.offers())
        with self.assertRaises(ValueError):
            RunPlan.from_data({"seed": 9, "pool": list(BY_KEY), "chosen": ["gibtsnicht"]})
        with self.assertRaises(ValueError):
            RunPlan.from_data({"chosen": []})

    def test_invalid_choices_and_pools_are_refused(self) -> None:
        plan = RunPlan(1)
        with self.assertRaises(ValueError):
            plan.choose(5)
        with self.assertRaises(ValueError):
            RunPlan(1, pool=("fleischwelt", "aktenhalde"))

    def test_a_bigger_pool_still_works(self) -> None:
        pool = (*BY_KEY, "extra_a", "extra_b")
        counts = itertools.count()
        for seed in range(5):
            plan = RunPlan(seed, pool=pool)
            while not plan.finished:
                plan.choose(next(counts) % len(plan.offers()))
            self.assertEqual(len(set(plan.visited)), 6)


if __name__ == "__main__":
    unittest.main()
