"""One run through the organism: depths, combat, loot, the way down and the outcome.

Pure game logic without pygame, so a whole run can be simulated in tests.
"""

from __future__ import annotations

import base64
import math
import random
import zlib
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from typing import Any

from src import materials as mat
from src import native
from src.authority import Wanted
from src.body import ENEMY_TEAM, PLAYER_TEAM, Body
from src.bosses import BossScript, make_boss_script
from src.bosses.evil_selves import (
    ECHO_HP_FACTOR,
    EVIL_HP,
    apply_empress_bargain,
    echo_for_depth,
    final_evil_self,
)
from src.bosses.headquarters import (
    HeadquartersController,
    can_enter_headquarters,
    generate_headquarters_arena,
)
from src.authority import AGENT_GOLD, BADGE_CHANCE, FORBIDDEN_BLOCKS, spawn_agents
from src.challenges import QUESTS, Challenge, Quest, quest_for
from src.chunks import CORPSE_HEIGHT, RIGID, FallingChunks
from src.depths import DEPTHS, Depth, choose_route, depth_by_key
from src.economy import boss_gold, creature_gold, mid_boss_gold
from src.enemies import SPECIES, Creature, EnemyManager, populate, spawn_boss
from src.events import Event
from src.flask import ABSORB_RATE, CAPACITY, POUR_RATE, REACH, Droplet, Flask, ThrownFlask
from src.hud import SpeechBubble
from src.inventory import Inventory
from src.klonita import Klonita
from src.klonita_lines import line_for
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
    DEBRIS,
    HARDNESS,
    KIND,
    LIQUID,
    POWDER,
    SOLID,
)
from src.perks import PERK_BY_KEY, PERKS
from src.player import ENERGY_RECHARGE_AIR, MAX_ENERGY, MAX_HP, Player
from src.projectiles import Blast, ProjectileSystem
from src.projectiles import build as build_projectile
from src.records import Records
from src.rules import RULE_KEYS, Rule, apply_player_rules
from src.settings import MAX_SIM_STEPS_PER_FRAME, SIM_HZ, WORLD_HEIGHT, WORLD_WIDTH
from src.spells import CATALOG, Block, resolve_payload_material
from src.universes import features as universe_features
from src.universes.catalog import BY_KEY as UNIVERSE_BY_KEY
from src.universes.catalog import MID_BOSSES, UNIVERSES
from src.universes.gen import evil_homes
from src.universes.gen.common import region_bands
from src.universes.model import SHAPES, Universe
from src.wand import PRESETS, Shot, Wand, WandSpec
from src.workshop import WorkshopLayout
from src.world import World
from src.worldgen import Level, ensure_path, generate_level, generate_sanctum

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
SPECK_INTERVAL = 0.2  # seconds between sweeps for floating specks around the player
SPECK_RADIUS = 70  # px around the player swept for specks
SPECK_MAX = 8  # cells: free-floating bits up to this size crumble away
CRUSH_MAX = 4  # cells: a thinner obstacle in the player's way is pushed aside
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
    klonita: bool = False  # [K]: call Klonita or send her away (pressed)


def arm_reach(block_count: int) -> float:
    """Length of the augmentation arm (it grows with the number of blocks)."""
    return 7 + block_count * 1.5


