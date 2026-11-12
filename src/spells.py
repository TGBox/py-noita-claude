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

from dataclasses import dataclass, replace
from enum import Enum


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
    uses: int = 0  # >0: charges per visit to a sanctum (0 = unlimited)
    rarity: float = 1.0  # weight when loot and shops pick blocks
    rarity_tier: int = 1  # tier 1..3 for fabricator and trader pricing (Contract V0b)
    timer: float = 0.0  # Zeit-Nerv: seconds until release (0 = the usual TIMER_DELAY)
    description_de: str = ""
    # Drüse (form)
    damage: float = 0.0  # direct hit damage to creatures
    speed: float = 0.0  # px/s
    gravity: float = 0.0  # px/s^2
    lifetime: float = 0.0  # seconds
    blast: int = 0  # explosion radius at the end of flight
    splash: int = 0  # radius of the material splash at the end of flight
    bounces: int = 0  # how often it bounces instead of ending on impact (fused forms)
    default_material: str | None = None  # material key
    pellets: int = 0  # >1: the form is cast as this many scattered pellets
    digs: int = 0  # >0: bores through solids with this radius instead of stopping
    lifesteal: float = 0.0  # share of direct damage that heals the caster
    ricochet: int = 0  # wall bounces before it ends (not a fuse like ``bounces``)
    teleport: bool = False  # the caster is pulled to where it ends
    mine: bool = False  # rests until a creature comes close, then goes off
    shock: int = 0  # >0: where it ends, sinew within this radius carries a nerve current
    polymorph: bool = False  # a hit creature turns into another one
    swap: bool = False  # you swap places with the creature it hits
    chain: int = 0  # >0: on a hit it jumps on to this many further creatures
    light: float = 0.0  # light radius in px (0 = the usual small glow)
    # Mutation (modifier)
    speed_factor: float = 1.0
    blast_bonus: int = 0
    flip_gravity: bool = False
    homing: bool = False
    multicast: int = 0
    formation: float = 0.0  # radians between multicast shots (0 = the usual narrow spread)
    pierce: bool = False  # passes through creatures
    bounce_bonus: int = 0  # extra bounces off walls
    ignites: bool = False  # sets hit creatures on fire
    lifetime_factor: float = 1.0
    gravity_factor: float = 1.0
    damage_bonus: float = 0.0
    trail: str | None = None  # material key left along the flight path
    spread_bonus: float = 0.0  # random aim deviation in radians
    recharge_bonus: float = 0.0  # seconds added to the wand's recharge (negative = faster)
    # Nerv (trigger)
    trigger: Trigger | None = None
    # Sekret (payload)
    material: str | None = None  # material key
    from_flask: bool = False
    local_material: bool = False
    retired: bool = False
    # Noita-style specials
    endless: bool = False  # Mutation: the next limited Drüse costs no charge
    divide: bool = False  # multicast that fires the next group ``multicast`` times
    absorb: bool = False  # Mutation: swallows your flying shots and adds their damage
    convert: str = ""  # Drüse: turns all your flying shots into this form (fires nothing)


