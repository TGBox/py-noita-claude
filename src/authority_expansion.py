"""Workshop Sabotage Alarm, S.O.K.O. Paragraf & Pfaendung debuff (Phase L01)."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.bosses.chef_pruefer import ChefPruefer

SABOTAGE_STATIONS: tuple[str, ...] = (
    "ws_haendler",
    "ws_shredder",
    "ws_archiv",
    "ws_kessel",
    "ws_liege",
    "ws_fabrikator",
)
ALARM_BANNER_DE = (
    "VERLETZUNG DER ARBEITSSTÄTTENRICHTLINIE § 4 ABSATZ 2: DIE BEHÖRDE IST ERZÜRNT!"
)
PFAENDUNG_FLUX_FACTOR = 1.40
PFAENDUNG_DURATION = 10.0


def effective_flux_cost(base_cost: float, pfaendung_timer: float) -> float:
    """Return flux cost multiplied by +40% while status_pfaendung is active."""
    return base_cost * PFAENDUNG_FLUX_FACTOR if pfaendung_timer > 0.0 else base_cost


@dataclass
class SokoParagraf:
    """Elite Authority investigator spawned next to the workshop portal on sabotage (L01)."""

    x: float
    y: float
    hp: float = 350.0
    max_hp: float = 350.0
    facing: int = 1
    front_shield: bool = True
    gold_reward: int = 200
    badge_drop: bool = True

    @property
    def dead(self) -> bool:
        return self.hp <= 0.0

    def take_hit(self, amount: float, attacker_x: float, damage_type: str = "normal") -> tuple[bool, float]:
        """Reflect frontal hits when front_shield is active; return (reflected, damage_taken)."""
        is_frontal = (attacker_x - self.x) * self.facing >= 0
        if self.front_shield and is_frontal and damage_type != "acid":
            return True, 0.0
        dmg = max(0.0, amount)
        self.hp = max(0.0, self.hp - dmg)
        return False, dmg

    def subpoena_hit(self, target: object) -> float:
        """Apply status_pfaendung (+40% flux cost for 10s) and direct damage."""
        if hasattr(target, "hurt"):
            target.hurt(15.0, "Mahnbescheid (S.O.K.O. Paragraf)")  # type: ignore[attr-defined]
        target.status_pfaendung = PFAENDUNG_DURATION  # type: ignore[attr-defined]
        return PFAENDUNG_DURATION


@dataclass
class WorkshopAlarmManager:
    """Tracks workshop station sabotage without ever making bedrock breakable (L01-L02)."""

    alarm_active: bool = False
    offenses: int = 0
    banner_de: str = ""
    light_blink_phase: float = 0.0
    active_boss: SokoParagraf | ChefPruefer | None = None
    history: list[str] = field(default_factory=list)

    def report_station_sabotage(
        self,
        station_key: str,
        portal_pos: tuple[float, float] = (578.0, 186.0),
    ) -> SokoParagraf | ChefPruefer | None:
        """Trigger high alarm on station sabotage; spawn SokoParagraf then ChefPruefer."""
        if station_key not in SABOTAGE_STATIONS:
            return None
        self.alarm_active = True
        self.offenses += 1
        self.banner_de = ALARM_BANNER_DE
        self.history.append(station_key)
        px, py = portal_pos
        if self.offenses == 1:
            self.active_boss = SokoParagraf(x=px, y=py)
        else:
            self.active_boss = ChefPruefer(x=px, y=py)
        return self.active_boss

    def tick(self, dt: float) -> bool:
        """Advance flashing red warning lights (returns True on high pulse half-second)."""
        if not self.alarm_active:
            return False
        self.light_blink_phase += dt
        return int(self.light_blink_phase) % 2 == 0
