"""Contract V7: Procedural limbs (Chain, Legs, Tentacle) and multi-part rigs (Cards A19, A20)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Chain:
    segments: list[tuple[float, float]] = field(default_factory=list)
    spacing: float = 6.0

    def update(self, head_x: float, head_y: float) -> list[tuple[float, float]]:
        """Pull chain segments towards (head_x, head_y) keeping spacing distance."""
        if not self.segments:
            return []

        # Start with the head position
        result = [(head_x, head_y)]

        # Process each segment
        for i in range(1, len(self.segments)):
            prev_x, prev_y = result[i - 1]
            seg_x, seg_y = self.segments[i]

            # Calculate vector from previous point to current segment
            dx = seg_x - prev_x
            dy = seg_y - prev_y

            # Calculate distance
            dist = math.hypot(dx, dy)

            # If distance is greater than spacing, move towards previous point
            if dist > self.spacing:
                ratio = self.spacing / dist
                new_x = prev_x + dx * ratio
                new_y = prev_y + dy * ratio
            else:
                new_x = seg_x
                new_y = seg_y

            result.append((new_x, new_y))

        return result


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
        result = []

        # Calculate step cycle
        step_cycle = self.phase + vx * 0.1

        for i in range(self.count):
            # Calculate leg position in cycle (alternating sides)
            leg_phase = step_cycle + (i * math.pi / 2)

            # Calculate foot position along stride
            foot_offset = math.sin(leg_phase) * self.stride / 2

            # Calculate hip position
            hip_x = body_x + foot_offset
            hip_y = body_y

            # Calculate foot position with step height
            foot_y_offset = math.sin(leg_phase + math.pi / 2) * self.step_height
            foot_x = hip_x
            foot_y = hip_y + foot_y_offset

            result.append((hip_x, hip_y, foot_x, foot_y))

        return result


@dataclass
class Tentacle:
    segments: int = 5
    length: float = 20.0
    amp: float = 4.0
    freq: float = 3.0
    phase: float = 0.0

    def points(self, root_x: float, root_y: float, time: float) -> list[tuple[float, float]]:
        """Return segments + 1 points starting at (root_x, root_y)."""
        result = [(root_x, root_y)]

        # Calculate segment length
        seg_length = self.length / self.segments

        for i in range(self.segments):
            # Calculate position along tentacle
            pos = (i + 1) * seg_length

            # Calculate wave pattern
            wave_offset = math.sin(pos * self.freq + time * self.freq + self.phase) * self.amp

            # Calculate point position
            x = root_x
            y = root_y + pos

            # Apply wave offset
            x += wave_offset

            result.append((x, y))

        return result


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
        self.time += dt

        # Decay recoils
        for key in list(self.recoils.keys()):
            self.recoils[key] *= 0.9  # Simple decay
            if abs(self.recoils[key]) < 0.01:
                del self.recoils[key]

    def recoil(self, part_key: str, amount: float) -> None:
        """Apply a temporary recoil displacement to part_key."""
        self.recoils[part_key] = amount

    def destroy_part(self, part_key: str) -> None:
        """Mark part_key as destroyed so it is omitted from world_parts."""
        self.destroyed.add(part_key)

    def world_parts(
        self,
        root_x: float,
        root_y: float,
        flip_x: bool = False,
    ) -> list[tuple[str, float, float, str]]:
        """Return z-ordered (part_key, wx, wy, sheet_name) for all non-destroyed parts."""
        result = []

        # Process parts in z-order
        for part_spec in sorted(self.layout.parts, key=lambda p: p.z_order):
            if part_spec.key in self.destroyed:
                continue

            # Apply offset and flip if needed
            offset_x, offset_y = part_spec.offset
            if flip_x:
                offset_x = -offset_x

            wx = root_x + offset_x
            wy = root_y + offset_y

            # Add bobbing effect
            if part_spec.bob_amp > 0:
                bob_offset = math.sin(self.time * part_spec.bob_freq) * part_spec.bob_amp
                wy += bob_offset

            result.append((part_spec.key, wx, wy, part_spec.sheet_name))

        return result


RIG_LAYOUTS: dict[str, PartLayout] = {
    "weltenherz": PartLayout(
        parts=(
            PartSpec(key="core", offset=(0.0, 0.0), z_order=1, sheet_name="weltenherz"),
            PartSpec(key="ventricle_left", offset=(-16.0, 4.0), z_order=0, sheet_name="weltenherz", bob_amp=2.0),
            PartSpec(key="ventricle_right", offset=(16.0, 4.0), z_order=0, sheet_name="weltenherz", bob_amp=2.0),
        )
    ),
    "oberstempler": PartLayout(
        parts=(
            PartSpec(key="body", offset=(0.0, 0.0), z_order=1, sheet_name="oberstempler"),
            PartSpec(key="stamp_arm", offset=(18.0, 6.0), z_order=2, sheet_name="oberstempler", bob_amp=3.0),
        )
    ),
    "mutter_glibber": PartLayout(
        parts=(
            PartSpec(key="nucleus", offset=(0.0, 0.0), z_order=1, sheet_name="mutter_glibber"),
            PartSpec(key="blob_orbit", offset=(-12.0, 10.0), z_order=0, sheet_name="mutter_glibber", bob_amp=2.5),
        )
    ),
    "dj_myzel": PartLayout(
        parts=(
            PartSpec(key="cap", offset=(0.0, -8.0), z_order=1, sheet_name="dj_myzel"),
            PartSpec(key="turntable", offset=(0.0, 12.0), z_order=2, sheet_name="dj_myzel", bob_amp=1.5),
        )
    ),
    "ameisenkoenigin": PartLayout(
        parts=(
            PartSpec(key="thorax", offset=(0.0, 0.0), z_order=1, sheet_name="ameisenkoenigin"),
            PartSpec(key="abdomen", offset=(-20.0, 4.0), z_order=0, sheet_name="ameisenkoenigin", bob_amp=1.0),
            PartSpec(key="mandibles", offset=(16.0, -2.0), z_order=2, sheet_name="ameisenkoenigin", bob_amp=2.0),
        )
    ),
    "abt_kieme": PartLayout(
        parts=(
            PartSpec(key="robe", offset=(0.0, 0.0), z_order=1, sheet_name="abt_kieme"),
            PartSpec(key="miter", offset=(0.0, -16.0), z_order=2, sheet_name="abt_kieme", bob_amp=1.0),
        )
    ),
    "trampolinwal": PartLayout(
        parts=(
            PartSpec(key="whale_body", offset=(0.0, 0.0), z_order=1, sheet_name="trampolinwal"),
        )
    ),
    "kirchenkrake": PartLayout(
        parts=(
            PartSpec(key="kraken_bell", offset=(0.0, 0.0), z_order=1, sheet_name="kirchenkrake"),
        )
    ),
}
