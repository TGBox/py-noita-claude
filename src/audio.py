"""Plays the synthesised sound effects; silently does nothing without an audio device."""

from __future__ import annotations

import pygame

from src.sounds import SAMPLE_RATE, synthesize_all

VOLUME = 0.6
QUIET = {"cast": 0.35, "pearl": 0.6}  # frequent sounds are played softer


class Audio:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(16)
            for name, data in synthesize_all().items():
                sound = pygame.mixer.Sound(buffer=data)
                sound.set_volume(VOLUME * QUIET.get(name, 1.0))
                self.sounds[name] = sound
            self.enabled = True
        except (pygame.error, NotImplementedError, ValueError):
            self.enabled = False  # no audio device: play nothing

    def toggle_mute(self) -> None:
        self.muted = not self.muted

    def play(self, name: str) -> None:
        if self.enabled and not self.muted and name in self.sounds:
            self.sounds[name].play()
