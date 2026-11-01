"""Universes as data (work package T3).

Every universe is one :class:`Universe` record (fields from bible chapter 03); the six
MVP universes live in ``catalog.py``. ``plan.py`` builds a run from them: six universes
in three ranks, a portal choice between two offers before each one, mid-bosses in their
home universes and one evil self at the end.
"""

from src.universes.catalog import BY_KEY, EVIL_SELVES, MID_BOSSES, UNIVERSES
from src.universes.model import RANK_LOOT, RANK_POWER, RANKS, Region, Universe
from src.universes.plan import Offer, RunPlan

__all__ = [
    "BY_KEY",
    "EVIL_SELVES",
    "MID_BOSSES",
    "RANKS",
    "RANK_LOOT",
    "RANK_POWER",
    "UNIVERSES",
    "Offer",
    "Region",
    "RunPlan",
    "Universe",
]
