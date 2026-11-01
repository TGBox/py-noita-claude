"""The route of a run through the multiverse (bible chapter 02, "Aufbau eines Laufs").

Six universes in three ranks, a workshop stop before each: the portal frame offers
two universes and Cloita picks one. The first universe of a rank is a *free* slot (two
random unvisited universes; choosing a mid-boss home there means no boss fight there),
the second is the *boss* slot (the unvisited homes of this rank's mid-bosses). Every
universe is visited at most once; the seed decides the offers and the evil self.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from src.universes.catalog import BY_KEY, EVIL_SELVES, MID_BOSSES
from src.universes.model import RANKS, Universe

SLOTS_PER_RANK = 2
SLOTS = RANKS * SLOTS_PER_RANK
FREE_OFFERS = 2


@dataclass(frozen=True)
class Offer:
    """One proposal in the portal frame."""

    universe: str
    rank: int  # 1-3
    boss: str | None = None  # mid-boss waiting at the anchor point

    @property
    def data(self) -> Universe:
        return BY_KEY[self.universe]


class RunPlan:
    """Which universes a run has visited and what the portal offers next."""

    def __init__(
        self,
        seed: int,
        pool: tuple[str, ...] | None = None,
        bosses: dict[int, tuple[tuple[str, str], ...]] | None = None,
    ) -> None:
        self.seed = seed
        self.pool = tuple(pool) if pool is not None else tuple(BY_KEY)
        self.bosses = bosses if bosses is not None else MID_BOSSES
        self.chosen: list[Offer] = []
        self.evil_self = random.Random(seed).choice(EVIL_SELVES)
        homes = [home for rank in self.bosses.values() for _, home in rank]
        if len(set(homes)) != len(homes) or not set(homes) <= set(self.pool):
            raise ValueError("every mid-boss needs its own home universe in the pool")
        if len(self.pool) < SLOTS:
            raise ValueError(f"a run needs at least {SLOTS} universes")

    # -------------------------------------------------------------- state

    @property
    def slot(self) -> int:
        """Index of the next universe (0-5); 6 means: on to the evil self."""
        return len(self.chosen)

    @property
    def finished(self) -> bool:
        return self.slot >= SLOTS

    @property
    def rank(self) -> int:
        return min(self.slot, SLOTS - 1) // SLOTS_PER_RANK + 1

    @property
    def boss_slot(self) -> bool:
        return self.slot % SLOTS_PER_RANK == SLOTS_PER_RANK - 1

    @property
    def visited(self) -> list[str]:
        return [offer.universe for offer in self.chosen]

    @property
    def current(self) -> Offer | None:
        return self.chosen[-1] if self.chosen else None

    # -------------------------------------------------------------- offers

    def _open_homes(self, rank: int, taken: set[str]) -> list[tuple[str, str]]:
        return [(boss, home) for boss, home in self.bosses.get(rank, ()) if home not in taken]

    def _keeps_plan_possible(self, universe: str) -> bool:
        """After visiting ``universe`` every remaining boss slot still has a home."""
        taken = {*self.visited, universe}
        return all(self._open_homes(rank, taken) for rank in range(self.rank, RANKS + 1))

    def offers(self) -> list[Offer]:
        """What the portal frame shows now (the same every time for the same state)."""
        if self.finished:
            return []
        rank = self.rank
        taken = set(self.visited)
        if self.boss_slot:
            return [Offer(home, rank, boss) for boss, home in self._open_homes(rank, taken)]
        candidates = [u for u in self.pool if u not in taken and self._keeps_plan_possible(u)]
        rng = random.Random(self.seed * 1009 + self.slot)
        picked = rng.sample(candidates, min(FREE_OFFERS, len(candidates)))
        return [Offer(u, rank) for u in picked]

    def choose(self, choice: int | str) -> Offer:
        """Take one of the current offers (by index or universe key)."""
        offers = self.offers()
        if isinstance(choice, int):
            if not 0 <= choice < len(offers):
                raise ValueError("no such offer")
            offer = offers[choice]
        else:
            matches = [o for o in offers if o.universe == choice]
            if not matches:
                raise ValueError(f"{choice} is not on offer")
            offer = matches[0]
        self.chosen.append(offer)
        return offer

    # -------------------------------------------------------------- saving

    def to_data(self) -> dict[str, Any]:
        return {"seed": self.seed, "pool": list(self.pool), "chosen": self.visited}

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> RunPlan:
        """Rebuild a plan by replaying the saved choices (raises ValueError if they no
        longer fit, e.g. after the universe pool changed)."""
        try:
            plan = cls(int(data["seed"]), tuple(data["pool"]))
            for universe in data["chosen"]:
                plan.choose(str(universe))
        except (KeyError, TypeError) as error:
            raise ValueError("broken run plan") from error
        return plan


UniversePlan = RunPlan
