"""Contract V8: Color ramps and universe/entity palettes (Card A21)."""

from __future__ import annotations

from dataclasses import dataclass

OUTLINE_DARK: tuple[int, int, int, int] = (18, 14, 24, 255)


@dataclass(frozen=True)
class PaletteRamp:
    shadow: tuple[int, int, int, int]
    mid: tuple[int, int, int, int]
    light: tuple[int, int, int, int]
    highlight: tuple[int, int, int, int]
    rim: tuple[int, int, int, int]


def make_ramp(base_rgb: tuple[int, int, int]) -> PaletteRamp:
    """Create a 5-stop PaletteRamp from base_rgb with monotonically increasing brightness."""
    raise NotImplementedError("Card A21")


UNIVERSE_PALETTES: dict[str, dict[str, PaletteRamp]] = {}
ENTITY_PALETTES: dict[str, dict[str, PaletteRamp]] = {}

