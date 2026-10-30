"""Procedurally synthesised sound effects (no audio files, no numpy).

The palette is low, muffled and wet to fit the organic horror theme: sine tones
with slow pitch drops, low-passed noise for squelches and rumbles. Every sound has
a smooth fade-in and fade-out (no clicks) and is normalised to the same peak.

All sounds are 16-bit signed mono PCM at ``SAMPLE_RATE``. This module is pure
Python so it can be tested without an audio device; ``src/audio.py`` plays them.
"""

from __future__ import annotations

import math
import random
import sys
from array import array
from collections.abc import Callable, Sequence
from pathlib import Path

SAMPLE_RATE = 22050
PEAK = 0.5  # -6 dBFS
FADE_IN = 0.006  # seconds
FADE_OUT = 0.03  # seconds

Signal = list[float]
Curve = Callable[[float], float]  # time in seconds -> value


# ------------------------------------------------------------------ building blocks


def _samples(duration: float) -> int:
    return max(1, int(duration * SAMPLE_RATE))


def sweep(start: float, end: float, duration: float, shape: float = 1.0) -> Curve:
    """Exponential-ish glide from ``start`` to ``end`` (shape > 1 drops faster)."""

    def curve(t: float) -> float:
        progress = min(1.0, max(0.0, t / duration)) ** (1.0 / shape)
        return start * (end / start) ** progress

    return curve


def sine(frequency: Curve, duration: float, harmonics: Sequence[float] = ()) -> Signal:
    """A sine with a time-varying frequency and optional overtones (relative levels)."""
    out: Signal = []
    phase = 0.0
    for i in range(_samples(duration)):
        t = i / SAMPLE_RATE
        phase += 2 * math.pi * frequency(t) / SAMPLE_RATE
        value = math.sin(phase)
        for k, level in enumerate(harmonics, start=2):
            value += level * math.sin(phase * k)
        out.append(value)
    return out


def noise(duration: float, cutoff: Curve, seed: int = 1, poles: int = 2) -> Signal:
    """White noise through a time-varying low-pass filter (``poles`` one-pole stages)."""
    rng = random.Random(seed)
    state = [0.0] * poles
    out: Signal = []
    for i in range(_samples(duration)):
        t = i / SAMPLE_RATE
        alpha = 1.0 - math.exp(-2 * math.pi * cutoff(t) / SAMPLE_RATE)
        value = rng.uniform(-1.0, 1.0)
        for k in range(poles):
            state[k] += alpha * (value - state[k])
            value = state[k]
        out.append(value)
    return out


def envelope(signal: Signal, attack: float, decay: float, sustain: float = 0.0) -> Signal:
    """Attack ramp, then exponential decay towards ``sustain`` (0..1)."""
    out: Signal = []
    for i, value in enumerate(signal):
        t = i / SAMPLE_RATE
        level = t / attack if t < attack else sustain + (1 - sustain) * math.exp(-(t - attack) * decay)
        out.append(value * level)
    return out


def mix(*parts: tuple[Signal, float]) -> Signal:
    """Sum (signal, gain) pairs; the result is as long as the longest part."""
    length = max(len(signal) for signal, _ in parts)
    out = [0.0] * length
    for signal, gain in parts:
        for i, value in enumerate(signal):
            out[i] += value * gain
    return out


def concat(*parts: Signal, gap: float = 0.0) -> Signal:
    out: Signal = []
    for index, part in enumerate(parts):
        if index and gap:
            out.extend([0.0] * _samples(gap))
        out.extend(part)
    return out


def finish(signal: Signal, gain: float = 1.0) -> bytes:
    """Fade both ends, normalise to ``PEAK * gain`` and encode as 16-bit PCM."""
    length = len(signal)
    fade_in, fade_out = _samples(FADE_IN), _samples(FADE_OUT)
    shaped = list(signal)
    for i in range(min(fade_in, length)):
        shaped[i] *= 0.5 - 0.5 * math.cos(math.pi * i / fade_in)
    for i in range(min(fade_out, length)):
        shaped[length - 1 - i] *= 0.5 - 0.5 * math.cos(math.pi * i / fade_out)
    peak = max((abs(v) for v in shaped), default=0.0) or 1.0
    scale = PEAK * gain / peak * 32767
    return array("h", (int(v * scale) for v in shaped)).tobytes()


# ----------------------------------------------------------------------- sounds


def cast(variant: int) -> bytes:
    """A soft wet whoosh with a small fleshy pop."""
    pitch = (1.0, 0.86, 1.15)[variant % 3]
    whoosh = envelope(noise(0.14, sweep(2600 * pitch, 500 * pitch, 0.14), seed=10 + variant), 0.012, 28)
    pop = envelope(sine(sweep(170 * pitch, 90 * pitch, 0.08), 0.08), 0.004, 40)
    return finish(mix((whoosh, 1.0), (pop, 0.6)), gain=0.7)


