"""Static grain texture: which colour variant each world cell uses."""

from __future__ import annotations

from src import native
from src.materials import VARIANTS


def make_grain(width: int, height: int, seed: int = 7) -> bytearray:
    """Return one colour variant (0..VARIANTS-1) per cell (smooth, organic noise)."""
    grain = bytearray(width * height)
    native.grain(native.byte_view(grain), width, height, seed, VARIANTS)
    return grain
