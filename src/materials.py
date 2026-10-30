"""Material definitions and lookup tables for the falling-sand simulation.

Every cell of the world stores one material id (one byte). All per-material
properties live in parallel lists indexed by that id, which keeps the hot
simulation loop free of attribute lookups.
"""

from __future__ import annotations

from dataclasses import dataclass

# Material ids
AIR = 0
BEDROCK = 1
STONE = 2
SAND = 3
WOOD = 4
WATER = 5
OIL = 6
LAVA = 7
FIRE = 8
SMOKE = 9
STEAM = 10
MATERIAL_COUNT = 11

# Kinds (behaviour classes). Everything below POWDER is static.
EMPTY = 0
SOLID = 1
POWDER = 2
LIQUID = 3
GAS = 4
FLAME = 5

# Number of colour variants per material (used for a grainy look).
VARIANTS = 4


@dataclass(frozen=True)
class Material:
    """Static description of one material."""

    name_de: str
    kind: int
    density: int
    color: tuple[int, int, int]
    flammability: float = 0.0  # chance per frame that a neighbouring fire ignites it
    burn_life: tuple[int, int] = (0, 0)  # fire lifetime (frames) once ignited
    life: tuple[int, int] = (0, 0)  # lifetime (frames) of freshly created cells
    fluidity: int = 0  # how far a liquid may spread sideways per frame
    hazard_dps: float = 0.0  # damage per second to the player


MATERIALS: tuple[Material, ...] = (
    Material("Luft", EMPTY, 0, (12, 14, 22)),
    Material("Grundgestein", SOLID, 255, (28, 28, 38)),
    Material("Stein", SOLID, 255, (98, 98, 110)),
    Material("Sand", POWDER, 60, (222, 196, 120)),
    Material("Holz", SOLID, 255, (122, 80, 42), flammability=0.03, burn_life=(90, 160)),
    Material("Wasser", LIQUID, 30, (50, 110, 220), fluidity=5),
    Material("Öl", LIQUID, 20, (62, 46, 34), flammability=0.5, burn_life=(10, 25), fluidity=4),
    Material("Lava", LIQUID, 50, (255, 100, 20), fluidity=1, hazard_dps=90.0),
    Material("Feuer", FLAME, -1, (255, 160, 40), life=(30, 60), hazard_dps=30.0),
    Material("Rauch", GAS, -2, (72, 72, 78), life=(50, 140)),
    Material("Dampf", GAS, -3, (190, 200, 215), life=(60, 160)),
)

KIND: list[int] = [m.kind for m in MATERIALS]
DENSITY: list[int] = [m.density for m in MATERIALS]
FLAMMABILITY: list[float] = [m.flammability for m in MATERIALS]
BURN_RANGE: list[tuple[int, int]] = [m.burn_life for m in MATERIALS]
LIFE_RANGE: list[tuple[int, int]] = [m.life for m in MATERIALS]
FLUIDITY: list[int] = [m.fluidity for m in MATERIALS]
HAZARD_DPS: list[float] = [m.hazard_dps for m in MATERIALS]
NAME_DE: list[str] = [m.name_de for m in MATERIALS]

# The player walks on solids and powders but wades through liquids.
BLOCKS_BODY: list[bool] = [k in (SOLID, POWDER) for k in KIND]
# Projectiles stop at everything that is not empty, gas or flame.
STOPS_PROJECTILE: list[bool] = [k in (SOLID, POWDER, LIQUID) for k in KIND]


def _build_fall_table() -> list[list[bool]]:
    """FALL[m][t]: may a falling cell of material m swap into target t?"""
    table = [[False] * MATERIAL_COUNT for _ in range(MATERIAL_COUNT)]
    for m in range(MATERIAL_COUNT):
        if KIND[m] not in (POWDER, LIQUID):
            continue
        for t in range(MATERIAL_COUNT):
            if KIND[t] in (EMPTY, LIQUID, GAS) and DENSITY[t] < DENSITY[m]:
                table[m][t] = True
    return table


def _build_rise_table() -> list[list[bool]]:
    """RISE[m][t]: may a gas cell of material m swap into target t?"""
    table = [[False] * MATERIAL_COUNT for _ in range(MATERIAL_COUNT)]
    for m in range(MATERIAL_COUNT):
        if KIND[m] != GAS:
            continue
        for t in range(MATERIAL_COUNT):
            if KIND[t] in (EMPTY, LIQUID, GAS) and DENSITY[t] > DENSITY[m]:
                table[m][t] = True
    return table


FALL_ALLOWED: list[list[bool]] = _build_fall_table()
RISE_ALLOWED: list[list[bool]] = _build_rise_table()


def build_palette() -> list[tuple[int, int, int]]:
    """Return a palette indexed by ``material_id * VARIANTS + variant``."""
    shifts = (-10, -3, 3, 10)
    palette: list[tuple[int, int, int]] = []
    for material in MATERIALS:
        for shift in shifts:
            r, g, b = material.color
            if material.kind == EMPTY:
                palette.append((r, g, b))
            else:
                palette.append(
                    (
                        max(0, min(255, r + shift)),
                        max(0, min(255, g + shift)),
                        max(0, min(255, b + shift)),
                    )
                )
    return palette
