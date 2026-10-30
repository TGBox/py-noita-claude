import random
import unittest

from src.body import BURN_TIME, WET_TIME
from src.enemies import MAGGOT, Creature
from src.materials import BLOOD, FIRE, SINEW
from src.player import PLAYER_HEIGHT, Player
from src.world import World

DT = 1 / 60
W, H = 160, 80
FLOOR = H - 2


def stand(world: World) -> Player:
    player = Player(60, FLOOR - PLAYER_HEIGHT)
    for _ in range(10):
        player.update(world, DT, 0, False, False)
    return player


class TestBurning(unittest.TestCase):
    def test_touching_fire_sets_the_body_on_fire(self) -> None:
        world = World(W, H, seed=1)
        player = stand(world)
        world.set_cell(player.x - 1, player.y + 5, FIRE)
        player.update(world, DT, 0, False, False)
        self.assertGreater(player.burning, BURN_TIME - 0.1)

    def test_burning_hurts_and_sheds_flames_then_stops(self) -> None:
        world = World(W, H, seed=2)
        player = stand(world)
        player.burning = BURN_TIME
        flames = 0
        for _ in range(30):
            player.update(world, DT, 0, False, False)
            flames = max(flames, world.count(FIRE))
        self.assertGreater(flames, 0)
        self.assertLess(player.hp, player.max_hp)
        for _ in range(round(BURN_TIME / DT) + 120):
            player.update(world, DT, 0, False, False)
            world.step()
        self.assertEqual(player.burning, 0.0)
        self.assertFalse(player.dead)

    def test_burning_body_ignites_flammable_surroundings(self) -> None:
        world = World(W, H, seed=3)
        for x in range(50, 80):
            world.set_cell(x, FLOOR - PLAYER_HEIGHT - 3, SINEW)  # low sinew ceiling
        player = stand(world)
        player.burning = BURN_TIME
        before = world.count(SINEW)
        for _ in range(240):
            player.update(world, DT, 0, False, False)
            world.step()
        self.assertLess(world.count(SINEW), before)

    def test_liquid_extinguishes_and_makes_wet(self) -> None:
        world = World(W, H, seed=4)
        for x in range(2, W - 2):
            for y in range(FLOOR - 4, FLOOR):
                world.set_cell(x, y, BLOOD)
        player = stand(world)
        player.burning = BURN_TIME
        player.update(world, DT, 0, False, False)
        self.assertEqual(player.burning, 0.0)
        self.assertGreater(player.wet, WET_TIME - 0.1)

    def test_wet_bodies_do_not_catch_fire(self) -> None:
        world = World(W, H, seed=5)
        player = stand(world)
        player.wet = WET_TIME
        world.set_cell(player.x - 1, player.y + 5, FIRE)
        player.update(world, DT, 0, False, False)
        self.assertEqual(player.burning, 0.0)

    def test_creatures_burn_too(self) -> None:
        world = World(W, H, seed=6)
        maggot = Creature(MAGGOT, 60, FLOOR - MAGGOT.height, random.Random(1))
        maggot.burning = BURN_TIME
        maggot.apply_environment(world, 1.0)
        self.assertLess(maggot.hp, maggot.max_hp)


if __name__ == "__main__":
    unittest.main()
