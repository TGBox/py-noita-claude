import unittest

from src.materials import (
    ACID,
    AIR,
    BEDROCK,
    BLOOD,
    BONE,
    BONE_DUST,
    CRUST,
    FIRE,
    FLESH,
    FUME,
    GROWTH,
    SINEW,
    SMOKE,
    SPORES,
    TALLOW,
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
        (x, y)
        for y in range(world.height)
        for x in range(world.width)
        if world.get(x, y) == material
    ]


class TestBasics(unittest.TestCase):
    def test_border_is_bedrock_and_protected(self) -> None:
        world = make_world()
        self.assertEqual(world.get(0, 0), BEDROCK)
        self.assertEqual(world.get(-5, 10), BEDROCK)
        self.assertFalse(world.set_cell(1, 10, BONE_DUST))
        self.assertFalse(world.set_cell(W + 3, 4, BONE_DUST))
        self.assertEqual(world.get(1, 10), BEDROCK)

    def test_reset_keeps_buffer_identity(self) -> None:
        world = make_world()
        grid = world.grid
        world.set_cell(10, 10, BONE_DUST)
        world.reset(FLESH)
        self.assertIs(world.grid, grid)
        self.assertEqual(world.get(10, 10), FLESH)

    def test_same_seed_same_result(self) -> None:
        def simulate() -> bytes:
            world = make_world(seed=5)
            fill(world, 10, 5, 30, 15, BONE_DUST)
            fill(world, 30, 5, 40, 15, BLOOD)
            world.set_cell(35, 20, FIRE)
            run(world, 150)
            return bytes(world.grid)

        self.assertEqual(simulate(), simulate())

    def test_reseed_changes_the_outcome(self) -> None:
        def simulate(seed: int) -> bytes:
            world = make_world()
            world.reseed(seed)
            fill(world, 10, 5, 50, 15, BONE_DUST)
            for x in range(10, 50):
                world.set_cell(x, 30, SMOKE)
            run(world, 20)  # compare mid-flight: settled piles end up alike
            return bytes(world.grid)

        self.assertEqual(simulate(3), simulate(3))
        self.assertNotEqual(simulate(3), simulate(4))


class TestPowderAndLiquid(unittest.TestCase):
    def test_bone_dust_falls_to_the_floor(self) -> None:
        world = make_world()
        world.set_cell(20, 5, BONE_DUST)
        run(world, 60)
        self.assertEqual(world.get(20, FLOOR_Y), BONE_DUST)
        self.assertEqual(world.get(20, 5), AIR)

    def test_dust_is_conserved_and_forms_a_pile(self) -> None:
        world = make_world()
        fill(world, 32, 10, 33, 25, BONE_DUST)  # one tall column
        run(world, 200)
        self.assertEqual(world.count(BONE_DUST), 15)
        floor_row = [x for x, y in cells(world, BONE_DUST) if y == FLOOR_Y]
        self.assertGreater(len(floor_row), 3)

    def test_dust_cannot_enter_bone(self) -> None:
        world = make_world()
        fill(world, 10, 20, 30, 22, BONE)
        fill(world, 15, 5, 25, 8, BONE_DUST)
        run(world, 100)
        for x, y in cells(world, BONE_DUST):
            if 10 <= x < 30:
                self.assertLess(y, 20)

    def test_blood_levels_out(self) -> None:
        world = make_world()
        fill(world, 30, 10, 36, 20, BLOOD)  # 60 cells
        run(world, 400)
        self.assertGreater(world.count(BLOOD) + world.count(CRUST), 58)
        rows = {y for _, y in cells(world, BLOOD)}
        self.assertLessEqual(len(rows), 2, rows)

    def test_dust_sinks_through_blood(self) -> None:
        world = make_world()
        fill(world, 10, FLOOR_Y - 6, 50, FLOOR_Y + 1, BLOOD)
        world.set_cell(30, FLOOR_Y - 6, BONE_DUST)
        run(world, 200)
        self.assertEqual(world.get(30, FLOOR_Y), BONE_DUST)

    def test_tallow_floats_on_blood(self) -> None:
        world = make_world()
        fill(world, 29, 5, 31, H - 2, BONE)  # left wall
        fill(world, 40, 5, 42, H - 2, BONE)  # right wall
        fill(world, 31, FLOOR_Y - 3, 40, FLOOR_Y + 1, TALLOW)  # tallow first (bottom)
        fill(world, 31, FLOOR_Y - 8, 40, FLOOR_Y - 3, BLOOD)  # blood on top
        run(world, 800)
        tallow_y = [y for _, y in cells(world, TALLOW)]
        blood_y = [y for _, y in cells(world, BLOOD)]
        self.assertGreater(sum(blood_y) / len(blood_y), sum(tallow_y) / len(tallow_y))


