"""Universum matroschka_simulation: Matroschka-Simulation (Ebene 4) (Phase S02)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "matroschka_simulation",
    "Matroschka-Simulation (Ebene 4)",
    "Eine Simulation in einer Simulation, in der besiegte Gegner kleinere Kopien ihrer selbst fallen lassen.",
    rule="rule_rekursion",
    shape="raster",
    ambient=0.56,
    material_set="matroschka_simulation",
    regions=(
        Region("ebene_4a", "Cache-Korridor"),
        Region("ebene_4b", "Shader-Brüche"),
        Region("kernel_kern", "Kernel-Kern"),
    ),
    natives=("holzpuppen_krieger", "debug_kaefer", "shader_spuk", "polygon_ratte"),
    event="speicherleck",
    samples=("probe_voxel", "probe_pixel"),
    sample_key="probe_voxel",
    mid_boss="kompilier_daemon",
    boss="kernel_architekt",
    arena_de="Verschachtelte Voxel-Kammer mit blinkenden Speicheradressen",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"nest_depth": 1, "split_count": 2},
    2: {"nest_depth": 2, "split_count": 2},
    3: {"nest_depth": 3, "split_count": 3},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="voxel_wand",
        trim_key="pixel_sand",
        liquid_key="cache_fluessigkeit",
        powder_key="pixel_sand",
        props=("matroschka_saeule", "debug_konsole"),
    )
