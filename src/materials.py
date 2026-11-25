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


def _m(
    key: str, name_de: str, kind: int, density: int, color: tuple[int, int, int], **kw
) -> Material:
    return Material(key, name_de, kind, density, color, **kw)


# ---------------------------------------------------------------------------------------
# Library: every material of every universe, by key.
# ---------------------------------------------------------------------------------------

_BASE = (
    _m("air", "Leere", EMPTY, 0, (30, 14, 18), grain=4),
    _m(
        "bedrock",
        "Weltrand",
        SOLID,
        255,
        (40, 32, 34),
        grain=4,
        hardness=4,
        description_de="Der Rand der Welt. Nichts kann ihn zerstören.",
    ),
    _m(
        "rock",
        "Fels",
        SOLID,
        255,
        (104, 98, 92),
        debris="sand",
        debris_chance=0.35,
        grain=10,
        hardness=2,
        description_de="Gewöhnlicher Stein. Explosionen sprengen ihn.",
    ),
    _m(
        "dirt",
        "Erde",
        SOLID,
        255,
        (96, 70, 48),
        debris="sand",
        debris_chance=0.2,
        grain=14,
        hardness=1,
        description_de="Weich. Lässt sich leicht wegsprengen.",
    ),
    _m(
        "sand",
        "Sand",
        POWDER,
        60,
        (190, 168, 116),
        grain=12,
        hardness=1,
        description_de="Rieselt.",
    ),
    _m(
        "water",
        "Wasser",
        LIQUID,
        30,
        (52, 96, 170),
        fluidity=5,
        description_de="Löscht Feuer und macht nass.",
    ),
    _m(
        "oil",
        "Öl",
        LIQUID,
        20,
        (60, 50, 34),
        flammability=0.5,
        burn_life=(10, 25),
        fluidity=3,
        mobility=0.7,
        description_de="Schwimmt oben. Sehr brennbar, macht dich ölig.",
    ),
    _m(
        "fire",
        "Feuer",
        FLAME,
        -1,
        (255, 160, 40),
        life=(30, 60),
        decay_into="smoke",
        decay_chance=0.25,
        hazard_dps=15.0,
        glow=255,
        description_de="Verbrennt dich und alles Brennbare.",
    ),
    _m(
        "smoke",
        "Rauch",
        GAS,
        -2,
        (54, 44, 46),
        life=(50, 140),
        description_de="Harmlos, verzieht sich.",
    ),
    _m(
        "steam",
        "Dampf",
        GAS,
        -3,
        (176, 184, 196),
        life=(60, 160),
        decay_into="water",
        decay_chance=0.08,
        hazard_dps=3.0,
        description_de="Heißer Dampf. Verbrüht ein wenig.",
    ),
    _m(
        "fluxschnaps",
        "Flux-Schnaps",
        LIQUID,
        28,
        (40, 210, 190),
        flammability=0.3,
        burn_life=(6, 14),
        fluidity=4,
        glow=90,
        description_de="Leuchtet türkis. Ein Schluck macht beschwipst.",
    ),
)

