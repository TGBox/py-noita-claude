"""Tests for Phase P Patentamt hub, procedural layout, alternate Cloitas, and C-404 alibi."""

from __future__ import annotations

from types import SimpleNamespace

from src.authority import Wanted
from src.patentamt import (
    PATENT_ALIBI_FORM,
    PATENTAMT_CLOITAS,
    PATENTAMT_DISTRICTS,
    PatentamtHub,
    PatentArchive,
    generate_patentamt_layout,
    talk_to_cloita,
)


def test_p01_patentamt_hub_districts_and_tickets() -> None:
    assert len(PATENTAMT_DISTRICTS) == 4
    hub = PatentamtHub()
    t1 = hub.draw_ticket()
    assert t1 == "W-101"
    hub.enter_district("klon_legebatterie")
    t2 = hub.draw_ticket()
    assert t2 == "K-102"
    assert "klon_legebatterie" in hub.visited_districts


def test_p02_procedural_patentamt_layout_deterministic() -> None:
    room_a = generate_patentamt_layout(42, district="klon_legebatterie")
    room_b = generate_patentamt_layout(42, district="klon_legebatterie")
    assert room_a.cells == room_b.cells
    assert len(room_a.incubators) > 0

    room_c = generate_patentamt_layout(42, district="aktenschrank_schlucht")
    assert len(room_c.cabinets) > 0


def test_p03_alternate_cloitas_are_unique_and_speak_german() -> None:
    assert len(PATENTAMT_CLOITAS) == 4
    assert len({c.name_de for c in PATENTAMT_CLOITAS.values()}) == 4
    line = talk_to_cloita("cloita_steuerberaterin", 0)
    assert "Beleg" in line or "Universum" in line


def test_p04_patent_alibi_c404_reduces_and_mitigates_wanted() -> None:
    wallet = SimpleNamespace(gold=200, player_name="Cloita")
    wanted = Wanted()
    wanted.add(3.0, "Laborunfall")
    archive = PatentArchive()

    ok, msg = archive.purchase_alibi(wallet, wanted)
    assert ok is True
    assert PATENT_ALIBI_FORM in msg
    assert wallet.gold == 50
    assert wanted.alibi_active is True
    assert wanted.level == 1.0

    # Subsequent infractions grow at half rate while C-404 alibi holds.
    wanted.add(1.0, "Aktenschrank geschmolzen")
    assert wanted.level == 1.5