BLOCKS: tuple[Block, ...] = (
    # Drüsen (forms)
    Block(
        "funke", "Flux-Funke", Category.FORM, mana=5, cast_delay=0.05,
        description_de="Schneller Funke, kleine Explosion. Das Brot und Butter jeder Wissenschaftlerin.",
        damage=6, speed=520, lifetime=1.0, blast=5, splash=4,
    ),
    Block(
        "nadel", "Nadelschuss", Category.FORM, mana=3,
        description_de="Sehr schnell, kratzt kaum an Wänden.",
        damage=4, speed=820, lifetime=0.6, blast=2, splash=3,
    ),
    Block(
        "gallenblase", "Hüpfgranate", Category.FORM, mana=25, cast_delay=0.35,
        description_de="Prallt ab und platzt nach kurzer Zeit gewaltig.",
        speed=300, gravity=700, lifetime=1.6, blast=16, splash=10, bounces=4,
    ),
    Block(
        "klumpen", "Matschbatzen", Category.FORM, mana=6, cast_delay=0.1,
        description_de="Fliegt im Bogen und zerplatzt zu einer Pfütze (Wasser).",
        damage=3, speed=340, gravity=600, lifetime=2.0, splash=6, default_material="blood",
    ),
    Block(
        "knochensplitter", "Schrotladung", Category.FORM, mana=12, cast_delay=0.15,
        description_de="Fünf Kugeln auf kurze Distanz.",
        damage=3, speed=600, lifetime=0.35, splash=2, pellets=5,
    ),
    Block(
        "zahnbohrer", "Bohrkopf", Category.FORM, mana=18, cast_delay=0.2,
        description_de="Frisst sich ein Stück weit durch Weiches und Hartes.",
        damage=4, speed=300, lifetime=0.5, digs=4,
    ),
    Block(
        "blutegel", "Lebenssauger", Category.FORM, mana=15, cast_delay=0.1,
        description_de="Langsam; heilt dich um die Hälfte seines Schadens.",
        damage=8, speed=260, lifetime=1.6, splash=3, default_material="blood", lifesteal=0.5,
    ),
    Block(
        "teleportbolzen", "Sprungbolzen (L15)", Category.FORM, mana=40, uses=15, cast_delay=0.1,
        description_de="Wo er einschlägt, reißt er dich hin.",
        speed=420, gravity=120, lifetime=1.0, teleport=True,
    ),
    Block(
        "knochensaege", "Kreissäge", Category.FORM, mana=20, cast_delay=0.1,
        description_de="Prallt oft ab und schneidet durch alles Lebendige.",
        damage=9, speed=240, lifetime=3.0, ricochet=8, pierce=True,
    ),
    Block(
        "sporenmine", "Haftmine", Category.FORM, mana=25, cast_delay=0.2,
        description_de="Bleibt liegen und platzt, wenn etwas naht.",
        damage=0, speed=180, gravity=500, lifetime=12.0, blast=10, bounces=1,
        splash=5, default_material="spores", mine=True,
    ),
    Block(
        "fressgeschwuer", "Tunnelfresser (L6)", Category.FORM, mana=60, uses=6, cast_delay=0.4,
        description_de="Träge Kugel, frisst einen breiten Gang.",
        damage=5, speed=110, lifetime=2.2, digs=9,
    ),
    Block(
        "knochenspeer", "Durchschlagbolzen", Category.FORM, mana=22, cast_delay=0.25,
        description_de="Spießt alles in seiner Bahn auf.",
        damage=26, speed=520, gravity=180, lifetime=1.2, pierce=True,
    ),
    Block(
        "gallenregen", "Gallenregen", Category.FORM, mana=18, cast_delay=0.15,
        description_de="Sechs Gallentropfen im hohen Bogen.",
        damage=2, speed=260, gravity=420, lifetime=2.0, splash=2, pellets=6,
        default_material="acid",
    ),
    Block(
        "eiterblase", "Talgblase", Category.FORM, mana=14, cast_delay=0.2,
        description_de="Eine schwerfällige Blase, die zu einer großen Lache zerplatzt.",
        damage=4, speed=200, gravity=300, lifetime=2.5, splash=9, default_material="tallow",
    ),
    Block(
        "mikrofunke", "Mikrofunke", Category.FORM, mana=1, cast_delay=-0.03,
        description_de="Winzig, billig, schnell.",
        damage=2, speed=800, lifetime=0.4,
    ),
    Block(
        "feuerball", "Feuerball", Category.FORM, mana=45, cast_delay=0.35,
        description_de="Glühender Klumpen, brennende Explosion.",
        damage=10, speed=230, gravity=60, lifetime=2.0, blast=12, splash=6, default_material="fire",
    ),
    Block(
        "knochenbombe", "Kraterbombe (L8)", Category.FORM, mana=55, uses=8, cast_delay=0.5,
        description_de="Prallt einmal ab, dann ein riesiger Krater.",
        speed=200, gravity=350, lifetime=2.2, blast=24, bounces=1,
    ),
    Block(
        "nadelregen", "Nadelregen", Category.FORM, mana=16, cast_delay=0.12,
        description_de="Acht Nadeln auf einmal.",
        damage=4, speed=640, gravity=40, lifetime=0.5, pellets=8,
    ),
    Block(
        "sporenball", "Sporenball", Category.FORM, mana=12, cast_delay=0.15,
        description_de="Eine weiche Kugel, die zu einer Sporenwolke zerplatzt.",
        damage=3, speed=180, gravity=-20, lifetime=2.0, splash=8, default_material="spores",
    ),
    Block(
        "schleimkugel", "Klebekugel", Category.FORM, mana=10, cast_delay=0.15,
        description_de="Macht Gegner klebrig, löscht Brände.",
        damage=4, speed=240, gravity=300, lifetime=2.0, splash=6, default_material="mucus",
    ),
    Block(
        "grabklaue", "Grabklaue", Category.FORM, mana=8, cast_delay=0.05,
        description_de="Kratzt einen schmalen, langen Gang ins Gewebe.",
        damage=2, speed=360, lifetime=0.35, digs=3,
    ),
    Block(
        "nervenstrom", "Stromstoß", Category.FORM, mana=20, cast_delay=0.1,
        description_de="Ein Blitz; in Wasser und Metall läuft er weiter.",
        damage=8, speed=700, lifetime=0.5, shock=6,
    ),
    Block(
        "wandlungsdruese", "Wandelstrahl (L5)", Category.FORM, mana=60, uses=5, cast_delay=0.3,
        description_de="Wen er trifft, der wird zu etwas anderem.",
        speed=380, lifetime=1.0, polymorph=True,
    ),
    Block(
        "tauschdruese", "Tauschstrahl (L15)", Category.FORM, mana=25, uses=15, cast_delay=0.1,
        description_de="Du tauschst den Platz mit dem Getroffenen.",
        damage=2, speed=560, lifetime=0.8, swap=True,
    ),
    Block(
        "kettenfunke", "Kettenblitz", Category.FORM, mana=22, cast_delay=0.1,
        description_de="Springt auf bis zu drei weitere Kreaturen.",
        damage=9, speed=650, lifetime=0.6, chain=3,
    ),
    Block(
        "leuchtkugel", "Leuchtfackel", Category.FORM, mana=10, cast_delay=0.2,
        description_de="Schwebt lange und erhellt die Dunkelheit.",
        speed=90, gravity=-8, lifetime=14.0, light=120.0, bounces=6,
    ),
    Block(
        "saeurepfeil", "Säurepfeil", Category.FORM, mana=9, cast_delay=0.08,
        description_de="Schnell und ätzend.",
        damage=6, speed=520, gravity=60, lifetime=0.9, splash=2, default_material="acid",
    ),
    Block(
        "blutstrahl", "Blutstrahl", Category.FORM, mana=3, cast_delay=-0.02,
        description_de="Ein dünner Strahl Blut: löscht Brände, schadet kaum.",
        damage=1, speed=420, gravity=300, lifetime=0.8, splash=1, default_material="blood",
    ),
    Block(
        "talgbombe", "Talgbombe", Category.FORM, mana=30, cast_delay=0.3,
        description_de="Prallt ab und platzt dann zu einer brennenden Fettlache.",
        speed=220, gravity=380, lifetime=1.8, blast=8, bounces=2, splash=10,
        default_material="tallow",
    ),
    Block(
        "dornenhagel", "Dornenhagel", Category.FORM, mana=26, cast_delay=0.25,
        description_de="Zwölf Knochendornen in alle Richtungen nach vorne.",
        damage=4, speed=520, gravity=200, lifetime=0.6, pellets=12,
    ),
    Block(
        "zahnrad", "Mahlwerk", Category.FORM, mana=35, cast_delay=0.2,
        description_de="Ein Zahnrad, das lange durch Wände mahlt.",
        damage=6, speed=160, lifetime=2.5, digs=5, pierce=True,
    ),
    Block(
        "gelenkkugel", "Flummi", Category.FORM, mana=12, cast_delay=0.1,
        description_de="Prallt immer wieder ab.",
        damage=10, speed=380, gravity=200, lifetime=4.0, ricochet=12,
    ),
    Block(
        "giftblase", "Giftblase", Category.FORM, mana=14, cast_delay=0.15,
        description_de="Zerplatzt zu einer Lache vergiftenden Eiters.",
        damage=3, speed=200, gravity=250, lifetime=2.0, splash=7, default_material="pus",
    ),
    Block(
        "glutkugel", "Glutkugel", Category.FORM, mana=50, uses=10, cast_delay=0.4,
        description_de="Ein Tropfen Glutblut, der alles in Brand setzt, was er berührt.",
        damage=12, speed=240, gravity=300, lifetime=2.0, splash=5, default_material="magma",
    ),
    # Mutationen (modifiers)
    Block(
        "beschleunigung", "Turbo", Category.MODIFIER, mana=3,
        description_de="Nächstes Geschoss fliegt schneller.", speed_factor=1.75,
    ),
    Block(
        "sprengkraft", "Sprengladung", Category.MODIFIER, mana=12, cast_delay=0.1,
        description_de="Größere Explosion.", blast_bonus=6,
    ),
    Block(
        "umkehr", "Antigrav", Category.MODIFIER, mana=4,
        description_de="Nächstes Geschoss fällt nach oben.", flip_gravity=True,
    ),
    Block(
        "zielsuche", "Zielsuchkopf", Category.MODIFIER, mana=8,
        description_de="Lenkt zum Mauszeiger.", homing=True,
    ),
    Block(
        "doppel", "Doppellauf", Category.MODIFIER, mana=2,
        description_de="Zwei Gruppen auf einmal.", multicast=2,
    ),
    Block(
        "durchbohren", "Panzerbrechend", Category.MODIFIER, mana=10,
        description_de="Fliegt durch Kreaturen hindurch.", pierce=True,
    ),
    Block(
        "abprall", "Gummierung", Category.MODIFIER, mana=5,
        description_de="Prallt dreimal von Wänden ab.", bounce_bonus=3,
    ),
    Block(
        "brandbeschleuniger", "Brandsatz", Category.MODIFIER, mana=8,
        description_de="Getroffene fangen Feuer.", ignites=True,
    ),
    Block(
        "langlebigkeit", "Langstrecke", Category.MODIFIER, mana=4,
        description_de="Fliegt doppelt so lange, aber langsamer.",
        lifetime_factor=2.0, speed_factor=0.8,
    ),
    Block(
        "dreifach", "Dreifachlauf", Category.MODIFIER, mana=3, cast_delay=0.05,
        description_de="Drei Gruppen auf einmal.", multicast=3,
    ),
    Block(
        "vierfach", "Vierfachzauber", Category.MODIFIER, mana=5, cast_delay=0.1,
        description_de="Zieht vier Gruppen auf einmal.", multicast=4,
    ),
    Block(
        "achterkreis", "Rundumschlag (L15)", Category.MODIFIER, mana=12, uses=15, cast_delay=0.2,
        description_de="Acht Gruppen im Kreis um dich.",
        multicast=8, formation=6.283185 / 8,
    ),
    Block(
        "faecher", "Fächerdüse", Category.MODIFIER, mana=6, cast_delay=0.1,
        description_de="Fünf Gruppen, weit aufgefächert.", multicast=5, formation=0.3,
    ),
    Block(
        "vorne_hinten", "Rückspiegel", Category.MODIFIER, mana=4,
        description_de="Eine Gruppe nach vorn, eine nach hinten.",
        multicast=2, formation=3.141593,
    ),
    Block(
        "beschleunigung_stark", "Überturbo", Category.MODIFIER, mana=10,
        description_de="Zweieinhalbmal so schnell. Hält nicht lange.", speed_factor=2.5,
    ),
    Block(
        "sprengkern", "Taschen-Atomkern", Category.MODIFIER, mana=25, cast_delay=0.2,
        description_de="Viel größere Explosion. Nicht schütteln.", blast_bonus=12,
    ),
    Block(
        "kurzlebig", "Kurzstrecke", Category.MODIFIER, mana=1, cast_delay=-0.05,
        description_de="Vergeht nach halber Zeit, dafür schneller schießen.",
        lifetime_factor=0.5,
    ),
    Block(
        "giftzahn", "Wucht", Category.MODIFIER, mana=9,
        description_de="Trifft deutlich härter.",
        damage_bonus=10, ignites=True,
    ),
    Block(
        "blutpreis", "Fluxpumpe", Category.MODIFIER, mana=-60, cast_delay=0.25,
        description_de="Gibt 60 Flux, kostet eine längere Pause.",
    ),
    Block(
        "dauerladung", "Schnelllader", Category.MODIFIER, mana=20,
        description_de="Lädt nach diesem Durchgang fast sofort.",
        recharge_bonus=-0.8,
    ),
    Block(
        "schleimspur", "Schleimspur", Category.MODIFIER, mana=6,
        description_de="Nächste Drüse zieht eine zähe Schleimspur.", trail="mucus",
    ),
    Block(
        "sporenspur", "Sporenspur", Category.MODIFIER, mana=6,
        description_de="Nächste Drüse zieht eine Sporenwolke hinter sich her.", trail="spores",
    ),
    Block(
        "zielsuche_stark", "Bluthunger", Category.MODIFIER, mana=14,
        description_de="Nächste Drüse sucht den Mauszeiger und fliegt schneller.",
        homing=True, speed_factor=1.3,
    ),
    Block(
        "glutspur", "Glutspur", Category.MODIFIER, mana=18,
        description_de="Nächste Drüse tropft Glutblut.", trail="magma",
    ),
    Block(
        "eiterspur", "Eiterspur", Category.MODIFIER, mana=6,
        description_de="Nächste Drüse tropft vergiftenden Eiter.", trail="pus",
    ),
    Block(
        "sprengkraft_klein", "Zündfunke", Category.MODIFIER, mana=4,
        description_de="Kleine Explosion am Ende des Flugs.", blast_bonus=3,
    ),
    Block(
        "lange_flugbahn", "Gleitfähigkeit", Category.MODIFIER, mana=3,
        description_de="Nächste Drüse fällt nur halb so stark und fliegt länger.",
        gravity_factor=0.5, lifetime_factor=1.5,
    ),
    Block(
        "schwerkraft_stark", "Bleischwere", Category.MODIFIER, mana=2,
        description_de="Nächste Drüse fällt dreimal so stark.", gravity_factor=3.0,
    ),
    Block(
        "durchbohren_brand", "Glühende Spitze", Category.MODIFIER, mana=16,
        description_de="Nächste Drüse fliegt durch Kreaturen und setzt sie in Brand.",
        pierce=True, ignites=True,
    ),
    Block(
        "doppelt_abprall", "Gummisehne", Category.MODIFIER, mana=8,
        description_de="Nächste Drüse prallt sechsmal ab.", bounce_bonus=6,
    ),
    Block(
        "zehnfach", "Zehnfachzauber", Category.MODIFIER, mana=20, uses=10, cast_delay=0.3,
        description_de="Zieht zehn Gruppen und fächert sie breit.", multicast=10, formation=0.12,
    ),
    Block(
        "schwerelos", "Schwebefeld", Category.MODIFIER, mana=2,
        description_de="Nächstes Geschoss fällt gar nicht.", gravity_factor=0.0,
    ),
    Block(
        "schwere_ladung", "Bleimantel", Category.MODIFIER, mana=7, cast_delay=0.1,
        description_de="Mehr Schaden, aber langsamer.", damage_bonus=12, speed_factor=0.6,
    ),
    Block(
        "schadenszuwachs", "Schadenszuwachs", Category.MODIFIER, mana=5, cast_delay=0.05,
        description_de="Nächste Drüse trifft härter.", damage_bonus=6,
    ),
    Block(
        "blutspur", "Blutspur", Category.MODIFIER, mana=4,
        description_de="Nächste Drüse zieht eine Blutspur hinter sich her.", trail="blood",
    ),
    Block(
        "saeurespur", "Säurespur", Category.MODIFIER, mana=10,
        description_de="Nächste Drüse tropft Magensäure.", trail="acid",
    ),
    Block(
        "feuerspur", "Feuerspur", Category.MODIFIER, mana=8,
        description_de="Nächste Drüse zieht eine Flammenspur.", trail="fire",
    ),
    Block(
        "talgspur", "Talgspur", Category.MODIFIER, mana=4,
        description_de="Nächste Drüse tropft Talg.", trail="tallow",
    ),
    Block(
        "streuung", "Streuung", Category.MODIFIER, mana=1,
        description_de="Nächste Drüse fliegt ungenau.", spread_bonus=0.35,
    ),
    Block(
        "manazuschuss", "Mana-Zuschuss", Category.MODIFIER, mana=-30, cast_delay=0.1,
        description_de="Gibt beim Zaubern 30 Mana zurück.",
    ),
    Block(
        "hast", "Abzugsfeder", Category.MODIFIER, mana=4, cast_delay=-0.15,
        description_de="Kürzere Pause bis zum nächsten Schuss.",
    ),
    Block(
        "schnellladung", "Schnellladung", Category.MODIFIER, mana=8,
        description_de="Die Augmentation lädt nach diesem Durchgang schneller nach.",
        recharge_bonus=-0.3,
    ),
    # Nerven (triggers)
    Block(
        "nerv_aufprall", "Aufschlagzünder", Category.TRIGGER, mana=6,
        description_de="Setzt die nächste Gruppe beim Aufprall frei.", trigger=Trigger.IMPACT,
    ),
    Block(
        "nerv_zeit", "Zeitzünder", Category.TRIGGER, mana=6,
        description_de="Nach kurzer Zeit.", trigger=Trigger.TIMER,
    ),
    Block(
        "nerv_ende", "Endzünder", Category.TRIGGER, mana=6,
        description_de="Am Ende des Flugs.", trigger=Trigger.END,
    ),
    Block(
        "nerv_naesse", "Nässezünder", Category.TRIGGER, mana=4,
        description_de="Sobald das Geschoss in Flüssigkeit eintaucht.",
        trigger=Trigger.WET,
    ),
    # Sekrete (payloads)
    Block("sekret_blut", "Blutfüllung", Category.PAYLOAD, mana=6, material="blood", description_de="Macht alles rot und glitschig."),
    Block("sekret_talg", "Talgsekret", Category.PAYLOAD, mana=8, material="tallow", retired=True),
    Block("sekret_saeure", "Säurefüllung", Category.PAYLOAD, mana=14, material="acid", description_de="Frisst sich durch fast alles."),
    Block("sekret_feuer", "Feuerfüllung", Category.PAYLOAD, mana=10, material="fire"),
    Block("sekret_sporen", "Sporensekret", Category.PAYLOAD, mana=10, material="spores", retired=True),
    Block("sekret_schleim", "Schleimsekret", Category.PAYLOAD, mana=8, material="mucus", retired=True),
    Block("sekret_rauch", "Rauchfüllung", Category.PAYLOAD, mana=3, material="smoke"),
    Block(
        "sekret_glut", "Glutfüllung", Category.PAYLOAD, mana=30, uses=12, material="magma",
        description_de="Heiß, langsam, sehr endgültig.",
    ),
    Block(
        "sekret_eiter", "Eitersekret", Category.PAYLOAD, mana=8, material="pus", retired=True,
        description_de="Hinterlässt vergiftenden Eiter.",
    ),
    Block(
        "fuellung_wasser", "Wasserfüllung", Category.PAYLOAD, mana=5, material="water",
        description_de="Klares Wasser zum Löschen und Reinigen.",
    ),
    Block(
        "fuellung_oel", "Ölfüllung", Category.PAYLOAD, mana=8, material="oil",
        description_de="Brennbares Öl für Kettenreaktionen.",
    ),
    Block(
        "fuellung_dampf", "Dampffüllung", Category.PAYLOAD, mana=6, material="steam",
        description_de="Heißer Dampf, der aufsteigt und vernebelt.",
    ),
    Block(
        "fuellung_sand", "Sandfüllung", Category.PAYLOAD, mana=6, material="sand",
        description_de="Rieselnder Sand, der verschüttet.",
    ),
    Block(
        "fuellung_erde", "Erdfüllung", Category.PAYLOAD, mana=7, material="dirt",
        description_de="Fruchtbare Erde zum Aufschütten.",
    ),
    Block(
        "fuellung_fels", "Felsfüllung", Category.PAYLOAD, mana=12, material="rock",
        description_de="Schwere Felsbrocken als massive Barrikade.",
    ),
    Block(
        "fuellung_kolben", "Kolbenfüllung", Category.PAYLOAD, mana=8, material=None,
        from_flask=True,
        description_de="Verschießt das Material des aktuell gehaltenen Kolbens.",
    ),
    Block(
        "fuellung_lokal", "Lokalkolorit", Category.PAYLOAD, mana=10, material=None,
        local_material=True,
        description_de="Verschießt ein typisches Material des aktuellen Universums.",
    ),
    Block("sekret_aetzdampf", "Ätzdampfsekret", Category.PAYLOAD, mana=12, material="fume", retired=True),
    Block("sekret_staub", "Staubsekret", Category.PAYLOAD, mana=5, material="bone_dust", retired=True),
    Block(
        "sekret_sehnen", "Sehnensekret", Category.PAYLOAD, mana=12, material="sinew", retired=True,
        description_de="Baut einen Klumpen Sehnen - eine Plattform zum Draufstehen.",
    ),
    Block(
        "sekret_knochen", "Knochensekret", Category.PAYLOAD, mana=16, material="bone", retired=True,
        description_de="Baut einen Klumpen Knochen - eine Deckung gegen Geschosse.",
    ),
    Block(
        "sekret_wucherung", "Wucherungssekret", Category.PAYLOAD, mana=12, material="growth", retired=True,
        description_de="Pflanzt eine Wucherung, die sich durch Fleisch frisst.",
    ),
)  # fmt: skip

