import math
import random
import unittest

from src.depths import DEPTHS
from src.editor_layout import hit, layout
from src.inventory import BAG_SIZE, MAX_WANDS, Inventory, SlotRef
from src.loot import Pickup, generate_wand, nearest_pickup, place_loot, random_block
from src.materials import BONE, FIRE
from src.perks import PERKS
from src.run import Controls, Run
from src.spells import CATALOG, Category
from src.wand import PRESETS, Wand, WandSpec
from src.world import World

DT = 1 / 60


class TestLoot(unittest.TestCase):
    def test_generated_wands_are_valid_and_castable(self) -> None:
        rng = random.Random(1)
        for level in (1, 2, 4, 8):
            for _ in range(50):
                spec = generate_wand(rng, level)
                wand = Wand(spec)
                self.assertGreaterEqual(spec.capacity, len(spec.blocks))
                self.assertTrue(any(CATALOG[k].category is Category.FORM for k in spec.blocks))
                self.assertTrue(wand.cast(), spec)
                self.assertTrue(spec.name_de)

    def test_deeper_wands_are_stronger_on_average(self) -> None:
        def average(level: int, field: str) -> float:
            rng = random.Random(7)
            return sum(getattr(generate_wand(rng, level), field) for _ in range(300)) / 300

        self.assertGreater(average(5, "capacity"), average(1, "capacity"))
        self.assertGreater(average(5, "mana_max"), average(1, "mana_max"))
        self.assertLess(average(5, "cast_delay"), average(1, "cast_delay"))

    def test_random_block_respects_category(self) -> None:
        rng = random.Random(2)
        for _ in range(50):
            self.assertIs(CATALOG[random_block(rng, Category.TRIGGER)].category, Category.TRIGGER)

    def test_pickups_fall_and_rest_on_the_floor(self) -> None:
        world = World(64, 48, seed=1)
        item = Pickup(30, 5, block="funke")
        for _ in range(120):
            item.update(world, DT)
        self.assertEqual(int(item.y), world.height - 3)

    def test_nearest_pickup_needs_to_be_close(self) -> None:
        items = [Pickup(100, 100, block="funke"), Pickup(110, 100, block="nadel")]
        self.assertIs(nearest_pickup(items, 108, 100), items[1])
        self.assertIsNone(nearest_pickup(items, 200, 200))

    def test_loot_is_placed_in_the_level(self) -> None:
        run = Run(seed=4)
        items = place_loot(run.world, random.Random(1), run.level.spawn, wands=3, blocks=6)
        self.assertGreaterEqual(len(items), 8)
        self.assertEqual(sum(item.wand is not None for item in items), 3)


