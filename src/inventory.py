"""The player's augmentations and loose building blocks, and how they are rearranged."""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.wand import Wand, WandSpec

MAX_WANDS = 4
# (key, German label) of the ways the bag can be sorted
SORT_MODES = (
    ("art", "Art"),
    ("schaden", "Schaden"),
    ("mana", "Mana"),
    ("name", "Name"),
    ("anzahl", "Anzahl"),
)
BAG_SIZE = 48  # 4 rows of 12 in the inventory screen; equal blocks stack in one slot


@dataclass(frozen=True)
class SlotRef:
    """A place a block can sit: a wand slot or a bag slot."""

    kind: str  # "wand" or "bag"
    index: int  # bag index, or wand slot index
    wand: int = 0  # which wand (for kind == "wand")


class Inventory:
    def __init__(
        self, wands: list[WandSpec] | None = None, rng: random.Random | None = None
    ) -> None:
        self.rng = rng or random.Random()
        self.wands: list[Wand] = [Wand(spec, self.rng) for spec in (wands or [])[:MAX_WANDS]]
        self.bag: list[str | None] = [None] * BAG_SIZE
        self.counts: list[int] = [0] * BAG_SIZE  # stack size per bag slot (0 = empty)
        self.samples: list[tuple[str, int] | None] = [None] * 12  # sample slots (Contract V11)
        self.active = 0

    def add_sample(self, key: str, count: int = 1) -> int:
        """Stack sample key (up to 99 per slot across 12 slots) and return added count (Card A04)."""
        raise NotImplementedError("Card A04")

    def sample_count(self, key: str) -> int:
        """Return total count of sample key across all sample slots (Card A04)."""
        raise NotImplementedError("Card A04")

    def total_samples(self) -> dict[str, int]:
        """Return {sample_key: total_count} for all carried samples (Card A04)."""
        raise NotImplementedError("Card A04")

    def take_samples(self, cost: dict[str, int]) -> bool:
        """Atomically deduct sample counts if all requirements in cost are met (Card A04)."""
        raise NotImplementedError("Card A04")

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

    def add_block(self, key: str, count: int = 1) -> bool:
        """Put blocks into the bag: onto a stack of the same block, else into a free slot."""
        index = self._slot_for(key)
        if index is None:
            return False
        self.counts[index] = (self.count(SlotRef("bag", index)) if self.bag[index] else 0) + count
        self.bag[index] = key
        return True

    def can_add(self, key: str) -> bool:
        return self._slot_for(key) is not None

    def _slot_for(self, key: str) -> int | None:
        if key in self.bag:
            return self.bag.index(key)
        return self.bag.index(None) if None in self.bag else None

    def count(self, ref: SlotRef) -> int:
        """How many blocks sit in a slot (bag slots stack)."""
        if not self._valid(ref) or self.get(ref) is None:
            return 0
        return max(1, self.counts[ref.index]) if ref.kind == "bag" else 1

    def set_bag(self, keys: list[str | None], counts: list[int] | None = None) -> None:
        """Fill the bag (from a save); stacks of equal blocks are merged."""
        self.bag = [None] * BAG_SIZE
        self.counts = [0] * BAG_SIZE
        for index, key in enumerate(keys):
            if key is None:
                continue
            amount = counts[index] if counts and index < len(counts) else 1
            self.add_block(key, max(1, int(amount)))

    def sort_bag(self, mode: str = "art") -> None:
        """Merge stacks and order the bag by ``mode`` (see ``SORT_MODES``)."""
        from src.spells import CATALOG, Category

        order = list(Category)
        totals: dict[str, int] = {}
        for key, amount in zip(self.bag, self.counts):
            if key is not None:
                totals[key] = totals.get(key, 0) + max(1, amount)

        def kind(key: str) -> int:
            return order.index(CATALOG[key].category)

        def damage(key: str) -> float:
            b = CATALOG[key]
            return b.damage * max(1, b.pellets) + b.blast * 3 + b.damage_bonus + b.blast_bonus * 3

        keys_of = {
            "art": lambda k: (kind(k), CATALOG[k].name_de),
            "schaden": lambda k: (-damage(k), kind(k), CATALOG[k].name_de),
            "mana": lambda k: (CATALOG[k].mana, kind(k), CATALOG[k].name_de),
            "name": lambda k: CATALOG[k].name_de.lower(),
            "anzahl": lambda k: (-totals[k], kind(k), CATALOG[k].name_de),
        }
        keys = sorted(totals, key=keys_of.get(mode, keys_of["art"]))
        self.bag = [None] * BAG_SIZE
        self.counts = [0] * BAG_SIZE
        for index, key in enumerate(keys):
            self.bag[index], self.counts[index] = key, totals[key]

    def quick_move(self, ref: SlotRef, *, edit_wands: bool) -> bool:
        """Right click / double click: wand slot -> bag, bag -> the wand in hand."""
        if not edit_wands or not self._valid(ref):
            return False
        key = self.get(ref)
        if key is None:
            return False
        if ref.kind == "wand":
            if not self.add_block(key):
                return False
            self._put(ref, None)
            return True
        wand = self.wand
        if None not in wand.slots:
            return False
        target = SlotRef("wand", list(wand.slots).index(None), self.active)
        self.take(ref)
        self._put(target, key)
        return True

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
        if source.kind == "bag" and target.kind == "bag":
            if moving == other:  # merge two stacks
                self.counts[target.index] = self.count(target) + self.count(source)
                self.bag[source.index], self.counts[source.index] = None, 0
            else:  # swap whole stacks
                a, b = source.index, target.index
                self.bag[a], self.bag[b] = self.bag[b], self.bag[a]
                self.counts[a], self.counts[b] = self.counts[b], self.counts[a]
            return True
        if source.kind == "bag":  # one block from a stack into a wand
            stacked = self.count(source) > 1
            if other is not None and stacked and not self.can_add(other):
                return False  # no room in the bag for the block it would replace
            self.take(source)
            self._put(target, moving)
            if other is not None:
                if self.bag[source.index] is None:
                    self._put(source, other)
                else:
                    self.add_block(other)
            return True
        if (
            target.kind == "bag"
            and other is not None
            and (other == moving or self.count(target) > 1)
        ):
            self._put(source, None)  # onto a stack: it joins (or finds its own stack)
            if other == moving:
                self.counts[target.index] = self.count(target) + 1
            else:
                self.add_block(moving)
            return True
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
        """Remove one block from ``ref`` and return it (a stack shrinks by one)."""
        if not self._valid(ref):
            return None
        key = self.get(ref)
        if key is None:
            return None
        if ref.kind == "bag" and self.count(ref) > 1:
            self.counts[ref.index] -= 1
        else:
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
            self.counts[ref.index] = 0 if key is None else 1
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
