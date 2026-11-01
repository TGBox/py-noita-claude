"""Contract V7: Procedural limbs (Chain, Legs, Tentacle) and multi-part rigs (Cards A19, A20)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chain:
    segments: list[tuple[float, float]] = field(default_factory=list)
    spacing: float = 6.0

    def update(self, head_x: float, head_y: float) -> list[tuple[float, float]]:
        """Pull chain segments towards (head_x, head_y) keeping spacing distance."""
        raise NotImplementedError("Card A19")


@dataclass
class Legs:
    count: int = 4
    stride: float = 8.0
    step_height: float = 3.0
    phase: float = 0.0

    def update(
        self,
        dt: float,
        body_x: float,
        body_y: float,
        vx: float = 0.0,
    ) -> list[tuple[float, float, float, float]]:
        """Return (hip_x, hip_y, foot_x, foot_y) tuples for each leg."""
        raise NotImplementedError("Card A19")


@dataclass
class Tentacle:
    segments: int = 5
    length: float = 20.0
    amp: float = 4.0
    freq: float = 3.0
    phase: float = 0.0

    def points(self, root_x: float, root_y: float, time: float) -> list[tuple[float, float]]:
        """Return segments + 1 points starting at (root_x, root_y)."""
        raise NotImplementedError("Card A19")


@dataclass(frozen=True)
class PartSpec:
    key: str
    offset: tuple[float, float]
    z_order: int = 0
    sheet_name: str = ""
    bob_amp: float = 1.0
    bob_freq: float = 2.5
    destructible: bool = False


@dataclass(frozen=True)
class PartLayout:
    parts: tuple[PartSpec, ...] = ()


class ProcRig:
    def __init__(self, layout: PartLayout) -> None:
        self.layout: PartLayout = layout
        self.time: float = 0.0
        self.destroyed: set[str] = set()
        self.recoils: dict[str, float] = {}

    def update(self, dt: float, vx: float = 0.0, vy: float = 0.0, facing: int = 1) -> None:
        """Advance rig bobbing and decay part recoils."""
        raise NotImplementedError("Card A20")

    def recoil(self, part_key: str, amount: float) -> None:
        """Apply a temporary recoil displacement to part_key."""
        raise NotImplementedError("Card A20")

    def destroy_part(self, part_key: str) -> None:
        """Mark part_key as destroyed so it is omitted from world_parts."""
        raise NotImplementedError("Card A20")

    def world_parts(
        self,
        root_x: float,
        root_y: float,
        flip_x: bool = False,
    ) -> list[tuple[str, float, float, str]]:
        """Return z-ordered (part_key, wx, wy, sheet_name) for all non-destroyed parts."""
        raise NotImplementedError("Card A20")


RIG_LAYOUTS: dict[str, PartLayout] = {}