# Families: every basic shape in every element, tiers of each mutation, formations
# and timed nerves - Noita's way of filling the spell pool with variations to combine.
ELEMENTS = (
    ("blood", "Blut", "blut"), ("acid", "Säure", "saeure"), ("tallow", "Talg", "talg"),
    ("spores", "Sporen", "sporen"), ("mucus", "Schleim", "schleim"), ("pus", "Eiter", "eiter"),
    ("magma", "Glut", "glut"), ("bone_dust", "Staub", "staub"), ("fume", "Dampf", "dampf"),
    ("smoke", "Rauch", "rauch"), ("fire", "Feuer", "feuer"), ("growth", "Wucher", "wucher"),
    ("sinew", "Sehnen", "sehnen"), ("bone", "Knochen", "knochen"),
)  # fmt: skip
FAMILY_RARITY = 0.3

# (key suffix, German suffix, description, Block fields)
SHAPES = (
    ("tropfen", "tropfen", "Ein schneller Tropfen {n}.", {"damage": 3, "speed": 480, "gravity": 120, "lifetime": 0.8, "splash": 2, "mana": 4}),
    ("kugel", "kugel", "Eine Kugel, die im Bogen fliegt und zu {n} zerplatzt.", {"damage": 6, "speed": 260, "gravity": 300, "lifetime": 2.0, "splash": 6, "mana": 10}),
    ("bombe", "bombe", "Prallt ab und platzt nach kurzer Zeit zu viel {n}.", {"speed": 220, "gravity": 380, "lifetime": 1.6, "blast": 10, "bounces": 2, "splash": 9, "mana": 30, "cast_delay": 0.3}),
    ("regen", "regen", "Sechs Tropfen {n} im hohen Bogen.", {"damage": 2, "speed": 280, "gravity": 420, "lifetime": 1.8, "splash": 2, "pellets": 6, "mana": 14}),
    ("strahl", "strahl", "Fliegt schnurgerade und weit, dann {n}.", {"damage": 4, "speed": 420, "lifetime": 1.5, "splash": 3, "mana": 8}),
    ("bohrer", "bohrer", "Bohrt sich durch Gewebe und hinterlässt {n}.", {"damage": 3, "speed": 280, "lifetime": 0.6, "digs": 3, "splash": 3, "mana": 16}),
    ("sucher", "sucher", "Sucht den Mauszeiger und bringt {n}.", {"damage": 5, "speed": 300, "lifetime": 2.0, "splash": 3, "homing": True, "mana": 14}),
    ("splitter", "splitter", "Acht kurze Splitter, jeder mit etwas {n}.", {"damage": 2, "speed": 560, "gravity": 100, "lifetime": 0.35, "splash": 1, "pellets": 8, "mana": 16}),
    ("mine", "mine", "Bleibt liegen und platzt zu {n}, wenn etwas naht.", {"speed": 160, "gravity": 480, "lifetime": 10.0, "blast": 6, "bounces": 1, "splash": 7, "mine": True, "mana": 20}),
    ("saege", "säge", "Eine kreisende Klinge, die {n} verspritzt.", {"damage": 7, "speed": 220, "lifetime": 2.5, "ricochet": 6, "pierce": True, "splash": 2, "mana": 22}),
    ("welle", "welle", "Eine träge Welle, die viel {n} bringt.", {"damage": 2, "speed": 120, "lifetime": 3.0, "splash": 10, "mana": 18}),
    ("geschoss", "geschoss", "Schwer und schnell, mit einem Kern aus {n}.", {"damage": 14, "speed": 600, "gravity": 60, "lifetime": 0.9, "splash": 1, "mana": 12}),
    ("blase", "blase", "Steigt nach oben und platzt zu {n}.", {"damage": 3, "speed": 140, "gravity": -160, "lifetime": 2.5, "splash": 7, "mana": 10}),
    ("nadel", "nadel", "Eine durchschlagende Nadel, getränkt in {n}.", {"damage": 6, "speed": 700, "gravity": 30, "lifetime": 0.6, "pierce": True, "splash": 1, "mana": 9}),
    ("kette", "kette", "Springt von Kreatur zu Kreatur und hinterlässt {n}.", {"damage": 7, "speed": 600, "lifetime": 0.6, "chain": 2, "splash": 2, "mana": 20}),
    ("schauer", "schauer", "Zwölf winzige Tropfen {n}, weit gestreut.", {"damage": 1, "speed": 380, "gravity": 260, "lifetime": 1.2, "splash": 1, "pellets": 12, "mana": 18}),
    ("klinge", "klinge", "Eine kurze, scharfe Klinge aus {n} für den Nahkampf.", {"damage": 18, "speed": 500, "lifetime": 0.15, "pierce": True, "splash": 2, "mana": 10}),
    ("leuchte", "leuchte", "Leuchtet lange und tropft schließlich {n}.", {"speed": 90, "gravity": -6, "lifetime": 10.0, "light": 100.0, "bounces": 4, "splash": 4, "mana": 12}),
)  # fmt: skip


