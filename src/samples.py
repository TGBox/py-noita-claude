"""Contract V11: Sample registry and stack constants (Card A04)."""

from __future__ import annotations

from dataclasses import dataclass

SAMPLE_SLOTS: int = 12
SAMPLE_STACK: int = 99


@dataclass(frozen=True)
class Sample:
    key: str
    name: str
    universe_key: str
    tier: int
    color: tuple[int, int, int]
    description: str


SAMPLES: dict[str, Sample] = {}

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
    "probe_saft": "probe_gallenstein",
    "probe_papier": "probe_stempelkissen",
    "probe_bunt": "probe_glibberkern",
    "probe_harz": "probe_ameisenduft",
    "probe_pilz": "probe_leuchtspore",
    "probe_salz": "probe_glockensplitter",
    "probe_rost": "probe_knochen",
    "probe_zucker": "probe_zuckerkristall",
    "probe_spule": "probe_aether",
}