class Run:
    def __init__(
        self,
        seed: int | None = None,
        width: int = WORLD_WIDTH,
        height: int = WORLD_HEIGHT,
        *,
        universe_key: str = "fleischwelt",
        boss_slot: bool = False,
    ) -> None:
        self.seed = seed if seed is not None else 0
        self.universe_key = universe_key
        self.boss_slot = boss_slot  # Contract V9 "Bossplatz"; the spawn logic comes with Card D10
        self.rng = random.Random(seed)
        self.klonita_rng = random.Random(seed * 71 + 13)  # her lines never touch the world
        self.default_size = (width, height)
        self.universe: Universe = UNIVERSE_BY_KEY.get(universe_key, UNIVERSES[0])
        if self.universe_key != "fleischwelt" and getattr(self.universe, "material_set", None):
            mat.activate_key(self.universe.material_set)
        else:
            mat.activate_key(mat.DEFAULT_SET.key)
        self.world = World(width, height, seed=self.rng.randrange(2**31))
        self.player = Player(0, 0)
        self.enemies = EnemyManager()
        self.projectiles = ProjectileSystem()
        self.projectiles.payload_resolver = self._resolve_payload
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
        self.stats = {"kills": 0, "pearls": 0, "time": 0.0, "samples": 0, "quests": 0, "bosses": 0}
        self._last_hp = 0.0
        self._acid_blood_cooldown = 0.0
        self.events: list[str] = []  # sound cues of the last update
        self._hurt_cooldown = 0.0
        self._accumulator = 0.0
        self.discoveries: list[
            tuple[str, str]
        ] = []  # ("block"|"creature", key), drained by the game
        self.checkpoint: dict[str, Any] | None = None  # state at the last sanctum entry
        # Kodex unlocks, set by the game before a run starts:
        self.favoured_blocks: frozenset[str] = frozenset()  # likelier in the shop
        self.start_pearls = 0  # blood pearls at the start of a run
        self.flasks: list[Flask] = []
        self.flask_index = 0
        self.last_aim = (0.0, 0.0)
        self.known_blocks: set[str] = set()  # blocks in the Kodex (unknown ones are marked)
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
        self._speck_timer = 0.0
        self._still_at, self._still_time = (0, 0), 0.0
        self._kick_cooldown = 0.0
        # called with the depth's name before a (possibly slow) world generation
        self.on_generate: Callable[[str], None] | None = None
        self.rule = Rule()  # the universe rule of the current depth (src/rules)
        self.memory_shards: int = 0
        self.blueprint_shards: int = 0
        self.badges: int = 0
        self.listeners: list[Callable[[str, dict[str, Any]], None]] = []
        self.emitted_events: list[tuple[str, dict[str, Any]]] = []
        self.price_factor: float = 1.0
        self.next_boost: str = ""
        self.in_workshop: bool = False
        self.in_headquarters: bool = False
        self.in_final: bool = False  # the final fight in the evil self's home world (F19)
        self._final_timers: dict[str, float] = {}
        self._press_cells: list[tuple[int, int, int, int]] = []  # strips a press fills now
        self.victory: bool = False
        self._true_ending_flag: bool = False
        self.menu_mode: str = ""
        self.listeners: list[Callable[[str, dict[str, Any]], None]] = []
        self.emitted_events: list[tuple[str, dict[str, Any]]] = []
        self.quest: Quest | None = None  # the universe's challenge (Contract V13b)
        self.ending: str = ""  # "normal", "wahr" or "boese" once the run is over (V17)
        self.extra_scripts: list[BossScript] = []  # echoes and headquarters bosses
        self.hq_controller: HeadquartersController | None = None
        self._bell_cooldown = 0.0
        self.listeners.append(self._on_bus_event)
        self.grudges: set[tuple[str, str]] = set()
        self.wanted: Wanted = Wanted()
        self.klonita: Klonita = Klonita()
        self.bubbles: list[SpeechBubble] = []
        self._say_clock: dict[str, float] = {}  # speaker -> run time of the last bubble
        self._low_hp_warned = False
        self._wanted_warned = False
        self.boss_banner: tuple[str, float] | None = None
        self.workshop_layout: WorkshopLayout | None = None
        self.event: Event | None = None
        self.event_timer: float = 0.0
        self.challenge: Challenge | None = None
        self.plan: Any = None  # the route through the multiverse (always there, V17)
        self.multiverse = False  # True: a multiverse run; False: the old organism descent
        self.fabricator: Any = None
        self.couch_used: bool = False
        self.minigames_played: set[str] = set()
        self.active_minigame: Any = None
        self.minigame_tool = "blast"  # Physik-o-Mat tool chosen with [1]-[4]
        self.experiment_picked: bool = False
        self.experiment_offers: list[str] = []
        self.experiment_rerolls: int = 0
        self.dummy_damage_total: float = 0.0
        self.active_traders: list[Any] = []
        self.trader_offers: dict[str, list[Any]] = {}
        self.selected_trader_key: str = ""
        self.active_trader_key: str = ""
        self.selected_offer_index: int = 0
        self.menu_index: int = 0
        self.inventory_open: bool = False
        self.boss_script: BossScript | None = None
        self.records: Records = Records()
        self._gold_vein_remainder: int = 0
        self.universe: Universe = UNIVERSE_BY_KEY.get(universe_key, UNIVERSES[0])
        self.portal_index: int = 0
        self.new_run()

    @property
    def traders(self) -> list[Any]:
        return self.active_traders

    @traders.setter
    def traders(self, val: list[Any]) -> None:
        self.active_traders = val

    # ---------------------------------------------------------------- flow

    @property
    def depth(self) -> Depth:
        return SANCTUM if self.in_sanctum else self.route[self.depth_index]

    @property
    def next_depth_number(self) -> int:
        """Number shown in the HUD: the depth we are in (or about to enter from a sanctum)."""
        return self.depth_index + (2 if self.in_sanctum else 1)

    def start_multiverse_run(self) -> None:
        """Start a run in the workshophub with universe progression (Card G14)."""
        from src.spells import blocks_of_tier
        from src.universes.plan import RunPlan

        self._reset()
        self.plan = RunPlan(self.seed)
        self.multiverse = True
        self.portal_index = 0
        for k in blocks_of_tier(1):
            self.records.discover("blueprint", k)
        self.enter_workshop()

    def new_run(self) -> None:
        from src.universes.plan import RunPlan

        self.plan = RunPlan(self.seed)  # only tells which evil self belongs to this seed
        self.multiverse = False  # the old organism descent (sandbox)
        self._reset()
        if self.universe_key != "fleischwelt":
            # a single universe outside a run plan (tests, bot): with its own material set,
            # rule and natives, like a universe entered through the portal
            self.enter_universe(self.universe, boss_slot=self.boss_slot)
        else:
            self.enter_depth(0)

    def _reset(self) -> None:
        """Fresh run state (starter wands, no perks) without generating a level."""
        self.inventory = Inventory(list(STARTER_WANDS), self.rng)
        self.outcome = ""
        self.pearls = self.start_pearls
        self.flasks = [Flask(mat.BLOOD, START_FLASK)]
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
        self.stats = {"kills": 0, "pearls": 0, "time": 0.0, "samples": 0, "quests": 0, "bosses": 0}
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

    def _resolve_payload(self, block: Block) -> str | None:
        return resolve_payload_material(block, self.flask, tuple(mat.KEYS), mat.BASE_KEYS, self.rng)

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

    def delete_item(self, source: tuple[str, Any]) -> str:
        """Destroy a thing from the inventory screen for good (the "Löschen" field and
        right click). Returns a German note ("" if fine)."""
        kind, value = source
        if kind == "slot":
            if value.kind == "wand" and not self.can_edit_wands:
                return "Augmentationen umbauen geht nur im Sanktum."
            while self.inventory.take(value) is not None:  # a stack goes as a whole
                pass
        elif kind == "wand":
            if self.inventory.remove_wand(value) is None:
                return "Eine Augmentation musst du behalten."
        elif kind == "flask" and 0 <= value < len(self.flasks):
            self.flasks.pop(value)
            if self.flask_index >= value and self.flask_index > 0:
                self.flask_index -= 1
        return ""

    def inventory_drop(self, source: tuple[str, Any], target: tuple[str, Any] | None) -> str:
        """Finish a drag in the inventory screen. Returns a German note ("" if fine).

        ``source`` / ``target`` are ("slot", SlotRef), ("wand", index), ("flask", index),
        ("drop", None) or ("outside", None); dropping on "drop" deletes the thing,
        dragging it out of the panel ("outside") throws it into the world. Wand slots only
        change where wands may be rebuilt.
        """
        kind, value = source
        where = target[0] if target is not None else None
        locked = "Augmentationen umbauen geht nur im Sanktum."
        if where == "drop":
            return self.delete_item(source)
        if where == "outside":
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
    def gold(self) -> int:
        """There is one currency. Workshop, traders and the old sanctum all take it; the
        code of the organism descent still calls it pearls."""
        return self.pearls

    @gold.setter
    def gold(self, value: int) -> None:
        self.pearls = int(value)

    @property
    def can_edit_wands(self) -> bool:
        """Like Noita's Holy Mountain: rebuilding augmentations needs a sanctum, the
        workshop (multiverse run) or a perk."""
        return self.in_sanctum or self.in_workshop or self.sandbox or "flinke_haende" in self.perks

    def enter_sanctum(self) -> None:
        """The safe chamber after depth ``depth_index``: heal, shop, choose a perk."""
        self.checkpoint = self.snapshot()  # taken first, so a restore rebuilds the same shop
        self.in_sanctum = True
        self._prepare_world(SANCTUM)
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
            Pickup(
                x, y, wand=generate_wand(self.rng, level), price=wand_price(level), floating=True
            )
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
        if self.on_generate is not None:
            self.on_generate(depth.name_de)
        self._prepare_world(depth)
        self.world.reseed(self.rng.randrange(2**31))
        self.boss_script = None
        self.extra_scripts = []
        self.in_headquarters = False
        self.in_final = False
        shaped: dict[str, Any] = {}
        if self.multiverse:
            # multiverse run: the proven organism generator, dressed in the universe's
            # materials (aliases of its set) and given the V9 fields (Card G19)
            organism = generate_level(self.world, depth, self.seed + index)
            rng = random.Random(self.seed * 31 + index + (self.plan.slot if self.multiverse else 0))
            sx, sy = organism.spawn  # top-left of the player's body
            body = (sx + self.player.width // 2, sy + self.player.height // 2, 14)
            keep = [body, (*organism.exit, 20)]
            shaped = universe_features.shape(self.world, self.universe.key, rng, keep, organism)
            self.level = self._dress_universe_level(organism, shaped)
            self._add_universe_features()
            self._ensure_universe_paths()
            universe_features.flood(
                self.world, self.universe.key, rng, keep + self._level_keep(), shaped
            )
            self.world.wake_all()
        elif self.universe_key != "fleischwelt":
            self.level = generate_level(
                self.world, depth, self.seed + index, universe=self.universe
            )
            # generators activate their base set; Python must use the core's (rule) set again
            if mat.ACTIVE is not self._world_set:
                mat.activate(self._world_set)
        else:
            self.level = generate_level(self.world, depth)
        if self.mirror:
            self.level = self._mirror_level(self.level)
        scale = self.area_scale

        def more(count: int) -> int:  # bigger worlds hold more creatures and loot
            return round(count * scale)

        self.enemies.creatures = populate(
            self.world,
            self.rng,
            self.level.spawn,
            more(depth.walkers),
            more(depth.flyers),
            more(depth.spitters),
            more(depth.bloats),
            extra=tuple((key, more(count)) for key, count in depth.extra),
            spread=self.multiverse,  # universes: natives in every part of the map
        )
        if self.universe_key != "fleischwelt" or self.multiverse:
            if getattr(self.universe, "mid_boss", None):
                mid_arena = getattr(self.level, "mid_boss_arena", None)
                if mid_arena and mid_arena != (0, 0, 0, 0):
                    mc = ((mid_arena[0] + mid_arena[2]) // 2, (mid_arena[1] + mid_arena[3]) // 2)
                else:
                    mc = (self.world.width // 2, self.world.height // 2)
                self.enemies.spawn(self.universe.mid_boss, mc[0], mc[1])
            if self.boss_slot and getattr(self.universe, "boss", None):
                b_arena = getattr(self.level, "boss_arena", None)
                if b_arena and b_arena != (0, 0, 0, 0):
                    bc = ((b_arena[0] + b_arena[2]) // 2, (b_arena[1] + b_arena[3]) // 2)
                else:
                    bc = (self.world.width // 2, self.world.height // 2)
                boss = self.enemies.spawn(self.universe.boss, bc[0], bc[1])
                self.boss_script = make_boss_script(boss)  # F06: fought in three phases
        elif depth.boss and self.level.arena is not None:
            self.enemies.creatures.append(spawn_boss(depth.boss, self.level.arena, self.rng))
        if self.ng or self.parallel:
            power = self.power
            for creature in self.enemies.creatures:
                if not creature.spec.prop:
                    creature.empower(power)
        self.exit_open = depth.boss is None
        self.pickups = place_loot(
            self.world, self.rng, self.level.spawn, more(depth.wands), more(depth.blocks),
            level=index + 1 + MIRROR_LOOT * abs(self.parallel),
            flasks=more(FLASKS_PER_DEPTH), hearts=1, cocoons=more(COCOONS_PER_DEPTH),
        )  # fmt: skip
        self._fill_caches(shaped.get("caches", ()))
        for species, x, y in shaped.get("spawns", ()):  # guards the terrain asked for
            if self.mirror:
                x = self.world.width - 1 - x - SPECIES[species].width
            if math.dist((x, y), self.level.spawn) < START_SAFE_RADIUS:
                continue  # the start stays quiet (playtest 2026-11-13)
            self.enemies.spawn(species, x, y)
        self._start_quest()
        self._spawn_echo()
        if self.universe_key != "fleischwelt" or self.multiverse:  # F02: the authority follows
            spawn_agents(self)
        self.thrown = []
        self.droplets = []
        if self.level.secret is not None:
            x, y = self.level.secret
            self.pickups.append(Pickup(x, y + 2, eye=True, floating=True))
        if self.level.vault is not None:
            self._fill_vault(index)
        self.pickups += scatter_pearls(self.world, self.rng, self.level.spawn, more(PEARL_PILES))
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

    @property
    def area_scale(self) -> float:
        """World area relative to the default size (creature and loot counts follow it)."""
        width, height = self.default_size
        return self.world.width * self.world.height / (width * height)

    def cycle_material_set(self) -> str:
        """Sandbox: rebuild the current depth with the next material set. Returns its key."""
        keys = ["koerper", "aktenhalde"]
        depth = self.route[self.depth_index]
        cur = depth.material_set if depth.material_set in keys else keys[0]
        nxt = keys[(keys.index(cur) + 1) % len(keys)]
        route = list(self.route)
        route[self.depth_index] = replace(depth, material_set=nxt)
        self.route = tuple(route)
        self.enter_depth(self.depth_index)
        return nxt

    def cycle_world_size(self) -> tuple[int, int]:
        """Sandbox: rebuild the current depth in the next world shape. Returns the size."""
        sizes = [self.default_size, *SHAPES.values()]
        depth = self.route[self.depth_index]
        current = depth.size or self.default_size
        nxt = sizes[(sizes.index(current) + 1) % len(sizes)] if current in sizes else sizes[0]
        route = list(self.route)
        route[self.depth_index] = replace(depth, size=None if nxt == self.default_size else nxt)
        self.route = tuple(route)
        self.enter_depth(self.depth_index)
        return nxt

    @property
    def rank(self) -> int:
        """Rank 1-3 of the current depth (the seven organism depths spread over three)."""
        if self.multiverse and self.plan.current is not None:
            return self.plan.current.rank  # multiverse run: rank of the chosen universe
        return 1 + self.depth_index * 3 // max(1, len(self.route))

    def _apply_rule(self, depth: Depth) -> mat.MaterialSet:
        """Set up the rule of ``depth``; returns the material set it asks for."""
        self.rule = Rule.make(depth.rule, self.rank)
        Body.gravity_scale = self.rule.gravity_scale
        self.projectiles.gravity_scale = self.rule.gravity_scale
        self.projectiles.bounce_bonus = {
            PLAYER_TEAM: self.rule.bounce_bonus(enemy=False),
            ENEMY_TEAM: self.rule.bounce_bonus(enemy=True),
        }
        return self.rule.material_set(mat.SETS[depth.material_set])

    def cycle_rule(self) -> str:
        """Sandbox: rebuild the current depth with the next universe rule."""
        keys = ["", *RULE_KEYS]
        depth = self.route[self.depth_index]
        nxt = keys[(keys.index(depth.rule) + 1) % len(keys)] if depth.rule in keys else ""
        route = list(self.route)
        route[self.depth_index] = replace(depth, rule=nxt)
        self.route = tuple(route)
        self.enter_depth(self.depth_index)
        return self.rule.name_de

    def _prepare_world(self, depth: Depth) -> None:
        """Rule, material set and world size of ``depth`` (work packages T1, T2, T4)."""
        material_set = self._apply_rule(depth)
        if mat.ACTIVE is not material_set:
            mat.activate(material_set)
        self._world_set = material_set  # what the native core simulates (see enter_depth)
        width, height = depth.size or self.default_size
        if not self.world.fits(material_set.key, width, height):
            self.world.reload(width, height)

    # ---------------------------------------------------------- save / load

    def snapshot(self) -> dict[str, Any]:
        """JSON-compatible state from which ``restore`` rebuilds the next sanctum."""
        player = self.player
        version, internal, gauss = self.rng.getstate()
        return {
            "version": SAVE_VERSION,
            "depth_index": self.depth_index,
            "pearls": self.pearls,
            "quest": self.quest.to_data() if self.quest is not None else None,
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
                {
                    "spec": {**asdict(wand.spec), "blocks": list(wand.spec.blocks)},
                    "slots": list(wand.slots),
                }
                for wand in self.inventory.wands
            ],
            "active": self.inventory.active,
            "favoured": sorted(self.favoured_blocks),
            "bag": list(self.inventory.bag),
            "bag_counts": list(self.inventory.counts),
            "flasks": [[flask.key, flask.amount] for flask in self.flasks],
            "flask_active": self.flask_index,
            "rng": [version, list(internal), gauss],
            # G07/G08: the multiverse state of the run
            "universe_key": self.universe_key,
            "multiverse": self.multiverse,
            "plan": self.plan.to_data() if self.plan is not None else None,
            "gold": self.pearls,
            "badges": self.badges,
            "memory_shards": self.memory_shards,
            "blueprint_shards": self.blueprint_shards,
            "samples": [list(slot) if slot else None for slot in self.inventory.samples],
            "wanted": self.wanted.to_data(),
            "klonita": self.klonita.to_data(),
            "status": {
                "stamped_good": self.player.body.stamped_good,
                "stamped_bad": self.player.body.stamped_bad,
            },
        }

    def save_state(self) -> dict[str, Any]:
        """Everything needed to continue exactly here ("Speichern und beenden").

        On top of the sanctum snapshot it holds the world itself (compressed), the
        level layout, the player's position and state, every creature and item.
        Projectiles and flying droplets are left out; falling tissue is set down.
        """
        for chunk in self.chunks.items:  # tissue in flight lands where it is
            for x, y, material in chunk.place(chunk.x, chunk.y, chunk.angle):
                if self.world.get(x, y) == AIR:
                    self.world.set_cell(x, y, material, force=True)
        self.chunks.clear()
        data = self.snapshot()
        player = self.player
        level = self.level
        data["live"] = {
            "in_sanctum": self.in_sanctum,
            "depth_index": self.depth_index,
            "time_in_depth": self.time_in_depth,
            "exit_open": self.exit_open,
            "level": [level.spawn, level.exit, level.arena, level.secret, level.vault],
            "level_universe": level.universe_key,
            "material_set": self.world.material_set,
            "size": [self.world.width, self.world.height],
            "world": _pack(self.world.grid),
            "life": _pack(self.world.life),
            "player": {
                "x": player.x, "y": player.y, "hp": player.hp, "energy": player.energy,
                "burning": player.burning, "wet": player.wet, "oily": player.oily,
                "slimed": player.slimed, "poisoned": player.poisoned,
                "polymorphed": player.polymorphed,
            },
            "creatures": [
                {
                    "key": c.spec.key, "x": c.x, "y": c.y, "hp": c.hp, "max_hp": c.max_hp,
                    "power": c.power, "alerted": c.alerted,
                }
                for c in self.enemies.creatures
                if not c.dead
            ],
            "pickups": [_pickup_data(item) for item in self.pickups],
            "god_mode": self.god_mode,
            "checkpoint": self.checkpoint,  # the last sanctum, if the game ends without saving
        }  # fmt: skip
        return data

    def restore(self, data: dict[str, Any]) -> None:
        """Continue a saved run.

        A sanctum snapshot enters that sanctum again; a full save (``save_state``)
        continues exactly where the player stopped. Raises ``ValueError`` for data
        that does not fit this version of the game.
        """
        try:
            if data.get("version") != SAVE_VERSION:
                raise ValueError("unsupported save version")
            depth_index = int(data["depth_index"])
            last = len(DEPTHS) if isinstance(data.get("live"), dict) else len(DEPTHS) - 1
            if not 0 <= depth_index < last:
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
        self._restore_multiverse(data)
        self.quest = Quest.from_data(data.get("quest"))
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
        live = data.get("live")
        if isinstance(live, dict):
            try:
                self._restore_live(live)
                self._restore_status(data)  # after place(): timers survive the move
                return
            except (KeyError, TypeError, ValueError, IndexError, zlib.error):
                checkpoint = live.get("checkpoint")  # damaged: back to the sanctum before
                if isinstance(checkpoint, dict) and "live" not in checkpoint:
                    self.restore(checkpoint)
                    return
        self.enter_sanctum()

    def _restore_multiverse(self, data: dict[str, Any]) -> None:
        """G07/G08: universe, run plan, currencies, samples, wanted level and Klonita."""
        from src.authority import Wanted
        from src.universes.plan import RunPlan

        key = str(data.get("universe_key", self.universe_key))
        if key in UNIVERSE_BY_KEY:
            self.universe_key = key
            self.universe = UNIVERSE_BY_KEY[key]
        plan = data.get("plan")
        if isinstance(plan, dict):
            try:
                self.plan = RunPlan.from_data(plan)
            except (KeyError, TypeError, ValueError):
                pass
        self.multiverse = bool(data.get("multiverse", self.multiverse))
        self.badges = int(data.get("badges", 0))
        self.memory_shards = int(data.get("memory_shards", 0))
        self.blueprint_shards = int(data.get("blueprint_shards", 0))
        samples = data.get("samples")
        if isinstance(samples, list):
            slots = [None] * len(self.inventory.samples)
            for i, slot in enumerate(samples[: len(slots)]):
                if isinstance(slot, (list, tuple)) and len(slot) == 2:
                    slots[i] = (str(slot[0]), int(slot[1]))
            self.inventory.samples = slots
        self.wanted = Wanted.from_data(data.get("wanted") if isinstance(data.get("wanted"), dict) else None)
        self.klonita = Klonita.from_data(data.get("klonita") if isinstance(data.get("klonita"), dict) else None)
        self._restore_status(data)

    def _restore_status(self, data: dict[str, Any]) -> None:
        status = data.get("status")
        if isinstance(status, dict):
            self.player.body.stamped_good = float(status.get("stamped_good", 0.0))
            self.player.body.stamped_bad = float(status.get("stamped_bad", 0.0))

    def _restore_live(self, live: dict[str, Any]) -> None:
        self._apply_rule(
            SANCTUM if live.get("in_sanctum") else self.route[int(live["depth_index"])]
        )
        set_key = str(live.get("material_set", mat.DEFAULT_SET.key))
        material_set = mat.find_set(set_key)
        if material_set is None:
            raise ValueError("unknown material set in the saved world")
        width, height = live.get("size", self.default_size)
        if mat.ACTIVE is not material_set:
            mat.activate(material_set)
        if not self.world.fits(set_key, int(width), int(height)):
            self.world.reload(int(width), int(height))
        world = self.world
        grid, life = _unpack(live["world"]), _unpack(live["life"])
        if len(grid) != len(world.grid) or len(life) != len(world.life):
            raise ValueError("saved world has the wrong size")
        if max(grid) >= mat.MATERIAL_COUNT:
            raise ValueError("unknown material in the saved world")
        checkpoint = live.get("checkpoint")
        self.checkpoint = checkpoint if isinstance(checkpoint, dict) else None
        self.in_sanctum = bool(live["in_sanctum"])
        self.depth_index = int(live["depth_index"])
        world.grid[:] = grid
        world.life[:] = life
        world.wake_all()

        def point(value):
            return None if value is None else (int(value[0]), int(value[1]))

        spawn, exit_point, arena, secret, vault = (point(v) for v in live["level"])
        self.level = Level(
            spawn, exit_point, arena, secret, vault,
            universe_key=str(live.get("level_universe", self.universe_key)),
        )  # fmt: skip
        self.exit_open = bool(live["exit_open"])
        self.time_in_depth = float(live.get("time_in_depth", 0.0))
        self.enemies.clear()
        for entry in live["creatures"]:
            spec = SPECIES.get(entry["key"])
            if spec is None:
                continue
            creature = Creature(spec, int(entry["x"]), int(entry["y"]), self.rng)
            creature.empower(float(entry.get("power", 1.0)))
            creature.max_hp = float(entry["max_hp"])
            creature.hp = float(entry["hp"])
            creature.alerted = bool(entry.get("alerted", False))
            self.enemies.creatures.append(creature)
        self.pickups = [item for item in map(_pickup_from, live["pickups"]) if item is not None]
        self.projectiles.clear()
        self.chunks.clear()
        self.thrown, self.droplets = [], []
        player = self.player
        state = live["player"]
        player.place(int(state["x"]), int(state["y"]))
        player.hp = min(player.max_hp, float(state["hp"]))
        player.energy = float(state.get("energy", player.energy_max))
        for name in ("burning", "wet", "oily", "slimed", "poisoned", "polymorphed"):
            setattr(player, name, float(state.get(name, 0.0)))
        self.god_mode = bool(live.get("god_mode", False))

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
        keys = [key for key in keys if key]
        self.discoveries.extend(("block", key) for key in keys)
        self.known_blocks.update(keys)

    def _refill_wands(self) -> None:
        for wand in self.inventory.wands:
            wand.mana = wand.spec.mana_max
            wand.cooldown = wand.recharge_left = 0.0

    # ---------------------------------------------------------------- update

    def shoulder(self, aim: tuple[float, float]) -> tuple[float, float]:
        cx, cy = self.player.center
        side = 1 if aim[0] >= cx else -1
        return cx + SHOULDER_OFFSET[0] * side, cy + SHOULDER_OFFSET[1]

    def update(
        self, dt: float, controls: Controls | None = None, area: Rect | None = None
    ) -> list[Blast]:
        """Advance the run by ``dt`` seconds; ``area`` limits simulation (cells)."""
        if controls is None:
            controls = Controls()
        self.events = []
        self.emitted_events = []
        self.last_aim = controls.aim
        self.time_in_depth += dt
        if not self.outcome:
            self.stats["time"] += dt

        # Universe secondary event lifecycle (Cards D11, D12)
        if not self.in_sanctum:
            if self.event is not None and self.event.active:
                self.event.tick(dt, self)
                if not self.event.active:
                    self.event = None
            elif self.event is None:
                self.event_timer += dt
                u_event_key = getattr(self.universe, "event", "")
                if u_event_key:
                    from src.events import EVENTS, Event

                    spec = EVENTS.get(u_event_key)
                    if spec is not None and self.event_timer >= spec.interval:
                        self.event_timer = 0.0
                        self.event = Event(spec=spec, remaining=spec.duration)
                        self.event.on_start(self)
                        self.klonita_trigger("event_start")
        alive = not self.player.dead and self.outcome not in ("victory", "bad_ending")
        if not alive:
            controls = Controls(aim=controls.aim)
        self._clear_overlap()
        if alive and controls.move:
            self._crush_debris(controls.move)
        self._speck_timer -= dt
        if self._speck_timer <= 0:
            self._speck_timer = SPECK_INTERVAL
            self._sweep_specks()
        if controls.jump and self.player.on_ground and not self.player.dead:
            px, py = self.player.center  # D28: the dance quest counts jumps on the beat
            self.emit("jump", x=px, y=py, on_beat=bool(self.rule.on_beat))
        self.player.update(self.world, dt, controls.move, controls.jump, controls.levitate)
        if self.quest is not None:
            self.quest.tick(dt, self)
        apply_player_rules(
            self.player, self.world, self.rule, dt, region=self._region_at(*self.player.center)
        )
        self.rule.update(self, dt, area)
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
        leave = False
        if controls.pickup:
            if self.in_workshop and self.menu_mode == "":
                self.interact_station()
            elif alive and self.try_interact_creature():
                pass  # talked to the quest giver or bribed a bouncer
            elif alive and self.exit_open and self.near_exit() and self.nearest_pickup() is None:
                leave = True  # the way on opens on a key press, never by walking into it
            else:
                self._pick_up_here()
        if alive and self.player.polymorphed <= 0:
            self._use_flask(controls, dt)
        self._kick_cooldown = max(0.0, self._kick_cooldown - dt)
        if alive and controls.kick and self._kick_cooldown <= 0:
            self._kick(controls.aim)

        self._step_world(dt, area)
        cells_destroyed = self.world.take_destroyed_cells()
        gold_cells = self.world.take_destroyed_gold_vein_cells()
        if cells_destroyed > 0 or gold_cells > 0:
            self.emit("cells_destroyed", count=cells_destroyed, gold_vein_cells=gold_cells)
            if self.wanted.on_cells_destroyed(cells_destroyed + gold_cells):  # F02
                self._wanted_changed("Sachbeschädigung")
        if gold_cells > 0:
            total_gold_cells = self._gold_vein_remainder + gold_cells
            n_drops = total_gold_cells // 6
            self._gold_vein_remainder = total_gold_cells % 6
            px, py = self.player.center
            for _ in range(n_drops):
                self.pickups.append(Pickup(px, py, kind="gold", amount=5))
            if gold_cells >= 18 and self.rng.random() < 0.25:
                self.pickups.append(Pickup(px, py, kind="sample", item_key="probe_gold", amount=1))

        everywhere = area or (0, 0, self.world.width, self.world.height)
        for creature in self.enemies.creatures:
            for key in list(creature.ability_cooldowns):
                creature.ability_cooldowns[key] = max(0.0, creature.ability_cooldowns[key] - dt)
        out_events: list[tuple[str, dict[str, Any]]] = []
        if self.boss_script is not None and not self.boss_script.boss.dead:
            self.boss_script.update(dt, self)
        for script in self.extra_scripts:
            if not script.boss.dead:
                script.update(dt, self)
        if self.in_headquarters and self.hq_controller is not None:
            self.hq_controller.update(dt, self)
        self._tick_final_arena(dt)
        self._tick_klonita(dt, controls)
        if self.boss_banner is not None:
            text, left = self.boss_banner
            self.boss_banner = (text, left - dt) if left > dt else None
        died = self.enemies.update(
            self.world,
            dt,
            self.player,
            self.projectiles,
            everywhere,
            grudges=self.grudges,
            on_beat=True,
            out_events=out_events,
        )
        for creature in died:
            for ability in getattr(creature.spec, "abilities", ()):
                if ability.kind == "split":
                    from src.behaviour import handle_split_on_death

                    handle_split_on_death(creature, ability, out_events)
        self._handle_creature_events(out_events)
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
        self._ring_bells(blasts, dt)
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
            self.emit(
                "hurt_player", amount=self._last_hp - self.player.hp,
                source="self" if self.player.last_cause == "Tritt" else "projectile",
            )  # fmt: skip
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
                self.world.splash(int(cx), int(cy), DEATH_SPLASH, mat.BLOOD)
        elif alive and leave:
            self._descend()
        return blasts

    @property
    def true_ending(self) -> bool:
        """Won with every Urauge: the organism is not just dead, it is yours."""
        return self._true_ending_flag or (self.outcome == "victory" and self.eyes >= len(DEPTHS))

    @true_ending.setter
    def true_ending(self, value: bool) -> None:
        self._true_ending_flag = bool(value)

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
        wand.unlimited = "unerschoepflich" in self.perks
        shots = wand.cast()
        if not shots:
            return
        shots = self._cast_specials(shots)
        if any(
            getattr(block, "key", "") in FORBIDDEN_BLOCKS
            for shot in shots for block in (shot.form, *shot.modifiers)
        ):  # F02: the authority frowns on the big spells
            self.add_wanted(0.5, "Verbotene Magie")
        sx, sy = self.shoulder(aim)
        angle = math.atan2(aim[1] - sy, aim[0] - sx) + self.rng.uniform(-1, 1) * wand.spec.spread
        reach = arm_reach(len(wand.blocks))
        tip = (sx + math.cos(angle) * reach, sy + math.sin(angle) * reach)
        factor = self.rule.cast_factor()
        self.projectiles.spawn(shots, tip[0], tip[1], angle, damage_factor=factor)
        self.events.append("cast")
        name = wand.spec.name_de
        self.cast_counts[name] = self.cast_counts.get(name, 0) + 1
        if "schnelle_druesen" in self.perks:
            wand.cooldown *= FAST_GLANDS
            wand.recharge_left *= FAST_GLANDS

    def _cast_specials(self, shots: list[Shot]) -> list[Shot]:
        """Noita-style specials that act on the shots already in the air.

        "Zauber zu ..." forms turn every flying shot of the player into another form and
        fire nothing themselves; "Zauber zu Kraft" swallows the flying shots near the
        player and adds their damage to the shot it modifies."""
        mine = [p for p in self.projectiles.items if p.alive and p.team == PLAYER_TEAM]
        out: list[Shot] = []
        for shot in shots:
            if shot.form.convert:
                target = CATALOG[shot.form.convert]
                for old in mine:
                    if old.alive and getattr(old.form, "key", "") != target.key:
                        still = target.key == "todeskreuz"
                        angle = math.atan2(old.vy, old.vx)
                        new = build_projectile(Shot(target), old.x, old.y, angle, PLAYER_TEAM)
                        if still:
                            new.vx = new.vy = 0.0
                        old.alive = False
                        self.projectiles.items.append(new)
                continue
            if any(m.absorb for m in shot.modifiers):
                px, py = self.player.center
                pool = 0.0
                for old in mine:
                    if old.alive and math.dist((old.x, old.y), (px, py)) <= ABSORB_RADIUS:
                        pool += old.damage + old.blast
                        old.alive = False
                if pool:
                    power = replace(CATALOG["zauber_zu_kraft"], absorb=False, damage_bonus=pool)
                    shot = replace(shot, modifiers=(*shot.modifiers, power))
            out.append(shot)
        return out

    def _fill_vault(self, index: int) -> None:
        """Treasure and a strengthened guardian inside the depth's bone vault."""
        if self.level.vault is None:
            return
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

    def _mirror_level(self, level: Level | None = None) -> Level:
        """Flip the freshly generated depth and every position in it."""
        if level is None:
            level = self.level
        self.world.mirror()
        w = self.world.width

        def flip(point: tuple[int, int] | None, width: int = 0) -> tuple[int, int] | None:
            return None if point is None else (w - 1 - point[0] - width, point[1])

        def flip_rect(rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
            x0, y0, x1, y1 = rect
            return (w - 1 - x1, y0, w - 1 - x0, y1)

        def flip_optional(
            rect: tuple[int, int, int, int] | None,
        ) -> tuple[int, int, int, int] | None:
            return None if rect is None else flip_rect(rect)

        return Level(
            flip(level.spawn, self.player.width - 1), flip(level.exit), flip(level.arena),
            flip(level.secret), flip(level.vault),
            exit_point=flip(level.exit_point),
            universe_key=level.universe_key,
            mid_boss_arena=flip_rect(level.mid_boss_arena),
            boss_arena=flip_rect(level.boss_arena),
            trader_nook=flip_optional(level.trader_nook),
            challenge_shrine=flip_optional(level.challenge_shrine),
            regions=[(name, flip_rect(rect)) for name, rect in level.regions],
            destructible_props=[(key, w - 1 - x, y) for key, x, y in level.destructible_props],
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
        px, py = int(player.x), int(player.y)
        for y in range(py, py + player.height):
            for x in range(px, px + player.width):
                cell = world.get(x, y)
                if not BLOCKS_BODY[cell] or cell == BEDROCK:
                    continue
                world.set_cell(x, y, AIR)
                if KIND[cell] == POWDER:
                    for up in range(1, 8):
                        if world.get(x, py - up) == AIR:
                            world.set_cell(x, py - up, cell)
                            break

    def _sweep_specks(self) -> None:
        """Tiny free-floating bits (left by fire, blasts, reactions) crumble away.

        In Noita such debris falls; here a speck that touches nothing would hang in
        the air forever and block the way, so it breaks into its debris.
        """
        cx, cy = self.player.center
        world = self.world
        groups = native.loose_groups(
            native.byte_view(world.grid), world.width, world.height, RIGID, (int(cx), int(cy)),
            SPECK_RADIUS, SPECK_RADIUS + 12, 1, SPECK_MAX,
        )  # fmt: skip
        w = world.width
        for group in groups:
            for index in group:
                x, y = index % w, index // w
                debris, _chance = DEBRIS[world.get(x, y)]
                world.set_cell(x, y, debris if KIND[debris] != SOLID else AIR)

    def _crush_debris(self, direction: int) -> None:
        """A thin obstacle (a few loose pixels) in front of the walking player gives way."""
        player, world = self.player, self.world
        x = player.x + player.width if direction > 0 else player.x - 1
        top = player.y
        bottom = player.y + player.height - 1 - player.step_up  # the feet climb small steps
        blocking = [(x, y) for y in range(top, bottom + 1) if BLOCKS_BODY[world.get(x, y)]]
        if not blocking or len(blocking) > CRUSH_MAX:
            return
        if any(HARDNESS[world.get(cx, cy)] >= 3 for cx, cy in blocking):
            return  # enamel and bedrock never give way
        if any(BLOCKS_BODY[world.get(cx + direction, cy)] for cx, cy in blocking):
            return  # more than a sliver: a real wall or ceiling, not loose debris
        for bx, by in blocking:
            debris, _chance = DEBRIS[world.get(bx, by)]
            world.set_cell(bx, by, debris if KIND[debris] != SOLID else AIR)

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
            and all(
                player.blocked(world, x + side, y - up)
                for side in (-1, 1)
                for up in range(step + 1)
            )
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

    def _kick(self, aim: tuple[float, float] | None = None) -> None:
        if aim is None:
            aim = (self.player.center[0] + 10.0, self.player.center[1])
        """Kick towards the cursor side: hurts and shoves creatures, bursts sacs, flings items."""
        self._kick_cooldown = KICK_COOLDOWN
        self.events.append("kick")
        player = self.player
        cx, cy = player.center
        side = 1 if aim[0] >= cx else -1
        reach_x = cx + side * (player.width / 2 + KICK_REACH / 2)
        for creature in self.enemies.creatures:
            ox, oy = creature.center
            if (
                abs(ox - reach_x) <= KICK_REACH / 2 + creature.width / 2
                and abs(oy - cy) <= creature.height / 2 + 6
            ):
                if creature.giver or getattr(creature.spec, "giver", False):
                    self._milk(creature)  # a giver is milked, not hurt
                    continue
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
            message = flask.drink(self.player, blood_heals="blutsauger" in self.perks)
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
            if distance <= PICKUP_RANGE * 0.6:
                self.pearls += item.pearls
                self.stats["pearls"] += item.pearls
                self.pickups.remove(item)
                self.events.append("pearl")
        # gold, samples and shards are collected by walking over them (playtest: too many clicks)
        for item in [i for i in self.pickups if i.kind in AUTO_PICKUP_KINDS and not i.price]:
            if math.hypot(item.x - cx, item.y - cy) <= PICKUP_RANGE * 0.6:
                self._pick_up_new_kind(item)

    def _pick_up_here(self) -> None:
        """[E]: take the nearest item, then every other free module lying in reach.

        Wands, flasks, perks and shop items stay one per press (they are choices)."""
        first = self.nearest_pickup()
        if first is None:
            return
        self._pick_up(first)
        cx, cy = self.player.center
        for item in list(self.pickups):
            if item is first or item.price or item.perk is not None or item.reroll:
                continue
            if item.portal or item.wand is not None or item.flask is not None:
                continue
            if item.block is None and item.kind not in NEW_PICKUP_KINDS:
                continue
            if item in self.pickups and math.hypot(item.x - cx, item.y - cy) <= PICKUP_RANGE:
                self._pick_up(item)

    def _pick_up(self, item: Pickup | None = None) -> bool:
        if item is None:
            item = self.nearest_pickup()
        if item is None:
            return
        if item.kind in NEW_PICKUP_KINDS:  # check kind first: these have no block/label
            return self._pick_up_new_kind(item)
        self._log(
            "aufheben", gegenstand=item.label_de, preis=self.price_of(item), perlen=self.pearls
        )
        if item.perk is not None:
            self.apply_perk(item.perk)
            self.pickups = [i for i in self.pickups if i.perk is None and not i.reroll]
            self.events.append("perk")
            return
        if item.portal:
            self.pickups.remove(item)
            if item.item_key == "headquarters":  # F10: the way to the true ending
                self.enter_headquarters()
            else:
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
            if item in self.pickups:
                self.pickups.remove(item)
            self.events.append("pickup")
            return True
        elif item.block is not None:
            note = "Beutel voll: im Rucksack [Tab] Module ablegen."
            if not self.messages or self.messages[-1] != note:
                self.messages.append(note)
        return False

    def _pick_up_new_kind(self, item: Pickup) -> bool:
        """Collect a pickup of one of the unified kinds (Contract V11, Card A06)."""
        kind = item.kind
        amount = max(1, item.amount) if kind != "gold" else max(0, item.amount)
        if kind == "sample":
            if self.inventory.add_sample(item.item_key, amount) <= 0:
                return False  # all slots full: the sample stays on the ground
            self.events.append("pickup")
        elif kind == "gold":
            self.gold += amount
            self.events.append("pearl")
        elif kind == "life_capsule":
            bonus = item.amount or 25
            self.player.max_hp += bonus
            self.player.hp = self.player.max_hp
            self.messages.append(f"Dein Herz wächst: +{bonus} maximales Leben.")
            self.events.append("perk")
        elif kind == "memory_shard":
            self.memory_shards += amount
            self.events.append("pickup")
        elif kind == "blueprint_shard":
            self.blueprint_shards += amount
            while self.blueprint_shards >= BLUEPRINT_SHARDS_NEEDED:
                self.blueprint_shards -= BLUEPRINT_SHARDS_NEEDED
                key = self._next_blueprint()
                if key is None:
                    self.messages.append("Alle Baupläne sind schon bekannt.")
                    continue
                self.records.discover("blueprint", key)
                self.messages.append(f"Neuer Bauplan: {CATALOG[key].name_de}.")
            self.events.append("pickup")
        elif kind == "badge":
            self.badges += amount
            self.records.badges += amount
            self.events.append("pickup")
        elif kind == "form_stamp":  # D25: a form lying around, stamped with [E]
            self.events.append("pickup")
            if item in self.pickups:
                self.pickups.remove(item)
            self.emit("form_stamped", x=float(item.x), y=float(item.y))
            return True
        else:  # "crate", "formular_stempel": opened or applied by later cards
            self.events.append("pickup")
        if item in self.pickups:
            self.pickups.remove(item)
        self.emit("pickup", kind=kind, key=item.item_key, amount=amount)
        if kind == "sample":
            self.stats["samples"] = self.stats.get("samples", 0) + amount
            self.emit("sample", key=item.item_key, count=amount)
        elif kind == "gold":
            self.emit("gold", amount=amount, source="pickup")
        return True

    def emit(self, event_name: str, **payload: Any) -> None:
        """Emit a gameplay event on the structured event bus (Contract V12, Card A07)."""
        payload = dict(payload)
        self.emitted_events.append((event_name, payload))
        for listener in list(self.listeners):
            listener(event_name, payload)

    def _pickup_data(self, item: Pickup) -> dict[str, Any]:
        return _pickup_data(item)

    def _pickup_from(self, data: dict[str, Any]) -> Pickup | None:
        return _pickup_from(data)

    def _milk(self, creature: Any) -> None:
        """Kicking a giver (aphid) squeezes out a few honey droplets, then it needs a rest."""
        if creature.ability_cooldowns.get("milk", 0.0) > 0.0:
            return
        creature.ability_cooldowns["milk"] = MILK_COOLDOWN
        honey = mat.MAT_ID.get("honig") or mat.MAT_ID.get("honey")
        if honey is None:  # material not part of the active set: a little healing instead
            self.player.hp = min(self.player.max_hp, self.player.hp + MILK_HEAL)
            return
        cx, cy = creature.center
        for k in range(MILK_DROPS):
            self.droplets.append(
                Droplet(honey, cx, cy + creature.height / 2, (k - 1.5) * 10.0, 20.0)
            )

    def try_interact_creature(self) -> bool:
        """Attempt special E-key interaction with nearby creature (Card A16, D23)."""
        px, py = self.player.center
        quest = self.quest
        if quest is not None and not quest.closed:
            for creature in self.enemies.creatures:
                if creature.dead or not creature.giver or creature.species != quest.spec.giver:
                    continue
                cx, cy = creature.center
                if math.hypot(cx - px, cy - py) > QUEST_GIVER_RANGE:
                    continue
                if not quest.accepted:
                    quest.accept(self)
                    self.say(creature.spec.name_de, quest.spec.text_de, cx, cy - creature.height)
                elif quest.turn_in(self):
                    self.stats["quests"] = self.stats.get("quests", 0) + 1
                    self.say(creature.spec.name_de, "Danke! Das hier ist für dich.", cx, cy)
                else:
                    left = f"{quest.progress}/{quest.spec.goal}"
                    self.say(creature.spec.name_de, f"{quest.spec.text_de} ({left})", cx, cy)
                return True
        for creature in self.enemies.creatures:
            if creature.dead or creature.species != "tuersteherpilz" or creature.bribed:
                continue
            cx, cy = creature.center
            if math.hypot(cx - px, cy - py) > BRIBE_RANGE or self.gold < BRIBE_COST:
                continue
            self.gold -= BRIBE_COST
            creature.bribed = True
            creature.aggro = False
            self.emit("bribe", species=creature.species, cost=BRIBE_COST)
            return True
        return False

    def _region_at(self, x: float, y: float) -> Any:
        """Return the Region object at world position (x, y)."""
        regions = getattr(self.level, "regions", None)
        if regions:
            for region_key, (x0, y0, x1, y1) in regions:
                if x0 <= x < x1 and y0 <= y < y1:
                    for reg in self.universe.regions:
                        if reg.key == region_key:
                            return reg
        # Fallback to thirds of the height
        if self.universe.regions:
            h = max(1, self.world.height)
            index = min(
                len(self.universe.regions) - 1, max(0, int(y / (h / len(self.universe.regions))))
            )
            return self.universe.regions[index]
        return None

    def _region_at(self, x: float, y: float) -> Any:
        """Return the Region object at world position (x, y)."""
        regions = getattr(self.level, "regions", None)
        if regions:
            for region_key, (x0, y0, x1, y1) in regions:
                if x0 <= x < x1 and y0 <= y < y1:
                    for reg in self.universe.regions:
                        if reg.key == region_key:
                            return reg
        # Fallback to thirds of the height
        if self.universe.regions:
            h = max(1, self.world.height)
            index = min(
                len(self.universe.regions) - 1, max(0, int(y / (h / len(self.universe.regions))))
            )
            return self.universe.regions[index]
        return None

    def enter_workshop(self) -> None:
        """Move the run into the workshop between universes (Contract V18, Card E10)."""
        from src.fabricator import Fabricator
        from src.traders import generate_offers, traders_for_workshop
        from src.universes.plan import RunPlan
        from src.workshop import WORKSHOP_SIZE, generate_workshop

        if not self.multiverse:
            self.plan = RunPlan(self.seed)
            self.multiverse = True

        self.in_workshop = True
        self.menu_mode = ""
        self.exit_open = False  # the workshop has no anchor point; the portal frame leads on

        # Build workshop world and layout
        # reuse the world object (renderer and systems hold it) and close the old native core
        self.world.reload(*WORKSHOP_SIZE)
        self.workshop_layout = generate_workshop(self.world)

        # Place player at workshop spawn and fully heal
        sx, sy = self.workshop_layout.spawn
        self.player.x, self.player.y = float(sx), float(sy)
        self.player.body.hp = self.player.body.max_hp

        # Move Klonita to couch position
        self.klonita.x, self.klonita.y = (
            float(self.workshop_layout.klonita_pos[0]),
            float(self.workshop_layout.klonita_pos[1]),
        )

        # Clear active enemies/pickups in workshop
        self.enemies.creatures.clear()
        self.pickups.clear()
        self.projectiles.clear()
        self.droplets.clear()
        self.chunks.clear()

        # Spawn target dummy in workshop (Card E15)
        import dataclasses

        dummy_x, dummy_y = self.workshop_layout.target_dummy_pos
        c = self.enemies.spawn("made", dummy_x, dummy_y)
        c.species = "trainings_attrappe"
        c.spec = dataclasses.replace(
            c.spec,
            key="trainings_attrappe",
            name_de="Trainings-Attrappe",
            stance="peaceful",
            speed=0,
            stationary=True,
            melee_damage=0,
            hp=9999,
        )
        c.max_hp = 9999.0
        c.hp = 9999.0

        def _dummy_hurt(amount: float, cause: str = "", _orig=c.hurt, _creature=c) -> None:
            if amount > 0:
                self.dummy_damage_total += amount  # damage numbers come from the floaters
                _creature.hp = _creature.max_hp  # never dies (dead follows from hp)
                if _creature.flash_cooldown <= 0:
                    _creature.flash = 0.1
                    _creature.flash_cooldown = 0.3

        c.hurt = _dummy_hurt

        # Contract V18 reset visit rules
        if self.wanted.on_workshop():
            self._wanted_changed("Aktenablage")
        if self.fabricator is None:
            self.fabricator = Fabricator()
        else:
            self.fabricator.reset_visit()

        self.couch_used = False
        self.minigames_played = set()
        self.active_minigame = None
        self.experiment_picked = False
        self.experiment_offers = []

        # Reset / populate active traders for workshop
        self.active_traders = traders_for_workshop(self.plan.visited)
        self.trader_offers = {}
        stage = (self.plan.slot + 1) if self.multiverse else 1
        for trader in self.active_traders:
            self.trader_offers[trader.key] = generate_offers(
                trader, stage, self.rng, price_factor=self.price_factor
            )

    def interact_station(self) -> None:
        """Interact with the nearest workshop station (Contract V18, Card E10)."""
        from src.economy import ZAPF_PRICE
        from src.flask import CAPACITY, Flask
        from src.workshop import station_at

        if not self.in_workshop or self.workshop_layout is None:
            return

        st = station_at(self.workshop_layout, int(self.player.x), int(self.player.y), radius=16)
        if st is None:
            return

        key = st.key
        if key == "ws_couch":
            if not self.couch_used:
                self.couch_used = True
                heal_amount = self.player.body.max_hp * 0.35
                self.player.body.hp = min(
                    self.player.body.max_hp, self.player.body.hp + heal_amount
                )
                try:
                    from src.klonita_lines import LINES

                    lines = LINES.get("couch", ("Kuschelig hier!",))
                    text = self.rng.choice(lines) if lines else "Kuschelig hier!"
                except (ImportError, AttributeError, IndexError):
                    text = "Kuschelig hier!"
                self.messages.append(f"Klonita: {text}")
        elif key == "ws_zapfhahn":
            if self.flask is not None:
                if self.gold >= ZAPF_PRICE:
                    self.gold -= ZAPF_PRICE
                    self.flask = Flask("fluxschnaps", CAPACITY)
                    self.messages.append("Kolben mit Fluxschnaps gefüllt (-10 Gold).")
                else:
                    self.messages.append("Zu wenig Gold für Fluxschnaps.")
        elif key == "ws_well":
            if self.flask is not None:
                self.flask = Flask("water", CAPACITY)
                self.messages.append("Kolben kostenlos mit Wasser gefüllt.")
        elif key == "ws_liege":
            if not self.experiment_picked:
                if not self.experiment_offers:
                    self._roll_experiments()
                self.menu_mode = "experiment"
                self.menu_index = 0
            else:
                self.messages.append(
                    "Für diesen Besuch hast du bereits ein Selbstexperiment gewählt."
                )
        elif key == "ws_fabrikator":
            self.menu_mode = "fabricator"
            self.menu_index = 0
        elif key == "ws_werkbank":
            self.inventory_open = True
        elif key == "ws_haendler":
            if not self.active_traders:
                # Default trader so workshop shop works even before first universe
                from src.traders import TRADERS, generate_offers

                default_trader = TRADERS["npc_magenhaendler"]
                self.active_traders = [default_trader]
                self.trader_offers[default_trader.key] = generate_offers(
                    default_trader, 1, self.rng, price_factor=self.price_factor
                )

            # Pick the nearest trader on the trader slots
            if len(self.active_traders) == 1:
                self.selected_trader_key = self.active_traders[0].key
            else:
                slots = self.workshop_layout.trader_slots
                px = self.player.x
                d0 = abs(px - slots[0][0])
                d1 = abs(px - slots[1][0])
                idx = 0 if d0 <= d1 else 1
                if idx < len(self.active_traders):
                    self.selected_trader_key = self.active_traders[idx].key
                else:
                    self.selected_trader_key = self.active_traders[0].key
            self.active_trader_key = self.selected_trader_key
            self.selected_offer_index = 0
            self.menu_index = 0
            self.menu_mode = "trader"
        elif key == "ws_archiv":
            self.menu_mode = "archive"
        elif key == "ws_portal":
            self.menu_mode = "portal_select"
        elif key in ("ws_automat", "ws_schiessstand") and not MINIGAMES_ENABLED:
            name = "Physik-o-Mat" if key == "ws_automat" else "Schießstand"
            self.messages.append(f"{name}: Außer Betrieb. Wird gerade umgebaut.")
        elif key == "ws_automat":
            from src.economy import PHYSIK_STAKE
            from src.minigames.physik_o_mat import make_physik_puzzle

            if "ws_automat" not in self.minigames_played and self.gold >= PHYSIK_STAKE:
                self.gold -= PHYSIK_STAKE
                self.minigames_played.add("ws_automat")
                mg_seed = self.seed + len(self.minigames_played)
                self.active_minigame = make_physik_puzzle(None, seed=mg_seed)
                self.menu_mode = "minigame"
            elif "ws_automat" in self.minigames_played:
                self.messages.append("Für diesen Besuch bereits gespielt.")
            else:
                self.messages.append("Zu wenig Gold für den Physik-o-Mat.")
        elif key == "ws_schiessstand":
            from src.economy import SCHIESS_STAKE
            from src.minigames.schiessstand import SchiessstandMinigame

            if "ws_schiessstand" not in self.minigames_played and self.gold >= SCHIESS_STAKE:
                self.gold -= SCHIESS_STAKE
                self.minigames_played.add("ws_schiessstand")
                mg_seed = self.seed + len(self.minigames_played)
                self.active_minigame = SchiessstandMinigame(seed=mg_seed)
                self.menu_mode = "minigame"
            elif "ws_schiessstand" in self.minigames_played:
                self.messages.append("Für diesen Besuch bereits gespielt.")
            else:
                self.messages.append("Zu wenig Gold für den Schießstand.")
        elif key == "ws_shredder":
            cost = self.wanted.bribe_cost()
            if self.gold >= cost and self.wanted.level > 0.0:
                self.gold -= cost
                self.add_wanted(-1.0, "Akten geschreddert")
                self.messages.append(f"Akten geschreddert (-{cost} Gold, -1.0 Fahndungsstufe).")
            elif self.wanted.level <= 0.0:
                self.messages.append("Keine Akten vorhanden.")
            else:
                self.messages.append("Zu wenig Gold zum Schreddern.")

    def buy_trader_offer(
        self, trader_key: str, index: int, *, use_samples: bool = False
    ) -> tuple[bool, str]:
        """Buy offer `index` from trader `trader_key` (Contracts V19 §2, Card E13)."""
        from src.traders import TRADERS, buy_offer

        offers = self.trader_offers.get(trader_key, [])
        if index < 0 or index >= len(offers):
            return False, "Angebot existiert nicht."

        trader = TRADERS.get(trader_key)
        if trader is None:
            return False, "Händler existiert nicht."

        offer = offers[index]
        ok, msg = buy_offer(self, trader, offer, use_samples=use_samples)
        if ok:
            offers.pop(index)
            self.events.append("pickup")
        return ok, msg

    def craft_selected_recipe(self, block_key: str) -> tuple[bool, str]:
        """Craft a module from a discovered blueprint at the fabricator (Card E12)."""
        from src.fabricator import Fabricator
        from src.loot import Pickup

        if self.fabricator is None:
            self.fabricator = Fabricator()

        inv = self.inventory
        can_fit = inv.can_add(block_key)

        if can_fit:
            ok, msg = self.fabricator.craft(self, block_key)
            if ok:
                self.events.append("pickup")
            return ok, msg

        # If bag is full, temporarily make space to let craft deduct materials and add block, then pop it out to Pickup
        # Or check if can_build would succeed without bag check
        ok, reason = self.fabricator.can_build(self, block_key)
        if not ok and reason != "Rucksack ist voll.":
            return False, reason

        # Temporarily free a slot
        last_item = inv.bag[-1]
        inv.bag[-1] = None
        ok, msg = self.fabricator.craft(self, block_key)
        inv.bag[-1] = last_item

        if ok:
            # Drop the crafted module as a Pickup
            px, py = self.player.center
            self.pickups.append(Pickup(px, py, block=block_key))
            self.events.append("pickup")
            return True, msg
        return ok, msg

    def _roll_experiments(self) -> None:
        """Roll 3 distinct perks not yet picked (Card E16)."""
        available = [p.key for p in PERKS if p.key not in self.perks]
        if len(available) >= 3:
            self.experiment_offers = self.rng.sample(available, 3)
        else:
            self.experiment_offers = list(available)

    def pick_experiment(self, index: int) -> bool:
        """Pick an experiment offer by index (Contracts V18, V19 §1; Card E16)."""
        if self.experiment_picked:
            return False
        if index < 0 or index >= len(self.experiment_offers):
            return False
        perk_key = self.experiment_offers[index]
        self.apply_perk(perk_key)
        self.experiment_picked = True
        self.events.append("perk")
        return True

    def reroll_experiments(self) -> bool:
        """Reroll the experiment couch offers (Contracts V18, V19 §1; Card E16)."""
        from src.economy import experiment_reroll_price

        if self.experiment_picked:
            return False

        # First consume free reroll from inventory if available
        if getattr(self.inventory, "rerolls", 0) > 0:
            self.inventory.rerolls -= 1
        else:
            price = experiment_reroll_price(self.experiment_rerolls)
            if self.gold < price:
                return False
            self.gold -= price
            self.experiment_rerolls += 1

        self._roll_experiments()
        self.events.append("pickup")
        return True

    def step_minigame(
        self,
        dt: float,
        action: str | None = None,
        cursor: tuple[int, int] = (80, 60),
    ) -> Any:
        """Step the active minigame, handle payout upon victory (Card E14)."""
        if self.active_minigame is None:
            return None

        res = self.active_minigame.step(dt, action=action, cursor=cursor)
        if res is not None:
            if res.won:
                if res.reward_gold:
                    self.gold += res.reward_gold
                if res.reward_sample:
                    self.inventory.add_sample(res.reward_sample, 1)
                if res.next_boost:
                    self.next_boost = res.next_boost
            if res.message_de:
                self.messages.append(res.message_de)
        return res

    def choose_next_universe(self, index: int) -> None:
        """Take portal offer ``index`` from ``self.plan.offers()`` and enter it (Card E11)."""
        from src.universes.catalog import ALL_UNIVERSES

        if self.plan.finished:  # after six universes only the evil self's home is left
            self.enter_final()
            return
        offer = self.plan.choose(index)
        self.enter_universe(ALL_UNIVERSES[offer.universe], boss_slot=offer.boss is not None)

        # Apply and consume active next_boost
        boost = self.next_boost
        self.next_boost = ""
        if boost == "flux":
            for wand in self.inventory.wands:
                wand.spec = replace(wand.spec, mana_regen=round(wand.spec.mana_regen * 1.2))
        elif boost == "damage":
            self.projectiles.player_damage = getattr(self.projectiles, "player_damage", 1.0) * 1.1
        elif boost == "speed":
            self.player.speed_scale = getattr(self.player, "speed_scale", 1.0) * 1.1

    def enter_universe(self, universe: Universe, *, boss_slot: bool = False) -> None:
        """Generate ``universe`` and put the player at its start (Card G16).

        The level still runs through ``enter_depth``, but with a depth built from the
        universe: its material set is active in Python *and* in the native core before the
        generator runs, and its rule, light and natives replace the old organism depth.
        """
        self.universe_key = universe.key
        self.universe = universe
        self.boss_slot = boss_slot
        self.in_workshop = False
        self.menu_mode = ""
        route = list(self.route)
        route[self.depth_index] = self._universe_depth(universe, boss_slot)
        self.route = tuple(route)
        self.enter_depth(self.depth_index)
        # bible 02: the anchor point is open unless a Zwischengegner guards it (boss slot)
        self.exit_open = not self.boss_slot
        self._klonita_arrives()

    def _dress_universe_level(self, level: Level, shaped: dict[str, Any] | None = None) -> Level:
        """Universe fields (V9) for an organism level: regions, arenas, quest giver."""
        w = self.world
        if shaped and shaped.get("exit"):  # the universe moved the anchor point (islands)
            level = replace(level, exit=shaped["exit"])
        if shaped and shaped.get("arena") and level.arena is not None:
            level = replace(level, arena=shaped["arena"])
        if shaped and shaped.get("quest_target"):
            level = replace(level, quest_target=shaped["quest_target"])
        rng = random.Random(self.seed * 7919 + (self.plan.slot if self.multiverse else 0))
        topology = UNIVERSE_TOPOLOGY.get(self.universe.key, "vertical")
        bands = region_bands(w.width, w.height, topology)
        regions = [(r.key, band) for r, band in zip(self.universe.regions, bands, strict=False)]
        mid = self._open_spot(rng, level.spawn, min_dist=w.width * 0.3)
        if mid is None:
            mid = (w.width // 2, w.height // 2)
        mid_arena = self._clamp_rect(mid[0] - 30, mid[1] - 60, mid[0] + 30, mid[1])
        if shaped and shaped.get("mid_arena"):  # the universe built its own arena (bible 03)
            mid_arena = self._clamp_rect(*shaped["mid_arena"])
        boss_arena = (0, 0, 0, 0)
        if level.arena is not None:  # boss slot: the depth's guarded chamber
            ax, ay = level.arena
            boss_arena = self._clamp_rect(int(ax) - 40, int(ay) - 30, int(ax) + 40, int(ay) + 30)
        giver = self._open_spot(rng, level.spawn, min_dist=40, max_dist=260) or level.spawn
        return replace(
            level,
            universe_key=self.universe.key,
            exit_point=level.exit,
            mid_boss_arena=mid_arena,
            boss_arena=boss_arena,
            regions=regions,
            quest_giver=giver,
        )

    def _add_universe_features(self) -> None:
        """The one or two things that make a universe more than recoloured caves (bible 03)."""
        if self.universe.key == "aktenhalde":
            self._add_firebreaks()

    def _add_firebreaks(self) -> None:
        """Aktenhalde "Brandabschnitte": walls of non-burning ink paper cut the paper mass
        into sections of at most FIREBREAK_CELL, so one fire never eats the whole universe.
        Only paper cells are replaced; tunnels and caves stay open."""
        w = self.world
        paper, wall = mat.MAT_ID.get("papier"), mat.MAT_ID.get("tintenpapier")
        if paper is None or wall is None or paper == wall:
            return
        # the deep paper mass is ink-soaked: only the lining of the caves can burn
        universe_features.paper_skin(w, paper, wall)
        step_x, step_y = FIREBREAK_CELL
        for x0 in range(step_x, w.width, step_x):
            for x in range(x0, min(w.width, x0 + FIREBREAK_THICKNESS)):
                for y in range(w.height):
                    if w.get(x, y) == paper:
                        w.set_cell(x, y, wall)
        for y0 in range(step_y, w.height, step_y):
            for y in range(y0, min(w.height, y0 + FIREBREAK_THICKNESS)):
                for x in range(w.width):
                    if w.get(x, y) == paper:
                        w.set_cell(x, y, wall)

    def _fill_caches(self, lockers: Any) -> None:
        """What waits in a universe's hiding places (Aktenschraenke behind paper doors,
        Kaugummi-Hoehlen ...): gold in each, a sample in the first, a module in every third."""
        rank = self.plan.rank if self.multiverse else self.rank
        for i, (x, y) in enumerate(lockers):
            if self.mirror:
                x = self.world.width - 1 - x
            amount = creature_gold(rank, self.rng, big=True)
            self.pickups.append(Pickup(x - 3, y - 2, kind="gold", amount=amount))
            if i == 0 and self.universe.samples:
                key = self.universe.samples[-1]
                self.pickups.append(Pickup(x + 3, y - 2, kind="sample", item_key=key, amount=1))
            elif i % 3 == 1:
                self.pickups.append(Pickup(x + 3, y - 2, block=random_block(self.rng)))

    def _clamp_rect(self, x0: int, y0: int, x1: int, y1: int) -> tuple[int, int, int, int]:
        w, h = self.world.width, self.world.height
        x0, y0 = max(0, min(x0, w - 2)), max(0, min(y0, h - 2))
        return (x0, y0, max(x0 + 1, min(x1, w)), max(y0 + 1, min(y1, h)))

    def _open_spot(
        self,
        rng: random.Random,
        spawn: tuple[int, int],
        min_dist: float = 0.0,
        max_dist: float = float("inf"),
    ) -> tuple[int, int] | None:
        """A floor point with room for a large body above it, at a distance from spawn."""
        w = self.world
        for _ in range(600):
            x = rng.randint(40, w.width - 40)
            y = rng.randint(40, w.height - 40)
            if w.get(x, y) != mat.AIR:
                continue
            while y < w.height - 3 and w.get(x, y + 1) == mat.AIR:
                y += 1
            if not w.rect_blocked(x, y + 1, 1, 1) or w.rect_blocked(x - 12, y - 30, 24, 30):
                continue
            if min_dist <= math.dist((x, y), spawn) <= max_dist:
                return (x, y)
        return None

    def _level_keep(self) -> list[tuple[int, int, int]]:
        """Arenas and the quest giver stay dry when a universe floods (features.flood)."""
        keep = []
        for arena in (self.level.mid_boss_arena, self.level.boss_arena):
            if arena and arena != (0, 0, 0, 0):
                cx, cy = (arena[0] + arena[2]) // 2, (arena[1] + arena[3]) // 2
                keep.append((cx, cy, max(arena[2] - arena[0], arena[3] - arena[1]) // 2 + 8))
        if self.level.quest_giver is not None:
            keep.append((*self.level.quest_giver, 16))
        return keep

    def _ensure_universe_paths(self) -> None:
        """Dig passages so the start reaches the anchor point, the arenas and the quest giver.

        The universe generators do not guarantee this themselves (first playtest: trapped in
        Glibbria's start area). Same repair as the organism levels use (flying allowed).
        """
        level = self.level
        targets = [level.exit]
        for arena in (level.mid_boss_arena, level.boss_arena):
            if arena and arena != (0, 0, 0, 0):
                targets.append(((arena[0] + arena[2]) // 2, (arena[1] + arena[3]) // 2))
        if level.quest_giver is not None:
            targets.append(level.quest_giver)
        for target in targets:
            ensure_path(self.world, level.spawn, target)

    def _universe_depth(self, universe: Universe, boss_slot: bool = False) -> Depth:
        """An organism depth re-dressed as ``universe`` (material set, rule, natives).

        The n-th universe of the run uses the n-th organism depth as its terrain template,
        so caves grow with the run; a boss slot keeps the depth's boss chamber.
        """
        natives = tuple((key, NATIVES_PER_SPECIES) for key in universe.natives if key in SPECIES)
        if universe.big and universe.big in SPECIES:
            natives += ((universe.big, 1),)
        slot = self.plan.slot if self.multiverse else 1
        template = DEPTHS[min(len(DEPTHS) - 2, max(0, slot - 1))]  # never the final depth
        return replace(
            template,
            key=universe.key,
            name_de=universe.name_de,
            walkers=0,
            flyers=0,
            spitters=0,
            bloats=0,
            extra=natives,
            wall="fleisch",  # flesh walls: the universe's main material forms the mass
            blocks=UNIVERSE_BLOCKS,
            boss=universe.boss if boss_slot else None,
            final=False,
            ambient=universe.ambient,
            material_set=universe.material_set,
            rule=universe.rule if universe.rule in RULE_KEYS else "",
            size=None,  # the run's default size for now; SHAPES sizes come after the playtest
        )

    # ------------------------------------------------------------ quests (V13b)

    def _start_quest(self) -> None:
        """D23: every universe level has its challenge and the native who gives it."""
        self.quest = None
        key = f"challenge_{self.universe.key}"
        if key not in QUESTS or self.in_sanctum or self.in_workshop:
            return
        self.quest = quest_for(self.universe.key)
        spot = self.level.quest_giver
        if spot is None:  # own dice: the quest must not shift the run's other random rolls
            rng = random.Random(self.seed * 53 + self.depth_index)
            spot = self._open_spot(rng, self.level.spawn, min_dist=40, max_dist=260)
        if spot is None:
            sx, sy = self.level.spawn
            spot = (sx + 30, sy + self.player.height - 1)
        spec = SPECIES[self.quest.spec.giver]
        giver = self.enemies.spawn(spec.key, spot[0] - spec.width // 2, spot[1] - spec.height)
        giver.giver = True
        giver.stance = "passive"
        giver.aggro = False
        if self.ng or self.parallel:
            giver.empower(self.power)

    def _on_bus_event(self, name: str, payload: dict[str, Any]) -> None:
        """Every emitted event reaches the quest; a few make the world react."""
        if name == "quest_accepted" and payload.get("key") == "challenge_aktenhalde":
            self._scatter_forms()
        elif name == "noise":
            self._make_noise(
                float(payload.get("x", 0.0)), float(payload.get("y", 0.0)),
                float(payload.get("radius", 80.0)),
            )  # fmt: skip
        if name == "boss_phase" and payload.get("phase") == 0:
            self.klonita_trigger("boss_spawn")
        elif name == "wanted_change":
            stars = int(payload.get("stars", 0))
            if stars >= 3 and not self._wanted_warned:
                self._wanted_warned = True
                self.klonita_trigger("wanted_high")
            elif stars < 3:
                self._wanted_warned = False
        if self.quest is not None:
            self.quest.on_event(name, payload, self)

    def _make_noise(self, x: float, y: float, radius: float) -> None:
        """Noise wakes sleepers (C09); who wakes up is announced on the bus (D29)."""
        wake_events: list[tuple[str, dict[str, Any]]] = []
        self.enemies.on_noise(x, y, radius, wake_events)
        if wake_events:
            self.events.append("wake")
        for name, data in wake_events:
            self.emit(name, **data)

    def _scatter_forms(self) -> None:
        """D25: six forms to stamp, on free floor spots around the level."""
        for _ in range(FORMS_TO_STAMP):
            spot = self._open_spot(self.rng, self.level.spawn, min_dist=30)
            if spot is None:
                px, py = self.player.center
                spot = (int(px), int(py))
            self.pickups.append(Pickup(spot[0], spot[1] - 2, kind="form_stamp", seen=True))

    def _ring_bells(self, blasts: list[Blast], dt: float) -> None:
        """D29: an explosion that touches bell bronze rings the bell, and that is loud."""
        self._bell_cooldown = max(0.0, self._bell_cooldown - dt)
        bronze = mat.MAT_ID.get("glockenbronze")
        if bronze is None or self._bell_cooldown > 0:
            return
        for blast in blasts:
            reach = blast.radius + 3
            cells = (
                (blast.x + dx, blast.y + dy)
                for dy in range(-reach, reach + 1, 2)
                for dx in range(-reach, reach + 1, 2)
            )
            if any(self.world.get(x, y) == bronze for x, y in cells):
                self._bell_cooldown = BELL_COOLDOWN
                self.emit("bell_rung", x=float(blast.x), y=float(blast.y))
                self.emit("noise", x=float(blast.x), y=float(blast.y), radius=200.0)
                return

    def enter_headquarters(self) -> None:
        """Enter the authority headquarters for the true ending (Contract V17, Card F10).

        No workshop visit, full health, the endless file hall and stage "anhoerung"."""
        self.in_workshop = self.in_sanctum = False
        self.menu_mode = ""
        hall = replace(
            self.route[self.depth_index], key="hauptquartier", name_de="Hauptquartier",
            material_set="aktenhalde", rule="", boss=None, final=False, size=None, ambient=0.6,
        )  # fmt: skip
        route = list(self.route)
        route[self.depth_index] = hall
        self.route = tuple(route)
        self._prepare_world(hall)
        spawn = generate_headquarters_arena(self.world)
        self.level = Level((spawn[0], spawn[1] - self.player.height), (-999, -999))
        self.enemies.creatures = []
        self.pickups = []
        self.projectiles.clear()
        self.boss_script = None
        self.extra_scripts = []
        self.quest = None
        self.exit_open = False
        self.outcome = ""
        self.player.place(*self.level.spawn)
        self.player.hp = self.player.max_hp
        self.in_headquarters = True
        self.in_final = False
        self.hq_controller = HeadquartersController()
        self.hq_controller.spawn_stage(self)
        self.boss_line("Die Splitter erinnern sich an dich.")

    def final_home_name_de(self) -> str:
        """The name of the home world the portal frame offers after six universes."""
        species = final_evil_self(self)
        return evil_homes.HOME_NAMES_DE.get(species, SPECIES[species].name_de)

    def enter_final(self) -> None:
        """The final fight: the home world of ``plan.evil_self`` (Contract V17 §2, Card F19).

        The world becomes her 1280x720 hall in her own material set; she waits in the
        middle with ``EVIL_HP`` and her four-phase script. Her death sets ``victory``."""
        species = final_evil_self(self)
        self.in_workshop = self.in_sanctum = False
        self.in_headquarters = False
        self.menu_mode = ""
        self.universe_key = species
        home = replace(
            self.route[self.depth_index], key=species, name_de=self.final_home_name_de(),
            material_set=species, rule="", boss=species, final=False, size=evil_homes.HOME_SIZE,
            ambient=0.7, extra=(), walkers=0, flyers=0, spitters=0, bloats=0,
        )  # fmt: skip
        route = list(self.route)
        route[self.depth_index] = home
        self.route = tuple(route)
        if self.on_generate is not None:
            self.on_generate(home.name_de)
        self._prepare_world(home)
        self.world.reseed(self.rng.randrange(2**31))
        self.level = evil_homes.generate_evil_home(self.world, species, self.seed)
        if mat.ACTIVE is not self._world_set:
            mat.activate(self._world_set)
        self.enemies.creatures = []
        self.pickups = []
        self.projectiles.clear()
        self.extra_scripts = []
        self.quest = None
        self.exit_open = False
        self.outcome = ""
        self.time_in_depth = 0.0
        self.player.place(*self.level.spawn)
        self.player.hp = self.player.max_hp
        spec = SPECIES[species]
        ax, ay = self.level.arena or (self.world.width // 2, self.world.height // 2)
        boss = self.enemies.spawn(species, ax - spec.width // 2, ay - spec.height // 2)
        boss.max_hp = boss.hp = float(EVIL_HP[species])
        self.boss_script = make_boss_script(boss)
        self.in_final = True
        self._final_timers = {"press": evil_homes.PRESS_INTERVAL, "cannon": 0.0, "stamp": 0.0}
        self._press_cells = []
        self.records.discover("universe", species)
        self._log("heimatwelt_betreten", boese_ich=species)
        self._klonita_arrives()
        self.boss_line(f"{spec.name_de}: Du bist spät dran, Cloita.")

    def _tick_final_arena(self, dt: float) -> None:
        """Arena mechanics of the home worlds (V17 §2): slippery gold and the throne cannon,
        light trails of the Good One, conveyor belts and presses of Omega."""
        if not self.in_final or self.boss_script is None:
            return
        species = self.universe_key
        boss = self.boss_script.boss
        phase = self.boss_script.phase
        timers = self._final_timers
        if species == "boese_kaiserin":
            if phase >= 3 and not boss.dead:  # the throne becomes a cannon
                timers["cannon"] = timers.get("cannon", 0.0) - dt
                if timers["cannon"] <= 0.0:
                    timers["cannon"] = evil_homes.CANNON_INTERVAL
                    for key, tx, ty in self.level.destructible_props:
                        if key != "thron":
                            continue
                        px, py = self.player.center
                        angle = math.atan2(py - ty, px - tx)
                        self.projectiles.spawn(
                            [Shot(CATALOG["feuerball"])], float(tx), float(ty), angle, ENEMY_TEAM
                        )
                        self.events.append("shoot")
        elif species == "boese_gute":
            light = mat.opt_id("heiliges_licht")
            if light is not None:  # her light rays leave holy light behind
                for p in self.projectiles.items:
                    if p.alive and p.team == ENEMY_TEAM and p.trail is None:
                        p.trail = light
            if phase >= 2 and not getattr(self.klonita, "converted", 0.0):
                # conversion: Klonita on her side for ten seconds (harmless, bible 05)
                self.klonita.converted = evil_homes.CONVERSION_TIME
            if getattr(self.klonita, "converted", 0.0):
                self.klonita.converted = max(0.0, self.klonita.converted - dt)
        elif species == "boese_omega":
            self._run_conveyors(dt)
            self._run_presses(dt)

    def _run_conveyors(self, dt: float) -> None:
        belt = mat.opt_id("foerderband")
        if belt is None:
            return
        bodies = [self.player.body] + [
            c.body for c in self.enemies.creatures if not c.spec.flying and not c.dead
        ]
        for body in bodies:
            if not body.on_ground:
                continue
            row = body.y + body.height
            under = {self.world.get(x, row) for x in range(body.x, body.x + body.width)}
            if belt not in under:
                continue
            direction = evil_homes.belt_direction(body.x + body.width // 2)
            body._move_x(self.world, direction * evil_homes.BELT_SPEED * dt)

    def _run_presses(self, dt: float) -> None:
        """Every three seconds all four presses stamp down: 30 damage in their strip."""
        timers = self._final_timers
        steel = mat.opt_id("stahl")
        if self._press_cells:  # a stamp is down: lift it again after a moment
            timers["stamp"] -= dt
            if timers["stamp"] <= 0.0:
                for x0, y0, x1, y1 in self._press_cells:
                    self.world.fill_rect(x0, y0, x1, y1, mat.AIR)
                self._press_cells = []
            return
        timers["press"] -= dt
        if timers["press"] > 0.0:
            return
        timers["press"] = evil_homes.PRESS_INTERVAL
        timers["stamp"] = evil_homes.PRESS_HOLD
        floor = evil_homes.FLOOR_Y
        boss = self.boss_script.boss if self.boss_script is not None else None
        for key, px, py in self.level.destructible_props:
            if key != "presse":
                continue
            strip = (px, py, px + evil_homes.PRESS_WIDTH, floor)
            for body in [self.player.body] + [c.body for c in self.enemies.creatures]:
                if boss is not None and body is boss.body:
                    continue
                if body.x < strip[2] and body.x + body.width > strip[0] and body.y + body.height > strip[1]:
                    body.hurt(evil_homes.PRESS_DAMAGE, "presse")
            if steel is not None:  # the strip is kept free of ledges by the generator
                self.world.fill_rect(*strip, steel)
                self._press_cells.append(strip)
        self.events.append("blast_big")
        self.emit("noise", x=float(self.world.width // 2), y=float(floor), radius=600.0)

    def offer_headquarters(self, x: float, y: float) -> bool:
        """After the final fight: the headquarters portal appears if the run earned it."""
        if not can_enter_headquarters(self):
            return False
        portal = Pickup(x, y, portal=True, floating=True, kind="portal", item_key="headquarters")
        self.pickups.append(portal)
        return True

    def resolve_empress_bargain(self, accepted: bool) -> None:
        """Answer the Empress's offer (Card F08): yes ends the run with the evil ending."""
        apply_empress_bargain(self, accepted)
        self.menu_mode = ""
        self.menu_index = 0

    def _spawn_echo(self) -> None:
        """F08: on the first universe of rank 2 and 3 an echo of an evil self waits in the
        secret room: 30 % of her health, two phases."""
        if not self.multiverse or self.in_workshop:
            return
        species = echo_for_depth(self, len(self.plan.chosen))
        spot = self.level.secret
        if species is None:
            return
        if spot is None:  # no secret room in this terrain: somewhere far from the start
            spot = self._open_spot(
                random.Random(self.seed * 59 + self.depth_index), self.level.spawn,
                min_dist=self.world.width * 0.3,
            )  # fmt: skip
        if spot is None:
            return
        spec = SPECIES[species]
        echo = self.enemies.spawn(species, spot[0] - spec.width // 2, spot[1] - spec.height // 2)
        echo.echo = True
        echo.max_hp = echo.hp = EVIL_HP[species] * ECHO_HP_FACTOR
        script = make_boss_script(echo)
        if script is not None:
            self.extra_scripts.append(script)

    def say(
        self,
        speaker: str,
        text: str,
        x: float,
        y: float,
        ttl: float = 3.0,
        color: tuple[int, int, int] = (235, 225, 255),
    ) -> None:
        """Show a speech bubble above (x, y) (Contract V22, Card F14).

        At most 60 characters, at most three bubbles, and one per speaker every 8 s."""
        now = float(self.stats.get("time", 0.0))
        last = self._say_clock.get(speaker)
        if last is not None and now - last < SAY_INTERVAL and now >= last:
            return
        self._say_clock[speaker] = now
        if len(text) > SAY_MAX_CHARS:
            text = text[: SAY_MAX_CHARS - 1] + "…"
        while len(self.bubbles) >= SAY_MAX_BUBBLES:
            self.bubbles.pop(0)
        self.bubbles.append(
            SpeechBubble(
                speaker=speaker,
                text=text,
                world_x=x,
                world_y=y,
                remaining=ttl,
                color=color,
            )
        )

    def _klonita_arrives(self) -> None:
        """A new universe: Klonita appears next to the player with a fresh quirk."""
        self.klonita.new_universe()
        self.klonita.x, self.klonita.y = self.player.center
        self._low_hp_warned = False
        self.klonita_trigger("enter_universe")

    def _tick_klonita(self, dt: float, controls: Controls) -> None:
        """Card F14: bubbles age, [K] toggles Klonita, she acts, and the HP trigger fires."""
        for bubble in self.bubbles:
            bubble.remaining -= dt
            if bubble.speaker == "Klonita":  # her bubble floats along with her
                bubble.world_x, bubble.world_y = self.klonita.x, self.klonita.y - 10
        self.bubbles = [b for b in self.bubbles if b.remaining > 0]
        klonita = self.klonita
        if controls.klonita and not self.player.dead:
            state = klonita.toggle()
            if state in ("follow", "dismissed"):
                topic = "called" if state == "follow" else "dismissed"
                if state == "follow":
                    klonita.x, klonita.y = self.player.center
                self.say("Klonita", line_for(topic, self.klonita_rng), klonita.x, klonita.y - 10)
        if not self.multiverse:
            return  # the classic descent has no companion (she lives in the workshop)
        if self.in_workshop:  # she rests on the couch (V18); only her tip quirk may fire
            klonita.update(dt, self)
            return
        body = self.player.body
        share = body.hp / body.max_hp if body.max_hp > 0 else 1.0
        if share < LOW_HP_SHARE and not self._low_hp_warned and not self.player.dead:
            self._low_hp_warned = True
            self.klonita_trigger("player_low_hp")
        elif share > 0.5:
            self._low_hp_warned = False
        klonita.update(dt, self)

    def klonita_trigger(self, trigger: str) -> None:
        """One of Klonita's five auto triggers: she comes back and says a line."""
        line = self.klonita.on_trigger(trigger, self)
        if line:
            self.say("Klonita", line, self.klonita.x, self.klonita.y - 10)

    def add_wanted(self, delta: float, reason: str) -> None:
        """Raise or lower the wanted level and tell the bus (Contract V15, Card F02)."""
        if self.wanted.add(delta, reason):
            self._wanted_changed(reason)

    def _wanted_changed(self, reason: str) -> None:
        self.emit("wanted_change", level=self.wanted.level, stars=self.wanted.stars, reason=reason)

    def _next_blueprint(self) -> str | None:
        """A block the fabricator cannot build yet; found modules come first, then the
        lowest tier (the fabricator builds block keys, Contract V20)."""
        from src.spells import BLOCKS

        known = set(self.records.blueprints)
        pool = [b for b in BLOCKS if not b.retired and b.key not in known and b.key in CATALOG]
        if not pool:
            return None
        seen = set(getattr(self, "known_blocks", ()) or ()) | set(self.records.blocks)
        rng = random.Random(self.seed * 37 + len(known))
        found = [b for b in pool if b.key in seen]
        choice = found or [b for b in pool if b.rarity_tier == min(x.rarity_tier for x in pool)]
        return rng.choice(choice).key

    def final_score(self) -> int:
        """The run's score (Contract V23, Card G04/G06)."""
        from src.records import compute_score

        depth = len(self.plan.chosen) + 1 if self.multiverse and self.plan else self.depth_index + 1
        return compute_score(
            depth=depth, kills=int(self.stats.get("kills", 0)), gold=int(self.pearls),
            samples_collected=int(self.stats.get("samples", 0)),
            challenges_won=int(self.stats.get("quests", 0)),
            bosses_killed=int(self.stats.get("bosses", 0)),
            victory=bool(self.victory or self.outcome == "victory"),
            true_ending=bool(self.true_ending),
        )  # fmt: skip

    def final_rank(self) -> str:
        from src.records import rank_for_score

        return rank_for_score(self.final_score())

    def boss_line(self, text_de: str) -> None:
        """Show a boss line at the top of the screen (Contract V22, Card F14)."""
        self.boss_banner = (text_de, BOSS_LINE_TIME)

    def handle_menu_input(self, key: int) -> bool:
        """Handle keyboard navigation for modal overlays (Card G09, G14, G22)."""
        import pygame

        if self.menu_mode == "empress_bargain":
            if key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                self.menu_index = 1 - min(1, self.menu_index)
                return True
            if key in (pygame.K_RETURN, pygame.K_e):
                self.resolve_empress_bargain(self.menu_index == 0)
                return True
            if key == pygame.K_ESCAPE:  # walking away is a "no": the fight goes on
                self.resolve_empress_bargain(False)
                return True
            return False

        if self.menu_mode == "archive":  # G05: five tabs
            from src.menus import ARCHIVE_TABS

            if key == pygame.K_ESCAPE:
                self.menu_mode = ""
                self.menu_index = 0
                return True
            if key in (pygame.K_TAB, pygame.K_RIGHT, pygame.K_d):
                self.menu_index = (self.menu_index + 1) % len(ARCHIVE_TABS)
                return True
            if key in (pygame.K_LEFT, pygame.K_a):
                self.menu_index = (self.menu_index - 1) % len(ARCHIVE_TABS)
                return True
            return False

        if self.menu_mode == "portal_select":
            offers = self.plan.offers() if self.multiverse else []
            if not offers:
                if self.multiverse and self.plan.finished and key in (pygame.K_RETURN, pygame.K_e, pygame.K_1):
                    self.menu_mode = ""
                    self.portal_index = self.menu_index = 0
                    self.enter_final()
                    return True
                if key == pygame.K_ESCAPE:
                    self.menu_mode = ""
                    self.menu_index = 0
                    return True
                return False

            if key in (pygame.K_UP, pygame.K_w):
                self.portal_index = (self.portal_index - 1) % len(offers)
                self.menu_index = self.portal_index
                return True
            if key in (pygame.K_DOWN, pygame.K_s):
                self.portal_index = (self.portal_index + 1) % len(offers)
                self.menu_index = self.portal_index
                return True
            if key in (pygame.K_1, pygame.K_2):
                idx = 0 if key == pygame.K_1 else 1
                if idx < len(offers):
                    self.portal_index = idx
                    self.menu_index = idx
                    return True
            if key in (pygame.K_RETURN, pygame.K_e):
                idx = self.portal_index
                self.menu_mode = ""
                self.portal_index = 0
                self.menu_index = 0
                self.choose_next_universe(idx)
                return True
            if key == pygame.K_ESCAPE:
                self.menu_mode = ""
                self.menu_index = 0
                return True
            return False

        if self.menu_mode == "trader":
            t_key = self.active_trader_key or self.selected_trader_key
            offers = self.trader_offers.get(t_key, [])
            if key == pygame.K_ESCAPE:
                self.menu_mode = ""
                self.menu_index = 0
                return True
            if not offers:
                return False
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(offers)
                self.selected_offer_index = self.menu_index
                return True
            if key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(offers)
                self.selected_offer_index = self.menu_index
                return True
            if key in (pygame.K_RETURN, pygame.K_e):
                self.buy_trader_offer(t_key, self.menu_index)
                if (
                    self.menu_index >= len(self.trader_offers.get(t_key, []))
                    and self.menu_index > 0
                ):
                    self.menu_index -= 1
                    self.selected_offer_index = self.menu_index
                return True
            if key == pygame.K_t:
                self.buy_trader_offer(t_key, self.menu_index, use_samples=True)
                if (
                    self.menu_index >= len(self.trader_offers.get(t_key, []))
                    and self.menu_index > 0
                ):
                    self.menu_index -= 1
                    self.selected_offer_index = self.menu_index
                return True
            return key == pygame.K_r

        if self.menu_mode == "experiment":
            offers = self.experiment_offers
            if key == pygame.K_ESCAPE:
                self.menu_mode = ""
                self.menu_index = 0
                return True
            if not offers:
                return False
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(offers)
                return True
            if key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(offers)
                return True
            if key in (pygame.K_RETURN, pygame.K_e):
                self.pick_experiment(self.menu_index)
                return True
            if key == pygame.K_r:
                self.reroll_experiments()
                self.menu_index = 0
                return True
            return False

        if self.menu_mode == "fabricator":
            blueprints = list(getattr(getattr(self, "records", None), "blueprints", []))
            if key == pygame.K_ESCAPE:
                self.menu_mode = ""
                self.menu_index = 0
                return True
            if not blueprints:
                return False
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(blueprints)
                return True
            if key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(blueprints)
                return True
            if key in (pygame.K_RETURN, pygame.K_e):
                if 0 <= self.menu_index < len(blueprints):
                    self.craft_selected_recipe(blueprints[self.menu_index])
                return True
            return False

        if self.menu_mode == "minigame":
            tools = {
                pygame.K_1: "blast", pygame.K_2: "dig", pygame.K_3: "ignite", pygame.K_4: "pour",
            }  # fmt: skip
            if key in tools:  # Physik-o-Mat: the tool a click applies (see main._click_minigame)
                self.minigame_tool = tools[key]
                return True
            if key == pygame.K_ESCAPE:
                from src.minigames import MinigameResult

                if self.active_minigame is not None and self.active_minigame.result is None:
                    self.active_minigame.result = MinigameResult(
                        completed=True, won=False, message_de="Aufgegeben."
                    )
                self.menu_mode = ""
                self.menu_index = 0
                return True
            return False

        return False

    def _on_death(self, creature) -> None:
        cx, cy = creature.center
        if self.boss_script is not None and creature is self.boss_script.boss:
            self.boss_script.on_death(self)
            self.boss_script = None
        for script in [s for s in self.extra_scripts if s.boss is creature]:
            script.on_death(self)
            self.extra_scripts.remove(script)
        if creature.spec.prop:  # a burst sac: no kill, but maybe a chain reaction
            if creature.spec.blast:
                destroyed = self.world.explode(int(cx), int(cy), creature.spec.blast)
                if destroyed > 0:
                    self.emit("cells_destroyed", count=destroyed, gold_vein_cells=0)
                self._prop_blasts.append(Blast(int(cx), int(cy), creature.spec.blast))
            self.events.append("shatter")
            return
        self.stats["kills"] += 1
        self.emit(
            "kill", species=creature.spec.key, x=cx, y=cy,
            killer="player" if creature.last_cause != "Welt" else "world",
        )  # fmt: skip
        self._log("getoetet", kreatur=creature.spec.key, durch=creature.last_cause)
        self.discoveries.append(("creature", creature.spec.key))
        if not creature.spec.boss and creature.spec.gore == "blood":
            width = max(3, creature.width - 2)
            self.chunks.drop_corpse(
                self.world, int(cx - width / 2), int(creature.y + creature.height - CORPSE_HEIGHT),
                width, corpse_material(),
            )  # fmt: skip
        if "blutdurst" in self.perks and not self.player.dead:
            self.player.hp = min(self.player.max_hp, self.player.hp + BLOODLUST_HEAL)
        if not self.multiverse:  # only the organism descent still pays its old loot table
            self.pickups.append(Pickup(cx, cy, pearls=creature.spec.pearls))
        peaceful = creature.spec.stance in ("peaceful", "passive", "neutral", "territorial", "shy")
        by_others = creature.last_cause.startswith("Geschoss")  # a creature's shot, not ours
        if peaceful and not by_others:
            self.add_wanted(0.25, "Unnötige Gewalt")  # F02 / V15
        rank = self.plan.rank if self.multiverse else self.rank
        mid_boss_keys = {boss for pairs in MID_BOSSES.values() for boss, _ in pairs}
        if (
            getattr(creature.spec, "is_boss", False) or getattr(creature.spec, "boss", False)
        ) and creature.spec.key in mid_boss_keys:
            gold_amount = boss_gold(rank)
        elif creature.spec.key in AGENT_GOLD:  # F02: agents pay a fixed sum, maybe a badge
            gold_amount = AGENT_GOLD[creature.spec.key]
            if self.rng.random() < BADGE_CHANCE.get(creature.spec.key, 0.0):
                self.pickups.append(Pickup(cx + 6, cy, kind="badge", amount=1))
        elif getattr(creature.spec, "is_mid_boss", False):
            gold_amount = mid_boss_gold(rank)
        else:
            is_big = bool(
                getattr(creature.spec, "big", False)
                or (
                    self.universe is not None
                    and getattr(self.universe, "big", None) == creature.spec.key
                )
            )
            gold_amount = creature_gold(rank, self.rng, big=is_big)
        self.pickups.append(Pickup(cx, cy, kind="gold", amount=gold_amount))
        sample_key = creature.spec.drops_sample or getattr(self.universe, "sample_key", "")
        if sample_key:
            sample_chance = getattr(creature.spec, "sample_chance", 0.35)
            if (
                getattr(creature.spec, "is_mid_boss", False)
                or getattr(creature.spec, "is_boss", False)
                or getattr(creature.spec, "boss", False)
                or self.rng.random() < sample_chance
            ):
                self.pickups.append(Pickup(cx, cy, kind="sample", item_key=sample_key, amount=1))
        self.events.append("blast_big" if creature.spec.boss else "kill")
        if creature.spec.boss:
            self.stats["bosses"] = self.stats.get("bosses", 0) + 1
            self._log(
                "waechter_besiegt", kreatur=creature.spec.key, zeit=round(self.stats["time"], 1)
            )
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

    def _handle_creature_events(self, events: list[tuple[str, dict[str, Any]]]) -> None:
        """Card C16: process split, steal, summon and noise events from creature update."""
        for event_name, payload in events:
            if event_name == "split":
                species = str(payload.get("species", ""))
                x = float(payload.get("x", 0.0))
                y = float(payload.get("y", 0.0))
                gen = int(payload.get("generation", 0))
                for dx in (-8.0, 8.0):
                    child = self.enemies.spawn(species, x + dx, y)
                    child.generation = gen + 1
            elif event_name == "steal_return":
                x = float(payload.get("x", 0.0))
                y = float(payload.get("y", 0.0))
                kind = str(payload.get("kind", "gold"))
                item_key = str(payload.get("item_key", ""))
                amount = int(payload.get("amount", 1))
                self.pickups.append(Pickup(x, y, kind=kind, item_key=item_key, amount=amount))
            elif event_name == "summon":
                target_species = str(payload.get("target_species", ""))
                x = float(payload.get("x", 0.0))
                y = float(payload.get("y", 0.0))
                count = int(payload.get("count", 1))
                summoner = payload.get("summoner")
                for _ in range(count):
                    self._spawn_summon(target_species, x, y, summoner)
            elif event_name == "noise":
                x = float(payload.get("x", 0.0))
                y = float(payload.get("y", 0.0))
                radius = float(payload.get("radius", 80.0))
                self._make_noise(x, y, radius)

    def _spawn_summon(self, species: str, x: float, y: float, summoner: Any) -> None:
        """A summoned helper: beside its summoner on free ground, on its side (faction)."""
        spec = SPECIES.get(species)
        if spec is None:
            return
        spot = self._summon_spot(spec, x, y, summoner)
        if spot is None:
            return  # no room: better no helper than one stuck in the wall
        child = self.enemies.spawn(species, *spot)
        if summoner is not None:
            child.faction = summoner.faction
            child.summoned = True
            child.aggro = True
            child.group_id = summoner.group_id
            summoner.helpers.append(child)

    def _summon_spot(self, spec: Any, x: float, y: float, summoner: Any) -> tuple[int, int] | None:
        """Top-left of a free box for ``spec`` next to (x, y), not overlapping the summoner;
        walkers stand on the ground."""
        w, h = spec.width, spec.height
        world = self.world
        gap = (summoner.width if summoner is not None else 0) // 2 + w // 2 + SUMMON_GAP
        for dist in (gap, gap + 8, gap + 16, gap + 28):
            for side in (1, -1):
                for lift in (0, -8, 8, -16, 16):
                    left = int(x + side * dist - w / 2)
                    top = int(y + lift - h / 2)
                    if world.rect_blocked(left, top, w, h):
                        continue
                    if summoner is not None and (
                        left < summoner.x + summoner.width and left + w > summoner.x
                        and top < summoner.y + summoner.height and top + h > summoner.y
                    ):
                        continue
                    if not spec.flying:  # drop onto the floor below (at most 40 cells)
                        for _ in range(40):
                            if world.rect_blocked(left, top + 1, w, h):
                                break
                            top += 1
                        else:
                            continue
                    return (left, top)
        return None

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
        if self.multiverse:  # multiverse run: the anchor point leads back to the workshop
            if not self.in_workshop:
                self.enter_workshop()
            return
        if self.in_sanctum:
            self.enter_depth(self.depth_index + 1)
        elif self.depth_index + 1 < len(DEPTHS):
            self.enter_sanctum()


def _pack(buffer: bytearray) -> str:
    return base64.b64encode(zlib.compress(bytes(buffer), 6)).decode("ascii")


def _unpack(text: str) -> bytes:
    return zlib.decompress(base64.b64decode(text.encode("ascii")))


FIREBREAK_CELL = universe_features.FIREBREAK_CELL  # Aktenhalde: paper sections (cells)
FIREBREAK_THICKNESS = universe_features.FIREBREAK_THICKNESS
NATIVES_PER_SPECIES = 6  # natives of each species per universe level (before area scaling)
BOSS_LINE_TIME = 4.0  # seconds a boss line stays on screen
SAY_INTERVAL = 8.0  # seconds between two bubbles of the same speaker (V22)
SAY_MAX_CHARS = 60
SAY_MAX_BUBBLES = 3
LOW_HP_SHARE = 0.25  # Klonita worries below this (auto trigger)
SUMMON_GAP = 6  # cells between a summoner and its helper
CORPSE_MAX_HARDNESS = 1  # remains never wall anything in (playtest 2026-11-13)


def corpse_material() -> int:
    """What a dead creature's remains are made of in the active universe: its stand-in for
    flesh if that is soft, else sand (in the Abtei flesh stands for masonry, hardness 3)."""
    flesh = mat.FLESH
    if mat.HARDNESS[flesh] <= CORPSE_MAX_HARDNESS and mat.KIND[flesh] in (mat.SOLID, mat.POWDER):
        return flesh
    return mat.SAND


START_SAFE_RADIUS = 170.0  # no hostile spawns this close to the player's start (as populate)
QUEST_GIVER_RANGE = 32.0  # px: talk to the quest giver from this close
FORMS_TO_STAMP = 6  # Aktenhalde quest: forms scattered when it is accepted
BELL_COOLDOWN = 0.4  # seconds between two rings of the abbey bell
ABSORB_RADIUS = 260.0  # "Zauber zu Kraft" reaches this far around the player (cells)
UNIVERSE_BLOCKS = 5  # loose modules per universe level (playtest: the backpack overflowed)
# region layout per universe (bible 03), used for region effects on organism-built levels
UNIVERSE_TOPOLOGY = {
    "fleischwelt": "vertical", "aktenhalde": "horizontal", "glibbria": "islands",
    "kruemelreich": "top_split", "sporenklub": "vertical", "abtei": "vertical",
}  # fmt: skip


NEW_PICKUP_KINDS = frozenset(
    {
        "gold",
        "sample",
        "life_capsule",
        "memory_shard",
        "blueprint_shard",
        "crate",
        "badge",
        "formular_stempel",
        "form_stamp",
    }
)
# Playtest 2026-11-08: Physik-o-Mat and Schießstand were not fun; switched off until they are
# redesigned together with the user (code and tests of E07-E09/E14 stay in place).
MINIGAMES_ENABLED = False
AUTO_PICKUP_KINDS = frozenset({"gold", "sample", "blueprint_shard", "memory_shard", "badge"})
BLUEPRINT_SHARDS_NEEDED = 3
MILK_COOLDOWN = 8.0  # seconds before a giver can be milked again
MILK_DROPS = 4
MILK_HEAL = 3.0
BRIBE_COST = 20
BRIBE_RANGE = 32.0

PICKUP_FIELDS = (
    "kind",
    "item_key",
    "amount",
    "pearls",
    "perk",
    "heart",
    "cocoon",
    "eye",
    "reroll",
    "portal",
    "seen",
    "price",
    "floating",
)


def _pickup_data(item: Pickup) -> dict[str, Any]:
    data: dict[str, Any] = {"x": item.x, "y": item.y}
    data.update({name: getattr(item, name) for name in PICKUP_FIELDS})
    if item.block is not None:
        data["block"] = item.block
    if item.wand is not None:
        data["wand"] = {**asdict(item.wand), "blocks": list(item.wand.blocks)}
    if item.flask is not None:
        data["flask"] = [item.flask.key, item.flask.amount]
    return data


def _pickup_from(data: dict[str, Any]) -> Pickup | None:
    """Rebuild a saved item; unknown blocks, perks or broken entries are skipped."""
    try:
        item = Pickup(float(data["x"]), float(data["y"]))
        for name in PICKUP_FIELDS:
            if name in data:
                setattr(item, name, data[name])
        if item.perk is not None and item.perk not in PERK_BY_KEY:
            return None
        block = data.get("block")
        if block is not None:
            if block not in CATALOG:
                return None
            item.block = block
        wand = data.get("wand")
        if wand is not None:
            spec = WandSpec(**{**wand, "blocks": tuple(wand["blocks"])})
            if any(key not in CATALOG for key in spec.blocks):
                return None
            item.wand = spec
        if "flask" in data:
            item.flask = _flask_from(data["flask"])
            if item.flask is None:
                return None
    except (KeyError, TypeError, ValueError):
        return None
    return item


def _flask_from(data: object) -> Flask | None:
    """Rebuild a saved flask; anything odd gives no flask rather than an error."""
    if not isinstance(data, list) or len(data) != 2:
        return None
    material, amount = data
    if material is None:
        return Flask()
    if not isinstance(amount, int):
        return None
    if isinstance(material, int):  # saves before material sets: ids of the organism set
        keys = mat.KOERPER.keys()
        if not 0 <= material < len(keys):
            return None
        material = keys[material]
    if not isinstance(material, str) or material not in mat.LIBRARY:
        return None
    if mat.LIBRARY[material].kind != LIQUID:
        return None
    return Flask(material, max(0, min(CAPACITY, amount)))
