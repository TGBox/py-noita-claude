"""Universe rules (work package T4): every MVP rule measurably does its thing."""

import unittest
from dataclasses import replace

from src import materials as mat
from src.body import ENEMY_TEAM, PLAYER_TEAM, Body
from src.player import Player
from src.rules import RANK_PARAMS, RULE_KEYS, Rule
from src.run import Controls, Run
from src.spells import CATALOG
from src.wand import Shot
from src.world import World


def _run_with_rule(rule: str, depth_index: int = 0, material_set: str = "koerper") -> Run:
    run = Run(seed=5)
    route = list(run.route)
    route[depth_index] = replace(route[depth_index], rule=rule, material_set=material_set)
    run.route = tuple(route)
    run.enter_depth(depth_index)
    return run


class RuleCase(unittest.TestCase):
    def tearDown(self) -> None:
        Body.gravity_scale = 1.0
        mat.activate(mat.DEFAULT_SET)


class TestRuleData(RuleCase):
    def test_six_rules_with_three_ranks_each(self) -> None:
        self.assertEqual(len(RULE_KEYS), 6)
        for key in RULE_KEYS:
            self.assertEqual(len(RANK_PARAMS[key]), 3)
            self.assertEqual(Rule.make(key, 9).rank, 3)
            self.assertEqual(Rule.make(key, 0).rank, 1)
        with self.assertRaises(ValueError):
            Rule.make("rule_gibtsnicht")
        self.assertEqual(Rule.make("").cast_factor(), 1.0)

    def test_rank_follows_the_depth(self) -> None:
        run = Run(seed=1)
        ranks = []
        for index in range(len(run.route)):
            run.depth_index = index
            ranks.append(run.rank)
        self.assertEqual(ranks[0], 1)
        self.assertEqual(ranks[-1], 3)
        self.assertEqual(sorted(ranks), ranks)


class TestLivingWalls(RuleCase):
    def _regrown(self, rank: int) -> int:
        run = _run_with_rule("rule_living_walls")
        run.rule = Rule.make("rule_living_walls", rank)
        world = run.world
        flesh = mat.FLESH
        world.reset()
        for y in range(100, 200):  # a block of flesh with a slot cut into it
            for x in range(300, 500):
                if not (380 <= x < 420 and 120 <= y < 180):
                    world.set_cell(x, y, flesh)
        run.player.place(40, 40)
        hole = sum(1 for y in range(120, 180) for x in range(380, 420) if world.get(x, y) == flesh)
        for _ in range(240):
            run.rule.update(run, 1 / 60, (280, 80, 520, 220))
        after = sum(1 for y in range(120, 180) for x in range(380, 420) if world.get(x, y) == flesh)
        return after - hole

    def test_holes_close_and_faster_on_higher_ranks(self) -> None:
        slow, fast = self._regrown(1), self._regrown(3)
        self.assertGreater(slow, 0)
        self.assertGreater(fast, slow)

    def test_never_grows_into_the_player(self) -> None:
        run = _run_with_rule("rule_living_walls")
        run.rule = Rule.make("rule_living_walls", 3)
        world = run.world
        world.reset()
        px, py = 200, 200
        for y in range(py - 30, py + 30):
            for x in range(px - 30, px + 30):
                if abs(x - px) > 16 or abs(y - py) > 16:
                    world.set_cell(x, y, mat.FLESH)
        run.player.place(px - 3, py - 8)
        for _ in range(600):
            run.rule.update(run, 1 / 60, (px - 40, py - 40, px + 40, py + 40))
        player = run.player
        inside = [
            world.get(x, y)
            for y in range(player.y, player.y + player.height)
            for x in range(player.x, player.x + player.width)
        ]
        self.assertNotIn(mat.FLESH, inside)


class TestPaperwork(RuleCase):
    def test_paper_burns_better_per_rank_and_saves(self) -> None:
        base = mat.LIBRARY["papier"].flammability
        for rank, factor in ((1, 1.5), (2, 2.0), (3, 3.0)):
            derived = Rule.make("rule_paperwork", rank).material_set(mat.AKTENHALDE)
            mat.activate(derived)
            self.assertAlmostEqual(
                mat.FLAMMABILITY[mat.id_of("papier")], min(1.0, base * factor)
            )
        run = _run_with_rule("rule_paperwork", 0, "aktenhalde")
        self.assertEqual(run.world.material_set, "aktenhalde+rule_paperwork1")
        self.assertAlmostEqual(mat.FLAMMABILITY[mat.id_of("papier")], base * 1.5)
        saved = run.save_state()
        mat.activate(mat.KOERPER)
        other = Run(seed=2)
        other.route = run.route
        other.restore(saved)
        self.assertEqual(other.world.material_set, "aktenhalde+rule_paperwork1")


