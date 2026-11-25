"""Phase N gadgets, pocket bureaucrat companion, and cockroach escape protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

GADGET_KEY = "G"

GADGET_SPECS: dict[str, dict[str, Any]] = {
    "gadget_tauchkapsel": {
        "name_de": "Multiversums-Tauchkapsel",
        "description_de": "Notfall-Kapsel mit Schutzschirm und Sicherheitsblase gegen Amts- und Weltuntergänge.",
        "max_charges": 2,
        "cooldown": 3.0,
        "duration": 3.5,
        "quote_de": "Die Welt brennt. Zeit für den Notausgang.",
    },
    "gadget_amts_imp": {
        "name_de": "Amts-Imp (Taschenbürokrat)",
        "description_de": "Sammelt Gold in der Nähe ein, stempelt Belege ab und erhöht nebenbei den Fahndungsdruck.",
        "max_charges": 3,
        "cooldown": 2.0,
        "duration": 12.0,
        "quote_de": "Quittung liegt bei. Ihre Akte wächst leider mit.",
    },
    "gadget_kolben_libelle": {
        "name_de": "Kolben-Libelle",
        "description_de": "Tarnt die Alchemistin, lädt Flugenergie auf und macht den nächsten Hinterhalt kritisch.",
        "max_charges": 2,
        "cooldown": 4.0,
        "duration": 4.0,
        "quote_de": "Leise wie eine Feder, giftig wie ein Mahnbescheid.",
    },
    "gadget_schwungscheibe": {
        "name_de": "Büro-Schwungscheibe",
        "description_de": "Kinetische Bumerang-Diskusscheibe, die Gegner durchschlägt und zurückkehrt.",
        "max_charges": 3,
        "cooldown": 1.5,
        "duration": 1.2,
        "quote_de": "Umlaufmappe mit Überschall.",
    },
    "mod_schaben_flucht": {
        "name_de": "Schaben-Flucht",
        "description_de": "Verwandelt die Spielfigur kurzzeitig in eine flinke Küchenschabe zur Notfallflucht.",
        "max_charges": 1,
        "cooldown": 8.0,
        "duration": 5.0,
        "quote_de": "Ich überlebe auch einen Meteoriten. Nur die Miete nicht.",
    },
}

GADGET_KEYS: tuple[str, ...] = tuple(GADGET_SPECS.keys())


@dataclass(frozen=True)
class Gadget:
    """Static definition of an equippable Phase 3 gadget."""

    key: str
    name_de: str
    description_de: str
    max_charges: int
    cooldown: float
    duration: float
    quote_de: str

    @classmethod
    def from_key(cls, key: str) -> Gadget:
        if key not in GADGET_SPECS:
            raise KeyError(f"Unbekanntes Gadget: {key}")
        spec = GADGET_SPECS[key]
        return cls(
            key=key,
            name_de=str(spec["name_de"]),
            description_de=str(spec["description_de"]),
            max_charges=int(spec["max_charges"]),
            cooldown=float(spec["cooldown"]),
            duration=float(spec["duration"]),
            quote_de=str(spec["quote_de"]),
        )


@dataclass
class GadgetState:
    """Mutable charge and cooldown state for one gadget."""

    key: str
    charges: int
    max_charges: int
    cooldown_timer: float = 0.0
    active_timer: float = 0.0

    def step(self, dt: float) -> None:
        if self.cooldown_timer > 0.0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)
        if self.active_timer > 0.0:
            self.active_timer = max(0.0, self.active_timer - dt)

    def recharge(self, amount: int = 1) -> int:
        before = self.charges
        self.charges = min(self.max_charges, self.charges + max(0, amount))
        return self.charges - before


@dataclass
class AmtsImp:
    """Autonomous pocket bureaucrat that collects nearby gold and ticks Wanted pressure."""

    x: float
    y: float
    lifetime: float = 12.0
    pickup_radius: float = 48.0
    wanted_per_second: float = 0.05
    collected_gold: int = 0
    stamped_docs: int = 0
    active: bool = True

    def step(
        self,
        dt: float,
        player: Any,
        pickups: list[Any] | None = None,
        wanted: Any | None = None,
    ) -> int:
        if not self.active or dt <= 0.0:
            return 0
        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.active = False
            return 0

        # Hover gently beside the player.
        px = float(getattr(player, "x", self.x))
        py = float(getattr(player, "y", self.y))
        self.x += (px + 12.0 - self.x) * min(1.0, 5.0 * dt)
        self.y += (py - 8.0 - self.y) * min(1.0, 5.0 * dt)

        gained = 0
        if pickups is not None:
            remaining: list[Any] = []
            for item in pickups:
                ix = float(item.get("x", 0.0) if isinstance(item, dict) else getattr(item, "x", 0.0))
                iy = float(item.get("y", 0.0) if isinstance(item, dict) else getattr(item, "y", 0.0))
                dx = ix - self.x
                dy = iy - self.y
                if dx * dx + dy * dy <= self.pickup_radius * self.pickup_radius:
                    val = int(
                        item.get("amount", item.get("value", 1))
                        if isinstance(item, dict)
                        else getattr(item, "amount", getattr(item, "value", 1))
                    )
                    gained += max(1, val)
                    self.stamped_docs += 1
                else:
                    remaining.append(item)
            pickups[:] = remaining
            self.collected_gold += gained
            if gained and hasattr(player, "gold"):
                player.gold = int(getattr(player, "gold", 0)) + gained

        if wanted is not None and hasattr(wanted, "add"):
            delta = self.wanted_per_second * dt
            if delta > 0.0:
                wanted.add(delta, "Amts-Imp Gebührenprüfung")
        return gained


@dataclass
class FlywheelDisc:
    """Kinetic office flywheel disc that pierces enemies and returns."""

    x: float
    y: float
    vx: float
    vy: float = 0.0
    damage: float = 35.0
    lifetime: float = 1.2
    returning: bool = False
    hits: int = 0
    active: bool = True

    def step(self, dt: float, player: Any, targets: list[Any] | None = None) -> list[Any]:
        if not self.active or dt <= 0.0:
            return []
        self.lifetime -= dt
        if self.lifetime <= 0.6:
            self.returning = True
        if self.returning:
            px = float(getattr(player, "x", self.x))
            py = float(getattr(player, "y", self.y))
            dx = px - self.x
            dy = py - self.y
            dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
            self.vx = (dx / dist) * 240.0
            self.vy = (dy / dist) * 240.0
            if dist <= 10.0:
                self.active = False
        self.x += self.vx * dt
        self.y += self.vy * dt

        hit_targets: list[Any] = []
        if targets:
            for target in targets:
                tx = float(target.get("x", 0.0) if isinstance(target, dict) else getattr(target, "x", 0.0))
                ty = float(target.get("y", 0.0) if isinstance(target, dict) else getattr(target, "y", 0.0))
                if (tx - self.x) ** 2 + (ty - self.y) ** 2 <= 16.0**2:
                    self.hits += 1
                    hit_targets.append(target)
                    if isinstance(target, dict):
                        target["hp"] = float(target.get("hp", 50.0)) - self.damage
                    elif hasattr(target, "hurt"):
                        target.hurt(self.damage)
                    elif hasattr(target, "hp"):
                        target.hp = max(0.0, float(target.hp) - self.damage)
        if self.lifetime <= 0.0:
            self.active = False
        return hit_targets


def consume_ambush_crit(player: Any, base_damage: float, multiplier: float = 2.5) -> float:
    """Apply and consume a Kolben-Libelle ambush critical multiplier if armed."""
    if getattr(player, "ambush_crit_ready", False):
        player.ambush_crit_ready = False
        return float(base_damage) * multiplier
    return float(base_damage)


def trigger_cockroach_escape(player: Any, duration: float = 5.0) -> dict[str, Any]:
    """Transform the player into the resilient cockroach escape state."""
    player.is_cockroach = True
    player.cockroach_timer = max(float(getattr(player, "cockroach_timer", 0.0)), duration)
    player.stealth_timer = max(float(getattr(player, "stealth_timer", 0.0)), min(duration, 3.0))
    if hasattr(player, "hp"):
        player.hp = max(10.0, float(player.hp))
    return {
        "activated": True,
        "form": "kuechenschabe_cloita",
        "duration": duration,
        "message_de": GADGET_SPECS["mod_schaben_flucht"]["quote_de"],
    }


def maybe_trigger_cockroach_escape(player: Any, incoming_damage: float = 0.0) -> bool:
    """Prevent fatal collapse once by triggering Schaben-Flucht if near death."""
    hp = float(getattr(player, "hp", 100.0))
    max_hp = float(getattr(player, "max_hp", 100.0))
    if hp - incoming_damage <= max(1.0, max_hp * 0.2):
        trigger_cockroach_escape(player)
        return True
    return False


@dataclass
class GadgetManager:
    """Manages equipped Phase 3 gadget, charges, cooldowns, and active helpers."""

    equipped: str | None = None
    states: dict[str, GadgetState] = field(default_factory=dict)
    active_imps: list[AmtsImp] = field(default_factory=list)
    active_discs: list[FlywheelDisc] = field(default_factory=list)
    keybind: str = GADGET_KEY

    def __post_init__(self) -> None:
        for key in GADGET_KEYS:
            if key not in self.states:
                spec = GADGET_SPECS[key]
                max_c = int(spec["max_charges"])
                self.states[key] = GadgetState(key=key, charges=max_c, max_charges=max_c)

    def equip(self, key: str, player: Any | None = None) -> Gadget:
        gadget = Gadget.from_key(key)
        self.equipped = key
        if player is not None:
            player.active_gadget = key
        return gadget

    def restock_all(self) -> None:
        for st in self.states.values():
            st.charges = st.max_charges
            st.cooldown_timer = 0.0

    def activate(
        self,
        player: Any,
        *,
        world: Any | None = None,
        direction: int = 1,
        key: str | None = None,
    ) -> dict[str, Any]:
        target_key = key or self.equipped or getattr(player, "active_gadget", None)
        if not target_key or target_key not in self.states:
            return {"activated": False, "reason_de": "Kein Gadget ausgerüstet."}
        spec = GADGET_SPECS[target_key]
        state = self.states[target_key]
        if state.charges <= 0:
            return {"activated": False, "reason_de": "Keine Ladungen mehr verfügbar."}
        if state.cooldown_timer > 0.0:
            return {
                "activated": False,
                "reason_de": f"Gadget lädt noch nach ({state.cooldown_timer:.1f}s).",
            }

        state.charges -= 1
        state.cooldown_timer = float(spec["cooldown"])
        state.active_timer = float(spec["duration"])
        player.active_gadget = target_key

        effect: dict[str, Any] = {
            "activated": True,
            "gadget": target_key,
            "name_de": spec["name_de"],
            "quote_de": spec["quote_de"],
            "charges_left": state.charges,
        }

        if target_key == "gadget_tauchkapsel":
            if hasattr(player, "shield_hp"):
                player.shield_hp = max(float(getattr(player, "shield_hp", 0.0)), 30.0)
            player.stealth_timer = max(float(getattr(player, "stealth_timer", 0.0)), 2.5)
            if hasattr(player, "energy") and hasattr(player, "energy_max"):
                player.energy = float(player.energy_max)
            effect["shield_hp"] = getattr(player, "shield_hp", 30.0)
            effect["capsule_radius"] = 12
            if world is not None and hasattr(world, "carve_circle"):
                world.carve_circle(int(getattr(player, "x", 0)), int(getattr(player, "y", 0)), 12)
        elif target_key == "gadget_amts_imp":
            imp = AmtsImp(
                x=float(getattr(player, "x", 0.0)) + 10.0,
                y=float(getattr(player, "y", 0.0)) - 6.0,
                lifetime=float(spec["duration"]),
            )
            self.active_imps.append(imp)
            effect["imp"] = imp
        elif target_key == "gadget_kolben_libelle":
            player.stealth_timer = max(float(getattr(player, "stealth_timer", 0.0)), float(spec["duration"]))
            player.ambush_crit_ready = True
            if hasattr(player, "energy") and hasattr(player, "energy_max"):
                player.energy = float(player.energy_max)
            if hasattr(player, "vy"):
                player.vy = min(float(player.vy), -110.0)
            effect["stealth_timer"] = player.stealth_timer
            effect["ambush_crit_ready"] = True
        elif target_key == "gadget_schwungscheibe":
            dir_sign = -1 if direction < 0 else 1
            disc = FlywheelDisc(
                x=float(getattr(player, "x", 0.0)),
                y=float(getattr(player, "y", 0.0)),
                vx=dir_sign * 220.0,
                lifetime=float(spec["duration"]),
            )
            self.active_discs.append(disc)
            effect["disc"] = disc
        elif target_key == "mod_schaben_flucht":
            esc = trigger_cockroach_escape(player, duration=float(spec["duration"]))
            effect.update(esc)

        return effect

    def update(
        self,
        dt: float,
        player: Any | None = None,
        *,
        pickups: list[Any] | None = None,
        wanted: Any | None = None,
        targets: list[Any] | None = None,
    ) -> None:
        for state in self.states.values():
            state.step(dt)
        if player is not None:
            for imp in self.active_imps:
                imp.step(dt, player, pickups=pickups, wanted=wanted)
            self.active_imps = [imp for imp in self.active_imps if imp.active]

            for disc in self.active_discs:
                disc.step(dt, player, targets=targets)
            self.active_discs = [disc for disc in self.active_discs if disc.active]
