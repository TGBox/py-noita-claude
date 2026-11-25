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
    """big: BIG_CREATURE_GOLD[rank]; sonst rng.randint(*CREATURE_GOLD[rank])."""
    if big:
        return BIG_CREATURE_GOLD[rank]
    low, high = CREATURE_GOLD[rank]
    return rng.randint(low, high)


def mid_boss_gold(rank: int) -> int:
    """Unter-Zwischenboss (spec.is_mid_boss): BIG_CREATURE_GOLD[rank]."""
    return BIG_CREATURE_GOLD[rank]


def boss_gold(rank: int) -> int:
    """Zwischengegner: BOSS_GOLD[rank]."""
    return BOSS_GOLD[rank]


def pile_gold(rank: int, rng: random.Random) -> int:
    """Goldhaufen: rng.randint(10, 40) * rank."""
    return rng.randint(10, 40) * rank


def crate_gold(rank: int, rng: random.Random) -> int:
    """Fundkiste: rng.randint(20, 60) * rank (dazu 1–3 Gegenstände, siehe loot.py)."""
    return rng.randint(20, 60) * rank


def module_price(rarity_tier: int, stage: int, price_factor: float = 1.0) -> int:
    """round(MODULE_BASE[rarity_tier] * (1 + 0.25 * stage) * price_factor)."""
    return round(MODULE_BASE[rarity_tier] * (1 + 0.25 * stage) * price_factor)


def weapon_price(stage: int, price_factor: float = 1.0) -> int:
    """round((160 + 70 * (stage - 1)) * price_factor)."""
    return round((160 + 70 * (stage - 1)) * price_factor)


def fabricator_gold(rarity_tier: int, stage: int) -> int:
    """round(module_price(rarity_tier, stage) * 0.7)."""
    return round(module_price(rarity_tier, stage) * 0.7)


def experiment_reroll_price(reroll_index: int) -> int:
    """100 * 2 ** reroll_index (100, 200, 400, …; Zähler gilt für den ganzen Lauf)."""
    return 100 * (2**reroll_index)
