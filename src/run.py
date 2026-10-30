"""One run through the organism: depths, combat, loot, the way down and the outcome.

Pure game logic without pygame, so a whole run can be simulated in tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass
from typing import Any

from src.body import Body
from src.depths import DEPTHS, Depth
from src.enemies import EnemyManager, populate, spawn_boss
from src.inventory import Inventory
from src.loot import (
    PICKUP_RANGE,
    Pickup,
    block_price,
    generate_wand,
    nearest_pickup,
    place_loot,
    random_block,
    scatter_pearls,
    wand_price,
)
from src.perks import PERK_BY_KEY, PERKS
from src.player import MAX_ENERGY, MAX_HP, Player
from src.projectiles import Blast, ProjectileSystem
from src.settings import MAX_SIM_STEPS_PER_FRAME, SIM_HZ, WORLD_HEIGHT, WORLD_WIDTH
from src.spells import CATALOG
from src.wand import PRESETS, Shot, Wand, WandSpec
from src.world import World
from src.worldgen import Level, generate_level, generate_sanctum

SIM_DT = 1.0 / SIM_HZ
BLAST_DAMAGE = 3.0  # damage per blast radius cell at point blank
BLAST_REACH = 6  # cells beyond the blast radius that still hurt
DROP_CHANCE = 0.3  # chance that a creature drops a block
EXIT_RANGE = 14.0
SHOULDER_OFFSET = (2.0, 1.0)  # arm root relative to the body centre (x towards the aim)
STARTER_WANDS = (PRESETS[0], PRESETS[1])
SAVE_VERSION = 1
SANCTUM = Depth("sanktum", "Das Sanktum", walkers=0, flyers=0, wands=0, blocks=0, ambient=0.55)
PEARL_PILES = 6
SHOP_BLOCKS = 4
PERK_CHOICES = 3
BLOODLUST_HEAL = 6.0
FAST_GLANDS = 0.75  # cast delay / recharge factor of the "Schnelle Drüsen" perk
ARMOUR_FACTOR = 0.2  # explosion damage factor of the "Panzerplatten" perk
ACID_BLOOD_COOLDOWN = 1.0
ACID_BLOOD_SPRAY = 6

Rect = tuple[int, int, int, int]


@dataclass
class Controls:
    """Player intent for one update (filled from keyboard and mouse by the game)."""

    move: int = 0
    jump: bool = False
    levitate: bool = False
    cast: bool = False
    aim: tuple[float, float] = (0.0, 0.0)
    pickup: bool = False


def arm_reach(block_count: int) -> float:
    """Length of the augmentation arm (it grows with the number of blocks)."""
    return 7 + block_count * 1.5


class Run:
    def __init__(
        self, seed: int | None = None, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT
    ) -> None:
        self.rng = random.Random(seed)
        self.world = World(width, height, seed=self.rng.randrange(2**31))
        self.player = Player(0, 0)
        self.enemies = EnemyManager()
        self.projectiles = ProjectileSystem()
        self.pickups: list[Pickup] = []
        self.inventory = Inventory(list(STARTER_WANDS), self.rng)
        self.depth_index = 0
        self.level = Level((0, 0), (0, 0), None)
        self.exit_open = False
        self.outcome = ""  # "", "dead" or "victory"
        self.time_in_depth = 0.0
        self.simulated_chunks = 0
        self.in_sanctum = False
        self.pearls = 0
        self.perks: set[str] = set()
        self.revive_used = False
        self.stats = {"kills": 0, "pearls": 0, "time": 0.0}
        self._last_hp = 0.0
        self._acid_blood_cooldown = 0.0
        self.events: list[str] = []  # sound cues of the last update
        self._hurt_cooldown = 0.0
        self._accumulator = 0.0
        self.discoveries: list[
            tuple[str, str]
        ] = []  # ("block"|"creature", key), drained by the game
        self.checkpoint: dict[str, Any] | None = None  # state at the last sanctum entry
        self.new_run()

    # ---------------------------------------------------------------- flow

    @property
    def depth(self) -> Depth:
        return SANCTUM if self.in_sanctum else DEPTHS[self.depth_index]

    @property
    def next_depth_number(self) -> int:
        """Number shown in the HUD: the depth we are in (or about to enter from a sanctum)."""
        return self.depth_index + (2 if self.in_sanctum else 1)

    def new_run(self) -> None:
        self._reset()
        self.enter_depth(0)

    def _reset(self) -> None:
        """Fresh run state (starter wands, no perks) without generating a level."""
        self.inventory = Inventory(list(STARTER_WANDS), self.rng)
        self.outcome = ""
        self.pearls = 0
        self.perks = set()
        self.revive_used = False
        self.stats = {"kills": 0, "pearls": 0, "time": 0.0}
        self.checkpoint = None
        for spec in STARTER_WANDS:
            self._discover_blocks(spec.blocks)
        player = self.player
        player.max_hp, player.energy_max = MAX_HP, MAX_ENERGY
        player.fire_immune = player.acid_immune = False
        player.place(0, 0)

    def apply_perk(self, key: str) -> None:
        """Gain a perk for the rest of the run."""
        self.perks.add(key)
        player = self.player
        if key == "feuerfest":
            player.fire_immune = True
            player.burning = 0.0
        elif key == "saeurehaut":
            player.acid_immune = True
        elif key == "zaehes_fleisch":
            player.max_hp += 50
            player.hp += 50
        elif key == "leichte_knochen":
            player.energy_max *= 1.5
            player.energy = player.energy_max

    def enter_sanctum(self) -> None:
        """The safe chamber after depth ``depth_index``: heal, shop, choose a perk."""
        self.checkpoint = self.snapshot()  # taken first, so a restore rebuilds the same shop
        self.in_sanctum = True
        layout = generate_sanctum(self.world)
        self.level = Level(layout.spawn, layout.exit, None)
        self.enemies.clear()
        self.projectiles.clear()
        self.exit_open = True
        level = self.depth_index + 2  # loot quality of the depth that follows
        offers: list[Pickup] = []
        for x, y in layout.shop[:SHOP_BLOCKS]:
            key = random_block(self.rng)
            offers.append(Pickup(x, y, block=key, price=block_price(key, level), floating=True))
        x, y = layout.shop[SHOP_BLOCKS]
        offers.append(
            Pickup(
                x, y, wand=generate_wand(self.rng, level), price=wand_price(level), floating=True
            )
        )
        available = [perk.key for perk in PERKS if perk.key not in self.perks]
        for (x, y), key in zip(layout.altar, self.rng.sample(available, PERK_CHOICES)):
            offers.append(Pickup(x, y, perk=key, floating=True))
        self.pickups = offers
        self.player.place(*layout.spawn)
        self._refill_wands()
        self.time_in_depth = 0.0

    def enter_depth(self, index: int) -> None:
        """Generate depth ``index`` and put the player at its entrance (fully healed)."""
        self.in_sanctum = False
        self.depth_index = index
        depth = self.depth
        self.world.reseed(self.rng.randrange(2**31))
        self.level = generate_level(self.world, depth)
        self.enemies.creatures = populate(
            self.world,
            self.rng,
            self.level.spawn,
            depth.walkers,
            depth.flyers,
            depth.spitters,
            depth.bloats,
        )
        if depth.boss and self.level.arena is not None:
            self.enemies.creatures.append(spawn_boss(depth.boss, self.level.arena, self.rng))
        self.exit_open = depth.boss is None
        self.pickups = place_loot(
            self.world, self.rng, self.level.spawn, depth.wands, depth.blocks, level=index + 1
        )
        self.pickups += scatter_pearls(self.world, self.rng, self.level.spawn, PEARL_PILES)
        self.projectiles.clear()
        self.player.place(*self.level.spawn)
        self._refill_wands()
        self.time_in_depth = 0.0

    # ---------------------------------------------------------- save / load

    def snapshot(self) -> dict[str, Any]:
        """JSON-compatible state from which ``restore`` rebuilds the next sanctum."""
        player = self.player
        version, internal, gauss = self.rng.getstate()
        return {
            "version": SAVE_VERSION,
            "depth_index": self.depth_index,
            "pearls": self.pearls,
            "perks": sorted(self.perks),
            "revive_used": self.revive_used,
            "stats": dict(self.stats),
            "player": {
                "max_hp": player.max_hp,
                "energy_max": player.energy_max,
                "fire_immune": player.fire_immune,
                "acid_immune": player.acid_immune,
            },
            "wands": [
                {
                    "spec": {**asdict(wand.spec), "blocks": list(wand.spec.blocks)},
                    "slots": list(wand.slots),
                }
                for wand in self.inventory.wands
            ],
            "active": self.inventory.active,
            "bag": list(self.inventory.bag),
            "rng": [version, list(internal), gauss],
        }

    def restore(self, data: dict[str, Any]) -> None:
        """Continue a saved run: enters the sanctum the snapshot was taken at.

        Raises ``ValueError`` for data that does not fit this version of the game.
        """
        try:
            if data.get("version") != SAVE_VERSION:
                raise ValueError("unsupported save version")
            depth_index = int(data["depth_index"])
            if not 0 <= depth_index < len(DEPTHS) - 1:
                raise ValueError("depth out of range")
            wands = []
            for entry in data["wands"]:
                spec = WandSpec(**{**entry["spec"], "blocks": tuple(entry["spec"]["blocks"])})
                if any(key not in CATALOG for key in spec.blocks):
                    raise ValueError("unknown block in a saved wand")
                wands.append((spec, [key if key in CATALOG else None for key in entry["slots"]]))
            bag = [key if key in CATALOG else None for key in data["bag"]]
            perks = {key for key in data["perks"] if key in PERK_BY_KEY}
            version, internal, gauss = data["rng"]
            rng_state = (version, tuple(internal), gauss)
            player_data = data["player"]
        except (KeyError, TypeError) as error:
            raise ValueError("broken save data") from error
        self._reset()
        self.depth_index = depth_index
        self.pearls = int(data["pearls"])
        self.perks = perks
        self.revive_used = bool(data["revive_used"])
        self.stats = {key: data["stats"].get(key, 0) for key in self.stats}
        player = self.player
        player.max_hp = float(player_data["max_hp"])
        player.energy_max = float(player_data["energy_max"])
        player.fire_immune = bool(player_data["fire_immune"])
        player.acid_immune = bool(player_data["acid_immune"])
        self.inventory.wands = []
        for spec, slots in wands:
            wand = Wand(spec, self.rng)
            count = len(wand.slots)
            wand.set_slots((slots + [None] * count)[:count])
            self.inventory.wands.append(wand)
        self.inventory.bag = (bag + [None] * len(self.inventory.bag))[: len(self.inventory.bag)]
        self.inventory.select(int(data.get("active", 0)))
        self.rng.setstate(rng_state)
        self.discoveries.clear()
        self.enter_sanctum()

    def _discover_blocks(self, keys) -> None:
        self.discoveries.extend(("block", key) for key in keys if key)

    def _refill_wands(self) -> None:
        for wand in self.inventory.wands:
            wand.mana = wand.spec.mana_max
            wand.cooldown = wand.recharge_left = 0.0

    # ---------------------------------------------------------------- update

    def shoulder(self, aim: tuple[float, float]) -> tuple[float, float]:
        cx, cy = self.player.center
        side = 1 if aim[0] >= cx else -1
        return cx + SHOULDER_OFFSET[0] * side, cy + SHOULDER_OFFSET[1]

    def update(self, dt: float, controls: Controls, area: Rect | None = None) -> list[Blast]:
        """Advance the run by ``dt`` seconds; ``area`` limits simulation (cells)."""
        self.events = []
        self.time_in_depth += dt
        if not self.outcome:
            self.stats["time"] += dt
        alive = not self.player.dead and self.outcome != "victory"
        if not alive:
            controls = Controls(aim=controls.aim)
        self.player.update(self.world, dt, controls.move, controls.jump, controls.levitate)
        for wand in self.inventory.wands:
            wand.update(dt)
        if controls.cast:
            self._cast(controls.aim)
        for item in self.pickups:
            item.update(self.world, dt)
        if alive:
            self._collect_pearls()
        if controls.pickup:
            self._pick_up()

        self._step_world(dt, area)
        everywhere = area or (0, 0, self.world.width, self.world.height)
        died = self.enemies.update(self.world, dt, self.player, self.projectiles, everywhere)
        for creature in died:
            self._on_death(creature)
        bodies: list[Body] = [self.player, *self.enemies.creatures]
        blasts = self.projectiles.update(self.world, dt, controls.aim, bodies)
        healing = self.projectiles.take_healing()
        if healing and not self.player.dead:
            self.player.hp = min(self.player.max_hp, self.player.hp + healing)
        for blast in blasts:
            self._apply_blast(blast, bodies)
            self.events.append("blast_big" if blast.radius >= 12 else "blast")
        self._hurt_cooldown = max(0.0, self._hurt_cooldown - dt)
        if self.player.hp < self._last_hp - 1.0 and self._hurt_cooldown <= 0:
            self.events.append("hurt")
            self._hurt_cooldown = 0.25
        self._perk_reactions(dt)

        if self.player.dead and not self.outcome:
            if "zweiter_puls" in self.perks and not self.revive_used:
                self.revive_used = True
                self.player.hp = self.player.max_hp * 0.5
                self.player.burning = 0.0
            else:
                self.outcome = "dead"
                self.events.append("death")
        elif alive and self.exit_open and self.near_exit():
            self._descend()
        return blasts

    def near_exit(self) -> bool:
        return math.dist(self.player.center, self.level.exit) <= EXIT_RANGE

    def nearest_pickup(self) -> Pickup | None:
        return nearest_pickup(self.pickups, *self.player.center)

    def can_afford(self, item: Pickup) -> bool:
        return self.pearls >= item.price

    # ---------------------------------------------------------------- helpers

    def _step_world(self, dt: float, area: Rect | None) -> None:
        self._accumulator += dt
        steps = 0
        while self._accumulator >= SIM_DT and steps < MAX_SIM_STEPS_PER_FRAME:
            self.simulated_chunks = self.world.step(area)
            self._accumulator -= SIM_DT
            steps += 1
        if steps == MAX_SIM_STEPS_PER_FRAME:
            self._accumulator = 0.0  # too slow: drop time instead of spiralling

    def _cast(self, aim: tuple[float, float]) -> None:
        wand = self.inventory.wand
        shots = wand.cast()
        if not shots:
            return
        sx, sy = self.shoulder(aim)
        angle = math.atan2(aim[1] - sy, aim[0] - sx) + self.rng.uniform(-1, 1) * wand.spec.spread
        reach = arm_reach(len(wand.blocks))
        tip = (sx + math.cos(angle) * reach, sy + math.sin(angle) * reach)
        self.projectiles.spawn(shots, tip[0], tip[1], angle)
        self.events.append("cast")
        if "schnelle_druesen" in self.perks:
            wand.cooldown *= FAST_GLANDS
            wand.recharge_left *= FAST_GLANDS

    def _collect_pearls(self) -> None:
        cx, cy = self.player.center
        for item in [i for i in self.pickups if i.pearls]:
            if math.hypot(item.x - cx, item.y - cy) <= PICKUP_RANGE + 4:
                self.pearls += item.pearls
                self.stats["pearls"] += item.pearls
                self.pickups.remove(item)
                self.events.append("pearl")

    def _pick_up(self) -> None:
        item = self.nearest_pickup()
        if item is None:
            return
        if item.perk is not None:
            self.apply_perk(item.perk)
            self.pickups = [i for i in self.pickups if i.perk is None]
            self.events.append("perk")
            return
        if item.price:
            if not self.can_afford(item):
                return
            if item.block is not None and None not in self.inventory.bag:
                return
            self.pearls -= item.price
            item.price = 0
            self.events.append("buy")
        if item.wand is not None:
            self._discover_blocks(item.wand.blocks)
            dropped = self.inventory.add_wand(item.wand)
            self.pickups.remove(item)
            if dropped is not None:
                self.pickups.append(Pickup(item.x, item.y, wand=dropped))
            self.events.append("pickup")
        elif item.block is not None and self.inventory.add_block(item.block):
            self._discover_blocks((item.block,))
            self.pickups.remove(item)
            self.events.append("pickup")

    def _on_death(self, creature) -> None:
        cx, cy = creature.center
        self.stats["kills"] += 1
        self.discoveries.append(("creature", creature.spec.key))
        if "blutdurst" in self.perks and not self.player.dead:
            self.player.hp = min(self.player.max_hp, self.player.hp + BLOODLUST_HEAL)
        self.pickups.append(Pickup(cx, cy, pearls=creature.spec.pearls))
        self.events.append("blast_big" if creature.spec.boss else "kill")
        if creature.spec.boss:
            if self.depth.final:
                self.outcome = "victory"
                self.events.append("victory")
            else:
                self.exit_open = True
                for _ in range(2):  # bosses always drop loot
                    self.pickups.append(Pickup(cx, cy, block=random_block(self.rng)))
        elif self.rng.random() < DROP_CHANCE:
            self.pickups.append(Pickup(cx, cy, block=random_block(self.rng)))

    def _apply_blast(self, blast: Blast, bodies: list[Body]) -> None:
        reach = blast.radius + BLAST_REACH
        for body in bodies:
            distance = math.dist(body.center, (blast.x, blast.y))
            if distance < reach:
                damage = BLAST_DAMAGE * blast.radius * (1 - distance / reach)
                if body is self.player and "panzerplatten" in self.perks:
                    damage *= ARMOUR_FACTOR
                body.hurt(damage)

    def _perk_reactions(self, dt: float) -> None:
        """Perks that react to what happened this update."""
        player = self.player
        self._acid_blood_cooldown = max(0.0, self._acid_blood_cooldown - dt)
        hurt = player.hp < self._last_hp - 1.0
        if "saeureblut" in self.perks and hurt and self._acid_blood_cooldown <= 0:
            self._acid_blood_cooldown = ACID_BLOOD_COOLDOWN
            spray = [Shot(CATALOG["klumpen"], (CATALOG["sekret_saeure"],))]
            cx, cy = player.center
            for k in range(ACID_BLOOD_SPRAY):
                angle = -math.pi / 2 + (k - (ACID_BLOOD_SPRAY - 1) / 2) * 0.45
                self.projectiles.spawn(spray, cx, cy - 6, angle)
        self._last_hp = player.hp

    def _descend(self) -> None:
        self.events.append("descend")
        if self.in_sanctum:
            self.enter_depth(self.depth_index + 1)
        elif self.depth_index + 1 < len(DEPTHS):
            self.enter_sanctum()
