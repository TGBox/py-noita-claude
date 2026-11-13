"""Contract V19: the 6 workshop traders, their offers and purchase rules (Cards E04, E05)."""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class TraderOffer:
    kind: str
    key: str
    gold_cost: int
    sample_cost: tuple[tuple[str, int], ...] = ()
    blessing: str = ""


@dataclass(frozen=True)
class TraderSpec:
    key: str
    name: str
    home_universe: str
    greeting_de: str
    quirk_de: str
    category: str
    price_multiplier: float = 1.0
    flat_fee: int = 0


TRADERS: dict[str, TraderSpec] = {
    "npc_magenhaendler": TraderSpec(
        key="npc_magenhaendler",
        name="Herr Pansen",
        home_universe="fleischwelt",
        greeting_de="Frische Körpersäfte direkt aus dem Magen! Alles noch warm.",
        quirk_de="Verkauft nur fleischwelt-eigene Füllungen (Blut, Säure, Glut).",
        category="PAYLOAD",
    ),
    "npc_sachbearbeiterin": TraderSpec(
        key="npc_sachbearbeiterin",
        name="Frau Abheft",
        home_universe="aktenhalde",
        greeting_de="Antrag auf Zauberausgabe bitte in dreifacher Ausfertigung.",
        quirk_de="Erhebt 10 Gold Bearbeitungsgebühr auf jedes Angebot.",
        category="TRIGGER",
        flat_fee=10,
    ),
    "npc_glibberhaendler": TraderSpec(
        key="npc_glibberhaendler",
        name="Wobbel",
        home_universe="glibbria",
        greeting_de="Huiiii! Alles wackelt, alles prallt!",
        quirk_de="Spezialist für Modifikatoren und Sprungkraft.",
        category="MODIFIER",
    ),
    "npc_ameisenhehler": TraderSpec(
        key="npc_ameisenhehler",
        name="Krümel-Karl",
        home_universe="kruemelreich",
        greeting_de="Pst! Feine Schmuggelware, kaum vom Boden aufgelesen.",
        quirk_de="25 % Rabatt oder Tausch gegen 2 Zuckerkristalle.",
        category="ANY",
        price_multiplier=0.75,
    ),
    "npc_dj": TraderSpec(
        key="npc_dj",
        name="DJ Lamelle",
        home_universe="sporenklub",
        greeting_de="Fühl den Beat! Keine Transaktion ohne Rhythmus.",
        quirk_de="Verkauft Formen nur im Takt des Basses.",
        category="FORM",
    ),
    "npc_kuester": TraderSpec(
        key="npc_kuester",
        name="Bruder Flosse",
        home_universe="abtei",
        greeting_de="Möge die Tiefe deinen Stab segnen, Wanderer.",
        quirk_de="Verkauft nur geweihte Stäbe mit heiligem Segen.",
        category="WAND",
    ),
}


def traders_for_workshop(visited: list[str]) -> list[TraderSpec]:
    """Home traders of the (at most) two most recently visited universes, newest first."""
    if not visited:
        return []
    # Map universe to trader
    u_to_trader: dict[str, TraderSpec] = {spec.home_universe: spec for spec in TRADERS.values()}
    result: list[TraderSpec] = []
    # Iterate from newest to oldest, without duplicates
    for u_key in reversed(visited):
        if u_key in u_to_trader:
            spec = u_to_trader[u_key]
            if spec not in result:
                result.append(spec)
            if len(result) == 2:
                break
    return result


def generate_offers(
    trader: TraderSpec,
    stage: int,
    rng: random.Random,
    *,
    price_factor: float = 1.0,
) -> list[TraderOffer]:
    """Generate 4 offers from the trader's category."""
    from src.economy import module_price, weapon_price
    from src.spells import BLOCKS, Category

    effective_factor = price_factor * trader.price_multiplier

    if trader.category == "WAND":
        # Bruder Flosse sells 4 wands with blessings
        blessings = ("mana_max", "recharge", "capacity")
        base_price = weapon_price(stage, effective_factor) + trader.flat_fee
        offers: list[TraderOffer] = []
        for _ in range(4):
            blessing = rng.choice(blessings)
            offers.append(
                TraderOffer(
                    kind="wand",
                    key="",
                    gold_cost=base_price,
                    blessing=blessing,
                )
            )
        return offers

    # Block pools
    if trader.key == "npc_magenhaendler":
        candidates = ["sekret_blut", "sekret_saeure", "sekret_glut"]
    elif trader.category == "ANY":
        candidates = [k for k, b in BLOCKS.items() if not b.retired]
    else:
        target_cat = getattr(Category, trader.category)
        candidates = [k for k, b in BLOCKS.items() if b.category is target_cat and not b.retired]

    # Pick 4 candidates (with replacement if len < 4, without if len >= 4)
    if len(candidates) >= 4:
        chosen_keys = rng.sample(candidates, 4)
    else:
        chosen_keys = [rng.choice(candidates) for _ in range(4)]

    sample_cost: tuple[tuple[str, int], ...] = ()
    if trader.key == "npc_ameisenhehler":
        sample_cost = (("probe_zuckerkristall", 2),)

    offers = []
    for k in chosen_keys:
        block = BLOCKS[k]
        cost = module_price(block.rarity_tier, stage, effective_factor) + trader.flat_fee
        offers.append(
            TraderOffer(
                kind="block",
                key=k,
                gold_cost=cost,
                sample_cost=sample_cost,
            )
        )
    return offers


def buy_offer(
    run: Run,
    trader: TraderSpec,
    offer: TraderOffer,
    *,
    use_samples: bool = False,
) -> tuple[bool, str]:
    """Execute a purchase and return (ok, German message)."""
    # 1. DJ Lamelle beat check
    if trader.key == "npc_dj":
        t = getattr(run, "time", None)
        if t is None:
            t = getattr(run, "time_in_depth", None)
        if t is None:
            t = run.stats.get("time", 0.0)
        if int(t / 0.75) % 2 != 0:
            return False, "Nicht im Takt!"

    # 2. Payment
    if use_samples:
        if not offer.sample_cost:
            return False, "Kein Proben-Tausch möglich."
        cost_dict = dict(offer.sample_cost)
        if not run.inventory.take_samples(cost_dict):
            return False, "Zu wenige Proben."
    else:
        cost = round(offer.gold_cost * getattr(run, "price_factor", 1.0))
        if run.gold < cost:
            return False, "Zu wenig Gold."
        run.gold -= cost

    # 3. Deliver item
    if offer.kind == "block":
        run.inventory.add_block(offer.key)
        return True, "Modul gekauft."
    elif offer.kind == "wand":
        from src.loot import Pickup, generate_wand

        stage = getattr(getattr(run, "plan", None), "slot", 0) + 1
        wand_spec = generate_wand(run.rng, level=stage)
        if offer.blessing == "mana_max":
            wand_spec = replace(wand_spec, mana_max=round(wand_spec.mana_max * 1.1))
        elif offer.blessing == "recharge":
            wand_spec = replace(wand_spec, recharge=round(wand_spec.recharge * 0.9, 3))
        elif offer.blessing == "capacity":
            wand_spec = replace(wand_spec, capacity=wand_spec.capacity + 1)
        dropped = run.inventory.add_wand(wand_spec)
        if dropped is not None:
            px, py = run.player.center
            run.pickups.append(Pickup(px, py, wand=dropped))
        return True, "Waffe gekauft."

    return False, "Unbekanntes Angebot."