_BODY = (  # the organism of the current game (transitional Fleischwelt set)
    _m(
        "bone",
        "Knochen",
        SOLID,
        255,
        (150, 138, 112),
        debris="bone_dust",
        debris_chance=0.35,
        grain=10,
        hardness=2,
        description_de="Fest. Kleine Zauber prallen ab, Explosionen sprengen ihn.",
    ),
    _m(
        "bone_dust",
        "Knochenstaub",
        POWDER,
        60,
        (172, 158, 128),
        grain=10,
        hardness=1,
        description_de="Rieselt. Lässt sich leicht wegsprengen.",
    ),
    _m(
        "flesh",
        "Fleisch",
        SOLID,
        255,
        (86, 30, 38),
        debris="blood",
        debris_chance=0.25,
        grain=16,
        hardness=1,
        description_de="Weiches Gewebe. Blutet, wenn man es zerstört.",
    ),
    _m(
        "sinew",
        "Sehnen",
        SOLID,
        255,
        (158, 104, 88),
        flammability=0.03,
        burn_life=(90, 160),
        grain=12,
        hardness=2,
        description_de="Zäh und brennbar. Leitet Nervenstrom.",
    ),
    _m(
        "blood",
        "Blut",
        LIQUID,
        30,
        (150, 12, 24),
        fluidity=5,
        description_de="Löscht Feuer. Ein Schluck heilt ein wenig.",
    ),
    _m(
        "crust",
        "Schorf",
        SOLID,
        255,
        (70, 26, 22),
        hardness=1,
        description_de="Verkrustetes Blut. Bröckelt leicht.",
    ),
    _m(
        "tallow",
        "Talg",
        LIQUID,
        20,
        (196, 174, 118),
        flammability=0.5,
        burn_life=(10, 25),
        fluidity=3,
        mobility=0.7,
        description_de="Fett. Sehr brennbar, macht dich ölig.",
    ),
    _m(
        "acid",
        "Magensäure",
        LIQUID,
        40,
        (140, 196, 40),
        fluidity=5,
        hazard_dps=60.0,
        glow=110,
        description_de="Ätzt Fleisch und dich. Meiden!",
    ),
    _m(
        "fume",
        "Ätzdampf",
        GAS,
        -3,
        (98, 132, 52),
        life=(60, 160),
        hazard_dps=8.0,
        glow=40,
        description_de="Giftiger Dampf. Schadet beim Einatmen.",
    ),
    _m(
        "growth",
        "Wucherung",
        SOLID,
        255,
        (124, 72, 116),
        flammability=0.08,
        burn_life=(40, 90),
        debris="spores",
        debris_chance=0.3,
        grain=14,
        hardness=1,
        description_de="Wächst und frisst Fleisch. Brennt, gibt Sporen ab.",
    ),
    _m(
        "spores",
        "Sporen",
        GAS,
        -4,
        (164, 128, 160),
        flammability=0.6,
        burn_life=(3, 8),
        life=(120, 240),
        hazard_dps=3.0,
        glow=60,
        description_de="Leicht giftig und hochentzündlich.",
    ),
    _m(
        "mucus",
        "Schleim",
        LIQUID,
        35,
        (176, 172, 120),
        fluidity=1,
        mobility=0.18,
        grain=12,
        description_de="Zäh. Bremst jede Bewegung.",
    ),
    _m(
        "magma",
        "Glutblut",
        LIQUID,
        45,
        (236, 96, 30),
        fluidity=2,
        mobility=0.35,
        hazard_dps=40.0,
        glow=230,
        grain=20,
        description_de="Glühend heiß. Setzt alles in Brand. Meiden!",
    ),
    _m(
        "pus",
        "Eiter",
        LIQUID,
        32,
        (186, 190, 84),
        fluidity=3,
        mobility=0.6,
        grain=10,
        description_de="Vergiftet dich bei Berührung.",
    ),
    _m(
        "spark",
        "Nervenstrom",
        FLAME,
        255,
        (190, 220, 255),
        life=(2, 4),
        decay_into="spent",
        decay_chance=1.0,
        hazard_dps=45.0,
        glow=255,
        grain=24,
        description_de="Elektrischer Schlag durch die Sehnen. Schmerzhaft.",
    ),
    _m(
        "spent",
        "Erschöpfte Sehne",
        SOLID,
        255,
        (110, 72, 64),
        flammability=0.001,
        burn_life=(60, 120),
        grain=10,
        hardness=1,
        description_de="Ausgebrannte Sehne. Erholt sich langsam.",
    ),
    _m(
        "enamel",
        "Zahnschmelz",
        SOLID,
        255,
        (206, 214, 222),
        debris="bone_dust",
        debris_chance=0.5,
        grain=10,
        hardness=3,
        glow=5,
        description_de="Sehr hart. Nur starke Explosionen brechen ihn.",
    ),
)

_FILES = (  # Aktenhalde
    _m(
        "papier",
        "Papier",
        SOLID,
        255,
        (237, 230, 210),
        flammability=0.6,
        burn_life=(8, 18),
        debris="asche",
        debris_chance=0.3,
        grain=8,
        hardness=1,
        description_de="Brennt schnell und weit.",
    ),
    _m(
        "tintenpapier",
        "Getränktes Papier",
        SOLID,
        255,
        (58, 64, 96),
        grain=8,
        hardness=1,
        description_de="Mit Tinte vollgesogen. Brennt nicht mehr.",
    ),
    _m(
        "aktendeckel",
        "Aktendeckel",
        SOLID,
        255,
        (200, 160, 96),
        flammability=0.05,
        burn_life=(80, 140),
        debris="asche",
        debris_chance=0.2,
        grain=10,
        hardness=2,
        description_de="Stabile Pappe. Brennt langsam.",
    ),
    _m(
        "tinte",
        "Tinte",
        LIQUID,
        30,
        (30, 42, 90),
        fluidity=4,
        description_de="Löscht Brände und tränkt Papier.",
    ),
    _m(
        "siegellack",
        "Siegellack",
        LIQUID,
        38,
        (176, 32, 42),
        fluidity=1,
        mobility=0.3,
        grain=10,
        description_de="Zäh und rot. Erstarrt an der Luft.",
    ),
    _m(
        "lack",
        "Lack",
        SOLID,
        255,
        (140, 24, 34),
        grain=8,
        hardness=1,
        description_de="Erstarrter Siegellack. Feuer schmilzt ihn.",
    ),
    _m(
        "asche",
        "Asche",
        POWDER,
        40,
        (90, 84, 88),
        grain=8,
        hardness=1,
        description_de="Rest von Papier.",
    ),
    _m(
        "stempelfarbe",
        "Stempelfarbe",
        LIQUID,
        31,
        (106, 32, 128),
        fluidity=4,
        description_de="Violett. Wer sie trinkt, fühlt sich genehmigt.",
    ),
)

_GLIBBRIA = (
    _m(
        "glibber",
        "Glibber",
        SOLID,
        255,
        (100, 220, 160),
        grain=6,
        hardness=1,
        description_de="Grüner, federnder Wackelpudding.",
    ),
    _m(
        "glibber_rot",
        "Roter Glibber",
        SOLID,
        255,
        (230, 80, 110),
        grain=6,
        hardness=1,
        flammability=0.3,
        description_de="Brennbarer süßer Gelee.",
    ),
    _m(
        "brausesirup",
        "Brausesirup",
        LIQUID,
        32,
        (246, 160, 224),  # bible 03: #F6A0E0
        fluidity=3,
        description_de="Prickelnder, klebriger Sirup.",
    ),
    _m(
        "schaum",
        "Zuckerschaum",
        GAS,
        -1,
        (240, 240, 255),
        description_de="Leichter Schaum auf Brauselachen.",
    ),
    _m(
        "kaugummi",
        "Kaugummi",
        SOLID,
        255,
        (230, 130, 180),
        grain=4,
        hardness=2,
        description_de="Zäh und extrem klebrig.",
    ),
    _m(
        "zuckerguss",
        "Zuckerguss",
        SOLID,
        255,
        (250, 245, 235),
        grain=4,
        hardness=1,
        description_de="Knusprige Schicht, karamellisiert bei Hitze.",
    ),
)

