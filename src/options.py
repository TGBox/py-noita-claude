"""Player settings (volume, display), stored as JSON next to the records."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from src.keybinds import Bindings
from src.records import data_dir, write_json

FILE_NAME = "optionen.json"
STEPS = 10  # volume steps


@dataclass
class Options:
    effects: int = 7  # 0..STEPS
    music: int = 5  # 0..STEPS
    fullscreen: bool = False
    lighting: bool = True
    shake: bool = True  # screen shake on explosions
    damage_numbers: bool = True

    # (attribute, German label) in menu order
    ENTRIES = (
        ("effects", "Effekte"),
        ("music", "Musik"),
        ("fullscreen", "Vollbild"),
        ("lighting", "Beleuchtung"),
        ("shake", "Bildschirmwackeln"),
        ("damage_numbers", "Schadenszahlen"),
    )

    def change(self, name: str, step: int) -> None:
        """Left/right on an entry: volumes move by ``step``, switches toggle."""
        value = getattr(self, name)
        if isinstance(value, bool):
            setattr(self, name, not value)
        else:
            setattr(self, name, max(0, min(STEPS, value + step)))

    def label(self, name: str, title: str) -> str:
        value = getattr(self, name)
        if isinstance(value, bool):
            return f"{title}: {'an' if value else 'aus'}"
        return f"{title}: {'|' * value}{'.' * (STEPS - value)}"


def load(path: Path | None = None) -> Options:
    path = path or data_dir() / FILE_NAME
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Options()
    if not isinstance(raw, dict):
        return Options()
    options = Options()
    for field in fields(Options):
        value = raw.get(field.name)
        default = getattr(options, field.name)
        if isinstance(default, bool) and isinstance(value, bool):
            setattr(options, field.name, value)
        elif isinstance(default, int) and isinstance(value, int) and not isinstance(value, bool):
            setattr(options, field.name, max(0, min(STEPS, value)))
    return options


def save(options: Options, path: Path | None = None) -> bool:
    return write_json(asdict(options), path or data_dir() / FILE_NAME)


# --------------------------------------------------------------- key bindings

BINDINGS_NAME = "steuerung.json"


def load_bindings(path: Path | None = None) -> Bindings:
    """The player's key bindings (defaults if none were saved or the file is broken)."""
    path = path or data_dir() / BINDINGS_NAME
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Bindings()
    return Bindings.from_json(raw)


def save_bindings(bindings: Bindings, path: Path | None = None) -> bool:
    return write_json(bindings.to_json(), path or data_dir() / BINDINGS_NAME)