def _families() -> list[Block]:
    out: list[Block] = []
    for material, stem, key in ELEMENTS:
        name_case = stem
        taken = {b.key for b in BLOCKS} | {b.name_de for b in BLOCKS}
        for suffix, word, text, fields in SHAPES:
            fields = dict(fields)
            mana = fields.pop("mana")
            delay = fields.pop("cast_delay", 0.1)
            if f"{key}{suffix}" in taken or f"{stem}{word}" in taken:
                continue  # a hand-made block of that name exists already
            out.append(Block(
                f"{key}{suffix}", f"{stem}{word}", Category.FORM, mana=mana, cast_delay=delay,
                description_de=text.format(n=name_case), default_material=material,
                rarity=FAMILY_RARITY, **fields,
            ))  # fmt: skip
        out.append(Block(
            f"kern_{key}", f"{stem}kern", Category.MODIFIER, mana=4,
            description_de=f"Die nächste Drüse trägt {stem} in sich.", material=material,
            rarity=FAMILY_RARITY,
        ))  # fmt: skip
    for material, stem, key in ELEMENTS:
        if not any(b.trail == material for b in BLOCKS):
            out.append(Block(
                f"spur_{key}", f"{stem}spur", Category.MODIFIER, mana=6,
                description_de=f"Nächste Drüse zieht eine Spur aus {stem}.", trail=material,
                rarity=FAMILY_RARITY,
            ))  # fmt: skip
    roman = ("I", "II", "III", "IV")
    tiers = (
        ("tempo", "Tempo", "Fluggeschwindigkeit ×{v}", "speed_factor", (0.5, 1.25, 1.6, 2.0)),
        ("wucht", "Wucht", "+{v} Schaden", "damage_bonus", (3.0, 9.0, 15.0, 25.0)),
        ("sprengsatz", "Sprengsatz", "+{v} Explosionsradius", "blast_bonus", (2, 5, 8, 16)),
        ("dauer", "Dauer", "Flugzeit ×{v}", "lifetime_factor", (0.3, 0.75, 1.25, 3.0)),
        ("schwere", "Schwere", "Schwerkraft ×{v}", "gravity_factor", (0.0, 0.25, 2.0, 5.0)),
        ("federung", "Federung", "+{v} Abpraller", "bounce_bonus", (1, 2, 4, 10)),
        ("zittern", "Zittern", "±{v} rad Streuung", "spread_bonus", (0.1, 0.2, 0.6)),
        ("eile", "Eile", "{v} s Zauberpause", "cast_delay", (-0.05, -0.1, -0.25)),
        ("nachwuchs", "Nachwuchs", "{v} s Nachladen", "recharge_bonus", (-0.1, -0.2, -0.5)),
        ("blutopfer", "Blutopfer", "gibt {v} Mana zurück", "mana", (-10.0, -20.0, -45.0)),
    )
    for key, name, text, field, values in tiers:
        for i, value in enumerate(values):
            fields = {field: value}
            mana = 2 + 3 * i
            if field == "mana":
                mana, fields = value, {}
            out.append(Block(
                f"{key}_{i + 1}", f"{name} {roman[i]}", Category.MODIFIER, mana=mana,
                description_de=f"Nächste Drüse: {text.format(v=value)}.", rarity=FAMILY_RARITY,
                **fields,
            ))  # fmt: skip
    for count in (3, 4, 5, 6, 8, 10, 12):
        out.append(Block(
            f"ring_{count}", f"{count}er-Ring", Category.MODIFIER, mana=2 + count,
            cast_delay=0.05 * count / 2,
            description_de=f"Zieht {count} Gruppen und verschießt sie im Kreis.",
            multicast=count, formation=6.283185 / count, rarity=FAMILY_RARITY,
        ))  # fmt: skip
    for count, spread, name in ((2, 0.6, "Zange"), (7, 0.25, "Weiter Fächer"), (5, 0.06, "Bündel")):
        out.append(Block(
            f"formation_{name.lower().replace(' ', '_')}", name, Category.MODIFIER, mana=3 + count,
            description_de=f"Zieht {count} Gruppen in dieser Formation.", multicast=count,
            formation=spread, rarity=FAMILY_RARITY,
        ))  # fmt: skip
    for delay, name in ((0.15, "Zuckender"), (0.8, "Träger"), (1.5, "Schlafender")):
        out.append(Block(
            f"nerv_zeit_{int(delay * 100)}", f"{name} Zeit-Nerv", Category.TRIGGER, mana=6,
            description_de=f"Setzt die nächste Gruppe nach {delay:g} s frei.",
            trigger=Trigger.TIMER, timer=delay, rarity=FAMILY_RARITY,
        ))  # fmt: skip
    return out


