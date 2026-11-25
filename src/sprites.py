"""Contract V5: Sprite-sheet metadata and frame animator (Card A17)."""

from __future__ import annotations

import json
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
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    frame_size = tuple(data["frame_size"])
    anchor = tuple(data["anchor"])

    anims = {}
    for name, spec in data.get("anims", {}).items():
        # Handle both "next" and "next_anim" keys for backward compatibility
        next_anim = spec.get("next_anim", spec.get("next", "idle"))
        anims[name] = AnimSpec(
            row=spec["row"],
            frames=spec["frames"],
            fps=spec.get("fps", 8.0),
            loop=spec.get("loop", True),
            next_anim=next_anim,
        )

    glow_points = []
    glow_data = data.get("glow", [])
    if isinstance(glow_data, list):
        # Handle both formats: list of dicts or list of lists
        for item in glow_data:
            if isinstance(item, dict):
                glow_points.append(
                    GlowPoint(
                        offset=tuple(item["offset"]),
                        color=tuple(item["color"]),
                        radius=item.get("radius", 12),
                    )
                )
            else:
                # Assume it's a list like [offset, color, radius]
                glow_points.append(
                    GlowPoint(
                        offset=tuple(item[0]),
                        color=tuple(item[1]),
                        radius=item[2] if len(item) > 2 else 12,
                    )
                )

    return SheetMeta(frame_size=frame_size, anchor=anchor, anims=anims, glow=tuple(glow_points))


class Animator:
    def __init__(self, meta: SheetMeta, initial: str = "idle") -> None:
        self.meta: SheetMeta = meta
        self.state: str = initial
        self.frame_index: int = 0
        self.timer: float = 0.0
        self.finished: bool = False

    def play(self, state: str, *, restart: bool = False) -> None:
        """Switch to animation state (ignored if already in state unless restart=True)."""
        if self.state != state or restart:
            self.state = state
            self.frame_index = 0
            self.timer = 0.0
            self.finished = False

    def update(self, dt: float) -> None:
        """Advance animation timer and frame_index by dt seconds."""
        anim_spec = self.meta.anims.get(self.state, AnimSpec(0, 1))
        self.timer += dt

        # Calculate expected frame based on fps
        expected_frame = int(self.timer * anim_spec.fps)

        if expected_frame >= anim_spec.frames:
            if anim_spec.loop:
                # Loop back to start
                self.frame_index = expected_frame % anim_spec.frames
                self.timer = (expected_frame % anim_spec.frames) / anim_spec.fps
            else:
                # Stop at last frame
                self.frame_index = anim_spec.frames - 1
                self.finished = True
                # Check if we should transition to next animation
                if not anim_spec.loop:
                    # Transition to next animation
                    next_state = anim_spec.next_anim
                    if next_state != self.state:
                        self.play(next_state)
                        return
        else:
            self.frame_index = expected_frame

    def frame_rect(self) -> tuple[int, int, int, int]:
        """Return (x, y, w, h) pixel rectangle on the sprite sheet."""
        anim_spec = self.meta.anims.get(self.state, AnimSpec(0, 1))
        x = self.frame_index * self.meta.frame_size[0]
        y = anim_spec.row * self.meta.frame_size[1]
        w, h = self.meta.frame_size
        return (x, y, w, h)
