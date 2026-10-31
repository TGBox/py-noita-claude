import math
import random
import unittest

from src.depths import DEPTHS
from src.editor_layout import hit, hit_any, layout
from src.inventory import BAG_SIZE, MAX_WANDS, Inventory, SlotRef
from src.loot import Pickup, generate_wand, nearest_pickup, place_loot, random_block
from src.materials import AIR, BONE, FIRE
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
        for width, height in ((1280, 720), (1920, 1080), (960, 540)):
            result = layout(width, height, inventory)
            slots = result.slots
            expected = sum(w.capacity for w in inventory.wands) + BAG_SIZE
            self.assertEqual(len(slots), expected)
            for ref, (x, y, w, h) in slots:
                self.assertEqual(hit(slots, x + w // 2, y + h // 2), ref)
            self.assertIsNone(hit(slots, 0, 0))
            for index, (x, y, w, h) in result.handles:
                self.assertEqual(hit_any(result, x + 2, y + 2), ("wand", index))
            for index, (x, y, w, h) in result.flasks:
                self.assertEqual(hit_any(result, x + 2, y + 2), ("flask", index))
            x, y, w, h = result.drop
            self.assertEqual(hit_any(result, x + 2, y + 2), ("drop", None))
            self.assertEqual(hit_any(result, 1, 1), ("outside", None))
            px, py, pw, ph = result.panel  # everything fits into the window
            self.assertGreaterEqual(px, 0)
            self.assertLessEqual(px + pw, width)
            self.assertLessEqual(py + ph, height)


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
        shop = [i for i in run.pickups if i.price and not i.reroll]
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


class TestSaveAndContinue(unittest.TestCase):
    def test_restore_rebuilds_the_same_sanctum(self) -> None:
        import json

        run = Run(5)
        run.pearls = 77
        run.apply_perk("zaehes_fleisch")
        run.inventory.add_block("zahnbohrer")
        run.inventory.add_wand(generate_wand(random.Random(3), 2))
        run.enter_sanctum()
        shop = [(p.block, p.perk, p.price, p.wand) for p in run.pickups]
        data = json.loads(json.dumps(run.checkpoint))  # must survive JSON

        other = Run(99)
        other.restore(data)
        self.assertTrue(other.in_sanctum)
        self.assertEqual(other.depth_index, 0)
        self.assertEqual(other.pearls, 77)
        self.assertEqual(other.perks, {"zaehes_fleisch"})
        self.assertEqual(other.player.max_hp, run.player.max_hp)
        self.assertEqual([w.slots for w in other.inventory.wands], [w.slots for w in run.inventory.wands])
        self.assertEqual(other.inventory.bag, run.inventory.bag)
        self.assertEqual([(p.block, p.perk, p.price, p.wand) for p in other.pickups], shop)
        # descending continues identically
        run._descend()
        other._descend()
        self.assertEqual(run.level, other.level)
        self.assertEqual(bytes(run.world.grid), bytes(other.world.grid))

    def test_broken_saves_are_rejected(self) -> None:
        run = Run(5)
        run.enter_sanctum()
        good = run.checkpoint
        for broken in ({}, {**good, "version": 0}, {**good, "depth_index": 9}, {**good, "wands": [{"spec": {}}]}):
            with self.assertRaises(ValueError):
                Run(1).restore(broken)
        wands = [{**good["wands"][0], "spec": {**good["wands"][0]["spec"], "blocks": ["gibtsnicht"]}}]
        with self.assertRaises(ValueError):
            Run(1).restore({**good, "wands": wands})

    def test_discoveries(self) -> None:
        run = Run(5)
        found = {key for kind, key in run.discoveries if kind == "block"}
        self.assertTrue(set(PRESETS[0].blocks) <= found)
        run.discoveries.clear()
        run.pickups = [Pickup(run.player.x, run.player.y, block="blutegel")]
        run._pick_up()
        self.assertEqual(run.discoveries, [("block", "blutegel")])


class TestBossExit(unittest.TestCase):
    def test_boss_death_clears_the_exit(self) -> None:
        from src.materials import GROWTH

        run = Run(4)
        run.enter_depth(next(i for i, d in enumerate(DEPTHS) if d.boss == "brutmutter"))
        ex, ey = run.level.exit
        run.world.fill_disc(ex, ey, 10, GROWTH)
        run.enemies.boss().hurt(1e9)
        run.update(DT, Controls(), (0, 0, run.world.width, run.world.height))
        self.assertTrue(run.exit_open)
        self.assertNotEqual(run.world.get(ex, ey), GROWTH)


class TestTeleport(unittest.TestCase):
    def test_teleport_bolt_moves_the_player(self) -> None:
        run = Run(6)
        run.inventory.wands[0].set_slots(["teleportbolzen"] + [None] * (len(run.inventory.wands[0].slots) - 1))
        start = run.player.center
        aim = (start[0] + 80, start[1] - 20)
        run.update(DT, Controls(cast=True, aim=aim))
        moved = False
        for _ in range(90):
            run.update(DT, Controls(aim=aim))
            if math.dist(run.player.center, start) > 20:
                moved = True
                break
        self.assertTrue(moved)
        self.assertFalse(run.player.blocked(run.world, run.player.x, run.player.y))


class TestHeartsAndCocoons(unittest.TestCase):
    def test_heart_raises_max_health(self) -> None:
        run = Run(8)
        before = run.player.max_hp
        run.player.hp = 10
        run.pickups = [Pickup(run.player.center[0], run.player.center[1], heart=20)]
        run._pick_up()
        self.assertEqual(run.player.max_hp, before + 20)
        self.assertEqual(run.player.hp, run.player.max_hp)

    def test_cocoon_spills_loot(self) -> None:
        run = Run(8)
        cx, cy = run.player.center
        run.pickups = [Pickup(cx, cy, cocoon=True)]
        run._pick_up()
        self.assertGreaterEqual(len(run.pickups), 2)
        self.assertTrue(any(item.pearls for item in run.pickups))
        self.assertFalse(any(item.cocoon for item in run.pickups))

    def test_depths_contain_hearts_and_cocoons(self) -> None:
        run = Run(8)
        self.assertEqual(sum(1 for item in run.pickups if item.heart), 1)
        self.assertGreaterEqual(sum(1 for item in run.pickups if item.cocoon), 1)


class TestNewPerks(unittest.TestCase):
    def test_editing_needs_a_sanctum_or_quick_hands(self) -> None:
        run = Run(10)
        self.assertFalse(run.can_edit_wands)
        run.enter_sanctum()
        self.assertTrue(run.can_edit_wands)
        run._descend()
        self.assertFalse(run.can_edit_wands)
        run.apply_perk("flinke_haende")
        self.assertTrue(run.can_edit_wands)

    def test_flag_perks(self) -> None:
        run = Run(10)
        for key in ("gaslunge", "schleimlaeufer", "dauerflug", "wutdruesen"):
            run.apply_perk(key)
        self.assertTrue(run.player.gas_immune and run.player.mucus_immune)
        self.assertGreater(run.player.air_recharge, 1.0)
        self.assertGreater(run.projectiles.player_damage, 1.0)
        run.new_run()  # a fresh run drops them
        self.assertFalse(run.player.gas_immune)
        self.assertEqual(run.projectiles.player_damage, 1.0)

    def test_flag_perks_survive_a_restore(self) -> None:
        run = Run(10)
        run.apply_perk("gaslunge")
        run.enter_sanctum()
        other = Run(11)
        other.restore(run.checkpoint)
        self.assertTrue(other.player.gas_immune)

    def test_haggling_and_magnet(self) -> None:
        run = Run(10)
        item = Pickup(0, 0, block="funke", price=90)
        self.assertEqual(run.price_of(item), 90)
        run.apply_perk("feilscher")
        self.assertEqual(run.price_of(item), 60)
        run.apply_perk("perlenmagnet")
        cx, cy = run.player.center
        run.pickups = [Pickup(cx + 100, cy, pearls=5)]
        before = run.pearls
        for _ in range(60):
            run.update(DT, Controls(aim=(cx, cy)))
        self.assertEqual(run.pearls, before + 5)


class TestSecrets(unittest.TestCase):
    def test_each_depth_hides_a_sealed_urauge(self) -> None:
        from src import native
        from src.materials import BLOCKS_BODY
        from src.player import PLAYER_HEIGHT, PLAYER_WIDTH

        run = Run(12)
        found = 0
        for index in range(len(DEPTHS)):
            run.enter_depth(index)
            secret = run.level.secret
            if secret is None:
                continue
            found += 1
            self.assertTrue(any(item.eye for item in run.pickups))
            blocking = [int(b) for b in BLOCKS_BODY]
            goal = (secret[0] - PLAYER_WIDTH // 2, secret[1] - PLAYER_HEIGHT // 2)
            reached, _closest = native.reachable(
                native.byte_view(run.world.grid), run.world.width, run.world.height, blocking,
                (PLAYER_WIDTH, PLAYER_HEIGHT), run.level.spawn, goal,
            )  # fmt: skip
            self.assertFalse(reached, "the chamber must be sealed")
        self.assertEqual(found, len(DEPTHS))

    def test_all_eyes_and_the_heart_give_the_true_ending(self) -> None:
        run = Run(12)
        for _ in range(len(DEPTHS)):
            cx, cy = run.player.center
            run.pickups = [Pickup(cx, cy, eye=True)]
            run._pick_up()
        self.assertEqual(run.eyes, len(DEPTHS))
        run.outcome = "victory"
        self.assertTrue(run.true_ending)
        run.enter_sanctum()
        other = Run(13)
        other.restore(run.checkpoint)
        self.assertEqual(other.eyes, len(DEPTHS))


class TestSanctumMachines(unittest.TestCase):
    def test_reroll_replaces_the_perks_and_gets_dearer(self) -> None:
        run = Run(14)
        run.enter_sanctum()
        reroll = next(item for item in run.pickups if item.reroll)
        before = {item.perk for item in run.pickups if item.perk}
        run.pearls = 1000
        run.player.place(int(reroll.x) - 4, int(reroll.y) - 9)
        run._pick_up()
        after = {item.perk for item in run.pickups if item.perk}
        self.assertEqual(len(after), 3)
        self.assertNotEqual(before, after)
        self.assertEqual(run.pearls, 1000 - 100)
        self.assertEqual(reroll.price, 200)
        run.pearls = 50  # too poor now
        run._pick_up()
        self.assertEqual(run.pearls, 50)

    def test_choosing_a_perk_removes_the_reroll(self) -> None:
        run = Run(14)
        run.enter_sanctum()
        perk = next(item for item in run.pickups if item.perk)
        run.player.place(int(perk.x) - 4, int(perk.y) - 9)
        run._pick_up()
        self.assertFalse(any(item.reroll or item.perk for item in run.pickups))

    def test_death_leaves_a_pool_of_blood(self) -> None:
        from src.materials import BLOOD

        run = Run(14)
        before = run.world.count(BLOOD)
        run.player.hurt(10_000)
        run.update(DT, Controls())
        self.assertGreater(run.world.count(BLOOD), before + 20)


class TestSacs(unittest.TestCase):
    def test_tallow_sac_bursts_into_burning_tallow_and_chains(self) -> None:
        from src.enemies import SPECIES, Creature
        from src.materials import FIRE, TALLOW

        run = Run(15)
        run.enemies.creatures = []
        cx, cy = run.player.center
        x, y = int(cx) + 60, int(cy) - 4
        first = Creature(SPECIES["talgsack"], x, y, run.rng)
        second = Creature(SPECIES["talgsack"], x + 12, y, run.rng)
        run.enemies.creatures = [first, second]
        kills = run.stats["kills"]
        first.hurt(100)
        blasts = run.update(DT, Controls(aim=(cx, cy)))
        self.assertEqual(len(blasts), 1)
        for _ in range(3):
            run.update(DT, Controls(aim=(cx, cy)))
        self.assertTrue(second.dead)  # caught in the first blast
        self.assertEqual(run.stats["kills"], kills)  # sacs are not kills
        self.assertGreater(run.world.count(TALLOW) + run.world.count(FIRE), 20)
        self.assertFalse(any(kind == "creature" and key == "talgsack" for kind, key in run.discoveries))

    def test_sacs_are_hit_by_enemy_shots_too(self) -> None:
        from src.enemies import SPECIES, Creature
        from src.projectiles import ProjectileSystem
        from src.wand import Shot
        from src.world import World

        world = World(200, 80, seed=1)
        sac = Creature(SPECIES["saeuresack"], 120, 40, random.Random(1))
        system = ProjectileSystem()
        system.spawn([Shot(CATALOG["nadel"], (), [])], 60, 44, 0.0, team="enemy")
        for _ in range(30):
            system.update(world, DT, (0, 0), [sac])
        self.assertLess(sac.hp, sac.max_hp)


class TestKick(unittest.TestCase):
    def test_kick_hurts_and_shoves_and_bursts_sacs(self) -> None:
        from src.enemies import SPECIES, Creature

        run = Run(16)
        cx, cy = run.player.center
        maggot = Creature(SPECIES["made"], int(cx) + 6, int(cy) - 3, run.rng)
        sac = Creature(SPECIES["talgsack"], int(cx) + 8, int(cy) - 4, run.rng)
        run.enemies.creatures = [maggot, sac]
        run.update(DT, Controls(aim=(cx + 50, cy), kick=True))
        self.assertLess(maggot.hp, maggot.max_hp)
        self.assertGreater(maggot.vx, 0)
        self.assertTrue(sac.dead or sac not in run.enemies.creatures)
        hp = maggot.hp
        run.update(DT, Controls(aim=(cx + 50, cy), kick=True))  # still on cooldown
        self.assertEqual(maggot.hp, hp)


class TestSpecialSpells(unittest.TestCase):
    def _run_with(self, form: str) -> Run:
        from src.materials import AIR, BONE

        run = Run(18)
        wand = run.inventory.wands[0]
        wand.set_slots([form] + [None] * (len(wand.slots) - 1))
        run.enemies.creatures = []
        player = run.player
        floor = player.y + player.height
        for y in range(floor - 50, floor + 4):  # an open test hall with a flat floor
            for x in range(player.x - 20, player.x + 130):
                run.world.set_cell(x, y, AIR if y < floor else BONE, force=True)
        return run

    def _target(self, run: Run, key: str = "made"):
        from src.enemies import SPECIES, Creature

        cx, cy = run.player.center
        creature = Creature(SPECIES[key], int(cx) + 60, int(cy) - 6, run.rng)
        run.enemies.creatures = [creature]
        for _ in range(30):  # let it land first
            run.update(DT, Controls(aim=(cx, cy)))
        return creature

    def test_polymorph_turns_a_creature_into_another(self) -> None:
        run = self._run_with("wandlungsdruese")
        maggot = self._target(run)
        aim = maggot.center
        run.update(DT, Controls(cast=True, aim=aim))
        for _ in range(30):
            run.update(DT, Controls(aim=aim))
        self.assertNotIn(maggot, run.enemies.creatures)
        self.assertEqual(len(run.enemies.creatures), 1)
        self.assertNotEqual(run.enemies.creatures[0].spec.key, "made")

    def test_swap_trades_places(self) -> None:
        run = self._run_with("tauschdruese")
        maggot = self._target(run)
        start = run.player.center
        aim = maggot.center
        run.update(DT, Controls(cast=True, aim=aim))
        for _ in range(30):
            run.update(DT, Controls(aim=aim))
        self.assertGreater(math.dist(run.player.center, start), 30)

    def test_chain_spark_jumps_between_creatures(self) -> None:
        from src.enemies import SPECIES, Creature
        from src.projectiles import ProjectileSystem
        from src.wand import Shot
        from src.world import World

        world = World(400, 100, seed=1)
        a = Creature(SPECIES["made"], 100, 60, random.Random(1))
        b = Creature(SPECIES["made"], 150, 60, random.Random(2))
        c = Creature(SPECIES["made"], 200, 60, random.Random(3))
        system = ProjectileSystem()
        system.spawn([Shot(CATALOG["kettenfunke"], (), [])], 40, 63, 0.0)
        for _ in range(60):
            system.update(world, DT, (0, 0), [a, b, c])
        self.assertTrue(all(m.hp < m.max_hp for m in (a, b, c)))


class TestNewGamePlus(unittest.TestCase):
    def test_victory_leads_into_a_tougher_loop_keeping_gear(self) -> None:
        run = Run(19)
        run.apply_perk("wutdruesen")
        wands = [w.slots for w in run.inventory.wands]
        run.new_game_plus()  # not won yet: nothing happens
        self.assertEqual(run.ng, 0)
        run.outcome = "victory"
        run.new_game_plus()
        self.assertEqual((run.ng, run.outcome, run.depth_index), (1, "", 0))
        self.assertEqual([w.slots for w in run.inventory.wands], wands)
        self.assertIn("wutdruesen", run.perks)
        normal = [c for c in run.enemies.creatures if not c.spec.prop]
        self.assertTrue(normal)
        self.assertTrue(all(c.max_hp > c.spec.hp for c in normal))
        self.assertGreater(run.projectiles.enemy_damage, 1.0)
        run.enter_sanctum()
        other = Run(20)
        other.restore(run.checkpoint)
        self.assertEqual(other.ng, 1)
        run.new_run()
        self.assertEqual((run.ng, run.projectiles.enemy_damage), (0, 1.0))


class TestPlayerPolymorph(unittest.TestCase):
    def test_polymorphed_player_cannot_cast_and_recovers(self) -> None:
        from src.player import POLYMORPH_SPEED  # noqa: F401  (exists)

        run = Run(21)
        run.projectiles.polymorphs.append(run.player)
        run.update(DT, Controls())
        self.assertGreater(run.player.polymorphed, 0)
        cx, cy = run.player.center
        run.update(DT, Controls(cast=True, aim=(cx + 50, cy)))
        self.assertEqual(run.projectiles.items, [])
        for _ in range(int(8 / DT)):
            run.update(DT, Controls(aim=(cx + 50, cy)))
        self.assertEqual(run.player.polymorphed, 0.0)


class TestVaults(unittest.TestCase):
    def test_every_depth_but_the_last_has_a_guarded_vault(self) -> None:
        run = Run(22)
        for index, depth in enumerate(DEPTHS):
            run.enter_depth(index)
            vault = run.level.vault
            if depth.final:
                self.assertIsNone(vault)
                continue
            self.assertIsNotNone(vault)
            x, y = vault
            near = [i for i in run.pickups if abs(i.x - x) < 50 and abs(i.y - y) < 40]
            self.assertTrue(any(i.wand is not None for i in near))
            guards = [c for c in run.enemies.creatures if c.max_hp > c.spec.hp * 2]
            self.assertTrue(guards)


class TestMirrorWorld(unittest.TestCase):
    def test_portal_in_the_first_vault_leads_into_a_mirrored_harder_world(self) -> None:
        run = Run(23)
        portal = next(item for item in run.pickups if item.portal)
        normal = [c.max_hp for c in run.enemies.creatures if not c.spec.prop]
        run.player.place(int(portal.x) - 4, int(portal.y) - 9)
        run._pick_up()
        self.assertTrue(run.mirror)
        self.assertEqual(run.depth_index, 0)
        self.assertTrue(any(item.portal for item in run.pickups))  # the next portal waits already
        tough = [c for c in run.enemies.creatures if not c.spec.prop and not c.spec.boss]
        self.assertTrue(all(c.max_hp > c.spec.hp * 1.5 for c in tough))
        self.assertTrue(normal)
        self.assertFalse(run.world.rect_blocked(*run.level.spawn, run.player.width, run.player.height))
        self.assertGreater(run.projectiles.enemy_damage, 1.0)

    def test_mirrored_level_is_the_flipped_original(self) -> None:
        from src.world import World
        from src.worldgen import generate_level

        a = World(1280, 720, seed=9)
        level = generate_level(a, DEPTHS[0])
        b = World(1280, 720, seed=9)
        generate_level(b, DEPTHS[0])
        b.mirror()
        y = level.exit[1]
        row_a = a.grid[y * 1280 : (y + 1) * 1280]
        row_b = b.grid[y * 1280 : (y + 1) * 1280]
        self.assertEqual(bytes(row_a), bytes(row_b[::-1]))


class TestRoutes(unittest.TestCase):
    def test_routes_vary_and_keep_the_bosses_in_place(self) -> None:
        from src.depths import VARIANTS, choose_route

        routes = {tuple(d.key for d in choose_route(random.Random(seed))) for seed in range(40)}
        self.assertGreater(len(routes), 5)
        for stage, depth in enumerate(DEPTHS):
            for variant in VARIANTS.get(depth.key, ()):
                self.assertEqual(variant.boss, depth.boss, variant.key)
                self.assertEqual(variant.final, depth.final)

    def test_route_survives_save_and_restore(self) -> None:
        run = Run(24)
        run.enter_sanctum()
        other = Run(25)
        other.restore(run.checkpoint)
        self.assertEqual([d.key for d in other.route], [d.key for d in run.route])


class TestVisibility(unittest.TestCase):
    def test_sealed_treasures_stay_hidden_until_seen(self) -> None:
        run = Run(26)
        run.update_visibility()
        eye = next(item for item in run.pickups if item.eye)
        self.assertFalse(eye.seen)  # sealed in bone, far away
        run.player.place(int(eye.x) - 4, int(eye.y) - 9)
        run.update_visibility()
        self.assertTrue(eye.seen)
        shop_run = Run(27)
        shop_run.enter_sanctum()
        shop_run.update_visibility()
        self.assertTrue(all(item.seen for item in shop_run.pickups if item.price))


class TestBiomeCount(unittest.TestCase):
    def test_more_than_thirty_biomes_all_reachable_by_routes(self) -> None:
        from src.depths import VARIANTS, biome_count, choose_route

        self.assertGreater(biome_count(), 30)
        seen = set()
        rng = random.Random(1)
        for _ in range(400):
            seen |= {d.key for d in choose_route(rng)}
        every = {d.key for d in DEPTHS} | {d.key for v in VARIANTS.values() for d in v}
        self.assertEqual(seen, every)


class TestParallelWorlds(unittest.TestCase):
    def test_portals_lead_ever_further(self) -> None:
        run = Run(28)
        powers = [run.power]
        for world in (1, 2, 3):
            portal = next(item for item in run.pickups if item.portal)
            run.player.place(int(portal.x) - 4, int(portal.y) - 9)
            run._pick_up()
            self.assertEqual(abs(run.parallel), world)  # east or west, always further out
            self.assertEqual(run.mirror, world % 2 == 1)
            powers.append(run.power)
        self.assertEqual(powers, sorted(powers))
        self.assertEqual(len(set(powers)), 4)
        run.enter_sanctum()
        other = Run(29)
        other.restore(run.checkpoint)
        self.assertEqual(other.parallel, run.parallel)


class TestKnockback(unittest.TestCase):
    def test_blasts_throw_bodies_away(self) -> None:
        from src.enemies import SPECIES, Creature
        from src.projectiles import Blast

        run = Run(30)
        cx, cy = run.player.center
        sac = Creature(SPECIES["sporensack"], int(cx) + 30, int(cy) - 4, run.rng)
        sac.hp = sac.max_hp = 1000
        run._apply_blast(Blast(int(cx) + 20, int(cy), 12), [sac])
        self.assertGreater(sac.vx, 20)
        self.assertLess(sac.vy, 0)


class TestWestAndItems(unittest.TestCase):
    def test_west_portal_leads_into_darker_worlds(self) -> None:
        run = Run(33)
        run.level = run.level.__class__(run.level.spawn, run.level.exit, run.level.arena, None, (50, 300))
        run.enter_mirror()
        self.assertEqual(run.parallel, -1)
        self.assertLess(run.darkness, 1.0)
        self.assertGreater(run.power, 1.0)

    def test_blasts_throw_items(self) -> None:
        from src.projectiles import Blast

        run = Run(33)
        cx, cy = run.player.center
        item = Pickup(cx + 20, cy, block="funke")
        run.pickups = [item]
        run._apply_blast(Blast(int(cx) + 10, int(cy) + 2, 12), [])
        self.assertGreater(item.vx, 0)
        x0 = item.x
        for _ in range(30):
            item.update(run.world, DT)
        self.assertNotEqual(item.x, x0)


class TestInventoryScreen(unittest.TestCase):
    """Looking into the bag works anywhere; rebuilding wands only in a sanctum."""

    def test_bag_can_be_sorted_anywhere_but_wands_are_locked(self) -> None:
        from src.inventory import BAG_SIZE, SlotRef

        run = Run(11)
        self.assertEqual(len(run.inventory.bag), BAG_SIZE)
        self.assertGreaterEqual(BAG_SIZE, 30)
        run.inventory.bag[0] = "funke"
        note = run.inventory_drop(("slot", SlotRef("bag", 0)), ("slot", SlotRef("bag", 5)))
        self.assertEqual(note, "")
        self.assertEqual(run.inventory.bag[5], "funke")
        target = ("slot", SlotRef("wand", 0, 0))
        before = list(run.inventory.wands[0].slots)
        note = run.inventory_drop(("slot", SlotRef("bag", 5)), target)
        self.assertIn("Sanktum", note)
        self.assertEqual(run.inventory.wands[0].slots, before)
        run.enter_sanctum()
        self.assertEqual(run.inventory_drop(("slot", SlotRef("bag", 5)), target), "")
        self.assertEqual(run.inventory.wands[0].slots[0], "funke")

    def test_dropping_blocks_wands_and_flasks(self) -> None:
        from src.inventory import SlotRef

        run = Run(12)
        run.inventory.bag[3] = "nadel"
        count = len(run.pickups)
        run.inventory_drop(("slot", SlotRef("bag", 3)), ("drop", None))
        self.assertIsNone(run.inventory.bag[3])
        self.assertTrue(any(p.block == "nadel" and p.seen for p in run.pickups[count:]))
        # a wand slot cannot be emptied outside a sanctum
        key = run.inventory.wands[0].slots[0]
        self.assertIn("Sanktum", run.inventory_drop(("slot", SlotRef("wand", 0, 0)), ("outside", None)))
        self.assertEqual(run.inventory.wands[0].slots[0], key)
        wands = len(run.inventory.wands)
        run.inventory_drop(("wand", 1), ("outside", None))
        self.assertEqual(len(run.inventory.wands), wands - 1)
        self.assertTrue(any(p.wand is not None for p in run.pickups))
        self.assertNotEqual(run.inventory_drop(("wand", 0), ("drop", None)), "")  # keep one
        run.inventory_drop(("flask", 0), ("drop", None))
        self.assertEqual(run.flasks, [])

    def test_reorder_wands(self) -> None:
        run = Run(13)
        first, second = run.inventory.wands
        run.inventory.select(0)
        run.inventory_drop(("wand", 0), ("wand", 1))
        self.assertEqual(run.inventory.wands, [second, first])
        self.assertIs(run.inventory.wand, first)


class TestPlaytestFixes(unittest.TestCase):
    """Second playtest: pouring, kicking, liquids, traps, sandbox."""

    def _hall(self, seed: int = 41) -> Run:
        from src.materials import BONE

        run = Run(seed)
        world = run.world
        world.reset(AIR)
        for x in range(world.width):
            for y in range(400, 410):
                world.set_cell(x, y, BONE, force=True)
        run.enemies.creatures = []
        run.pickups = []
        run.player.place(300, 400 - run.player.height)
        return run

    def test_pouring_acid_does_not_hurt_the_pourer(self) -> None:
        from src.flask import Flask
        from src.materials import ACID, FUME

        run = self._hall()
        for x in range(330, 520):  # a basin the acid is poured into
            for y in range(400, 409):
                run.world.set_cell(x, y, AIR, force=True)
        run.flasks = [Flask(ACID, 300)]
        hp = run.player.hp
        cx, cy = run.player.center
        for frame in range(90):  # one second of pouring forwards, then wait
            run.update(1 / 60, Controls(aim=(cx + 120, cy - 30), pour=frame < 60))
        self.assertLess(run.flask.amount, 300)
        poured = [
            x
            for y in range(300, 410)
            for x in range(run.world.width)
            if run.world.get(x, y) in (ACID, FUME)
        ]
        self.assertGreater(len(poured), 20)  # (acid eats into the bone floor and fumes away)
        player = run.player
        near = [
            (x, y)
            for y in range(player.y - 3, player.y + player.height + 3)
            for x in range(player.x - 3, player.x + player.width + 3)
            if run.world.get(x, y) == ACID
        ]
        self.assertEqual(near, [])  # nothing landed on the one pouring
        self.assertEqual(run.player.hp, hp)

    def test_kick_sends_a_creature_flying(self) -> None:
        from src.enemies import SPECIES, Creature

        run = self._hall()
        px, py = run.player.center
        made = Creature(SPECIES["made"], int(px) + 6, 400 - SPECIES["made"].height, run.rng)
        run.enemies.creatures = [made]
        start = made.x
        run.update(1 / 60, Controls(aim=(px + 50, py), kick=True))
        for _ in range(20):
            run.update(1 / 60, Controls(aim=(px + 50, py)))
        self.assertGreater(made.x - start, 15)
        self.assertLess(made.hp, made.max_hp)

    def test_shots_dive_through_liquid(self) -> None:
        from src.enemies import SPECIES, Creature
        from src.materials import BLOOD
        from src.wand import Shot

        run = self._hall()
        for x in range(380, 460):
            for y in range(360, 400):
                run.world.set_cell(x, y, BLOOD, force=True)
        made = Creature(SPECIES["made"], 430, 400 - SPECIES["made"].height, run.rng)
        made.hp = made.max_hp = 1000
        run.enemies.creatures = [made]
        cx, cy = run.player.center
        run.projectiles.spawn([Shot(CATALOG["nadel"], ())], 370, 395, 0.0)
        for _ in range(30):
            run.update(1 / 60, Controls(aim=(cx + 100, cy)))
        self.assertLess(made.hp, 1000)  # hit under the surface

    def test_a_shell_around_the_player_does_not_trap_it(self) -> None:
        from src.materials import CRUST

        run = self._hall()
        player = run.player
        for _ in range(5):
            run.update(1 / 60, Controls())
        x0, y0 = player.x - 2, player.y - 2
        for y in range(y0, player.y + player.height + 2):
            for x in range(x0, player.x + player.width + 2):
                if not player.contains(x, y):
                    run.world.set_cell(x, y, CRUST, force=True)
        run.world.set_cell(player.x + 2, player.y + 3, CRUST, force=True)  # one inside, too
        hp = player.hp
        for _ in range(60):
            run.update(1 / 60, Controls(move=1))
        self.assertFalse(player.blocked(run.world, player.x, player.y - 1) and
                         player.blocked(run.world, player.x + 1, player.y))
        self.assertGreaterEqual(player.hp, hp - 1)

    def test_sandbox_god_mode_and_editing(self) -> None:
        run = self._hall()
        self.assertFalse(run.can_edit_wands)
        run.sandbox = run.god_mode = True
        self.assertTrue(run.can_edit_wands)
        run.player.hurt(10_000)
        run.update(1 / 60, Controls())
        self.assertEqual(run.outcome, "")
        self.assertEqual(run.player.hp, run.player.max_hp)
