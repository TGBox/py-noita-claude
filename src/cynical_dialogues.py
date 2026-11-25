"""Cynical German quips for Cloita, Klonita, and 4th-wall meta commentary (Phase T03)."""

from __future__ import annotations

import random

CLOITA_QUIPS: tuple[str, ...] = (
    "Schon wieder ein neues Universum. Die Miete zahlt sich leider in keinem davon von selbst.",
    "Wenn etwas grün leuchtet, ist es entweder radioaktiv, bürokratisch oder mein Abendessen.",
    "Wissenschaft bedeutet: Dinge so lange in die Luft jagen, bis das Amt einen Stempel darauf setzt.",
    "Ich wollte heute eigentlich Urlaub nehmen, aber die Realität hatte andere Absturzpläne.",
)

KLONITA_QUIPS: tuple[str, ...] = (
    "Ich stecke wieder im Rucksack. Wenigstens zieht es hier drin nicht.",
    "Überstunden zählen in Parallelwelten doppelt — behauptet zumindest mein leeres Kaffeeglas.",
    "Falls ich sterbe, rufe ich einfach das Patentamt wegen ungenehmigter Abnutzung an.",
    "Kein Sorge, ich bin vertraglich unkaputtbar. Mein Geduldsfaden allerdings nicht.",
)

FOURTH_WALL_QUIPS: tuple[str, ...] = (
    "Schau auf die Bildrate, nicht auf meine Entscheidungen — die sind beide fragwürdig.",
    "Du klickst schon wieder auf jeden Schalter, ohne den Warnhinweis zu lesen, richtig?",
    "Dieser Text kommt direkt aus einem Python-Modul. Fühlst du dich jetzt klüger?",
    "Irgendwo protokolliert eine JSON-Datei jede deiner Peinlichkeiten. Viel Erfolg!",
)

EVENT_REACTIONS_DE: dict[str, str] = {
    "death": "Neuer Klon, alte Schulden. Willkommen zurück in der Werkstatt.",
    "fine": "Der Sachbearbeiter freut sich über deine Spende in die Kaffeekasse.",
    "parasite": "Niemand in diesem Multiversum ist jemals ohne Grund nett zu dir.",
    "boss_win": "Ein Problem weniger — drei neue Formulare dafür.",
    "tv": "Endlich Qualitätsfernsehen für Menschen mit zu wenig Schlaf.",
}


def pick_cynical_line(category: str = "cloita", seed: int | None = None) -> str:
    """Select a deterministic or random German cynical line by category."""
    pools: dict[str, tuple[str, ...]] = {
        "cloita": CLOITA_QUIPS,
        "klonita": KLONITA_QUIPS,
        "fourth_wall": FOURTH_WALL_QUIPS,
        "meta": FOURTH_WALL_QUIPS,
    }
    pool = pools.get(category, CLOITA_QUIPS)
    if seed is None:
        return random.choice(pool)
    return pool[seed % len(pool)]


def react_to_event(trigger_key: str) -> str:
    """Return a matching cynical German reaction line for a gameplay milestone."""
    return EVENT_REACTIONS_DE.get(trigger_key, CLOITA_QUIPS[0])
