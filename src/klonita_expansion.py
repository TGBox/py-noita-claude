"""Klonita Lab Assistant upgrades, backpack expansion & parallel-world encounters (Phase K)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from src import materials as mat
from src.body import Body
from src.flask import Flask
from src.klonita import KNOCKED_TIME, Klonita
from src.world import World

EXTINGUISHER_COOLDOWN = 20.0
EXTINGUISHER_CELLS = 50
SHOCK_COMB_COOLDOWN = 30.0
SHOCK_COMB_DURATION = 1.5
SHOCK_COMB_RADIUS = 96.0
BIO_LIGHT_RADIUS = 60.0


@dataclass(frozen=True)
class KlonitaUpgrade:
    key: str
    name_de: str
    description_de: str
    visual_de: str
    reaction_de: str
    cost_gold: int = 80


KLONITA_UPGRADES: dict[str, KlonitaUpgrade] = {
    "klonita_schwebe": KlonitaUpgrade(
        "klonita_schwebe",
        "Mini-Propeller",
        "Klonita schwebt per Propeller und fällt nie in Säure oder Abgründe.",
        "Kleiner Messing-Propeller auf dem Kopf.",
        "Guck mal Cloita, ich bin ein Hubschrauber! Wusch!",
        cost_gold=90,
    ),
    "klonita_packesel": KlonitaUpgrade(
        "klonita_packesel",
        "Labor-Ranzen",
        "Klonita trägt 2 zusätzliche Kolben- und 4 zusätzliche Proben-Slots.",
        "Klobiger Leder-Rucksack mit klirrenden Gläsern.",
        "Ich passe ganz doll auf, dass nichts zerbricht!",
        cost_gold=110,
    ),
    "klonita_feuerwehr": KlonitaUpgrade(
        "klonita_feuerwehr",
        "Lösch-Düse",
        "Spritzt bei Brand sofort 50 Einheiten Wasser auf Cloita (Abklingzeit 20 s).",
        "Kleiner Messing-Sprühkopf am Gürtel.",
        "Wasser marsch! Keine Sorge, ich lösche dich!",
        cost_gold=100,
    ),
    "klonita_funkenkamm": KlonitaUpgrade(
        "klonita_funkenkamm",
        "Statischer Schockkamm",
        "Alle 30 s lähmt Klonita einen nahen Angreifer für 1,5 s.",
        "Haare stehen lustig zu allen Seiten ab.",
        "Bitz! Das kitzelt in den Zehen!",
        cost_gold=120,
    ),
    "klonita_bioleuchte": KlonitaUpgrade(
        "klonita_bioleuchte",
        "Phosphor-Schleife",
        "Klonitas Haarschleife fluoresziert und erhellt 60 px im Umkreis.",
        "Türkis leuchtende Schleife.",
        "Ich leuchte wie ein Glühwürmchen! Hübsch, oder?",
        cost_gold=75,
    ),
}


@dataclass
class KlonitaBackpack:
    """Extra storage slots unlocked by klonita_packesel (2 flasks + 4 samples)."""

    max_flasks: int = 2
    max_samples: int = 4
    flasks: list[Flask | None] = field(default_factory=lambda: [None, None])
    samples: list[tuple[str, int] | None] = field(default_factory=lambda: [None, None, None, None])

    def add_flask(self, flask: Flask) -> bool:
        for idx, cur in enumerate(self.flasks):
            if cur is None:
                self.flasks[idx] = flask
                return True
        return False

    def pop_flask(self, slot: int) -> Flask | None:
        if 0 <= slot < len(self.flasks):
            got = self.flasks[slot]
            self.flasks[slot] = None
            return got
        return None

    def add_sample(self, key: str, amount: int = 1) -> bool:
        if amount <= 0:
            return False
        for idx, cur in enumerate(self.samples):
            if cur is not None and cur[0] == key:
                self.samples[idx] = (key, cur[1] + amount)
                return True
        for idx, cur in enumerate(self.samples):
            if cur is None:
                self.samples[idx] = (key, amount)
                return True
        return False

    def pop_sample(self, slot: int) -> tuple[str, int] | None:
        if 0 <= slot < len(self.samples):
            got = self.samples[slot]
            self.samples[slot] = None
            return got
        return None

    def quick_slot_labels(self) -> list[str]:
        labels = [
            f"[F{i + 1}] {f.label_de if f is not None else 'Leer'}"
            for i, f in enumerate(self.flasks)
        ]
        labels.extend(
            f"[P{i + 1}] {f'{s[0]}×{s[1]}' if s is not None else 'Leer'}"
            for i, s in enumerate(self.samples)
        )
        return labels

    def to_data(self) -> dict[str, object]:
        return {
            "flasks": [
                {"key": f.key, "amount": f.amount} if f is not None else None for f in self.flasks
            ],
            "samples": [list(s) if s is not None else None for s in self.samples],
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> KlonitaBackpack:
        bp = cls()
        if not data:
            return bp
        for idx, entry in enumerate(list(data.get("flasks", []))[: bp.max_flasks]):  # type: ignore[arg-type]
            if isinstance(entry, dict):
                bp.flasks[idx] = Flask(entry.get("key"), int(entry.get("amount", 0)))
        for idx, entry in enumerate(list(data.get("samples", []))[: bp.max_samples]):  # type: ignore[arg-type]
            if isinstance(entry, (list, tuple)) and len(entry) == 2:
                bp.samples[idx] = (str(entry[0]), int(entry[1]))
        return bp


@dataclass
class KlonitaAssistant:
    """Manages Klonita's equipped upgrades and active assistant actions (K01-K02)."""

    klonita: Klonita = field(default_factory=Klonita)
    equipped: set[str] = field(default_factory=set)
    backpack: KlonitaBackpack = field(default_factory=KlonitaBackpack)
    extinguisher_cd: float = 0.0
    shock_comb_cd: float = 0.0

    def equip(self, key: str) -> str | None:
        """Equip upgrade key (or return reaction line)."""
        spec = KLONITA_UPGRADES.get(key)
        if spec is None:
            return None
        self.equipped.add(key)
        return spec.reaction_de

    def has_upgrade(self, key: str) -> bool:
        return key in self.equipped

    @property
    def can_hover(self) -> bool:
        return "klonita_schwebe" in self.equipped

    @property
    def light_radius(self) -> float:
        return BIO_LIGHT_RADIUS if "klonita_bioleuchte" in self.equipped else 0.0

    @property
    def backpack_unlocked(self) -> bool:
        return "klonita_packesel" in self.equipped

    def knock_out(self) -> None:
        """Klonita is indestructible: enters 5-second knocked state instead of dying."""
        self.klonita.state = "knocked"
        self.klonita.knocked_timer = KNOCKED_TIME
        self.klonita.hp = 1.0

    def tick(
        self,
        dt: float,
        player: Body,
        world: World | None = None,
        enemies: Sequence[Body] = (),
    ) -> list[str]:
        """Advance assistant cooldowns, revive indestructible Klonita, and trigger assists."""
        events: list[str] = []
        self.extinguisher_cd = max(0.0, self.extinguisher_cd - dt)
        self.shock_comb_cd = max(0.0, self.shock_comb_cd - dt)

        # Indestructible companion always revives after KNOCKED_TIME (5 s)
        if self.klonita.state == "knocked":
            self.klonita.knocked_timer = max(0.0, self.klonita.knocked_timer - dt)
            if self.klonita.knocked_timer <= 0.0:
                self.klonita.state = "follow"
                self.klonita.hp = self.klonita.max_hp
                events.append("klonita_revived")
            return events

        # klonita_feuerwehr: douse burning Cloita with 50 water cells
        if (
            self.has_upgrade("klonita_feuerwehr")
            and self.extinguisher_cd <= 0.0
            and player.burning > 0.0
        ):
            player.burning = 0.0
            player.wet = max(player.wet, 5.0)
            self.extinguisher_cd = EXTINGUISHER_COOLDOWN
            if world is not None:
                px, py = int(player.center[0]), int(player.center[1])
                water_id = mat.MAT_ID.get("water", mat.WATER)
                placed = 0
                for dy in range(-5, 6):
                    for dx in range(-5, 6):
                        if placed >= EXTINGUISHER_CELLS:
                            break
                        if world.get(px + dx, py + dy) == mat.AIR:
                            world.set_cell(px + dx, py + dy, water_id)
                            placed += 1
            events.append("klonita_extinguished")

        # klonita_funkenkamm: shock nearest attacker for 1.5s stun
        if self.has_upgrade("klonita_funkenkamm") and self.shock_comb_cd <= 0.0:
            kx, ky = self.klonita.x, self.klonita.y
            nearest: Body | None = None
            best_d = SHOCK_COMB_RADIUS
            for enemy in enemies:
                body = getattr(enemy, "body", enemy)
                if body.dead:
                    continue
                dist = math.hypot(body.center[0] - kx, body.center[1] - ky)
                if dist <= best_d:
                    best_d = dist
                    nearest = body
            if nearest is not None:
                nearest.charged = max(nearest.charged, SHOCK_COMB_DURATION)
                nearest.frozen = max(nearest.frozen, SHOCK_COMB_DURATION)
                self.shock_comb_cd = SHOCK_COMB_COOLDOWN
                events.append("klonita_shock_comb")

        return events


@dataclass
class ParallelKlonita:
    """Confused parallel-world Klonita encounter pacified via Schutztonikum (K04)."""

    x: float
    y: float
    pacified: bool = False
    reward_given: bool = False

    def pacify_with_tonic(self, material_key: str) -> tuple[bool, str]:
        """Calm the confused clone peacefully using schutztonikum (never violent)."""
        if self.pacified:
            return True, "Huch? Zwei Cloitas! Das spart bestimmt Schreibarbeit!"
        if material_key != "schutztonikum":
            return False, "Das sieht gruselig aus... ich will mein eigenes Schutztonikum!"
        self.pacified = True
        self.reward_given = True
        return True, "Ooooh, das glitzert! Bist du auch eine Cloita? Wollen wir Freunde sein?"
