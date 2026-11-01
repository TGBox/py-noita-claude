"""Contract V14: Deterministic headless playtest bot (Cards D15, D16)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BotReport:
    universe_key: str
    seed: int
    ticks: int = 0
    reached_exit: bool = False
    died: bool = False
    kills: int = 0
    gold_collected: int = 0
    samples_collected: int = 0
    stuck_ratio: float = 0.0
    min_hp_ratio: float = 1.0
    errors: list[str] = field(default_factory=list)


def run_bot(
    universe_key: str,
    seed: int = 1,
    max_seconds: float = 120.0,
) -> BotReport:
    """Run deterministic bot in a single universe and return BotReport."""
    raise NotImplementedError("Card D15")


def run_full(
    seed: int = 1,
    max_seconds_per_stage: float = 120.0,
) -> list[BotReport]:
    """Run deterministic bot across a 5-universe sequence and return reports."""
    raise NotImplementedError("Card D16")

