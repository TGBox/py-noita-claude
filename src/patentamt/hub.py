"""Patentamt hub districts, ticket queue, and navigation state."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DistrictSpec:
    """One district inside the Multiversums-Patentamt citadel."""

    key: str
    title_de: str
    subtitle_de: str
    ticket_prefix: str
    danger_tier: int


PATENTAMT_DISTRICTS: tuple[DistrictSpec, ...] = (
    DistrictSpec(
        "wartezimmer",
        "Wartezimmer Endlos-B",
        "Plastikstühle, vergessene Zeitschriften und gezogene Wartenummern bis in die Ewigkeit.",
        "W",
        1,
    ),
    DistrictSpec(
        "aktenschrank_schlucht",
        "Aktenschrank-Schlucht",
        "Vierzig Meter hohe Stahlregistraturen mit Zugluft und scharfkantigen Hängeregistern.",
        "A",
        2,
    ),
    DistrictSpec(
        "klon_legebatterie",
        "Klon-Legebatterie",
        "Brutkästen alternativer Zeitlinien-Cloitas unter Neonröhren und Kaffeeduft.",
        "K",
        2,
    ),
    DistrictSpec(
        "kassenschalter",
        "Kassenschalter C-404",
        "Hier werden Geldstrafen gestempelt und kostenpflichtige Patent-Alibis verkauft.",
        "C",
        1,
    ),
)

DISTRICTS_BY_KEY: dict[str, DistrictSpec] = {d.key: d for d in PATENTAMT_DISTRICTS}


@dataclass
class PatentamtHub:
    """Tracks exploration, queue ticket number, and active district inside the Patentamt."""

    active_district: str = "wartezimmer"
    ticket_number: int = 101
    visited_districts: set[str] = field(default_factory=lambda: {"wartezimmer"})
    stamps_collected: int = 0

    def enter_district(self, key: str) -> DistrictSpec:
        if key not in DISTRICTS_BY_KEY:
            raise KeyError(f"Unbekannter Patentamt-Bezirk: {key}")
        self.active_district = key
        self.visited_districts.add(key)
        return DISTRICTS_BY_KEY[key]

    def draw_ticket(self) -> str:
        spec = DISTRICTS_BY_KEY[self.active_district]
        code = f"{spec.ticket_prefix}-{self.ticket_number}"
        self.ticket_number += 1
        return code

    def stamp_pass(self) -> int:
        self.stamps_collected += 1
        return self.stamps_collected
