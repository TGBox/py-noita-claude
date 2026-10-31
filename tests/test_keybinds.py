import tempfile
import unittest
from pathlib import Path

from src.keybinds import ACTIONS, K_ESCAPE, MOUSE_RIGHT, Bindings, binding_name_de
from src.options import load_bindings, save_bindings


class TestBindings(unittest.TestCase):
    def test_defaults(self) -> None:
        bindings = Bindings()
        self.assertEqual(bindings.actions_for(ord("s")), ["absorb"])  # S fills the flask
        self.assertIn("pour", bindings.actions_for(MOUSE_RIGHT))
        self.assertEqual(bindings.describe("jump"), "W / Leertaste / Pfeil hoch")
        self.assertEqual(bindings.describe_pad("cast"), "RT")
        # every action has a label and no key is bound twice by default
        keys = [k for action in ACTIONS for k in action.keys]
        self.assertEqual(len(keys), len(set(keys)))
        pads = [a.pad for a in ACTIONS if a.pad]
        self.assertEqual(len(pads), len(set(pads)))

    def test_rebinding_takes_the_key_from_other_actions(self) -> None:
        bindings = Bindings()
        losers = bindings.bind("drink", ord("e"))
        self.assertEqual(losers, ["pickup"])
        self.assertEqual(bindings.keys["drink"], [ord("e")])
        self.assertEqual(bindings.keys["pickup"], [])
        self.assertEqual(bindings.bind("drink", K_ESCAPE), [])  # ESC stays the pause key
        self.assertEqual(bindings.bind_pad("drink", "a"), ["jump"])
        self.assertIsNone(bindings.pad["jump"])
        bindings.reset("pickup")
        self.assertEqual(bindings.keys["pickup"], [ord("e")])

    def test_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "steuerung.json"
            bindings = Bindings()
            bindings.bind("kick", "maus2")
            bindings.bind_pad("kick", "ls")
            self.assertTrue(save_bindings(bindings, path))
            loaded = load_bindings(path)
            self.assertEqual(loaded.keys["kick"], ["maus2"])
            self.assertEqual(loaded.pad["kick"], "ls")
            path.write_text('{"keys": {"kick": [true, "x", 27, 120]}, "pad": {"jump": "zz"}}')
            broken = load_bindings(path)
            self.assertEqual(broken.keys["kick"], [120])
            self.assertEqual(broken.pad["jump"], "a")

    def test_names(self) -> None:
        self.assertEqual(binding_name_de(ord("q")), "Q")
        self.assertEqual(binding_name_de(MOUSE_RIGHT), "Rechte Maus")
        self.assertEqual(binding_name_de((1 << 30) | 68), "F11")
