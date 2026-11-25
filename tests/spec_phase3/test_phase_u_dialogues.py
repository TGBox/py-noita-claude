"""Phase U dialogue & German localization completeness checks."""

from __future__ import annotations

from src.cynical_dialogues import (
    CLOITA_QUIPS,
    EVENT_REACTIONS_DE,
    FOURTH_WALL_QUIPS,
    KLONITA_QUIPS,
)
from src.events import PHASE3_EVENTS
from src.gadgets import GADGET_SPECS
from src.patentamt import PATENTAMT_CLOITAS, PATENTAMT_DISTRICTS
from src.rules import PHASE3_DESCRIPTIONS_DE, PHASE3_NAMES_DE
from src.tv_channels import TV_CHANNELS
from src.universes.catalog_phase3 import PHASE3_UNIVERSES
from src.workshop import PHASE3_STATIONS

BANNED_MARKERS = ("todo", "fixme", "tbd", "lorem ipsum")


def _assert_clean_german(text: str) -> None:
    stripped = text.strip()
    assert len(stripped) >= 4
    low = stripped.lower()
    for marker in BANNED_MARKERS:
        assert marker not in low


def test_u04_all_phase3_texts_are_clean_non_empty_german() -> None:
    for spec in GADGET_SPECS.values():
        _assert_clean_german(str(spec["name_de"]))
        _assert_clean_german(str(spec["description_de"]))
        _assert_clean_german(str(spec["quote_de"]))

    for ch in TV_CHANNELS:
        _assert_clean_german(ch.title_de)
        _assert_clean_german(ch.tagline_de)
        _assert_clean_german(ch.buff_desc_de)
        for line in ch.lines_de:
            _assert_clean_german(line)

    for st in PHASE3_STATIONS.values():
        _assert_clean_german(st.name)
        _assert_clean_german(st.prompt_de)

    for d in PATENTAMT_DISTRICTS:
        _assert_clean_german(d.title_de)
        _assert_clean_german(d.subtitle_de)

    for c in PATENTAMT_CLOITAS.values():
        _assert_clean_german(c.name_de)
        _assert_clean_german(c.role_de)
        for line in c.lines_de:
            _assert_clean_german(line)

    for ev in PHASE3_EVENTS.values():
        _assert_clean_german(ev.name)
        _assert_clean_german(ev.description)

    for u in PHASE3_UNIVERSES:
        _assert_clean_german(u.name_de)
        _assert_clean_german(u.pitch_de)
        _assert_clean_german(PHASE3_NAMES_DE[u.rule])
        _assert_clean_german(PHASE3_DESCRIPTIONS_DE[u.rule])

    for line in (*CLOITA_QUIPS, *KLONITA_QUIPS, *FOURTH_WALL_QUIPS, *EVENT_REACTIONS_DE.values()):
        _assert_clean_german(line)
