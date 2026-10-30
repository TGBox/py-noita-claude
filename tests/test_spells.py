import unittest

from src.spells import BLOCKS, CATALOG, Category, Trigger
from src.wand import MULTICAST_SPREAD, PRESETS, Wand, WandSpec


def wand(*blocks: str, **stats: float) -> Wand:
    return Wand(WandSpec("Test", blocks, **stats))


def names(shots: list) -> list[str]:
    return [shot.form.key for shot in shots]


class TestCatalog(unittest.TestCase):
    def test_every_category_has_blocks(self) -> None:
        for category in Category:
            self.assertGreaterEqual(sum(b.category is category for b in BLOCKS), 4, category)

    def test_forms_fly(self) -> None:
        for block in BLOCKS:
            if block.category is Category.FORM:
                self.assertGreater(block.speed, 0, block.key)
                self.assertGreater(block.lifetime, 0, block.key)

    def test_category_fields_are_consistent(self) -> None:
        for block in BLOCKS:
            self.assertEqual(block.trigger is not None, block.category is Category.TRIGGER)
            self.assertEqual(block.material is not None, block.category is Category.PAYLOAD)
            self.assertTrue(block.name_de)

    def test_every_trigger_kind_is_available(self) -> None:
        self.assertEqual({b.trigger for b in BLOCKS if b.trigger}, set(Trigger))

    def test_presets_only_use_known_blocks_and_cast(self) -> None:
        for spec in PRESETS:
            self.assertTrue(all(key in CATALOG for key in spec.blocks), spec.name_de)
            self.assertTrue(Wand(spec).cast(), spec.name_de)

    def test_unknown_block_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            wand("funke", "gibt_es_nicht")


class TestDeck(unittest.TestCase):
    def test_draws_one_form_per_cast_in_order(self) -> None:
        w = wand("funke", "nadel", "klumpen")
        self.assertEqual(names(w.cast()), ["funke"])
        w.cooldown = 0
        self.assertEqual(names(w.cast()), ["nadel"])
        w.cooldown = 0
        self.assertEqual(names(w.cast()), ["klumpen"])

    def test_recharges_after_the_last_block(self) -> None:
        w = wand("funke", "nadel", recharge=0.5, cast_delay=0.1)
        w.cast()
        self.assertFalse(w.recharging)
        w.update(1.0)
        w.cast()
        self.assertTrue(w.recharging)
        self.assertEqual(w.index, 0)
        self.assertEqual(w.cast(), [])  # still recharging
        w.update(0.6)
        self.assertEqual(names(w.cast()), ["funke"])

    def test_cast_delay_includes_block_delays(self) -> None:
        w = wand("gallenblase", "funke", cast_delay=0.1)
        w.cast()
        self.assertAlmostEqual(w.cooldown, 0.1 + CATALOG["gallenblase"].cast_delay)
        self.assertEqual(w.cast(), [])
        w.update(0.5)
        self.assertTrue(w.cast())

    def test_modifiers_apply_to_the_next_form_only(self) -> None:
        w = wand("beschleunigung", "sekret_saeure", "funke", "funke")
        first = w.cast()[0]
        self.assertEqual([m.key for m in first.modifiers], ["beschleunigung", "sekret_saeure"])
        w.cooldown = 0
        self.assertEqual(w.cast()[0].modifiers, ())

    def test_multicast_draws_several_groups_with_spread(self) -> None:
        w = wand("sprengkraft", "doppel", "funke", "sekret_feuer", "klumpen")
        shots = w.cast()
        self.assertEqual(names(shots), ["funke", "klumpen"])
        offsets = [shot.angle_offset for shot in shots]
        self.assertAlmostEqual(offsets[1] - offsets[0], MULTICAST_SPREAD)
        # modifiers drawn before the multicast apply to every group
        for shot in shots:
            self.assertIn("sprengkraft", [m.key for m in shot.modifiers])
        self.assertIn("sekret_feuer", [m.key for m in shots[1].modifiers])
        self.assertNotIn("sekret_feuer", [m.key for m in shots[0].modifiers])

    def test_trigger_carries_the_next_group_as_payload(self) -> None:
        w = wand("nerv_aufprall", "nadel", "sekret_saeure", "klumpen", "funke")
        shots = w.cast()
        self.assertEqual(names(shots), ["nadel"])
        self.assertEqual(names(shots[0].children), ["klumpen"])
        self.assertEqual(shots[0].children[0].modifiers[0].key, "sekret_saeure")
        w.cooldown = 0
        self.assertEqual(names(w.cast()), ["funke"])  # deck continues after the payload

    def test_nested_triggers(self) -> None:
        w = wand("nerv_zeit", "funke", "nerv_aufprall", "nadel", "klumpen")
        outer = w.cast()[0]
        inner = outer.children[0]
        self.assertEqual(inner.form.key, "nadel")
        self.assertEqual(names(inner.children), ["klumpen"])

    def test_incomplete_group_wraps_to_the_start(self) -> None:
        w = wand("funke", "sekret_feuer")
        w.cast()
        w.cooldown = 0
        shots = w.cast()  # fire secretion + wraps around to the spark
        self.assertEqual(names(shots), ["funke"])
        self.assertEqual(shots[0].modifiers[0].key, "sekret_feuer")
        self.assertTrue(w.recharging)

    def test_deck_without_forms_casts_nothing_and_never_loops(self) -> None:
        w = wand("beschleunigung", "doppel", "nerv_ende")
        self.assertEqual(w.cast(), [])
        self.assertTrue(w.recharging)

    def test_each_block_is_drawn_once_per_cast(self) -> None:
        w = wand("doppel", "doppel", "funke")
        self.assertEqual(len(w.cast()), 1)

    def test_mana_limits_casting_and_regenerates(self) -> None:
        cost = CATALOG["gallenblase"].mana
        w = wand("gallenblase", mana_max=cost * 1.5, mana_regen=10, cast_delay=0, recharge=0)
        self.assertTrue(w.cast())
        w.update(0.4)  # cooldown over, but mana still too low
        self.assertEqual(w.cast(), [])
        self.assertEqual(w.index, 0)  # failed cast does not advance the deck
        w.update(3.0)
        self.assertTrue(w.cast())

    def test_mana_does_not_exceed_maximum(self) -> None:
        w = wand("funke", mana_max=50)
        w.update(100)
        self.assertEqual(w.mana, 50)


if __name__ == "__main__":
    unittest.main()
