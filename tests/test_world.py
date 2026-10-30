import unittest

from src.materials import (
    AIR,
    BEDROCK,
    FIRE,
    LAVA,
    OIL,
    SAND,
    SMOKE,
    STEAM,
    STONE,
    WATER,
    WOOD,
)
from src.world import World

W, H = 64, 48
FLOOR_Y = H - 3  # lowest free row (bedrock occupies the two rows below)


def make_world(seed: int = 1) -> World:
    return World(W, H, seed=seed)


def fill(world: World, x0: int, y0: int, x1: int, y1: int, material: int) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            world.set_cell(x, y, material)


def run(world: World, steps: int) -> None:
    for _ in range(steps):
        world.step()


def cells(world: World, material: int) -> list[tuple[int, int]]:
    return [
        (x, y) for y in range(H) for x in range(W) if world.get(x, y) == material
    ]


class TestBasics(unittest.TestCase):
    def test_border_is_bedrock_and_protected(self) -> None:
        world = make_world()
        self.assertEqual(world.get(0, 0), BEDROCK)
        self.assertEqual(world.get(-5, 10), BEDROCK)
        self.assertFalse(world.set_cell(1, 10, SAND))
        self.assertFalse(world.set_cell(W + 3, 4, SAND))
        self.assertEqual(world.get(1, 10), BEDROCK)

    def test_width_must_be_multiple_of_four(self) -> None:
        with self.assertRaises(ValueError):
            World(63, 40)

    def test_reset_keeps_buffer_identity(self) -> None:
        world = make_world()
        grid = world.grid
        world.set_cell(10, 10, SAND)
        world.reset(STONE)
        self.assertIs(world.grid, grid)
        self.assertEqual(world.get(10, 10), STONE)

    def test_same_seed_same_result(self) -> None:
        def simulate() -> bytes:
            world = make_world(seed=5)
            fill(world, 10, 5, 30, 15, SAND)
            fill(world, 30, 5, 40, 15, WATER)
            run(world, 150)
            return bytes(world.grid)

        self.assertEqual(simulate(), simulate())


class TestPowderAndLiquid(unittest.TestCase):
    def test_sand_falls_to_the_floor(self) -> None:
        world = make_world()
        world.set_cell(20, 5, SAND)
        run(world, 60)
        self.assertEqual(world.get(20, FLOOR_Y), SAND)
        self.assertEqual(world.get(20, 5), AIR)

    def test_sand_is_conserved_and_forms_a_pile(self) -> None:
        world = make_world()
        fill(world, 32, 10, 33, 25, SAND)  # one tall column
        run(world, 200)
        self.assertEqual(world.count(SAND), 15)
        floor_row = [x for x, y in cells(world, SAND) if y == FLOOR_Y]
        self.assertGreater(len(floor_row), 3)

    def test_sand_cannot_enter_stone(self) -> None:
        world = make_world()
        fill(world, 10, 20, 30, 22, STONE)
        fill(world, 15, 5, 25, 8, SAND)
        run(world, 100)
        for x, y in cells(world, SAND):
            self.assertLess(y, 20 + 1 if 10 <= x < 30 else H)

    def test_water_levels_out(self) -> None:
        world = make_world()
        fill(world, 30, 10, 36, 20, WATER)  # 60 cells
        run(world, 400)
        self.assertEqual(world.count(WATER), 60)
        rows = {y for _, y in cells(world, WATER)}
        self.assertLessEqual(len(rows), 2, rows)

    def test_sand_sinks_through_water(self) -> None:
        world = make_world()
        fill(world, 10, FLOOR_Y - 6, 50, FLOOR_Y + 1, WATER)
        world.set_cell(30, FLOOR_Y - 6, SAND)
        run(world, 200)
        self.assertEqual(world.get(30, FLOOR_Y), SAND)

    def test_oil_floats_on_water(self) -> None:
        world = make_world()
        fill(world, 29, 5, 31, H - 2, STONE)  # left wall
        fill(world, 40, 5, 42, H - 2, STONE)  # right wall
        fill(world, 31, FLOOR_Y - 3, 40, FLOOR_Y + 1, OIL)  # oil first (bottom)
        fill(world, 31, FLOOR_Y - 8, 40, FLOOR_Y - 3, WATER)  # water on top
        run(world, 600)
        oil_y = [y for _, y in cells(world, OIL)]
        water_y = [y for _, y in cells(world, WATER)]
        self.assertGreater(sum(water_y) / len(water_y), sum(oil_y) / len(oil_y))


