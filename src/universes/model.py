"""Data model of a universe (bible chapter 03, "Felder eines Universums")."""

from __future__ import annotations

from dataclasses import dataclass, field

RANKS = 3
RANK_POWER = (1.0, 1.5, 2.2)  # enemy strength factor per rank
RANK_LOOT = ((1, 2), (3, 4), (5, 6))  # loot tiers per rank

# World shapes and their size in cells (bible chapter 02, "Weltgröße").
SHAPES: dict[str, tuple[int, int]] = {
    "breit": (3072, 1024),
    "hoch": (1280, 2560),
    "quadrat": (2048, 1536),
    "inseln": (2560, 1280),
}


@dataclass(frozen=True)
class Region:
    """A part of a universe with its own generator mix (parameters are free-form)."""

    key: str
    name_de: str
    params: tuple[tuple[str, float], ...] = ()

    def param(self, name: str, default: float = 0.0) -> float:
        return dict(self.params).get(name, default)


@dataclass(frozen=True)
class Universe:
    key: str
    name_de: str
    pitch_de: str
    rule: str  # key of the main rule (bible chapter 02, "Regelbibliothek")
    shape: str  # key of SHAPES
    ambient: float  # base brightness 0-1
    material_set: str  # key of src.materials.SETS
    regions: tuple[Region, ...] = ()
    natives: tuple[str, ...] = ()  # creature keys living here
    big: str | None = None  # big creature key, if any
    event: str = ""  # key of the recurring event
    samples: tuple[str, ...] = ()  # two sample item keys (workshop crafting)
    music_de: str = ""  # mood note for later music (no music in the MVP)
    arena_de: str = ""  # what a mid-boss arena looks like here
    klonita_de: tuple[str, ...] = ()  # Klonita lines only spoken here
    ready: bool = False  # generator, creatures and materials done (Phase C)
    size_override: tuple[int, int] | None = field(default=None)

    @property
    def size(self) -> tuple[int, int]:
        return self.size_override or SHAPES[self.shape]