def blast(big: bool) -> bytes:
    """A deep thump with a muffled rumble tail."""
    duration = 1.1 if big else 0.4
    thump = envelope(sine(sweep(95 if big else 130, 32 if big else 48, duration, 2.0), duration), 0.008, 5 if big else 11)
    rumble = envelope(noise(duration, sweep(900 if big else 1400, 120, duration), seed=3), 0.01, 3.5 if big else 9)
    return finish(mix((thump, 1.0), (rumble, 0.9)))


def hurt() -> bytes:
    """A muffled, wet thud."""
    thud = envelope(sine(sweep(190, 85, 0.16), 0.16, harmonics=(0.3,)), 0.004, 18)
    squelch = envelope(noise(0.12, sweep(700, 250, 0.12), seed=5), 0.004, 30)
    return finish(mix((thud, 1.0), (squelch, 0.7)), gain=0.85)


def kill() -> bytes:
    """A short splat."""
    splat = envelope(noise(0.22, sweep(1600, 300, 0.22, 1.5), seed=7), 0.003, 16)
    body = envelope(sine(sweep(110, 60, 0.18), 0.18), 0.003, 20)
    return finish(mix((splat, 1.0), (body, 0.8)), gain=0.8)


def chime(frequency: float, duration: float) -> Signal:
    """A soft bell-like tone (sine with gentle overtones)."""
    return envelope(sine(lambda _t: frequency, duration, harmonics=(0.25, 0.08)), 0.005, 9)


def pickup() -> bytes:
    return finish(concat(chime(523.0, 0.16), chime(784.0, 0.22), gap=0.02), gain=0.6)


def pearl() -> bytes:
    return finish(envelope(sine(lambda _t: 1047.0, 0.16, harmonics=(0.2,)), 0.004, 22), gain=0.4)


def buy() -> bytes:
    notes = [chime(f, 0.18) for f in (523.0, 659.0, 784.0)]
    return finish(concat(*notes, gap=0.015), gain=0.6)


def chord(frequencies: Sequence[float], duration: float, attack: float) -> Signal:
    voices = [envelope(sine(lambda _t, f=f: f, duration, harmonics=(0.15,)), attack, 2.5) for f in frequencies]
    return mix(*((voice, 1.0 / len(voices)) for voice in voices))


def perk() -> bytes:
    """A slow, warm swell."""
    return finish(chord((220.0, 261.6, 329.6, 440.0), 1.0, 0.2), gain=0.7)


def descend() -> bytes:
    """A deep, rumbling drop."""
    drone = envelope(sine(sweep(90, 42, 1.4), 1.4, harmonics=(0.4, 0.2)), 0.25, 1.8)
    rumble = envelope(noise(1.4, lambda _t: 220.0, seed=9), 0.3, 1.6)
    return finish(mix((drone, 1.0), (rumble, 0.6)), gain=0.9)


def death() -> bytes:
    """Two low, slowly beating tones sinking away."""
    low = sine(sweep(110, 70, 1.8), 1.8)
    beat = sine(sweep(116.5, 73, 1.8), 1.8)
    sub = sine(sweep(55, 35, 1.8), 1.8)
    return finish(envelope(mix((low, 0.5), (beat, 0.5), (sub, 0.7)), 0.15, 1.5), gain=0.9)


def victory() -> bytes:
    chords = [
        chord((261.6, 329.6, 392.0), 0.6, 0.05),
        chord((293.7, 370.0, 440.0), 0.6, 0.05),
        chord((329.6, 415.3, 493.9, 659.3), 1.2, 0.05),
    ]
    return finish(concat(*chords), gain=0.8)


def synthesize_all() -> dict[str, list[bytes]]:
    """Every sound effect of the game by event name (several variants where useful)."""
    return {
        "cast": [cast(v) for v in range(3)],
        "blast": [blast(big=False)],
        "blast_big": [blast(big=True)],
        "hurt": [hurt()],
        "kill": [kill()],
        "pickup": [pickup()],
        "pearl": [pearl()],
        "buy": [buy()],
        "perk": [perk()],
        "descend": [descend()],
        "death": [death()],
        "victory": [victory()],
    }


# ----------------------------------------------------------------- custom files

EXTENSIONS = (".wav", ".ogg")


def asset_dir() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / "assets" / "audio"


def custom_files(directory: Path, name: str) -> list[Path]:
    """Sound files in ``directory`` for event ``name`` (``name.ext`` or ``name_N.ext``)."""
    if not directory.is_dir():
        return []
    return sorted(
        path
        for path in directory.iterdir()
        if path.suffix.lower() in EXTENSIONS
        and (path.stem == name or path.stem.startswith(f"{name}_"))
    )
