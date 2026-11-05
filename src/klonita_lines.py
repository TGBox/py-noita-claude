"""Contract V21: Klonita German dialogue lines database (Card F11)."""

from __future__ import annotations

import random

LINES: dict[str, tuple[str, ...]] = {}

# Minimum number of lines per topic (Contract V21 section 4, bible 08 "Textmengen").
LINE_COUNTS: dict[str, int] = {}


def line_for(topic: str, rng: random.Random) -> str:
    """Return a deterministic German dialogue line for topic."""
    raise NotImplementedError("Card F11")