class TestInventory(unittest.TestCase):
    def make(self) -> Inventory:
        return Inventory([PRESETS[0], PRESETS[1]], random.Random(1))

    def test_blocks_go_into_the_bag_until_it_is_full(self) -> None:
        inventory = self.make()
        for _ in range(BAG_SIZE):
            self.assertTrue(inventory.add_block("funke"))
        self.assertFalse(inventory.add_block("funke"))

    def test_wands_are_added_until_full_then_swapped(self) -> None:
        inventory = self.make()
        extra = WandSpec("Neu", ("nadel",), capacity=3)
        for _ in range(MAX_WANDS - 2):
            self.assertIsNone(inventory.add_wand(extra))
        self.assertEqual(len(inventory.wands), MAX_WANDS)
        inventory.select(0)
        dropped = inventory.add_wand(extra)
        self.assertIsNotNone(dropped)
        assert dropped is not None
        self.assertEqual(dropped.name_de, PRESETS[0].name_de)
        self.assertEqual(inventory.wands[0].spec.name_de, "Neu")

    def test_move_blocks_between_wand_and_bag(self) -> None:
        inventory = self.make()
        first_block = inventory.wands[0].slots[0]
        self.assertTrue(inventory.move(SlotRef("wand", 0, 0), SlotRef("bag", 3)))
        self.assertEqual(inventory.bag[3], first_block)
        self.assertIsNone(inventory.wands[0].slots[0])
        self.assertEqual(len(inventory.wands[0].blocks), len(PRESETS[0].blocks) - 1)
        # and back into another wand, swapping with what is there
        target = SlotRef("wand", 0, 1)
        replaced = inventory.get(target)
        self.assertTrue(inventory.move(SlotRef("bag", 3), target))
        self.assertEqual(inventory.get(target), first_block)
        self.assertEqual(inventory.bag[3], replaced)

    def test_invalid_moves_are_rejected(self) -> None:
        inventory = self.make()
        self.assertFalse(inventory.move(SlotRef("bag", 0), SlotRef("bag", 1)))  # empty source
        self.assertFalse(inventory.move(SlotRef("wand", 99, 0), SlotRef("bag", 1)))
        self.assertFalse(inventory.move(SlotRef("wand", 0, 7), SlotRef("bag", 1)))

    def test_cycle_and_select(self) -> None:
        inventory = self.make()
        inventory.cycle(1)
        self.assertEqual(inventory.active, 1)
        inventory.cycle(1)
        self.assertEqual(inventory.active, 0)
        inventory.select(3)  # not owned
        self.assertEqual(inventory.active, 0)

    def test_editor_layout_covers_every_slot_without_overlap(self) -> None:
        inventory = self.make()
        slots = layout(1280, 720, inventory)
        expected = sum(w.capacity for w in inventory.wands) + BAG_SIZE
        self.assertEqual(len(slots), expected)
        for ref, (x, y, w, h) in slots:
            self.assertEqual(hit(slots, x + w // 2, y + h // 2), ref)
        self.assertIsNone(hit(slots, 0, 0))


class TestRun(unittest.TestCase):
    def test_new_run_starts_in_the_first_depth(self) -> None:
        run = Run(seed=1)
        self.assertEqual(run.depth_index, 0)
        self.assertEqual(len(run.inventory.wands), 2)
        self.assertTrue(run.exit_open)
        self.assertGreater(len(run.enemies.creatures), 0)
        self.assertFalse(run.world.rect_blocked(*run.level.spawn, 8, 18))

    def test_exit_leads_through_the_sanctum_one_depth_deeper(self) -> None:
        run = Run(seed=2)
        run.player.hurt(30)

        def go_to_exit() -> None:
            run.player.place(int(run.level.exit[0]) - 4, int(run.level.exit[1]) - 9)
            run.update(DT, Controls())

        go_to_exit()
        self.assertTrue(run.in_sanctum)
        self.assertEqual(run.depth.key, "sanktum")
        self.assertEqual(run.next_depth_number, 2)
        self.assertEqual(run.player.hp, run.player.max_hp)  # the sanctum heals
        self.assertEqual(run.enemies.creatures, [])
        go_to_exit()
        self.assertFalse(run.in_sanctum)
        self.assertEqual(run.depth_index, 1)

    def test_boss_depth_is_locked_until_the_boss_dies(self) -> None:
        run = Run(seed=3)
        run.enter_depth(1)  # the stomach
        boss = run.enemies.boss()
        self.assertIsNotNone(boss)
        self.assertFalse(run.exit_open)
        assert boss is not None
        boss.hurt(10_000)
        run.update(DT, Controls())
        self.assertTrue(run.exit_open)
        self.assertIsNone(run.enemies.boss())

    def test_killing_the_heart_wins_the_run(self) -> None:
        run = Run(seed=4)
        run.enter_depth(len(DEPTHS) - 1)
        heart = run.enemies.boss()
        assert heart is not None
        self.assertEqual(heart.spec.key, "herz")
        heart.hurt(10_000)
        run.update(DT, Controls())
        self.assertEqual(run.outcome, "victory")

    def test_death_ends_the_run_and_r_starts_over(self) -> None:
        run = Run(seed=5)
        run.enter_depth(2)
        run.player.hurt(1_000)
        run.update(DT, Controls())
        self.assertEqual(run.outcome, "dead")
        run.new_run()
        self.assertEqual((run.outcome, run.depth_index), ("", 0))
        self.assertFalse(run.player.dead)

    def test_casting_spawns_projectiles_from_the_arm(self) -> None:
        run = Run(seed=6)
        cx, cy = run.player.center
        run.update(DT, Controls(cast=True, aim=(cx + 100, cy)))
        self.assertTrue(run.projectiles.items or run.projectiles._pending)

    def test_picking_up_items(self) -> None:
        run = Run(seed=7)
        cx, cy = run.player.center
        run.pickups = [Pickup(cx, cy, block="nadel"), Pickup(cx + 300, cy, wand=PRESETS[2])]
        run.update(DT, Controls(pickup=True))
        self.assertIn("nadel", run.inventory.bag)
        self.assertEqual(len(run.pickups), 1)

    def test_creature_drops_and_blasts_hurt_everyone_nearby(self) -> None:
        run = Run(seed=8)
        run.enemies.creatures = run.enemies.creatures[:1]
        creature = run.enemies.creatures[0]
        run.rng.seed(0)
        creature.hurt(10_000)
        before = len(run.pickups)
        for _ in range(20):
            run.update(DT, Controls())
        self.assertGreaterEqual(len(run.pickups), before)
        # an explosion right next to the player hurts the player
        cx, cy = run.player.center
        run.world.set_cell(int(cx) + 12, int(cy), BONE)
        from src.projectiles import Blast

        run._apply_blast(Blast(int(cx), int(cy), 8), [run.player])
        self.assertLess(run.player.hp, run.player.max_hp)

    def test_a_short_session_runs_without_errors(self) -> None:
        run = Run(seed=9)
        rng = random.Random(1)
        for frame in range(600):
            cx, cy = run.player.center
            controls = Controls(
                move=rng.choice((-1, 0, 1)),
                jump=frame % 50 == 0,
                levitate=frame % 90 < 30,
                cast=True,
                aim=(cx + math.cos(frame / 20) * 80, cy + math.sin(frame / 20) * 80),
                pickup=frame % 30 == 0,
            )
            if frame % 120 == 0:
                run.inventory.cycle(1)
            run.update(DT, controls, (0, 0, run.world.width, run.world.height))
        self.assertIn(run.outcome, ("", "dead"))


class TestSanctum(unittest.TestCase):
    def sanctum(self, seed: int = 1) -> Run:
        run = Run(seed=seed)
        run.enter_sanctum()
        return run

    def stand_at(self, run: Run, item: Pickup) -> None:
        run.player.place(int(item.x) - 4, int(item.y) - 9)

    def test_sanctum_offers_shop_items_and_three_perks(self) -> None:
        run = self.sanctum()
        perks = [i for i in run.pickups if i.perk]
        shop = [i for i in run.pickups if i.price]
        self.assertEqual(len(perks), 3)
        self.assertEqual(len(shop), 5)
        self.assertEqual(sum(i.wand is not None for i in shop), 1)
        self.assertFalse(run.world.rect_blocked(*run.level.spawn, 8, 18))

    def test_buying_needs_enough_pearls(self) -> None:
        run = self.sanctum()
        item = next(i for i in run.pickups if i.block and i.price)
        self.stand_at(run, item)
        run.update(DT, Controls(pickup=True))
        self.assertIn(item, run.pickups)  # too poor
        run.pearls = item.price + 5
        self.stand_at(run, item)
        run.update(DT, Controls(pickup=True))
        self.assertNotIn(item, run.pickups)
        self.assertEqual(run.pearls, 5)
        self.assertIn(item.block, run.inventory.bag)

    def test_choosing_a_perk_removes_the_others(self) -> None:
        run = self.sanctum()
        orb = next(i for i in run.pickups if i.perk)
        self.stand_at(run, orb)
        run.update(DT, Controls(pickup=True))
        self.assertIn(orb.perk, run.perks)
        self.assertFalse(any(i.perk for i in run.pickups))

    def test_perks_are_never_offered_twice(self) -> None:
        run = self.sanctum()
        for perk in PERKS[:-3]:
            run.apply_perk(perk.key)
        run.enter_sanctum()
        offered = {i.perk for i in run.pickups if i.perk}
        self.assertTrue(offered.isdisjoint(run.perks))


class TestPearlsAndPerks(unittest.TestCase):
    def test_pearls_are_collected_by_touch_and_dropped_by_creatures(self) -> None:
        run = Run(seed=3)
        cx, cy = run.player.center
        run.pickups.append(Pickup(cx, cy, pearls=17))
        run.update(DT, Controls())
        self.assertEqual(run.pearls, 17)
        creature = run.enemies.creatures[0]
        creature.hurt(1000)
        run.update(DT, Controls())
        self.assertTrue(any(i.pearls for i in run.pickups))
        self.assertEqual(run.stats["kills"], 1)

    def test_fireproof_skin(self) -> None:
        run = Run(seed=4)
        run.apply_perk("feuerfest")
        player = run.player
        for _ in range(5):
            run.update(DT, Controls())
        player.burning = 0
        run.world.set_cell(player.x - 1, player.y + 5, FIRE)
        hp = player.hp
        run.update(DT, Controls())
        self.assertEqual(player.burning, 0.0)
        self.assertEqual(player.hp, hp)

    def test_tough_flesh_and_light_bones(self) -> None:
        run = Run(seed=5)
        run.apply_perk("zaehes_fleisch")
        run.apply_perk("leichte_knochen")
        self.assertEqual(run.player.max_hp, 150)
        self.assertAlmostEqual(run.player.energy_max, 4.5)
        run.new_run()  # perks end with the run
        self.assertEqual(run.player.max_hp, 100)
        self.assertEqual(run.perks, set())

    def test_armour_plates_reduce_blast_damage(self) -> None:
        from src.projectiles import Blast

        run = Run(seed=6)
        cx, cy = run.player.center
        run._apply_blast(Blast(int(cx), int(cy), 10), [run.player])
        unprotected = run.player.max_hp - run.player.hp
        run.player.hp = run.player.max_hp
        run.apply_perk("panzerplatten")
        run._apply_blast(Blast(int(cx), int(cy), 10), [run.player])
        self.assertLess(run.player.max_hp - run.player.hp, unprotected * 0.5)

    def test_second_pulse_revives_once(self) -> None:
        run = Run(seed=7)
        run.apply_perk("zweiter_puls")
        run.player.hurt(1000)
        run.update(DT, Controls())
        self.assertEqual(run.outcome, "")
        self.assertGreater(run.player.hp, 0)
        run.player.hurt(1000)
        run.update(DT, Controls())
        self.assertEqual(run.outcome, "dead")

    def test_acid_blood_sprays_when_hurt(self) -> None:
        run = Run(seed=8)
        run.apply_perk("saeureblut")
        run.update(DT, Controls())
        run.player.hurt(10)
        run.update(DT, Controls())
        self.assertGreaterEqual(len(run.projectiles.items) + len(run.projectiles._pending), 6)

    def test_run_reports_sound_events(self) -> None:
        run = Run(seed=10)
        cx, cy = run.player.center
        run.pickups.append(Pickup(cx, cy, pearls=5))
        run.update(DT, Controls(cast=True, aim=(cx + 100, cy)))
        self.assertIn("cast", run.events)
        self.assertIn("pearl", run.events)
        run.enemies.creatures[0].hurt(1000)
        run.update(DT, Controls())
        self.assertIn("kill", run.events)

    def test_bloodlust_heals_on_kills(self) -> None:
        run = Run(seed=9)
        run.apply_perk("blutdurst")
        run.player.hurt(30)
        hp = run.player.hp
        run.enemies.creatures[0].hurt(1000)
        run.update(DT, Controls())
        self.assertGreater(run.player.hp, hp)


if __name__ == "__main__":
    unittest.main()
