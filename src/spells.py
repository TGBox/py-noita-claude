"""Wand building blocks ("augmentations") as plain data.

A wand is a deck of blocks that is drawn in order when casting:

* Drüse (form): a projectile. Ends the current draw.
* Mutation (modifier): changes the next drawn projectile (speed, blast, ...).
  ``multicast`` blocks draw several projectiles at once.
* Nerv (trigger): the next drawn group becomes the projectile's payload and is
  released on an event (impact, timer, end of flight, touching liquid).
* Sekret (payload): what the projectile leaves behind - a splash of a material.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.materials import ACID, BLOOD, FIRE, SPORES, TALLOW


class Category(Enum):
    FORM = "Drüse"
    MODIFIER = "Mutation"
    TRIGGER = "Nerv"
    PAYLOAD = "Sekret"


class Trigger(Enum):
    IMPACT = "Aufprall"
    TIMER = "Zeit"
    END = "Ende"
    WET = "Nässe"


TIMER_DELAY = 0.4  # seconds until a timer nerve releases its payload


@dataclass(frozen=True)
class Block:
    """One building block. Only the fields of its category are relevant."""

    key: str
    name_de: str
    category: Category
    mana: float
    cast_delay: float = 0.0  # seconds added to the wand's cast delay
    description_de: str = ""
    # Drüse (form)
    speed: float = 0.0  # px/s
    gravity: float = 0.0  # px/s^2
    lifetime: float = 0.0  # seconds
    blast: int = 0  # explosion radius at the end of flight
    splash: int = 0  # radius of the material splash at the end of flight
    bounces: int = 0  # how often it bounces instead of ending on impact
    default_material: int | None = None
    # Mutation (modifier)
    speed_factor: float = 1.0
    blast_bonus: int = 0
    flip_gravity: bool = False
    homing: bool = False
    multicast: int = 0
    # Nerv (trigger)
    trigger: Trigger | None = None
    # Sekret (payload)
    material: int | None = None


BLOCKS: tuple[Block, ...] = (
    # Drüsen (forms)
    Block(
        "funke", "Funke", Category.FORM, mana=5, cast_delay=0.05,
        description_de="Schneller Funke, kleine Explosion.",
        speed=520, lifetime=1.0, blast=5, splash=4,
    ),
    Block(
        "nadel", "Knochennadel", Category.FORM, mana=3,
        description_de="Sehr schnell, gräbt sich nur wenig ein.",
        speed=820, lifetime=0.6, blast=2, splash=3,
    ),
    Block(
        "gallenblase", "Gallenblase", Category.FORM, mana=25, cast_delay=0.35,
        description_de="Prallt ab und platzt nach kurzer Zeit mit großer Wucht.",
        speed=300, gravity=700, lifetime=1.6, blast=16, splash=10, bounces=4,
    ),
    Block(
        "klumpen", "Klumpen", Category.FORM, mana=6, cast_delay=0.1,
        description_de="Fliegt im Bogen und zerplatzt zu einer Lache.",
        speed=340, gravity=600, lifetime=2.0, splash=6, default_material=BLOOD,
    ),
    # Mutationen (modifiers)
    Block(
        "beschleunigung", "Beschleunigung", Category.MODIFIER, mana=3,
        description_de="Nächste Drüse fliegt schneller.", speed_factor=1.75,
    ),
    Block(
        "sprengkraft", "Sprengkraft", Category.MODIFIER, mana=12, cast_delay=0.1,
        description_de="Größere Explosion.", blast_bonus=6,
    ),
    Block(
        "umkehr", "Schwerkraftumkehr", Category.MODIFIER, mana=4,
        description_de="Nächste Drüse fällt nach oben.", flip_gravity=True,
    ),
    Block(
        "zielsuche", "Zielsuche", Category.MODIFIER, mana=8,
        description_de="Nächste Drüse lenkt zum Mauszeiger.", homing=True,
    ),
    Block(
        "doppel", "Doppelzauber", Category.MODIFIER, mana=2,
        description_de="Zieht zwei Gruppen auf einmal.", multicast=2,
    ),
    # Nerven (triggers)
    Block(
        "nerv_aufprall", "Aufprall-Nerv", Category.TRIGGER, mana=6,
        description_de="Setzt die nächste Gruppe beim Aufprall frei.", trigger=Trigger.IMPACT,
    ),
    Block(
        "nerv_zeit", "Zeit-Nerv", Category.TRIGGER, mana=6,
        description_de="Setzt die nächste Gruppe nach kurzer Zeit frei.", trigger=Trigger.TIMER,
    ),
    Block(
        "nerv_ende", "End-Nerv", Category.TRIGGER, mana=6,
        description_de="Setzt die nächste Gruppe am Ende des Flugs frei.", trigger=Trigger.END,
    ),
    Block(
        "nerv_naesse", "Nässe-Nerv", Category.TRIGGER, mana=4,
        description_de="Setzt die nächste Gruppe frei, wenn die Drüse Flüssigkeit trifft.",
        trigger=Trigger.WET,
    ),
    # Sekrete (payloads)
    Block("sekret_blut", "Blutsekret", Category.PAYLOAD, mana=6, material=BLOOD),
    Block("sekret_talg", "Talgsekret", Category.PAYLOAD, mana=8, material=TALLOW),
    Block("sekret_saeure", "Säuresekret", Category.PAYLOAD, mana=14, material=ACID),
    Block("sekret_feuer", "Feuersekret", Category.PAYLOAD, mana=10, material=FIRE),
    Block("sekret_sporen", "Sporensekret", Category.PAYLOAD, mana=10, material=SPORES),
)  # fmt: skip

CATALOG: dict[str, Block] = {block.key: block for block in BLOCKS}
assert len(CATALOG) == len(BLOCKS), "duplicate block keys"
