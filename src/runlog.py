"""Detailed run log for playtests: one JSON-Lines file per run in the data folder.

Every line is a JSON object with ``t`` (seconds since the run started), ``ereignis``
(event name) and event data: depths entered, items picked up and bought, perks,
damage taken by cause, kills, deaths, frame times per depth, errors with their
traceback. After a playtest the file shows exactly what happened and when.
"""

from __future__ import annotations

import json
import platform
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from src.records import data_dir

LOG_DIR = "protokolle"
KEEP_FILES = 30  # older logs are deleted
DAMAGE_FLUSH = 5.0  # seconds between damage summaries


class RunLog:
    """Writes events of the current run to ``<data>/protokolle/lauf-<time>.jsonl``."""

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or data_dir() / LOG_DIR
        self.path: Path | None = None
        self._file = None
        self._start = time.monotonic()
        self.frames: list[float] = []  # frame times (s) since the last flush
        self.disabled = False

    # ---------------------------------------------------------------- files

    def start(self, **info: Any) -> None:
        """Begin a new log file (closes the previous one)."""
        self.close()
        if self.disabled:
            return
        stamp = time.strftime("%Y%m%d-%H%M%S")
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            self.path = self.directory / f"lauf-{stamp}.jsonl"
            suffix = 1
            while self.path.exists():
                suffix += 1
                self.path = self.directory / f"lauf-{stamp}-{suffix}.jsonl"
            self._file = self.path.open("w", encoding="utf-8")
        except OSError:
            self.path, self._file = None, None
            return
        self._start = time.monotonic()
        self.frames = []
        self._prune()
        self.write(
            "start",
            python=sys.version.split()[0],
            system=platform.platform(),
            uhrzeit=time.strftime("%Y-%m-%d %H:%M:%S"),
            **info,
        )

    def _prune(self) -> None:
        try:
            logs = sorted(self.directory.glob("lauf-*.jsonl"))
        except OSError:
            return
        for old in logs[:-KEEP_FILES]:
            try:
                old.unlink()
            except OSError:
                continue

    def close(self) -> None:
        if self._file is not None:
            try:
                self._file.close()
            except OSError:
                pass
        self._file = None

    # --------------------------------------------------------------- events

    def write(self, event: str, **data: Any) -> None:
        if self._file is None:
            return
        entry = {"t": round(time.monotonic() - self._start, 2), "ereignis": event, **data}
        try:
            self._file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
            self._file.flush()
        except (OSError, ValueError):
            self.close()

    def frame(self, dt: float) -> None:
        self.frames.append(dt)

    def flush_frames(self, where: str) -> None:
        """Summarise the frame times collected since the last flush."""
        frames, self.frames = self.frames, []
        if len(frames) < 10:
            return
        ordered = sorted(frames)
        mean = sum(frames) / len(frames)
        self.write(
            "bildrate",
            ort=where,
            bilder=len(frames),
            mittel_ms=round(mean * 1000, 2),
            p99_ms=round(ordered[int(len(ordered) * 0.99) - 1] * 1000, 2),
            max_ms=round(ordered[-1] * 1000, 2),
            fps=round(1 / mean, 1) if mean else 0,
        )

    def error(self, exc: BaseException) -> None:
        text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        self.write("fehler", art=type(exc).__name__, meldung=str(exc), traceback=text)
