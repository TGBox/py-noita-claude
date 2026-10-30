import tempfile
import unittest
from pathlib import Path

from src.records import Records, format_time, load, save


class TestRecords(unittest.TestCase):
    def test_add_run_tracks_bests(self) -> None:
        records = Records()
        self.assertTrue(records.add_run(won=False, depth=2, kills=10, pearls=50, time=300))
        self.assertFalse(records.add_run(won=False, depth=1, kills=3, pearls=5, time=60))
        self.assertTrue(records.add_run(won=True, depth=4, kills=40, pearls=400, time=1500))
        self.assertTrue(records.add_run(won=True, depth=4, kills=40, pearls=400, time=1200))
        self.assertEqual((records.runs, records.wins, records.best_depth), (4, 2, 4))
        self.assertEqual(records.kills, 93)
        self.assertEqual(records.best_time, 1200)
        self.assertIn("Schnellster Sieg: 20:00", records.lines_de())

    def test_no_lines_before_the_first_run(self) -> None:
        self.assertEqual(Records().lines_de(), [])
        self.assertEqual(format_time(65.9), "1:05")

    def test_round_trip_and_broken_files(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sub" / "records.json"
            self.assertEqual(load(path), Records())
            records = Records(runs=3, wins=1, best_depth=4, best_time=999.5)
            self.assertTrue(save(records, path))
            self.assertEqual(load(path), records)
            path.write_text("{kaputt", encoding="utf-8")
            self.assertEqual(load(path), Records())
            path.write_text('{"runs": "viele", "wins": 2, "unknown": 1}', encoding="utf-8")
            self.assertEqual(load(path), Records(wins=2))


if __name__ == "__main__":
    unittest.main()


class TestKodex(unittest.TestCase):
    def test_discover_blocks_and_creatures(self) -> None:
        records = Records()
        self.assertTrue(records.discover("block", "funke"))
        self.assertFalse(records.discover("block", "funke"))
        self.assertTrue(records.discover("creature", "made"))
        self.assertFalse(records.discover("creature", "made"))
        self.assertEqual(records.creatures, {"made": 2})

    def test_kodex_survives_a_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "records.json"
            records = Records(blocks=["funke", "nadel"], creatures={"herz": 1})
            save(records, path)
            self.assertEqual(load(path), records)
            path.write_text('{"blocks": ["funke", 3], "creatures": {"made": "x", "herz": 2}}')
            self.assertEqual(load(path), Records(blocks=["funke"], creatures={"herz": 2}))

    def test_codex_lists_every_block_and_creature(self) -> None:
        from src.enemies import SPECIES
        from src.spells import BLOCKS

        try:
            from src.menus import codex_entries
        except ImportError:  # pygame missing in this environment
            self.skipTest("pygame not installed")
        blocks, creatures = codex_entries(Records(blocks=["funke"], creatures={"made": 4}))
        self.assertEqual(len(blocks), len(BLOCKS))
        self.assertEqual(len(creatures), len(SPECIES))
        self.assertEqual(sum(seen for _, seen in blocks), 1)
        self.assertIn("Fleischmade: 4 getötet", [text for text, _ in creatures])


class TestSavedRun(unittest.TestCase):
    def test_save_load_delete(self) -> None:
        from src.records import delete_run, load_run, save_run

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "lauf.json"
            self.assertIsNone(load_run(path))
            self.assertTrue(save_run({"depth_index": 1}, path))
            self.assertEqual(load_run(path), {"depth_index": 1})
            delete_run(path)
            self.assertIsNone(load_run(path))
            delete_run(path)  # deleting twice is fine
