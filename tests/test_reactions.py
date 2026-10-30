import unittest

from src.materials import (
    AIR,
    FIRE,
    KIND,
    MATERIAL_COUNT,
    MATERIALS,
    SOLID,
    VARIANTS,
    build_palette,
)
from src.reactions import REACTIONS, Reaction, build_tables, to_fixed


class TestMaterials(unittest.TestCase):
    def test_palette_covers_every_variant(self) -> None:
        self.assertEqual(len(build_palette()), MATERIAL_COUNT * VARIANTS)

    def test_palette_index_fits_a_byte(self) -> None:
        self.assertLess(MATERIAL_COUNT * VARIANTS, 256)

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
