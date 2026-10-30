"""Player character: pixel-perfect collision against the world, levitation, hazards."""

from __future__ import annotations

from src.materials import HAZARD_DPS, KIND, LIQUID
from src.world import World

# Sizes and speeds are in world cells; one cell is one pixel at 640x360.
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 18
MAX_HP = 100.0
MAX_ENERGY = 2.0  # seconds of levitation

RUN_SPEED = 150.0  # px/s
RUN_ACCEL = 14.0  # how fast velocity follows the target speed (1/s)
GRAVITY = 1000.0  # px/s^2
JUMP_SPEED = 290.0
LEVITATE_ACCEL = 1750.0  # upward acceleration while levitating (must exceed GRAVITY)
LEVITATE_MAX_SPEED = 210.0
MAX_FALL_SPEED = 500.0
LIQUID_MAX_SPEED = 140.0
LIQUID_RUN_FACTOR = 0.6
ENERGY_RECHARGE = 1.5  # per second while standing on the ground
STEP_UP = 5  # max ledge height the player walks up automatically
UNSTICK_MAX = 24


class Player:
    """Position is the top-left corner of the body box, in world cells."""

    def __init__(self, x: int, y: int) -> None:
        self.reset(x, y)

    def reset(self, x: int, y: int) -> None:
        """Respawn at (x, y) with full health and energy."""
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = MAX_HP
        self.energy = MAX_ENERGY
        self.on_ground = False
        self.levitating = False
        self._rx = 0.0
        self._ry = 0.0

    @property
    def dead(self) -> bool:
        return self.hp <= 0

    @property
    def center(self) -> tuple[float, float]:
        return self.x + PLAYER_WIDTH / 2, self.y + PLAYER_HEIGHT / 2

    def hurt(self, amount: float) -> None:
        """Take damage (explosions, hazards)."""
        self.hp = max(0.0, self.hp - amount)

    def update(
        self,
        world: World,
        dt: float,
        move_dir: int,
        jump_pressed: bool,
        levitate_held: bool,
    ) -> None:
        """Advance the player by ``dt`` seconds. ``move_dir`` is -1, 0 or 1."""
        if self.dead:
            move_dir, jump_pressed, levitate_held = 0, False, False
        self._unstick(world)

        cx, cy = self.center
        in_liquid = KIND[world.get(int(cx), int(cy))] == LIQUID

        target = move_dir * RUN_SPEED * (LIQUID_RUN_FACTOR if in_liquid else 1.0)
        self.vx += (target - self.vx) * min(1.0, RUN_ACCEL * dt)

        self.levitating = False
        if jump_pressed and (self.on_ground or in_liquid):
            self.vy = -JUMP_SPEED * (0.6 if in_liquid and not self.on_ground else 1.0)
        elif levitate_held and not self.on_ground and self.energy > 0:
            self.levitating = True
            self.vy = max(self.vy - (LEVITATE_ACCEL - GRAVITY) * dt, -LEVITATE_MAX_SPEED)
            self.energy = max(0.0, self.energy - dt)
        else:
            self.vy = min(self.vy + GRAVITY * dt, MAX_FALL_SPEED)
        if in_liquid:
            self.vy = max(-LIQUID_MAX_SPEED, min(LIQUID_MAX_SPEED, self.vy))

        self._move_x(world, self.vx * dt)
        self._move_y(world, self.vy * dt)
        self.on_ground = world.rect_blocked(self.x, self.y + 1, PLAYER_WIDTH, PLAYER_HEIGHT)
        if self.on_ground and not self.levitating:
            self.energy = min(MAX_ENERGY, self.energy + ENERGY_RECHARGE * dt)

        self.hp = max(0.0, self.hp - self._hazard_dps(world) * dt)

    def _unstick(self, world: World) -> None:
        """Push the player out of material that landed on top of them."""
        if not world.rect_blocked(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT):
            return
        for up in range(1, UNSTICK_MAX + 1):
            if not world.rect_blocked(self.x, self.y - up, PLAYER_WIDTH, PLAYER_HEIGHT):
                self.y -= up
                return

    def _move_x(self, world: World, delta: float) -> None:
        self._rx += delta
        steps = int(self._rx)
        self._rx -= steps
        sign = 1 if steps > 0 else -1
        for _ in range(abs(steps)):
            if not world.rect_blocked(self.x + sign, self.y, PLAYER_WIDTH, PLAYER_HEIGHT):
                self.x += sign
                continue
            for up in range(1, STEP_UP + 1):
                if self.on_ground and not world.rect_blocked(
                    self.x + sign, self.y - up, PLAYER_WIDTH, PLAYER_HEIGHT
                ):
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
            if world.rect_blocked(self.x, self.y + sign, PLAYER_WIDTH, PLAYER_HEIGHT):
                self.vy = 0.0
                self._ry = 0.0
                break
            self.y += sign

    def _hazard_dps(self, world: World) -> float:
        """Strongest damage source touching the body (fire, lava)."""
        worst = 0.0
        for yy in range(self.y - 1, self.y + PLAYER_HEIGHT + 1):
            for xx in range(self.x - 1, self.x + PLAYER_WIDTH + 1):
                worst = max(worst, HAZARD_DPS[world.get(xx, yy)])
        return worst