class TestSleepingAndArea(unittest.TestCase):
    def test_settled_world_goes_to_sleep_and_wakes_up(self) -> None:
        world = make_world()
        fill(world, 20, 10, 30, 14, BONE_DUST)
        run(world, 300)
        self.assertEqual(world.active_chunks, 0)
        world.set_cell(25, 3, BONE_DUST)
        self.assertGreater(world.active_chunks, 0)
        run(world, 100)
        self.assertEqual(world.count(BONE_DUST), 41)
        self.assertEqual(world.active_chunks, 0)

    def test_only_the_given_area_is_simulated(self) -> None:
        world = World(128, 48, seed=1)
        world.set_cell(10, 5, BONE_DUST)  # inside the area
        world.set_cell(100, 5, BONE_DUST)  # outside the area
        for _ in range(60):
            world.step((0, 0, 48, 48))
        self.assertEqual(world.get(10, FLOOR_Y), BONE_DUST)
        self.assertEqual(world.get(100, 5), BONE_DUST)  # frozen, but still pending
        run(world, 60)
        self.assertEqual(world.get(100, FLOOR_Y), BONE_DUST)


class TestFireAndReactions(unittest.TestCase):
    def test_fire_burns_a_sinew_bridge_and_dies(self) -> None:
        world = make_world(seed=3)
        fill(world, 10, 30, 40, 32, SINEW)
        world.set_cell(10, 29, FIRE)
        run(world, 3000)
        self.assertEqual(world.count(SINEW), 0)
        self.assertEqual(world.count(FIRE), 0)

    def test_bone_does_not_burn(self) -> None:
        world = make_world()
        fill(world, 10, 30, 20, 32, BONE)
        world.set_cell(9, 30, FIRE)
        run(world, 300)
        self.assertEqual(world.count(BONE), 20)

    def test_fire_chars_flesh_into_scab_instead_of_burning_it(self) -> None:
        world = make_world(seed=2)
        fill(world, 10, 30, 50, FLOOR_Y + 1, FLESH)
        for x in range(20, 40):
            world.set_cell(x, 29, FIRE)
        run(world, 400)
        self.assertGreater(world.count(CRUST), 0)
        self.assertGreater(world.count(FLESH), 40 * (FLOOR_Y + 1 - 30) - 60)

    def test_tallow_burns_quickly(self) -> None:
        world = make_world(seed=2)
        fill(world, 10, FLOOR_Y - 1, 40, FLOOR_Y + 1, TALLOW)
        world.set_cell(25, FLOOR_Y - 2, FIRE)
        run(world, 400)
        self.assertLess(world.count(TALLOW), 30)  # most of the 60 cells burned

    def test_blood_douses_fire_and_cooks_into_scab(self) -> None:
        world = make_world()
        fill(world, 15, 15, 27, 26, BONE)  # solid block with a two-cell cavity
        world.set_cell(20, 20, FIRE)
        world.set_cell(21, 20, BLOOD)
        run(world, 30)
        self.assertEqual(world.count(FIRE), 0)
        self.assertEqual(world.count(CRUST), 1)

    def test_blood_clots_where_it_touches_air(self) -> None:
        world = make_world()
        fill(world, 10, FLOOR_Y - 2, 50, FLOOR_Y + 1, BLOOD)
        run(world, 3000)
        crust = cells(world, CRUST)
        self.assertGreater(len(crust), 0)
        # Scab forms where blood touches air; early clots may get covered by later flow.
        covered = sum(1 for x, y in crust if world.get(x, y - 1) == BLOOD)
        self.assertLess(covered, len(crust) * 0.2, crust)

    def test_acid_eats_flesh_and_is_used_up(self) -> None:
        world = make_world()
        fill(world, 10, 30, 54, FLOOR_Y + 1, FLESH)
        fill(world, 20, 26, 40, 30, ACID)  # 80 cells resting on flesh
        flesh_before = world.count(FLESH)
        run(world, 1500)
        eaten = flesh_before - world.count(FLESH)
        self.assertGreater(eaten, 20)
        self.assertLessEqual(eaten, 80)  # every dissolved cell costs one acid cell
        self.assertLess(world.count(ACID), 80)

    def test_acid_dissolves_bone_slower_than_flesh(self) -> None:
        def eaten(material: int) -> int:
            world = make_world(seed=4)
            fill(world, 10, 30, 54, FLOOR_Y + 1, material)
            fill(world, 20, 26, 40, 30, ACID)
            before = world.count(material)
            run(world, 300)
            return before - world.count(material)

        self.assertGreater(eaten(FLESH), eaten(BONE))

    def test_acid_releases_fumes(self) -> None:
        world = make_world()
        fill(world, 10, 30, 54, FLOOR_Y + 1, FLESH)
        fill(world, 20, 26, 40, 30, ACID)
        seen = 0
        for _ in range(200):
            world.step()
            seen = max(seen, world.count(FUME))
        self.assertGreater(seen, 0)

    def test_growth_spreads_into_flesh(self) -> None:
        world = make_world()
        fill(world, 10, 20, 54, 40, FLESH)
        world.set_cell(30, 30, GROWTH)
        run(world, 2000)
        self.assertGreater(world.count(GROWTH), 5)

    def test_spores_infect_flesh(self) -> None:
        world = make_world()
        fill(world, 10, 10, 54, 12, FLESH)  # ceiling: spores rise against it
        for x in range(20, 40):
            world.set_cell(x, 30, SPORES)
        run(world, 600)
        self.assertGreater(world.count(GROWTH), 0)

    def test_spores_are_flammable(self) -> None:
        world = make_world()
        for x in range(20, 40):
            world.set_cell(x, 30, SPORES)
        world.set_cell(19, 30, FIRE)
        seen_fire = 0
        for _ in range(30):
            world.step()
            seen_fire = max(seen_fire, world.count(FIRE))
        self.assertGreater(seen_fire, 3)

    def test_gases_dissipate(self) -> None:
        world = make_world()
        for x in range(10, 20):
            world.set_cell(x, 30, SMOKE)
            world.set_cell(x + 20, 30, FUME)
        run(world, 400)
        self.assertEqual(world.count(SMOKE), 0)
        self.assertEqual(world.count(FUME), 0)

    def test_smoke_rises(self) -> None:
        world = make_world()
        world.set_cell(30, 40, SMOKE)
        run(world, 40)
        smoke = cells(world, SMOKE)
        if smoke:  # may have dissipated, but must not have sunk
            self.assertLess(smoke[0][1], 40)


