"""Alternate-timeline Cloita NPCs inside the Patentamt and clone battery."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CloitaVariant:
    """Unique alternate Cloita (never duplicated inside a run)."""

    key: str
    name_de: str
    role_de: str
    district: str
    lines_de: tuple[str, ...]
    discount_gold: int = 0


PATENTAMT_CLOITAS: dict[str, CloitaVariant] = {
    "cloita_steuerberaterin": CloitaVariant(
        key="cloita_steuerberaterin",
        name_de="Steuerberaterin Cloita",
        role_de="Fachkraft für alchemistische Abschreibungen",
        district="wartezimmer",
        lines_de=(
            "Wenn Ihnen ein Universum explodiert, setzen Sie die Trümmer einfach als Schwund ab.",
            "Ohne Beleg erkenne ich weder Ihre Heldentat noch Ihre Brandwunden an.",
        ),
        discount_gold=15,
    ),
    "cloita_schlafwandlerin": CloitaVariant(
        key="cloita_schlafwandlerin",
        name_de="Nachtschicht-Cloita",
        role_de="Chronisch unterkoffeinierte Aktensortiererin",
        district="aktenschrank_schlucht",
        lines_de=(
            "Ich stemple seit vierhundert Schichten denselben Ordner. Ich glaube, es ist Dienstag.",
            "Falls Sie die rebellische Version suchen: Sie schuldet mir noch einen Kaffeebecher.",
        ),
    ),
    "cloita_prueferin": CloitaVariant(
        key="cloita_prueferin",
        name_de="Oberamts-Cloita",
        role_de="Stempelaufsicht der Klon-Legebatterie",
        district="klon_legebatterie",
        lines_de=(
            "Jede Cloita hier trägt eine eigene Seriennummer. Doppelungen gelten als Ordnungswidrigkeit.",
            "Ihre Wartenummer liegt rund dreitausend Jahre hinter dem aktuellen Aufruf.",
        ),
    ),
    "cloita_kasse": CloitaVariant(
        key="cloita_kasse",
        name_de="Schalter-Cloita",
        role_de="Ausgabestelle für Formular C-404",
        district="kassenschalter",
        lines_de=(
            "Mit einem gültigen Patent-Alibi sieht das Gesetz kurz in die andere Richtung.",
            "Gold wird bar gezählt. Reue wird nicht erstattet.",
        ),
    ),
}


def talk_to_cloita(npc_key: str, round_idx: int = 0) -> str:
    """Return a German dialogue line for one unique alternate Cloita."""
    if npc_key not in PATENTAMT_CLOITAS:
        raise KeyError(f"Unbekannte Cloita-Variante: {npc_key}")
    npc = PATENTAMT_CLOITAS[npc_key]
    return npc.lines_de[round_idx % len(npc.lines_de)]
