"""Material definitions and per-universe material sets.

Every cell of the world stores one material id (one byte). The 8-bit palette holds at
most 21 materials, so every universe loads its own **material set**: an ordered list of
material keys (``air`` and ``bedrock`` always first). Ids therefore only mean something
relative to the active set; anything that outlives a world (flasks, saves, blocks)
refers to materials by key.

All per-material properties live in parallel module-level lists indexed by id. They are
rewritten in place by :func:`activate`, so ``from src.materials import KIND`` keeps
working. The named ids (``mat.BLOOD``, ``mat.ROCK`` ...) are module attributes that also
change on activation, so code must read them as ``mat.NAME`` at use time. A name the set
does not contain resolves through aliases to a stand-in (blood becomes ink in the file
universe), which lets older generators and spells run in every universe.

The Rust core receives the active set's data when a world is created (``src/native.py``).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

AIR = 0
BEDROCK = 1

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
MAX_MATERIALS = 256 // (VARIANTS * LIGHT_LEVELS)  # 21


@dataclass(frozen=True)
class Material:
    """Static description of one material."""

    key: str
    name_de: str
    kind: int
    density: int
    color: tuple[int, int, int]
    flammability: float = 0.0  # chance per tick that an adjacent fire ignites it
    burn_life: tuple[int, int] = (0, 0)  # fire lifetime (ticks) once ignited
    life: tuple[int, int] = (0, 0)  # lifetime (ticks) of freshly created cells, 0 = forever
    decay_into: str = "air"  # what a cell becomes when its lifetime ends ...
    decay_chance: float = 0.0  # ... with this chance (otherwise air)
    fluidity: int = 0  # how far a liquid spreads sideways per tick
    mobility: float = 1.0  # chance per tick that a liquid tries to move (viscosity)
    hazard_dps: float = 0.0  # damage per second to a body touching it
    debris: str = "air"  # what an explosion leaves behind ...
    debris_chance: float = 0.0  # ... with this chance (otherwise air)
    grain: int = 8  # brightness spread between the colour variants
    glow: int = 0  # 0-255, how strongly the material lights its surroundings
    hardness: int = 0  # solids/powders: 1 soft, 2 firm, 3 hard, 4 indestructible
    description_de: str = ""  # shown when the cursor rests on it


def _m(key: str, name_de: str, kind: int, density: int, color: tuple[int, int, int], **kw) -> Material:
    return Material(key, name_de, kind, density, color, **kw)


# ---------------------------------------------------------------------------------------
# Library: every material of every universe, by key.
# ---------------------------------------------------------------------------------------

_BASE = (
    _m("air", "Leere", EMPTY, 0, (30, 14, 18), grain=4),
    _m(
        "bedrock", "Weltrand", SOLID, 255, (40, 32, 34), grain=4, hardness=4,
        description_de="Der Rand der Welt. Nichts kann ihn zerstören.",
    ),
    _m(
        "rock", "Fels", SOLID, 255, (104, 98, 92), debris="sand", debris_chance=0.35, grain=10,
        hardness=2, description_de="Gewöhnlicher Stein. Explosionen sprengen ihn.",
    ),
    _m(
        "dirt", "Erde", SOLID, 255, (96, 70, 48), debris="sand", debris_chance=0.2, grain=14,
        hardness=1, description_de="Weich. Lässt sich leicht wegsprengen.",
    ),
    _m(
        "sand", "Sand", POWDER, 60, (190, 168, 116), grain=12, hardness=1,
        description_de="Rieselt.",
    ),
    _m(
        "water", "Wasser", LIQUID, 30, (52, 96, 170), fluidity=5,
        description_de="Löscht Feuer und macht nass.",
    ),
    _m(
        "oil", "Öl", LIQUID, 20, (60, 50, 34), flammability=0.5, burn_life=(10, 25), fluidity=3,
        mobility=0.7, description_de="Schwimmt oben. Sehr brennbar, macht dich ölig.",
    ),
    _m(
        "fire", "Feuer", FLAME, -1, (255, 160, 40),
        life=(30, 60), decay_into="smoke", decay_chance=0.25, hazard_dps=15.0, glow=255,
        description_de="Verbrennt dich und alles Brennbare.",
    ),
    _m("smoke", "Rauch", GAS, -2, (54, 44, 46), life=(50, 140), description_de="Harmlos, verzieht sich."),
    _m(
        "steam", "Dampf", GAS, -3, (176, 184, 196), life=(60, 160), decay_into="water",
        decay_chance=0.08, hazard_dps=3.0, description_de="Heißer Dampf. Verbrüht ein wenig.",
    ),
    _m(
        "fluxschnaps", "Flux-Schnaps", LIQUID, 28, (40, 210, 190), flammability=0.3,
        burn_life=(6, 14), fluidity=4, glow=90,
        description_de="Leuchtet türkis. Ein Schluck macht beschwipst.",
    ),
)

_BODY = (  # the organism of the current game (transitional Fleischwelt set)
    _m(
        "bone", "Knochen", SOLID, 255, (150, 138, 112), debris="bone_dust", debris_chance=0.35,
        grain=10, hardness=2,
        description_de="Fest. Kleine Zauber prallen ab, Explosionen sprengen ihn.",
    ),
    _m(
        "bone_dust", "Knochenstaub", POWDER, 60, (172, 158, 128), grain=10, hardness=1,
        description_de="Rieselt. Lässt sich leicht wegsprengen.",
    ),
    _m(
        "flesh", "Fleisch", SOLID, 255, (86, 30, 38), debris="blood", debris_chance=0.25,
        grain=16, hardness=1, description_de="Weiches Gewebe. Blutet, wenn man es zerstört.",
    ),
    _m(
        "sinew", "Sehnen", SOLID, 255, (158, 104, 88), flammability=0.03, burn_life=(90, 160),
        grain=12, hardness=2, description_de="Zäh und brennbar. Leitet Nervenstrom.",
    ),
    _m(
        "blood", "Blut", LIQUID, 30, (150, 12, 24), fluidity=5,
        description_de="Löscht Feuer. Ein Schluck heilt ein wenig.",
    ),
    _m(
        "crust", "Schorf", SOLID, 255, (70, 26, 22), hardness=1,
        description_de="Verkrustetes Blut. Bröckelt leicht.",
    ),
    _m(
        "tallow", "Talg", LIQUID, 20, (196, 174, 118), flammability=0.5, burn_life=(10, 25),
        fluidity=3, mobility=0.7, description_de="Fett. Sehr brennbar, macht dich ölig.",
    ),
    _m(
        "acid", "Magensäure", LIQUID, 40, (140, 196, 40), fluidity=5, hazard_dps=60.0, glow=110,
        description_de="Ätzt Fleisch und dich. Meiden!",
    ),
    _m(
        "fume", "Ätzdampf", GAS, -3, (98, 132, 52), life=(60, 160), hazard_dps=8.0, glow=40,
        description_de="Giftiger Dampf. Schadet beim Einatmen.",
    ),
    _m(
        "growth", "Wucherung", SOLID, 255, (124, 72, 116), flammability=0.08,
        burn_life=(40, 90), debris="spores", debris_chance=0.3, grain=14, hardness=1,
        description_de="Wächst und frisst Fleisch. Brennt, gibt Sporen ab.",
    ),
    _m(
        "spores", "Sporen", GAS, -4, (164, 128, 160), flammability=0.6, burn_life=(3, 8),
        life=(120, 240), hazard_dps=3.0, glow=60,
        description_de="Leicht giftig und hochentzündlich.",
    ),
    _m(
        "mucus", "Schleim", LIQUID, 35, (176, 172, 120), fluidity=1, mobility=0.18, grain=12,
        description_de="Zäh. Bremst jede Bewegung.",
    ),
    _m(
        "magma", "Glutblut", LIQUID, 45, (236, 96, 30), fluidity=2, mobility=0.35,
        hazard_dps=40.0, glow=230, grain=20,
        description_de="Glühend heiß. Setzt alles in Brand. Meiden!",
    ),
    _m(
        "pus", "Eiter", LIQUID, 32, (186, 190, 84), fluidity=3, mobility=0.6, grain=10,
        description_de="Vergiftet dich bei Berührung.",
    ),
    _m(
        "spark", "Nervenstrom", FLAME, 255, (190, 220, 255), life=(2, 4), decay_into="spent",
        decay_chance=1.0, hazard_dps=45.0, glow=255, grain=24,
        description_de="Elektrischer Schlag durch die Sehnen. Schmerzhaft.",
    ),
    _m(
        "spent", "Erschöpfte Sehne", SOLID, 255, (110, 72, 64), flammability=0.001,
        burn_life=(60, 120), grain=10, hardness=1,
        description_de="Ausgebrannte Sehne. Erholt sich langsam.",
    ),
    _m(
        "enamel", "Zahnschmelz", SOLID, 255, (206, 214, 222), debris="bone_dust",
        debris_chance=0.5, grain=10, hardness=3, glow=5,
        description_de="Sehr hart. Nur starke Explosionen brechen ihn.",
    ),
)

_FILES = (  # Aktenhalde
    _m(
        "papier", "Papier", SOLID, 255, (237, 230, 210), flammability=0.6, burn_life=(8, 18),
        debris="asche", debris_chance=0.3, grain=8, hardness=1,
        description_de="Brennt schnell und weit.",
    ),
    _m(
        "tintenpapier", "Getränktes Papier", SOLID, 255, (58, 64, 96), grain=8, hardness=1,
        description_de="Mit Tinte vollgesogen. Brennt nicht mehr.",
    ),
    _m(
        "aktendeckel", "Aktendeckel", SOLID, 255, (200, 160, 96), flammability=0.05,
        burn_life=(80, 140), debris="asche", debris_chance=0.2, grain=10, hardness=2,
        description_de="Stabile Pappe. Brennt langsam.",
    ),
    _m(
        "tinte", "Tinte", LIQUID, 30, (30, 42, 90), fluidity=4,
        description_de="Löscht Brände und tränkt Papier.",
    ),
    _m(
        "siegellack", "Siegellack", LIQUID, 38, (176, 32, 42), fluidity=1, mobility=0.3,
        grain=10, description_de="Zäh und rot. Erstarrt an der Luft.",
    ),
    _m(
        "lack", "Lack", SOLID, 255, (140, 24, 34), grain=8, hardness=1,
        description_de="Erstarrter Siegellack. Feuer schmilzt ihn.",
    ),
    _m("asche", "Asche", POWDER, 40, (90, 84, 88), grain=8, hardness=1, description_de="Rest von Papier."),
    _m(
        "stempelfarbe", "Stempelfarbe", LIQUID, 31, (106, 32, 128), fluidity=4,
        description_de="Violett. Wer sie trinkt, fühlt sich genehmigt.",
    ),
)

LIBRARY: dict[str, Material] = {m.key: m for m in (*_BASE, *_BODY, *_FILES)}
assert len(LIBRARY) == len(_BASE) + len(_BODY) + len(_FILES), "duplicate material key"

BASE_KEYS: tuple[str, ...] = tuple(m.key for m in _BASE)

# Stand-ins for keys a set does not contain (followed in a chain, first hit wins).
DEFAULT_ALIASES: dict[str, str] = {
    "rock": "bone", "bone": "rock", "enamel": "bone", "dirt": "flesh", "flesh": "dirt",
    "sinew": "flesh", "spent": "sinew", "crust": "dirt", "growth": "flesh",
    "sand": "bone_dust", "bone_dust": "sand", "water": "blood", "blood": "water",
    "acid": "water", "pus": "water", "mucus": "oil", "oil": "tallow", "tallow": "oil",
    "magma": "fire", "spark": "fire", "steam": "smoke", "fume": "steam", "spores": "smoke",
    "fluxschnaps": "water", "papier": "dirt", "tintenpapier": "dirt", "aktendeckel": "rock",
    "lack": "dirt", "asche": "sand", "tinte": "water", "siegellack": "oil",
    "stempelfarbe": "water",
}  # fmt: skip

# Module attribute -> key. These names resolve in every set (directly or via aliases).
NAMES: dict[str, str] = {
    "ROCK": "rock", "DIRT": "dirt", "SAND": "sand", "WATER": "water", "OIL": "oil",
    "FIRE": "fire", "SMOKE": "smoke", "STEAM": "steam", "FLUXSCHNAPS": "fluxschnaps",
    "BONE": "bone", "BONE_DUST": "bone_dust", "FLESH": "flesh", "SINEW": "sinew",
    "BLOOD": "blood", "CRUST": "crust", "TALLOW": "tallow", "ACID": "acid", "FUME": "fume",
    "GROWTH": "growth", "SPORES": "spores", "MUCUS": "mucus", "MAGMA": "magma", "PUS": "pus",
    "SPARK": "spark", "SPENT": "spent", "ENAMEL": "enamel",
}  # fmt: skip


@dataclass(frozen=True)
class MaterialSet:
    """The materials one universe loads (``air`` and ``bedrock`` first, at most 21).

    Entries are library keys or full :class:`Material` overrides (same key, e.g. a
    differently coloured world edge). ``aliases`` maps keys the set lacks to keys it has.
    """

    key: str
    materials: tuple[str | Material, ...]
    aliases: tuple[tuple[str, str], ...] = ()
    reactions: tuple = field(default=())  # extra key-based Reaction rules of this set

    def resolved(self) -> tuple[Material, ...]:
        return tuple(LIBRARY[m] if isinstance(m, str) else m for m in self.materials)

    def keys(self) -> tuple[str, ...]:
        return tuple(m.key for m in self.resolved())


# ---------------------------------------------------------------------------------------
# Active set state. Lists are rewritten in place; ids are module attributes.
# ---------------------------------------------------------------------------------------

MATERIALS: list[Material] = []
KIND: list[int] = []
FLAMMABILITY: list[float] = []
BURN_RANGE: list[tuple[int, int]] = []
LIFE_RANGE: list[tuple[int, int]] = []
HAZARD_DPS: list[float] = []
NAME_DE: list[str] = []
DEBRIS: list[tuple[int, float]] = []
DECAY_INTO: list[int] = []
GLOW: list[int] = []
HARDNESS: list[int] = []
OPAQUE: list[int] = []  # currents shine through
# The player walks on solids and powders but wades through liquids. A nerve current is
# a flame-like cell inside sinew; the sinew it runs through stays solid.
BLOCKS_BODY: list[bool] = []
# Projectiles stop at everything that is not empty, gas or flame.
STOPS_PROJECTILE: list[bool] = []
KEYS: list[str] = []

MATERIAL_COUNT = 0
ACTIVE: MaterialSet | None = None
GENERATION = 0  # bumped on every activation (caches compare against it)
_index: dict[str, int] = {}
_aliases: dict[str, str] = {}
_listeners: list[Callable[[], None]] = []

# How much smaller a blast or bore gets against each hardness (cells): firm tissue
# shrugs off tiny sparks, enamel only breaks near the centre of a big explosion.
HARDNESS_SHRINK = (0, 0, 2, 9, 10_000)
HARDNESS_DE = ("", "weich", "hart", "sehr hart", "unzerstörbar")

# Named ids, valid for the active set (set by activate).
ROCK = DIRT = SAND = WATER = OIL = FIRE = SMOKE = STEAM = FLUXSCHNAPS = 0
BONE = BONE_DUST = FLESH = SINEW = BLOOD = CRUST = TALLOW = ACID = FUME = 0
GROWTH = SPORES = MUCUS = MAGMA = PUS = SPARK = SPENT = ENAMEL = 0


def resolve(key: str) -> int | None:
    """Id of ``key`` in the active set, following aliases; None if nothing stands in."""
    seen: set[str] = set()
    while key not in _index:
        if key in seen:
            return None
        seen.add(key)
        nxt = _aliases.get(key) or DEFAULT_ALIASES.get(key)
        if nxt is None:
            return None
        key = nxt
    return _index[key]


def id_of(key: str | None, default: int = AIR) -> int:
    """Like :func:`resolve` but never fails (``default`` if nothing stands in)."""
    if key is None:
        return default
    found = resolve(key)
    return default if found is None else found


def opt_id(key: str | None) -> int | None:
    """Id for an optional key (None stays None)."""
    return None if key is None else id_of(key)


def has(key: str) -> bool:
    """True if the active set contains ``key`` itself (not just a stand-in)."""
    return key in _index


def key_of(material: int) -> str:
    return KEYS[material] if 0 <= material < len(KEYS) else "air"


def subscribe(listener: Callable[[], None]) -> None:
    """Call ``listener`` after every activation (and once right away)."""
    _listeners.append(listener)
    listener()


def validate(material_set: MaterialSet) -> None:
    mats = material_set.resolved()
    keys = [m.key for m in mats]
    if keys[:2] != ["air", "bedrock"]:
        raise ValueError(f"{material_set.key}: a set must start with air and bedrock")
    if len(set(keys)) != len(keys):
        raise ValueError(f"{material_set.key}: duplicate material")
    if len(mats) > MAX_MATERIALS:
        raise ValueError(f"{material_set.key}: {len(mats)} materials, at most {MAX_MATERIALS}")
    flames = [m.key for m in mats if m.kind == FLAME]
    if flames and flames[0] != "fire":
        raise ValueError(f"{material_set.key}: fire must be the first flame (core rule)")
    for alias, target in material_set.aliases:
        if target not in keys:
            raise ValueError(f"{material_set.key}: alias {alias} -> {target} not in set")


def activate(material_set: MaterialSet) -> None:
    """Make ``material_set`` the active one: rewrite all tables and named ids."""
    global ACTIVE, MATERIAL_COUNT, GENERATION
    validate(material_set)
    mats = material_set.resolved()
    _index.clear()
    _index.update({m.key: i for i, m in enumerate(mats)})
    _aliases.clear()
    _aliases.update(dict(material_set.aliases))
    ACTIVE = material_set
    MATERIAL_COUNT = len(mats)
    MATERIALS[:] = mats
    KEYS[:] = [m.key for m in mats]
    KIND[:] = [m.kind for m in mats]
    FLAMMABILITY[:] = [m.flammability for m in mats]
    BURN_RANGE[:] = [m.burn_life for m in mats]
    LIFE_RANGE[:] = [m.life for m in mats]
    HAZARD_DPS[:] = [m.hazard_dps for m in mats]
    NAME_DE[:] = [m.name_de for m in mats]
    DEBRIS[:] = [(id_of(m.debris), m.debris_chance if resolve(m.debris) is not None else 0.0) for m in mats]
    DECAY_INTO[:] = [id_of(m.decay_into) for m in mats]
    GLOW[:] = [m.glow for m in mats]
    HARDNESS[:] = [m.hardness for m in mats]
    OPAQUE[:] = [int(m.kind in (SOLID, POWDER)) for m in mats]
    BLOCKS_BODY[:] = [m.kind in (SOLID, POWDER) or m.key == "spark" for m in mats]
    STOPS_PROJECTILE[:] = [
        m.kind in (SOLID, POWDER, LIQUID) or m.key == "spark" for m in mats
    ]
    module = globals()
    for name, key in NAMES.items():
        module[name] = id_of(key)
    GENERATION += 1
    for listener in _listeners:
        listener()


# ---------------------------------------------------------------------------------------
# Sets. Universes pick theirs by key (src/universes).
# ---------------------------------------------------------------------------------------

# The current game's organism, id-compatible with the old fixed table. It becomes the
# real Fleischwelt set (11 base materials + 10 own) in work package U1.
KOERPER = MaterialSet(
    "koerper",
    (
        "air",
        _m(
            "bedrock", "Panzerknochen", SOLID, 255, (40, 32, 34), grain=4, hardness=4,
            description_de="Uralter Panzer. Nichts kann ihn zerstören.",
        ),
        "bone", "bone_dust", "flesh", "sinew", "blood", "crust", "tallow", "acid", "fire",
        "smoke", "fume", "growth", "spores", "mucus", "magma", "pus", "spark", "spent",
        "enamel",
    ),
)

AKTENHALDE = MaterialSet(
    "aktenhalde",
    (
        *BASE_KEYS, "papier", "tintenpapier", "aktendeckel", "tinte", "siegellack", "lack",
        "asche", "stempelfarbe",
    ),
    aliases=(
        # older generators and spells ask for organism materials: map them onto paperwork
        ("flesh", "papier"), ("growth", "papier"), ("bone", "aktendeckel"),
        ("enamel", "aktendeckel"), ("sinew", "aktendeckel"), ("spent", "aktendeckel"),
        ("crust", "lack"), ("bone_dust", "asche"), ("blood", "tinte"), ("pus", "tinte"),
        ("acid", "stempelfarbe"), ("mucus", "siegellack"), ("tallow", "oil"),
        ("magma", "fire"), ("spark", "fire"), ("fume", "steam"), ("spores", "smoke"),
    ),
)

SETS: dict[str, MaterialSet] = {s.key: s for s in (KOERPER, AKTENHALDE)}
# Sets changed by a universe rule (e.g. flammability), keyed "<set>+<rule><rank>".
DERIVED: dict[str, MaterialSet] = {}


def find_set(key: str) -> MaterialSet | None:
    return SETS.get(key) or DERIVED.get(key)
DEFAULT_SET = KOERPER


def activate_key(key: str) -> None:
    """Activate a registered set by key (no-op if it is already active)."""
    if ACTIVE is not None and ACTIVE.key == key:
        return
    activate(SETS[key])


activate(DEFAULT_SET)


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
    """Palette of the active set, indexed ``(material * VARIANTS + variant) * LIGHT_LEVELS + level``.

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
