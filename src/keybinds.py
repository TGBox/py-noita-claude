"""Rebindable controls: which keys, mouse buttons and gamepad buttons trigger which action.

Pure data without pygame, so bindings can be tested and saved headless. Keyboard keys
are stored as SDL2 key codes (the values of pygame 2's ``K_*`` constants), mouse
buttons as ``"maus1"`` .. ``"maus3"`` and gamepad buttons by name (``"a"``, ``"rt"``).
"""

from __future__ import annotations

from dataclasses import dataclass

# SDL2 key codes (identical to pygame 2's K_* constants)
_SDLK_SCANCODE = 1 << 30


def _key(char: str) -> int:
    return ord(char)


def _scancode(code: int) -> int:
    return code | _SDLK_SCANCODE


K_TAB, K_RETURN, K_ESCAPE, K_SPACE, K_BACKSPACE, K_DELETE = 9, 13, 27, 32, 8, 127
K_RIGHT, K_LEFT, K_DOWN, K_UP = (_scancode(c) for c in (79, 80, 81, 82))
K_F11 = _scancode(68)
K_LSHIFT, K_LCTRL = _scancode(225), _scancode(224)

MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT = "maus1", "maus2", "maus3"

PAD_BUTTONS = (
    "a", "b", "x", "y", "lb", "rb", "lt", "rt", "back", "start", "ls", "rs",
    "hoch", "runter", "links", "rechts",
)  # fmt: skip
PAD_NAMES_DE = {
    "a": "A", "b": "B", "x": "X", "y": "Y", "lb": "LB", "rb": "RB", "lt": "LT", "rt": "RT",
    "back": "Back", "start": "Start", "ls": "Linker Stick", "rs": "Rechter Stick",
    "hoch": "Steuerkreuz hoch", "runter": "Steuerkreuz runter",
    "links": "Steuerkreuz links", "rechts": "Steuerkreuz rechts",
}  # fmt: skip

Binding = int | str  # key code or mouse button token


@dataclass(frozen=True)
class Action:
    key: str
    label_de: str
    keys: tuple[Binding, ...]  # default keyboard / mouse bindings
    pad: str | None  # default gamepad button
    group: str  # heading in the controls screen


ACTIONS: tuple[Action, ...] = (
    Action("left", "Nach links", (_key("a"), K_LEFT), None, "Bewegung"),
    Action("right", "Nach rechts", (_key("d"), K_RIGHT), None, "Bewegung"),
    Action("jump", "Springen / Schweben (halten)", (_key("w"), K_SPACE, K_UP), "a", "Bewegung"),
    Action("cast", "Zaubern", (MOUSE_LEFT,), "rt", "Kampf"),
    Action("kick", "Treten", (_key("q"),), "b", "Kampf"),
    Action("next_wand", "Nächste Augmentation", (), "rb", "Kampf"),
    Action("prev_wand", "Vorige Augmentation", (), "links", "Kampf"),
    Action("pour", "Phiole ausgießen (halten)", (MOUSE_RIGHT,), "lt", "Phiolen"),
    Action("absorb", "Phiole füllen (halten)", (_key("s"), K_DOWN), "lb", "Phiolen"),
    Action("drink", "Aus Phiole trinken", (_key("f"),), "y", "Phiolen"),
    Action("throw", "Phiole werfen", (_key("t"),), "hoch", "Phiolen"),
    Action("next_flask", "Nächste Phiole", (_key("c"),), "rechts", "Phiolen"),
    Action("pickup", "Aufheben / Kaufen / Wählen", (_key("e"),), "x", "Gegenstände"),
    Action("inventory", "Rucksack (im Sanktum: umbauen)", (K_TAB, _key("i")), "back", "Gegenstände"),
    Action("light", "Licht an/aus", (_key("l"),), None, "Anzeige"),
    Action("mute", "Ton an/aus", (_key("m"),), None, "Anzeige"),
    Action("fullscreen", "Vollbild", (K_F11,), None, "Anzeige"),
    Action("new_game_plus", "Neues Spiel+ (nach dem Sieg)", (_key("n"),), "runter", "Sonstiges"),
)  # fmt: skip
ACTION_BY_KEY = {action.key: action for action in ACTIONS}
# Fixed keys that cannot be rebound (so the menus always stay reachable).
RESERVED: frozenset[Binding] = frozenset({K_ESCAPE})
HOLD_ACTIONS = frozenset({"left", "right", "jump", "cast", "pour", "absorb"})

