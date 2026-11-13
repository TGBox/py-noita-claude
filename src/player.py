"""Player character: Noita-like walking, hopping and levitation."""

from __future__ import annotations

from src import materials as mat
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
POLYMORPH_SPEED = 0.6  # movement while turned into a maggot
LEVITATE_RUN_SPEED = 52.0 * SCREEN_SCALE  # horizontal speed while levitating
RUN_RESPONSE = 9.75  # 1/s, how fast horizontal speed follows the input
GRAVITY = 350.0 * SCREEN_SCALE  # px/s^2
JUMP_SPEED = 95.0 * SCREEN_SCALE
LEVITATE_MAX_SPEED = 84.0 * SCREEN_SCALE  # a little weaker than Noita's 95
LEVITATE_RESPONSE = 14.0  # 1/s, how fast vertical speed approaches the levitation speed
MAX_FALL_SPEED = 350.0 * SCREEN_SCALE
LIQUID_MAX_SPEED = 60.0 * SCREEN_SCALE
LIQUID_RUN_FACTOR = 0.6
ENERGY_RECHARGE = 6.0  # per second on the ground
ENERGY_RECHARGE_AIR = 0.4  # per second in the air while not levitating
STEP_UP = 6  # max ledge height the player walks up automatically
STICKY_JUMP = 0.65  # jump speed while "klebrig" (chewing gum)
FIZZY_JUMP = 1.5  # jump speed while "sprudelnd" (Brausesirup)
# Jelly is a trampoline (Glibbria), mushroom caps bounce a little (Sporenklub). Landing
# faster than BOUNCE_MIN_SPEED (a fall of about 30 cells; an ordinary hop lands softer)
# throws the body back up with this share of the landing speed.
SLIPPERY_MATERIALS = {"goldboden": 3.0}  # braking distance factor on the ground
BOUNCE_MATERIALS = {"glibber": 0.8, "glibber_rot": 0.8, "pilzhut": 0.5}
BOUNCE_MIN_SPEED = 180.0
BOUNCE_BOOST = 0.35  # extra share with jump pressed shortly before landing
BOUNCE_BUFFER = 0.25  # seconds a jump press counts for the boost
BOUNCE_MAX_SPEED = 1.1 * MAX_FALL_SPEED


class Player(Body):
    """The player: levitation energy on top of the shared body physics."""

    team = PLAYER_TEAM

    def __init__(self, x: float, y: float) -> None:
        self.energy_max = MAX_ENERGY
        self.mana: float = 100.0
        self.max_mana: float = 100.0
        super().__init__(int(x), int(y), PLAYER_WIDTH, PLAYER_HEIGHT, MAX_HP)
        self.step_up = STEP_UP
        self._bounce_buffer = 0.0  # seconds left in which a jump press boosts a bounce

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, val: float) -> None:
        self._x = int(val)

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, val: float) -> None:
        self._y = int(val)

    def _bounce_share(self, world: World) -> float:
        """How bouncy the ground right under the feet is (0 = not at all)."""
        row = self.y + self.height
        keys = {mat.KEYS[world.get(x, row)] for x in range(self.x, self.x + self.width)}
        return max((BOUNCE_MATERIALS.get(key, 0.0) for key in keys), default=0.0)

    def _slip_share(self, world: World) -> float:
        """How slippery the ground under the feet is (1 = normal grip)."""
        row = self.y + self.height
        keys = {mat.KEYS[world.get(x, row)] for x in range(self.x, self.x + self.width)}
        return max((SLIPPERY_MATERIALS.get(key, 1.0) for key in keys), default=1.0)

    def place(self, x: int, y: int) -> None:
        super().place(x, y)
        self.energy = self.energy_max
        self.levitating = False

    def reset(self, x: int, y: int) -> None:
        """Respawn at (x, y) with full health and energy."""
        self.place(x, y)

    polymorphed = 0.0  # seconds left as a maggot (no casting, no flask)
    air_recharge = ENERGY_RECHARGE_AIR  # per second in the air (the "dauerflug" perk raises it)

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
        self._bounce_buffer = BOUNCE_BUFFER if jump_pressed else self._bounce_buffer - dt

        self.levitating = False
        if jump_pressed and (self.on_ground or in_liquid):
            self.vy = -JUMP_SPEED * (0.6 if in_liquid and not self.on_ground else 1.0)
            # status effects change the jump itself (once), not the speed in every frame
            if self.sticky > 0:
                self.vy *= STICKY_JUMP
            if self.fizzy_time > 0:
                self.vy *= FIZZY_JUMP
        elif levitate_held and not self.on_ground and self.energy > 0:
            self.levitating = True
            follow = min(1.0, LEVITATE_RESPONSE * dt)
            self.vy += (-LEVITATE_MAX_SPEED - self.vy) * follow
            self.energy = max(0.0, self.energy - dt)
        else:
            # Apply frozen effect to fall speed
            fall_speed = MAX_FALL_SPEED
            if self.frozen > 0:
                fall_speed *= 0.3
            self.vy = min(self.vy + GRAVITY * self.gravity_scale * dt, fall_speed)
        if in_liquid:
            self.vy = max(-LIQUID_MAX_SPEED, min(LIQUID_MAX_SPEED, self.vy))

        speed = LEVITATE_RUN_SPEED if self.levitating else RUN_SPEED
        speed *= getattr(self, "speed_scale", 1.0)
        # Apply haste_time effect to run speed
        if self.haste_time > 0:
            speed *= 1.3
        # Apply sticky effect to run speed
        if self.sticky > 0:
            speed *= 0.55
        if self.polymorphed > 0:  # a maggot crawls
            speed *= POLYMORPH_SPEED
            self.polymorphed = max(0.0, self.polymorphed - dt)

        target = move_dir * speed * (LIQUID_RUN_FACTOR if in_liquid else 1.0)
        # Apply drunk effect to movement
        if self.drunk > 0:
            # Add slight wobble to movement direction
            import random

            target += random.uniform(-0.5, 0.5) * speed

        response = RUN_RESPONSE
        if self.on_ground:  # polished gold: the feet find three times less grip (V17 §2)
            response /= self._slip_share(world)
        self.vx += (target - self.vx) * min(1.0, response * dt)

        impact = self.vy
        self.move(world, dt)
        if self.on_ground and impact > BOUNCE_MIN_SPEED and not in_liquid and not self.dead:
            keep = self._bounce_share(world)
            if keep:
                keep += BOUNCE_BOOST if self._bounce_buffer > 0 else 0.0
                self.vy = -min(impact * keep, BOUNCE_MAX_SPEED)
                self.on_ground = False
        if self.on_ground and not self.levitating:
            self.energy = min(self.energy_max, self.energy + ENERGY_RECHARGE * dt)
        elif not levitate_held:
            self.energy = min(self.energy_max, self.energy + self.air_recharge * dt)

        self.apply_environment(world, dt)
