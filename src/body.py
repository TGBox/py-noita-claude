"""Pixel-perfect bodies that collide with the world (player and creatures)."""

from __future__ import annotations

from src import materials as mat
from src.materials import AIR, BLOCKS_BODY, GAS, HAZARD_DPS, KEYS, KIND, LIQUID, NAME_DE
from src.world import World

UNSTICK_MAX = 24
# Material keys behind the status effects (every universe set may bring its own).
ACID_KEYS = frozenset({"acid", "fume"})
OILY_KEYS = frozenset({"tallow", "oil"})
SLIMY_KEYS = frozenset({"mucus", "kaugummi"})
AIR_STEP_UP = 2  # small ledges a body slides over even while airborne
BURN_TIME = 3.0  # seconds a body keeps burning after catching fire
BURN_DPS = 10.0
WET_TIME = 5.0  # seconds a body stays wet (and fireproof) after touching liquid
FLAME_INTERVAL = 0.08  # a burning body sheds a flame this often
IGNITE_GRACE = 0.6  # seconds after burning out before catching fire again
SLIME_FACTOR = 0.4  # mucus slows every movement to this share
SLIMED_FACTOR = 0.75  # ... and a little while after leaving it
SLIMED_TIME = 1.5
OILY_TIME = 8.0  # seconds a body stays soaked in tallow
OILY_BURN_FACTOR = 1.6  # oily bodies burn longer and harder
POISON_TIME = 6.0
POISON_DPS = 3.0
PLAYER_TEAM = "player"
ENEMY_TEAM = "enemy"


