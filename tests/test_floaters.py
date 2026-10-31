import unittest

from src.body import Body
from src.floaters import LIFETIME, MIN_INTERVAL, FloatingNumbers
from src.world import World


class TestFloaters(unittest.TestCase):
    def test_damage_becomes_a_number_that_fades(self) -> None:
        body = Body(10, 10, 4, 4, 100)
        numbers = FloatingNumbers()
        body.hurt(12.4)
        numbers.update([body], 0.01)
        self.assertEqual([f.text for f in numbers.items], ["12"])
        self.assertEqual(body.damage_taken, 0.0)
        numbers.update([body], LIFETIME)
        self.assertEqual(numbers.items, [])

    def test_small_ticks_are_bundled(self) -> None:
        body = Body(10, 10, 4, 4, 100)
        numbers = FloatingNumbers()
        shown = 0
        for _ in range(60):  # one second of burning at 0.2 per frame
            body.hurt(0.2)
            before = len(numbers.items)
            numbers.update([body], 1 / 60)
            shown += len(numbers.items) > before
        self.assertLessEqual(shown, int(1 / MIN_INTERVAL) + 1)
        self.assertGreater(shown, 0)

    def test_wounds_bleed_into_the_world(self) -> None:
        from src.materials import BLOOD

        world = World(60, 40, seed=1)
        body = Body(20, 10, 4, 4, 100)
        body.bleed(world, 22, 12, 30, 1.0)
        self.assertGreater(world.count(BLOOD), 3)


if __name__ == "__main__":
    unittest.main()
