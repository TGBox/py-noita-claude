"""Loot: procedurally grown augmentations and loose building blocks in the world."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from src.materials import AIR, STOPS_PROJECTILE
from src.perks import PERK_BY_KEY
from src.spells import BLOCKS, CATALOG, Block, Category
from src.wand import WandSpec
from src.world import World

ITEM_GRAVITY = 400.0
PICKUP_RANGE = 14.0  # px between player centre and item

ADJECTIVES = ("Pulsierende", "Eitrige", "Vernarbte", "Zuckende", "Blasse", "Schwärende", "Hohle")
NOUNS = ("Drüse", "Ranke", "Klaue", "Zyste", "Wucherung", "Sehne", "Rippe")

# How often each category shows up as loose loot / inside generated wands.
CATEGORY_WEIGHTS = {
    Category.FORM: 4.0,
    Category.MODIFIER: 3.0,
    Category.PAYLOAD: 2.5,
    Category.TRIGGER: 1.5,
}


def random_block(rng: random.Random, category: Category | None = None) -> str:
    """Pick a block key, weighted by category."""
    pool = [b for b in BLOCKS if category is None or b.category is category]
    weights = [CATEGORY_WEIGHTS[b.category] for b in pool]
    return rng.choices(pool, weights)[0].key


def generate_wand(rng: random.Random, level: int = 1) -> WandSpec:
    """Grow a random augmentation. Deeper levels give bigger, stronger wands.

    Stats trade off against each other like in Noita: lots of slots or a short
    recharge are paid for with less mana or a slower cast.
    """
    level = max(1, level)
    capacity = min(12, rng.randint(2, 4) + rng.randint(0, level))
    casts = 2 if rng.random() < 0.12 + 0.05 * level else 1
    shuffle = rng.random() < max(0.15, 0.65 - 0.1 * level)
    budget = 1.0 + 0.35 * (level - 1)
    roll = rng.random()  # where the budget goes: mana vs. speed
    mana_max = round((80 + 120 * roll) * budget)
    mana_regen = round((25 + 45 * rng.random()) * budget)
    cast_delay = round(max(0.03, (0.35 - 0.25 * (1 - roll)) / budget + rng.uniform(-0.05, 0.05)), 2)
    recharge = round(max(0.1, rng.uniform(0.3, 1.2) / budget + 0.08 * capacity), 2)
    if shuffle:  # shuffling wands are compensated with better stats
        mana_regen = round(mana_regen * 1.2)
        recharge = round(recharge * 0.8, 2)

    filled = rng.randint(1, max(1, capacity - 1))
    keys = [random_block(rng, Category.FORM)]
    keys += [random_block(rng) for _ in range(filled - 1)]
    rng.shuffle(keys)
    name = f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)}"
    return WandSpec(
        name,
        tuple(keys),
        mana_max=mana_max,
        mana_regen=mana_regen,
        cast_delay=cast_delay,
        recharge=recharge,
        spread=round(rng.uniform(0.0, 0.12), 3),
        casts=casts,
        shuffle=shuffle,
        capacity=capacity,
    )


@dataclass
class Pickup:
    """An item lying in the world: either a wand or a single block."""

    x: float
    y: float
    wand: WandSpec | None = None
    block: str | None = None
    pearls: int = 0  # blood pearls (currency), collected on touch
    perk: str | None = None  # a perk offered at the sanctum altar
    price: int = 0  # >0: shop item that must be bought
    floating: bool = False  # shop items and perks hover in place
    vy: float = 0.0
    age: float = 0.0

    @property
    def label_de(self) -> str:
        if self.perk is not None:
            perk = PERK_BY_KEY[self.perk]
            return f"Perk: {perk.name_de} - {perk.description_de}"
        if self.pearls:
            return f"{self.pearls} Blutperlen"
        if self.wand is not None:
            return f"Augmentation: {self.wand.name_de}"
        block: Block = CATALOG[self.block or ""]
        return f"{block.category.value}: {block.name_de}"

    def update(self, world: World, dt: float) -> None:
        """Fall until resting on something solid (items float on liquids)."""
        self.age += dt
        if self.floating:
            return
        self.vy = min(self.vy + ITEM_GRAVITY * dt, 300.0)
        steps = int(abs(self.vy * dt)) + 1
        for _ in range(steps):
            ny = self.y + self.vy * dt / steps
            if STOPS_PROJECTILE[world.get(int(self.x), int(ny))]:
                self.vy = 0.0
                return
            self.y = ny


def nearest_pickup(pickups: list[Pickup], x: float, y: float) -> Pickup | None:
    """Closest item that needs a key press (pearls are collected automatically)."""
    best, best_distance = None, PICKUP_RANGE
    for item in pickups:
        if item.pearls:
            continue
        distance = math.hypot(item.x - x, item.y - y)
        if distance <= best_distance:
            best, best_distance = item, distance
    return best


def place_loot(
    world: World,
    rng: random.Random,
    avoid: tuple[int, int],
    wands: int,
    blocks: int,
    level: int = 1,
    safe_radius: float = 60,
) -> list[Pickup]:
    """Scatter loot on cave floors. One block always lies next to the spawn."""
    items: list[Pickup] = [Pickup(avoid[0] + 18, avoid[1], block=random_block(rng, Category.FORM))]
    wanted = [("wand", wands), ("block", blocks)]
    for kind, count in wanted:
        placed = 0
        for _attempt in range(count * 60):
            if placed >= count:
                break
            x = rng.randint(20, world.width - 20)
            y = rng.randint(20, world.height - 20)
            if world.get(x, y) != AIR or math.hypot(x - avoid[0], y - avoid[1]) < safe_radius:
                continue
            while world.get(x, y + 1) == AIR and y < world.height - 3:
                y += 1
            if kind == "wand":
                items.append(Pickup(x, y, wand=generate_wand(rng, level)))
            else:
                items.append(Pickup(x, y, block=random_block(rng)))
            placed += 1
    return items


BLOCK_PRICES = {
    Category.FORM: 60,
    Category.MODIFIER: 50,
    Category.PAYLOAD: 45,
    Category.TRIGGER: 80,
}


def block_price(key: str, level: int) -> int:
    return round(BLOCK_PRICES[CATALOG[key].category] * (1 + 0.25 * (level - 1)))


def wand_price(level: int) -> int:
    return 160 + 70 * (level - 1)


def scatter_pearls(
    world: World, rng: random.Random, avoid: tuple[int, int], piles: int
) -> list[Pickup]:
    """Small piles of blood pearls lying on cave floors."""
    items: list[Pickup] = []
    for _attempt in range(piles * 60):
        if len(items) >= piles:
            break
        x = rng.randint(20, world.width - 20)
        y = rng.randint(20, world.height - 20)
        if world.get(x, y) != AIR or math.hypot(x - avoid[0], y - avoid[1]) < 40:
            continue
        items.append(Pickup(x, y, pearls=rng.randint(8, 25)))
    return items