_KRUEMELREICH: tuple[Material, ...] = (
    _m(
        "kruemel",
        "Krümel",
        SOLID,
        255,
        (205, 160, 110),
        debris="brosel",
        debris_chance=0.4,
        grain=10,
        hardness=2,
        description_de="Trockener Teigboden. Zerbröselt leicht.",
    ),
    _m(
        "brosel",
        "Brösel",
        POWDER,
        60,
        (215, 175, 120),
        grain=12,
        hardness=1,
        description_de="Feine Kuchenbrösel, rieseln durch Ritzen.",
    ),
    _m(
        "zucker",
        "Zucker",
        POWDER,
        65,
        (245, 245, 250),
        grain=8,
        hardness=1,
        flammability=0.1,
        description_de="Weißer Kristallzucker. Schmilzt bei Feuer.",
    ),
    _m(
        "karamell",
        "Karamell",
        LIQUID,
        25,
        (160, 90, 30),
        mobility=0.3,
        fluidity=2,
        description_de="Klebrige, heiße Karamellmasse.",
    ),
    _m(
        "honig",
        "Honig",
        LIQUID,
        20,
        (220, 150, 20),
        mobility=0.2,
        fluidity=2,
        description_de="Dickflüssig und süß.",
    ),
    _m(
        "fliese",
        "Kachelfliese",
        SOLID,
        255,
        (180, 185, 190),
        grain=2,
        hardness=3,
        description_de="Backstubenfliesen. Hart und hitzebeständig.",
    ),
    _m(
        "staubfluse",
        "Staubfluse",
        POWDER,
        30,
        (130, 125, 120),
        grain=14,
        hardness=1,
        flammability=0.3,
        description_de="Trockener Backstubenstaub. Leicht entflammbar.",
    ),
)

_SPORENKLUB: tuple[Material, ...] = (
    _m(
        "pilzfleisch",
        "Pilzfleisch",
        SOLID,
        255,
        (120, 90, 80),
        grain=6,
        hardness=2,
        description_de="Zähes, faseriges Geflecht alter Riesenpilze.",
    ),
    _m(
        "pilzhut",
        "Pilzhut",
        SOLID,
        255,
        (170, 70, 60),
        grain=8,
        hardness=2,
        description_de="Glatte, samtige Kappe eines Riesenpilzes.",
    ),
    _m(
        "leuchtsporen",
        "Leuchtsporen",
        POWDER,
        40,
        (140, 255, 100),
        grain=10,
        hardness=1,
        glow=160,
        description_de="Fluoreszierender Sporenstaub.",
    ),
    _m(
        "neonsaft",
        "Neonsaft",
        LIQUID,
        25,
        (50, 240, 180),
        fluidity=4,
        glow=160,
        description_de="Hell leuchtender Nährsaft des Sporenklubs.",
    ),
    _m(
        "nebel",
        "Sporennebel",
        GAS,
        -1,
        (160, 220, 190),
        life=(150, 255),  # life is stored in a byte
        description_de="Dichter Dunst, der den Tanzboden verhüllt.",
    ),
)

_ABTEI: tuple[Material, ...] = (
    _m(
        "mauerwerk",
        "Mauerwerk",
        SOLID,
        255,
        (110, 115, 120),
        grain=10,
        hardness=3,
        description_de="Uralter nasser Stein der versunkenen Klosterruine.",
    ),
    _m(
        "buntglas",
        "Buntglas",
        SOLID,
        255,
        (180, 70, 140),
        grain=4,
        hardness=2,
        description_de="Zerbrechliches sakrales Kirchenfensterglas.",
    ),
    _m(
        "kerzenwachs",
        "Kerzenwachs",
        SOLID,
        255,
        (235, 230, 200),
        grain=4,
        hardness=1,
        flammability=0.2,
        description_de="Geweihtes Bienenwachs, schmilzt bei Feuer.",
    ),
    _m(
        "glockenbronze",
        "Glockenbronze",
        SOLID,
        255,
        (175, 130, 60),
        grain=6,
        hardness=3,
        description_de="Schwere Bronze uralter Kirchenglocken.",
    ),
    _m(
        "algen",
        "Algen",
        SOLID,
        255,
        (40, 120, 50),
        grain=8,
        hardness=1,
        description_de="Glibbrige Grünalgen auf überflutetem Gestein.",
    ),
    _m(
        "weihrauch",
        "Weihrauch",
        GAS,
        -1,
        (210, 200, 220),
        life=(200, 255),  # life is stored in a byte
        description_de="Duftender Nebel uralter Weihrauchkessel.",
    ),
)

