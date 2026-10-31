import math
import random
import unittest

from src.body import ENEMY_TEAM, PLAYER_TEAM
from src.enemies import (
    BONE_SPITTER,
    MAGGOT,
    SPORE_BLOAT,
    SWARMER,
    Creature,
    EnemyManager,
    populate,
)
from src.materials import ACID, BLOOD, BONE, SPORES
from src.player import PLAYER_HEIGHT, Player
from src.projectiles import ProjectileSystem
from src.spells import CATALOG
from src.wand import Shot
from src.world import World
from src.worldgen import generate_world

DT = 1 / 60
W, H = 320, 120
FLOOR = H - 2  # first bedrock row
EVERYWHERE = (0, 0, 10_000, 10_000)


def room() -> World:
    return World(W, H, seed=1)


def run(world, manager, player, projectiles, seconds, area=EVERYWHERE) -> list:
    died = []
    for _ in range(round(seconds / DT)):
        player.update(world, DT, 0, False, False)
        died += manager.update(world, DT, player, projectiles, area)
        projectiles.update(world, DT, (0.0, 0.0), [player, *manager.creatures])
    return died


def on_floor(spec, x: int) -> Creature:
    return Creature(spec, x, FLOOR - spec.height, random.Random(1))


class TestMaggot(unittest.TestCase):
    def test_chases_and_bites_the_player(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        player = Player(200, FLOOR - PLAYER_HEIGHT)
        manager.creatures = [on_floor(MAGGOT, 60)]
        run(world, manager, player, projectiles, 5.0)
        self.assertLess(player.hp, 100)
        self.assertGreater(manager.creatures[0].x, 150)

    def test_jumps_over_a_wall_when_chasing(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        for y in range(FLOOR - 10, FLOOR):
            for x in range(120, 124):
                world.set_cell(x, y, BONE)
        for y in range(FLOOR - 30, FLOOR):  # pedestal: the player is visible over the wall
            for x in range(210, 240):
                world.set_cell(x, y, BONE)
        player = Player(220, FLOOR - 30 - PLAYER_HEIGHT)
        manager.creatures = [on_floor(MAGGOT, 60)]
        run(world, manager, player, projectiles, 6.0)
        self.assertGreater(manager.creatures[0].x, 124)

    def test_does_not_see_through_walls(self) -> None:
        world = room()
        for y in range(2, FLOOR):
            for x in range(150, 160):
                world.set_cell(x, y, BONE)
        maggot = on_floor(MAGGOT, 60)
        self.assertFalse(maggot.can_see(world, 250, FLOOR - 5, 450))
        self.assertTrue(maggot.can_see(world, 120, FLOOR - 5, 450))

    def test_dies_in_acid(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        for y in range(FLOOR - 8, FLOOR):
            for x in range(40, 100):
                world.set_cell(x, y, ACID)
        manager.creatures = [on_floor(MAGGOT, 60)]
        player = Player(300, FLOOR - PLAYER_HEIGHT)
        died = run(world, manager, player, projectiles, 2.0)
        self.assertEqual(len(died), 1)
        self.assertEqual(manager.creatures, [])

    def test_dead_creatures_bleed(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        maggot = on_floor(MAGGOT, 60)
        maggot.hurt(1000)
        manager.creatures = [maggot]
        run(world, manager, Player(300, FLOOR - PLAYER_HEIGHT), projectiles, DT)
        self.assertGreater(world.count(BLOOD), 0)


class TestSwarmer(unittest.TestCase):
    def test_flies_towards_the_player_and_spits_acid(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        player = Player(220, FLOOR - PLAYER_HEIGHT)
        swarmer = Creature(SWARMER, 60, 40, random.Random(2))
        manager.creatures = [swarmer]
        start = math.dist(swarmer.center, player.center)
        spat = False
        for _ in range(round(4.0 / DT)):
            run(world, manager, player, projectiles, DT)
            spat = spat or any(p.team == ENEMY_TEAM for p in projectiles.items)
        self.assertTrue(spat)
        self.assertLess(math.dist(swarmer.center, player.center), start)
        self.assertGreater(world.count(ACID), 0)

    def test_hovers_without_falling(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        swarmer = Creature(SWARMER, 100, 30, random.Random(3))
        manager.creatures = [swarmer]
        far_away = Player(310, 2)
        far_away.hp = 0  # dead players are not chased
        run(world, manager, far_away, projectiles, 2.0)
        self.assertLess(swarmer.y, FLOOR - 30)


class TestCombat(unittest.TestCase):
    def test_player_projectiles_hurt_creatures_but_not_the_player(self) -> None:
        world, projectiles = room(), ProjectileSystem()
        player = Player(100, 50)
        maggot = Creature(MAGGOT, 180, 52, random.Random(1))
        projectiles.spawn([Shot(CATALOG["nadel"])], 90, 55, 0.0, PLAYER_TEAM)  # through player
        for _ in range(30):
            projectiles.update(world, DT, (0, 0), [player, maggot])
        self.assertEqual(player.hp, player.max_hp)
        self.assertLess(maggot.hp, maggot.max_hp)

    def test_enemy_projectiles_pass_through_creatures(self) -> None:
        world, projectiles = room(), ProjectileSystem()
        maggot = Creature(MAGGOT, 120, 52, random.Random(1))
        player = Player(200, 48)
        projectiles.spawn([Shot(CATALOG["nadel"])], 100, 55, 0.0, ENEMY_TEAM)
        for _ in range(30):
            projectiles.update(world, DT, (0, 0), [player, maggot])
        self.assertEqual(maggot.hp, maggot.max_hp)
        self.assertLess(player.hp, player.max_hp)

    def test_hurt_creatures_flash_and_become_alert(self) -> None:
        maggot = Creature(MAGGOT, 0, 0, random.Random(1))
        maggot.hurt(5)
        self.assertGreater(maggot.flash, 0)
        self.assertTrue(maggot.alerted)
        self.assertEqual(maggot.hp, MAGGOT.hp - 5)

    def test_creatures_outside_the_area_are_frozen(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        player = Player(10, FLOOR - PLAYER_HEIGHT)
        swarmer = Creature(SWARMER, 250, 30, random.Random(3))
        manager.creatures = [swarmer]
        run(world, manager, player, projectiles, 1.0, area=(0, 0, 100, H))
        self.assertEqual((swarmer.x, swarmer.y), (250, 30))


class TestNewCreatures(unittest.TestCase):
    def test_bone_spitter_hangs_still_and_shoots_needles(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        for x in range(2, W - 2):
            for y in range(2, 20):
                world.set_cell(x, y, BONE)
        spitter = Creature(BONE_SPITTER, 100, 20, random.Random(1))
        manager.creatures = [spitter]
        player = Player(180, FLOOR - PLAYER_HEIGHT)
        shot = False
        for _ in range(round(3.0 / DT)):
            run(world, manager, player, projectiles, DT)
            shot = shot or any(p.form.key == "nadel" for p in projectiles.items)
        self.assertTrue(shot)
        self.assertEqual((spitter.x, spitter.y), (100, 20))

    def test_spore_bloat_pops_on_touch_into_spores(self) -> None:
        world, projectiles, manager = room(), ProjectileSystem(), EnemyManager()
        player = Player(120, FLOOR - PLAYER_HEIGHT)
        bloat = Creature(SPORE_BLOAT, 100, FLOOR - 30, random.Random(2))
        manager.creatures = [bloat]
        died = run(world, manager, player, projectiles, 4.0)
        self.assertEqual(len(died), 1)
        self.assertLess(player.hp, player.max_hp)
        self.assertGreater(world.count(SPORES), 0)

    def test_spitters_are_placed_under_ceilings(self) -> None:
        world = World(1280, 720, seed=4)
        spawn = generate_world(world)
        creatures = populate(world, random.Random(3), spawn, 0, 0, spitters=6, bloats=4)
        spitters = [c for c in creatures if c.spec is BONE_SPITTER]
        self.assertGreaterEqual(len(spitters), 4)
        for c in spitters:
            self.assertTrue(world.rect_blocked(c.x + c.width // 2, c.y - 1, 1, 1))
        self.assertGreaterEqual(sum(c.spec is SPORE_BLOAT for c in creatures), 3)


class TestPopulate(unittest.TestCase):
    def test_creatures_are_placed_in_free_space_away_from_spawn(self) -> None:
        world = World(1280, 720, seed=4)
        spawn = generate_world(world)
        creatures = populate(world, random.Random(1), spawn, 14, 8)
        self.assertGreaterEqual(len(creatures), 18)
        for c in creatures:
            self.assertFalse(world.rect_blocked(c.x, c.y, c.width, c.height))
            self.assertGreater(math.dist((c.x, c.y), spawn), 150)
            if not c.spec.flying:
                self.assertTrue(world.rect_blocked(c.x, c.y + 1, c.width, c.height))

    def test_population_is_deterministic(self) -> None:
        def place() -> list:
            world = World(1280, 720, seed=4)
            spawn = generate_world(world)
            return [(c.spec.key, c.x, c.y) for c in populate(world, random.Random(5), spawn, 5, 5)]

        self.assertEqual(place(), place())


if __name__ == "__main__":
    unittest.main()



class TestBroodMother(unittest.TestCase):
    def test_guards_the_gedaerm_and_summons_in_turn(self) -> None:
        from src.depths import DEPTHS
        from src.enemies import BROOD_MOTHER, spawn_boss

        self.assertIn("brutmutter", [d.boss for d in DEPTHS if d.key == "gedaerm"])
        world = World(640, 200, seed=1)
        mother = spawn_boss("brutmutter", (320, 80), random.Random(1))
        manager = EnemyManager()
        manager.creatures.append(mother)
        player = Player(250, 200 - 2 - PLAYER_HEIGHT)
        player.hp = player.max_hp = 1e9  # survive the fight
        projectiles, keys = ProjectileSystem(), set()
        for _ in range(round((BROOD_MOTHER.summon_interval * 2 + 0.5) / DT)):
            run(world, manager, player, projectiles, DT)
            keys |= {c.spec.key for c in manager.creatures if c is not mother}
        self.assertEqual(keys, {"sporenblase", "schwaermer"})


class TestNewSpecies(unittest.TestCase):
    def test_every_depth_spawns_its_extra_species(self) -> None:
        from src.depths import DEPTHS
        from src.enemies import SPECIES

        for depth in DEPTHS:
            for key, count in depth.extra:
                self.assertIn(key, SPECIES)
                self.assertGreater(count, 0)

    def test_immunities_and_gore(self) -> None:
        from src.enemies import SPECIES

        ember = Creature(SPECIES["brandmade"], 10, 10, random.Random(1))
        self.assertTrue(ember.fire_immune)
        self.assertEqual(ember.blood, SPECIES["brandmade"].gore)
        self.assertTrue(Creature(SPECIES["schleimkriecher"], 10, 10, random.Random(1)).acid_immune)

    def test_populate_places_extra_species(self) -> None:
        world = generate_world_and_return()
        creatures = populate(world, random.Random(2), (640, 100), 0, 0, extra=(("egel", 3), ("augenblase", 2)))
        keys = [c.spec.key for c in creatures]
        self.assertEqual(keys.count("egel"), 3)
        self.assertEqual(keys.count("augenblase"), 2)

    def test_sprites_match_the_creature_sizes(self) -> None:
        try:
            from src.rendering import CREATURE_COLORS, CREATURE_SPRITES, FRAME_RATES
        except ImportError:
            self.skipTest("pygame not installed")
        from src.enemies import SPECIES

        for key, frames in CREATURE_SPRITES.items():
            spec = SPECIES[key]
            self.assertIn(key, FRAME_RATES)
            for rows in frames:
                self.assertEqual((len(rows[0]), len(rows)), (spec.width, spec.height), key)
                self.assertTrue(all(c == "." or c in CREATURE_COLORS for r in rows for c in r))


def generate_world_and_return() -> World:
    world = World(1280, 720, seed=4)
    generate_world(world)
    return world


class TestNewBosses(unittest.TestCase):
    def test_every_boss_depth_has_a_known_boss(self) -> None:
        from src.depths import DEPTHS
        from src.enemies import SPECIES

        bosses = [d.boss for d in DEPTHS if d.boss]
        self.assertEqual(len(bosses), 5)
        self.assertTrue(all(SPECIES[b].boss for b in bosses))

    def test_bone_eater_burrows_through_bone(self) -> None:
        from src.enemies import spawn_boss

        world = World(400, 200, seed=1)
        for y in range(2, 198):
            for x in range(150, 250):
                world.set_cell(x, y, BONE)
        eater = spawn_boss("knochenfresser", (100, 100), random.Random(1))
        manager = EnemyManager()
        manager.creatures.append(eater)
        player = Player(320, 200 - 2 - PLAYER_HEIGHT)
        player.hp = player.max_hp = 1e9
        start = eater.x
        run(world, manager, player, ProjectileSystem(), 4.0)
        self.assertGreater(eater.x, start + 60)  # into or through the bone wall
        self.assertGreater(sum(1 for y in range(60, 140) for x in range(150, 250) if world.get(x, y) != BONE), 300)

    def test_breath_sucks_the_player_in_and_exhales_spores(self) -> None:
        from src.enemies import INHALE_TIME, spawn_boss

        world = World(500, 200, seed=1)
        breath = spawn_boss("atem", (100, 100), random.Random(1))
        breath.alerted = True
        manager = EnemyManager()
        manager.creatures.append(breath)
        player = Player(300, 200 - 2 - PLAYER_HEIGHT)
        player.hp = player.max_hp = 1e9
        projectiles = ProjectileSystem()
        start = player.x
        run(world, manager, player, projectiles, INHALE_TIME * 0.9)
        self.assertLess(player.x, start - 40)
        before = len(projectiles.items)
        run(world, manager, player, projectiles, INHALE_TIME * 0.1 + 0.1)  # the breath turns
        self.assertGreaterEqual(len(projectiles.items) - before, 6)