class Body:
    """Axis-aligned box in world cells; position is the top-left corner."""

    team = "neutral"  # projectiles never hit bodies of their own team
    gravity_scale = 1.0  # set for all bodies by the universe rule (rule_tiny)
    blood = "blood"  # material key a wound sprays into the world (None: nothing)
    gas_immune = False  # spores and fumes do no harm
    mucus_immune = False  # not slowed by mucus
    fire_immune = False
    acid_immune = False

    def __init__(self, x: int, y: int, width: int, height: int, hp: float) -> None:
        self.width = width
        self.height = height
        self.max_hp = hp
        self.step_up = 0
        self.place(x, y)

    @property
    def body(self) -> Body:
        """Compatibility alias so both entity.hp and entity.body.hp resolve to this Body."""
        return self

    def step_timers(self, dt: float, world: World) -> None:
        """Advance all status effect timers on this Body by dt seconds (Card A08)."""
        raise NotImplementedError("Card A08")

    def take_damage(self, amount: float, cause: str = "") -> None:
        """Apply damage taking status multipliers (e.g. stamped_bad) into account (Card A08)."""
        self.hurt(amount, cause)

    def place(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = self.max_hp
        self.damage_taken = 0.0
        self.on_ground = False
        self.burning = 0.0
        self.wet = 0.0
        self.oily = 0.0  # soaked in tallow: burns longer and hotter
        self.slimed = 0.0  # covered in mucus: still slowed for a moment
        self.poisoned = 0.0  # festering after touching pus
        self.chilled = 0.0  # slowed by cold aura/effects (Contract V4b)
        self.regen = 0.0  # healing over time timer (Contract V4b)
        self.drunk = 0.0  # wobbly movement + aim spread (Contract V4b, Card A08)
        self.sticky = 0.0  # slowed run and jump (Contract V4b, Card A08)
        self.stamped_good = 0.0  # authority pass & shop discount (Contract V4b, Card A08)
        self.stamped_bad = 0.0  # +25% incoming damage taken (Contract V4b, Card A08)
        self.marked_time = 0.0  # targeted by nearby enemies (Contract V4b, Card A08)
        self.frozen = 0.0  # immobilized (Contract V4b, Card A08)
        self.charged = 0.0  # electric discharge in liquid (Contract V4b, Card A08)
        self.befogged = 0.0  # reduced sight radius (Contract V4b, Card A08)
        self._flame_timer = 0.0
        self._ignite_grace = 0.0
        self._rx = 0.0
        self._ry = 0.0
        self.last_cause = ""

    # ----------------------------------------------------------------- state

    @property
    def dead(self) -> bool:
        return self.hp <= 0

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height

    def hurt(self, amount: float, cause: str = "") -> None:
        self.hp = max(0.0, self.hp - amount)
        self.damage_taken += amount  # read and reset by the game for damage numbers
        if amount > 0 and cause:
            self.last_cause = cause  # for the run log: what hurt (or killed) this body

    def bleed(self, world: World, x: float, y: float, amount: float, dx: float = 0.0) -> None:
        """Spray a few cells of ``blood`` from a wound at (x, y), more for bigger hits."""
        blood = mat.resolve(self.blood) if self.blood else None
        if not blood:
            return
        rng = world.rng
        for _ in range(min(12, 1 + int(amount / 3))):
            px = int(x + rng.uniform(-2, 2) + dx * rng.uniform(0, 4))
            py = int(y + rng.uniform(-3, 1))
            if world.get(px, py) == AIR:
                world.set_cell(px, py, blood)

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

    def in_mucus(self, world: World) -> bool:
        """Centre or feet stuck in mucus."""
        cx = self.x + self.width // 2
        return mat.MUCUS in (
            world.get(cx, self.y + self.height // 2),
            world.get(cx, self.y + self.height - 1),
        )

    def move(self, world: World, dt: float) -> None:
        """Move by the current velocity and update ``on_ground``."""
        factor = 1.0
        if not self.mucus_immune:
            if self.in_mucus(world):
                factor = SLIME_FACTOR
            elif self.slimed > 0:
                factor = SLIMED_FACTOR
        self._move_x(world, self.vx * dt * factor)
        self._move_y(world, self.vy * dt * factor)
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
            step = self.step_up if self.on_ground else min(self.step_up, AIR_STEP_UP)
            for up in range(1, step + 1):
                if not self.blocked(world, self.x + sign, self.y - up):
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
        """Hazard damage plus status effects: burning, wet, oily (tallow), slimed (mucus)."""
        worst, touches_fire, touches_liquid = 0.0, False, False
        worst_material = AIR
        touches_tallow = touches_mucus = touches_pus = False
        keys = KEYS  # status effects go by material key, never by a stand-in id
        for yy in range(self.y - 1, self.y + self.height + 1):
            for xx in range(self.x - 1, self.x + self.width + 1):
                material = world.get(xx, yy)
                key = keys[material]
                if key == "fire" and self.fire_immune:
                    continue
                if key in ACID_KEYS and self.acid_immune:
                    touches_liquid = touches_liquid or key == "acid"
                    continue
                if KIND[material] == GAS and self.gas_immune:
                    continue
                if HAZARD_DPS[material] > worst:
                    worst, worst_material = HAZARD_DPS[material], material
                if key == "fire":
                    touches_fire = True
                elif key in OILY_KEYS:
                    touches_tallow = True  # fat does not douse, it soaks in
                elif key in SLIMY_KEYS:
                    touches_mucus = touches_liquid = True
                elif key == "pus":
                    touches_pus = touches_liquid = True
                elif KIND[material] == LIQUID:
                    touches_liquid = True

        self._ignite_grace = max(0.0, self._ignite_grace - dt)
        if touches_tallow:
            self.oily = OILY_TIME
            self.wet = 0.0  # fat washes the water off: an oily body burns
        if touches_mucus:
            self.slimed = SLIMED_TIME
        if touches_pus and not self.acid_immune:
            self.poisoned = POISON_TIME
        if touches_liquid and not touches_tallow:
            self.wet = WET_TIME
            self.burning = 0.0
            self.oily = 0.0
        elif touches_fire and self.wet <= 0 and self.burning <= 0 and self._ignite_grace <= 0:
            self.burning = BURN_TIME * (OILY_BURN_FACTOR if self.oily > 0 else 1.0)
        self.wet = max(0.0, self.wet - dt)
        self.oily = max(0.0, self.oily - dt)
        self.slimed = max(0.0, self.slimed - dt)
        if self.poisoned > 0:
            worst_poison = POISON_DPS
            self.poisoned = max(0.0, self.poisoned - dt)
        else:
            worst_poison = 0.0

        damage = worst + worst_poison
        cause = NAME_DE[worst_material] if worst else ("Gift" if worst_poison else "")
        if self.burning > 0:
            cause = "Feuer (brennend)" if not worst else cause
            damage += BURN_DPS * (OILY_BURN_FACTOR if self.oily > 0 else 1.0)
            self.burning = max(0.0, self.burning - dt)
            if self.burning <= 0:
                self._ignite_grace = IGNITE_GRACE
            self._flame_timer -= dt
            if self._flame_timer <= 0:
                self._flame_timer = FLAME_INTERVAL
                self._shed_flame(world)
        self.hurt(damage * dt, cause)

    def _shed_flame(self, world: World) -> None:
        """Burning bodies set fire to the air just above them (and what is there)."""
        x = self.x + world.rng.randrange(self.width)
        y = self.y - 1 - world.rng.randrange(2)
        if world.get(x, y) == AIR:
            world.set_cell(x, y, mat.FIRE)

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
