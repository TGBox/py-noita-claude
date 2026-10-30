import unittest

from src import native
from src.materials import (
    ACID,
    AIR,
    BLOOD,
    BONE,
    BONE_DUST,
    FLESH,
    GROWTH,
    MATERIAL_COUNT,
    VARIANTS,
)
from src.texture import make_grain
from src.player import PLAYER_HEIGHT, PLAYER_WIDTH
from src.viewport import Viewport
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


class TestWorldGen(unittest.TestCase):
    def test_spawn_is_free_and_standing_on_ground(self) -> None:
        for seed in (1, 2, 3, 4, 5):
            world = World(1280, 720, seed=seed)
            x, y = generate_world(world)
            self.assertFalse(world.rect_blocked(x, y, PLAYER_WIDTH, PLAYER_HEIGHT), seed)
            self.assertTrue(world.rect_blocked(x, y + 1, PLAYER_WIDTH, PLAYER_HEIGHT), seed)

    def test_generation_is_deterministic(self) -> None:
        a, b = World(1280, 720, seed=9), World(1280, 720, seed=9)
        generate_world(a)
        generate_world(b)
        self.assertEqual(a.grid, b.grid)

    def test_level_has_caves_and_materials(self) -> None:
        world = World(1280, 720, seed=7)
        generate_world(world)
        total = world.width * world.height
        self.assertGreater(world.count(AIR), total * 0.1)
        self.assertGreater(world.count(FLESH), total * 0.3)
        for material in (BONE, BONE_DUST, BLOOD, ACID, GROWTH):
            self.assertGreater(world.count(material), 0, material)

    def test_spawn_is_safe_from_acid(self) -> None:
        for seed in (1, 2, 3):
            world = World(1280, 720, seed=seed)
            x, y = generate_world(world)
            for _ in range(240):
                world.step((x - 200, y - 150, x + 200, y + 150))
            for yy in range(y - 60, y + 30):
                for xx in range(x - 80, x + 80):
                    self.assertNotEqual(world.get(xx, yy), ACID, (seed, xx, yy))

    def test_settles_quickly_near_the_camera(self) -> None:
        world = World(1280, 720, seed=11)
        generate_world(world)
        area = (320, 0, 960, 360)
        for _ in range(600):
            world.step(area)
        self.assertLess(world.step(area), 600)  # most chunks fell asleep


class TestRenderCore(unittest.TestCase):
    def test_render_writes_palette_indices_for_the_view(self) -> None:
        world = World(64, 48, seed=1)
        world.set_cell(10, 12, BLOOD)
        grain = make_grain(64, 48)
        out = bytearray(20 * 10)
        native.render(
            native.byte_view(world.grid),
            native.byte_view(grain),
            native.byte_view(out),
            64, 5, 8, 20, 10, VARIANTS,
        )  # fmt: skip
        index = (12 - 8) * 20 + (10 - 5)
        self.assertEqual(out[index], BLOOD * VARIANTS + grain[12 * 64 + 10])
        self.assertEqual(out[0], world.get(5, 8) * VARIANTS + grain[8 * 64 + 5])
        self.assertLess(max(out), MATERIAL_COUNT * VARIANTS)

    def test_grain_uses_every_variant_and_is_deterministic(self) -> None:
        a = make_grain(256, 128, seed=3)
        self.assertEqual(a, make_grain(256, 128, seed=3))
        self.assertNotEqual(a, make_grain(256, 128, seed=4))
        self.assertEqual(set(a), set(range(VARIANTS)))


if __name__ == "__main__":
    unittest.main()
