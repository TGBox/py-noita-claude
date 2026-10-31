"""Procedural ambient music: slow drones, breathing noise and a distant heartbeat.

Each loop is generated once (pure Python, no audio device needed) and loops
seamlessly: every tone completes a whole number of cycles over the loop and the
noise bed is cross-faded with its own start.
"""

from __future__ import annotations

import math
import random
from array import array

from src.sounds import PEAK, SAMPLE_RATE

LOOP_SECONDS = 12.0

# Per mood: drone root (Hz), heartbeat (beats per minute, 0 = none), noise level, brightness
MOODS: dict[str, tuple[float, float, float, float]] = {
    "schlund": (55.0, 52, 0.25, 500.0),
    "magen": (49.0, 60, 0.35, 380.0),
    "knochenmark": (51.9, 56, 0.2, 650.0),
    "gedaerm": (46.25, 66, 0.3, 420.0),
    "leber": (43.65, 62, 0.4, 340.0),
    "lunge": (58.3, 48, 0.55, 900.0),  # breathing
    "herzkammer": (41.2, 84, 0.25, 300.0),
    "sanktum": (65.4, 0, 0.12, 700.0),
    "speiseroehre": (55.0, 50, 0.3, 560.0),
    "zahnhoehle": (61.7, 46, 0.18, 760.0),
    "pansen": (46.25, 58, 0.4, 360.0),
    "rueckenmark": (49.0, 54, 0.22, 700.0),
    "blinddarm": (43.65, 68, 0.35, 380.0),
    "niere": (51.9, 60, 0.3, 480.0),
    "milz": (41.2, 70, 0.3, 320.0),
    "bronchien": (61.7, 46, 0.6, 1000.0),
    "rachen": (55.0, 54, 0.3, 520.0),
    "kehlkopf": (65.4, 44, 0.25, 820.0),
    "zungengrund": (49.0, 50, 0.3, 450.0),
    "labmagen": (46.25, 62, 0.4, 340.0),
    "magenpfoertner": (49.0, 58, 0.35, 400.0),
    "beckenhoehle": (51.9, 52, 0.2, 640.0),
    "schaedel": (58.3, 48, 0.15, 760.0),
    "duenndarm": (46.25, 64, 0.3, 430.0),
    "dickdarm": (41.2, 66, 0.35, 360.0),
    "gallenblase_biom": (43.65, 60, 0.45, 330.0),
    "bauchspeicheldruese": (46.25, 62, 0.4, 380.0),
    "lymphknoten": (51.9, 56, 0.35, 470.0),
    "zwerchfell": (55.0, 44, 0.55, 860.0),
    "luftroehre": (61.7, 42, 0.65, 1050.0),
    "herzvorhof": (38.9, 88, 0.25, 290.0),
    "wurmfortsatz": (43.65, 66, 0.35, 350.0),
    "nebenniere": (46.25, 70, 0.3, 420.0),
}


def _whole_cycles(frequency: float) -> float:
    """Nearest frequency that fits a whole number of cycles into the loop."""
    return max(1, round(frequency * LOOP_SECONDS)) / LOOP_SECONDS


def ambient(mood: str) -> bytes:
    root, bpm, noise_level, brightness = MOODS.get(mood, MOODS["schlund"])
    n = int(LOOP_SECONDS * SAMPLE_RATE)
    rng = random.Random(sum(map(ord, mood)))
    voices = [  # (frequency, level, lfo rate) - root, fifth, octave, slightly detuned
        (_whole_cycles(root), 0.5, _whole_cycles(0.083)),
        (_whole_cycles(root * 1.003), 0.35, _whole_cycles(0.125)),
        (_whole_cycles(root * 1.5), 0.2, _whole_cycles(0.167)),
        (_whole_cycles(root * 2.0), 0.12, _whole_cycles(0.25)),
    ]
    breath_rate = _whole_cycles(0.25)  # four breaths per loop
    beat = 60.0 / bpm if bpm else 0.0
    beats = max(1, round(LOOP_SECONDS / beat)) if beat else 0
    beat = LOOP_SECONDS / beats if beats else 0.0

    tau = 2 * math.pi
    alpha = 1.0 - math.exp(-tau * brightness / SAMPLE_RATE)
    low = 0.0
    noise_bed = []
    for _ in range(n):
        low += alpha * (rng.uniform(-1, 1) - low)
        noise_bed.append(low)
    fade = SAMPLE_RATE // 2  # cross-fade the noise loop seam
    for i in range(fade):
        w = i / fade
        noise_bed[i] = noise_bed[i] * w + noise_bed[n - fade + i] * (1 - w)
    noise_peak = max(abs(v) for v in noise_bed) or 1.0

    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        value = 0.0
        for frequency, level, lfo in voices:
            swell = 0.65 + 0.35 * math.sin(tau * lfo * t)
            value += level * swell * math.sin(tau * frequency * t)
        breath = 0.5 - 0.5 * math.cos(tau * breath_rate * t)
        value += noise_level * breath * noise_bed[i] / noise_peak
        if beats:
            phase = t % beat
            for offset, strength in ((0.0, 1.0), (0.22, 0.6)):  # lub-dub
                local = phase - offset
                if 0 <= local < 0.18:
                    value += 0.6 * strength * math.exp(-local * 26) * math.sin(tau * 48 * local)
        out.append(value)
    peak = max(abs(v) for v in out) or 1.0
    scale = PEAK * 0.8 / peak * 32767
    return array("h", (int(v * scale) for v in out)).tobytes()
