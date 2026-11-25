"""Twelve satirical interdimensional TV channels for ws_tv."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TVChannel:
    """Definition of one interdimensional television channel and its watch buff."""

    number: int
    key: str
    title_de: str
    tagline_de: str
    lines_de: tuple[str, ...]
    buff_key: str
    buff_desc_de: str
    buff_effect: dict[str, Any]
    promo_code: str | None = None


PROMO_DISCOUNTS: dict[str, float] = {
    "RABATT-42-GLIBBER": 0.42,
}


TV_CHANNELS: tuple[TVChannel, ...] = (
    TVChannel(
        1,
        "kanal_teleshop",
        "Glibber-Teleshopping 24",
        "Bestellen Sie jetzt dreidimensionalen Schleim zum Zweidimensional-Preis!",
        (
            "Nur heute: Der selbstnachfüllende Büroeimer mit Extra-Haftung!",
            "Geben Sie am Fabrikator den Code RABATT-42-GLIBBER ein!",
        ),
        "buff_schnaeppchen",
        "+10% Goldfunde im nächsten Einsatz.",
        {"gold_bonus": 0.10},
        promo_code="RABATT-42-GLIBBER",
    ),
    TVChannel(
        2,
        "kanal_kochen",
        "Kochen mit Gallenstein",
        "Heißer als eine Fehlinvestition in Antimaterie.",
        (
            "Eine Prise Schwefel, zwei Löffel Büroschweiß und fertig ist der Fluch.",
            "Hinweis der Redaktion: Topf nicht direkt anstarren.",
        ),
        "buff_magenstaerke",
        "+15 temporärer Schutzschild beim Betreten.",
        {"shield_hp": 15.0},
    ),
    TVChannel(
        3,
        "kanal_amtsnews",
        "Patentamt-Tagesschau",
        "Die wichtigsten Formulare des Tages — verlesen in Zeitlupe.",
        (
            "Eilmeldung: Formular 17-B wurde wegen Überfüllung in 17-B/Alt umbenannt.",
            "Das Wetter bleibt heute streng genehmigungspflichtig.",
        ),
        "buff_alibi_licht",
        "-10% Fahndungszuwachs durch Aktenkenntnis.",
        {"wanted_scale": 0.90},
    ),
    TVChannel(
        4,
        "kanal_hamster",
        "Endlos-Hamsterrad HD",
        "24 Stunden ununterbrochenes Laufen ohne Fortschritt.",
        (
            "Runde 482.910: Der kleine Nager hält das Tempo — ganz wie Sie im Labor.",
            "Experten sehen hierin ein starkes Konjunktursignal.",
        ),
        "buff_ausdauer",
        "+15% Flugenergie-Kapazität für einen Lauf.",
        {"energy_bonus": 0.15},
    ),
    TVChannel(
        5,
        "kanal_seifenoper",
        "Sturm der Klone",
        "Folge 9.402: Cloita entdeckt, dass ihr Zwilling auch nur eine Vertretung ist.",
        (
            "'Du hast meinen Kittel gestohlen!' — 'Nein, du warst die Vorlage!'",
            "Dramatischer Zoom auf eine leere Kaffeetasse.",
        ),
        "buff_drama",
        "+10% kritischer Schaden auf den ersten Zauber.",
        {"crit_bonus": 0.10},
    ),
    TVChannel(
        6,
        "kanal_wetter",
        "Multiversums-Wetterbericht",
        "Vorsicht vor lokalem Zuckersturm und leichtem Bleiregen.",
        (
            "In Pastell-Hölle steigen die klebrigen Tiefdruckgebiete auf 38 Grad.",
            "Nehmen Sie heute besser einen Regenschirm aus Titan mit.",
        ),
        "buff_resistenz",
        "+1.5s Feuerschutz zu Laufbeginn.",
        {"fire_ward": 1.5},
    ),
    TVChannel(
        7,
        "kanal_gericht",
        "Geistergericht am Nachmittag",
        "Heute: Ein Kobold klagt gegen einen explodierten Zauberstab.",
        (
            "Richterin: 'Haben Sie vor der Detonation ein Warnschild aufgestellt?'",
            "Zeuge: 'Nur ein leichtes Pfeifen.'",
        ),
        "buff_beweissicherung",
        "+1 Bauplan-Bonuschance bei Elitefunden.",
        {"loot_luck": 0.10},
    ),
    TVChannel(
        8,
        "kanal_quiz",
        "Wer wird Reagenzglas?",
        "Drei Kandidaten, vier Dimensionen, null richtige Antworten.",
        (
            "Frage für 500 Gold: Wie oft darf man denselben Fehler patentieren?",
            "Antwort A: Immer. Antwort B: Mit Gebühr sogar zweimal.",
        ),
        "buff_quizgeist",
        "+12% Mana-Regeneration im nächsten Lauf.",
        {"mana_regen": 0.12},
    ),
    TVChannel(
        9,
        "kanal_diy",
        "Basteln mit Schrott",
        "Aus zwei alten Federn und etwas Panik entsteht ein Stab.",
        (
            "Wenn es funkt, nennen wir es Feature. Wenn es brennt, nennen wir es Kunst.",
            "Kleber niemals auf laufende Portale auftragen.",
        ),
        "buff_bastelei",
        "+8% Projektilschaden.",
        {"damage_bonus": 0.08},
    ),
    TVChannel(
        10,
        "kanal_verkehr",
        "Kosmische Stau-Kamera",
        "Vollsperrung auf Portal-Spur 3 wegen entlaufener Pudding-Wolke.",
        (
            "Reisende Richtung Krawatten-Planet planen bitte 400 Formulare Zeit ein.",
            "Umleitung über den nächsten Müllschacht empfohlen.",
        ),
        "buff_sprint",
        "+8% Laufgeschwindigkeit.",
        {"speed_bonus": 0.08},
    ),
    TVChannel(
        11,
        "kanal_schlaf",
        "Meditation mit Laubbläser",
        "Entspannungsmusik für überarbeitete Alchemistinnen.",
        (
            "Atmen Sie ein. Atmen Sie Staub aus. Vergessen Sie die Mietrechnung.",
            "Nichts bedeutet etwas, aber zumindest brummt der Bildschirm angenehm.",
        ),
        "buff_gelassenheit",
        "+10 Max-Schildpunkte.",
        {"shield_hp": 10.0},
    ),
    TVChannel(
        12,
        "kanal_scifi",
        "Raumschiff Büroklammer",
        "Die mutige Besatzung erforscht Aktenordner, die nie ein Mensch zuvor las.",
        (
            "Captain: 'Energie auf die Kaffeemaschine!' — 'Zu spät, sie kocht Wasser!'",
            "Fortsetzung folgt nach der nächsten Haushaltskürzung.",
        ),
        "buff_laser",
        "+10% Projektiltempo.",
        {"speed_mult": 1.10},
    ),
)

TV_CHANNELS_BY_KEY: dict[str, TVChannel] = {ch.key: ch for ch in TV_CHANNELS}