class TestSleeping(unittest.TestCase):
    def test_settled_world_goes_to_sleep_and_wakes_up(self) -> None:
        world = make_world()
        fill(world, 20, 10, 30, 14, SAND)
        run(world, 300)
        self.assertEqual(world.active_chunks, 0)
        world.set_cell(25, 3, SAND)
        self.assertGreater(world.active_chunks, 0)
        run(world, 100)
        self.assertEqual(world.count(SAND), 41)
        self.assertEqual(world.active_chunks, 0)


class TestFireAndReactions(unittest.TestCase):
    def test_fire_burns_a_wooden_plank_and_dies(self) -> None:
        world = make_world(seed=3)
        fill(world, 10, 30, 40, 32, WOOD)
        world.set_cell(10, 30, FIRE)
        run(world, 2500)
        self.assertEqual(world.count(WOOD), 0)
        self.assertEqual(world.count(FIRE), 0)

    def test_stone_does_not_burn(self) -> None:
        world = make_world()
        fill(world, 10, 30, 20, 32, STONE)
        world.set_cell(9, 30, FIRE)
        run(world, 300)
        self.assertEqual(world.count(STONE), 20 + 0)

    def test_oil_burns_quickly(self) -> None:
        world = make_world(seed=2)
        fill(world, 10, FLOOR_Y - 1, 40, FLOOR_Y + 1, OIL)
        world.set_cell(25, FLOOR_Y - 2, FIRE)
        run(world, 400)
        self.assertLess(world.count(OIL), 30)  # most of the 60 cells burned

    def test_water_extinguishes_fire(self) -> None:
        world = make_world()
        fill(world, 15, 15, 27, 26, STONE)  # solid block with a two-cell cavity
        world.set_cell(20, 20, FIRE)
        world.set_cell(21, 20, WATER)
        run(world, 30)
        self.assertEqual(world.count(FIRE), 0)
        self.assertEqual(world.count(WATER) + world.count(STEAM), 1 + 0)

    def test_lava_meets_water_makes_stone(self) -> None:
        world = make_world()
        fill(world, 10, FLOOR_Y - 1, 30, FLOOR_Y + 1, LAVA)
        fill(world, 10, FLOOR_Y - 5, 30, FLOOR_Y - 1, WATER)
        run(world, 400)
        self.assertGreater(world.count(STONE), 0)

    def test_lava_ignites_wood(self) -> None:
        world = make_world(seed=4)
        fill(world, 10, FLOOR_Y, 20, FLOOR_Y + 1, LAVA)
        fill(world, 10, FLOOR_Y - 1, 20, FLOOR_Y, WOOD)
        run(world, 600)
        self.assertLess(world.count(WOOD), 10)

    def test_smoke_and_steam_dissipate(self) -> None:
        world = make_world()
        for x in range(10, 20):
            world.set_cell(x, 30, SMOKE)
            world.set_cell(x + 20, 30, STEAM)
        run(world, 400)
        self.assertEqual(world.count(SMOKE), 0)
        self.assertEqual(world.count(STEAM), 0)

    def test_smoke_rises(self) -> None:
        world = make_world()
        world.set_cell(30, 40, SMOKE)
        run(world, 40)
        smoke = cells(world, SMOKE)
        if smoke:  # may have dissipated, but must not have sunk
            self.assertLess(smoke[0][1], 40)


class TestTools(unittest.TestCase):
    def test_explosion_digs_stone_but_not_bedrock(self) -> None:
        world = make_world()
        fill(world, 5, 10, 60, 40, STONE)
        before = world.count(STONE)
        destroyed = world.explode(32, 25, 6)
        self.assertGreater(destroyed, 30)
        self.assertLess(world.count(STONE), before)
        self.assertEqual(world.get(32, 25), AIR)
        world.explode(32, H - 2, 8)
        self.assertEqual(world.get(32, H - 1), BEDROCK)

    def test_paint_and_erase(self) -> None:
        world = make_world()
        world.paint(30, 20, 3, STONE)
        self.assertEqual(world.get(30, 20), STONE)
        world.paint(30, 20, 3, AIR)
        self.assertEqual(world.get(30, 20), AIR)
        world.paint(1, 1, 3, AIR)  # bedrock stays
        self.assertEqual(world.get(0, 0), BEDROCK)


if __name__ == "__main__":
    unittest.main()
