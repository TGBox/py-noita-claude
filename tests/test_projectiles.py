import math
import unittest

from src.materials import ACID, BLOOD, BONE, FIRE, FLESH, SPORES, TALLOW
from src.projectiles import MAX_PROJECTILES, ProjectileSystem, build
from src.spells import CATALOG, TIMER_DELAY, Trigger
from src.wand import Shot
from src.world import World

DT = 1 / 60
W, H = 160, 96


def shot(form: str, *modifiers: str, children: list[Shot] | None = None) -> Shot:
    return Shot(CATALOG[form], tuple(CATALOG[m] for m in modifiers), children or [])


def wall_world() -> World:
    """Open room with a bone wall on the right (x >= 120)."""
    world = World(W, H, seed=1)
    for y in range(2, H - 2):
        for x in range(120, W - 2):
            world.set_cell(x, y, BONE)
    return world


def open_world(width: int = 1200) -> World:
    """Wide empty room, so projectiles expire before reaching the border."""
    return World(width, H, seed=1)


def run(system: ProjectileSystem, world: World, seconds: float, target=(0.0, 0.0)) -> int:
    blasts = 0
    for _ in range(round(seconds / DT)):
        blasts += len(system.update(world, DT, target))
    return blasts


class TestBuild(unittest.TestCase):
    def test_modifiers_shape_the_projectile(self) -> None:
        p = build(shot("funke", "beschleunigung", "sprengkraft", "sekret_saeure"), 0, 0, 0.0)
        self.assertAlmostEqual(p.vx, CATALOG["funke"].speed * 1.75)
        self.assertEqual(p.blast, CATALOG["funke"].blast + 6)
        self.assertEqual(p.material, ACID)

    def test_gravity_flip(self) -> None:
        self.assertLess(build(shot("klumpen", "umkehr"), 0, 0, 0.0).gravity, 0)
        self.assertLess(build(shot("funke", "umkehr"), 0, 0, 0.0).gravity, 0)

    def test_trigger_and_angle_offset(self) -> None:
        s = shot("nadel", "nerv_naesse")
        s.angle_offset = math.pi / 2
        p = build(s, 0, 0, 0.0)
        self.assertIs(p.trigger, Trigger.WET)
        self.assertAlmostEqual(p.vx, 0.0, places=6)
        self.assertGreater(p.vy, 0)

    def test_klumpen_bleeds_by_default(self) -> None:
        self.assertEqual(build(shot("klumpen"), 0, 0, 0.0).material, BLOOD)


class TestFlight(unittest.TestCase):
    def test_spark_explodes_on_the_wall(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        before = world.count(BONE)
        system.spawn([shot("funke")], 40, 48, 0.0)
        self.assertEqual(run(system, world, 0.5), 1)
        self.assertLess(world.count(BONE), before)
        self.assertEqual(system.items, [])

    def test_payload_splashes_material(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("funke", "sekret_talg")], 40, 48, 0.0)
        run(system, world, 0.5)
        self.assertGreater(world.count(TALLOW), 0)

    def test_fire_payload_ignites(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("klumpen", "sekret_feuer")], 40, 40, 0.0)
        run(system, world, 1.0)
        self.assertGreater(world.count(FIRE), 0)

    def test_spark_expires_in_open_space(self) -> None:
        world, system = open_world(), ProjectileSystem()
        system.spawn([shot("funke", "umkehr")], 80, 80, -math.pi / 2)  # hits the ceiling
        system.spawn([shot("nadel")], 300, 48, 0.0)
        run(system, world, 0.05)
        self.assertEqual(len(system.items), 2)
        self.assertEqual(run(system, world, 2.0), 1)  # only the spark explodes
        self.assertEqual(system.items, [])

    def test_bomb_bounces_and_explodes_on_its_fuse(self) -> None:
        world, system = World(W, H, seed=1), ProjectileSystem()
        system.spawn([shot("gallenblase")], 80, 40, math.pi / 2)  # thrown down
        blasts = run(system, world, CATALOG["gallenblase"].lifetime - 0.1)
        self.assertEqual(blasts, 0)
        self.assertEqual(len(system.items), 1)
        bomb = system.items[0]
        self.assertLess(bomb.bounces, CATALOG["gallenblase"].bounces)
        self.assertGreater(bomb.y, H - 12)  # resting on the floor
        self.assertEqual(run(system, world, 0.3), 1)

    def test_bomb_releases_impact_payload_once(self) -> None:
        world, system = World(W, H, seed=1), ProjectileSystem()
        payload = [shot("klumpen", "sekret_talg")]
        system.spawn([shot("gallenblase", "nerv_aufprall", children=payload)], 80, 40, 1.5)
        run(system, world, 0.8)
        self.assertTrue(system.items[0].released)
        self.assertGreater(world.count(TALLOW), 0)

    def test_homing_turns_towards_the_target(self) -> None:
        world, system = World(W, H, seed=1), ProjectileSystem()
        system.spawn([shot("funke", "zielsuche")], 20, 48, 0.0)  # flies right
        run(system, world, 0.1, target=(20.0, 2000.0))  # target far below
        p = system.items[0]
        self.assertGreater(p.vy, 0)

    def test_projectile_cap(self) -> None:
        system = ProjectileSystem()
        system.spawn([shot("funke")] * (MAX_PROJECTILES + 50), 10, 10, 0.0)
        system.update(World(W, H, seed=1), 0.0, (0, 0))
        self.assertEqual(len(system.items), MAX_PROJECTILES)