_EVIL_HOMES = (  # home worlds of the three evil selves (Contract V17 §2, Card F18)
    _m(
        "goldboden",
        "Goldboden",
        SOLID,
        255,
        (222, 184, 70),
        grain=6,
        glow=40,
        hardness=3,
        description_de="Poliertes Gold des Thronsaals. Fest, aber spiegelglatt: dreifacher Bremsweg.",
    ),
    _m(
        "lichtstein",
        "Lichtstein",
        SOLID,
        255,
        (238, 232, 205),
        grain=5,
        glow=110,
        hardness=2,
        description_de="Leuchtender Stein der Lichtkathedrale.",
    ),
    _m(
        "heiliges_licht",
        "Heiliges Licht",
        GAS,
        -1,
        (255, 248, 190),
        life=(150, 220),  # life is stored in a byte
        hazard_dps=4.0,
        glow=160,
        description_de="Gleißendes Licht der Bösen Guten. Brennt auf der Haut: 4 Schaden pro Sekunde.",
    ),
    _m(
        "foerderband",
        "Förderband",
        SOLID,
        255,
        (62, 64, 74),
        grain=4,
        hardness=3,
        description_de="Laufendes Band der Fabrikhalle. Schiebt alles, was darauf steht.",
    ),
    _m(
        "stahl",
        "Stahl",
        SOLID,
        255,
        (150, 156, 168),
        grain=5,
        hardness=3,
        description_de="Sehr harter Werkstahl der Bösen Omega.",
    ),
)

_EXPANSION_ALCHEMY = (
    _m(
        "schutztonikum",
        "Schutztonikum",
        LIQUID,
        28,
        (64, 255, 224),
        fluidity=4,
        glow=140,
        description_de="Funkelndes Alchemie-Tonikum: verleiht einen Schutzschild und Flux-Schub.",
    ),
    _m(
        "midas_schmelze",
        "Midas-Schmelze",
        LIQUID,
        48,
        (255, 215, 0),
        fluidity=3,
        glow=160,
        description_de="Flammendes Reingold: verwandelt feste Materie in Golderz-Adern.",
    ),
)

_EXPANSION_UNIVERSES = (
    # J01 schrott
    _m("altmetall", "Altmetall", SOLID, 255, (112, 101, 88), hardness=3, grain=10, debris="roststaub", debris_chance=0.2),
    _m("roststaub", "Roststaub", POWDER, 55, (181, 80, 48), flammability=0.85, burn_life=(6, 14), hardness=1, grain=10),
    _m("fluessigeisen", "Flüssigeisen", LIQUID, 50, (255, 112, 32), fluidity=2, mobility=0.4, hazard_dps=45.0, glow=220),
    _m("magnetit", "Magnetiterz", SOLID, 255, (48, 48, 56), hardness=3, grain=6, glow=25),
    # J02 kuchen
    _m("biskuit", "Biskuitteig", SOLID, 255, (232, 192, 122), hardness=1, grain=8, flammability=0.25, burn_life=(20, 40)),
    _m("zuckerglasur", "Zuckerglasur", SOLID, 255, (255, 245, 234), hardness=2, grain=4, flammability=0.1, burn_life=(12, 24)),
    _m("karamell_kuchen", "Kochendes Karamell", LIQUID, 36, (184, 96, 20), fluidity=1, mobility=0.2, hazard_dps=18.0, flammability=0.35),
    _m("puderzucker", "Puderzucker", POWDER, 40, (248, 248, 255), flammability=0.9, burn_life=(4, 10), hardness=1, grain=4),
    # J03 spule
    _m("kupferdraht", "Kupferdraht", SOLID, 255, (200, 117, 64), hardness=3, grain=6),
    _m("isolator", "Isolierkeramik", SOLID, 255, (74, 85, 104), hardness=3, grain=6),
    _m("plasma", "Plasmagas", GAS, -5, (112, 224, 255), life=(100, 180), hazard_dps=32.0, glow=240),
    _m("elektrolyt", "Elektrolytlösung", LIQUID, 30, (64, 255, 160), fluidity=5, glow=110),
    # J04 uhrwerkwueste
    _m("chrono_sand", "Zeitensand", POWDER, 52, (224, 192, 112), hardness=1, grain=10),
    _m("messing_zahnrad", "Zahnradmessing", SOLID, 255, (212, 175, 55), hardness=3, grain=6, glow=15),
    _m("fluessig_zeit", "Flüssige Zeit", LIQUID, 34, (192, 216, 232), fluidity=2, mobility=0.25, glow=90),
    _m("unruh_fett", "Uhrenöl", LIQUID, 22, (138, 112, 48), fluidity=4, flammability=0.6, burn_life=(12, 28)),
    # J05 suppenmeer
    _m("bouillon", "Fleischbrühe", LIQUID, 32, (229, 193, 88), fluidity=5),
    _m("suppenfett", "Suppenfett", LIQUID, 18, (255, 240, 144), fluidity=4, flammability=0.7, burn_life=(15, 30)),
    _m("nudel_teig", "Nudelteig", SOLID, 255, (245, 224, 160), hardness=1, grain=6),
    _m("pfefferdampf", "Pfeffergas", GAS, -2, (74, 64, 48), life=(160, 240)),
    # J06 freizeitpark
    _m("rost_schiene", "Achterbahnschiene", SOLID, 255, (128, 80, 64), hardness=3, grain=8),
    _m("zuckerwatte_rot", "Zuckerwatte", POWDER, 28, (255, 128, 160), flammability=0.75, burn_life=(6, 14), hardness=1),
    _m("helium_gas", "Helium", GAS, -6, (224, 255, 255), life=(180, 250)),
    _m("spiegel_glas", "Spiegelglas", SOLID, 255, (176, 196, 222), hardness=2, grain=4),
)

