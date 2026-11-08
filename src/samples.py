"""Contract V11: Sample registry and stack constants (Card A04)."""

from __future__ import annotations

from dataclasses import dataclass

SAMPLE_SLOTS: int = 12
SAMPLE_STACK: int = 99


@dataclass(frozen=True)
class Sample:
    key: str  # "probe_gallenstein", "probe_wucherung", ... (exakt wie in V0a)
    name: str  # Deutscher Anzeigename, z. B. "Gallenstein"
    universe_key: str  # "fleischwelt", "aktenhalde", ... oder "allgemein"
    tier: int  # 1 = gewöhnlich, 2 = selten, 3 = rar
    color: tuple[int, int, int]
    description: str


SAMPLES: dict[str, Sample] = {
    # 12 Universums-Proben (je 2 pro MVP-Universum, exakt nach Bibel Kap. 07 & V0a):
    "probe_gallenstein": Sample(
        "probe_gallenstein",
        "Gallenstein",
        "fleischwelt",
        1,
        (224, 198, 72),
        "Ausgefällter Säuresplitter aus der Fleischwelt.",
    ),
    "probe_wucherung": Sample(
        "probe_wucherung",
        "Wucherungsableger",
        "fleischwelt",
        1,
        (214, 96, 128),
        "Pulsierender Gewebe-Ableger aus der Fleischwelt.",
    ),
    "probe_stempelkissen": Sample(
        "probe_stempelkissen",
        "Stempelkissen",
        "aktenhalde",
        1,
        (88, 124, 210),
        "Mit amtlicher Stempelfarbe getränktes Kissen aus der Aktenhalde.",
    ),
    "probe_formular": Sample(
        "probe_formular",
        "Formular B-38",
        "aktenhalde",
        1,
        (228, 220, 192),
        "Dreifach gestempeltes Antragsformular aus der Aktenhalde.",
    ),
    "probe_glibberkern": Sample(
        "probe_glibberkern",
        "Glibberkern",
        "glibbria",
        1,
        (236, 98, 224),
        "Elastischer Gelatinekern aus Glibbria.",
    ),
    "probe_brauseperle": Sample(
        "probe_brauseperle",
        "Brauseperle",
        "glibbria",
        1,
        (255, 216, 84),
        "Prickelnde Brausekapsel aus der Sirupküste von Glibbria.",
    ),
    "probe_zuckerkristall": Sample(
        "probe_zuckerkristall",
        "Riesenzuckerkristall",
        "kruemelreich",
        1,
        (244, 182, 216),
        "Glasharter Zuckerkristall aus dem Krümelreich.",
    ),
    "probe_ameisenduft": Sample(
        "probe_ameisenduft",
        "Ameisenduft-Ampulle",
        "kruemelreich",
        1,
        (218, 154, 62),
        "Duftstoff-Ampulle aus dem Ameisenbau des Krümelreichs.",
    ),
    "probe_leuchtspore": Sample(
        "probe_leuchtspore",
        "Leuchtspore im Glas",
        "sporenklub",
        1,
        (124, 232, 178),
        "Biolumineszente Sporenkapsel aus dem Sporen-Klub.",
    ),
    "probe_plattennadel": Sample(
        "probe_plattennadel",
        "Plattennadel",
        "sporenklub",
        1,
        (132, 198, 255),
        "Noch vom Bass vibrierende Plattennadel aus dem Sporen-Klub.",
    ),
    "probe_glockensplitter": Sample(
        "probe_glockensplitter",
        "Glockensplitter",
        "abtei",
        1,
        (196, 178, 114),
        "Klingender Bronzesplitter aus der Versunkenen Abtei.",
    ),
    "probe_kerzenstumpf": Sample(
        "probe_kerzenstumpf",
        "Kerzenstumpf mit Gesicht",
        "abtei",
        1,
        (238, 222, 176),
        "Wasserfester Wachsstumpf aus der Versunkenen Abtei.",
    ),
    # 5 seltene / allgemeine Proben (Tier 2 & Tier 3):
    "probe_knochen": Sample(
        "probe_knochen",
        "Mark-Splitter",
        "allgemein",
        2,
        (230, 222, 200),
        "Dichter Knochensplitter starker Kreaturen.",
    ),
    "probe_aether": Sample(
        "probe_aether",
        "Äther-Flocke",
        "allgemein",
        2,
        (164, 214, 255),
        "Schwereloser Rückstand aus instabilen Zaubern.",
    ),
    "probe_schatten": Sample(
        "probe_schatten",
        "Schatten-Faden",
        "allgemein",
        2,
        (96, 74, 138),
        "Dunkle Faser aus Geheimräumen und Verliesen.",
    ),
    "probe_gold": Sample(
        "probe_gold",
        "Reingold-Korn",
        "allgemein",
        3,
        (255, 214, 70),
        "Hochreines Goldkorn aus tiefen Goldadern.",
    ),
    "probe_kern": Sample(
        "probe_kern",
        "Wächter-Kern",
        "allgemein",
        3,
        (255, 96, 132),
        "Pulsierendes Herzstück eines besiegten Wächters.",
    ),
}

SAMPLE_ALIASES: dict[str, str] = {
    "gallenstein": "probe_gallenstein",
    "wucherung": "probe_wucherung",
    "wucherungsableger": "probe_wucherung",
    "stempelkissen": "probe_stempelkissen",
    "formular": "probe_formular",
    "formular_b38": "probe_formular",
    "glibberkern": "probe_glibberkern",
    "brauseperle": "probe_brauseperle",
    "zuckerkristall": "probe_zuckerkristall",
    "riesenzuckerkristall": "probe_zuckerkristall",
    "ameisenduft": "probe_ameisenduft",
    "leuchtspore": "probe_leuchtspore",
    "leuchtspore_im_glas": "probe_leuchtspore",
    "plattennadel": "probe_plattennadel",
    "glockensplitter": "probe_glockensplitter",
    "kerzenstumpf": "probe_kerzenstumpf",
}

SAMPLE_NAMES: dict[str, str] = {k: s.name for k, s in SAMPLES.items()}
