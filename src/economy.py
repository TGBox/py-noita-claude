"""Contract V19: gold sources and prices after bible chapter 02 (Card E02)."""

from __future__ import annotations

import random

CREATURE_GOLD: dict[int, tuple[int, int]] = {1: (5, 10), 2: (10, 18), 3: (18, 30)}
BIG_CREATURE_GOLD: dict[int, int] = {1: 40, 2: 70, 3: 110}
BOSS_GOLD: dict[int, int] = {1: 200, 2: 350, 3: 500}
PILES_PER_UNIVERSE: tuple[int, int] = (6, 8)
MODULE_BASE: dict[int, int] = {1: 50, 2: 85, 3: 120}
PHYSIK_STAKE = 30
SCHIESS_STAKE = 20
ZAPF_PRICE = 10


def creature_gold(rank: int, rng: random.Random, *, big: bool = False) -> int:
    raise NotImplementedError("Card E02")


def mid_boss_gold(rank: int) -> int:
    raise NotImplementedError("Card E02")


def boss_gold(rank: int) -> int:
    raise NotImplementedError("Card E02")


def pile_gold(rank: int, rng: random.Random) -> int:
    raise NotImplementedError("Card E02")


def crate_gold(rank: int, rng: random.Random) -> int:
    raise NotImplementedError("Card E02")


def module_price(rarity_tier: int, stage: int, price_factor: float = 1.0) -> int:
    raise NotImplementedError("Card E02")


def weapon_price(stage: int, price_factor: float = 1.0) -> int:
    raise NotImplementedError("Card E02")


def fabricator_gold(rarity_tier: int, stage: int) -> int:
    raise NotImplementedError("Card E02")


def experiment_reroll_price(reroll_index: int) -> int:
    raise NotImplementedError("Card E02")