BLOCKS = BLOCKS + tuple(_families())

# Cloita Classic leftovers: secretions of the old organism that the universes do not even
# have as materials. They stay castable (old saves, presets) but no longer turn up as loot,
# in shops or as blueprints. Blood, embers, fire and bone remain.
RETIRED_ELEMENTS = frozenset(
    {"acid", "tallow", "spores", "mucus", "pus", "bone_dust", "fume", "smoke", "growth", "sinew"}
)
RETIRED_KEYS = frozenset(
    {
        "eiterblase", "saeurepfeil", "talgbombe", "gallenregen", "sporenball", "schleimkugel",
        "giftblase", "schleimspur", "sporenspur", "eiterspur", "saeurespur", "talgspur",
    }
)  # fmt: skip


def _retire(block: Block) -> Block:
    family = block.rarity == FAMILY_RARITY and (
        {block.default_material, block.material, block.trail} & RETIRED_ELEMENTS
    )
    return replace(block, retired=True) if family or block.key in RETIRED_KEYS else block


BLOCKS = tuple(_retire(b) for b in BLOCKS)

_SAW = next(b for b in BLOCKS if b.key == "knochensaege")
NOITA_BLOCKS: tuple[Block, ...] = (
    # Drüsen after Noita's projectile spells
    Block(
        "flux_rakete", "Flux-Rakete", Category.FORM, mana=45, cast_delay=0.4,
        description_de="Träge Rakete mit kräftiger Explosion.",
        damage=30, speed=380, lifetime=2.0, blast=14, splash=4,
    ),
    Block(
        "grosse_flux_rakete", "Große Flux-Rakete (L10)", Category.FORM, mana=90, cast_delay=0.6,
        uses=10, description_de="Die große Schwester: reißt ganze Kammern auf.",
        damage=60, speed=300, lifetime=2.5, blast=22, splash=6,
    ),
    Block(
        "energiekugel", "Energiekugel", Category.FORM, mana=30, cast_delay=0.1,
        description_de="Langsame, schwere Kugel aus reinem Flux.",
        damage=22, speed=300, lifetime=2.5, blast=6, splash=3,
    ),
    Block(
        "leuchtbohrer", "Leuchtbohrer", Category.FORM, mana=10, cast_delay=-0.3,
        description_de="Kurzer Lichtstrahl, der sich durch fast alles frisst. Zaubert rasend "
        "schnell.",
        damage=12, speed=900, lifetime=0.09, digs=4, light=60.0,
    ),
    Block(
        "schwarzes_loch", "Schwarzes Loch (L3)", Category.FORM, mana=180, cast_delay=0.8, uses=3,
        description_de="Kriecht geradeaus und verschlingt alles Feste auf seinem Weg.",
        speed=110, lifetime=2.4, digs=11,
    ),
    Block(
        "todeskreuz", "Todeskreuz", Category.FORM, mana=80, cast_delay=0.5,
        description_de="Schwebt fast auf der Stelle und explodiert nach einem Atemzug.",
        speed=50, lifetime=1.1, blast=19, splash=3,
    ),
    Block(
        "blitzschlag", "Blitzschlag", Category.FORM, mana=70, cast_delay=0.6,
        description_de="Schlägt sofort ein und springt auf drei weitere Kreaturen über.",
        damage=40, speed=1400, lifetime=0.25, blast=8, chain=3, shock=20, light=90.0,
    ),
    Block(
        "dynamit", "Dynamitstange (L16)", Category.FORM, mana=50, cast_delay=0.5, uses=16,
        description_de="Fliegt im Bogen, rollt aus und sprengt ein großes Loch.",
        speed=320, gravity=600, lifetime=1.5, blast=20, bounces=2, splash=4,
    ),
    Block(
        "meteorit", "Meteorit (L6)", Category.FORM, mana=150, cast_delay=1.0, uses=6,
        description_de="Ein glühender Brocken, der mit Wucht einschlägt.",
        damage=40, speed=520, gravity=320, lifetime=3.0, blast=28, splash=8,
        default_material="magma",
    ),
    Block(
        "atombombe", "Atombombe (L1)", Category.FORM, mana=200, cast_delay=1.2, uses=1,
        description_de="Genau eine. Lauf.",
        damage=80, speed=260, gravity=140, lifetime=4.0, blast=56, splash=10,
    ),
    Block(
        "feuerbolzen", "Feuerbolzen (L25)", Category.FORM, mana=50, cast_delay=0.4, uses=25,
        description_de="Hüpft einmal auf und geht dann in Flammen auf.",
        damage=12, speed=360, gravity=500, lifetime=2.0, blast=12, bounces=1, splash=6,
        default_material="fire",
    ),
    Block(
        "prallkugel", "Prallkugel", Category.FORM, mana=5, cast_delay=-0.03,
        description_de="Billig, flink und springt an jeder Wand weiter.",
        damage=5, speed=480, gravity=300, lifetime=4.0, ricochet=6, splash=1,
    ),
    replace(
        _SAW, key="riesensaege", name_de="Riesensägeblatt", mana=70, cast_delay=0.3,
        description_de="Ein gewaltiges Sägeblatt. Kommt gern zu dir zurück.",
        damage=26, speed=300, lifetime=4.0, ricochet=12,
    ),
    # Mutationen after Noita's modifiers
    Block(
        "schwerer_schuss", "Schwerer Schuss", Category.MODIFIER, mana=7,
        description_de="Nächste Drüse: +18 Schaden, aber nur noch ein Drittel so schnell.",
        damage_bonus=18.0, speed_factor=0.33,
    ),
    Block(
        "teiler_2", "Teiler ×2", Category.MODIFIER, mana=35, cast_delay=0.1,
        description_de="Feuert die nächste Gruppe gleich zweimal ab, auch teure Einzelstücke.",
        multicast=2, divide=True,
    ),
    Block(
        "teiler_3", "Teiler ×3", Category.MODIFIER, mana=50, cast_delay=0.2,
        description_de="Feuert die nächste Gruppe dreimal ab.", multicast=3, divide=True,
    ),
    Block(
        "teiler_4", "Teiler ×4", Category.MODIFIER, mana=70, cast_delay=0.3,
        description_de="Feuert die nächste Gruppe viermal ab.", multicast=4, divide=True,
    ),
    Block(
        "unerschoepflich", "Unerschöpflicher Kern", Category.MODIFIER, mana=40,
        description_de="Die nächste Drüse mit Ladungen verbraucht keine Ladung.",
        endless=True, rarity=0.5,
    ),
    Block(
        "zauber_zu_kraft", "Zauber zu Kraft", Category.MODIFIER, mana=110, cast_delay=0.6,
        description_de="Verschlingt deine fliegenden Geschosse in der Nähe und packt ihren "
        "Schaden auf die nächste Drüse.",
        absorb=True, rarity=0.5,
    ),
    # Drüsen that transform everything of yours that is in the air
    Block(
        "zauber_zu_raketen", "Zauber zu Raketen (L20)", Category.FORM, mana=100, cast_delay=1.0,
        uses=20, description_de="Alle deine fliegenden Geschosse werden zu Flux-Raketen.",
        convert="flux_rakete", rarity=0.5,
    ),
    Block(
        "zauber_zu_saegen", "Zauber zu Sägeblättern (L20)", Category.FORM, mana=100,
        cast_delay=1.0, uses=20,
        description_de="Alle deine fliegenden Geschosse werden zu Riesensägeblättern.",
        convert="riesensaege", rarity=0.5,
    ),
    Block(
        "zauber_zu_kreuzen", "Zauber zu Todeskreuzen (L15)", Category.FORM, mana=80,
        cast_delay=1.0, uses=15,
        description_de="Alle deine fliegenden Geschosse bleiben stehen und werden zu Todeskreuzen.",
        convert="todeskreuz", rarity=0.5,
    ),
    Block(
        "zauber_zu_loechern", "Zauber zu Schwarzen Löchern (L3)", Category.FORM, mana=200,
        cast_delay=1.5, uses=3,
        description_de="Alle deine fliegenden Geschosse werden zu Schwarzen Löchern.",
        convert="schwarzes_loch", rarity=0.3,
    ),
    Block(
        "zauber_zu_bomben", "Zauber zu Atombomben (L1)", Category.FORM, mana=250, cast_delay=2.0,
        uses=1,
        description_de="Alle deine fliegenden Geschosse werden zu Atombomben. Wirklich alle.",
        convert="atombombe", rarity=0.15,
    ),
)  # fmt: skip
BLOCKS = BLOCKS + NOITA_BLOCKS

