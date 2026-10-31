"""One run through the organism: depths, combat, loot, the way down and the outcome.

Pure game logic without pygame, so a whole run can be simulated in tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass
from typing import Any

from src.body import Body
from src.chunks import CORPSE_HEIGHT, FallingChunks
from src.depths import DEPTHS, Depth, choose_route, depth_by_key
from src.enemies import SPECIES, Creature, EnemyManager, populate, spawn_boss
from src.flask import ABSORB_RATE, CAPACITY, POUR_RATE, REACH, Droplet, Flask, ThrownFlask
from src.inventory import Inventory
from src.loot import (
    PICKUP_RANGE,
    Pickup,
    block_price,
    cocoon_loot,
    generate_wand,
    nearest_pickup,
    place_loot,
    random_block,
    scatter_pearls,
    wand_price,
)
from src.materials import (
    AIR,
    BEDROCK,
    BLOCKS_BODY,
    BLOOD,
    FLESH,
    KIND,
    LIQUID,
    MATERIAL_COUNT,
    POWDER,
)
from src.perks import PERK_BY_KEY, PERKS
from src.player import ENERGY_RECHARGE_AIR, MAX_ENERGY, MAX_HP, Player
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
EXIT_CLEAR_RADIUS = 16  # cells dug free around a boss exit when it opens
SHOULDER_OFFSET = (2.0, 1.0)  # arm root relative to the body centre (x towards the aim)
STARTER_WANDS = (PRESETS[0], PRESETS[1])
AIR_RECHARGE_PERK = 1.6  # energy per second in the air with "dauerflug"
RAGE_FACTOR = 1.3
MAGNET_RANGE = 140.0
MAGNET_SPEED = 260.0  # px/s
HAGGLE_FACTOR = 2 / 3
START_FLASK = 150  # cells of blood in the starting flask
MAX_FLASKS = 4
SPRAY_START = 9.0  # px from the shoulder where poured liquid leaves the flask
DROP_TOSS = 70.0  # px/s an item is tossed forward when dropped from the inventory
FLASKS_PER_DEPTH = 2
COCOONS_PER_DEPTH = 2
EYE_BONUS = 10  # maximum health per Urauge
SECRET_HINT_RANGE = 90.0
REROLL_PRICE = 100  # doubles with every use in a run
DEATH_SPLASH = 6
BLAST_KNOCKBACK = 30.0  # px/s per blast radius at the centre
SIGHT_RANGE = 520.0  # px the player can see along a clear line
NEAR_SIGHT = 40.0  # px: always visible this close
PLAYER_POLYMORPH_TIME = 7.0
VAULT_GUARD_POWER = 3.0  # the vault guardian's health and damage
VAULT_FLOOR_OFFSET = 18  # loot height above the vault centre's floor
WEST_DARKNESS = 0.7  # ambient light kept per western world
MIRROR_POWER = 1.8  # creature health in the mirror world
MIRROR_DAMAGE = 1.4  # creature projectile damage there
MIRROR_LOOT = 2  # extra loot levels there
NG_POWER = 0.6  # creature health per New Game+ loop
NG_DAMAGE = 0.4  # creature projectile damage per loop
KICK_COOLDOWN = 0.45
KICK_REACH = 12.0  # px in front of the player
KICK_DAMAGE = 8.0
KICK_PUSH = 260.0  # px/s
KICK_STAGGER = 0.6  # seconds a kicked creature tumbles without control
BLAST_STAGGER = 0.35
TRAPPED_TIME = 0.4  # seconds walled in on every side before the player tears free
FREE_RADIUS = 6  # cells around the body cleared when that happens
POCKET_CHECK = 1.5  # seconds of trying to move without moving before checking for a pocket
POCKET_MOVE = 3.0  # px: moving less than this counts as not moving
POCKET_SIZE = 24  # px: a cavity the body cannot leave within this range counts as sealed
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
    pour: bool = False  # flask: pour towards the cursor (held)
    absorb: bool = False  # flask: suck up liquid at the cursor (held)
    drink: bool = False  # flask: take a sip (pressed)
    throw: bool = False  # flask: throw it (pressed)
    kick: bool = False  # kick whatever is in front of you (pressed)


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
        self.discoveries: list[tuple[str, str]] = []  # ("block"|"creature", key), drained by the game
        self.checkpoint: dict[str, Any] | None = None  # state at the last sanctum entry
        # Kodex unlocks, set by the game before a run starts:
        self.favoured_blocks: frozenset[str] = frozenset()  # likelier in the shop
        self.start_pearls = 0  # blood pearls at the start of a run
        self.flasks: list[Flask] = []
        self.flask_index = 0
        self.last_aim = (0.0, 0.0)
        self.sandbox = False  # a test run from the title menu: wands editable everywhere
        self.god_mode = False  # sandbox: the player cannot die
        self.thrown: list[ThrownFlask] = []
        self.droplets: list[Droplet] = []
        self.chunks = FallingChunks()
        self.messages: list[str] = []  # short German notes for the HUD, drained by the game
        self.log: list[tuple[str, dict[str, Any]]] = []  # run log entries, drained by the game
        self.cast_counts: dict[str, int] = {}  # casts per wand in the current depth
        self._damage: dict[str, float] = {}  # player damage by cause since the last flush
        self._damage_timer = 0.0
        self._flask_budget = 0.0
        self._pouring = False
        self._trapped = 0.0
        self._still_at, self._still_time = (0, 0), 0.0
        self._kick_cooldown = 0.0
        self.new_run()

    # ---------------------------------------------------------------- flow

    @property
    def depth(self) -> Depth:
        return SANCTUM if self.in_sanctum else self.route[self.depth_index]

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
        self.pearls = self.start_pearls
        self.flasks = [Flask(BLOOD, START_FLASK)]
        self.flask_index = 0
        self.eyes = 0  # Uraugen found this run
        self.ng = 0  # New Game+ loop (0 = first descent)
        self.route = choose_route(self.rng)  # the biome of every stage in this run
        # parallel world: 0 = the main world, positive = east, negative = west (darker);
        # odd worlds are mirrored
        self.parallel = 0
        self.projectiles.enemy_damage = 1.0
        self.reroll_price = REROLL_PRICE
        self.thrown = []
        self.droplets = []
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
        self._apply_perk_flags()

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
        self._apply_perk_flags()

    def _apply_perk_flags(self) -> None:
        """Perk effects that are plain switches (re-applied after loading a run)."""
        player, perks = self.player, self.perks
        player.fire_immune = player.fire_immune or "feuerfest" in perks
        player.acid_immune = player.acid_immune or "saeurehaut" in perks
        player.gas_immune = "gaslunge" in perks
        player.mucus_immune = "schleimlaeufer" in perks
        player.air_recharge = AIR_RECHARGE_PERK if "dauerflug" in perks else ENERGY_RECHARGE_AIR
        self.projectiles.player_damage = RAGE_FACTOR if "wutdruesen" in perks else 1.0

    @property
    def flask(self) -> Flask | None:
        """The flask in hand (pour, drink, throw); None if you carry none."""
        if not self.flasks:
            return None
        self.flask_index = min(self.flask_index, len(self.flasks) - 1)
        return self.flasks[self.flask_index]

    @flask.setter
    def flask(self, flask: Flask | None) -> None:
        if flask is None:
            if self.flasks:
                self.flasks.pop(min(self.flask_index, len(self.flasks) - 1))
                self.flask_index = max(0, min(self.flask_index, len(self.flasks) - 1))
        elif self.flasks:
            self.flasks[min(self.flask_index, len(self.flasks) - 1)] = flask
        else:
            self.flasks = [flask]
            self.flask_index = 0

    def cycle_flask(self, step: int = 1) -> None:
        if self.flasks:
            self.flask_index = (self.flask_index + step) % len(self.flasks)

    def select_flask(self, index: int) -> None:
        if 0 <= index < len(self.flasks):
            self.flask_index = index

    # ------------------------------------------------------------- logging

    def _log(self, event: str, **data: Any) -> None:
        self.log.append((event, data))

    def _flush_log(self) -> None:
        """Write the collected casts and damage of this stretch into the log."""
        if self._damage:
            damage = {
                cause or "unbekannt": round(amount, 1)
                for cause, amount in self._damage.items()
                if amount >= 0.05
            }
            self._log("schaden", ursachen=damage, leben=round(self.player.hp, 1))
            self._damage = {}
        if self.cast_counts:
            self._log("zauber", wuerfe=dict(self.cast_counts))
            self.cast_counts = {}

    def _log_place(self) -> dict[str, Any]:
        return {
            "tiefe": self.depth.key,
            "nummer": self.next_depth_number,
            "x": round(self.player.x),
            "y": round(self.player.y),
        }

    # ------------------------------------------------------------ dropping

    def _drop(self, item: Pickup) -> None:
        """Put an item from the inventory into the world in front of the player."""
        cx, cy = self.player.center
        side = 1 if self.last_aim[0] >= cx else -1
        item.x, item.y = cx, cy
        spread = self.rng.uniform(0.7, 1.3)  # a dropped stack scatters a little
        item.vx, item.vy = side * DROP_TOSS * spread, -DROP_TOSS * spread
        item.seen = True
        self.pickups.append(item)
        self.events.append("kick")
        self._log("abgelegt", gegenstand=item.label_de)

    def drop_block(self, ref) -> bool:
        """Drop the block at ``ref``; wand slots only where wands may be rebuilt."""
        if ref.kind == "wand" and not self.can_edit_wands:
            return False
        count = self.inventory.count(ref)  # a stack is dropped as a whole
        for _ in range(count):
            key = self.inventory.take(ref)
            if key is None:
                break
            self._drop(Pickup(0, 0, block=key))
        return count > 0

    def drop_wand(self, index: int) -> bool:
        spec = self.inventory.remove_wand(index)
        if spec is None:
            return False
        self._drop(Pickup(0, 0, wand=spec))
        return True

    def drop_flask(self, index: int) -> bool:
        if not 0 <= index < len(self.flasks):
            return False
        flask = self.flasks.pop(index)
        if self.flask_index >= index and self.flask_index > 0:
            self.flask_index -= 1
        self._drop(Pickup(0, 0, flask=flask))
        return True

    def inventory_drop(self, source: tuple[str, Any], target: tuple[str, Any] | None) -> str:
        """Finish a drag in the inventory screen. Returns a German note ("" if fine).

        ``source`` / ``target`` are ("slot", SlotRef), ("wand", index), ("flask", index),
        ("drop", None) or ("outside", None); dropping on "drop"/"outside" throws the
        thing into the world. Wand slots only change where wands may be rebuilt.
        """
        kind, value = source
        where = target[0] if target is not None else None
        locked = "Augmentationen umbauen geht nur im Sanktum."
        if where in ("drop", "outside"):
            if kind == "slot":
                return "" if self.drop_block(value) else locked
            if kind == "wand":
                return "" if self.drop_wand(value) else "Eine Augmentation musst du behalten."
            if kind == "flask":
                self.drop_flask(value)
            return ""
        if target is None:
            return ""
        if kind == "slot" and where == "slot":
            edit = self.can_edit_wands
            if not self.inventory.move(value, target[1], edit_wands=edit):
                return "" if edit else locked
            return ""
        if kind == "wand" and where == "wand":
            self.inventory.move_wand(value, target[1])
        elif kind == "flask" and where == "flask" and target[1] < len(self.flasks):
            a, b = value, target[1]
            flasks = self.flasks
            flasks[a], flasks[b] = flasks[b], flasks[a]
            if self.flask_index in (a, b):
                self.flask_index = b if self.flask_index == a else a
        return ""

    @property
    def can_edit_wands(self) -> bool:
        """Like Noita's Holy Mountain: rebuilding augmentations needs a sanctum (or a perk)."""
        return self.in_sanctum or self.sandbox or "flinke_haende" in self.perks

    def enter_sanctum(self) -> None:
        """The safe chamber after depth ``depth_index``: heal, shop, choose a perk."""
        self.checkpoint = self.snapshot()  # taken first, so a restore rebuilds the same shop
        self.in_sanctum = True
        layout = generate_sanctum(self.world)
        self.level = Level(layout.spawn, layout.exit, None)
        self.enemies.clear()
        self.projectiles.clear()
        self.chunks.clear()
        self.droplets = []
        self.exit_open = True
        level = self.depth_index + 2  # loot quality of the depth that follows
        offers: list[Pickup] = []
        for x, y in layout.shop[:SHOP_BLOCKS]:
            key = random_block(self.rng, favoured=self.favoured_blocks)
            offers.append(Pickup(x, y, block=key, price=block_price(key, level), floating=True))
        x, y = layout.shop[SHOP_BLOCKS]
        offers.append(
            Pickup(x, y, wand=generate_wand(self.rng, level), price=wand_price(level), floating=True)
        )
        available = [perk.key for perk in PERKS if perk.key not in self.perks]
        for (x, y), key in zip(layout.altar, self.rng.sample(available, PERK_CHOICES)):
            offers.append(Pickup(x, y, perk=key, floating=True))
        x, y = layout.altar[-1]
        offers.append(Pickup(x + 40, y, reroll=True, price=self.reroll_price, floating=True))
        self.pickups = offers
        self._flush_log()
        self._log(
            "sanktum", nach_tiefe=self.depth_index + 1, angebote=[o.label_de for o in offers],
            blutperlen=self.pearls,
        )  # fmt: skip
        self.player.place(*layout.spawn)
        self._refill_wands()
        for wand in self.inventory.wands:  # like Noita's Holy Mountain: spells are restored
            wand.refill_charges()
        self.time_in_depth = 0.0

    def enter_depth(self, index: int) -> None:
        """Generate depth ``index`` and put the player at its entrance (fully healed)."""
        self.in_sanctum = False
        self.depth_index = index
        depth = self.depth
        self.world.reseed(self.rng.randrange(2**31))
        self.level = generate_level(self.world, depth)
        if self.mirror:
            self.level = self._mirror_level(self.level)
        self.enemies.creatures = populate(
            self.world,
            self.rng,
            self.level.spawn,
            depth.walkers,
            depth.flyers,
            depth.spitters,
            depth.bloats,
            extra=depth.extra,
        )
        if depth.boss and self.level.arena is not None:
            self.enemies.creatures.append(spawn_boss(depth.boss, self.level.arena, self.rng))
        if self.ng or self.parallel:
            power = self.power
            for creature in self.enemies.creatures:
                if not creature.spec.prop:
                    creature.empower(power)
        self.exit_open = depth.boss is None
        self.pickups = place_loot(
            self.world, self.rng, self.level.spawn, depth.wands, depth.blocks,
            level=index + 1 + MIRROR_LOOT * abs(self.parallel),
            flasks=FLASKS_PER_DEPTH, hearts=1, cocoons=COCOONS_PER_DEPTH,
        )  # fmt: skip
        self.thrown = []
        self.droplets = []
        if self.level.secret is not None:
            x, y = self.level.secret
            self.pickups.append(Pickup(x, y + 2, eye=True, floating=True))
        if self.level.vault is not None:
            self._fill_vault(index)
        self.pickups += scatter_pearls(self.world, self.rng, self.level.spawn, PEARL_PILES)
        self.projectiles.clear()
        self.chunks.clear()
        self.player.place(*self.level.spawn)
        self.player.polymorphed = 0.0
        self._flush_log()
        self._log(
            "tiefe", schluessel=depth.key, name=depth.name_de, nummer=index + 1,
            parallelwelt=self.parallel, ng=self.ng, kreaturen=len(self.enemies.creatures),
            gegenstaende=len(self.pickups), leben=round(self.player.hp, 1),
            augmentationen=[
                {"name": w.spec.name_de, "bausteine": [k for k in w.slots if k]}
                for w in self.inventory.wands
            ],
        )  # fmt: skip
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
            "eyes": self.eyes,
            "ng": self.ng,
            "route": [depth.key for depth in self.route],
            "parallel": self.parallel,
            "reroll_price": self.reroll_price,
            "stats": dict(self.stats),
            "player": {
                "max_hp": player.max_hp,
                "energy_max": player.energy_max,
                "fire_immune": player.fire_immune,
                "acid_immune": player.acid_immune,
            },
            "wands": [
                {"spec": {**asdict(wand.spec), "blocks": list(wand.spec.blocks)}, "slots": list(wand.slots)}
                for wand in self.inventory.wands
            ],
            "active": self.inventory.active,
            "favoured": sorted(self.favoured_blocks),
            "bag": list(self.inventory.bag),
            "bag_counts": list(self.inventory.counts),
            "flasks": [[flask.material, flask.amount] for flask in self.flasks],
            "flask_active": self.flask_index,
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
        self.eyes = max(0, min(len(DEPTHS), int(data.get("eyes", 0))))
        self.ng = max(0, int(data.get("ng", 0)))
        self.parallel = int(data.get("parallel", 1 if data.get("mirror") else 0))
        route = [depth_by_key(key) for key in data.get("route", [])]
        if len(route) == len(DEPTHS) and all(route):
            self.route = tuple(route)
        else:
            self.route = DEPTHS
        self.projectiles.enemy_damage = self._enemy_damage()
        self.projectiles.enemy_damage = 1.0 + NG_DAMAGE * self.ng
        self.reroll_price = max(REROLL_PRICE, int(data.get("reroll_price", REROLL_PRICE)))
        self.stats = {key: data["stats"].get(key, 0) for key in self.stats}
        player = self.player
        player.max_hp = float(player_data["max_hp"])
        player.energy_max = float(player_data["energy_max"])
        player.fire_immune = bool(player_data["fire_immune"])
        player.acid_immune = bool(player_data["acid_immune"])
        self._apply_perk_flags()
        self.inventory.wands = []
        for spec, slots in wands:
            wand = Wand(spec, self.rng)
            count = len(wand.slots)
            wand.set_slots((slots + [None] * count)[:count])
            self.inventory.wands.append(wand)
        counts = data.get("bag_counts")
        self.inventory.set_bag(bag, counts if isinstance(counts, list) else None)
        self.inventory.select(int(data.get("active", 0)))
        self.favoured_blocks = frozenset(key for key in data.get("favoured", ()) if key in CATALOG)
        saved_flasks = data.get("flasks")
        if not isinstance(saved_flasks, list):
            saved_flasks = [data.get("flask")]  # saves from before several flasks
        self.flasks = [f for f in map(_flask_from, saved_flasks) if f is not None][:MAX_FLASKS]
        flask_active = data.get("flask_active", 0)
        self.flask_index = flask_active if isinstance(flask_active, int) else 0
        self.flask_index = max(0, min(self.flask_index, len(self.flasks) - 1))
        self.rng.setstate(rng_state)
        self.discoveries.clear()
        self.enter_sanctum()

    def _reroll_perks(self) -> None:
        """Replace the perks on the altar with a new choice (never ones already owned)."""
        spots = [(item.x, item.y) for item in self.pickups if item.perk]
        shown = {item.perk for item in self.pickups if item.perk}
        available = [p.key for p in PERKS if p.key not in self.perks and p.key not in shown]
        if len(available) < len(spots):  # few perks left: allow the current ones again
            available = [p.key for p in PERKS if p.key not in self.perks]
        self.pickups = [item for item in self.pickups if not item.perk]
        for (x, y), key in zip(spots, self.rng.sample(available, len(spots))):
            self.pickups.append(Pickup(x, y, perk=key, floating=True))

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
        self.last_aim = controls.aim
        self.time_in_depth += dt
        if not self.outcome:
            self.stats["time"] += dt
        alive = not self.player.dead and self.outcome != "victory"
        if not alive:
            controls = Controls(aim=controls.aim)
        self._clear_overlap()
        self.player.update(self.world, dt, controls.move, controls.jump, controls.levitate)
        if alive:
            self._check_trapped(dt, bool(controls.move or controls.levitate))
        for wand in self.inventory.wands:
            wand.update(dt)
        if controls.cast and self.player.polymorphed <= 0:
            self._cast(controls.aim)
        for item in self.pickups:
            item.update(self.world, dt)
        if alive:
            self._collect_pearls(dt)
        if controls.pickup:
            self._pick_up()
        if alive and self.player.polymorphed <= 0:
            self._use_flask(controls, dt)
        self._kick_cooldown = max(0.0, self._kick_cooldown - dt)
        if alive and controls.kick and self._kick_cooldown <= 0:
            self._kick(controls.aim)

        self._step_world(dt, area)
        everywhere = area or (0, 0, self.world.width, self.world.height)
        died = self.enemies.update(self.world, dt, self.player, self.projectiles, everywhere)
        self._prop_blasts: list[Blast] = []
        for creature in died:
            self._on_death(creature)
        bodies: list[Body] = [self.player, *self.enemies.creatures]
        for thrown in self.thrown:
            if thrown.update(self.world, dt, bodies[1:]):
                self.events.append("shatter")
        self.thrown = [t for t in self.thrown if t.alive]
        for drop in self.droplets:
            drop.update(self.world, dt, self.player)
        self.droplets = [d for d in self.droplets if d.alive]
        blasts = self.projectiles.update(self.world, dt, controls.aim, bodies) + self._prop_blasts
        if self.projectiles.teleports:
            tx, ty = self.projectiles.teleports[-1]
            self.projectiles.teleports.clear()
            if alive:
                self._teleport(tx, ty)
        self._resolve_polymorphs()
        if self.projectiles.swaps:
            victim = self.projectiles.swaps[-1]
            self.projectiles.swaps.clear()
            if alive and not victim.dead:
                self._swap_with(victim)
        healing = self.projectiles.take_healing()
        if healing and not self.player.dead:
            self.player.hp = min(self.player.max_hp, self.player.hp + healing)
        for blast in blasts:
            self._apply_blast(blast, bodies)
            self.chunks.detach(self.world, blast.x, blast.y, blast.radius)
            self.events.append("blast_big" if blast.radius >= 12 else "blast")
        if self.chunks.update(self.world, dt, bodies):
            self.events.append("kick")  # a dull thud as tissue lands
        lost = self._last_hp - self.player.hp
        if lost > 0:
            cause = self.player.last_cause
            self._damage[cause] = self._damage.get(cause, 0.0) + lost
        self._damage_timer += dt
        if self._damage_timer >= 5.0:
            self._damage_timer = 0.0
            if self._damage:
                self._flush_log()
        self._hurt_cooldown = max(0.0, self._hurt_cooldown - dt)
        if self.player.hp < self._last_hp - 1.0 and self._hurt_cooldown <= 0:
            self.events.append("hurt")
            self._hurt_cooldown = 0.25
        self._perk_reactions(dt)

        if self.god_mode:
            player = self.player
            player.hp = player.max_hp
            player.burning = player.poisoned = 0.0
        if self.player.dead and not self.outcome:
            self._flush_log()
            if "zweiter_puls" in self.perks and not self.revive_used:
                self._log("wiederbelebt", ursache=self.player.last_cause, **self._log_place())
                self.revive_used = True
                self.player.hp = self.player.max_hp * 0.5
                self.player.burning = 0.0
            else:
                self.outcome = "dead"
                self._log(
                    "tod", ursache=self.player.last_cause, zeit=round(self.stats["time"], 1),
                    getoetet=self.stats["kills"], **self._log_place(),
                )  # fmt: skip
                self.events.append("death")
                cx, cy = self.player.center
                self.world.splash(int(cx), int(cy), DEATH_SPLASH, BLOOD)
        elif alive and self.exit_open and self.near_exit():
            self._descend()
        return blasts

    @property
    def true_ending(self) -> bool:
        """Won with every Urauge: the organism is not just dead, it is yours."""
        return self.outcome == "victory" and self.eyes >= len(DEPTHS)

    def near_secret(self, distance: float = SECRET_HINT_RANGE) -> bool:
        secret = self.level.secret
        return (
            secret is not None
            and any(item.eye for item in self.pickups)
            and math.dist(self.player.center, secret) <= distance
        )

    def update_visibility(self) -> set[int]:
        """Reveal pickups the player can see; returns ids of creatures in sight.

        Like Noita's darkness, what lies behind solid tissue stays hidden: sealed
        chambers and vaults do not give themselves away.
        """
        player, world = self.player, self.world
        cx, cy = player.center
        for item in self.pickups:
            if item.seen or item.floating and not (item.eye or item.portal):
                item.seen = True  # shop items and altar perks are always on display
                continue
            close = math.hypot(item.x - cx, item.y - cy) <= NEAR_SIGHT
            if close or player.can_see(world, item.x, item.y - 2, SIGHT_RANGE):
                item.seen = True
        visible = set()
        for creature in self.enemies.creatures:
            ox, oy = creature.center
            near = creature.spec.boss or math.hypot(ox - cx, oy - cy) <= NEAR_SIGHT
            if near or player.can_see(world, ox, oy, SIGHT_RANGE):
                visible.add(id(creature))
        return visible

    def near_exit(self) -> bool:
        return math.dist(self.player.center, self.level.exit) <= EXIT_RANGE

    def nearest_pickup(self) -> Pickup | None:
        return nearest_pickup(self.pickups, *self.player.center)

    def price_of(self, item: Pickup) -> int:
        """What an item costs the player right now (the "feilscher" perk haggles)."""
        if "feilscher" in self.perks:
            return max(1, round(item.price * HAGGLE_FACTOR)) if item.price else 0
        return item.price

    def can_afford(self, item: Pickup) -> bool:
        return self.pearls >= self.price_of(item)

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
        name = wand.spec.name_de
        self.cast_counts[name] = self.cast_counts.get(name, 0) + 1
        if "schnelle_druesen" in self.perks:
            wand.cooldown *= FAST_GLANDS
            wand.recharge_left *= FAST_GLANDS

    def _fill_vault(self, index: int) -> None:
        """Treasure and a strengthened guardian inside the depth's bone vault."""
        x, y = self.level.vault
        floor = y + VAULT_FLOOR_OFFSET
        self.pickups += [
            Pickup(x - 20, floor, wand=generate_wand(self.rng, index + 3)),
            Pickup(x + 20, floor, block=random_block(self.rng)),
            Pickup(x + 30, floor, block=random_block(self.rng)),
            Pickup(x - 32, floor, pearls=60 * (index + 1) * (1 + abs(self.parallel))),
        ]
        if index == 0 and not self.ng:  # the way into the next parallel world
            self.pickups.append(Pickup(x, y - 4, portal=True, floating=True))
        options = [s for s in SPECIES.values() if not s.boss and not s.prop and s.flying]
        spec = self.rng.choice(options)
        guardian = Creature(spec, x - spec.width // 2, y - spec.height // 2 - 6, self.rng)
        guardian.empower(VAULT_GUARD_POWER * self.power)
        self.enemies.creatures.append(guardian)

    def _resolve_polymorphs(self) -> None:
        """Creatures hit by a polymorph bolt become a random other (non-boss) species."""
        victims, self.projectiles.polymorphs = self.projectiles.polymorphs, []
        for victim in victims:
            if victim is self.player:
                if not self.player.dead:
                    self.player.polymorphed = PLAYER_POLYMORPH_TIME
                    self.messages.append("Du bist zu einer Made geworden!")
                    self.events.append("teleport")
                continue
            if victim not in self.enemies.creatures or victim.dead or victim.spec.boss:
                continue
            options = [s for s in SPECIES.values() if not s.boss and s.key != victim.spec.key]
            spec = self.rng.choice(options)
            cx, cy = victim.center
            new = Creature(spec, int(cx - spec.width / 2), int(cy - spec.height / 2), self.rng)
            new.alerted = not spec.prop
            index = self.enemies.creatures.index(victim)
            self.enemies.creatures[index] = new
            self.events.append("teleport")

    def _swap_with(self, victim: Body) -> None:
        player = self.player
        (px, py), (vx, _vy) = player.center, victim.center
        tx = int(vx - player.width / 2)
        feet = victim.y + victim.height  # stand where the creature stood
        for lift in range(0, 14, 2):
            ty = feet - player.height - lift
            if not player.blocked(self.world, tx, ty):
                break
        else:
            return  # the player would not fit where the creature was
        player.x, player.y = tx, ty
        victim.x, victim.y = int(px - victim.width / 2), int(py - victim.height / 2)
        player.vx = player.vy = 0.0
        self.events.append("teleport")

    @property
    def power(self) -> float:
        """How much tougher creatures are (New Game+ loops and parallel worlds)."""
        return (1.0 + NG_POWER * self.ng) * (1.0 + (MIRROR_POWER - 1.0) * abs(self.parallel))

    @property
    def mirror(self) -> bool:
        """Odd parallel worlds are mirrored left to right."""
        return abs(self.parallel) % 2 == 1

    @property
    def darkness(self) -> float:
        """Western worlds are darker: a factor on the depth's ambient light."""
        return WEST_DARKNESS ** abs(self.parallel) if self.parallel < 0 else 1.0

    def _mirror_level(self, level: Level) -> Level:
        """Flip the freshly generated depth and every position in it."""
        self.world.mirror()
        w = self.world.width

        def flip(point: tuple[int, int] | None, width: int = 0) -> tuple[int, int] | None:
            return None if point is None else (w - 1 - point[0] - width, point[1])

        return Level(
            flip(level.spawn, self.player.width - 1), flip(level.exit), flip(level.arena),
            flip(level.secret), flip(level.vault),
        )  # fmt: skip

    def _enemy_damage(self) -> float:
        return (1.0 + NG_DAMAGE * self.ng) * (1.0 + (MIRROR_DAMAGE - 1.0) * abs(self.parallel))

    def enter_mirror(self) -> None:
        """Step through a portal: the run starts over in the next parallel world.

        Like Noita, the direction matters: a portal at the east edge leads further east,
        one at the west edge further west.
        """
        east = self.level.vault is None or self.level.vault[0] >= self.world.width // 2
        if self.parallel == 0:
            self.parallel = 1 if east else -1
        else:
            self.parallel += 1 if self.parallel > 0 else -1
        self.route = choose_route(self.rng)
        self.projectiles.enemy_damage = self._enemy_damage()
        side = "Ost" if self.parallel > 0 else "West"
        self.messages.append(
            f"Parallelwelt {side} {abs(self.parallel)}: "
            + ("finsterer, " if self.parallel < 0 else "")
            + ("alles verkehrt, " if self.mirror else "")
            + "alles stärker, alles reicher."
        )
        self.events.append("descend")
        self.enter_depth(0)

    def new_game_plus(self) -> None:
        """After a victory: descend again with everything you carry, against tougher flesh."""
        if self.outcome != "victory":
            return
        self.ng += 1
        self.route = choose_route(self.rng)  # a new way down
        self.outcome = ""
        self.eyes = 0
        self.projectiles.enemy_damage = self._enemy_damage()
        self.player.hp = self.player.max_hp
        self.messages.append(f"Neues Spiel+ {self.ng}: Das Fleisch ist zäher geworden.")
        self.events.append("descend")
        self.enter_depth(0)

    def _clear_overlap(self) -> None:
        """Material that appeared inside the player's body is pushed out of it.

        Reactions, splashes and growth do not know about bodies; a cell that lands
        inside the player would otherwise lock it in. Powders are moved above the
        body, solids that grew into it are removed.
        """
        player, world = self.player, self.world
        for y in range(player.y, player.y + player.height):
            for x in range(player.x, player.x + player.width):
                cell = world.get(x, y)
                if not BLOCKS_BODY[cell] or cell == BEDROCK:
                    continue
                world.set_cell(x, y, AIR)
                if KIND[cell] == POWDER:
                    for up in range(1, 8):
                        if world.get(x, player.y - up) == AIR:
                            world.set_cell(x, player.y - up, cell)
                            break

    def _check_trapped(self, dt: float, trying: bool) -> None:
        """Walled in (a crust, growth or debris shell around the body): tear free.

        Fully stuck is noticed at once; a small sealed pocket is noticed when the
        player tries to move for a while without getting anywhere.
        """
        player, world = self.player, self.world
        x, y, step = player.x, player.y, player.step_up
        stuck = (
            player.blocked(world, x, y - 1)
            and player.blocked(world, x, y + 1)
            and all(player.blocked(world, x + side, y - up) for side in (-1, 1) for up in range(step + 1))
        )
        self._trapped = self._trapped + dt if stuck else 0.0
        if math.dist((x, y), self._still_at) > POCKET_MOVE:
            self._still_at, self._still_time = (x, y), 0.0
        elif trying:
            self._still_time += dt
        if self._still_time >= POCKET_CHECK:
            self._still_time = 0.0
            if self._sealed_pocket():
                self._trapped = TRAPPED_TIME
        if self._trapped < TRAPPED_TIME:
            return
        self._trapped = 0.0
        cx, cy = player.center
        radius = max(player.width, player.height) // 2 + FREE_RADIUS
        self.world.dig(int(cx), int(cy), radius, force=True)
        self.messages.append("Du reißt dich frei.")
        self.events.append("kick")
        self._log("befreit", **self._log_place())

    def _sealed_pocket(self) -> bool:
        """Is the player shut in a small cavity it cannot leave?"""
        player, world = self.player, self.world
        start = (player.x, player.y)
        seen, queue = {start}, [start]
        while queue:
            x, y = queue.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) in seen or player.blocked(world, nx, ny):
                    continue
                if abs(nx - start[0]) > POCKET_SIZE or abs(ny - start[1]) > POCKET_SIZE:
                    return False  # got out of the neighbourhood: not sealed in
                seen.add((nx, ny))
                queue.append((nx, ny))
        return True

    def _kick(self, aim: tuple[float, float]) -> None:
        """Kick towards the cursor side: hurts and shoves creatures, bursts sacs, flings items."""
        self._kick_cooldown = KICK_COOLDOWN
        self.events.append("kick")
        player = self.player
        cx, cy = player.center
        side = 1 if aim[0] >= cx else -1
        reach_x = cx + side * (player.width / 2 + KICK_REACH / 2)
        for creature in self.enemies.creatures:
            ox, oy = creature.center
            if abs(ox - reach_x) <= KICK_REACH / 2 + creature.width / 2 and abs(oy - cy) <= creature.height / 2 + 6:
                creature.hurt(KICK_DAMAGE, "Tritt")
                if not creature.spec.boss and not creature.spec.stationary:
                    creature.vx = side * KICK_PUSH
                    creature.vy = -KICK_PUSH * 0.6
                    creature.stagger = KICK_STAGGER
        for item in self.pickups:
            if not item.floating and abs(item.x - reach_x) <= KICK_REACH and abs(item.y - cy) <= 12:
                item.vy = -KICK_PUSH * 0.8
                item.vx = side * KICK_PUSH
        # loose powder and liquid in front of the feet is scattered too
        foot_y = player.y + player.height - 2
        for dy in range(-6, 2):
            for dx in range(2, int(KICK_REACH)):
                x, y = int(cx + side * (player.width / 2 + dx)), foot_y + dy
                cell = self.world.get(x, y)
                if KIND[cell] in (POWDER, LIQUID) and self.world.get(x + side * 4, y - 3) == AIR:
                    self.world.set_cell(x, y, AIR)
                    self.world.set_cell(x + side * 4, y - 3, cell)

    def _teleport(self, tx: float, ty: float) -> None:
        """Move the player to (tx, ty) if the body fits there or a little above."""
        player = self.player
        x, y = int(tx - player.width / 2), int(ty - player.height / 2)
        for lift in range(0, 12, 2):
            if not player.blocked(self.world, x, y - lift):
                player.x, player.y = x, y - lift
                player.vx = player.vy = 0.0
                self.events.append("teleport")
                return

    def _use_flask(self, controls: Controls, dt: float) -> None:
        flask = self.flask
        if flask is None:
            self._flask_budget = 0.0
            return
        sx, sy = self.shoulder(controls.aim)
        angle = math.atan2(controls.aim[1] - sy, controls.aim[0] - sx)
        if controls.throw:
            self._log("werfen", phiole=flask.label_de)
            self.thrown.append(ThrownFlask.throw(flask, sx, sy, angle))
            self.flask = None
            self.events.append("cast")
            return
        if controls.drink:
            message = flask.drink(self.player)
            if message:
                self._log("trinken", phiole=flask.label_de)
                self.messages.append(message)
                self.events.append("drink")
        if controls.pour or controls.absorb:
            self._flask_budget += (POUR_RATE if controls.pour else ABSORB_RATE) * dt
            budget = int(self._flask_budget)
            self._flask_budget -= budget
            if controls.pour:
                if not self._pouring:
                    self._log("giessen", phiole=flask.label_de)
                reach = max(SPRAY_START, arm_reach(len(self.inventory.wand.blocks)))
                tip = (sx + math.cos(angle) * reach, sy + math.sin(angle) * reach)
                self.droplets += flask.spray(*tip, angle, budget, self.rng)
            else:
                distance = min(REACH, math.dist((sx, sy), controls.aim))
                tx = int(sx + math.cos(angle) * distance)
                ty = int(sy + math.sin(angle) * distance)
                flask.absorb(self.world, tx, ty, budget)
        else:
            self._flask_budget = 0.0
        self._pouring = controls.pour

    def _collect_pearls(self, dt: float) -> None:
        cx, cy = self.player.center
        magnet = "perlenmagnet" in self.perks
        for item in [i for i in self.pickups if i.pearls]:
            distance = math.hypot(item.x - cx, item.y - cy)
            if magnet and distance <= MAGNET_RANGE:
                pull = min(1.0, MAGNET_SPEED * dt / max(distance, 1.0))
                item.x += (cx - item.x) * pull
                item.y += (cy - item.y) * pull
                item.vy = 0.0
                distance = math.hypot(item.x - cx, item.y - cy)
            if distance <= PICKUP_RANGE + 4:
                self.pearls += item.pearls
                self.stats["pearls"] += item.pearls
                self.pickups.remove(item)
                self.events.append("pearl")

    def _pick_up(self) -> None:
        item = self.nearest_pickup()
        if item is None:
            return
        self._log("aufheben", gegenstand=item.label_de, preis=self.price_of(item), perlen=self.pearls)
        if item.perk is not None:
            self.apply_perk(item.perk)
            self.pickups = [i for i in self.pickups if i.perk is None and not i.reroll]
            self.events.append("perk")
            return
        if item.portal:
            self.pickups.remove(item)
            self.enter_mirror()
            return
        if item.reroll:
            if not any(i.perk for i in self.pickups) or not self.can_afford(item):
                return
            self.pearls -= self.price_of(item)
            self.reroll_price *= 2
            item.price = self.reroll_price
            self._reroll_perks()
            self.events.append("buy")
            return
        if item.price:
            if not self.can_afford(item):
                return
            if item.block is not None and not self.inventory.can_add(item.block):
                return
            self.pearls -= self.price_of(item)
            item.price = 0
            self.events.append("buy")
        if item.eye:
            self.pickups.remove(item)
            self.eyes += 1
            self.player.max_hp += EYE_BONUS
            self.player.hp = self.player.max_hp
            self.messages.append(f"Ein Urauge öffnet sich in dir ({self.eyes}/{len(DEPTHS)}).")
            self.events.append("victory" if self.eyes == len(DEPTHS) else "perk")
            return
        if item.heart:
            self.pickups.remove(item)
            self.player.max_hp += item.heart
            self.player.hp = self.player.max_hp
            self.messages.append(f"Dein Herz wächst: +{item.heart} maximales Leben.")
            self.events.append("perk")
            return
        if item.cocoon:
            self.pickups.remove(item)
            self.pickups += cocoon_loot(self.rng, item.x, item.y - 4, self.depth_index + 1)
            self.events.append("shatter")
            return
        if item.flask is not None:
            self.pickups.remove(item)
            if len(self.flasks) < MAX_FLASKS:
                self.flasks.append(item.flask)
                self.flask_index = len(self.flasks) - 1
            else:  # hands full: swap with the flask in hand
                self.pickups.append(Pickup(item.x, item.y, flask=self.flask, seen=True))
                self.flask = item.flask
            self.events.append("pickup")
            return
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
        if creature.spec.prop:  # a burst sac: no kill, but maybe a chain reaction
            if creature.spec.blast:
                self.world.explode(int(cx), int(cy), creature.spec.blast)
                self._prop_blasts.append(Blast(int(cx), int(cy), creature.spec.blast))
            self.events.append("shatter")
            return
        self.stats["kills"] += 1
        self._log("getoetet", kreatur=creature.spec.key, durch=creature.last_cause)
        self.discoveries.append(("creature", creature.spec.key))
        if not creature.spec.boss and creature.spec.gore == BLOOD:
            width = max(3, creature.width - 2)
            self.chunks.drop_corpse(
                self.world, int(cx - width / 2), int(creature.y + creature.height - CORPSE_HEIGHT),
                width, FLESH,
            )  # fmt: skip
        if "blutdurst" in self.perks and not self.player.dead:
            self.player.hp = min(self.player.max_hp, self.player.hp + BLOODLUST_HEAL)
        self.pickups.append(Pickup(cx, cy, pearls=creature.spec.pearls))
        self.events.append("blast_big" if creature.spec.boss else "kill")
        if creature.spec.boss:
            self._log("waechter_besiegt", kreatur=creature.spec.key, zeit=round(self.stats["time"], 1))
            if self.depth.final:
                self.outcome = "victory"
                self.events.append("victory")
            else:
                self.exit_open = True
                # Whatever the fight left at the exit (growth, scab, bone) is cleared away.
                self.world.dig(
                    int(self.level.exit[0]), int(self.level.exit[1]), EXIT_CLEAR_RADIUS, force=True
                )
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
                body.hurt(damage, "Explosion")
                # knockback: lighter bodies fly further, bosses barely move
                strength = BLAST_KNOCKBACK * blast.radius * (1 - distance / reach)
                mass = max(1.0, (body.width * body.height) ** 0.5 / 4)
                if getattr(getattr(body, "spec", None), "boss", False):
                    mass *= 8
                dx, dy = body.center[0] - blast.x, body.center[1] - blast.y
                norm = math.hypot(dx, dy) or 1.0
                body.vx += dx / norm * strength / mass
                body.vy += dy / norm * strength / mass - strength / mass * 0.3
                if hasattr(body, "stagger") and not body.spec.boss and strength / mass > 40:
                    body.stagger = max(body.stagger, BLAST_STAGGER)
        for item in self.pickups:  # loose items fly too
            if item.floating:
                continue
            distance = math.hypot(item.x - blast.x, item.y - blast.y)
            if distance < reach:
                strength = BLAST_KNOCKBACK * blast.radius * (1 - distance / reach) * 0.6
                norm = distance or 1.0
                item.vx += (item.x - blast.x) / norm * strength
                item.vy += (item.y - blast.y) / norm * strength - strength * 0.5

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


def _flask_from(data: object) -> Flask | None:
    """Rebuild a saved flask; anything odd gives no flask rather than an error."""
    if not isinstance(data, list) or len(data) != 2:
        return None
    material, amount = data
    if material is None:
        return Flask()
    if not isinstance(material, int) or not isinstance(amount, int):
        return None
    if not 0 <= material < MATERIAL_COUNT or KIND[material] != LIQUID:
        return None
    return Flask(material, max(0, min(CAPACITY, amount)))
