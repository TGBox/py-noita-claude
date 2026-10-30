"""The stages of a run: deeper into the organism, harder, richer, with bosses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Depth:
    key: str
    name_de: str
    # material amounts relative to the base level layout
    bone_dust: float = 1.0
    blood: float = 1.0
    tallow: float = 1.0
    acid: float = 1.0
    growth: float = 1.0
    bridges: float = 1.0
    # population and loot
    walkers: int = 10
    flyers: int = 5
    spitters: int = 0
    bloats: int = 0
    wands: int = 3
    blocks: int = 8
    ambient: float = 0.3  # base brightness (0 = pitch black, 1 = fully lit)
    boss: str | None = None  # creature key of the boss guarding this depth
    final: bool = False  # killing the boss wins the run


DEPTHS: tuple[Depth, ...] = (
    Depth("schlund", "Der Schlund", acid=0.5, growth=0.5, walkers=9, flyers=4, ambient=0.3),
    Depth(
        "magen", "Der Magen", acid=2.6, tallow=1.4, growth=0.6,
        walkers=11, flyers=8, spitters=3, bloats=2, blocks=10, boss="magenwurm", ambient=0.25,
    ),
    Depth(
        "gedaerm", "Das Gedärm", blood=1.6, growth=3.0, bridges=1.5,
        walkers=13, flyers=8, spitters=5, bloats=7, blocks=10, boss="brutmutter", ambient=0.2,
    ),
    Depth(
        "herzkammer", "Die Herzkammer", blood=2.4, acid=1.0, growth=1.2,
        walkers=9, flyers=7, spitters=4, bloats=4, wands=2, blocks=8, boss="herz", final=True,
        ambient=0.16,
    ),
)  # fmt: skip
