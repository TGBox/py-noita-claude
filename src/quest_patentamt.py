"""Patentamt sidequest progression and Cloita-Null reward logic (Phase Q)."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.bosses.cloita_null import CloitaNullBoss
from src.weapon_parts import get_phase3_weapon


@dataclass
class PatentamtQuest:
    """Tracks Cloita-Null rebellion questline and Patentkoffer weapon reward."""

    stage: str = "offen"
    stamps_sabotaged: int = 0
    stamps_required: int = 3
    boss_defeated: bool = False
    reward_weapon_key: str | None = None
    log_de: list[str] = field(
        default_factory=lambda: [
            "Cloita-Null hat in der Klon-Legebatterie eine Rebellion gegen den Stempelzwang ausgerufen."
        ]
    )

    def accept(self) -> str:
        if self.stage == "offen":
            self.stage = "sabotage"
            self.log_de.append("Auftrag: Zerstöre 3 zentrale Patent-Stempelterminals.")
        return self.stage

    def sabotage_stamp(self, count: int = 1) -> str:
        if self.stage == "offen":
            self.accept()
        self.stamps_sabotaged = min(self.stamps_required, self.stamps_sabotaged + max(0, count))
        if self.stamps_sabotaged >= self.stamps_required and self.stage == "sabotage":
            self.stage = "duell_bereit"
            self.log_de.append("Alle Stempelterminals blockiert — Cloita-Null wartet in der Arena!")
        return self.stage

    def resolve_boss_fight(self, boss: CloitaNullBoss) -> dict[str, object] | None:
        """Complete quest when Cloita-Null is defeated and grant Titan-Aktenkoffer."""
        if not boss.dead:
            return None
        self.boss_defeated = True
        self.stage = "abgeschlossen"
        self.reward_weapon_key = "waffe_patent_koffer"
        weapon = get_phase3_weapon("waffe_patent_koffer")
        self.log_de.append("Cloita-Null geschlagen! Belohnung erhalten: Titan-Aktenkoffer-Blaster.")
        return weapon
