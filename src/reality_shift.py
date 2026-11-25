"""Palette-bound Global Reality Shift system (Phase I04)."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from src import materials as mat
from src.world import World

SHIFT_COOLDOWN = 180.0
MAX_SHIFTS_PER_RUN = 5
VISION_DURATION = 10.0


@dataclass(frozen=True)
class ShiftRecord:
    """Record of one reality shift applied during a run."""

    source: str
    target: str
    timestamp: float
    cells_changed: int


@dataclass
class RealityShiftManager:
    """Manages palette-bound reality shifts with cooldown and per-run cap."""

    cooldown: float = SHIFT_COOLDOWN
    max_shifts: int = MAX_SHIFTS_PER_RUN
    shifts: list[ShiftRecord] = field(default_factory=list)
    material_aliases: dict[str, str] = field(default_factory=dict)
    vision_timer: float = 0.0
    last_shift_time: float = -SHIFT_COOLDOWN

    def can_shift(self, elapsed_time: float) -> bool:
        """True if cooldown elapsed and per-run shift limit not yet reached."""
        if len(self.shifts) >= self.max_shifts:
            return False
        if not self.shifts:
            return True
        return (elapsed_time - self.last_shift_time) >= self.cooldown

    def trigger_shift(
        self,
        world: World,
        rng: random.Random,
        *,
        active_keys: Sequence[str] | None = None,
        held_flask_key: str | None = None,
        elapsed_time: float = 0.0,
        source_override: str | None = None,
        target_override: str | None = None,
    ) -> ShiftRecord | None:
        """Permanently transmute one active-palette material into another across world."""
        if not self.can_shift(elapsed_time):
            return None
        palette_keys = active_keys if active_keys is not None else mat.KEYS
        mutable = [k for k in palette_keys if k not in ("air", "bedrock")]
        if len(mutable) < 2:
            return None

        source = source_override if source_override in mutable else None
        if source is None:
            if held_flask_key in mutable and rng.random() < 0.5:
                source = held_flask_key
            else:
                source = rng.choice(mutable)

        targets = [k for k in mutable if k != source]
        target = target_override if target_override in targets else rng.choice(targets)

        src_id = mat.MAT_ID.get(source)
        dst_id = mat.MAT_ID.get(target)
        if src_id is None or dst_id is None:
            return None

        changed = 0
        grid = world.grid
        for idx, val in enumerate(grid):
            if val == src_id:
                grid[idx] = dst_id
                changed += 1

        self.material_aliases[source] = target
        mat.REALITY_ALIASES[source] = target
        self.vision_timer = VISION_DURATION
        self.last_shift_time = elapsed_time
        record = ShiftRecord(source, target, elapsed_time, changed)
        self.shifts.append(record)
        return record

    def tick(self, dt: float) -> None:
        self.vision_timer = max(0.0, self.vision_timer - dt)

    def to_data(self) -> dict[str, object]:
        return {
            "shifts": [
                {
                    "source": s.source,
                    "target": s.target,
                    "timestamp": s.timestamp,
                    "cells_changed": s.cells_changed,
                }
                for s in self.shifts
            ],
            "material_aliases": dict(self.material_aliases),
            "vision_timer": self.vision_timer,
            "last_shift_time": self.last_shift_time,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> RealityShiftManager:
        if not data:
            return cls()
        mgr = cls()
        mgr.material_aliases = {
            str(k): str(v) for k, v in dict(data.get("material_aliases", {})).items()  # type: ignore[arg-type]
        }
        mgr.vision_timer = float(data.get("vision_timer", 0.0))  # type: ignore[arg-type]
        mgr.last_shift_time = float(data.get("last_shift_time", -SHIFT_COOLDOWN))  # type: ignore[arg-type]
        for entry in list(data.get("shifts", [])):  # type: ignore[arg-type]
            if isinstance(entry, dict):
                mgr.shifts.append(
                    ShiftRecord(
                        source=str(entry.get("source", "")),
                        target=str(entry.get("target", "")),
                        timestamp=float(entry.get("timestamp", 0.0)),
                        cells_changed=int(entry.get("cells_changed", 0)),
                    )
                )
        return mgr
