"""Contract V11: Sample registry and stack constants (Card A04)."""

from __future__ import annotations

from dataclasses import dataclass

SAMPLE_SLOTS: int = 12
SAMPLE_STACK: int = 99


@dataclass(frozen=True)
class Sample:
    key: str
    name: str
    universe_key: str
    tier: int
    color: tuple[int, int, int]
    description: str


SAMPLES: dict[str, Sample] = {}

