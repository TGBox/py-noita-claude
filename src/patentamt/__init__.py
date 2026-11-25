"""Multiversums-Patentamt & Klon-Legebatterie hub package (Phase P)."""

from __future__ import annotations

from src.patentamt.archive import PATENT_ALIBI_FORM, PatentAlibiRecord, PatentArchive
from src.patentamt.generator import PatentamtRoom, generate_patentamt_layout
from src.patentamt.hub import PATENTAMT_DISTRICTS, DistrictSpec, PatentamtHub
from src.patentamt.npcs import PATENTAMT_CLOITAS, CloitaVariant, talk_to_cloita

__all__ = [
    "PATENTAMT_CLOITAS",
    "PATENTAMT_DISTRICTS",
    "PATENT_ALIBI_FORM",
    "CloitaVariant",
    "DistrictSpec",
    "PatentAlibiRecord",
    "PatentArchive",
    "PatentamtHub",
    "PatentamtRoom",
    "generate_patentamt_layout",
    "talk_to_cloita",
]
