"""Contract V19: 6 trader personalities, offer generation, and purchase rules (Cards E04, E05)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class TraderOffer:
    kind: str
    key: str
    gold_cost: int
    sample_cost: tuple[tuple[str, int], ...] = ()
    blessed: bool = False


@dataclass(frozen=True)
class TraderSpec:
    key: str
    name: str
    home_universe: str
    greeting_de: str
    quirk_de: str
    price_multiplier: float = 1.0
    flat_fee: int = 0


TRADERS: dict[str, TraderSpec] = {}


def pick_trader_for_universe(universe_key: str, rng: random.Random) -> TraderSpec:
    """Pick the home trader (60% chance) or a random trader from TRADERS."""
    raise NotImplementedError("Card E04")


def generate_offers(
    trader: TraderSpec,
    depth: int,
    rng: random.Random,
    *,
    price_factor: float = 1.0,
    universe_sample_key: str = "probe_rost",
) -> list[TraderOffer]:
    """Generate 4 offers tailored to trader's quirk and assortment."""
    raise NotImplementedError("Card E04")


def buy_offer(
    run: Run,
    trader: TraderSpec,
    offer: TraderOffer,
    *,
    use_samples: bool = False,
) -> tuple[bool, str]:
    """Execute purchase of offer from trader on run, enforcing all trader quirks."""
    raise NotImplementedError("Card E05")