TIER3_BLOCKS: frozenset[str] = frozenset(
    {
        "grosse_flux_rakete", "schwarzes_loch", "blitzschlag", "meteorit", "atombombe",
        "teiler_3", "teiler_4", "unerschoepflich", "zauber_zu_kraft", "zauber_zu_raketen",
        "zauber_zu_saegen", "zauber_zu_kreuzen", "zauber_zu_loechern", "zauber_zu_bomben",
        "sprengkern",
        "knochenbombe",
        "achterkreis",
        "dreifach",
        "zielsuche",
        "kettenfunke",
        "schwerelos",
        "blutpreis",
    }
)


def _tier(block: Block) -> int:
    if block.key in TIER3_BLOCKS:
        return 3
    if block in NOITA_BLOCKS:
        return 2 if block.mana >= 30 else 1
    return 2 if block.rarity == FAMILY_RARITY else 1


BLOCKS = tuple(replace(b, rarity_tier=_tier(b)) for b in BLOCKS)

from typing import Any


class _BlockCatalogTuple(tuple[Block, ...]):
    """Tuple of Block instances that also supports dict-like lookup by block key."""

    def keys(self):
        return CATALOG.keys()

    def values(self):
        return CATALOG.values()

    def items(self):
        return CATALOG.items()

    def get(self, key: str, default: Any = None) -> Any:
        k = resolve_block_key(key)
        return CATALOG.get(k, default)

    def __getitem__(self, key: int | slice | str) -> Any:  # type: ignore[override]
        if isinstance(key, str):
            k = resolve_block_key(key)
            return CATALOG[k]
        return super().__getitem__(key)


