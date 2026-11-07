"""Contract V20: the fabricator builds modules from blueprints (Card E06)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.economy import fabricator_gold
from src.samples import SAMPLES
from src.spells import BLOCKS, Category

if TYPE_CHECKING:
    from .run import Run

MAX_BUILDS_PER_VISIT: int = 3
TIER2_SAMPLES: tuple[str, ...] = ("probe_knochen", "probe_aether", "probe_schatten")
TIER3_SAMPLES: tuple[str, ...] = ("probe_gold", "probe_kern")


@dataclass(frozen=True)
class Recipe:
    block_key: str
    rarity_tier: int
    universe_samples: int
    universe: str | None
    special_samples: tuple[str, ...]
    blueprint_shards: int
    gold: int


def _universe_for_material(material: str | None) -> str | None:
    if not material:
        return None
    from src import materials as mat

    base = set(mat.BASE_KEYS)
    if material in base:
        return None
    for u_key, s in mat.SETS.items():
        if u_key != "koerper" and material in s.materials:
            return u_key
    return None


def build_cost(block_key: str, stage: int = 1) -> Recipe:
    block = BLOCKS[block_key]
    tier = block.rarity_tier

    # Category sample requirements:
    # Trigger: 2, others: 1
    u_samples = 2 if block.category is Category.TRIGGER else 1

    # Universe requirement for specific payloads
    universe = None
    if block.category is Category.PAYLOAD:
        universe = _universe_for_material(block.material)

    special_samples: tuple[str, ...] = ()
    blueprint_shards = 0
    if tier == 2:
        special_samples = TIER2_SAMPLES
    elif tier == 3:
        special_samples = TIER3_SAMPLES
        blueprint_shards = 1

    gold = fabricator_gold(tier, stage)

    return Recipe(
        block_key=block_key,
        rarity_tier=tier,
        universe_samples=u_samples,
        universe=universe,
        special_samples=special_samples,
        blueprint_shards=blueprint_shards,
        gold=gold,
    )


class Fabricator:
    def __init__(self) -> None:
        self.builds_this_visit: int = 0

    def reset_visit(self) -> None:
        self.builds_this_visit = 0

    def can_build(self, run: Run, block_key: str) -> tuple[bool, str]:
        if self.builds_this_visit >= MAX_BUILDS_PER_VISIT:
            return False, "Maximale Bauten für diesen Besuch erreicht (3/3)."

        # Blueprint check
        blueprints = getattr(run.records, "blueprints", [])
        if block_key not in blueprints:
            return False, "Bauplan noch nicht freigeschaltet."

        recipe = build_cost(block_key, getattr(getattr(run, "plan", None), "slot", 0) + 1)

        # Gold check
        if run.gold < recipe.gold:
            return False, f"Zu wenig Gold (benötigt: {recipe.gold})."

        # Blueprint shards check
        if recipe.blueprint_shards > 0:
            shards = getattr(run, "blueprint_shards", 0)
            if shards < recipe.blueprint_shards:
                return False, "Zu wenige Bauplan-Splitter."

        # Universe samples check
        inv = run.inventory
        if recipe.universe:
            # Must be from recipe.universe
            available = sum(
                inv.sample_count(k) for k, s in SAMPLES.items() if s.universe_key == recipe.universe
            )
        else:
            # Any of the 12 universe samples
            available = sum(
                inv.sample_count(k) for k, s in SAMPLES.items() if s.universe_key != "allgemein"
            )

        if available < recipe.universe_samples:
            return False, "Zu wenige Universums-Proben."

        # Special samples check
        if recipe.special_samples:
            avail_special = sum(inv.sample_count(k) for k in recipe.special_samples)
            if avail_special < 1:
                return False, "Benötigte Zusatz-Probe fehlt."

        # Bag space check
        if not inv.can_add(block_key):
            return False, "Rucksack ist voll."

        return True, "Bereit zum Bauen."

        # Blueprint check
        blueprints = getattr(run.records, "blueprints", [])
        if block_key not in blueprints:
            return False, "Bauplan noch nicht freigeschaltet."

        recipe = build_cost(block_key, getattr(getattr(run, "plan", None), "slot", 0) + 1)

        # Gold check
        if run.gold < recipe.gold:
            return False, f"Zu wenig Gold (benötigt: {recipe.gold})."

        # Blueprint shards check
        if recipe.blueprint_shards > 0:
            shards = getattr(run, "blueprint_shards", 0)
            if shards < recipe.blueprint_shards:
                return False, "Zu wenige Bauplan-Splitter."

        # Universe samples check
        inv = run.inventory
        if recipe.universe:
            # Must be from recipe.universe
            available = sum(
                inv.sample_count(k)
                for k, s in SAMPLES.items()
                if s.universe_key == recipe.universe
            )
        else:
            # Any of the 12 universe samples
            available = sum(
                inv.sample_count(k)
                for k, s in SAMPLES.items()
                if s.universe_key != "allgemein"
            )

        if available < recipe.universe_samples:
            return False, "Zu wenige Universums-Proben."

        # Special samples check
        if recipe.special_samples:
            avail_special = sum(inv.sample_count(k) for k in recipe.special_samples)
            if avail_special < 1:
                return False, "Benötigte Zusatz-Probe fehlt."

        # Bag space check
        if not inv.can_add(block_key):
            return False, "Rucksack ist voll."

        return True, "Bereit zum Bauen."

    def craft(self, run: Run, block_key: str) -> tuple[bool, str]:
        ok, reason = self.can_build(run, block_key)
        if not ok:
            return False, reason

        recipe = build_cost(block_key, getattr(getattr(run, "plan", None), "slot", 0) + 1)
        inv = run.inventory

        # Determine which special sample to take (the one with the highest count)
        deduct_cost: dict[str, int] = {}
        if recipe.special_samples:
            best_special = max(recipe.special_samples, key=lambda k: inv.sample_count(k))
            deduct_cost[best_special] = 1

        # Determine which universe samples to take (the ones with the most stock first)
        needed_u = recipe.universe_samples
        if recipe.universe:
            candidate_keys = [k for k, s in SAMPLES.items() if s.universe_key == recipe.universe]
        else:
            candidate_keys = [k for k, s in SAMPLES.items() if s.universe_key != "allgemein"]

        # Sort candidate keys by available count descending
        sorted_candidates = sorted(
            candidate_keys, key=lambda k: inv.sample_count(k) - deduct_cost.get(k, 0), reverse=True
        )

        for ck in sorted_candidates:
            if needed_u <= 0:
                break
            have = inv.sample_count(ck) - deduct_cost.get(ck, 0)
            if have > 0:
                take_amt = min(have, needed_u)
                deduct_cost[ck] = deduct_cost.get(ck, 0) + take_amt
                needed_u -= take_amt

        if needed_u > 0:
            return False, "Zu wenige Universums-Proben."

        # Deduct samples
        if not inv.take_samples(deduct_cost):
            return False, "Fehler beim Abziehen der Proben."

        # Deduct gold & shards
        run.gold -= recipe.gold
        if recipe.blueprint_shards > 0:
            run.blueprint_shards -= recipe.blueprint_shards

        # Add block to bag
        inv.add_block(block_key)
        self.builds_this_visit += 1

        return True, f"{BLOCKS[block_key].name_de} erfolgreich gebaut."

        recipe = build_cost(block_key, getattr(getattr(run, "plan", None), "slot", 0) + 1)
        inv = run.inventory

        # Determine which special sample to take (the one with the highest count)
        deduct_cost: dict[str, int] = {}
        if recipe.special_samples:
            best_special = max(recipe.special_samples, key=lambda k: inv.sample_count(k))
            deduct_cost[best_special] = 1

        # Determine which universe samples to take (the ones with the most stock first)
        needed_u = recipe.universe_samples
        if recipe.universe:
            candidate_keys = [
                k for k, s in SAMPLES.items() if s.universe_key == recipe.universe
            ]
        else:
            candidate_keys = [
                k for k, s in SAMPLES.items() if s.universe_key != "allgemein"
            ]

        # Sort candidate keys by available count descending
        sorted_candidates = sorted(
            candidate_keys, key=lambda k: inv.sample_count(k) - deduct_cost.get(k, 0), reverse=True
        )

        for ck in sorted_candidates:
            if needed_u <= 0:
                break
            have = inv.sample_count(ck) - deduct_cost.get(ck, 0)
            if have > 0:
                take_amt = min(have, needed_u)
                deduct_cost[ck] = deduct_cost.get(ck, 0) + take_amt
                needed_u -= take_amt

        if needed_u > 0:
            return False, "Zu wenige Universums-Proben."

        # Deduct samples
        if not inv.take_samples(deduct_cost):
            return False, "Fehler beim Abziehen der Proben."

        # Deduct gold & shards
        run.gold -= recipe.gold
        if recipe.blueprint_shards > 0:
            run.blueprint_shards -= recipe.blueprint_shards

        # Add block to bag
        inv.add_block(block_key)
        self.builds_this_visit += 1

        return True, f"{BLOCKS[block_key].name_de} erfolgreich gebaut."
