"""Creatures living in the organism and how they are placed in a level."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from src.body import ENEMY_TEAM, Body
from src.materials import ACID, AIR, BLOOD, BONE_DUST, FIRE, MUCUS, SPORES, TALLOW
from src.player import GRAVITY, MAX_FALL_SPEED
from src.projectiles import ProjectileSystem
from src.spells import CATALOG
from src.wand import Shot, Wand, WandSpec
from src.world import World, disc_offsets

Rect = tuple[int, int, int, int]


@dataclass(frozen=True)
class CreatureSpec:
    key: str
    name_de: str
    width: int
    height: int
    hp: float
    flying: bool
    speed: float  # px/s
    sight: float  # px
    melee_damage: float = 0.0
    melee_cooldown: float = 1.0
    jump_speed: float = 0.0
    # Ranged attacks are small wands (block keys); several patterns are cycled.
    patterns: tuple[tuple[str, ...], ...] = ()
    ranged_cooldown: float = 0.0
    ranged_range: float = 0.0
    radial: int = 0  # >0: cast every pattern in this many directions at once
    hover_height: float = 0.0  # flyers keep this far above the player
    stationary: bool = False
    summon: tuple[str, ...] = ()  # creature keys spawned periodically, in turn
    summon_interval: float = 0.0
    summon_max: int = 0
    boss: bool = False
    gore: int = BLOOD
    burst: int = 4  # radius of the gore splash on death
    pop_on_touch: bool = False  # bursts when it touches the player
    hangs: bool = False  # placed under ceilings instead of on floors
    pearls: int = 10  # blood pearls dropped on death
    fire_immune: bool = False
    acid_immune: bool = False
    prop: bool = False  # a lifeless object (no AI, hit by everyone, not counted as a kill)
    blast: int = 0  # explosion radius when it is destroyed
    ignites: bool = False  # sets its splash on fire when destroyed
    burrows: int = 0  # >0: digs through solid tissue with this radius as it moves
    inhale: float = 0.0  # >0: periodically sucks the player in (px/s) and breathes out spores


MAGGOT = CreatureSpec(
    "made", "Fleischmade", width=10, height=6, hp=20, flying=False, speed=45, sight=450,
    melee_damage=8, melee_cooldown=0.8, jump_speed=170, pearls=8,
)  # fmt: skip
SWARMER = CreatureSpec(
    "schwaermer", "Gallenschwärmer", width=9, height=7, hp=14, flying=True, speed=60,
    sight=450, patterns=(("sekret_saeure", "klumpen"),), ranged_cooldown=2.6,
    ranged_range=320, hover_height=60, pearls=12,
)  # fmt: skip
STOMACH_WORM = CreatureSpec(
    "magenwurm", "Der Magenwurm", width=28, height=14, hp=360, flying=True, speed=55,
    sight=650, melee_damage=15, melee_cooldown=1.0,
    patterns=(
        ("doppel", "sekret_saeure", "klumpen", "sekret_saeure", "klumpen"),
        ("beschleunigung", "nadel"),
        ("beschleunigung", "nadel"),
    ),
    ranged_cooldown=1.1, ranged_range=520, hover_height=70, boss=True, gore=ACID, pearls=150,
)  # fmt: skip
HEART = CreatureSpec(
    "herz", "Das Herz", width=40, height=36, hp=1000, flying=True, speed=0, sight=700,
    patterns=(("sekret_feuer", "klumpen"), ("sekret_saeure", "klumpen"), ("funke",)),
    ranged_cooldown=1.9, ranged_range=700, radial=12, stationary=True,
    summon=("made",), summon_interval=7.0, summon_max=5, boss=True,
)  # fmt: skip
BROOD_MOTHER = CreatureSpec(
    "brutmutter", "Die Brutmutter", width=36, height=26, hp=650, flying=True, speed=34,
    sight=650, melee_damage=18, melee_cooldown=1.2,
    patterns=(
        ("sekret_wucherung", "klumpen"),
        ("knochensplitter",),
        ("doppel", "sekret_sporen", "klumpen", "sekret_sporen", "klumpen"),
    ),
    ranged_cooldown=1.4, ranged_range=520, hover_height=55,
    summon=("sporenblase", "schwaermer"), summon_interval=5.0, summon_max=4,
    boss=True, gore=SPORES, pearls=220,  # solid gore would plug the exit
)  # fmt: skip
BONE_SPITTER = CreatureSpec(
    "knochenspeier", "Knochenspeier", width=8, height=7, hp=30, flying=True, speed=0,
    sight=380, patterns=(("beschleunigung", "nadel"), ("doppel", "nadel", "nadel")),
    ranged_cooldown=1.8, ranged_range=380, stationary=True, hangs=True, pearls=15,
)  # fmt: skip
SPORE_BLOAT = CreatureSpec(
    "sporenblase", "Sporenblase", width=9, height=9, hp=8, flying=True, speed=28, sight=300,
    melee_damage=6, pop_on_touch=True, gore=SPORES, burst=11, pearls=10,
)  # fmt: skip
EMBER_MAGGOT = CreatureSpec(
    "brandmade", "Brandmade", width=10, height=6, hp=26, flying=False, speed=58, sight=450,
    melee_damage=10, melee_cooldown=0.8, jump_speed=190, gore=FIRE, burst=6,
    fire_immune=True, pearls=14,
)  # fmt: skip
ACID_SPITTER = CreatureSpec(
    "saeurespucker", "Säurespucker", width=11, height=9, hp=34, flying=False, speed=30,
    sight=420, melee_damage=6, jump_speed=120,
    patterns=(("sekret_saeure", "klumpen"), ("gallenregen",)), ranged_cooldown=2.2,
    ranged_range=300, gore=ACID, acid_immune=True, pearls=16,
)  # fmt: skip
LEECH = CreatureSpec(
    "egel", "Blutegel", width=7, height=4, hp=8, flying=True, speed=95, sight=380,
    melee_damage=4, melee_cooldown=0.4, hover_height=0, pearls=6,
)  # fmt: skip
EYE_BLOAT = CreatureSpec(
    "augenblase", "Augenblase", width=11, height=11, hp=30, flying=True, speed=22, sight=600,
    patterns=(("beschleunigung", "knochenspeer"),), ranged_cooldown=3.2, ranged_range=560,
    hover_height=110, pearls=20,
)  # fmt: skip
MUCUS_CRAWLER = CreatureSpec(
    "schleimkriecher", "Schleimkriecher", width=16, height=9, hp=90, flying=False, speed=24,
    sight=360, melee_damage=18, melee_cooldown=1.3, jump_speed=0, gore=MUCUS, burst=8,
    acid_immune=True, pearls=24,
)  # fmt: skip
NERVE_KNOT = CreatureSpec(
    "nervenknoten", "Nervenknoten", width=9, height=9, hp=45, flying=True, speed=0, sight=420,
    patterns=(("funke",), ("nervenstrom",)), ranged_cooldown=2.6, ranged_range=420,
    radial=6, stationary=True, hangs=True, pearls=22,
)  # fmt: skip
BONE_EATER = CreatureSpec(
    "knochenfresser", "Der Knochenfresser", width=30, height=18, hp=520, flying=True, speed=46,
    sight=700, melee_damage=14, melee_cooldown=1.3,
    patterns=(("knochensaege",), ("beschleunigung", "knochenspeer"), ("doppel", "knochenspeer", "knochenspeer")),
    ranged_cooldown=1.5, ranged_range=520, hover_height=0, burrows=17, boss=True,
    gore=BONE_DUST, pearls=200,
)  # fmt: skip
BREATH = CreatureSpec(
    "atem", "Der Atem", width=40, height=30, hp=520, flying=True, speed=26, sight=700,
    melee_damage=12, melee_cooldown=1.3,
    patterns=(("sekret_sporen", "klumpen"), ("sekret_schleim", "klumpen")), radial=6,
    ranged_cooldown=3.0, ranged_range=600, hover_height=40, inhale=55.0,
    summon=("egel",), summon_interval=6.0, summon_max=6, boss=True, gore=MUCUS, pearls=240,
)  # fmt: skip
INHALE_TIME = 2.2  # seconds of each breath cycle spent sucking in
BREATH_CYCLE = 6.0
EXHALE_SHOTS = 12
SHAPESHIFTER = CreatureSpec(
    "gestaltwandler", "Gestaltwandler", width=10, height=10, hp=35, flying=True, speed=30,
    sight=420, patterns=(("wandlungsdruese",), ("funke",), ("funke",)), ranged_cooldown=3.0,
    ranged_range=320, hover_height=70, pearls=30,
)  # fmt: skip
TALLOW_SAC = CreatureSpec(
    "talgsack", "Talgsack", width=8, height=9, hp=3, flying=False, speed=0, sight=0,
    gore=TALLOW, burst=7, blast=12, ignites=True, prop=True, pearls=0,
)  # fmt: skip
ACID_SAC = CreatureSpec(
    "saeuresack", "Säuresack", width=8, height=9, hp=3, flying=False, speed=0, sight=0,
    gore=ACID, burst=8, blast=6, prop=True, acid_immune=True, pearls=0,
)  # fmt: skip
SPORE_SAC = CreatureSpec(
    "sporensack", "Sporensack", width=8, height=9, hp=2, flying=False, speed=0, sight=0,
    gore=SPORES, burst=12, prop=True, pearls=0,
)  # fmt: skip
PROPS = ("talgsack", "saeuresack", "sporensack")
SPECIES: dict[str, CreatureSpec] = {
    spec.key: spec
    for spec in (
        MAGGOT, SWARMER, BONE_SPITTER, SPORE_BLOAT, STOMACH_WORM, BROOD_MOTHER, HEART,
        EMBER_MAGGOT, ACID_SPITTER, LEECH, EYE_BLOAT, MUCUS_CRAWLER, NERVE_KNOT,
        TALLOW_SAC, ACID_SAC, SPORE_SAC, BONE_EATER, BREATH, SHAPESHIFTER,
    )
}  # fmt: skip

MELEE_REACH = 2  # px around the body that counts as touching
WANDER_PAUSE = 0.35  # chance that a new wander leg is a pause
HURT_FLASH = 0.08  # seconds a creature flashes after taking damage
MEMORY = 3.0  # seconds a creature keeps hunting the last place it saw the player


class Creature(Body):
    team = ENEMY_TEAM

    def __init__(self, spec: CreatureSpec, x: int, y: int, rng: random.Random) -> None:
        super().__init__(x, y, spec.width, spec.height, spec.hp)
        self.spec = spec
        self.blood = spec.gore
        self.fire_immune = spec.fire_immune
        self.acid_immune = spec.acid_immune
        if spec.prop:
            self.team = "neutral"  # everyone's shots and blasts can burst it
        self.rng = rng
        self.step_up = 3
        self.facing = 1
        self.attack_cooldown = 0.0
        self.ranged_cooldown = rng.uniform(0.5, spec.ranged_cooldown or 1.0)
        self.wander_dir = 0
        self.wander_time = 0.0
        self.flash = 0.0
        self.age = rng.uniform(0, 10)
        self.alerted = False
        self.memory = 0.0
        self.last_seen = (0.0, 0.0)
        self.pattern = 0
        self.summon_timer = spec.summon_interval
        self.summon_count = 0
        self.summons: list[str] = []  # creature keys the manager should spawn
        self.breath = 0.0  # position in the breathing cycle (inhaling bosses)
        self.power = 1.0  # damage factor (New Game+)
        self.flash_cooldown = 0.0
        self.inhaling = False
        self.attacks = [
            Wand(
                WandSpec(spec.name_de, blocks, mana_max=1e9, mana_regen=1e9, cast_delay=0, recharge=0),
                rng,
            )
            for blocks in spec.patterns
        ]

    def empower(self, power: float) -> None:
        """Scale health and damage (New Game+)."""
        self.power = power
        self.max_hp = self.hp = self.spec.hp * power

    def hurt(self, amount: float, cause: str = "") -> None:
        if amount > 0:
            if self.flash_cooldown <= 0:  # under constant fire it blinks instead of glowing white
                self.flash = HURT_FLASH
                self.flash_cooldown = HURT_FLASH * 3
            self.alerted = True
        super().hurt(amount, cause)

    def update(
        self, world: World, dt: float, player: Body, projectiles: ProjectileSystem
    ) -> None:
        if self.dead:
            return
        self.age += dt
        self.flash = max(0.0, self.flash - dt)
        self.flash_cooldown = max(0.0, self.flash_cooldown - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.ranged_cooldown = max(0.0, self.ranged_cooldown - dt)
        self.unstick(world)

        px, py = player.center
        if self.spec.burrows:  # it eats its way through and feels the player through bone
            cx, cy = self.center
            world.dig(int(cx), int(cy), self.spec.burrows, force=True)
            sees = not player.dead and math.hypot(px - cx, py - cy) <= self.spec.sight
        else:
            sees = not player.dead and self.can_see(world, px, py, self.spec.sight)
        self.alerted = self.alerted or sees
        if sees:
            self.memory = MEMORY
            self.last_seen = (px, py)
        else:
            self.memory = max(0.0, self.memory - dt)
        hunting = self.memory > 0 and not player.dead
        if self.spec.stationary:
            self.vx = self.vy = 0.0
        else:
            if self.spec.flying:
                self._fly(world, dt, hunting)
            else:
                self._crawl(world, dt, hunting)
            self.move(world, dt)

        if sees:
            self._attack(player, projectiles)
        if self.spec.inhale and self.alerted and not player.dead:
            self._breathe(world, dt, player, projectiles)
        if self.spec.summon and self.alerted:
            self.summon_timer -= dt
            if self.summon_timer <= 0:
                self.summon_timer = self.spec.summon_interval
                self.summons.append(self.spec.summon[self.summon_count % len(self.spec.summon)])
                self.summon_count += 1
        self.apply_environment(world, dt)

    # -------------------------------------------------------------- movement

    def _wander(self, dt: float) -> int:
        self.wander_time -= dt
        if self.wander_time <= 0:
            self.wander_time = self.rng.uniform(0.8, 2.5)
            self.wander_dir = 0 if self.rng.random() < WANDER_PAUSE else self.rng.choice((-1, 1))
        return self.wander_dir

    def _crawl(self, world: World, dt: float, hunting: bool) -> None:
        cx, _ = self.center
        px, _ = self.last_seen
        if hunting:
            direction = 0 if abs(px - cx) < 2 else (1 if px > cx else -1)
            speed = self.spec.speed
        else:
            direction = self._wander(dt)
            speed = self.spec.speed * 0.5
        if direction:
            self.facing = direction
        self.vx += (direction * speed - self.vx) * min(1.0, 8.0 * dt)
        wall_ahead = direction and self.blocked(world, self.x + direction, self.y - self.step_up)
        if wall_ahead and self.on_ground:
            if hunting:
                self.vy = -self.spec.jump_speed
            else:
                self.wander_dir = -self.wander_dir
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL_SPEED)

    def _fly(self, world: World, dt: float, hunting: bool) -> None:
        cx, cy = self.center
        if hunting:
            px, py = self.last_seen
            tx, ty = px, py - self.spec.hover_height
            dx, dy = tx - cx, ty - cy
            distance = math.hypot(dx, dy) or 1.0
            if distance < 12:
                dx = dy = 0.0
            wanted_vx = dx / distance * self.spec.speed
            wanted_vy = dy / distance * self.spec.speed
            self.facing = 1 if px > cx else -1
        else:
            direction = self._wander(dt)
            if direction:
                self.facing = direction
            wanted_vx = direction * self.spec.speed * 0.5
            wanted_vy = 0.0
        wanted_vy += math.sin(self.age * 5) * 18  # buzzing bob
        follow = min(1.0, 3.0 * dt)
        self.vx += (wanted_vx - self.vx) * follow
        self.vy += (wanted_vy - self.vy) * follow

    # --------------------------------------------------------------- attacks

    def _attack(self, player: Body, projectiles: ProjectileSystem) -> None:
        spec = self.spec
        if spec.melee_damage and self.attack_cooldown <= 0 and self._touches(player):
            player.hurt(spec.melee_damage * self.power, f"Biss: {spec.name_de}")
            self.attack_cooldown = spec.melee_cooldown
            if spec.pop_on_touch:
                self.hp = 0.0
                return
        if self.attacks and self.ranged_cooldown <= 0:
            cx, cy = self.center
            px, py = player.center
            if math.hypot(px - cx, py - cy) <= spec.ranged_range:
                wand = self.attacks[self.pattern % len(self.attacks)]
                self.pattern += 1
                wand.cooldown = wand.recharge_left = 0.0
                shots = wand.cast()
                if spec.radial:
                    turn = self.rng.uniform(0, math.tau)
                    for k in range(spec.radial):
                        angle = turn + math.tau * k / spec.radial
                        projectiles.spawn(shots, cx, cy, angle, self.team)
                else:
                    angle = math.atan2(py - cy, px - cx) - 0.25  # lob slightly upwards
                    projectiles.spawn(shots, cx, cy, angle, self.team)
                self.ranged_cooldown = spec.ranged_cooldown * self.rng.uniform(0.8, 1.2)

    def _breathe(
        self, world: World, dt: float, player: Body, projectiles: ProjectileSystem
    ) -> None:
        """Suck the player in for a while, then breathe out a ring of spores."""
        was_inhaling = self.inhaling
        self.breath = (self.breath + dt) % BREATH_CYCLE
        self.inhaling = self.breath < INHALE_TIME
        cx, cy = self.center
        px, py = player.center
        distance = math.hypot(cx - px, cy - py) or 1.0
        if self.inhaling and distance <= self.spec.sight:
            pull = self.spec.inhale * dt
            player._move_x(world, (cx - px) / distance * pull)
            player._move_y(world, (cy - py) / distance * pull * 0.6)
        elif was_inhaling:  # the breath turns: exhale
            spores = [Shot(CATALOG["klumpen"], (CATALOG["sekret_sporen"],), [])]
            for k in range(EXHALE_SHOTS):
                angle = math.tau * k / EXHALE_SHOTS
                projectiles.spawn(spores, cx, cy, angle, self.team)

    def _touches(self, other: Body) -> bool:
        r = MELEE_REACH
        return (
            self.x - r < other.x + other.width
            and other.x < self.x + self.width + r
            and self.y - r < other.y + other.height
            and other.y < self.y + self.height + r
        )


class EnemyManager:
    """All creatures of a level."""

    def __init__(self) -> None:
        self.creatures: list[Creature] = []

    def clear(self) -> None:
        self.creatures.clear()

    def alive(self) -> list[Creature]:
        return [c for c in self.creatures if not c.dead]

    def update(
        self,
        world: World,
        dt: float,
        player: Body,
        projectiles: ProjectileSystem,
        area: Rect,
    ) -> list[Creature]:
        """Update creatures inside ``area``; returns the ones that died this update."""
        x0, y0, x1, y1 = area
        for creature in self.creatures:
            cx, cy = creature.center
            if x0 <= cx < x1 and y0 <= cy < y1:
                creature.update(world, dt, player, projectiles)
        self._spawn_summons(world)
        died = [c for c in self.creatures if c.dead]
        for creature in died:
            cx, cy = creature.center
            radius = 12 if creature.spec.boss else creature.spec.burst
            world.splash(int(cx), int(cy), radius, creature.spec.gore)
            if creature.spec.ignites:
                for dx, dy in disc_offsets(radius):
                    x, y = int(cx) + dx, int(cy) + dy
                    if world.get(x, y) == creature.spec.gore and world.rng.random() < 0.3:
                        world.ignite(x, y)
        self.creatures = [c for c in self.creatures if not c.dead]
        return died

    def _spawn_summons(self, world: World) -> None:
        for parent in list(self.creatures):
            for key in parent.summons:
                spec = SPECIES[key]
                alive = sum(1 for c in self.creatures if c.spec is spec and not c.dead)
                if alive >= parent.spec.summon_max:
                    continue
                cx, cy = parent.center
                side = parent.rng.choice((-1, 1))
                x = int(cx + side * (parent.width / 2 + spec.width + 2))
                y = int(cy)
                if not world.rect_blocked(x, y, spec.width, spec.height):
                    child = Creature(spec, x, y, parent.rng)
                    child.empower(parent.power)
                    child.alerted = True
                    child.memory = MEMORY
                    child.last_seen = parent.last_seen
                    self.creatures.append(child)
            parent.summons.clear()

    def boss(self) -> Creature | None:
        for creature in self.creatures:
            if creature.spec.boss and not creature.dead:
                return creature
        return None


def spawn_boss(key: str, centre: tuple[int, int], rng: random.Random) -> Creature:
    """Create a boss centred on ``centre``."""
    spec = SPECIES[key]
    return Creature(spec, centre[0] - spec.width // 2, centre[1] - spec.height // 2, rng)


def populate(
    world: World,
    rng: random.Random,
    avoid: tuple[int, int],
    walkers: int,
    flyers: int,
    spitters: int = 0,
    bloats: int = 0,
    safe_radius: float = 170,
    extra: tuple[tuple[str, int], ...] = (),
) -> list[Creature]:
    """Place creatures in open cave space, away from ``avoid`` (the spawn).

    ``extra`` adds further species as (creature key, count).
    """
    creatures: list[Creature] = []
    wanted = (
        (MAGGOT, walkers), (SWARMER, flyers), (BONE_SPITTER, spitters), (SPORE_BLOAT, bloats),
        *((SPECIES[key], count) for key, count in extra),
    )  # fmt: skip
    for spec, count in wanted:
        placed = 0
        for _attempt in range(count * 80):
            if placed >= count:
                break
            x = rng.randint(20, world.width - 20)
            y = rng.randint(20, world.height - 20)
            if world.get(x, y) != AIR or math.hypot(x - avoid[0], y - avoid[1]) < safe_radius:
                continue
            if spec.hangs:
                while world.get(x, y - 1) == AIR and y > 3:
                    y -= 1
                if not world.rect_blocked(x, y - 1, 1, 1):  # needs a ceiling
                    continue
                top = y
            elif not spec.flying:
                while world.get(x, y + 1) == AIR and y < world.height - 3:
                    y += 1
                if not world.rect_blocked(x, y + 1, 1, 1):  # needs solid ground
                    continue
                top = y - spec.height + 1
            else:
                top = y
            left = x - spec.width // 2
            clearance = 6 if spec.flying and not spec.hangs else 0
            if world.rect_blocked(
                left - clearance, top - clearance,
                spec.width + 2 * clearance, spec.height + 2 * clearance,
            ):  # fmt: skip
                continue
            creatures.append(Creature(spec, left, top, rng))
            placed += 1
    return creatures
