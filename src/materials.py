"""Material definitions for Cloita's cell simulation.

Every cell of the world stores one material id (one byte). All per-material
properties live in parallel lists indexed by that id. The Rust core receives the
same data once at start-up (see ``src/native.py``), so this module is the single
source of truth for how materials behave.
"""

from __future__ import annotations

from dataclasses import dataclass

# Material ids
AIR = 0
BEDROCK = 1
BONE = 2
BONE_DUST = 3
FLESH = 4
SINEW = 5
BLOOD = 6
CRUST = 7
TALLOW = 8
ACID = 9
FIRE = 10
SMOKE = 11
FUME = 12
GROWTH = 13
SPORES = 14
MUCUS = 15
MAGMA = 16
PUS = 17
SPARK = 18  # nerve current travelling through sinew
SPENT = 19  # sinew right after a current passed (heals back into sinew)
ENAMEL = 20  # tooth enamel: very hard, only strong explosions break it
MATERIAL_COUNT = 21

# Kinds (behaviour classes), must match native/src/lib.rs.
EMPTY = 0
SOLID = 1
POWDER = 2
LIQUID = 3
GAS = 4
FLAME = 5

# Number of colour variants per material (grainy look without textures). Three variants
# leave room in the 8-bit palette for up to 21 materials.
VARIANTS = 3
# Brightness steps for lighting; palette index = (material * VARIANTS + variant) * levels + level.
LIGHT_LEVELS = 4
LIGHT_BRIGHTNESS = (0.16, 0.4, 0.7, 1.0)


@dataclass(frozen=True)
class Material:
    """Static description of one material."""

    name_de: str
    kind: int
    density: int
    color: tuple[int, int, int]
    flammability: float = 0.0  # chance per tick that an adjacent fire ignites it
    burn_life: tuple[int, int] = (0, 0)  # fire lifetime (ticks) once ignited
    life: tuple[int, int] = (0, 0)  # lifetime (ticks) of freshly created cells, 0 = forever
    decay_into: int = AIR  # what a cell becomes when its lifetime ends ...
    decay_chance: float = 0.0  # ... with this chance (otherwise air)
    fluidity: int = 0  # how far a liquid spreads sideways per tick
    mobility: float = 1.0  # chance per tick that a liquid tries to move (viscosity)
    hazard_dps: float = 0.0  # damage per second to a body touching it
    debris: int = AIR  # what an explosion leaves behind ...
    debris_chance: float = 0.0  # ... with this chance (otherwise air)
    grain: int = 8  # brightness spread between the colour variants
    glow: int = 0  # 0-255, how strongly the material lights its surroundings
    hardness: int = 0  # solids/powders: 1 soft, 2 firm, 3 hard, 4 indestructible
    description_de: str = ""  # shown when the cursor rests on it


MATERIALS: tuple[Material, ...] = (
    Material("Leere", EMPTY, 0, (30, 14, 18), grain=4),
    Material(
        "Panzerknochen", SOLID, 255, (40, 32, 34), grain=4, hardness=4,
        description_de="Uralter Panzer. Nichts kann ihn zerstören.",
    ),
    Material(
        "Knochen", SOLID, 255, (150, 138, 112), debris=BONE_DUST, debris_chance=0.35, grain=10,
        hardness=2, description_de="Fest. Kleine Zauber prallen ab, Explosionen sprengen ihn.",
    ),
    Material(
        "Knochenstaub", POWDER, 60, (172, 158, 128), grain=10, hardness=1,
        description_de="Rieselt. Lässt sich leicht wegsprengen.",
    ),
    Material(
        "Fleisch", SOLID, 255, (86, 30, 38), debris=BLOOD, debris_chance=0.25, grain=16,
        hardness=1, description_de="Weiches Gewebe. Blutet, wenn man es zerstört.",
    ),
    Material(
        "Sehnen", SOLID, 255, (158, 104, 88), flammability=0.03, burn_life=(90, 160), grain=12,
        hardness=2, description_de="Zäh und brennbar. Leitet Nervenstrom.",
    ),
    Material(
        "Blut", LIQUID, 30, (150, 12, 24), fluidity=5,
        description_de="Löscht Feuer. Ein Schluck heilt ein wenig.",
    ),
    Material(
        "Schorf", SOLID, 255, (70, 26, 22), hardness=1,
        description_de="Verkrustetes Blut. Bröckelt leicht.",
    ),
    Material(
        "Talg", LIQUID, 20, (196, 174, 118),
        flammability=0.5, burn_life=(10, 25), fluidity=3, mobility=0.7,
        description_de="Fett. Sehr brennbar, macht dich ölig.",
    ),
    Material(
        "Magensäure", LIQUID, 40, (140, 196, 40), fluidity=5, hazard_dps=60.0, glow=110,
        description_de="Ätzt Fleisch und dich. Meiden!",
    ),
    Material(
        "Feuer", FLAME, -1, (255, 160, 40),
        life=(30, 60), decay_into=SMOKE, decay_chance=0.25, hazard_dps=15.0, glow=255,
        description_de="Verbrennt dich und alles Brennbare.",
    ),
    Material(
        "Rauch", GAS, -2, (54, 44, 46), life=(50, 140),
        description_de="Harmlos, verzieht sich.",
    ),
    Material(
        "Ätzdampf", GAS, -3, (98, 132, 52), life=(60, 160), hazard_dps=8.0, glow=40,
        description_de="Giftiger Dampf. Schadet beim Einatmen.",
    ),
    Material(
        "Wucherung", SOLID, 255, (124, 72, 116),
        flammability=0.08, burn_life=(40, 90), debris=SPORES, debris_chance=0.3, grain=14,
        hardness=1, description_de="Wächst und frisst Fleisch. Brennt, gibt Sporen ab.",
    ),
    Material(
        "Sporen", GAS, -4, (164, 128, 160),
        flammability=0.6, burn_life=(3, 8), life=(120, 240), hazard_dps=3.0, glow=60,
        description_de="Leicht giftig und hochentzündlich.",
    ),
    Material(
        "Schleim", LIQUID, 35, (176, 172, 120), fluidity=1, mobility=0.18, grain=12,
        description_de="Zäh. Bremst jede Bewegung.",
    ),
    Material(
        "Glutblut", LIQUID, 45, (236, 96, 30), fluidity=2, mobility=0.35, hazard_dps=40.0,
        glow=230, grain=20, description_de="Glühend heiß. Setzt alles in Brand. Meiden!",
    ),
    Material(
        "Eiter", LIQUID, 32, (186, 190, 84), fluidity=3, mobility=0.6, grain=10,
        description_de="Vergiftet dich bei Berührung.",
    ),
    Material(
        "Nervenstrom", FLAME, 255, (190, 220, 255),
        life=(2, 4), decay_into=SPENT, decay_chance=1.0, hazard_dps=45.0, glow=255, grain=24,
        description_de="Elektrischer Schlag durch die Sehnen. Schmerzhaft.",
    ),
    Material(
        "Erschöpfte Sehne", SOLID, 255, (110, 72, 64),
        flammability=0.001, burn_life=(60, 120), grain=10, hardness=1,
        description_de="Ausgebrannte Sehne. Erholt sich langsam.",
    ),
    Material(
        "Zahnschmelz", SOLID, 255, (206, 214, 222), debris=BONE_DUST, debris_chance=0.5, grain=10,
        hardness=3, glow=5,
        description_de="Sehr hart. Nur starke Explosionen brechen ihn.",
    ),
)

