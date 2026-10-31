import math
import unittest

from src.body import Body
from src.flask import CAPACITY, SIP, Flask, ThrownFlask
from src.materials import ACID, AIR, BLOOD, BONE, MUCUS, TALLOW
from src.run import Controls, Run
from src.world import World

DT = 1 / 60


def pool(world: World, material: int, x0: int, x1: int, y0: int, y1: int) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            world.set_cell(x, y, material)


class TestFlask(unittest.TestCase):
    def test_absorb_takes_one_liquid_up_to_capacity(self) -> None:
        world = World(120, 80, seed=1)
        pool(world, BLOOD, 10, 30, 50, 60)
        pool(world, ACID, 30, 40, 50, 60)
        flask = Flask()
        taken = flask.absorb(world, 30, 55, 10_000)
        self.assertGreater(taken, 0)
        self.assertIn(flask.material, (BLOOD, ACID))
        other = ACID if flask.material == BLOOD else BLOOD
        self.assertEqual(world.count(other), 100)  # the other liquid stays
        self.assertLessEqual(flask.amount, CAPACITY)
        self.assertEqual(flask.absorb(world, 50, 20, 100), 0)  # nothing there

    def test_absorb_ignores_solids(self) -> None:
        world = World(80, 60, seed=1)
        pool(world, BONE, 10, 30, 30, 40)
        self.assertEqual(Flask().absorb(world, 20, 35, 100), 0)

    def test_pour_places_cells_and_empties(self) -> None:
        world = World(120, 80, seed=1)
        flask = Flask(TALLOW, 20)
        placed = 0
        for _ in range(10):
            placed += flask.pour(world, 60, 30, 0.0, 5)
            for _ in range(3):
                world.step()
        self.assertEqual(placed, 20)
        self.assertTrue(flask.empty)
        self.assertIsNone(flask.material)
        self.assertEqual(world.count(TALLOW), 20)

    def test_drinking(self) -> None:
        body = Body(0, 0, 4, 4, 100)
        body.hp = 50
        body.burning = 2.0
        flask = Flask(BLOOD, SIP * 2)
        self.assertTrue(flask.drink(body))
        self.assertGreater(body.hp, 50)
        self.assertEqual(body.burning, 0.0)
        self.assertEqual(flask.amount, SIP)
        acid = Flask(ACID, SIP)
        hp = body.hp
        acid.drink(body)
        self.assertLess(body.hp, hp)
        self.assertTrue(acid.empty)
        self.assertEqual(acid.drink(body), "")

    def test_thrown_flask_shatters_into_a_splash(self) -> None:
        world = World(200, 80, seed=1)
        pool(world, BONE, 150, 160, 2, 78)
        thrown = ThrownFlask.throw(Flask(MUCUS, CAPACITY), 100, 30, -0.1)
        for _ in range(120):
            if thrown.update(world, DT, []):
                break
        self.assertFalse(thrown.alive)
        self.assertGreater(world.count(MUCUS), 100)

    def test_thrown_flask_breaks_on_creatures(self) -> None:
        world = World(200, 80, seed=1)
        target = Body(130, 20, 8, 30, 10)
        thrown = ThrownFlask.throw(Flask(ACID, 50), 100, 30, 0.0)
        hit = any(thrown.update(world, DT, [target]) for _ in range(60))
        self.assertTrue(hit)
        self.assertLess(abs(thrown.x - 130), 8)


class TestFlaskInRun(unittest.TestCase):
    def test_run_starts_with_blood_and_can_throw_it(self) -> None:
        run = Run(3)
        self.assertEqual(run.flask.material, BLOOD)
        aim = (run.player.center[0] + 60, run.player.center[1] - 30)
        run.update(DT, Controls(aim=aim, throw=True))
        self.assertIsNone(run.flask)
        self.assertEqual(len(run.thrown), 1)

    def test_pouring_and_absorbing_in_a_run(self) -> None:
        run = Run(3)
        before = run.flask.amount
        aim = (run.player.center[0] + 30, run.player.center[1])
        for _ in range(30):
            run.update(DT, Controls(aim=aim, pour=True))
        self.assertLess(run.flask.amount, before)
        poured = before - run.flask.amount
        for _ in range(60):
            run.update(DT, Controls(aim=aim))  # let it settle
        cx, cy = run.player.center
        spot = min(
            ((x, y) for y in range(int(cy) - 40, int(cy) + 40) for x in range(int(cx) - 40, int(cx) + 40)
             if run.world.get(x, y) == BLOOD),
            key=lambda p: math.dist(p, (cx, cy)),
        )  # fmt: skip
        for _ in range(120):
            run.update(DT, Controls(aim=(float(spot[0]), float(spot[1])), absorb=True))
        self.assertGreater(run.flask.amount, before - poured + poured // 3)

    def test_flask_survives_save_and_restore(self) -> None:
        run = Run(3)
        run.flask = Flask(ACID, 77)
        run.enter_sanctum()
        other = Run(9)
        other.restore(run.checkpoint)
        self.assertEqual((other.flask.material, other.flask.amount), (ACID, 77))
        broken = dict(run.checkpoint, flask=[AIR, 5])
        other.restore(broken)
        self.assertIsNone(other.flask)
        self.assertTrue(math.isfinite(other.player.hp))


if __name__ == "__main__":
    unittest.main()