class TestTools(unittest.TestCase):
    def test_explosion_digs_but_not_bedrock(self) -> None:
        world = make_world()
        fill(world, 5, 10, 60, 40, BONE)
        before = world.count(BONE)
        destroyed = world.explode(32, 25, 6)
        self.assertGreater(destroyed, 30)
        self.assertLess(world.count(BONE), before)
        self.assertIn(world.get(32, 25), (AIR, BONE_DUST))
        world.explode(32, H - 2, 8)
        self.assertEqual(world.get(32, H - 1), BEDROCK)

    def test_explosions_leave_no_loose_pixels(self) -> None:
        for seed in range(5):
            world = make_world(seed=seed)
            fill(world, 5, 5, 60, 44, BONE)
            for cx in (20, 32, 44):
                world.explode(cx, 24, 7)
            for y in range(3, 45):
                for x in range(3, 61):
                    if world.get(x, y) != BONE:
                        continue
                    neighbours = sum(
                        world.get(x + dx, y + dy) in (BONE, BEDROCK)
                        for dx in (-1, 0, 1)
                        for dy in (-1, 0, 1)
                        if dx or dy
                    )
                    self.assertGreater(neighbours, 2, (seed, x, y))

    def test_crumbling_turns_splinters_into_debris(self) -> None:
        world = make_world()
        world.set_cell(30, 20, BONE)  # a lone bone pixel floating in the air
        world.set_cell(40, 20, FLESH)
        self.assertEqual(world.crumble_loose(35, 20, 10), 2)
        self.assertEqual(world.get(30, 20), BONE_DUST)
        self.assertEqual(world.get(40, 20), BLOOD)

    def test_explosion_leaves_debris(self) -> None:
        world = make_world(seed=6)
        fill(world, 5, 5, 60, 44, FLESH)
        world.explode(32, 24, 12)
        self.assertGreater(world.count(BLOOD), 0)  # flesh bleeds

    def test_explosion_ignites_flammables(self) -> None:
        world = make_world(seed=6)
        fill(world, 5, 20, 60, 30, TALLOW)
        world.explode(32, 25, 8)
        self.assertGreater(world.count(FIRE), 0)

    def test_paint_and_erase(self) -> None:
        world = make_world()
        world.paint(30, 20, 3, BONE)
        self.assertEqual(world.get(30, 20), BONE)
        world.paint(30, 20, 3, AIR)
        self.assertEqual(world.get(30, 20), AIR)
        world.paint(1, 1, 3, AIR)  # bedrock stays
        self.assertEqual(world.get(0, 0), BEDROCK)


if __name__ == "__main__":
    unittest.main()
