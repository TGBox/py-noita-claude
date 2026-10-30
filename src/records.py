"""Persistent statistics across runs, stored as JSON in the user's data folder."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

FILE_NAME = "records.json"


def data_dir() -> Path:
    """Per-user folder for Cloita's data (created on save)."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        return base / "Cloita"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Cloita"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "cloita"


@dataclass
class Records:
    runs: int = 0
    wins: int = 0
    kills: int = 0
    pearls: int = 0
    best_depth: int = 0  # deepest depth reached (1 = Schlund)
    best_time: float = 0.0  # fastest win in seconds, 0 = none yet
    blocks: list[str] = field(default_factory=list)  # Kodex: blocks ever found
    creatures: dict[str, int] = field(default_factory=dict)  # Kodex: kills per species

    def discover(self, kind: str, key: str) -> bool:
        """Note a find for the Kodex. Returns True the first time."""
        if kind == "block":
            if key in self.blocks:
                return False
            self.blocks.append(key)
            return True
        first = key not in self.creatures
        self.creatures[key] = self.creatures.get(key, 0) + 1
        return first

    def add_run(self, *, won: bool, depth: int, kills: int, pearls: int, time: float) -> bool:
        """Count a finished run. Returns True if it set a new record."""
        record = depth > self.best_depth or (won and (not self.best_time or time < self.best_time))
        self.runs += 1
        self.kills += kills
        self.pearls += pearls
        self.best_depth = max(self.best_depth, depth)
        if won:
            self.wins += 1
            self.best_time = time if not self.best_time else min(self.best_time, time)
        return record

    def lines_de(self) -> list[str]:
        """Short German summary for the title screen (empty before the first run)."""
        if not self.runs:
            return []
        lines = [
            f"Läufe: {self.runs}   Siege: {self.wins}   Tiefste Tiefe: {self.best_depth}",
            f"Getötet: {self.kills}   Blutperlen: {self.pearls}",
        ]
        if self.best_time:
            lines.append(f"Schnellster Sieg: {format_time(self.best_time)}")
        return lines


def format_time(seconds: float) -> str:
    minutes, rest = divmod(int(seconds), 60)
    return f"{minutes}:{rest:02d}"


def load(path: Path | None = None) -> Records:
    """Read the records; a missing or broken file gives fresh records."""
    path = path or data_dir() / FILE_NAME
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Records()
    if not isinstance(raw, dict):
        return Records()
    numbers = {f.name for f in fields(Records)} - {"blocks", "creatures"}
    values: dict[str, Any] = {}
    for name, value in raw.items():
        if name in numbers and _is_number(value):
            values[name] = float(value) if name == "best_time" else int(value)
    blocks = raw.get("blocks")
    if isinstance(blocks, list):
        values["blocks"] = [key for key in blocks if isinstance(key, str)]
    creatures = raw.get("creatures")
    if isinstance(creatures, dict):
        values["creatures"] = {
            key: int(count) for key, count in creatures.items() if isinstance(key, str) and _is_number(count)
        }
    return Records(**values)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def save(records: Records, path: Path | None = None) -> bool:
    """Write the records; returns False if the folder is not writable."""
    return write_json(asdict(records), path or data_dir() / FILE_NAME)


def write_json(data: object, path: Path) -> bool:
    """Write atomically (temporary file, then rename). False if that fails."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(path)
    except OSError:
        return False
    return True


# ------------------------------------------------------------------- saved run

SAVE_NAME = "lauf.json"


def load_run(path: Path | None = None) -> dict[str, Any] | None:
    """The saved run, or None if there is none (or it cannot be read)."""
    path = path or data_dir() / SAVE_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def save_run(data: dict[str, Any], path: Path | None = None) -> bool:
    return write_json(data, path or data_dir() / SAVE_NAME)


def delete_run(path: Path | None = None) -> None:
    try:
        (path or data_dir() / SAVE_NAME).unlink()
    except OSError:
        pass
