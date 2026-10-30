import unittest

from src.materials import AIR, FIRE, LAVA, SAND, STONE, build_palette, MATERIAL_COUNT, VARIANTS
from src.player import PLAYER_HEIGHT, PLAYER_WIDTH
from src.viewport import Viewport
from src.wand import BOLT_SPEED, WAND_COOLDOWN, Bolt, Wand
from src.world import World
from src.worldgen import generate_world


class TestViewport(unittest.TestCase):
    def test_letterbox_keeps_aspect_ratio(self) -> None:
        view = Viewport(320, 180)
        view.resize(1000, 1000)
        self.assertAlmostEqual(view.scale, 1000 / 320)
        self.assertEqual(view.target_width, 1000)
        self.assertEqual(view.target_height, int(180 * 1000 / 320))
        self.assertEqual(view.offset_x, 0)
        self.assertGreater(view.offset_y, 0)

    def test_exact_fit(self) -> None:
        view = Viewport(320, 180)
        view.resize(1280, 720)
        self.assertEqual((view.target_width, view.target_height), (1280, 720))
        self.assertEqual((view.offset_x, view.offset_y), (0, 0))
        self.assertEqual(view.to_virtual(640, 360), (160, 90))

    def test_mouse_mapping_is_clamped_in_the_bars(self) -> None:
        view = Viewport(320, 180)
        view.resize(1000, 1000)
        self.assertEqual(view.to_virtual(0, 0), (0, 0))
        self.assertEqual(view.to_virtual(999, 999), (319, 179))

    def test_tiny_window_does_not_crash(self) -> None:
        view = Viewport(320, 180)
        view.resize(0, 0)
        self.assertGreaterEqual(view.target_width, 1)


class TestWand(unittest.TestCase):
    def test_cooldown_and_direction(self) -> None:
        wand = Wand()
        bolt = wand.try_fire((10.0, 10.0), (20.0, 10.0))
        self.assertIsNotNone(bolt)
        assert bolt is not None
        self.assertAlmostEqual(bolt.vx, BOLT_SPEED)
        self.assertAlmostEqual(bolt.vy, 0.0)
        self.assertIsNone(wand.try_fire((10.0, 10.0), (20.0, 10.0)))
        wand.update(WAND_COOLDOWN + 0.01)
        self.assertIsNotNone(wand.try_fire((10.0, 10.0), (20.0, 10.0)))

    def test_no_shot_at_own_position(self) -> None:
        self.assertIsNone(Wand().try_fire((5.0, 5.0), (5.0, 5.0)))

    def test_bolt_explodes_in_stone(self) -> None:
        world = World(64, 48, seed=1)
        for y in range(10, 30):
            for x in range(30, 50):
                world.set_cell(x, y, STONE)
        before = world.count(STONE)
        bolt = Bolt(10.0, 20.0, BOLT_SPEED, 0.0)
        exploded = False
        for _ in range(60):
            if bolt.update(world, 1 / 60):
                exploded = True
                break
        self.assertTrue(exploded)
        self.assertFalse(bolt.alive)
        self.assertLess(world.count(STONE), before)

    def test_bolt_flies_through_air_and_expires(self) -> None:
        world = World(64, 48, seed=1)
        bolt = Bolt(5.0, 5.0, 1.0, 0.0, ttl=0.1)
        for _ in range(10):
            bolt.update(world, 1 / 60)
        self.assertFalse(bolt.alive)


class TestMaterials(unittest.TestCase):
    def test_palette_covers_every_variant(self) -> None:
        self.assertEqual(len(build_palette()), MATERIAL_COUNT * VARIANTS)

    def test_big_int_render_trick(self) -> None:
        # The renderer packs material*VARIANTS + noise per byte via big-int arithmetic.
        grid = bytes([0, 3, 10, 7, 2] * 50)
        noise = bytes([3, 0, 1, 2, 3] * 50)
        packed = int.from_bytes(grid, "little") * VARIANTS + int.from_bytes(noise, "little")
        expected = bytes(g * VARIANTS + n for g, n in zip(grid, noise))
        self.assertEqual(packed.to_bytes(len(grid), "little"), expected)


class TestWorldGen(unittest.TestCase):
    def test_spawn_is_free_and_standing_on_ground(self) -> None:
        for seed in (1, 2, 3, 4, 5):
            world = World(640, 360, seed=seed)
            x, y = generate_world(world)
            self.assertFalse(world.rect_blocked(x, y, PLAYER_WIDTH, PLAYER_HEIGHT), seed)
            self.assertTrue(world.rect_blocked(x, y + 1, PLAYER_WIDTH, PLAYER_HEIGHT), seed)

    def test_generation_is_deterministic(self) -> None:
        a, b = World(640, 360, seed=9), World(640, 360, seed=9)
        generate_world(a)
        generate_world(b)
        self.assertEqual(a.grid, b.grid)

    def test_level_has_caves_and_materials(self) -> None:
        world = World(640, 360, seed=7)
        generate_world(world)
        total = world.width * world.height
        self.assertGreater(world.count(AIR), total * 0.1)
        self.assertGreater(world.count(STONE), total * 0.3)
        self.assertGreater(world.count(SAND), 0)
        self.assertGreater(world.count(LAVA) + world.count(FIRE), 0)

    def test_world_is_playable_for_a_while(self) -> None:
        world = World(640, 360, seed=11)
        generate_world(world)
        for _ in range(120):
            world.step()
        self.assertLess(world.active_chunks, 23 * 40)


if __name__ == "__main__":
    unittest.main()
