"""Gamepad input: standard controllers (Xbox layout) read once per frame.

pygame-ce's SDL game controller API gives every supported pad the same layout; if it
is missing, a plain joystick with the common XInput layout is used instead. All
reading goes through a small adapter, so the logic can be tested with a fake pad.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import ClassVar

import pygame

try:  # standardised layout for every known pad (pygame-ce, SDL2)
    from pygame._sdl2 import controller as sdl_controller
except ImportError:  # pragma: no cover - depends on the pygame build
    sdl_controller = None

DEADZONE = 0.25
TRIGGER_THRESHOLD = 0.4
RESCAN_INTERVAL = 2.0  # seconds between looking for a newly plugged-in pad
AXIS_MAX = 32767.0


@dataclass
class PadState:
    """One frame of gamepad input."""

    buttons: frozenset[str] = frozenset()
    move: tuple[float, float] = (0.0, 0.0)  # left stick, dead zone applied
    aim: tuple[float, float] = (0.0, 0.0)  # right stick, dead zone applied
    connected: bool = False
    name: str = ""
    pressed: frozenset[str] = field(default_factory=frozenset)  # went down this frame


def deadzone(x: float, y: float, zone: float = DEADZONE) -> tuple[float, float]:
    """Radial dead zone, rescaled so the stick still reaches full strength."""
    length = math.hypot(x, y)
    if length < zone:
        return 0.0, 0.0
    scale = min(1.0, (length - zone) / (1.0 - zone)) / length
    return x * scale, y * scale


class _ControllerAdapter:
    """SDL game controller (pygame._sdl2.controller)."""

    BUTTONS: ClassVar[dict[str, str]] = {
        "a": "CONTROLLER_BUTTON_A", "b": "CONTROLLER_BUTTON_B", "x": "CONTROLLER_BUTTON_X",
        "y": "CONTROLLER_BUTTON_Y", "lb": "CONTROLLER_BUTTON_LEFTSHOULDER",
        "rb": "CONTROLLER_BUTTON_RIGHTSHOULDER", "back": "CONTROLLER_BUTTON_BACK",
        "start": "CONTROLLER_BUTTON_START", "ls": "CONTROLLER_BUTTON_LEFTSTICK",
        "rs": "CONTROLLER_BUTTON_RIGHTSTICK", "hoch": "CONTROLLER_BUTTON_DPAD_UP",
        "runter": "CONTROLLER_BUTTON_DPAD_DOWN", "links": "CONTROLLER_BUTTON_DPAD_LEFT",
        "rechts": "CONTROLLER_BUTTON_DPAD_RIGHT",
    }  # fmt: skip
    AXES: ClassVar[dict[str, str]] = {
        "lx": "CONTROLLER_AXIS_LEFTX", "ly": "CONTROLLER_AXIS_LEFTY",
        "rx": "CONTROLLER_AXIS_RIGHTX", "ry": "CONTROLLER_AXIS_RIGHTY",
        "lt": "CONTROLLER_AXIS_TRIGGERLEFT", "rt": "CONTROLLER_AXIS_TRIGGERRIGHT",
    }  # fmt: skip

    def __init__(self, device) -> None:
        self.device = device
        self.name = str(device.name)
        self._buttons = {k: getattr(pygame, v) for k, v in self.BUTTONS.items() if hasattr(pygame, v)}
        self._axes = {k: getattr(pygame, v) for k, v in self.AXES.items() if hasattr(pygame, v)}

    def attached(self) -> bool:
        return bool(self.device.attached())

    def button(self, name: str) -> bool:
        index = self._buttons.get(name)
        return index is not None and bool(self.device.get_button(index))

    def axis(self, name: str) -> float:
        index = self._axes.get(name)
        if index is None:
            return 0.0
        return max(-1.0, min(1.0, self.device.get_axis(index) / AXIS_MAX))


class _JoystickAdapter:
    """Fallback: a plain joystick read with the usual XInput (Xbox) layout."""

    BUTTONS: ClassVar[dict[str, int]] = {"a": 0, "b": 1, "x": 2, "y": 3, "lb": 4, "rb": 5, "back": 6, "start": 7, "ls": 8, "rs": 9}
    AXES: ClassVar[dict[str, int]] = {"lx": 0, "ly": 1, "lt": 2, "rx": 3, "ry": 4, "rt": 5}

    def __init__(self, device) -> None:
        self.device = device
        self.name = str(device.get_name())

    def attached(self) -> bool:
        return True

    def button(self, name: str) -> bool:
        device = self.device
        if name in self.BUTTONS:
            index = self.BUTTONS[name]
            return index < device.get_numbuttons() and bool(device.get_button(index))
        if device.get_numhats() == 0:
            return False
        hx, hy = device.get_hat(0)
        return {"hoch": hy > 0, "runter": hy < 0, "links": hx < 0, "rechts": hx > 0}.get(name, False)

    def axis(self, name: str) -> float:
        index = self.AXES[name]
        if index >= self.device.get_numaxes():
            return 0.0
        value = float(self.device.get_axis(index))
        if name in ("lt", "rt"):  # triggers rest at -1 on XInput joysticks
            return (value + 1.0) / 2.0
        return value


def read_state(adapter, previous: frozenset[str] = frozenset()) -> PadState:
    """Sample a pad through its adapter (triggers count as buttons)."""
    buttons = {name for name in _ControllerAdapter.BUTTONS if adapter.button(name)}
    for trigger in ("lt", "rt"):
        if adapter.axis(trigger) > TRIGGER_THRESHOLD:
            buttons.add(trigger)
    move = deadzone(adapter.axis("lx"), adapter.axis("ly"))
    aim = deadzone(adapter.axis("rx"), adapter.axis("ry"))
    down = frozenset(buttons)
    return PadState(down, move, aim, True, adapter.name, down - previous)


class Gamepad:
    """The first connected pad; plugging one in or out during play is handled."""

    def __init__(self) -> None:
        self.adapter = None
        self.state = PadState()
        self._rescan = 0.0
        self._ready = False

    def _init(self) -> None:
        self._ready = True
        try:
            if sdl_controller is not None:
                sdl_controller.init()
            pygame.joystick.init()
        except (pygame.error, AttributeError):
            pass

    def _connect(self) -> None:
        if not self._ready:
            self._init()
        try:
            if sdl_controller is not None:
                for index in range(sdl_controller.get_count()):
                    if sdl_controller.is_controller(index):
                        self.adapter = _ControllerAdapter(sdl_controller.Controller(index))
                        return
            if pygame.joystick.get_count() > 0:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                self.adapter = _JoystickAdapter(joystick)
        except (pygame.error, AttributeError, TypeError):
            self.adapter = None

    def poll(self, dt: float) -> PadState:
        if self.adapter is None:
            self._rescan -= dt
            if self._rescan > 0:
                self.state = PadState()
                return self.state
            self._rescan = RESCAN_INTERVAL
            self._connect()
            if self.adapter is None:
                self.state = PadState()
                return self.state
        try:
            if not self.adapter.attached():
                raise pygame.error("pad unplugged")
            self.state = read_state(self.adapter, self.state.buttons)
        except (pygame.error, AttributeError, TypeError):
            self.adapter = None
            self.state = PadState()
        return self.state
