"""Projectiles built from wand shots: flight, collisions and end-of-flight effects."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from src import materials as mat
from src.body import BURN_TIME, PLAYER_TEAM, Body
from src.materials import AIR, KIND, LIQUID, STOPS_PROJECTILE
from src.spells import TIMER_DELAY, Block, Category, Trigger
from src.wand import Shot
from src.world import World

MAX_PROJECTILES = 256
HOMING_TURN_RATE = 7.0  # radians per second
FLIPPED_GRAVITY = 300.0  # px/s^2 for forms that normally fly straight
BOUNCE_DAMPING = 0.55
WALL_BOUNCE_DAMPING = 0.85  # bounces from the "Abprall" modifier keep more speed
PELLET_SPREAD = 0.22  # radians
CHAIN_RANGE = 90.0  # px a chain spark can leap
MINE_ARM_TIME = 0.8  # seconds before a mine reacts
MINE_RANGE = 16.0  # px
LIQUID_DRAG = 0.97  # speed kept per cell flown through liquid (projectiles pass through pools)



@dataclass(frozen=True)
class Blast:
    """An explosion that happened this frame (for camera shake and damage)."""

    x: int
    y: int
    radius: int


@dataclass
class Projectile:
    form: Block
    x: float
    y: float
    vx: float
    vy: float
    gravity: float
    lifetime: float
    blast: int
    splash: int
    material: int | None
    bounces: int
    homing: bool
    trigger: Trigger | None
    damage: float = 0.0
    team: str = PLAYER_TEAM
    children: list[Shot] = field(default_factory=list)
    pierce: bool = False
    ignites: bool = False
    digs: int = 0
    lifesteal: float = 0.0
    trail: int | None = None
    teleport: bool = False
    mine: bool = False
    shock: int = 0
    chain: int = 0
    timer: float = TIMER_DELAY  # when a Zeit-Nerv releases its payload
    age: float = 0.0
    alive: bool = True
    released: bool = False
    hit_ids: set[int] = field(default_factory=set)
    wet: bool = False  # flew through liquid (Nässe-Nerv)

    @property
    def fused(self) -> bool:
        """Fused forms (bombs) rest after bouncing and only end when their time is up."""
        return self.form.bounces > 0


def build(
    shot: Shot, x: float, y: float, angle: float, team: str = PLAYER_TEAM
) -> Projectile:
    """Apply a shot's modifiers to its form and launch it."""
    form = shot.form
    speed, gravity, blast = form.speed, form.gravity, form.blast
    material, homing, trigger = mat.opt_id(form.default_material), form.homing, None
    timer = 0.0
    lifetime, bounces = form.lifetime, form.bounces + form.ricochet
    pierce, ignites = form.pierce, False
    damage, trail = form.damage, None
    for block in shot.modifiers:
        gravity *= block.gravity_factor
        damage += block.damage_bonus
        if block.trail is not None:
            trail = mat.id_of(block.trail)
        speed *= block.speed_factor
        blast += block.blast_bonus
        lifetime *= block.lifetime_factor
        bounces += block.bounce_bonus
        pierce = pierce or block.pierce
        ignites = ignites or block.ignites
        if block.flip_gravity:
            gravity = -(gravity or FLIPPED_GRAVITY)
        homing = homing or block.homing
        if block.category is Category.TRIGGER:
            trigger = block.trigger
            timer = block.timer
        if block.material is not None:
            material = mat.id_of(block.material)
    angle += shot.angle_offset
    return Projectile(
        form=form,
        x=x,
        y=y,
        vx=math.cos(angle) * speed,
        vy=math.sin(angle) * speed,
        gravity=gravity,
        lifetime=lifetime,
        blast=blast,
        splash=form.splash,
        material=material,
        bounces=bounces,
        homing=homing,
        trigger=trigger,
        damage=damage,
        team=team,
        children=list(shot.children),
        pierce=pierce,
        ignites=ignites,
        digs=form.digs,
        lifesteal=form.lifesteal,
        trail=trail,
        teleport=form.teleport,
        mine=form.mine,
        shock=form.shock,
        chain=form.chain,
        timer=timer or TIMER_DELAY,
    )


