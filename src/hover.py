"""What lies under the cursor: names and short explanations, like Noita's hover text.

Pure logic (no pygame): the game asks ``describe`` for the world position under the
cursor and draws the returned ``HoverInfo`` as a tooltip. The same text builders are
used by the inventory screen for blocks and wands.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.enemies import Creature
from src.flask import CAPACITY as FLASK_CAPACITY
from src.flask import DRINK_EFFECTS
from src.loot import Pickup
from src.materials import (
    AIR,
    FLAME,
    FLAMMABILITY,
    GAS,
    HARDNESS,
    HARDNESS_DE,
    HAZARD_DPS,
    KIND,
    LIBRARY,
    LIQUID,
    MATERIALS,
    POWDER,
    SOLID,
)
from src.perks import PERK_BY_KEY
from src.spells import CATALOG, Block, Category
from src.wand import WandSpec

PICKUP_HOVER = 7.0  # px around an item that count as "on" it
CREATURE_HOVER = 2  # px of slack around a creature's box
Color = tuple[int, int, int]

KIND_DE = {SOLID: "Fest", POWDER: "Pulver", LIQUID: "Flüssigkeit", GAS: "Gas", FLAME: "Glut"}
CATEGORY_DE = {
    Category.FORM: "Drüse (Geschoss)",
    Category.MODIFIER: "Mutation (verändert die nächste Drüse)",
    Category.TRIGGER: "Nerv (löst die nächste Gruppe aus)",
    Category.PAYLOAD: "Sekret (Füllung der Drüse)",
}
CREATURE_INFO_DE: dict[str, str] = {
    "made": "Kriecht heran, springt und beißt.",
    "schwaermer": "Fliegt umher und spuckt Säurebatzen.",
    "knochenspeier": "Hängt an der Decke und schießt Knochennadeln.",
    "sporenblase": "Schwebt heran und platzt bei Berührung zu Sporen.",
    "magenwurm": "Wächter des Magens. Spuckt Säure in Salven.",
    "brutmutter": "Wächterin des Gedärms. Gebiert Sporenblasen und Schwärmer.",
    "herz": "Das Herz des Organismus. Zerstöre es!",
    "brandmade": "Eine brennende Made. Feuerfest, setzt alles in Brand.",
    "saeurespucker": "Spuckt Säure im Bogen und lässt Galle regnen.",
    "egel": "Saugt sich an dir fest. Fliegt.",
    "augenblase": "Starrt dich an und schießt Knochenspeere.",
    "schleimkriecher": "Langsam und zäh. Beißt sehr fest.",
    "nervenknoten": "Hängt an der Decke und jagt Strom durch die Sehnen.",
    "talgsack": "Ein Sack voll Talg. Platzt in einer Feuerexplosion.",
    "saeuresack": "Ein Sack voll Säure. Platzt bei Treffern.",
    "sporensack": "Ein Sack voller Sporen. Platzt bei Treffern.",
    "knochenfresser": "Wächter des Knochenmarks. Frisst sich durch alles Gewebe.",
    "atem": "Wächter der Lunge. Saugt dich an und atmet Sporen aus.",
    "gestaltwandler": "Verwandelt, was er trifft, in etwas anderes.",
}


@dataclass
class HoverInfo:
    """Tooltip content for whatever is under the cursor."""

    title: str
    lines: list[str] = field(default_factory=list)
    color: Color = (214, 200, 182)
    kind: str = "material"  # "material", "creature", "pickup"
    block: str | None = None  # draw this block's icon
    wand: WandSpec | None = None  # draw stat bars for this wand ...
    compare: WandSpec | None = None  # ... compared with this one (the wand in hand)
    hp: tuple[float, float] | None = None  # (current, maximum) for creatures


# ----------------------------------------------------------------- materials


def material_lines(material: int) -> list[str]:
    spec = MATERIALS[material]
    tags = [KIND_DE.get(KIND[material], "")]
    hardness = HARDNESS[material]
    if hardness:
        tags.append(HARDNESS_DE[hardness])
    if FLAMMABILITY[material] >= 0.02:
        tags.append("brennbar")
    if HAZARD_DPS[material]:
        tags.append(f"{HAZARD_DPS[material]:g} Schaden/s")
    lines = [", ".join(t for t in tags if t)]
    if spec.description_de:
        lines.append(spec.description_de)
    return lines


def describe_material(material: int) -> HoverInfo | None:
    if material == AIR:
        return None
    spec = MATERIALS[material]
    danger = HAZARD_DPS[material] > 0
    color = (236, 120, 100) if danger else spec.color
    return HoverInfo(spec.name_de, material_lines(material), _readable(color))


# ----------------------------------------------------------------- creatures


def describe_creature(creature: Creature) -> HoverInfo:
    spec = creature.spec
    lines = []
    info = CREATURE_INFO_DE.get(spec.key)
    if info:
        lines.append(info)
    traits = []
    if spec.boss:
        traits.append("Wächter")
    if spec.flying:
        traits.append("fliegt")
    if spec.fire_immune:
        traits.append("feuerfest")
    if spec.acid_immune:
        traits.append("säurefest")
    if spec.blast:
        traits.append("explodiert")
    if traits:
        lines.append(", ".join(traits).capitalize())
    if not spec.prop:
        lines.append(f"Beute: {spec.pearls} Blutperlen")
    color = (236, 90, 90) if not spec.prop else (214, 190, 140)
    return HoverInfo(
        spec.name_de, lines, color, "creature", hp=(max(0.0, creature.hp), creature.max_hp)
    )


# -------------------------------------------------------------------- blocks


def block_lines(block: Block) -> list[str]:
    """Category, cost and the numbers that matter for one building block."""
    lines = [CATEGORY_DE[block.category]]
    cost = f"Mana: {block.mana:g}"
    if block.cast_delay:
        cost += f"   Verzögerung: {block.cast_delay:+.2f} s"
    if block.recharge_bonus:
        cost += f"   Nachladen: {block.recharge_bonus:+.2f} s"
    lines.append(cost)
    if block.uses:
        lines.append(f"Ladungen: {block.uses} (im Sanktum aufgefüllt)")
    stats = []
    if block.damage:
        stats.append(f"Schaden {block.damage:g}")
    if block.blast:
        stats.append(f"Explosion {block.blast}")
    if block.pellets > 1:
        stats.append(f"{block.pellets} Geschosse")
    if block.speed:
        stats.append(f"Tempo {block.speed:g}")
    if block.digs:
        stats.append(f"gräbt {block.digs}")
    if block.multicast:
        stats.append(f"{block.multicast} Gruppen")
    if block.damage_bonus:
        stats.append(f"Schaden {block.damage_bonus:+g}")
    if block.blast_bonus:
        stats.append(f"Explosion {block.blast_bonus:+d}")
    if stats:
        lines.append(", ".join(stats))
    material = block.material if block.material is not None else block.default_material
    if block.trail is not None:
        lines.append(f"Spur: {LIBRARY[block.trail].name_de}")
    elif material is not None:
        lines.append(f"Material: {LIBRARY[material].name_de}")
    if block.description_de:
        lines.append(block.description_de)
    return lines


# --------------------------------------------------------------------- wands

# (label, getter, scale maximum, higher is better, format)
WAND_STATS: tuple[tuple[str, object, float, bool, str], ...] = (
    ("Mana", lambda s: s.mana_max, 600.0, True, "{:.0f}"),
    ("Mana/s", lambda s: s.mana_regen, 200.0, True, "{:.0f}"),
    ("Verzögerung", lambda s: s.cast_delay, 0.6, False, "{:.2f} s"),
    ("Nachladen", lambda s: s.recharge, 1.5, False, "{:.2f} s"),
    ("Plätze", lambda s: s.capacity or len(s.blocks), 12.0, True, "{:.0f}"),
    ("Zauber/Wurf", lambda s: s.casts, 3.0, True, "{:.0f}"),
    ("Streuung", lambda s: math.degrees(s.spread), 8.0, False, "{:.1f}°"),
)


def wand_values(spec: WandSpec) -> list[tuple[str, float, float, bool, str]]:
    """(label, value, bar fill 0..1, higher is better, text) for every wand stat."""
    rows = []
    for label, getter, top, higher, fmt in WAND_STATS:
        value = float(getter(spec))  # type: ignore[operator]
        fill = min(1.0, max(0.0, value / top))
        rows.append((label, value, fill, higher, fmt.format(value)))
    return rows


def compare(value: float, other: float, higher: bool) -> int:
    """+1 if ``value`` is better than ``other``, -1 if worse, 0 if equal."""
    if abs(value - other) < 1e-6:
        return 0
    return 1 if (value > other) == higher else -1


# -------------------------------------------------------------------- pickups


def describe_pickup(
    item: Pickup, current: WandSpec | None, price: int, known: set[str] | None = None
) -> HoverInfo:
    """Tooltip for an item; ``price`` is what it costs the player right now."""
    lines: list[str] = []
    title, color, block, wand = item.label_de, (232, 214, 180), None, None
    if item.perk is not None:
        perk = PERK_BY_KEY[item.perk]
        title, color = f"Perk: {perk.name_de}", perk.color
        lines = [perk.description_de, "E: Wählen (die anderen verschwinden)"]
    elif item.block is not None:
        spec = CATALOG[item.block]
        title, block = spec.name_de, spec.key
        lines = block_lines(spec)
        if known is not None and spec.key not in known:
            title, color = f"Neu: {spec.name_de}", (255, 226, 130)
            lines.insert(0, "Noch nicht im Kodex.")
    elif item.wand is not None:
        title, wand = f"Augmentation: {item.wand.name_de}", item.wand
        lines = ["Mischt die Bausteine" if item.wand.shuffle else "Feste Reihenfolge"]
        names = [CATALOG[key].name_de for key in item.wand.blocks]
        if names:
            lines.append("Enthält: " + ", ".join(names))
        new = [CATALOG[k].name_de for k in item.wand.blocks if known is not None and k not in known]
        if new:
            lines.append("Neu darin: " + ", ".join(dict.fromkeys(new)))
    elif item.flask is not None:
        flask = item.flask
        if flask.empty:
            lines = ["Leer. Halte sie an eine Flüssigkeit, um sie zu füllen."]
        else:
            share = round(100 * flask.amount / FLASK_CAPACITY)
            lines = [f"{flask.name_de}: {share} %"]
            effect = DRINK_EFFECTS.get(flask.key)
            if effect:
                lines.append(f"Trinken: {effect[2]}")
    elif item.heart:
        lines = ["Ein pochender Klumpen Herzmuskel.", f"Erhöht dein maximales Leben um {item.heart}."]
    elif item.cocoon:
        lines = ["Ein zuckender Kokon. Öffne ihn mit E – drinnen liegt Beute."]
    elif item.eye:
        lines = ["Ein Auge des Ursprungs. +10 maximales Leben.", "Sammle alle für das wahre Ende."]
    elif item.reroll:
        lines = ["Würfelt die Perks auf dem Altar neu.", "Der Preis verdoppelt sich jedes Mal."]
    elif item.portal:
        lines = ["Führt in die nächste Parallelwelt.", "Härtere Gegner, reichere Beute."]
    if price:
        lines.append(f"Preis: {price} Blutperlen (E: Kaufen)")
    elif item.perk is None and not item.pearls:
        lines.append("E: Aufheben")
    return HoverInfo(title, lines, color, "pickup", block=block, wand=wand, compare=current if wand else None)


# --------------------------------------------------------------------- query


def describe(
    run,
    x: float,
    y: float,
    visible: set[int] | None,
) -> HoverInfo | None:
    """Tooltip for the world position (x, y): creature, then item, then material.

    ``visible`` holds the ids of creatures in sight (None = all); hidden items
    (``seen`` False) are not described, so the cursor cannot give secrets away.
    """
    for creature in run.enemies.creatures:
        if creature.dead or (visible is not None and id(creature) not in visible):
            continue
        if (
            creature.x - CREATURE_HOVER <= x < creature.x + creature.width + CREATURE_HOVER
            and creature.y - CREATURE_HOVER <= y < creature.y + creature.height + CREATURE_HOVER
        ):
            return describe_creature(creature)
    best, best_distance = None, PICKUP_HOVER
    for item in run.pickups:
        if not item.seen or item.pearls:
            continue
        distance = math.hypot(item.x - x, item.y - 3 - y)
        if distance <= best_distance:
            best, best_distance = item, distance
    if best is not None:
        current = run.inventory.wand.spec if run.inventory.wands else None
        if current is not None:
            from src.inventory import spec_of

            current = spec_of(run.inventory.wand)
        return describe_pickup(best, current, run.price_of(best), getattr(run, "known_blocks", None))
    world = run.world
    if not (0 <= x < world.width and 0 <= y < world.height):
        return None
    return describe_material(world.get(int(x), int(y)))


def _readable(color: Color) -> Color:
    """Lift dark colours so the title stays legible on the dark tooltip."""
    if sum(color) >= 330:
        return color
    return (min(255, color[0] + 90), min(255, color[1] + 80), min(255, color[2] + 80))