_PHASE3_UNIVERSES = (
    # R01 anatomie_park
    _m("lebergewebe", "Lebergewebe", SOLID, 255, (168, 72, 78), hardness=2, grain=8),
    _m("magensaeure", "Magensäure", LIQUID, 33, (156, 228, 72), fluidity=4, hazard_dps=25.0, glow=90),
    _m("knochen_bruecke", "Knochenbrücke", SOLID, 255, (236, 226, 204), hardness=3, grain=6),
    _m("adrenalin_dampf", "Adrenalindampf", GAS, -3, (255, 168, 128), life=(140, 220), glow=60),
    # R02 pastell_hoelle
    _m("pluesch_wand", "Plüschwand", SOLID, 255, (246, 182, 214), hardness=1, grain=4, flammability=0.6, burn_life=(10, 20)),
    _m("erdbeernektar", "Erdbeernektar", LIQUID, 30, (255, 118, 164), fluidity=4, glow=75, description_de="Süßer Pastellnektar: verleiht Zuckerschub und Schutzschild, heilt nie direkt."),
    _m("glitzer_sand", "Glitzersand", POWDER, 45, (248, 220, 255), hardness=1, grain=10, glow=120),
    _m("einhorn_gas", "Einhorndunst", GAS, -4, (218, 192, 255), life=(160, 240), glow=80),
    # R03 klonenberg_welt
    _m("klon_fleisch", "Klonengewebe", SOLID, 255, (214, 152, 134), hardness=2, grain=6),
    _m("bartstoppel_sand", "Bartstoppelsand", POWDER, 50, (110, 92, 78), hardness=1, grain=10),
    _m("rasier_schaum", "Rasierschaum", GAS, -2, (242, 248, 255), life=(150, 230)),
    _m("spiegel_lauge", "Spiegellauge", LIQUID, 31, (164, 214, 224), fluidity=5),
    # R04 talent_kosmos
    _m("buehnen_stein", "Bühnenstein", SOLID, 255, (82, 74, 108), hardness=3, grain=6),
    _m("nebelmaschinen_dunst", "Bühnennebel", GAS, -3, (206, 214, 234), life=(170, 250)),
    _m("applaus_gold", "Applausstaub", POWDER, 58, (248, 212, 74), hardness=1, grain=8, glow=90),
    _m("scheinwerfer_plasma", "Scheinwerfer-Plasma", LIQUID, 26, (255, 242, 148), fluidity=4, glow=180),
    # R05 antrags_labyrinth
    _m("formular_beton", "Formularbeton", SOLID, 255, (186, 182, 168), hardness=3, grain=8),
    _m("tacker_schrott", "Tackerklammern", POWDER, 64, (148, 154, 164), hardness=2, grain=10),
    _m("kaffee_alt", "Abgestandener Kaffee", LIQUID, 31, (76, 48, 28), fluidity=4),
    _m("stempel_dunst", "Stempelfarb-Dunst", GAS, -2, (168, 92, 186), life=(140, 220)),
    # R06 krawatten_planet
    _m("akten_marmor", "Konzernmarmor", SOLID, 255, (142, 148, 156), hardness=3, grain=5),
    _m("espresso_schlamm", "Espressoschlamm", LIQUID, 35, (64, 38, 22), fluidity=2, mobility=0.4),
    _m("krawatten_stoff", "Krawattengewebe", POWDER, 42, (98, 64, 128), flammability=0.7, burn_life=(8, 16), hardness=1),
    _m("meeting_nebel", "Meeting-Dunst", GAS, -2, (172, 176, 184), life=(160, 240)),
    # S01 klo_paradies
    _m("porzellan_glanz", "Glanzporzellan", SOLID, 255, (242, 248, 252), hardness=3, grain=4),
    _m("heilquell_wasser", "Heilquell-Wasser", LIQUID, 29, (124, 224, 246), fluidity=5, glow=85, description_de="Klares Quellwasser: füllt Schild und Flux auf, heilt jedoch keine Lebenspunkte."),
    _m("seifenschaum", "Seifenschaum", GAS, -4, (230, 248, 255), life=(160, 240)),
    _m("bimsstein_mehl", "Bimssteinmehl", POWDER, 46, (216, 210, 198), hardness=1, grain=8),
    # S02 matroschka_simulation
    _m("voxel_wand", "Voxelblock", SOLID, 255, (72, 138, 168), hardness=3, grain=4),
    _m("cache_fluessigkeit", "Cache-Lösung", LIQUID, 28, (96, 224, 192), fluidity=5, glow=70),
    _m("pixel_sand", "Pixelsand", POWDER, 48, (152, 232, 214), hardness=1, grain=4),
    _m("ram_dunst", "Speichernebel", GAS, -3, (128, 192, 214), life=(150, 230)),
    # S03 kollektiv_buerokratie
    _m("waben_stahl", "Wabenstahl", SOLID, 255, (156, 134, 78), hardness=3, grain=6),
    _m("tinten_nectar", "Tintennektar", LIQUID, 32, (62, 54, 132), fluidity=4),
    _m("lochkarten_staub", "Lochkartenstaub", POWDER, 44, (224, 212, 176), flammability=0.7, hardness=1, grain=8),
    _m("synchro_gas", "Synchrongas", GAS, -3, (198, 224, 132), life=(160, 240)),
    # S04 unsterblichkeits_resort
    _m("marmor_pool", "Poolmarmor", SOLID, 255, (228, 236, 242), hardness=3, grain=5),
    _m("cocktail_elixir", "Schirmchen-Elixier", LIQUID, 29, (255, 146, 98), fluidity=4, glow=60),
    _m("sonnencreme_sand", "Resortsand", POWDER, 50, (244, 222, 174), hardness=1, grain=10),
    _m("sauna_dampf", "Saunadampf", GAS, -4, (238, 244, 248), life=(140, 210)),
    # S05 schroedinger_kammer
    _m("karton_wand", "Versuchskarton", SOLID, 255, (176, 138, 96), hardness=1, grain=8, flammability=0.8, burn_life=(8, 18)),
    _m("quanten_supp", "Quantensuppe", LIQUID, 31, (148, 112, 248), fluidity=4, glow=120),
    _m("wellen_staub", "Wellenstaub", POWDER, 45, (186, 168, 248), hardness=1, grain=8),
    _m("ungewissheits_nebel", "Ungewissheitsnebel", GAS, -4, (164, 152, 214), life=(160, 250), glow=65),
    # S06 kater_bunker
    _m("bunker_blei", "Bunkerblei", SOLID, 255, (74, 78, 88), hardness=3, grain=6),
    _m("konter_brause", "Konterbrause", LIQUID, 30, (232, 198, 68), fluidity=5, glow=50),
    _m("kopfschmerz_asche", "Katerasche", POWDER, 40, (118, 114, 112), hardness=1, grain=8),
    _m("abgestandene_luft", "Bunkerluft", GAS, -1, (144, 148, 138), life=(180, 250)),
)

