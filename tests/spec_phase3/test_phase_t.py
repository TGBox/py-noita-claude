"""Tests for Phase T parasite event, cynical dialogue pools, and workshop stats wall."""

from __future__ import annotations

from src.cynical_dialogues import (
    CLOITA_QUIPS,
    FOURTH_WALL_QUIPS,
    KLONITA_QUIPS,
    pick_cynical_line,
    react_to_event,
)
from src.events import ALL_EVENTS
from src.events_parasites import SUSPECT_KEYS, FalscheFreundeEvent
from src.workshop_stats import WorkshopStats


def test_t01_t02_falsche_freunde_parasite_deduction() -> None:
    assert "event_falsche_freunde" in ALL_EVENTS
    assert len(SUSPECT_KEYS) == 4

    ev = FalscheFreundeEvent(seed=7)
    sweet = [s for s in ev.suspects.values() if s.is_parasite]
    grumpy = [s for s in ev.suspects.values() if not s.is_parasite]
    assert len(sweet) == 1
    assert len(grumpy) == 3

    inspected = ev.inspect_suspect(sweet[0].key)
    assert "verdächtig" in inspected.flashback_de.lower() or "fälschung" in inspected.flashback_de.lower() or "kitsch" in inspected.flashback_de.lower() or "zu nett" in inspected.flashback_de.lower()

    # Shooting wrong suspect fails; shooting the sweet parasite succeeds.
    wrong_ev = FalscheFreundeEvent(seed=7)
    ok_wrong, _ = wrong_ev.shoot_suspect(grumpy[0].key)
    assert ok_wrong is False

    ok_hit, msg_hit = ev.shoot_suspect(sweet[0].key)
    assert ok_hit is True
    assert "treffer" in msg_hit.lower()


def test_t03_cynical_dialogues_all_pools_german() -> None:
    assert len(CLOITA_QUIPS) >= 3
    assert len(KLONITA_QUIPS) >= 3
    assert len(FOURTH_WALL_QUIPS) >= 3
    assert pick_cynical_line("cloita", seed=0) == CLOITA_QUIPS[0]
    assert pick_cynical_line("klonita", seed=1) == KLONITA_QUIPS[1]
    assert pick_cynical_line("fourth_wall", seed=2) == FOURTH_WALL_QUIPS[2]
    assert "klon" in react_to_event("death").lower()


def test_t04_workshop_stats_wall_counters_and_roundtrip() -> None:
    stats = WorkshopStats()
    stats.record_death()
    stats.record_fine(150)
    stats.record_explosion(3)
    stats.record_coffee(2)
    stats.record_tv_watch(20.0)
    stats.record_parasite()

    lines = stats.summary_lines_de()
    assert len(lines) >= 6
    assert any("150" in line for line in lines)

    restored = WorkshopStats.from_data(stats.to_data())
    assert restored == stats
