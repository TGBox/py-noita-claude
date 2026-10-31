"""The player's augmentations and loose building blocks, and how they are rearranged."""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.wand import Wand, WandSpec

MAX_WANDS = 4
BAG_SIZE = 36  # 3 rows of 12 in the inventory screen


@dataclass(frozen=True)
class SlotRef:
    """A place a block can sit: a wand slot or a bag slot."""

    kind: str  # "wand" or "bag"
    index: int  # bag index, or wand slot index
    wand: int = 0  # which wand (for kind == "wand")


class Inventory:
    def __init__(self, wands: list[WandSpec], rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.wands: list[Wand] = [Wand(spec, self.rng) for spec in wands[:MAX_WANDS]]
        self.bag: list[str | None] = [None] * BAG_SIZE
        self.active = 0

    @property
    def wand(self) -> Wand:
        return self.wands[self.active]

    def select(self, index: int) -> None:
        if 0 <= index < len(self.wands):
            self.active = index

    def cycle(self, step: int) -> None:
        if self.wands:
            self.active = (self.active + step) % len(self.wands)

    # ---------------------------------------------------------------- pickup

    def add_block(self, key: str) -> bool:
        """Put a block into the first free bag slot. False if the bag is full."""
        for index, slot in enumerate(self.bag):
            if slot is None:
                self.bag[index] = key
                return True
        return False

    def add_wand(self, spec: WandSpec) -> WandSpec | None:
        """Take a wand. With all slots full, the active wand is swapped out and returned."""
        new = Wand(spec, self.rng)
        if len(self.wands) < MAX_WANDS:
            self.wands.append(new)
            self.active = len(self.wands) - 1
            return None
        old = self.wands[self.active]
        self.wands[self.active] = new
        return _spec_of(old)

    # ----------------------------------------------------------------- edit

    def get(self, ref: SlotRef) -> str | None:
        if ref.kind == "bag":
            return self.bag[ref.index]
        return self.wands[ref.wand].slots[ref.index]

    def move(self, source: SlotRef, target: SlotRef, *, edit_wands: bool = True) -> bool:
        """Move (or swap) the block at ``source`` to ``target``. False if invalid.

        Without ``edit_wands`` (outside a sanctum) only the bag can be rearranged.
        """
        if source == target or not self._valid(source) or not self._valid(target):
            return False
        if not edit_wands and "wand" in (source.kind, target.kind):
            return False
        moving, other = self.get(source), self.get(target)
        if moving is None:
            return False
        self._put(target, moving)
        self._put(source, other)
        return True

    def put(self, ref: SlotRef, key: str) -> bool:
        """Place ``key`` into a slot, replacing what was there (sandbox spell book)."""
        if not self._valid(ref):
            return False
        self._put(ref, key)
        return True

    def take(self, ref: SlotRef) -> str | None:
        """Remove and return the block at ``ref`` (to drop it into the world)."""
        if not self._valid(ref):
            return None
        key = self.get(ref)
        if key is not None:
            self._put(ref, None)
        return key

    def remove_wand(self, index: int) -> WandSpec | None:
        """Take a wand out of the inventory (one always stays). Returns its contents."""
        if len(self.wands) <= 1 or not 0 <= index < len(self.wands):
            return None
        wand = self.wands.pop(index)
        if self.active >= len(self.wands) or self.active > index:
            self.active = max(0, self.active - 1)
        return _spec_of(wand)

    def move_wand(self, source: int, target: int) -> bool:
        """Swap two wands' places in the inventory (the active wand follows)."""
        count = len(self.wands)
        if source == target or not (0 <= source < count and 0 <= target < count):
            return False
        wands = self.wands
        wands[source], wands[target] = wands[target], wands[source]
        if self.active in (source, target):
            self.active = target if self.active == source else source
        return True

    def _valid(self, ref: SlotRef) -> bool:
        if ref.kind == "bag":
            return 0 <= ref.index < len(self.bag)
        if ref.kind == "wand" and 0 <= ref.wand < len(self.wands):
            return 0 <= ref.index < self.wands[ref.wand].capacity
        return False

    def _put(self, ref: SlotRef, key: str | None) -> None:
        if ref.kind == "bag":
            self.bag[ref.index] = key
            return
        wand = self.wands[ref.wand]
        slots = list(wand.slots)
        slots[ref.index] = key
        wand.set_slots(slots)


def spec_of(wand: Wand) -> WandSpec:
    return _spec_of(wand)


def _spec_of(wand: Wand) -> WandSpec:
    """Current contents of a wand as a spec (to drop it back into the world)."""
    spec = wand.spec
    return WandSpec(
        spec.name_de,
        tuple(key for key in wand.slots if key is not None),
        mana_max=spec.mana_max,
        mana_regen=spec.mana_regen,
        cast_delay=spec.cast_delay,
        recharge=spec.recharge,
        spread=spec.spread,
        casts=spec.casts,
        shuffle=spec.shuffle,
        capacity=wand.capacity,
    )
