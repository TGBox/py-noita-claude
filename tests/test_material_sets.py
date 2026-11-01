"""Material sets per universe (work package T1): switching, stand-ins, saving by key."""

import unittest
from dataclasses import replace

from src import materials as mat
from src.flask import Flask
from src.run import Run, _flask_from
from src.world import World


def _count(world: World, key: str) -> int:
    material = mat.resolve(key)
    return sum(1 for cell in world.grid if cell == material)


class MaterialSetCase(unittest.TestCase):
    def tearDown(self) -> None:
        mat.activate(mat.DEFAULT_SET)


class TestSets(MaterialSetCase):
    def test_every_set_fits_the_palette_and_names_resolve(self) -> None:
        for material_set in mat.SETS.values():
            mat.validate(material_set)
            mat.activate(material_set)
            self.assertLessEqual(mat.MATERIAL_COUNT, mat.MAX_MATERIALS)
            self.assertEqual(len(mat.build_palette()), mat.MATERIAL_COUNT * 12)
            for name, key in mat.NAMES.items():
                found = mat.resolve(key)
                self.assertIsNotNone(found, f"{material_set.key}: {name}")
                self.assertNotEqual(found, mat.AIR, f"{material_set.key}: {name}")

    def test_default_set_keeps_the_old_ids(self) -> None:
        self.assertEqual((mat.BONE, mat.BLOOD, mat.ACID, mat.ENAMEL), (2, 6, 9, 20))
        self.assertEqual(mat.MATERIAL_COUNT, 21)

    def test_activation_rewrites_ids_and_tables_in_place(self) -> None:
        kind = mat.KIND
        mat.activate(mat.AKTENHALDE)
        self.assertIs(mat.KIND, kind)
        self.assertEqual(mat.KEYS[mat.BLOOD], "tinte")  # blood stands in as ink
        self.assertEqual(mat.KEYS[mat.FLESH], "papier")
        self.assertTrue(mat.has("papier"))
        self.assertFalse(mat.has("blood"))
        self.assertEqual(len(mat.KIND), mat.MATERIAL_COUNT)
        self.assertGreater(mat.FLAMMABILITY[mat.id_of("papier")], 0.5)

    def test_invalid_sets_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            mat.validate(mat.MaterialSet("x", ("bedrock", "air")))
        with self.assertRaises(ValueError):
            mat.validate(mat.MaterialSet("x", ("air", "bedrock", "spark", "fire")))
        too_many = ("air", "bedrock", *[k for k in mat.LIBRARY if k not in ("air", "bedrock")])
        with self.assertRaises(ValueError):
            mat.validate(mat.MaterialSet("x", too_many))


class TestFileUniverseMaterials(MaterialSetCase):
    def setUp(self) -> None:
        mat.activate(mat.AKTENHALDE)
        self.world = World(80, 60, seed=3)

    def test_paper_burns_down_to_ash(self) -> None:
        papier = mat.id_of("papier")
        for y in range(30, 40):
            for x in range(20, 60):
                self.world.set_cell(x, y, papier)
        before = _count(self.world, "papier")
        self.world.ignite(40, 30)
        for _ in range(300):
            self.world.step()
        self.assertLess(_count(self.world, "papier"), before // 2)

    def test_ink_soaked_paper_does_not_burn(self) -> None:
        soaked = mat.id_of("tintenpapier")
        self.assertEqual(mat.FLAMMABILITY[soaked], 0.0)

    def test_sealing_wax_sets_in_the_air(self) -> None:
        wax = mat.id_of("siegellack")
        for x in range(30, 50):
            self.world.set_cell(x, 50, wax)
        for _ in range(900):
            self.world.step()
        self.assertGreater(_count(self.world, "lack"), 0)


class TestUniverseSwitch(MaterialSetCase):
    def test_flask_keeps_its_content_by_key(self) -> None:
        flask = Flask(mat.ACID, 100)
        self.assertEqual(flask.key, "acid")
        mat.activate(mat.AKTENHALDE)
        self.assertEqual(mat.KEYS[flask.material], "stempelfarbe")  # pours its stand-in
        self.assertEqual(flask.key, "acid")
        mat.activate(mat.KOERPER)
        self.assertEqual(flask.material, 9)

    def test_old_saves_with_flask_ids_still_load(self) -> None:
        self.assertEqual(_flask_from([9, 120]).key, "acid")
        self.assertEqual(_flask_from(["tinte", 50]).key, "tinte")
        self.assertIsNone(_flask_from(["papier", 50]))  # not a liquid
        self.assertIsNone(_flask_from(["unbekannt", 50]))

    def test_two_universes_in_a_row_and_save_across_the_switch(self) -> None:
        run = Run(seed=11)
        first = run.route[0]
        self.assertEqual(run.world.material_set, "koerper")
        files = replace(run.route[1], key="aktentest", material_set="aktenhalde")
        run.route = (first, files, *run.route[2:])
        run.flasks = [Flask(mat.BLOOD, 80)]
        run.enter_depth(1)
        self.assertEqual(run.world.material_set, "aktenhalde")
        self.assertEqual(mat.ACTIVE.key, "aktenhalde")
        self.assertGreater(_count(run.world, "papier"), 1000)  # the flesh walls are paper now
        saved = run.save_state()

        mat.activate(mat.KOERPER)
        other = Run(seed=99)
        other.restore(saved)
        self.assertEqual(mat.ACTIVE.key, "aktenhalde")
        self.assertEqual(other.world.material_set, "aktenhalde")
        self.assertEqual(bytes(other.world.grid), bytes(run.world.grid))
        self.assertEqual(other.flasks[0].key, "blood")

        other.enter_depth(0)
        self.assertEqual(other.world.material_set, "koerper")
        self.assertEqual(other.flasks[0].material, 6)
        self.assertFalse(mat.has("papier"))


if __name__ == "__main__":
    unittest.main()
