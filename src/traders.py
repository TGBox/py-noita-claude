"""Contract V19: the 6 workshop traders, their offers and purchase rules (Cards E04, E05)."""

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
    blessing: str = ""


@dataclass(frozen=True)
class TraderSpec:
    key: str
    name: str
    home_universe: str
    greeting_de: str
    quirk_de: str
    category: str
    price_multiplier: float = 1.0
    flat_fee: int = 0


TRADERS: dict[str, TraderSpec] = {}


def traders_for_workshop(visited: list[str]) -> list[TraderSpec]:
    """Home traders of the (at most) two most recently visited universes, newest first."""
    raise NotImplementedError("Card E04")


def generate_offers(
    trader: TraderSpec,
    stage: int,
    rng: random.Random,
    *,
    price_factor: float = 1.0,
) -> list[TraderOffer]:
    """Generate 4 offers from the trader's category."""
    raise NotImplementedError("Card E04")


def buy_offer(
    run: Run,
    trader: TraderSpec,
    offer: TraderOffer,
    *,
    use_samples: bool = False,
) -> tuple[bool, str]:
    """Execute a purchase and return (ok, German message)."""
    raise NotImplementedError("Card E05")
