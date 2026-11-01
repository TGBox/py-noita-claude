"""Universes as data (work package T3).

Every universe is one :class:`Universe` record (fields from bible chapter 03); the six
MVP universes live in ``catalog.py``. ``plan.py`` builds a run from them: six universes
in three ranks, a portal choice between two offers before each one, mid-bosses in their
home universes and one evil self at the end.
"""

from src.universes.catalog import (
    ALL_UNIVERSES,
    BY_KEY,
    EVIL_SELVES,
    MID_BOSSES,
    POOL_UNIVERSES,
    UNIVERSE_ALIASES,
    UNIVERSES,
)
from src.universes.model import RANK_LOOT, RANK_POWER, RANKS, Region, Universe
from src.universes.plan import Offer, RunPlan, UniversePlan

__all__ = [
    "ALL_UNIVERSES",
    "BY_KEY",
    "EVIL_SELVES",
    "MID_BOSSES",
    "POOL_UNIVERSES",
    "RANKS",
    "RANK_LOOT",
    "RANK_POWER",
    "UNIVERSES",
    "UNIVERSE_ALIASES",
    "Offer",
    "Region",
    "RunPlan",
    "Universe",
    "UniversePlan",
]
