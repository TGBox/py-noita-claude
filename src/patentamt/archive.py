"""Patent archive, Form C-404 alibi issuance, and Wanted mitigation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PATENT_ALIBI_FORM = "C-404"
PATENT_ALIBI_COST_GOLD = 150


@dataclass(frozen=True)
class PatentAlibiRecord:
    """Proof of purchase for a temporary bureaucratic immunity certificate."""

    form_code: str
    holder_name: str
    cost_gold: int
    note_de: str


@dataclass
class PatentArchive:
    """Issues Patent-Alibi forms and logs registered multiversal patents."""

    issued_alibis: list[PatentAlibiRecord] = field(default_factory=list)
    registered_patents: list[str] = field(default_factory=list)

    def purchase_alibi(
        self,
        run_or_wallet: Any,
        wanted: Any | None = None,
        *,
        cost_gold: int = PATENT_ALIBI_COST_GOLD,
        duration: float = 60.0,
    ) -> tuple[bool, str]:
        gold = int(getattr(run_or_wallet, "gold", 0))
        if gold < cost_gold:
            return False, f"Zu wenig Gold für Formular {PATENT_ALIBI_FORM} ({cost_gold} benötigt)."
        run_or_wallet.gold = gold - cost_gold
        record = PatentAlibiRecord(
            form_code=PATENT_ALIBI_FORM,
            holder_name=str(getattr(run_or_wallet, "player_name", "Cloita")),
            cost_gold=cost_gold,
            note_de="Rückwirkende Befugniserteilung für experimentelle Zerstörung.",
        )
        self.issued_alibis.append(record)
        if wanted is not None and hasattr(wanted, "apply_patent_alibi"):
            wanted.apply_patent_alibi(PATENT_ALIBI_FORM, duration=duration)
        return True, f"Formular {PATENT_ALIBI_FORM} gestempelt: Fahndungsdruck reduziert!"

    def register_patent(self, title_de: str) -> int:
        self.registered_patents.append(title_de)
        return len(self.registered_patents)