_NAMED_KEYS_DE = {
    K_TAB: "Tab", K_RETURN: "Enter", K_ESCAPE: "ESC", K_SPACE: "Leertaste",
    K_BACKSPACE: "Rücktaste", K_DELETE: "Entf", K_RIGHT: "Pfeil rechts", K_LEFT: "Pfeil links",
    K_DOWN: "Pfeil runter", K_UP: "Pfeil hoch", K_LSHIFT: "Umschalt", K_LCTRL: "Strg",
    MOUSE_LEFT: "Linke Maus", MOUSE_MIDDLE: "Mittlere Maus", MOUSE_RIGHT: "Rechte Maus",
}  # fmt: skip


def binding_name_de(binding: Binding) -> str:
    """Human-readable German name of a key or mouse button."""
    if binding in _NAMED_KEYS_DE:
        return _NAMED_KEYS_DE[binding]
    if isinstance(binding, int):
        if 32 < binding < 127:
            return chr(binding).upper()
        if _scancode(58) <= binding <= _scancode(69):  # F1 .. F12
            return f"F{binding - _scancode(58) + 1}"
        return f"Taste {binding}"
    return str(binding)


class Bindings:
    """The player's current bindings (defaults until changed)."""

    def __init__(self) -> None:
        self.keys: dict[str, list[Binding]] = {}
        self.pad: dict[str, str | None] = {}
        self.reset()

    def reset(self, action: str | None = None) -> None:
        for spec in ACTIONS:
            if action is None or spec.key == action:
                self.keys[spec.key] = list(spec.keys)
                self.pad[spec.key] = spec.pad

    # ------------------------------------------------------------- queries

    def actions_for(self, binding: Binding) -> list[str]:
        return [action for action, keys in self.keys.items() if binding in keys]

    def pad_actions_for(self, button: str) -> list[str]:
        return [action for action, pad in self.pad.items() if pad == button]

    def describe(self, action: str) -> str:
        """The keyboard/mouse bindings of an action, e.g. ``"W / Leertaste"``."""
        names = [binding_name_de(b) for b in self.keys.get(action, [])]
        return " / ".join(names) if names else "-"

    def describe_pad(self, action: str) -> str:
        button = self.pad.get(action)
        return PAD_NAMES_DE.get(button, "-") if button else "-"

    # ------------------------------------------------------------- changes

    def bind(self, action: str, binding: Binding) -> list[str]:
        """Make ``binding`` the (only) key of ``action``; other actions lose it.

        Returns the actions that lost the binding.
        """
        if action not in self.keys or binding in RESERVED:
            return []
        losers = [other for other in self.actions_for(binding) if other != action]
        for other in losers:
            self.keys[other] = [b for b in self.keys[other] if b != binding]
        self.keys[action] = [binding]
        return losers

    def bind_pad(self, action: str, button: str) -> list[str]:
        if action not in self.pad or button not in PAD_BUTTONS:
            return []
        losers = [other for other in self.pad_actions_for(button) if other != action]
        for other in losers:
            self.pad[other] = None
        self.pad[action] = button
        return losers

    # --------------------------------------------------------- persistence

    def to_json(self) -> dict[str, object]:
        return {"keys": {k: list(v) for k, v in self.keys.items()}, "pad": dict(self.pad)}

    @classmethod
    def from_json(cls, data: object) -> Bindings:
        """Read saved bindings; anything unknown or broken keeps its default."""
        bindings = cls()
        if not isinstance(data, dict):
            return bindings
        keys, pad = data.get("keys"), data.get("pad")
        if isinstance(keys, dict):
            for action, values in keys.items():
                if action in bindings.keys and isinstance(values, list):
                    valid = [v for v in values if _valid_binding(v)]
                    bindings.keys[action] = valid
        if isinstance(pad, dict):
            for action, button in pad.items():
                if action in bindings.pad and (button is None or button in PAD_BUTTONS):
                    bindings.pad[action] = button
        return bindings


def _valid_binding(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value > 0 and value not in RESERVED
    return value in (MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT)