CATALOG: dict[str, Block] = {block.key: block for block in BLOCKS}
assert len(CATALOG) == len(BLOCKS), "duplicate block keys"
BLOCKS = _BlockCatalogTuple(BLOCKS)

MODULE_ALIASES: dict[str, str] = {
    # Geschosse (24)
    "flux_funke": "funke",
    "spark": "funke",
    "funken": "funke",
    "nadelschuss": "nadel",
    "huepfgranate": "gallenblase",
    "matschbatzen": "klumpen",
    "schrotladung": "knochensplitter",
    "bohrkopf": "zahnbohrer",
    "lebenssauger": "blutegel",
    "sprungbolzen": "teleportbolzen",
    "kreissaege": "knochensaege",
    "haftmine": "sporenmine",
    "tunnelfresser": "fressgeschwuer",
    "durchschlagbolzen": "knochenspeer",
    "mikrofunke": "mikrofunke",
    "feuerball": "feuerball",
    "kraterbombe": "knochenbombe",
    "nadelregen": "nadelregen",
    "klebekugel": "schleimkugel",
    "stromstoss": "nervenstrom",
    "wandelstrahl": "wandlungsdruese",
    "tauschstrahl": "tauschdruese",
    "kettenblitz": "kettenfunke",
    "leuchtfackel": "leuchtkugel",
    "mahlwerk": "zahnrad",
    "flummi": "gelenkkugel",
    # Aufsätze (22)
    "turbo": "beschleunigung",
    "turbo_x": "beschleunigung_stark",
    "sprengladung": "sprengkraft",
    "atomkern": "sprengkern",
    "antigrav": "umkehr",
    "schwebefeld": "schwerelos",
    "bleimantel": "schwere_ladung",
    "zielsuchkopf": "zielsuche",
    "doppellauf": "doppel",
    "dreifachlauf": "dreifach",
    "rundumschlag": "achterkreis",
    "faecherduese": "faecher",
    "rueckspiegel": "vorne_hinten",
    "panzerbrechend": "durchbohren",
    "gummierung": "abprall",
    "brandsatz": "brandbeschleuniger",
    "langstrecke": "langlebigkeit",
    "kurzstrecke": "kurzlebig",
    "wucht": "giftzahn",
    "fluxpumpe": "blutpreis",
    "schnelllader": "dauerladung",
    "abzugsfeder": "hast",
    # Zünder (4)
    "aufschlagzuender": "nerv_aufprall",
    "zeitzuender": "nerv_zeit",
    "endzuender": "nerv_ende",
    "naessezuender": "nerv_naesse",
    # Füllungen (2 Aliase auf bestehende Sekrete)
    "fuellung_feuer": "sekret_feuer",
    "fuellung_rauch": "sekret_rauch",
}


