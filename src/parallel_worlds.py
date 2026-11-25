"""Wobble Parallel Worlds & Toxic Bureaucracy Border Hazard (Phase L03)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from src.body import Body
from src.klonita_expansion import ParallelKlonita
from src.world import World

TOXIC_BORDER_DPS = 18.0
BORDER_ZONE_WIDTH = 24
PARALLEL_HP_MULTIPLIER = 1.5
PARALLEL_LOOT_BONUS = 1.5


@dataclass(frozen=True)
class ParallelCreatureModifier:
    """Scales creature toughness (+50% HP) and rarity for parallel-world spawns."""

    parallel_index: int
    hp_multiplier: float = PARALLEL_HP_MULTIPLIER
    loot_bonus: float = PARALLEL_LOOT_BONUS

    def apply(self, body: Body) -> Body:
        body.max_hp *= self.hp_multiplier
        body.hp = body.max_hp
        body.parallel_index = self.parallel_index  # type: ignore[attr-defined]
        return body


@dataclass(frozen=True)
class ParallelWorldState:
    """Descriptor returned when entering a West/East parallel world."""

    parallel_index: int
    seed: int
    mirrored: bool
    modifier: ParallelCreatureModifier
    parallel_klonita: ParallelKlonita


@dataclass
class ParallelWorldManager:
    """Manages toxic world-border crossing and clean buffer transitions into parallel worlds."""

    parallel_index: int = 0
    visited_indices: tuple[int, ...] = (0,)

    def check_border_hazard(self, x: float, world_width: int, dt: float, body: Body) -> float:
        """Apply toxic bureaucracy barrier damage when close to outer world edge."""
        if x < BORDER_ZONE_WIDTH or x > world_width - BORDER_ZONE_WIDTH:
            dmg = TOXIC_BORDER_DPS * dt
            body.hurt(dmg, "Toxische Bürokratie-Barriere")
            return dmg
        return 0.0

    def enter_parallel(
        self,
        base_seed: int,
        direction: int,
        world: World,
        bodies: Sequence[Body] = (),
    ) -> ParallelWorldState:
        """Transition cleanly into West (-1) or East (+1) parallel world without memory leak."""
        step = -1 if direction < 0 else 1
        self.parallel_index += step
        if self.parallel_index not in self.visited_indices:
            self.visited_indices = (*self.visited_indices, self.parallel_index)

        # Unload previous chunk buffers by cleanly resetting world storage
        world.reset()
        derived_seed = (base_seed ^ ((self.parallel_index & 0xFFFF) * 0x9E3779B1)) & 0x7FFFFFFF
        modifier = ParallelCreatureModifier(self.parallel_index)
        for body in bodies:
            modifier.apply(body)

        pk = ParallelKlonita(x=float(world.width // 2), y=float(world.height // 2))
        return ParallelWorldState(
            parallel_index=self.parallel_index,
            seed=derived_seed,
            mirrored=(self.parallel_index % 2 != 0),
            modifier=modifier,
            parallel_klonita=pk,
        )