assert len(MATERIALS) == MATERIAL_COUNT
assert MATERIAL_COUNT * VARIANTS * LIGHT_LEVELS <= 256, "palette index must fit a byte"

KIND: list[int] = [m.kind for m in MATERIALS]
FLAMMABILITY: list[float] = [m.flammability for m in MATERIALS]
BURN_RANGE: list[tuple[int, int]] = [m.burn_life for m in MATERIALS]
LIFE_RANGE: list[tuple[int, int]] = [m.life for m in MATERIALS]
HAZARD_DPS: list[float] = [m.hazard_dps for m in MATERIALS]
NAME_DE: list[str] = [m.name_de for m in MATERIALS]
DEBRIS: list[tuple[int, float]] = [(m.debris, m.debris_chance) for m in MATERIALS]
GLOW: list[int] = [m.glow for m in MATERIALS]
HARDNESS: list[int] = [m.hardness for m in MATERIALS]
# How much smaller a blast or bore gets against each hardness (cells): firm tissue
# shrugs off tiny sparks, enamel only breaks near the centre of a big explosion.
HARDNESS_SHRINK = (0, 0, 2, 9, 10_000)
HARDNESS_DE = ("", "weich", "hart", "sehr hart", "unzerstörbar")
OPAQUE: list[int] = [int(k in (SOLID, POWDER)) for k in KIND]  # currents shine through

# The player walks on solids and powders but wades through liquids. A nerve current is
# a flame-like cell inside sinew; the sinew it runs through stays solid.
BLOCKS_BODY: list[bool] = [k in (SOLID, POWDER) or i == SPARK for i, k in enumerate(KIND)]
# Projectiles stop at everything that is not empty, gas or flame.
STOPS_PROJECTILE: list[bool] = [k in (SOLID, POWDER, LIQUID) or i == SPARK for i, k in enumerate(KIND)]


def variant_color(material: Material, variant: int) -> tuple[int, int, int]:
    r, g, b = material.color
    shift = round((variant - (VARIANTS - 1) / 2) * material.grain)
    return (
        max(0, min(255, r + shift)),
        max(0, min(255, g + shift)),
        max(0, min(255, b + shift)),
    )


def shade(color: tuple[int, int, int], level: int) -> tuple[int, int, int]:
    factor = LIGHT_BRIGHTNESS[level]
    return (round(color[0] * factor), round(color[1] * factor), round(color[2] * factor))


def build_palette(lit: bool = True) -> list[tuple[int, int, int]]:
    """Palette indexed by ``(material * VARIANTS + variant) * LIGHT_LEVELS + level``.

    With ``lit=False`` the light level is left out (index ``material * VARIANTS + variant``).
    """
    palette: list[tuple[int, int, int]] = []
    for material in MATERIALS:
        for variant in range(VARIANTS):
            color = variant_color(material, variant)
            if not lit:
                palette.append(color)
                continue
            palette.extend(shade(color, level) for level in range(LIGHT_LEVELS))
    return palette
