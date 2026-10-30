import tempfile
import unittest
from array import array
from pathlib import Path

from src.sounds import PEAK, SAMPLE_RATE, custom_files, synthesize_all

EVENTS = ("cast", "blast", "blast_big", "hurt", "kill", "pickup", "pearl", "buy",
          "perk", "descend", "death", "victory")  # fmt: skip


def samples(data: bytes) -> array:
    return array("h", data)


class TestSounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sounds = synthesize_all()

    def test_every_event_has_audible_variants(self) -> None:
        for name in EVENTS:
            self.assertTrue(self.sounds[name], name)
            for data in self.sounds[name]:
                values = samples(data)
                self.assertGreater(max(abs(v) for v in values), 3000, name)
                self.assertLess(len(values) / SAMPLE_RATE, 3.0, name)

    def test_no_clicks_at_the_edges(self) -> None:
        for name, variants in self.sounds.items():
            for data in variants:
                values = samples(data)
                edges = [*values[:10], *values[-10:]]
                self.assertLess(max(abs(v) for v in edges), 400, name)  # below -38 dBFS

    def test_never_louder_than_the_peak(self) -> None:
        for name, variants in self.sounds.items():
            for data in variants:
                self.assertLessEqual(max(abs(v) for v in samples(data)), PEAK * 32767 + 1, name)

    def test_sounds_are_not_shrill(self) -> None:
        # Brightness estimate from the slope energy: sqrt(E[dx^2] / E[x^2]) ~ 2*pi*f/sr.
        for name, variants in self.sounds.items():
            for data in variants:
                values = samples(data)
                energy = sum(v * v for v in values)
                slope = sum((values[i] - values[i - 1]) ** 2 for i in range(1, len(values)))
                brightness = (slope / energy) ** 0.5 * SAMPLE_RATE / 6.283
                self.assertLess(brightness, 2000, name)

    def test_custom_files_override_by_name(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for file in ("cast.wav", "cast_2.ogg", "castle.wav", "kill.mp3", "pearl.WAV"):
                (directory / file).write_bytes(b"")
            self.assertEqual(
                [p.name for p in custom_files(directory, "cast")], ["cast.wav", "cast_2.ogg"]
            )
            self.assertEqual([p.name for p in custom_files(directory, "pearl")], ["pearl.WAV"])
            self.assertEqual(custom_files(directory, "kill"), [])
            self.assertEqual(custom_files(directory / "missing", "cast"), [])


if __name__ == "__main__":
    unittest.main()
