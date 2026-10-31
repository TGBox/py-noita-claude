import tempfile
import unittest
from array import array
from pathlib import Path

from src.music import LOOP_SECONDS, MOODS, ambient
from src.options import STEPS, Options, load, save
from src.sounds import SAMPLE_RATE


class TestOptions(unittest.TestCase):
    def test_change_clamps_volumes_and_toggles_switches(self) -> None:
        options = Options(effects=STEPS)
        options.change("effects", 1)
        self.assertEqual(options.effects, STEPS)
        options.change("music", -99)
        self.assertEqual(options.music, 0)
        options.change("fullscreen", 1)
        self.assertTrue(options.fullscreen)
        self.assertEqual(options.label("fullscreen", "Vollbild"), "Vollbild: an")
        self.assertTrue(options.label("effects", "Effekte").startswith("Effekte: ||||"))

    def test_round_trip_and_bad_values(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "optionen.json"
            self.assertEqual(load(path), Options())
            save(Options(effects=2, music=9, lighting=False), path)
            self.assertEqual(load(path), Options(effects=2, music=9, lighting=False))
            path.write_text('{"effects": 99, "music": "laut", "shake": 1}')
            self.assertEqual(load(path), Options(effects=STEPS))


class TestMusic(unittest.TestCase):
    def test_every_mood_loops_seamlessly(self) -> None:
        for mood in ("lunge", "herzkammer"):
            samples = array("h", ambient(mood))
            self.assertEqual(len(samples), int(LOOP_SECONDS * SAMPLE_RATE))
            peak = max(abs(v) for v in samples)
            self.assertGreater(peak, 8000)
            seam = abs(samples[-1] - samples[0])
            self.assertLess(seam, peak * 0.1, mood)  # no click when the loop restarts
        self.assertIn("sanktum", MOODS)

    def test_music_cache(self) -> None:
        try:
            from src.audio import cached_loop
        except ImportError:
            self.skipTest("pygame not installed")
        with tempfile.TemporaryDirectory() as folder:
            first = cached_loop(Path(folder), "sanktum")
            self.assertTrue(any(Path(folder).glob("sanktum_*.wav")))
            self.assertEqual(cached_loop(Path(folder), "sanktum"), first)


if __name__ == "__main__":
    unittest.main()
