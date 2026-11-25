"""Procedural chamber generator for Patentamt bureaucratic layouts."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class PatentamtRoom:
    """Procedural grid layout for a Patentamt district wing."""

    district: str
    width: int
    height: int
    cells: list[list[str]] = field(default_factory=list)
    desks: list[tuple[int, int]] = field(default_factory=list)
    cabinets: list[tuple[int, int]] = field(default_factory=list)
    incubators: list[tuple[int, int]] = field(default_factory=list)
    spawn: tuple[int, int] = (4, 4)


def generate_patentamt_layout(
    seed: int,
    district: str = "wartezimmer",
    width: int = 64,
    height: int = 40,
) -> PatentamtRoom:
    """Generate an office/bureaucracy grid layout with desks, cabinets, and corridors."""
    rng = random.Random(seed)
    cells = [["air" for _ in range(width)] for _ in range(height)]

    # Outer steel-bureaucracy frame & floor.
    for x in range(width):
        cells[0][x] = "stahlwall"
        cells[height - 1][x] = "stahlboden"
    for y in range(height):
        cells[y][0] = "stahlwall"
        cells[y][width - 1] = "stahlwall"

    desks: list[tuple[int, int]] = []
    cabinets: list[tuple[int, int]] = []
    incubators: list[tuple[int, int]] = []

    # Mid-level catwalk floor with passage gap.
    mid_y = height // 2
    gap_start = rng.randint(width // 4, (width * 2) // 3)
    for x in range(2, width - 2):
        if gap_start <= x < gap_start + 6:
            continue
        cells[mid_y][x] = "betonboden"

    # Place filing cabinets, desks, or clone incubators based on district flavor.
    for x in range(6, width - 6, 8):
        y_ground = height - 2
        if district == "klon_legebatterie":
            cells[y_ground][x] = "klon_kapsel"
            incubators.append((x, y_ground))
        elif district == "aktenschrank_schlucht":
            for dy in range(4):
                cells[y_ground - dy][x] = "aktenschrank"
            cabinets.append((x, y_ground))
        else:
            cells[y_ground][x] = "schreibtisch"
            desks.append((x, y_ground))
        if mid_y - 2 > 2 and rng.random() < 0.65:
            cells[mid_y - 1][x] = "aktenstapel"
            cabinets.append((x, mid_y - 1))

    return PatentamtRoom(
        district=district,
        width=width,
        height=height,
        cells=cells,
        desks=desks,
        cabinets=cabinets,
        incubators=incubators,
        spawn=(4, height - 3),
    )
