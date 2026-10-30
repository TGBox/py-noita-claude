"""Plays sound effects; silently does nothing without an audio device.

Every event uses the synthesised sounds from ``src/sounds.py`` unless matching
files exist in ``assets/audio/``: ``<event>.wav`` / ``<event>.ogg`` or variants
like ``cast_1.wav``, ``cast_2.ogg`` (one is picked at random each time).
"""

from __future__ import annotations

import random
import time

import pygame

from src.sounds import SAMPLE_RATE, asset_dir, custom_files, synthesize_all

VOLUME = 0.6
QUIET = {"cast": 0.45, "pearl": 0.7}  # frequent sounds are played softer
MIN_INTERVAL = {"cast": 0.07, "pearl": 0.05, "hurt": 0.2}  # seconds between repeats


class Audio:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False
        self.sounds: dict[str, list[pygame.mixer.Sound]] = {}
        self._last_played: dict[str, float] = {}
        self._rng = random.Random()
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(16)
            directory = asset_dir()
            for name, variants in synthesize_all().items():
                files = custom_files(directory, name)
                if files:
                    sounds = [pygame.mixer.Sound(str(path)) for path in files]
                else:
                    sounds = [pygame.mixer.Sound(buffer=data) for data in variants]
                for sound in sounds:
                    sound.set_volume(VOLUME * QUIET.get(name, 1.0))
                self.sounds[name] = sounds
            self.enabled = True
        except (pygame.error, NotImplementedError, ValueError, OSError):
            self.enabled = False  # no audio device: play nothing

    def toggle_mute(self) -> None:
        self.muted = not self.muted

    def play(self, name: str) -> None:
        if not self.enabled or self.muted or name not in self.sounds:
            return
        now = time.monotonic()
        if now - self._last_played.get(name, -1.0) < MIN_INTERVAL.get(name, 0.0):
            return
        self._last_played[name] = now
        self._rng.choice(self.sounds[name]).play()
