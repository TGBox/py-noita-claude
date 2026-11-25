"""Repeat-offense Authority boss: Der Chef-Prüfer (Phase L02)."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class ChefPruefer:
    """Authority repeat-offense boss with frontal projectile-dissolving aura (L02)."""

    x: float
    y: float
    hp: float = 500.0
    max_hp: float = 500.0
    facing: int = 1
    aura_radius: float = 48.0
    gold_reward: int = 350

    @property
    def dead(self) -> bool:
        return self.hp <= 0.0

    def dissolves_projectile(self, px: float, py: float, is_acid: bool = False) -> bool:
        """True if frontal aura dissolves non-acid projectiles within aura_radius."""
        if is_acid:
            return False
        if math.hypot(px - self.x, py - self.y) > self.aura_radius:
            return False
        return (px - self.x) * self.facing >= 0

    def take_hit(self, amount: float, attacker_x: float, damage_type: str = "normal") -> float:
        """Vulnerable from behind or to acid; frontal non-acid hits are neutralized."""
        is_from_behind = (attacker_x - self.x) * self.facing < 0
        if not is_from_behind and damage_type != "acid":
            return 0.0
        dmg = max(0.0, amount)
        self.hp = max(0.0, self.hp - dmg)
        return dmg

    def subpoena_beam(self, target: object) -> None:
        """Deal beam damage and apply status_pfaendung on target."""
        if hasattr(target, "hurt"):
            target.hurt(22.0, "Prüfungs-Strahl (Chef-Prüfer)")  # type: ignore[attr-defined]
        target.status_pfaendung = 10.0  # type: ignore[attr-defined]