class TestBounce(RuleCase):
    def _bounces(self, run: Run, team: str) -> int:
        run.projectiles.clear()
        run.projectiles._pending.clear()
        shot = Shot(CATALOG["funke"], [])
        run.projectiles.spawn([shot], 100, 100, 0.0, team)
        return run.projectiles._pending[-1].bounces

    def test_shots_bounce_more(self) -> None:
        plain = Run(seed=5)
        normal = self._bounces(plain, PLAYER_TEAM)
        run = _run_with_rule("rule_bounce")
        self.assertEqual(self._bounces(run, PLAYER_TEAM), normal + 2)
        self.assertEqual(self._bounces(run, ENEMY_TEAM), normal)
        run.rule = Rule.make("rule_bounce", 3)
        run.projectiles.bounce_bonus = {PLAYER_TEAM: 4, ENEMY_TEAM: run.rule.bounce_bonus(True)}
        self.assertEqual(self._bounces(run, ENEMY_TEAM), normal + 2)


class TestTiny(RuleCase):
    def test_bodies_fall_at_half_speed(self) -> None:
        def fall(scale: float) -> float:
            Body.gravity_scale = scale
            world = World(200, 400, seed=1)
            player = Player(100, 20)
            for _ in range(20):
                player.update(world, 1 / 60, 0, False, False)
            return player.vy

        normal, tiny = fall(1.0), fall(0.5)
        self.assertAlmostEqual(tiny / normal, 0.5, places=2)

    def test_run_applies_gravity_to_bodies_and_shots(self) -> None:
        run = _run_with_rule("rule_tiny")
        self.assertEqual(Body.gravity_scale, 0.5)
        self.assertEqual(run.projectiles.gravity_scale, 0.5)
        run.enter_sanctum()
        self.assertEqual(Body.gravity_scale, 1.0)


class TestBeat(RuleCase):
    def test_beats_and_bonus_on_the_beat(self) -> None:
        run = _run_with_rule("rule_beat")
        rule = run.rule
        beats = 0
        for _ in range(121):  # just over 2 s at 0.5 s per beat
            run.events = []
            rule.update(run, 1 / 60, None)
            beats += run.events.count("beat")
        self.assertEqual(beats, 4)
        rule.beat_time = 0.02
        self.assertAlmostEqual(rule.cast_factor(), 1.25)
        rule.beat_time = 0.25
        self.assertEqual(rule.cast_factor(), 1.0)
        self.assertGreater(Rule(**{**rule.__dict__, "beat_time": 0.0}).light_factor(), 1.0)
        self.assertAlmostEqual(Rule.make("rule_beat", 3).params["period"], 0.33)


class TestFlooded(RuleCase):
    def test_breath_runs_out_under_water_and_refills_in_the_air(self) -> None:
        run = _run_with_rule("rule_flooded")
        world, player = run.world, run.player
        world.reset()
        x, y = 300, 300
        for yy in range(y - 30, y + 30):
            for xx in range(x - 30, x + 30):
                world.set_cell(xx, yy, mat.BLOOD)
        player.place(x, y)
        player.hp = player.max_hp
        rule = run.rule
        for _ in range(16 * 60):
            rule.update(run, 1 / 60, None)
        self.assertEqual(rule.breath, 0.0)
        hp = player.hp
        rule.update(run, 0.5, None)
        self.assertLess(player.hp, hp)  # drowning
        player.place(100, 100)
        rule.update(run, 1.0, None)
        self.assertGreater(rule.breath, 0.0)
        self.assertEqual(Rule.make("rule_flooded", 3).max_breath, 8.0)

    def test_rule_runs_inside_the_normal_update(self) -> None:
        run = _run_with_rule("rule_flooded")
        run.rule.breath = 3.0
        run.update(1 / 60, Controls())
        self.assertGreater(run.rule.breath, 3.0)  # spawn is dry: breath refills


if __name__ == "__main__":
    unittest.main()
