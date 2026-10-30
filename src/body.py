"""Pixel-perfect bodies that collide with the world (player and creatures)."""

from __future__ import annotations

from src.materials import ACID, AIR, BLOCKS_BODY, FIRE, FUME, HAZARD_DPS, KIND, LIQUID
from src.world import World

UNSTICK_MAX = 24
BURN_TIME = 3.0  # seconds a body keeps burning after catching fire
BURN_DPS = 10.0
WET_TIME = 5.0  # seconds a body stays wet (and fireproof) after touching liquid
FLAME_INTERVAL = 0.08  # a burning body sheds a flame this often
IGNITE_GRACE = 0.6  # seconds after burning out before catching fire again
PLAYER_TEAM = "player"
ENEMY_TEAM = "enemy"


class Body:
    """Axis-aligned box in world cells; position is the top-left corner."""

    team = "neutral"  # projectiles never hit bodies of their own team
    fire_immune = False
    acid_immune = False

    def __init__(self, x: int, y: int, width: int, height: int, hp: float) -> None:
        self.width = width
        self.height = height
        self.max_hp = hp
        self.step_up = 0
        self.place(x, y)

    def place(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = self.max_hp
        self.on_ground = False
        self.burning = 0.0
        self.wet = 0.0
        self._flame_timer = 0.0
        self._ignite_grace = 0.0
        self._rx = 0.0
        self._ry = 0.0

    # ----------------------------------------------------------------- state

    @property
    def dead(self) -> bool:
        return self.hp <= 0

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height

    def hurt(self, amount: float) -> None:
        self.hp = max(0.0, self.hp - amount)

    def in_liquid(self, world: World) -> bool:
        cx, cy = self.center
        return KIND[world.get(int(cx), int(cy))] == LIQUID

    # --------------------------------------------------------------- physics

    def blocked(self, world: World, x: int, y: int) -> bool:
        return world.rect_blocked(x, y, self.width, self.height)

    def unstick(self, world: World) -> None:
        """Push the body out of material that landed on top of it."""
        if not self.blocked(world, self.x, self.y):
            return
        for up in range(1, UNSTICK_MAX + 1):
            if not self.blocked(world, self.x, self.y - up):
                self.y -= up
                return

    def move(self, world: World, dt: float) -> None:
        """Move by the current velocity and update ``on_ground``."""
        self._move_x(world, self.vx * dt)
        self._move_y(world, self.vy * dt)
        self.on_ground = self.blocked(world, self.x, self.y + 1)

    def _move_x(self, world: World, delta: float) -> None:
        self._rx += delta
        steps = int(self._rx)
        self._rx -= steps
        sign = 1 if steps > 0 else -1
        for _ in range(abs(steps)):
            if not self.blocked(world, self.x + sign, self.y):
                self.x += sign
                continue
            for up in range(1, self.step_up + 1):
                if self.on_ground and not self.blocked(world, self.x + sign, self.y - up):
                    self.x += sign
                    self.y -= up
                    break
            else:
                self.vx = 0.0
                self._rx = 0.0
                break

    def _move_y(self, world: World, delta: float) -> None:
        self._ry += delta
        steps = int(self._ry)
        self._ry -= steps
        sign = 1 if steps > 0 else -1
        for _ in range(abs(steps)):
            if self.blocked(world, self.x, self.y + sign):
                self.vy = 0.0
                self._ry = 0.0
                break
            self.y += sign

    def apply_environment(self, world: World, dt: float) -> None:
        """Hazard damage plus status effects: catching fire, burning, getting wet."""
        worst, touches_fire, touches_liquid = 0.0, False, False
        for yy in range(self.y - 1, self.y + self.height + 1):
            for xx in range(self.x - 1, self.x + self.width + 1):
                material = world.get(xx, yy)
                if material == FIRE and self.fire_immune:
                    continue
                if material in (ACID, FUME) and self.acid_immune:
                    touches_liquid = True
                    continue
                worst = max(worst, HAZARD_DPS[material])
                if material == FIRE:
                    touches_fire = True
                elif KIND[material] == LIQUID:
                    touches_liquid = True

        self._ignite_grace = max(0.0, self._ignite_grace - dt)
        if touches_liquid:
            self.wet = WET_TIME
            self.burning = 0.0
        elif touches_fire and self.wet <= 0 and self.burning <= 0 and self._ignite_grace <= 0:
            self.burning = BURN_TIME
        self.wet = max(0.0, self.wet - dt)

        damage = worst
        if self.burning > 0:
            damage += BURN_DPS
            self.burning = max(0.0, self.burning - dt)
            if self.burning <= 0:
                self._ignite_grace = IGNITE_GRACE
            self._flame_timer -= dt
            if self._flame_timer <= 0:
                self._flame_timer = FLAME_INTERVAL
                self._shed_flame(world)
        self.hurt(damage * dt)

    def _shed_flame(self, world: World) -> None:
        """Burning bodies set fire to the air just above them (and what is there)."""
        x = self.x + world.rng.randrange(self.width)
        y = self.y - 1 - world.rng.randrange(2)
        if world.get(x, y) == AIR:
            world.set_cell(x, y, FIRE)

    def hazard_dps(self, world: World) -> float:
        """Strongest damage source touching the body (fire, acid, ...)."""
        worst = 0.0
        for yy in range(self.y - 1, self.y + self.height + 1):
            for xx in range(self.x - 1, self.x + self.width + 1):
                worst = max(worst, HAZARD_DPS[world.get(xx, yy)])
        return worst

    def can_see(self, world: World, tx: float, ty: float, max_distance: float) -> bool:
        """Line of sight from the body's centre to (tx, ty) through non-blocking cells."""
        cx, cy = self.center
        dx, dy = tx - cx, ty - cy
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > max_distance:
            return False
        steps = int(distance / 2) + 1
        for i in range(1, steps):
            t = i / steps
            if BLOCKS_BODY[world.get(int(cx + dx * t), int(cy + dy * t))]:
                return False
        return True