class TestTriggers(unittest.TestCase):
    def test_impact_trigger_releases_payload_at_the_wall(self) -> None:
        payload = [shot("klumpen", "sekret_saeure")]
        world, system = open_world(), ProjectileSystem()
        system.spawn([shot("nadel", "nerv_aufprall", children=payload)], 600, 48, math.pi)
        run(system, world, 1.0)  # expires in open space: no impact, no payload
        self.assertEqual(world.count(ACID), 0)

        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("nadel", "nerv_aufprall", children=payload)], 40, 48, 0.0)
        run(system, world, 0.5)
        self.assertGreater(world.count(ACID), 0)

    def test_timer_trigger_releases_mid_flight(self) -> None:
        world, system = open_world(), ProjectileSystem()
        payload = [shot("nadel"), shot("nadel")]
        system.spawn([shot("funke", "nerv_zeit", children=payload)], 10, 48, 0.0)
        run(system, world, TIMER_DELAY - 0.05)
        self.assertEqual(len(system.items), 1)
        run(system, world, 0.1)
        self.assertEqual(len(system.items), 3)

    def test_end_trigger_releases_when_the_flight_ends(self) -> None:
        world, system = World(W, H, seed=1), ProjectileSystem()
        payload = [shot("klumpen", "sekret_sporen")]
        system.spawn([shot("nadel", "nerv_ende", children=payload)], 20, 30, math.pi)
        run(system, world, 1.5)
        self.assertGreater(world.count(SPORES), 0)

    def test_wet_trigger_only_fires_on_liquid(self) -> None:
        payload = [shot("klumpen", "sekret_saeure")]

        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("nadel", "nerv_naesse", children=payload)], 40, 48, 0.0)
        run(system, world, 0.5)
        self.assertEqual(world.count(ACID), 0)  # hit bone: dry

        world, system = World(W, H, seed=1), ProjectileSystem()
        for y in range(30, 70):
            for x in range(100, 110):
                world.set_cell(x, y, BLOOD)
        system.spawn([shot("nadel", "nerv_naesse", children=payload)], 40, 48, 0.0)
        run(system, world, 0.5)
        self.assertGreater(world.count(ACID), 0)

    def test_payload_continues_in_flight_direction(self) -> None:
        world, system = open_world(), ProjectileSystem()
        system.spawn([shot("funke", "nerv_zeit", children=[shot("nadel")])], 10, 48, 0.0)
        run(system, world, TIMER_DELAY + 0.05)  # released payload joins on the next update
        child = [p for p in system.items if p.form.key == "nadel"][0]
        self.assertGreater(child.vx, 0)
        self.assertAlmostEqual(child.vy, 0.0, places=3)

    def test_acid_payload_eats_flesh(self) -> None:
        world, system = World(W, H, seed=1), ProjectileSystem()
        for y in range(60, H - 2):
            for x in range(2, W - 2):
                world.set_cell(x, y, FLESH)
        system.spawn([shot("klumpen", "sekret_saeure")], 80, 30, math.pi / 2)
        run(system, world, 0.5)
        flesh = world.count(FLESH)
        for _ in range(600):
            world.step()
        self.assertLess(world.count(FLESH), flesh)


if __name__ == "__main__":
    unittest.main()
