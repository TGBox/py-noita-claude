"""Contract V5: Sprite-sheet metadata and frame animator (Card A17)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AnimSpec:
    row: int
    frames: int
    fps: float = 8.0
    loop: bool = True
    next_anim: str = "idle"


@dataclass(frozen=True)
class GlowPoint:
    offset: tuple[int, int]
    color: tuple[int, int, int]
    radius: int = 12


@dataclass(frozen=True)
class SheetMeta:
    frame_size: tuple[int, int]
    anchor: tuple[int, int]
    anims: dict[str, AnimSpec] = field(default_factory=dict)
    glow: tuple[GlowPoint, ...] = ()


def load_sheet_meta(json_path: Path) -> SheetMeta:
    """Load SheetMeta from a JSON sidecar file."""
    raise NotImplementedError("Card A17")


class Animator:
    def __init__(self, meta: SheetMeta, initial: str = "idle") -> None:
        self.meta: SheetMeta = meta
        self.state: str = initial
        self.frame_index: int = 0
        self.timer: float = 0.0
        self.finished: bool = False

    def play(self, state: str, *, restart: bool = False) -> None:
        """Switch to animation state (ignored if already in state unless restart=True)."""
        raise NotImplementedError("Card A17")

    def update(self, dt: float) -> None:
        """Advance animation timer and frame_index by dt seconds."""
        raise NotImplementedError("Card A17")

    def frame_rect(self) -> tuple[int, int, int, int]:
        """Return (x, y, w, h) pixel rectangle on the sprite sheet."""
        raise NotImplementedError("Card A17")

