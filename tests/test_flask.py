import math
import unittest

from src.body import Body
from src.flask import CAPACITY, SIP, Flask, ThrownFlask
from src.materials import ACID, AIR, BLOOD, BONE, MUCUS, PUS, TALLOW
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
        flask = Flask(BLOOD, SIP * 3)
        self.assertTrue(flask.drink(body))
        self.assertEqual(body.hp, 50)  # blood does not heal (like in Noita) ...
        self.assertEqual(body.burning, 0.0)  # ... but it still puts out fire
        self.assertEqual(flask.amount, SIP * 2)
        flask.drink(body, blood_heals=True)  # the "Blutsauger" perk
        self.assertGreater(body.hp, 50)
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
        aim = (run.player.center[0] + 30, run.player.center[1] + 40)  # pour onto the ground nearby
        for _ in range(30):
            run.update(DT, Controls(aim=aim, pour=True))
        self.assertLess(run.flask.amount, before)
        poured = before - run.flask.amount
        for _ in range(60):
            run.update(DT, Controls(aim=aim))  # let it settle
        cx, cy = run.player.center
        spot = min(
            ((x, y) for y in range(int(cy) - 60, int(cy) + 60) for x in range(int(cx) - 60, int(cx) + 60)
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
        broken = dict(run.checkpoint, flasks=[[AIR, 5]])
        other.restore(broken)
        self.assertIsNone(other.flask)
        self.assertTrue(math.isfinite(other.player.hp))
        old = {k: v for k, v in run.checkpoint.items() if k not in ("flasks", "flask_active")}
        other.restore(dict(old, flask=[ACID, 50]))  # a save from before several flasks
        self.assertEqual((other.flask.material, other.flask.amount), (ACID, 50))


if __name__ == "__main__":
    unittest.main()


class TestSeveralFlasks(unittest.TestCase):
    def test_carry_cycle_and_throw(self) -> None:
        from src.loot import Pickup
        from src.run import MAX_FLASKS, Run

        run = Run(5)
        self.assertEqual(len(run.flasks), 1)
        for material in (ACID, TALLOW, PUS, MUCUS):
            cx, cy = run.player.center
            run.pickups = [Pickup(cx, cy, flask=Flask(material, 100))]
            run._pick_up()
        self.assertEqual(len(run.flasks), MAX_FLASKS)
        # hands full: the mucus flask replaced the pus flask in hand, which now lies there
        self.assertEqual(run.flask.material, MUCUS)
        self.assertTrue(any(item.flask and item.flask.material == PUS for item in run.pickups))
        run.select_flask(0)
        self.assertEqual(run.flask.material, BLOOD)
        run.cycle_flask(1)
        self.assertEqual(run.flask.material, ACID)
        run.flask = None  # thrown away
        self.assertEqual(len(run.flasks), MAX_FLASKS - 1)
        run.enter_sanctum()
        other = Run(6)
        other.restore(run.checkpoint)
        self.assertEqual([f.material for f in other.flasks], [f.material for f in run.flasks])
        self.assertEqual(other.flask_index, run.flask_index)

    def test_drop_flask(self) -> None:
        from src.run import Run

        run = Run(5)
        self.assertTrue(run.drop_flask(0))
        self.assertIsNone(run.flask)
        self.assertTrue(any(item.flask is not None and item.seen for item in run.pickups))
