import unittest

from src.materials import (
    AIR,
    FIRE,
    KIND,
    LIGHT_LEVELS,
    MATERIAL_COUNT,
    MATERIALS,
    SOLID,
    VARIANTS,
    build_palette,
)
from src.reactions import REACTIONS, Reaction, build_tables, to_fixed


class TestMaterials(unittest.TestCase):
    def test_palette_covers_every_variant_and_light_level(self) -> None:
        self.assertEqual(len(build_palette()), MATERIAL_COUNT * VARIANTS * LIGHT_LEVELS)
        self.assertEqual(len(build_palette(lit=False)), MATERIAL_COUNT * VARIANTS)

    def test_palette_index_fits_a_byte(self) -> None:
        self.assertLessEqual(MATERIAL_COUNT * VARIANTS * LIGHT_LEVELS, 256)

    def test_darker_light_levels_are_darker(self) -> None:
        palette = build_palette()
        for base in range(0, len(palette), LIGHT_LEVELS):
            levels = [sum(palette[base + level]) for level in range(LIGHT_LEVELS)]
            self.assertEqual(levels, sorted(levels))

    def test_every_material_has_a_german_name(self) -> None:
        names = [m.name_de for m in MATERIALS]
        self.assertEqual(len(set(names)), len(names))
        self.assertTrue(all(names))

    def test_lifetimes_fit_a_byte(self) -> None:
        for material in MATERIALS:
            for value in (*material.life, *material.burn_life):
                self.assertTrue(0 <= value <= 255, material)

    def test_solids_have_maximum_density(self) -> None:
        for index, material in enumerate(MATERIALS):
            if KIND[index] == SOLID:
                self.assertEqual(material.density, 255, material.name_de)


class TestReactionTable(unittest.TestCase):
    def test_tables_have_one_entry_per_pair(self) -> None:
        a, b, chance = build_tables()
        size = MATERIAL_COUNT * MATERIAL_COUNT
        self.assertEqual((len(a), len(b), len(chance)), (size, size, size))
        self.assertEqual(sum(1 for c in chance if c), len(REACTIONS))

    def test_entries_land_at_actor_times_n_plus_neighbour(self) -> None:
        a, b, chance = build_tables()
        for rule in REACTIONS:
            index = rule.actor * MATERIAL_COUNT + rule.neighbour
            self.assertEqual((a[index], b[index]), (rule.actor_into, rule.neighbour_into))
            self.assertGreater(chance[index], 0)

    def test_results_are_valid_materials(self) -> None:
        for rule in REACTIONS:
            for material in (rule.actor, rule.neighbour, rule.actor_into, rule.neighbour_into):
                self.assertTrue(0 <= material < MATERIAL_COUNT, rule)

    def test_air_cannot_act(self) -> None:
        with self.assertRaises(ValueError):
            build_tables((Reaction(AIR, FIRE, AIR, AIR, 0.5),))

    def test_duplicates_are_rejected(self) -> None:
        rule = Reaction(FIRE, AIR, FIRE, FIRE, 0.1)
        with self.assertRaises(ValueError):
            build_tables((rule, rule))

    def test_invalid_chance_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_tables((Reaction(FIRE, AIR, FIRE, FIRE, 0.0),))
        with self.assertRaises(ValueError):
            build_tables((Reaction(FIRE, AIR, FIRE, FIRE, 1.5),))

    def test_tiny_chances_do_not_round_to_zero(self) -> None:
        _, _, chance = build_tables((Reaction(FIRE, AIR, FIRE, FIRE, 1e-9),))
        self.assertEqual(chance[FIRE * MATERIAL_COUNT + AIR], 1)

    def test_fixed_point_conversion(self) -> None:
        self.assertEqual(to_fixed(0.0), 0)
        self.assertEqual(to_fixed(0.5), 32768)
        self.assertEqual(to_fixed(1.0), 65535)


if __name__ == "__main__":
    unittest.main()


class TestHotAndFoul(unittest.TestCase):
    def test_glutblut_ignites_tallow_and_cools_in_blood(self) -> None:
        from src.materials import BLOOD, CRUST, FIRE, MAGMA, TALLOW
        from src.world import World

        world = World(80, 60, seed=1)
        for x in range(10, 70):
            for y in range(50, 58):
                world.set_cell(x, y, TALLOW)
        for x in range(30, 40):
            world.set_cell(x, 40, MAGMA)
        fire_seen = False
        for _ in range(200):
            world.step()
            fire_seen = fire_seen or world.count(FIRE) > 0
        self.assertTrue(fire_seen)
        world = World(80, 60, seed=1)
        for x in range(10, 70):
            for y in range(50, 58):
                world.set_cell(x, y, BLOOD)
        for x in range(30, 40):
            world.set_cell(x, 45, MAGMA)
        for _ in range(200):
            world.step()
        self.assertGreater(world.count(CRUST), 3)

    def test_pus_poisons(self) -> None:
        from src.body import POISON_DPS, Body
        from src.materials import PUS
        from src.world import World

        world = World(60, 40, seed=1)
        body = Body(20, 10, 4, 4, 100)
        world.set_cell(19, 12, PUS, force=True)
        body.apply_environment(world, 0.01)
        self.assertGreater(body.poisoned, 0)
        world.set_cell(19, 12, 0, force=True)
        hp = body.hp
        body.apply_environment(world, 1.0)
        self.assertAlmostEqual(hp - body.hp, POISON_DPS, places=3)

    def test_palette_still_fits_a_byte(self) -> None:
        self.assertLessEqual(MATERIAL_COUNT * VARIANTS * LIGHT_LEVELS, 256)


class TestNerveCurrent(unittest.TestCase):
    def test_current_runs_along_sinew_once_and_heals(self) -> None:
        from src.materials import SINEW, SPARK, SPENT
        from src.world import World

        world = World(200, 40, seed=1)
        for x in range(10, 190):
            world.set_cell(x, 20, SINEW)
        self.assertGreaterEqual(world.electrify(10, 20, 1), 1)
        reached = 0
        for _ in range(260):  # the wave moves about one cell per tick
            world.step()
            charged = [x for x in range(200) if world.get(x, 20) == SPARK]
            if charged:
                reached = max(reached, max(charged))
        self.assertGreater(reached, 150)  # the wave travelled along the strand
        self.assertEqual(world.count(SPARK), 0)  # and died out instead of looping
        for _ in range(3000):
            world.step()
        self.assertEqual(world.count(SPENT), 0)  # spent sinew healed
        self.assertGreaterEqual(world.count(SINEW), 172)  # a spark may singe a cell or two

    def test_current_hurts_bodies_touching_it(self) -> None:
        from src.materials import HAZARD_DPS, SPARK

        self.assertGreater(HAZARD_DPS[SPARK], 20)
