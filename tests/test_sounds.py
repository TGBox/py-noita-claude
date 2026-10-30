import unittest
from array import array

from src.sounds import SAMPLE_RATE, mix, noise, sequence, synthesize_all, tone


class TestSounds(unittest.TestCase):
    def test_every_event_has_an_audible_sound(self) -> None:
        sounds = synthesize_all()
        for name in ("cast", "blast", "blast_big", "hurt", "kill", "pickup", "pearl", "buy",
                     "perk", "descend", "death", "victory"):  # fmt: skip
            data = sounds[name]
            self.assertEqual(len(data) % 2, 0, name)
            samples = array("h", data)
            self.assertGreater(max(abs(v) for v in samples), 1000, name)
            self.assertLess(len(samples) / SAMPLE_RATE, 2.0, name)

    def test_tone_length_and_clipping(self) -> None:
        samples = array("h", tone(440, 440, 0.5, volume=2.0))
        self.assertEqual(len(samples), SAMPLE_RATE // 2)
        self.assertLessEqual(max(abs(v) for v in samples), 32767)

    def test_mix_and_sequence(self) -> None:
        a, b = tone(440, 440, 0.1), noise(0.2)
        self.assertEqual(len(mix(a, b)), max(len(a), len(b)))
        self.assertEqual(len(sequence(a, b)), len(a) + len(b))


if __name__ == "__main__":
    unittest.main()