LIBRARY: dict[str, Material] = {
    m.key: m
    for m in (
        *_BASE,
        *_BODY,
        *_FILES,
        *_GLIBBRIA,
        *_KRUEMELREICH,
        *_SPORENKLUB,
        *_ABTEI,
        *_EVIL_HOMES,
        *_EXPANSION_ALCHEMY,
        *_EXPANSION_UNIVERSES,
        *_PHASE3_UNIVERSES,
    )
}
assert len(LIBRARY) == (
    len(_BASE)
    + len(_BODY)
    + len(_FILES)
    + len(_GLIBBRIA)
    + len(_KRUEMELREICH)
    + len(_SPORENKLUB)
    + len(_ABTEI)
    + len(_EVIL_HOMES)
    + len(_EXPANSION_ALCHEMY)
    + len(_EXPANSION_UNIVERSES)
    + len(_PHASE3_UNIVERSES)
), "duplicate material key"

REALITY_ALIASES: dict[str, str] = {}


def resolve_shift_alias(key: str) -> str:
    """Resolve active reality-shift material alias chains (Phase I04)."""
    seen: set[str] = set()
    cur = key
    while cur in REALITY_ALIASES and cur not in seen:
        seen.add(cur)
        cur = REALITY_ALIASES[cur]
    return cur

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
MAT_ID: dict[str, int] = {}

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
    DEBRIS[:] = [
        (id_of(m.debris), m.debris_chance if resolve(m.debris) is not None else 0.0) for m in mats
    ]
    DECAY_INTO[:] = [id_of(m.decay_into) for m in mats]
    GLOW[:] = [m.glow for m in mats]
    HARDNESS[:] = [m.hardness for m in mats]
    OPAQUE[:] = [int(m.kind in (SOLID, POWDER)) for m in mats]
    BLOCKS_BODY[:] = [m.kind in (SOLID, POWDER) or m.key == "spark" for m in mats]
    STOPS_PROJECTILE[:] = [m.kind in (SOLID, POWDER, LIQUID) or m.key == "spark" for m in mats]
    module = globals()
    for name, key in NAMES.items():
        module[name] = id_of(key)
    MAT_ID.clear()
    for k in LIBRARY:
        MAT_ID[k] = id_of(k)
    for k, target in (
        ("stone", "rock"),
        ("gold_vein", "rock"),
        ("rust", "rock"),
        ("zucker", "sand"),
    ):
        MAT_ID.setdefault(k, id_of(target))
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
            "bedrock",
            "Panzerknochen",
            SOLID,
            255,
            (40, 32, 34),
            grain=4,
            hardness=4,
            description_de="Uralter Panzer. Nichts kann ihn zerstören.",
        ),
        "bone",
        "bone_dust",
        "flesh",
        "sinew",
        "blood",
        "crust",
        "tallow",
        "acid",
        "fire",
        "smoke",
        "fume",
        "growth",
        "spores",
        "mucus",
        "magma",
        "pus",
        "spark",
        "spent",
        "enamel",
    ),
)

AKTENHALDE = MaterialSet(
    "aktenhalde",
    (
        *BASE_KEYS,
        "papier",
        "tintenpapier",
        "aktendeckel",
        "tinte",
        "siegellack",
        "lack",
        "asche",
        "stempelfarbe",
    ),
    aliases=(
        # older generators and spells ask for organism materials: map them onto paperwork
        ("flesh", "papier"),
        ("growth", "papier"),
        ("bone", "aktendeckel"),
        ("enamel", "aktendeckel"),
        ("sinew", "papier"),  # bridges as soft as the paper around them (playtest)
        ("spent", "aktendeckel"),
        ("crust", "lack"),
        ("bone_dust", "asche"),
        ("blood", "tinte"),
        ("pus", "tinte"),
        ("acid", "stempelfarbe"),
        ("mucus", "siegellack"),
        ("tallow", "oil"),
        ("magma", "fire"),
        ("spark", "fire"),
        ("fume", "steam"),
        ("spores", "smoke"),
    ),
)

