import unittest

from src.materials import BLOOD, BONE, BONE_DUST, FIRE
from src.player import (
    ENERGY_RECHARGE,
    MAX_ENERGY,
    MAX_HP,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    Player,
)
from src.world import World

W, H = 240, 96
DT = 1 / 60


def make_world() -> World:
    return World(W, H, seed=1)


def fill(world: World, x0: int, y0: int, x1: int, y1: int, material: int) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            world.set_cell(x, y, material)


def tick(player: Player, world: World, seconds: float, **inputs: object) -> None:
    for _ in range(round(seconds / DT)):
        player.update(
            world,
            DT,
            int(inputs.get("move", 0)),
            bool(inputs.get("jump", False)),
            bool(inputs.get("levitate", False)),
        )


class TestPlayer(unittest.TestCase):
    def test_falls_and_lands_on_floor(self) -> None:
        world = make_world()
        player = Player(40, 10)
        tick(player, world, 2.0)
        self.assertEqual(player.y, H - 2 - PLAYER_HEIGHT)
        self.assertTrue(player.on_ground)

    def test_walks_and_stops_at_wall(self) -> None:
        world = make_world()
        fill(world, 60, 10, 62, H - 2, BONE)
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 3.0, move=1)
        self.assertEqual(player.x, 60 - PLAYER_WIDTH)

    def test_steps_up_small_ledges_but_not_big_ones(self) -> None:
        world = make_world()
        fill(world, 50, H - 4, 70, H - 2, BONE)  # 2 px ledge
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 2.0, move=1)
        self.assertGreater(player.x, 60)

        world = make_world()
        fill(world, 50, H - 12, 70, H - 2, BONE)  # 10 px wall (higher than STEP_UP)
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 2.0, move=1)
        self.assertEqual(player.x, 50 - PLAYER_WIDTH)

    def test_jump_leaves_the_ground(self) -> None:
        world = make_world()
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 0.2)
        floor_y = player.y
        player.update(world, DT, 0, True, False)
        tick(player, world, 0.15)
        self.assertLess(player.y, floor_y - 5)

    def test_levitation_drains_and_recharges_energy(self) -> None:
        world = make_world()
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 0.2)
        player.update(world, DT, 0, True, True)
        tick(player, world, 1.0, levitate=True)
        self.assertLess(player.energy, MAX_ENERGY)
        self.assertLess(player.y, H - 2 - PLAYER_HEIGHT - 20)
        tick(player, world, 4.0)  # fall back and rest
        self.assertTrue(player.on_ground)
        tick(player, world, MAX_ENERGY / ENERGY_RECHARGE + 0.5)
        self.assertAlmostEqual(player.energy, MAX_ENERGY, places=2)

    def test_levitation_runs_out(self) -> None:
        world = make_world()
        player = Player(40, 40)
        tick(player, world, MAX_ENERGY + 0.2, levitate=True)
        self.assertEqual(player.energy, 0.0)
        self.assertFalse(player.on_ground)

    def test_buried_player_is_pushed_out_of_bone_dust(self) -> None:
        world = make_world()
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 0.1)
        fill(world, 36, player.y + 4, 50, player.y + 9, BONE_DUST)  # buries the lower body
        tick(player, world, 0.1)
        self.assertFalse(world.rect_blocked(player.x, player.y, PLAYER_WIDTH, PLAYER_HEIGHT))

    def test_fire_hurts_and_kills(self) -> None:
        world = make_world()
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 0.2)
        world.set_cell(player.x + 1, player.y + 2, FIRE)
        player.update(world, DT, 0, False, False)
        self.assertLess(player.hp, MAX_HP)
        for _ in range(600):
            world.set_cell(player.x + 1, player.y + 2, FIRE)
            player.update(world, DT, 0, False, False)
        self.assertTrue(player.dead)

    def test_blood_slows_walking(self) -> None:
        dry = make_world()
        p_dry = Player(10, H - 2 - PLAYER_HEIGHT)
        tick(p_dry, dry, 1.0, move=1)

        wet = make_world()
        fill(wet, 2, H - 14, W - 2, H - 2, BLOOD)
        p_wet = Player(10, H - 2 - PLAYER_HEIGHT)
        tick(p_wet, wet, 1.0, move=1)
        self.assertLess(p_wet.x, p_dry.x)

    def test_jump_is_a_small_hop_and_levitation_does_the_climbing(self) -> None:
        world = make_world()
        hop = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(hop, world, 0.2)
        start = hop.y
        hop.update(world, DT, 0, True, False)
        best = start
        for _ in range(60):
            hop.update(world, DT, 0, False, False)
            best = min(best, hop.y)
        self.assertLess(start - best, 30)  # small hop

        flyer = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(flyer, world, 0.2)
        flyer.update(world, DT, 0, True, True)
        tick(flyer, world, 0.4, levitate=True)
        self.assertLess(flyer.y, best)

    def test_energy_refills_quickly_on_the_ground(self) -> None:
        world = make_world()
        player = Player(40, H - 2 - PLAYER_HEIGHT)
        tick(player, world, 0.2)
        player.energy = 0.0
        tick(player, world, 0.6)
        self.assertEqual(player.energy, MAX_ENERGY)

    def test_reset_restores_health(self) -> None:
        player = Player(40, 10)
        player.hp = 0
        player.reset(5, 5)
        self.assertFalse(player.dead)
        self.assertEqual((player.x, player.y), (5, 5))


if __name__ == "__main__":
    unittest.main()
