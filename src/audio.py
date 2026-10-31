"""Plays sound effects and ambient music; silently does nothing without an audio device.

Every event uses the synthesised sounds from ``src/sounds.py`` unless matching
files exist in ``assets/audio/``: ``<event>.wav`` / ``<event>.ogg`` or variants
like ``cast_1.wav``, ``cast_2.ogg`` (one is picked at random each time). Music
loops come from ``src/music.py``; they are generated in the background on first
use and cached as WAV files in the user data folder. ``assets/audio/musik_<mood>``
files replace them.
"""

from __future__ import annotations

import random
import threading
import time
import wave
from pathlib import Path

import pygame

from src.music import MOODS, ambient
from src.records import data_dir
from src.sounds import SAMPLE_RATE, asset_dir, custom_files, synthesize_all

VOLUME = 0.6
QUIET = {"cast": 0.45, "pearl": 0.7}  # frequent sounds are played softer
MIN_INTERVAL = {"cast": 0.07, "pearl": 0.05, "hurt": 0.2}  # seconds between repeats
MUSIC_VOLUME = 0.5
MUSIC_FADE_MS = 1500
CACHE_VERSION = 1


class Audio:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False
        self.effects_volume = 0.7  # 0..1, set from the options
        self.music_volume = 0.5
        self.sounds: dict[str, list[pygame.mixer.Sound]] = {}
        self._last_played: dict[str, float] = {}
        self._rng = random.Random()
        self._music: dict[str, pygame.mixer.Sound] = {}
        self._music_lock = threading.Lock()
        self._mood = ""
        self._music_channel = None
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)
            self._music_channel = pygame.mixer.Channel(0)
            directory = asset_dir()
            for name, variants in synthesize_all().items():
                files = custom_files(directory, name)
                if files:
                    sounds = [pygame.mixer.Sound(str(path)) for path in files]
                else:
                    sounds = [pygame.mixer.Sound(buffer=data) for data in variants]
                self.sounds[name] = sounds
            self.enabled = True
        except (pygame.error, NotImplementedError, ValueError, OSError):
            self.enabled = False  # no audio device: play nothing
            return
        threading.Thread(target=self._prepare_music, daemon=True).start()

    # ---------------------------------------------------------------- effects

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        self._apply_music_volume()

    def set_volumes(self, effects: float, music: float) -> None:
        self.effects_volume, self.music_volume = effects, music
        self._apply_music_volume()

    def play(self, name: str) -> None:
        if not self.enabled or self.muted or name not in self.sounds:
            return
        now = time.monotonic()
        if now - self._last_played.get(name, -1.0) < MIN_INTERVAL.get(name, 0.0):
            return
        self._last_played[name] = now
        sound = self._rng.choice(self.sounds[name])
        channel = sound.play()
        if channel is not None:
            channel.set_volume(VOLUME * self.effects_volume * QUIET.get(name, 1.0))

    # ------------------------------------------------------------------ music

    def play_music(self, mood: str) -> None:
        """Cross-fade to the loop of ``mood`` (if it is ready yet)."""
        if not self.enabled or self._music_channel is None or mood == self._mood:
            return
        with self._music_lock:
            sound = self._music.get(mood)
        if sound is None:
            return  # still being generated: the next call tries again
        self._mood = mood
        self._music_channel.fadeout(MUSIC_FADE_MS // 2)
        self._music_channel.play(sound, loops=-1, fade_ms=MUSIC_FADE_MS)
        self._apply_music_volume()

    def _apply_music_volume(self) -> None:
        if self._music_channel is not None:
            level = 0.0 if self.muted else MUSIC_VOLUME * self.music_volume
            self._music_channel.set_volume(level)

    def _prepare_music(self) -> None:
        """Load (or generate and cache) every music loop; runs in a background thread."""
        custom = asset_dir()
        cache = data_dir() / "musik"
        for mood in MOODS:
            try:
                files = custom_files(custom, f"musik_{mood}")
                if files:
                    sound = pygame.mixer.Sound(str(files[0]))
                else:
                    sound = pygame.mixer.Sound(buffer=cached_loop(cache, mood))
            except (pygame.error, OSError, ValueError):
                continue
            with self._music_lock:
                self._music[mood] = sound


def cached_loop(cache: Path, mood: str) -> bytes:
    """The loop of ``mood`` from the WAV cache, generated and stored if missing."""
    path = cache / f"{mood}_v{CACHE_VERSION}.wav"
    try:
        with wave.open(str(path), "rb") as file:
            if file.getframerate() == SAMPLE_RATE and file.getsampwidth() == 2 and file.getnframes():
                return file.readframes(file.getnframes())
    except (OSError, EOFError, wave.Error):
        pass
    data = ambient(mood)
    try:
        cache.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        with wave.open(str(temporary), "wb") as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(SAMPLE_RATE)
            file.writeframes(data)
        temporary.replace(path)  # never leave a half-written loop behind
    except OSError:
        pass  # no cache: generate again next time
    return data