def blocks_of_tier(tier: int) -> list[str]:
    """Return all block keys with rarity_tier == tier (Card A02)."""
    return [block.key for block in BLOCKS if block.rarity_tier == tier and not block.retired]


def resolve_block_key(key: str) -> str:
    """Resolve German/legacy alias to canonical block key (Card A02)."""
    return MODULE_ALIASES.get(key, key)


def __getattr__(name: str) -> Any:
    if name in ("Wand", "WandSpec"):
        from src import wand

        return getattr(wand, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


FLASK_PAYLOAD_CELLS = 10  # cells of the held flask one "Kolbenfüllung" shot uses (Contract V0e)


def resolve_payload_material(
    block: Block,
    flask: Any,
    set_keys: tuple[str, ...],
    base_keys: tuple[str, ...],
    rng: Any,
) -> str | None:
    """Material key a payload block delivers for one cast (Contract V0e)."""
    if not (block.from_flask or block.local_material):
        return block.material

    if block.from_flask:
        key = getattr(flask, "key", None) or getattr(flask, "liquid", None)
        amt = getattr(flask, "amount", 0.0)
        if flask is not None and key and amt >= FLASK_PAYLOAD_CELLS:
            flask.amount -= FLASK_PAYLOAD_CELLS
            return key
        return "water"

    if block.local_material:
        universe_materials = [k for k in set_keys if k not in base_keys]
        if universe_materials:
            return rng.choice(universe_materials)
        return "water"

    return block.material
