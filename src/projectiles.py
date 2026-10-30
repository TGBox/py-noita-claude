"""Projectiles built from wand shots: flight, collisions and end-of-flight effects."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from src.body import PLAYER_TEAM, Body
from src.materials import KIND, LIQUID, STOPS_PROJECTILE
from src.spells import TIMER_DELAY, Block, Category, Trigger
from src.wand import Shot
from src.world import World

MAX_PROJECTILES = 256
HOMING_TURN_RATE = 7.0  # radians per second
FLIPPED_GRAVITY = 300.0  # px/s^2 for forms that normally fly straight
BOUNCE_DAMPING = 0.55


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
    age: float = 0.0
    alive: bool = True
    released: bool = False


def build(
    shot: Shot, x: float, y: float, angle: float, team: str = PLAYER_TEAM
) -> Projectile:
    """Apply a shot's modifiers to its form and launch it."""
    form = shot.form
    speed, gravity, blast = form.speed, form.gravity, form.blast
    material, homing, trigger = form.default_material, False, None
    for block in shot.modifiers:
        speed *= block.speed_factor
        blast += block.blast_bonus
        if block.flip_gravity:
            gravity = -(gravity or FLIPPED_GRAVITY)
        homing = homing or block.homing
        if block.category is Category.TRIGGER:
            trigger = block.trigger
        if block.material is not None:
            material = block.material
    angle += shot.angle_offset
    return Projectile(
        form=form,
        x=x,
        y=y,
        vx=math.cos(angle) * speed,
        vy=math.sin(angle) * speed,
        gravity=gravity,
        lifetime=form.lifetime,
        blast=blast,
        splash=form.splash,
        material=material,
        bounces=form.bounces,
        homing=homing,
        trigger=trigger,
        damage=form.damage,
        team=team,
        children=list(shot.children),
    )


class ProjectileSystem:
    """Owns all live projectiles and resolves their effects on the world."""

    def __init__(self) -> None:
        self.items: list[Projectile] = []
        self._pending: list[Projectile] = []
        self._blasts: list[Blast] = []

    def clear(self) -> None:
        self.items.clear()

    def spawn(
        self, shots: list[Shot], x: float, y: float, angle: float, team: str = PLAYER_TEAM
    ) -> None:
        for shot in shots:
            if len(self.items) + len(self._pending) >= MAX_PROJECTILES:
                return
            self._pending.append(build(shot, x, y, angle, team))

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
        if p.trigger is Trigger.TIMER and not p.released and p.age >= TIMER_DELAY:
            self._release(p)

        dx, dy = p.vx * dt, p.vy * dt
        steps = int(math.hypot(dx, dy)) + 1
        for _ in range(steps):
            nx, ny = p.x + dx / steps, p.y + dy / steps
            if p.form.bounces == 0:
                victim = _body_at(bodies, p.team, nx, ny)
                if victim is not None:
                    victim.hurt(p.damage)
                    p.x, p.y = nx, ny
                    self._end(p, world, hit=True, wet=False)
                    return
            cell = world.get(int(nx), int(ny))
            if not STOPS_PROJECTILE[cell]:
                p.x, p.y = nx, ny
                continue
            if p.form.bounces > 0:  # bouncers never end on impact, only on their fuse
                self._bounce(p, world, nx, ny)
                return
            self._end(p, world, hit=True, wet=KIND[cell] == LIQUID)
            return

    def _bounce(self, p: Projectile, world: World, nx: float, ny: float) -> None:
        if p.trigger is Trigger.IMPACT and not p.released:
            self._release(p)
        if p.bounces <= 0:  # out of bounces: come to rest until the fuse runs out
            p.vx = p.vy = 0.0
            return
        p.bounces -= 1
        blocked_x = STOPS_PROJECTILE[world.get(int(nx), int(p.y))]
        blocked_y = STOPS_PROJECTILE[world.get(int(p.x), int(ny))]
        if blocked_x or not blocked_y:
            p.vx = -p.vx * BOUNCE_DAMPING
        if blocked_y or not blocked_x:
            p.vy = -p.vy * BOUNCE_DAMPING

    # ---------------------------------------------------------------- effects

    def _end(self, p: Projectile, world: World, *, hit: bool, wet: bool) -> None:
        p.alive = False
        x, y = int(p.x), int(p.y)
        # Projectiles explode on impact; fused bouncers also when their time runs out.
        if p.blast > 0 and (hit or p.form.bounces > 0):
            world.explode(x, y, p.blast)
            self._blasts.append(Blast(x, y, p.blast))
        if p.material is not None and p.splash > 0:
            world.splash(x, y, p.splash, p.material)
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


def _body_at(bodies: Sequence[Body], team: str, x: float, y: float) -> Body | None:
    for body in bodies:
        if body.team != team and not body.dead and body.contains(x, y):
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
