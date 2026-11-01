"""Contract V19: Gold drop and shop pricing formulas (Card E02)."""

from __future__ import annotations

import random


def creature_gold(max_hp: float, depth: int, rng: random.Random) -> int:
    """Compute gold dropped by a regular creature."""
    raise NotImplementedError("Card E02")


def pile_gold(depth: int, rng: random.Random) -> int:
    """Compute gold in a world gold pile."""
    raise NotImplementedError("Card E02")


def crate_gold(depth: int, rng: random.Random) -> int:
    """Compute gold dropped by a loot crate."""
    raise NotImplementedError("Card E02")


def mid_boss_gold(depth: int) -> int:
    """Compute fixed gold dropped by a mid-boss (45 + 15 * depth)."""
    raise NotImplementedError("Card E02")


def module_price(rarity_tier: int, depth: int, price_factor: float = 1.0) -> int:
    """Compute shop price for a spell module of rarity_tier (1..3)."""
    raise NotImplementedError("Card E02")


def weapon_price(wand_tier: int, depth: int, price_factor: float = 1.0) -> int:
    """Compute shop price for a wand of wand_tier (1..3)."""
    raise NotImplementedError("Card E02")


def reroll_price(reroll_index: int, price_factor: float = 1.0) -> int:
    """Compute cost for shop/workbench reroll index (0, 1, 2, ...)."""
    raise NotImplementedError("Card E02")

