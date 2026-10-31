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
        child = next(p for p in system.items if p.form.key == "nadel")
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


def dummy(x: int, y: int = 40, hp: float = 100.0):
    from src.body import ENEMY_TEAM, Body

    body = Body(x, y, 6, 10, hp)
    body.team = ENEMY_TEAM
    return body


class TestNewBlocks(unittest.TestCase):
    def test_pellets_spawn_several_projectiles(self) -> None:
        system = ProjectileSystem()
        system.spawn([shot("knochensplitter")], 10, 40, 0.0)
        system.update(open_world(), DT, (0.0, 0.0))
        self.assertEqual(len(system.items), CATALOG["knochensplitter"].pellets)

    def test_modifiers_extend_lifetime_and_bounces(self) -> None:
        p = build(shot("funke", "langlebigkeit", "abprall", "durchbohren", "brandbeschleuniger"), 0, 0, 0.0)
        self.assertAlmostEqual(p.lifetime, CATALOG["funke"].lifetime * 2)
        self.assertEqual(p.bounces, 3)
        self.assertTrue(p.pierce and p.ignites)
        self.assertFalse(p.fused)

    def test_bouncy_spark_survives_the_wall(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("funke", "abprall")], 100, 40, 0.0)
        for _ in range(10):
            system.update(world, DT, (0.0, 0.0))
        self.assertTrue(system.items)
        self.assertLess(system.items[0].vx, 0)

    def test_drill_bores_through_bone(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("zahnbohrer")], 110, 40, 0.0)
        run(system, world, 0.3)
        self.assertEqual(world.get(125, 40), 0)

    def test_pierce_hits_every_creature_once(self) -> None:
        world, system = open_world(), ProjectileSystem()
        first, second = dummy(60), dummy(90)
        system.spawn([shot("nadel", "durchbohren")], 20, 44, 0.0)
        for _ in range(30):
            system.update(world, DT, (0.0, 0.0), [first, second])
        damage = CATALOG["nadel"].damage
        self.assertAlmostEqual(first.hp, 100 - damage)
        self.assertAlmostEqual(second.hp, 100 - damage)

    def test_igniting_and_leeching(self) -> None:
        world, system = open_world(), ProjectileSystem()
        victim = dummy(60)
        system.spawn([shot("blutegel", "brandbeschleuniger")], 20, 44, 0.0)
        for _ in range(60):
            system.update(world, DT, (0.0, 0.0), [victim])
        self.assertGreater(victim.burning, 0)
        self.assertAlmostEqual(system.take_healing(), CATALOG["blutegel"].damage * 0.5)
        self.assertEqual(system.take_healing(), 0.0)

    def test_building_payloads(self) -> None:
        for key, material in (("sekret_sehnen", 5), ("sekret_knochen", BONE)):
            world, system = wall_world(), ProjectileSystem()
            before = world.grid.count(material)
            system.spawn([shot("funke", key)], 60, 40, 0.0)
            run(system, world, 1.0)
            self.assertGreater(world.grid.count(material), before)


class TestMoreBlocks(unittest.TestCase):
    def test_catalogue_has_over_fifty_blocks(self) -> None:
        self.assertGreater(len(CATALOG), 50)

    def test_teleport_bolt_reports_where_it_ended(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("teleportbolzen", "schwerelos")], 60, 40, 0.0)
        run(system, world, 1.0)
        self.assertEqual(len(system.teleports), 1)
        x, _y = system.teleports[0]
        self.assertLess(x, 120)  # in front of the wall, not inside it
        self.assertGreater(x, 100)

    def test_saw_ricochets_and_cuts_through(self) -> None:
        world, system = wall_world(), ProjectileSystem()
        system.spawn([shot("knochensaege")], 100, 40, 0.0)
        for _ in range(20):
            system.update(world, DT, (0.0, 0.0))
        self.assertTrue(system.items)
        self.assertLess(system.items[0].vx, 0)
        self.assertTrue(system.items[0].pierce)

    def test_mine_waits_for_a_creature(self) -> None:
        world, system = open_world(), ProjectileSystem()
        system.spawn([shot("sporenmine")], 40, 80, 0.0)
        for _ in range(120):
            system.update(world, DT, (0.0, 0.0), [])
        self.assertEqual(len(system.items), 1)
        mine = system.items[0]
        victim = dummy(int(mine.x) - 3, int(mine.y) - 8)
        blasts = 0
        for _ in range(10):
            blasts += len(system.update(world, DT, (0.0, 0.0), [victim]))
        self.assertEqual(blasts, 1)
        self.assertFalse(system.items)

    def test_trail_and_gravity_and_damage_modifiers(self) -> None:
        p = build(shot("klumpen", "schwerelos", "schadenszuwachs", "blutspur"), 0, 0, 0.0)
        self.assertEqual(p.gravity, 0.0)
        self.assertEqual(p.damage, CATALOG["klumpen"].damage + 6)
        self.assertEqual(p.trail, BLOOD)
        world, system = open_world(), ProjectileSystem()
        system.spawn([shot("funke", "talgspur")], 20, 40, 0.0)
        run(system, world, 0.3)
        self.assertGreater(world.count(TALLOW), 5)


class TestWandBlocks(unittest.TestCase):
    def test_mana_refund_and_haste(self) -> None:
        from src.wand import Wand, WandSpec

        wand = Wand(WandSpec("t", ("manazuschuss", "hast", "funke"), mana_max=100, cast_delay=0.1))
        wand.mana = 50
        self.assertTrue(wand.cast())
        self.assertGreater(wand.mana, 50)  # refund outweighs the cost
        self.assertLessEqual(wand.mana, 100)
        # 0.1 wand + 0.1 refund + 0.05 spark - 0.15 haste
        self.assertAlmostEqual(wand.cooldown, 0.1)

    def test_fast_recharge(self) -> None:
        from src.wand import Wand, WandSpec

        plain = Wand(WandSpec("a", ("funke",), recharge=0.5))
        quick = Wand(WandSpec("b", ("schnellladung", "funke"), recharge=0.5))
        plain.cast()
        quick.cast()
        self.assertAlmostEqual(plain.recharge_left, 0.5)
        self.assertAlmostEqual(quick.recharge_left, 0.2)

    def test_triple_cast(self) -> None:
        from src.wand import Wand, WandSpec

        wand = Wand(WandSpec("t", ("dreifach", "funke", "nadel", "klumpen")))
        self.assertEqual(len(wand.cast()), 3)


class TestFormations(unittest.TestCase):
    def test_circle_and_front_back(self) -> None:
        from src.wand import Wand, WandSpec

        circle = Wand(WandSpec("k", ("achterkreis",) + ("funke",) * 8))
        shots = circle.cast()
        self.assertEqual(len(shots), 8)
        offsets = sorted(round(s.angle_offset % math.tau, 3) for s in shots)
        self.assertAlmostEqual(offsets[1] - offsets[0], math.tau / 8, places=2)
        both = Wand(WandSpec("v", ("vorne_hinten", "funke", "funke"))).cast()
        self.assertEqual(sorted(round(abs(s.angle_offset), 2) for s in both), [0.0, 3.14])

    def test_fan_is_centred(self) -> None:
        from src.wand import Wand, WandSpec

        shots = Wand(WandSpec("f", ("faecher",) + ("nadel",) * 5)).cast()
        self.assertAlmostEqual(sum(s.angle_offset for s in shots), 0.0, places=6)

    def test_catalogue_size(self) -> None:
        self.assertGreaterEqual(len(CATALOG), 70)
