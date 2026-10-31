"""Logic behind the new interface pieces: hover text, icons, gamepad, run log."""

import json
import tempfile
import unittest
from pathlib import Path

from src.flask import Flask
from src.hover import compare, describe, describe_material, wand_values
from src.icons import BACKGROUND, glyph_signature, icon_pixels
from src.loot import Pickup
from src.materials import ACID, AIR, BEDROCK, ENAMEL, FLESH
from src.run import Run
from src.runlog import RunLog
from src.spells import BLOCKS, Category


class TestHover(unittest.TestCase):
    def test_materials_explain_themselves(self) -> None:
        self.assertIsNone(describe_material(AIR))
        acid = describe_material(ACID)
        self.assertEqual(acid.title, "Magensäure")
        self.assertTrue(any("Schaden/s" in line for line in acid.lines))
        self.assertIn("sehr hart", describe_material(ENAMEL).lines[0])
        self.assertIn("unzerstörbar", describe_material(BEDROCK).lines[0])
        self.assertIn("weich", describe_material(FLESH).lines[0])

    def test_creature_item_material_order(self) -> None:
        run = Run(21)
        creature = next(c for c in run.enemies.creatures if not c.spec.prop)
        cx, cy = creature.center
        info = describe(run, cx, cy, {id(creature)})
        self.assertEqual(info.kind, "creature")
        self.assertEqual(info.title, creature.spec.name_de)
        self.assertIsNotNone(info.hp)
        hidden = describe(run, cx, cy, set())  # not in sight: no name given away
        self.assertNotEqual(getattr(hidden, "kind", None), "creature")
        px, py = run.player.center
        run.pickups.append(Pickup(px, py, flask=Flask(ACID, 150), seen=True))
        info = describe(run, px, py - 3, set())
        self.assertEqual(info.kind, "pickup")
        self.assertTrue(any("Magensäure" in line for line in info.lines))
        run.pickups[-1].seen = False  # hidden items stay hidden
        self.assertNotEqual(getattr(describe(run, px, py - 3, set()), "kind", None), "pickup")

    def test_shop_items_show_price_and_block_details(self) -> None:
        run = Run(22)
        run.enter_sanctum()
        run.update_visibility()  # shop items are always on display
        offer = next(item for item in run.pickups if item.block and item.price)
        info = describe(run, offer.x, offer.y - 3, set())
        self.assertEqual(info.block, offer.block)
        self.assertTrue(any("Preis" in line for line in info.lines))
        self.assertTrue(any("Mana" in line for line in info.lines))
        wand = next(item for item in run.pickups if item.wand)
        info = describe(run, wand.x, wand.y - 3, set())
        self.assertIsNotNone(info.wand)
        self.assertIsNotNone(info.compare)

    def test_wand_comparison(self) -> None:
        self.assertEqual(compare(10, 5, True), 1)
        self.assertEqual(compare(0.1, 0.5, False), 1)
        self.assertEqual(compare(3, 3, True), 0)
        run = Run(23)
        rows = wand_values(run.inventory.wand.spec)
        self.assertTrue(all(0.0 <= fill <= 1.0 for _l, _v, fill, _h, _t in rows))


class TestIcons(unittest.TestCase):
    def test_every_block_has_a_framed_icon(self) -> None:
        for block in BLOCKS:
            pixels = icon_pixels(block.key)
            self.assertEqual(len(pixels), 16)
            self.assertTrue(all(len(row) == 16 for row in pixels))
            inner = [p for row in pixels[2:14] for p in row[2:14]]
            self.assertTrue(any(p not in (None, BACKGROUND) for p in inner), block.key)

    def test_icons_tell_kinds_apart(self) -> None:
        shapes = {glyph_signature(b.key) for b in BLOCKS}
        self.assertGreater(len(shapes), 60)
        forms = {glyph_signature(b.key) for b in BLOCKS if b.category is Category.FORM}
        self.assertGreater(len(forms), 15)


class FakePad:
    name = "Testpad"

    def __init__(self, buttons=(), axes=None) -> None:
        self.buttons = set(buttons)
        self.axes = axes or {}

    def button(self, name: str) -> bool:
        return name in self.buttons

    def axis(self, name: str) -> float:
        return self.axes.get(name, 0.0)


class TestGamepad(unittest.TestCase):
    def test_read_state(self) -> None:
        try:
            from src.gamepad import deadzone, read_state
        except ImportError:
            self.skipTest("pygame not installed")
        state = read_state(FakePad({"a"}, {"rt": 0.9, "lx": 0.1, "rx": 1.0}))
        self.assertIn("a", state.buttons)
        self.assertIn("rt", state.buttons)  # a pulled trigger counts as a button
        self.assertEqual(state.move, (0.0, 0.0))  # inside the dead zone
        self.assertAlmostEqual(state.aim[0], 1.0)
        later = read_state(FakePad({"a", "x"}), state.buttons)
        self.assertEqual(later.pressed, frozenset({"x"}))
        self.assertEqual(deadzone(0.1, 0.1), (0.0, 0.0))


class TestRunLog(unittest.TestCase):
    def test_writes_json_lines(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            log = RunLog(Path(folder))
            log.start(seed=5)
            from src.run import Controls

            run = Run(31)
            run.update(1 / 60, Controls())
            run.player.hurt(12, "Magensäure")
            run.update(1 / 60, Controls())
            run._flush_log()
            for event, data in run.log:
                log.write(event, **data)
            for _ in range(20):
                log.frame(1 / 60)
            log.flush_frames("schlund")
            try:
                raise RuntimeError("Testfehler")
            except RuntimeError as error:
                log.error(error)
            log.close()
            lines = [json.loads(line) for line in log.path.read_text(encoding="utf-8").splitlines()]
            events = [entry["ereignis"] for entry in lines]
            self.assertEqual(events[0], "start")
            self.assertIn("tiefe", events)
            self.assertIn("bildrate", events)
            error = next(entry for entry in lines if entry["ereignis"] == "fehler")
            self.assertIn("Testfehler", error["traceback"])
            damage = [entry for entry in lines if entry["ereignis"] == "schaden"]
            self.assertTrue(damage and "Magensäure" in damage[0]["ursachen"])
