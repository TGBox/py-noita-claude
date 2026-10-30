"""Wands: decks of building blocks that are drawn in order when casting.

Casting draws blocks until a form (projectile) completes a group; a wand with
``casts > 1`` draws several groups per cast. Modifiers and payloads drawn on the
way apply to that form; a trigger makes the *next* group the projectile's payload;
a multicast block draws several groups at once. Blocks the wand cannot pay for are
skipped. When the deck runs out, the wand recharges (and reshuffles if it is a
shuffling wand). Every block is drawn at most once per cast, so no deck can loop
forever.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.spells import CATALOG, Block, Category

MULTICAST_SPREAD = 0.14  # radians between the shots of one multicast


@dataclass(frozen=True)
class WandSpec:
    """Static description of a wand (an augmentation)."""

    name_de: str
    blocks: tuple[str, ...]
    mana_max: float = 150.0
    mana_regen: float = 50.0  # per second
    cast_delay: float = 0.15  # seconds between casts
    recharge: float = 0.5  # seconds after the deck ran out
    spread: float = 0.03  # random aim deviation in radians
    casts: int = 1  # groups drawn per cast ("Zauber pro Wurf")
    shuffle: bool = False  # reshuffle the deck on every recharge
    capacity: int = 0  # number of slots; 0 means exactly as many as blocks


@dataclass
class Shot:
    """One projectile to spawn, with the blocks that shape it and its payload."""

    form: Block
    modifiers: tuple[Block, ...] = ()
    children: list[Shot] = field(default_factory=list)
    angle_offset: float = 0.0


PRESETS: tuple[WandSpec, ...] = (
    WandSpec(
        "Funkendrüse",
        ("beschleunigung", "funke", "funke", "funke"),
        mana_max=120, mana_regen=60, cast_delay=0.08, recharge=0.35,
    ),
    WandSpec(
        "Gallenwerfer",
        ("sekret_talg", "gallenblase", "sekret_feuer", "klumpen"),
        mana_max=200, mana_regen=50, cast_delay=0.2, recharge=0.6,
    ),
    WandSpec(
        "Nervennadel",
        ("nerv_aufprall", "nadel", "doppel", "sekret_saeure", "klumpen", "sekret_saeure", "klumpen"),
        mana_max=200, mana_regen=45, cast_delay=0.15, recharge=0.8,
    ),
    WandSpec(
        "Sporenschleuder",
        ("zielsuche", "nerv_zeit", "funke", "doppel", "sekret_sporen", "klumpen", "sekret_feuer", "funke"),
        mana_max=250, mana_regen=55, cast_delay=0.25, recharge=1.0,
    ),
)  # fmt: skip


class _Draw:
    """Draws blocks from a deck for one cast and adds up their cost."""

    def __init__(
        self, blocks: tuple[Block, ...], order: list[int], start: int, mana: float
    ) -> None:
        self.blocks = blocks
        self.order = order
        self.index = start
        self.available = mana
        self.drawn = 0
        self.mana = 0.0
        self.delay = 0.0
        self.wrapped = False

    def next(self) -> Block | None:
        """Draw the next affordable block; unaffordable ones are skipped."""
        while self.drawn < len(self.blocks):
            if self.index >= len(self.blocks):
                self.wrapped = True
                self.index = 0
            block = self.blocks[self.order[self.index]]
            self.index += 1
            self.drawn += 1
            if self.mana + block.mana > self.available:
                continue
            self.mana += block.mana
            self.delay += block.cast_delay
            return block
        return None

    def group(self, inherited: tuple[Block, ...] = ()) -> list[Shot]:
        """Draw until a form completes a group; returns its shot(s)."""
        modifiers = list(inherited)
        while (block := self.next()) is not None:
            if block.category is Category.FORM:
                has_trigger = any(m.category is Category.TRIGGER for m in modifiers)
                children = self.group() if has_trigger else []
                return [Shot(block, tuple(modifiers), children)]
            if block.multicast:
                shots: list[Shot] = []
                for index in range(block.multicast):
                    offset = (index - (block.multicast - 1) / 2) * MULTICAST_SPREAD
                    for shot in self.group(tuple(modifiers)):
                        shot.angle_offset += offset
                        shots.append(shot)
                return shots
            modifiers.append(block)
        return []


class Wand:
    """Runtime state of one wand: deck position, mana and timers."""

    def __init__(self, spec: WandSpec, rng: random.Random | None = None) -> None:
        self.spec = spec
        self.rng = rng or random.Random()
        capacity = max(spec.capacity, len(spec.blocks))
        self.slots: list[str | None] = [*spec.blocks, *[None] * (capacity - len(spec.blocks))]
        self.mana = spec.mana_max
        self.cooldown = 0.0
        self.recharge_left = 0.0
        self.set_slots(self.slots)

    @property
    def capacity(self) -> int:
        return len(self.slots)

    def set_slots(self, slots: list[str | None]) -> None:
        """Replace the wand's contents (empty slots are ``None``) and restart its deck."""
        unknown = [key for key in slots if key is not None and key not in CATALOG]
        if unknown:
            raise ValueError(f"unknown blocks in {self.spec.name_de}: {unknown}")
        if len(slots) != len(self.slots):
            raise ValueError("slot count must not change")
        self.slots = list(slots)
        self.blocks: tuple[Block, ...] = tuple(CATALOG[k] for k in self.slots if k is not None)
        self.order = list(range(len(self.blocks)))
        if self.spec.shuffle:
            self.rng.shuffle(self.order)
        self.index = 0

    @property
    def next_block(self) -> int | None:
        """Index (into ``blocks``) of the block that will be drawn next."""
        if self.recharging or not self.blocks:
            return None
        return self.order[self.index % len(self.blocks)]

    @property
    def ready(self) -> bool:
        return self.cooldown <= 0 and self.recharge_left <= 0

    @property
    def recharging(self) -> bool:
        return self.recharge_left > 0

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        self.recharge_left = max(0.0, self.recharge_left - dt)
        self.mana = min(self.spec.mana_max, self.mana + self.spec.mana_regen * dt)

    def cast(self) -> list[Shot]:
        """Draw the next group. Returns no shots if the wand is busy or lacks mana."""
        if not self.ready or not self.blocks:
            return []
        draw = _Draw(self.blocks, self.order, self.index, self.mana)
        shots: list[Shot] = []
        for _ in range(max(1, self.spec.casts)):
            shots += draw.group()
        if not shots:  # nothing castable (or affordable) left in the deck
            self._start_recharge()
            return []
        self.mana -= draw.mana
        self.index = draw.index
        self.cooldown = self.spec.cast_delay + draw.delay
        if draw.wrapped or self.index >= len(self.blocks):
            self._start_recharge()
        return shots

    def _start_recharge(self) -> None:
        self.index = 0
        self.recharge_left = self.spec.recharge
        if self.spec.shuffle:
            self.rng.shuffle(self.order)