FLEISCHWELT = MaterialSet(
    "fleischwelt",
    (
        *BASE_KEYS,
        "flesh",
        "bone",
        "enamel",
        "blood",
        "acid",
        "growth",
        "spores",
        "tallow",
        "crust",
        "magma",
    ),
)

GLIBBRIA = MaterialSet(
    "glibbria",
    (
        *BASE_KEYS,
        "glibber",
        "glibber_rot",
        "brausesirup",
        "schaum",
        "kaugummi",
        "zuckerguss",
    ),
)

KRUEMELREICH = MaterialSet(
    "kruemelreich",
    (
        *BASE_KEYS,
        "kruemel",
        "brosel",
        "zucker",
        "karamell",
        "honig",
        "fliese",
        "staubfluse",
    ),
)

SPORENKLUB = MaterialSet(
    "sporenklub",
    (
        *BASE_KEYS,
        "pilzfleisch",
        "pilzhut",
        "leuchtsporen",
        "neonsaft",
        "nebel",
    ),
)

ABTEI = MaterialSet(
    "abtei",
    (
        *BASE_KEYS,
        "mauerwerk",
        "buntglas",
        "kerzenwachs",
        "glockenbronze",
        "algen",
        "weihrauch",
    ),
)

# Home worlds of the evil selves (Contract V17 §2): base materials plus their own few.
_HOME_ALIASES = (
    ("flesh", "__wall__"),
    ("growth", "__wall__"),
    ("bone", "__wall__"),
    ("enamel", "__wall__"),
    ("sinew", "__wall__"),
    ("spent", "__wall__"),
    ("crust", "__wall__"),
    ("bone_dust", "sand"),
    ("blood", "water"),
    ("pus", "water"),
    ("acid", "water"),
    ("mucus", "water"),
    ("tallow", "oil"),
    ("magma", "fire"),
    ("spark", "fire"),
    ("fume", "steam"),
    ("spores", "smoke"),
)


def _home_set(key: str, own: tuple[str, ...], wall: str) -> MaterialSet:
    aliases = tuple((a, wall if b == "__wall__" else b) for a, b in _HOME_ALIASES)
    return MaterialSet(key, (*BASE_KEYS, *own), aliases=aliases)


BOESE_KAISERIN = _home_set("boese_kaiserin", ("goldboden",), "goldboden")
BOESE_GUTE = _home_set("boese_gute", ("lichtstein", "heiliges_licht"), "lichtstein")
BOESE_OMEGA = _home_set("boese_omega", ("foerderband", "stahl"), "stahl")

SETS: dict[str, MaterialSet] = {s.key: s for s in (KOERPER, FLEISCHWELT, AKTENHALDE, GLIBBRIA, KRUEMELREICH, SPORENKLUB, ABTEI, BOESE_KAISERIN, BOESE_GUTE, BOESE_OMEGA)}


