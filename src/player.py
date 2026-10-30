"""Player character: Noita-like walking, hopping and levitation."""

from __future__ import annotations

from src.body import PLAYER_TEAM, Body
from src.world import World

# Sizes and speeds are in world cells; one cell is one pixel at 640x360.
# Movement is tuned to Noita's feel, scaled by 1.5 because our view shows 1.5x as
# many pixels: walking is slow, jumping is a small hop and levitation is the main
# way to move, with a quick refill on the ground.
SCREEN_SCALE = 1.5
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 18
MAX_HP = 100.0
MAX_ENERGY = 3.0  # seconds of levitation

RUN_SPEED = 57.0 * SCREEN_SCALE  # px/s
LEVITATE_RUN_SPEED = 52.0 * SCREEN_SCALE  # horizontal speed while levitating
RUN_RESPONSE = 9.75  # 1/s, how fast horizontal speed follows the input
GRAVITY = 350.0 * SCREEN_SCALE  # px/s^2
JUMP_SPEED = 95.0 * SCREEN_SCALE
LEVITATE_MAX_SPEED = 95.0 * SCREEN_SCALE
LEVITATE_RESPONSE = 17.3  # 1/s, how fast vertical speed approaches the levitation speed
MAX_FALL_SPEED = 350.0 * SCREEN_SCALE
LIQUID_MAX_SPEED = 60.0 * SCREEN_SCALE
LIQUID_RUN_FACTOR = 0.6
ENERGY_RECHARGE = 6.0  # per second on the ground
ENERGY_RECHARGE_AIR = 0.4  # per second in the air while not levitating
STEP_UP = 6  # max ledge height the player walks up automatically


class Player(Body):
    """The player: levitation energy on top of the shared body physics."""

    team = PLAYER_TEAM

    def __init__(self, x: int, y: int) -> None:
        self.energy_max = MAX_ENERGY
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, MAX_HP)
        self.step_up = STEP_UP

    def place(self, x: int, y: int) -> None:
        super().place(x, y)
        self.energy = self.energy_max
        self.levitating = False

    def reset(self, x: int, y: int) -> None:
        """Respawn at (x, y) with full health and energy."""
        self.place(x, y)

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
        self.unstick(world)
        in_liquid = self.in_liquid(world)

        self.levitating = False
        if jump_pressed and (self.on_ground or in_liquid):
            self.vy = -JUMP_SPEED * (0.6 if in_liquid and not self.on_ground else 1.0)
        elif levitate_held and not self.on_ground and self.energy > 0:
            self.levitating = True
            follow = min(1.0, LEVITATE_RESPONSE * dt)
            self.vy += (-LEVITATE_MAX_SPEED - self.vy) * follow
            self.energy = max(0.0, self.energy - dt)
        else:
            self.vy = min(self.vy + GRAVITY * dt, MAX_FALL_SPEED)
        if in_liquid:
            self.vy = max(-LIQUID_MAX_SPEED, min(LIQUID_MAX_SPEED, self.vy))

        speed = LEVITATE_RUN_SPEED if self.levitating else RUN_SPEED
        target = move_dir * speed * (LIQUID_RUN_FACTOR if in_liquid else 1.0)
        self.vx += (target - self.vx) * min(1.0, RUN_RESPONSE * dt)

        self.move(world, dt)
        if self.on_ground and not self.levitating:
            self.energy = min(self.energy_max, self.energy + ENERGY_RECHARGE * dt)
        elif not levitate_held:
            self.energy = min(self.energy_max, self.energy + ENERGY_RECHARGE_AIR * dt)

        self.apply_environment(world, dt)
