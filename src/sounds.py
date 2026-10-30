"""Procedurally synthesised sound effects (no audio files, no numpy).

Every sound is 16-bit signed mono PCM at ``SAMPLE_RATE``. This module is pure
Python so it can be tested without an audio device; ``src/audio.py`` plays them.
"""

from __future__ import annotations

import math
import random
from array import array

SAMPLE_RATE = 22050


def _render(duration: float, sample) -> bytes:
    count = int(duration * SAMPLE_RATE)
    data = array("h", (max(-32767, min(32767, int(sample(i / SAMPLE_RATE, i) * 32767))) for i in range(count)))
    return data.tobytes()


def tone(
    start_hz: float,
    end_hz: float,
    duration: float,
    volume: float = 0.4,
    square: bool = False,
    decay: float = 6.0,
) -> bytes:
    """A pitch sweep with exponential decay."""
    phase = [0.0]

    def sample(t: float, _i: int) -> float:
        freq = start_hz + (end_hz - start_hz) * (t / duration)
        phase[0] += 2 * math.pi * freq / SAMPLE_RATE
        wave = math.sin(phase[0])
        if square:
            wave = 1.0 if wave >= 0 else -1.0
        attack = min(1.0, t * 400)
        return wave * volume * attack * math.exp(-decay * t)

    return _render(duration, sample)


def noise(duration: float, volume: float = 0.5, decay: float = 8.0, smooth: float = 0.6) -> bytes:
    """Low-passed noise burst (explosions, splats)."""
    rng = random.Random(1)
    last = [0.0]

    def sample(t: float, _i: int) -> float:
        last[0] = last[0] * smooth + rng.uniform(-1, 1) * (1 - smooth)
        return last[0] * volume * 2.5 * math.exp(-decay * t)

    return _render(duration, sample)


def mix(*parts: bytes) -> bytes:
    """Overlay several sounds (the result is as long as the longest part)."""
    arrays = [array("h", part) for part in parts]
    length = max(len(a) for a in arrays)
    out = array("h", bytes(2 * length))
    for a in arrays:
        for i, value in enumerate(a):
            out[i] = max(-32767, min(32767, out[i] + value))
    return out.tobytes()


def sequence(*parts: bytes) -> bytes:
    """Play sounds one after another."""
    return b"".join(parts)


def synthesize_all() -> dict[str, bytes]:
    """Every sound effect of the game, by event name."""
    return {
        "cast": tone(900, 520, 0.07, volume=0.18, square=True, decay=25),
        "blast": noise(0.3, volume=0.45, decay=11, smooth=0.55),
        "blast_big": mix(noise(0.8, volume=0.6, decay=4.5, smooth=0.85), tone(70, 40, 0.8, 0.5, decay=4)),
        "hurt": tone(230, 140, 0.13, volume=0.3, square=True, decay=12),
        "kill": mix(noise(0.14, volume=0.35, decay=18, smooth=0.5), tone(320, 110, 0.14, 0.25)),
        "pickup": sequence(tone(660, 660, 0.06, 0.3, decay=10), tone(990, 990, 0.08, 0.3, decay=10)),
        "pearl": tone(1320, 1760, 0.05, volume=0.18, decay=20),
        "buy": sequence(tone(520, 520, 0.05, 0.3), tone(780, 780, 0.05, 0.3), tone(1040, 1040, 0.08, 0.3)),
        "perk": sequence(*(tone(f, f, 0.09, 0.3, decay=5) for f in (440, 554, 659, 880))),
        "descend": tone(110, 50, 0.9, volume=0.5, decay=2.5),
        "death": tone(300, 55, 1.3, volume=0.45, square=True, decay=1.8),
        "victory": sequence(*(tone(f, f, 0.16, 0.35, decay=3) for f in (392, 494, 587, 784, 988))),
    }
