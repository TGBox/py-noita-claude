"""Cosmic Quest: The 4 Essences of Wakefulness, Ur-Perkolator & Black Coffee Sun (Phase L04-L05)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from src.records import Records
from src.wand import Wand

ESSENCE_ORIGINS: dict[str, str] = {
    "essenz_roestung": "kuchen",
    "essenz_blitz": "spule",
    "essenz_zucker": "kruemelreich",
    "essenz_zeit": "uhrwerkwueste",
}
ESSENCE_KEYS: tuple[str, ...] = tuple(ESSENCE_ORIGINS)
REQUIRED_LIQUID_UNITS = 250
FLUX_BONUS_PER_S = 120.0
ENDING_KEY = "kaffeepause_der_ewigkeit"
ENDING_TITLE_DE = "Die Kaffeepause der Ewigkeit"
VALID_IGNITION_SOURCES = frozenset(
    {"plasma", "elektrolyt", "nervenstrom", "spark", "blitz", "electric"}
)


@dataclass
class BlackCoffeeSun:
    """Physical Cosmic Entity spawned by Ur-Perkolator: +120 Flux/s & true cosmic ending (L05)."""

    x: float
    y: float
    key: str = "kaffee_sonne"
    flux_bonus: float = FLUX_BONUS_PER_S
    vortex_radius: float = 120.0
    vortex_strength: float = 40.0

    def apply_flux_boost(self, wand: Wand, dt: float) -> float:
        """Grant +120 Flux/s directly onto the equipped wand."""
        added = min(wand.spec.mana_max - wand.mana, self.flux_bonus * dt)
        wand.mana = min(wand.spec.mana_max, wand.mana + self.flux_bonus * dt)
        return max(0.0, added)

    def apply_vortex(self, dt: float, entities: Sequence[object]) -> int:
        """Pull entities within vortex_radius gently toward the Black Coffee Sun."""
        pulled = 0
        for ent in entities:
            ex = float(getattr(ent, "x", 0.0))
            ey = float(getattr(ent, "y", 0.0))
            dx, dy = self.x - ex, self.y - ey
            dist = math.hypot(dx, dy)
            if 2.0 < dist <= self.vortex_radius:
                ent.x = ex + (dx / dist) * self.vortex_strength * dt  # type: ignore[attr-defined]
                ent.y = ey + (dy / dist) * self.vortex_strength * dt  # type: ignore[attr-defined]
                pulled += 1
        return pulled

    def unlock_ending(self, records: Records) -> bool:
        """Unlock true cosmic archive entry 'Die Kaffeepause der Ewigkeit'."""
        return records.discover("ending", ENDING_KEY)


@dataclass
class UrPerkolator:
    """Giant brass/bronze Abtei bell-tower apparatus for brewing the Black Coffee Sun (L04)."""

    x: float = 320.0
    y: float = 140.0
    universe_key: str = "abtei"
    essences: set[str] = field(default_factory=set)
    liquids: dict[str, int] = field(
        default_factory=lambda: {"fluessig_zeit": 0, "schutztonikum": 0}
    )
    ignited: bool = False

    def insert_essence(self, key: str) -> bool:
        if key not in ESSENCE_ORIGINS or key in self.essences:
            return False
        self.essences.add(key)
        return True

    def add_liquid(self, material_key: str, amount: int) -> int:
        if material_key not in self.liquids or amount <= 0:
            return 0
        cur = self.liquids[material_key]
        added = min(amount, max(0, 300 - cur))
        self.liquids[material_key] = cur + added
        return added

    def is_ready_to_ignite(self) -> bool:
        return (
            len(self.essences) == len(ESSENCE_KEYS)
            and self.liquids.get("fluessig_zeit", 0) >= REQUIRED_LIQUID_UNITS
            and self.liquids.get("schutztonikum", 0) >= REQUIRED_LIQUID_UNITS
        )

    def ignite(self, source: str) -> BlackCoffeeSun | None:
        """Ignite with plasma or high voltage once all 4 essences and 250+250 units are loaded."""
        if self.ignited or not self.is_ready_to_ignite():
            return None
        if source.lower() not in VALID_IGNITION_SOURCES:
            return None
        self.ignited = True
        return BlackCoffeeSun(x=self.x, y=self.y)
