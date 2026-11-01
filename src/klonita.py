"""Contract V21: Klonita companion state machine, 4 assists, and 3 quirks (Cards F12, F13)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run

KLONITA_STATES: tuple[str, ...] = (
    "dismissed",
    "follow",
    "assist",
    "quirk",
    "knocked",
)

AUTO_TRIGGERS: tuple[str, ...] = (
    "enter_universe",
    "player_low_hp",
    "boss_spawn",
    "wanted_high",
    "event_start",
)


@dataclass
class Klonita:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    hp: float = 60.0
    max_hp: float = 60.0
    state: str = "follow"
    knocked_timer: float = 0.0
    quirk_used_in_universe: bool = False
    cooldowns: dict[str, float] = field(
        default_factory=lambda: {
            "shield": 0.0,
            "snack": 0.0,
            "spark": 0.0,
            "cleanse": 0.0,
        }
    )
    facing: int = 1

    def toggle(self) -> str:
        """Toggle between 'dismissed' and 'follow' (unless 'knocked') and return new state."""
        raise NotImplementedError("Card F12")

    def on_trigger(self, trigger: str, run: Run) -> str | None:
        """React to one of AUTO_TRIGGERS, return to 'follow', and return German dialogue line."""
        raise NotImplementedError("Card F12")

    def take_damage(self, amount: float) -> bool:
        """Apply damage; enter 5.0s 'knocked' state instead of dying when hp <= 0."""
        raise NotImplementedError("Card F12")

    def trigger_quirk(self, kind: str, run: Run) -> bool:
        """Execute a once-per-universe quirk ('shiny_poke', 'loud_sneeze', 'sample_nibble')."""
        raise NotImplementedError("Card F13")

    def update(self, dt: float, run: Run) -> None:
        """Update follow movement, cooldowns, assist actions, and quirks."""
        raise NotImplementedError("Card F12")

    def to_data(self) -> dict[str, object]:
        return {
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "hp": round(self.hp, 2),
            "max_hp": round(self.max_hp, 2),
            "state": self.state,
            "knocked_timer": round(self.knocked_timer, 3),
            "quirk_used_in_universe": self.quirk_used_in_universe,
            "cooldowns": dict(self.cooldowns),
            "facing": self.facing,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Klonita:
        if not data:
            return cls()
        return cls(
            x=float(data.get("x", 0.0)),  # type: ignore[arg-type]
            y=float(data.get("y", 0.0)),  # type: ignore[arg-type]
            hp=float(data.get("hp", 60.0)),  # type: ignore[arg-type]
            max_hp=float(data.get("max_hp", 60.0)),  # type: ignore[arg-type]
            state=str(data.get("state", "follow")),
            knocked_timer=float(data.get("knocked_timer", 0.0)),  # type: ignore[arg-type]
            quirk_used_in_universe=bool(data.get("quirk_used_in_universe", False)),
            facing=int(data.get("facing", 1)),  # type: ignore[arg-type]
        )

