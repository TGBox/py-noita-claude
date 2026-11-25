"""Contract V21 section 4: Klonita's German dialogue lines (Card F11).

Tone (bible 08): warm, a little clumsy, never cruel; at most 60 characters per line.
"""

from __future__ import annotations

import random

UNIVERSE_KEYS: tuple[str, ...] = (
    "fleischwelt", "aktenhalde", "glibbria", "kruemelreich", "sporenklub", "abtei",
)  # fmt: skip

LINES: dict[str, tuple[str, ...]] = {
    "enter_universe": (
        "Neue Welt, neues Glück!",
        "Riecht hier irgendwie anders.",
        "Ich bleib dicht bei dir, versprochen.",
        "Ob es hier Snacks gibt?",
        "Der Portalrahmen hat gezuckt. Alles gut?",
        "Notiz an mich: nichts anfassen. Fast nichts.",
        "Die Schwerkraft fühlt sich komisch an.",
        "Wenn was schiefgeht, war ich es nicht.",
    ),
    "enter_fleischwelt": (
        "Igitt, es pulsiert.",
        "Das Fleisch hier guckt zurück.",
        "Bitte nicht in die Pfützen treten.",
    ),
    "enter_aktenhalde": (
        "So viel Papier. So wenig Kaffee.",
        "Formulare, soweit das Auge reicht.",
        "Wenn jemand fragt: wir haben einen Termin.",
    ),
    "enter_glibbria": (
        "Alles wabbelt. Ich mag es.",
        "Pass auf, der Boden federt!",
        "Kaugummi! Also, wahrscheinlich.",
    ),
    "enter_kruemelreich": (
        "Es riecht nach Zucker und Ärger.",
        "Nicht die Ameisen ärgern. Bitte.",
        "Ich knabbere nur ganz kurz an der Wand.",
    ),
    "enter_sporenklub": (
        "Der Bass! Ich spüre ihn im Bauch.",
        "Nicht einatmen, einfach tanzen.",
        "Die Pilze leuchten. Das ist nie gut.",
    ),
    "enter_abtei": (
        "Hier unten ist es so still.",
        "Luft holen nicht vergessen!",
        "Die Glocken hören mit.",
    ),
    "player_hurt": (
        "Au! Das sah schlimm aus.",
        "Hey, pass doch auf dich auf!",
        "Soll ich pusten?",
        "Nicht nochmal, bitte.",
        "Das wird einen Fleck geben.",
        "Du blutest ein bisschen. Nur zur Info.",
    ),
    "kill_peaceful": (
        "Das war nicht nötig.",
        "Es hat dir nichts getan.",
        "Die Behörde hat das bestimmt gesehen.",
        "Ich schau kurz weg.",
        "Mir wird schlecht.",
        "Das stand nicht im Plan.",
    ),
    "klonita_hit": (
        "Autsch! Mein Arm!",
        "Warum immer ich?",
        "Das tat weh, du Blödmann!",
        "Ich seh Sterne. Und Formulare.",
        "Kurz hinsetzen. Nur kurz.",
        "Mein Helm! Ach so, ich hab keinen.",
    ),
    "klonita_up": (
        "Alles wieder dran. Glaube ich.",
        "Wo war ich? Ach ja: hinter dir.",
        "Nur ein Kratzer. Oder zwei.",
        "Ich lebe! Wieder mal.",
        "Nächstes Mal duck ich mich.",
        "Weiter geht es, Chefin.",
    ),
    "point_secret": (
        "Da hinten! Siehst du das?",
        "Pssst. Da ist was versteckt.",
        "Mein Bauch sagt: dort entlang.",
        "Die Wand da klingt hohl.",
        "Glitzert da was?",
    ),
    "event_warn_fleischwelt": ("Das Herz schlägt schneller!", "Es wächst nach. Schnell!"),
    "event_warn_aktenhalde": ("Aktenlawine! Kopf einziehen!", "Der Schredder läuft heiß."),
    "event_warn_glibbria": ("Die Flut kommt. Klebrig!", "Alles hüpft. Festhalten!"),
    "event_warn_kruemelreich": ("Die Ameisen schwärmen aus!", "Zuckerregen! Nicht lecken."),
    "event_warn_sporenklub": ("Bass-Drop! Ohren zu!", "Die Sporen kommen in Wellen."),
    "event_warn_abtei": ("Das Wasser steigt!", "Die Glocken läuten. Weg hier!"),
    "boss_spawn": (
        "Oh nein. Der ist groß.",
        "Okay. Okay. Wir schaffen das.",
        "Ich bin direkt hinter dir. Weit hinter dir.",
        "Hat der auch einen Namen? Egal, drauf!",
    ),
    "boss_dead": (
        "Hast du gesehen? Ich hab geholfen!",
        "Puh. Das war knapp.",
        "Der steht nicht mehr auf, oder?",
        "Schnell, einsammeln!",
    ),
    "couch": (
        "Kuschelig hier!",
        "Nur fünf Minuten. Oder zehn.",
        "Die Couch versteht mich.",
        "Hier riecht es nach zu Hause.",
        "Ich hab ein Kissen geformt. Aus Flux.",
        "Nicht wecken, bitte.",
        "Zzz... Formulare... zzz...",
        "Ich bewache die Couch. Von innen.",
        "Kurz die Füße hoch.",
        "Die Werkstatt ist schön ruhig.",
        "Ob ich hier wohnen kann?",
        "Weck mich, wenn es losgeht.",
    ),
    "drink_good": (
        "Prickelt! Und schmeckt nach lila.",
        "Davon nehme ich auch einen Schluck.",
        "Blubb. Gesundheit!",
        "Das wird dir guttun.",
    ),
    "drink_bad": (
        "Pfui! Das war keine Limo.",
        "Warum trinkst du das?",
        "Mir dreht sich alles. Und ich war es nicht.",
        "Das hätte ich dir sagen können.",
    ),
    "trader_robbed": (
        "Das war Diebstahl! Ich sag's keinem.",
        "Der Händler guckt böse.",
        "Jetzt stehen wir auf der Liste.",
    ),
    "player_death": (
        "Nein, nein, nein. Steh auf!",
        "Ich hol Hilfe. Irgendwo. Gleich.",
        "Das war nicht abgemacht.",
        "Bitte. Nur noch einmal.",
        "Ich warte hier. So lange es dauert.",
    ),
    "called": (
        "Da bin ich!",
        "Hast du mich vermisst?",
        "Schon unterwegs!",
        "Ich war nie weg. Fast.",
        "Melde mich zum Dienst!",
    ),
    "dismissed": (
        "Okay. Ich bin in der Tasche.",
        "Ruf einfach, ja?",
        "Dann mach ich Pause.",
        "Pass auf dich auf.",
        "Ich zähl die Sekunden.",
    ),
    "player_low_hp": (
        "Du siehst blass aus. Snack?",
        "Rückzug! Ich bestehe darauf.",
        "Bitte nicht sterben. Ich hab Pläne.",
    ),
    "memory_shard": (
        "Ein Splitter! Der erinnert sich.",
        "Das kitzelt im Kopf.",
        "Noch einer für die Sammlung.",
    ),
    "wanted_high": ("Die Behörde kommt. Viele.", "Drei Siegel! Wir sind berühmt."),
    "helper_carry": ("Hab ich dir runtergeholt!", "Bitte sehr. Lag ganz oben."),
    "quirk_tip_trader": ("Für Ihre Mühe!", "Trinkgeld muss sein."),
    "quirk_feed_creature": ("Hier, ein Krümel für dich.", "Es hatte Hunger, okay?"),
    "quirk_warn_enemy": ("Pass auf, sie schießt gleich!", "Vorsicht! Ups."),
    "shiny_poke": ("Oh, glänzt das?", "Nur kurz anstupsen."),
    "loud_sneeze": ("Haaa-tschi!", "Entschuldigung. Pollen."),
    "sample_nibble": ("Schmeckt nach Wissenschaft!", "War nur ein Krümel."),
    "snack": ("Hier, iss was.", "Snackpause!"),
    "shield": ("Hab ich!", "Nicht heute!"),
    "cleanse": ("Weg damit.", "Sauber."),
    "default": ("Hm.", "Bin dabei!"),
}

LINE_COUNTS: dict[str, int] = {
    "enter_universe": 8,
    "player_hurt": 6,
    "kill_peaceful": 6,
    "klonita_hit": 6,
    "klonita_up": 6,
    "point_secret": 5,
    "boss_spawn": 4,
    "boss_dead": 4,
    "couch": 12,
    "drink_good": 4,
    "drink_bad": 4,
    "trader_robbed": 3,
    "player_death": 5,
    "called": 5,
    "dismissed": 5,
    "player_low_hp": 3,
    "memory_shard": 3,
    "wanted_high": 2,
    "helper_carry": 2,
    "quirk_tip_trader": 2,
    "quirk_feed_creature": 2,
    "quirk_warn_enemy": 2,
    "default": 2,
    **{f"enter_{key}": 3 for key in UNIVERSE_KEYS},
    **{f"event_warn_{key}": 2 for key in UNIVERSE_KEYS},
}


def line_for(topic: str, rng: random.Random) -> str:
    """Pick a line for ``topic`` (unknown topics fall back to "default")."""
    return rng.choice(LINES.get(topic) or LINES["default"])
