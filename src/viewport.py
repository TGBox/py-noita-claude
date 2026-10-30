"""Virtual resolution with letterboxing: maps window pixels to game pixels."""

from __future__ import annotations


class Viewport:
    """Scales a fixed virtual resolution into any window without distorting it."""

    def __init__(self, virtual_width: int, virtual_height: int) -> None:
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.target_width = virtual_width
        self.target_height = virtual_height

    def resize(self, window_width: int, window_height: int) -> None:
        """Recompute scale and centring for a new window size."""
        window_width = max(1, window_width)
        window_height = max(1, window_height)
        self.scale = min(window_width / self.virtual_width, window_height / self.virtual_height)
        self.target_width = max(1, int(self.virtual_width * self.scale))
        self.target_height = max(1, int(self.virtual_height * self.scale))
        self.offset_x = (window_width - self.target_width) // 2
        self.offset_y = (window_height - self.target_height) // 2

    def to_virtual(self, screen_x: int, screen_y: int) -> tuple[int, int]:
        """Convert window coordinates to virtual coordinates, clamped to the picture."""
        x = int((screen_x - self.offset_x) / self.scale)
        y = int((screen_y - self.offset_y) / self.scale)
        return (
            min(max(x, 0), self.virtual_width - 1),
            min(max(y, 0), self.virtual_height - 1),
        )