def _init_set_reactions() -> None:
    from src.reactions import Reaction

    global GLIBBRIA, KRUEMELREICH, SPORENKLUB, ABTEI
    GLIBBRIA = MaterialSet(
        "glibbria",
        (
            *BASE_KEYS,
            "glibber",
            "glibber_rot",
            "brausesirup",
            "schaum",
            "kaugummi",
            "zuckerguss",
        ),
        # the organism generator's materials, re-dressed as jelly (cave walls, ribs, pools)
        aliases=(
            ("flesh", "glibber"),
            ("growth", "glibber"),
            ("sinew", "glibber_rot"),
            ("bone", "zuckerguss"),
            ("enamel", "zuckerguss"),
            ("spent", "zuckerguss"),
            ("crust", "kaugummi"),
            ("blood", "brausesirup"),
            ("pus", "brausesirup"),
            ("acid", "brausesirup"),
            ("mucus", "brausesirup"),
            ("spores", "schaum"),
            ("fume", "schaum"),
        ),
        reactions=(
            Reaction("fire", "glibber_rot", "fire", "smoke", 0.05),
            Reaction("fire", "brausesirup", "fire", "smoke", 0.05),
            Reaction("fire", "zuckerguss", "fire", "smoke", 0.05),
        ),
    )
    KRUEMELREICH = MaterialSet(
        "kruemelreich",
        (
            *BASE_KEYS,
            "kruemel",
            "brosel",
            "zucker",
            "karamell",
            "honig",
            "fliese",
            "staubfluse",
        ),
        aliases=(
            ("flesh", "kruemel"),
            ("growth", "kruemel"),
            ("sinew", "kruemel"),
            ("bone", "fliese"),
            ("enamel", "fliese"),
            ("spent", "fliese"),
            ("crust", "fliese"),
            ("bone_dust", "brosel"),
            ("blood", "honig"),
            ("pus", "karamell"),
            ("acid", "karamell"),
            ("mucus", "honig"),
        ),
        reactions=(
            Reaction("fire", "zucker", "fire", "karamell", 0.05),
        ),
    )
    SPORENKLUB = MaterialSet(
        "sporenklub",
        (
            *BASE_KEYS,
            "pilzfleisch",
            "pilzhut",
            "leuchtsporen",
            "neonsaft",
            "nebel",
        ),
        aliases=(
            ("flesh", "pilzfleisch"),
            ("growth", "pilzfleisch"),
            ("sinew", "pilzhut"),
            ("bone", "pilzhut"),
            ("enamel", "pilzhut"),
            ("spent", "pilzhut"),
            ("crust", "pilzhut"),
            ("bone_dust", "leuchtsporen"),
            ("blood", "neonsaft"),
            ("pus", "neonsaft"),
            ("acid", "neonsaft"),
            ("mucus", "neonsaft"),
            ("spores", "nebel"),
            ("fume", "nebel"),
        ),
    )
    ABTEI = MaterialSet(
        "abtei",
        (
            *BASE_KEYS,
            "mauerwerk",
            "buntglas",
            "kerzenwachs",
            "glockenbronze",
            "algen",
            "weihrauch",
        ),
        aliases=(
            ("flesh", "mauerwerk"),
            ("bone", "mauerwerk"),
            ("spent", "mauerwerk"),
            ("crust", "mauerwerk"),
            ("enamel", "glockenbronze"),
            ("growth", "algen"),
            ("sinew", "algen"),
            ("blood", "water"),
            ("pus", "water"),
            ("acid", "water"),
            ("mucus", "water"),
            ("tallow", "kerzenwachs"),
            ("spores", "weihrauch"),
            ("fume", "weihrauch"),
        ),
        reactions=(
            Reaction("fire", "kerzenwachs", "fire", "smoke", 0.05),
            # no "algae grow into water": that overgrew every flooded passage within minutes
        ),
    )
    SETS["glibbria"] = GLIBBRIA
    SETS["kruemelreich"] = KRUEMELREICH
    SETS["sporenklub"] = SPORENKLUB
    SETS["abtei"] = ABTEI
    for exp_key, exp_locals, extra_aliases in (
        ("schrott", ("altmetall", "roststaub", "fluessigeisen", "magnetit"), (("magma", "fluessigeisen"),)),
        ("kuchen", ("biskuit", "zuckerglasur", "karamell_kuchen", "puderzucker"), (("bone", "zuckerglasur"),)),
        ("spule", ("kupferdraht", "isolator", "plasma", "elektrolyt"), (("spark", "plasma"),)),
        ("uhrwerkwueste", ("chrono_sand", "messing_zahnrad", "fluessig_zeit", "unruh_fett"), (("oil", "unruh_fett"),)),
        ("suppenmeer", ("bouillon", "suppenfett", "nudel_teig", "pfefferdampf"), (("water", "bouillon"),)),
        ("freizeitpark", ("rost_schiene", "zuckerwatte_rot", "helium_gas", "spiegel_glas"), (("enamel", "spiegel_glas"),)),
        ("anatomie_park", ("lebergewebe", "magensaeure", "knochen_bruecke", "adrenalin_dampf"), (("acid", "magensaeure"), ("bone", "knochen_bruecke"))),
        ("pastell_hoelle", ("pluesch_wand", "erdbeernektar", "glitzer_sand", "einhorn_gas"), (("flesh", "pluesch_wand"),)),
        ("klonenberg_welt", ("klon_fleisch", "bartstoppel_sand", "rasier_schaum", "spiegel_lauge"), (("flesh", "klon_fleisch"),)),
        ("talent_kosmos", ("buehnen_stein", "nebelmaschinen_dunst", "applaus_gold", "scheinwerfer_plasma"), (("spark", "scheinwerfer_plasma"),)),
        ("antrags_labyrinth", ("formular_beton", "tacker_schrott", "kaffee_alt", "stempel_dunst"), (("acid", "kaffee_alt"),)),
        ("krawatten_planet", ("akten_marmor", "espresso_schlamm", "krawatten_stoff", "meeting_nebel"), (("mud", "espresso_schlamm"),)),
        ("klo_paradies", ("porzellan_glanz", "heilquell_wasser", "seifenschaum", "bimsstein_mehl"), (("water", "heilquell_wasser"),)),
        ("matroschka_simulation", ("voxel_wand", "cache_fluessigkeit", "pixel_sand", "ram_dunst"), (("rock", "voxel_wand"),)),
        ("kollektiv_buerokratie", ("waben_stahl", "tinten_nectar", "lochkarten_staub", "synchro_gas"), (("blood", "tinten_nectar"),)),
        ("unsterblichkeits_resort", ("marmor_pool", "cocktail_elixir", "sonnencreme_sand", "sauna_dampf"), (("water", "cocktail_elixir"),)),
        ("schroedinger_kammer", ("karton_wand", "quanten_supp", "wellen_staub", "ungewissheits_nebel"), (("acid", "quanten_supp"),)),
        ("kater_bunker", ("bunker_blei", "konter_brause", "kopfschmerz_asche", "abgestandene_luft"), (("rock", "bunker_blei"),)),
    ):
        SETS[exp_key] = MaterialSet(
            exp_key,
            (*BASE_KEYS, *exp_locals),
            aliases=(
                ("flesh", "dirt"),
                ("growth", "dirt"),
                ("sinew", "rock"),
                ("bone", "rock"),
                ("enamel", "rock"),
                ("spent", "rock"),
                ("crust", "dirt"),
                ("bone_dust", "sand"),
                ("blood", "water"),
                ("pus", "water"),
                ("acid", "water"),
                ("mucus", "oil"),
                ("tallow", "oil"),
                ("magma", "fire"),
                ("spark", "fire"),
                ("spores", "smoke"),
                ("fume", "steam"),
                *extra_aliases,
            ),
        )


_init_set_reactions()
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