class ProjectileSystem:
    """Owns all live projectiles and resolves their effects on the world."""

    def __init__(self) -> None:
        self.items: list[Projectile] = []
        self._pending: list[Projectile] = []
        self._blasts: list[Blast] = []
        self._rng = random.Random()
        self.healing = 0.0  # life stolen for the player since the last ``take_healing``
        self.teleports: list[tuple[float, float]] = []  # where player teleport bolts ended
        self.player_damage = 1.0  # factor on the player's projectile damage (perks)
        self.enemy_damage = 1.0  # factor on creatures' projectile damage (New Game+)
        # universe rule: gravity factor and extra bounces per team
        self.gravity_scale = 1.0
        self.bounce_bonus: dict[str, int] = {}
        self.polymorphs: list[Body] = []  # creatures hit by a polymorph bolt (run replaces them)
        self.swaps: list[Body] = []  # creatures the player swaps places with

    def clear(self) -> None:
        self.items.clear()

    def spawn(
        self,
        shots: list[Shot],
        x: float,
        y: float,
        angle: float,
        team: str = PLAYER_TEAM,
        damage_factor: float = 1.0,
    ) -> None:
        for shot in shots:
            pellets = max(1, shot.form.pellets)
            for _ in range(pellets):
                if len(self.items) + len(self._pending) >= MAX_PROJECTILES:
                    return
                spread = self._rng.uniform(-PELLET_SPREAD, PELLET_SPREAD) if pellets > 1 else 0.0
                extra = sum(m.spread_bonus for m in shot.modifiers)
                if extra:
                    spread += self._rng.uniform(-extra, extra)
                projectile = build(shot, x, y, angle + spread, team)
                projectile.gravity *= self.gravity_scale
                projectile.bounces += self.bounce_bonus.get(team, 0)
                projectile.damage *= damage_factor
                if pellets > 1:
                    factor = self._rng.uniform(0.8, 1.1)
                    projectile.vx *= factor
                    projectile.vy *= factor
                self._pending.append(projectile)

    def take_healing(self) -> float:
        """Life stolen by the player's projectiles since the last call."""
        amount, self.healing = self.healing, 0.0
        return amount

    def update(
        self,
        world: World,
        dt: float,
        target: tuple[float, float],
        bodies: Sequence[Body] = (),
    ) -> list[Blast]:
        """Advance every projectile; returns the explosions of this update.

        Projectiles hit ``bodies`` of other teams and deal their direct damage.
        """
        self._blasts = []
        self.items.extend(self._pending)
        self._pending = []
        for projectile in self.items:
            self._update_one(projectile, world, dt, target, bodies)
        self.items = [p for p in self.items if p.alive]
        return self._blasts

    # ----------------------------------------------------------------- flight

    def _update_one(
        self,
        p: Projectile,
        world: World,
        dt: float,
        target: tuple[float, float],
        bodies: Sequence[Body],
    ) -> None:
        p.age += dt
        if p.age >= p.lifetime:
            self._end(p, world, hit=False, wet=False)
            return
        if p.homing:
            _steer(p, target, dt)
        p.vy += p.gravity * dt
        if p.trigger is Trigger.TIMER and not p.released and p.age >= p.timer:
            self._release(p)
        if p.mine and p.age > MINE_ARM_TIME and _body_near(bodies, p.team, p.x, p.y, MINE_RANGE):
            self._end(p, world, hit=True, wet=False)
            return

        dx, dy = p.vx * dt, p.vy * dt
        steps = int(math.hypot(dx, dy)) + 1
        for _ in range(steps):
            nx, ny = p.x + dx / steps, p.y + dy / steps
            if not p.fused:
                victim = _body_at(bodies, p.team, nx, ny, p.hit_ids)
                if victim is not None:
                    self._hit_body(p, victim, world, bodies)
                    if not p.pierce:
                        p.x, p.y = nx, ny
                        self._end(p, world, hit=True, wet=False)
                        return
            cell = world.get(int(nx), int(ny))
            if KIND[cell] == LIQUID:  # like in Noita, shots dive through pools, slowed down
                if not p.wet:
                    p.wet = True
                    if p.trigger is Trigger.WET and not p.released:
                        self._release(p)
                p.vx *= LIQUID_DRAG
                p.vy *= LIQUID_DRAG
                p.x, p.y = nx, ny
                if math.hypot(p.vx, p.vy) < 25:  # stuck in the pool: end down there
                    self._end(p, world, hit=True, wet=True)
                    return
                continue
            if not STOPS_PROJECTILE[cell]:
                if p.trail is not None and cell == AIR and (int(nx), int(ny)) != (int(p.x), int(p.y)):
                    world.set_cell(int(p.x), int(p.y), p.trail)  # behind the projectile
                p.x, p.y = nx, ny
                continue
            if p.digs and world.diggable(cell, p.digs):
                world.dig(int(nx), int(ny), p.digs)
                p.x, p.y = nx, ny
                continue
            if p.fused or p.bounces > 0:
                self._bounce(p, world, nx, ny)
                return
            self._end(p, world, hit=True, wet=KIND[cell] == LIQUID)
            return

    def _chain(self, p: Projectile, victim: Body, bodies: Sequence[Body]) -> None:
        """Leap from ``victim`` to the nearest other creature in reach."""
        vx, vy = victim.center
        best, best_distance = None, CHAIN_RANGE
        for body in bodies:
            if body is victim or body.team == p.team or body.dead or id(body) in p.hit_ids:
                continue
            distance = math.hypot(body.center[0] - vx, body.center[1] - vy)
            if distance < best_distance:
                best, best_distance = body, distance
        if best is None:
            return
        angle = math.atan2(best.center[1] - vy, best.center[0] - vx)
        speed = math.hypot(p.vx, p.vy)
        leap = replace(
            p, x=vx + math.cos(angle) * (victim.width / 2 + 2), y=vy + math.sin(angle) * (victim.height / 2 + 2),
            vx=math.cos(angle) * speed, vy=math.sin(angle) * speed, chain=p.chain - 1, age=0.0,
            hit_ids=set(p.hit_ids), children=[],
        )  # fmt: skip
        self._pending.append(leap)

    def _hit_body(self, p: Projectile, victim: Body, world: World, bodies: Sequence[Body] = ()) -> None:
        p.hit_ids.add(id(victim))
        damage = p.damage * (self.player_damage if p.team == PLAYER_TEAM else self.enemy_damage)
        owner = "Eigener Zauber" if p.team == PLAYER_TEAM else "Geschoss"
        victim.hurt(damage, f"{owner}: {p.form.name_de}")
        speed = math.hypot(p.vx, p.vy) or 1.0
        victim.bleed(world, p.x, p.y, p.damage, p.vx / speed)
        if p.form.polymorph:
            self.polymorphs.append(victim)
        if p.form.swap and p.team == PLAYER_TEAM:
            self.swaps.append(victim)
        if p.chain > 0:
            self._chain(p, victim, bodies)
        if p.ignites and victim.wet <= 0 and not victim.fire_immune:
            victim.burning = BURN_TIME
        if p.lifesteal and p.team == PLAYER_TEAM:
            self.healing += damage * p.lifesteal

    def _bounce(self, p: Projectile, world: World, nx: float, ny: float) -> None:
        if p.trigger is Trigger.IMPACT and not p.released:
            self._release(p)
        if p.bounces <= 0:  # out of bounces: come to rest until the fuse runs out
            p.vx = p.vy = 0.0
            return
        p.bounces -= 1
        damping = BOUNCE_DAMPING if p.fused else WALL_BOUNCE_DAMPING
        blocked_x = STOPS_PROJECTILE[world.get(int(nx), int(p.y))]
        blocked_y = STOPS_PROJECTILE[world.get(int(p.x), int(ny))]
        if blocked_x or not blocked_y:
            p.vx = -p.vx * damping
        if blocked_y or not blocked_x:
            p.vy = -p.vy * damping

    # ---------------------------------------------------------------- effects

    def _end(self, p: Projectile, world: World, *, hit: bool, wet: bool) -> None:
        p.alive = False
        x, y = int(p.x), int(p.y)
        if p.teleport and p.team == PLAYER_TEAM:
            # step back along the flight so the caster lands in the open, not in the wall
            speed = math.hypot(p.vx, p.vy) or 1.0
            self.teleports.append((p.x - p.vx / speed * 6, p.y - p.vy / speed * 6))
        # Projectiles explode on impact; fused bouncers also when their time runs out.
        if p.blast > 0 and (hit or p.fused):
            world.explode(x, y, p.blast)
            self._blasts.append(Blast(x, y, p.blast))
        if p.material is not None and p.splash > 0:
            world.splash(x, y, p.splash, p.material)
        if p.shock:
            world.electrify(x, y, p.shock)
        if p.released or p.trigger is None:
            return
        if (
            p.trigger in (Trigger.END, Trigger.TIMER)
            or (p.trigger is Trigger.IMPACT and hit)
            or (p.trigger is Trigger.WET and wet)
        ):
            self._release(p)

    def _release(self, p: Projectile) -> None:
        """Cast the payload group from the projectile's position and heading."""
        p.released = True
        angle = math.atan2(p.vy, p.vx)
        self.spawn(p.children, p.x, p.y, angle, p.team)


def _body_near(bodies: Sequence[Body], team: str, x: float, y: float, radius: float) -> bool:
    for body in bodies:
        if body.team != team and not body.dead:
            cx, cy = body.center
            if math.hypot(cx - x, cy - y) <= radius + max(body.width, body.height) / 2:
                return True
    return False


def _body_at(
    bodies: Sequence[Body], team: str, x: float, y: float, skip: set[int]
) -> Body | None:
    for body in bodies:
        if body.team != team and not body.dead and id(body) not in skip and body.contains(x, y):
            return body
    return None


def _steer(p: Projectile, target: tuple[float, float], dt: float) -> None:
    speed = math.hypot(p.vx, p.vy)
    if speed < 1e-6:
        return
    current = math.atan2(p.vy, p.vx)
    wanted = math.atan2(target[1] - p.y, target[0] - p.x)
    diff = (wanted - current + math.pi) % (2 * math.pi) - math.pi
    turn = max(-HOMING_TURN_RATE * dt, min(HOMING_TURN_RATE * dt, diff))
    p.vx = math.cos(current + turn) * speed
    p.vy = math.sin(current + turn) * speed
