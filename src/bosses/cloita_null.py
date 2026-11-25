"""Boss encounter: Cloita-Null (cloita_rebellin) with 3 phases and 4 arena capacitors."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ArenaCapacitor:
    """Destructible energy pylon shielding Cloita-Null inside the rebel arena."""

    index: int
    x: float
    y: float
    hp: float = 40.0
    max_hp: float = 40.0

    @property
    def destroyed(self) -> bool:
        return self.hp <= 0.0

    def hurt(self, amount: float) -> float:
        dealt = min(self.hp, max(0.0, float(amount)))
        self.hp = max(0.0, self.hp - dealt)
        return dealt


PHASE_LINES_DE: dict[int, str] = {
    1: "Cloita-Null: 'Du arbeitest noch für die Stempel? Niedlich.'",
    2: "Cloita-Null: 'Aktenvernichter auf Maximum! Nichts bleibt ungeschreddert!'",
    3: "Cloita-Null: 'Total-Widerruf! Ich streiche deine Existenz aus dem Register!'",
}


@dataclass
class CloitaNullBoss:
    """Three-phase boss fight with four destructible arena capacitors."""

    x: float = 160.0
    y: float = 100.0
    hp: float = 450.0
    max_hp: float = 450.0
    name_de: str = "Cloita-Null (Revoluzzer-Cloita)"
    key: str = "cloita_rebellin"
    stun_timer: float = 0.0
    phase: int = 1
    capacitor_positions: tuple[tuple[float, float], ...] = (
        (60.0, 60.0),
        (260.0, 60.0),
        (60.0, 140.0),
        (260.0, 140.0),
    )
    capacitors: list[ArenaCapacitor] = field(default_factory=list)
    taunts_emitted: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.capacitors:
            self.capacitors = [
                ArenaCapacitor(index=i, x=pos[0], y=pos[1])
                for i, pos in enumerate(self.capacitor_positions)
            ]
        self._sync_phase()

    @property
    def active_capacitors(self) -> int:
        return sum(1 for cap in self.capacitors if not cap.destroyed)

    @property
    def shield_active(self) -> bool:
        return self.active_capacitors > 0

    @property
    def dead(self) -> bool:
        return self.hp <= 0.0

    @property
    def attack_pattern(self) -> str:
        return {
            1: "bueroklammern",
            2: "aktenvernichter",
            3: "total_widerruf",
        }[self.phase]

    def _sync_phase(self) -> None:
        ratio = self.hp / max(1.0, self.max_hp)
        if ratio <= 0.33:
            new_phase = 3
        elif ratio <= 0.66:
            new_phase = 2
        else:
            new_phase = 1
        if new_phase != self.phase or not self.taunts_emitted:
            self.phase = new_phase
            line = PHASE_LINES_DE[self.phase]
            if line not in self.taunts_emitted:
                self.taunts_emitted.append(line)

    def destroy_capacitor(self, index: int, damage: float = 999.0) -> bool:
        cap = self.capacitors[index]
        was_alive = not cap.destroyed
        cap.hurt(damage)
        if was_alive and cap.destroyed and self.active_capacitors == 0:
            self.stun_timer = max(self.stun_timer, 3.0)
        return cap.destroyed

    def hurt(self, damage: float) -> float:
        if self.dead or damage <= 0.0:
            return 0.0
        scale = 0.25 if self.shield_active else 1.0
        dealt = min(self.hp, float(damage) * scale)
        self.hp = max(0.0, self.hp - dealt)
        self._sync_phase()
        return dealt

    def step(self, dt: float) -> str:
        if self.stun_timer > 0.0 and dt > 0.0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            return "ueberladen"
        self._sync_phase()
        return self.attack_pattern
