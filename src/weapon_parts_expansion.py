"""Expansion weapon modules (Phase H): protocols, clone splitters, orbit modifiers, triggers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.spells import Block, Category, Trigger

EXPANSION_BLOCK_KEYS: tuple[str, ...] = (
    # H02 Copy protocols
    "proto_alpha",
    "proto_gamma",
    "proto_tau",
    "proto_omega",
    "proto_zeta",
    "proto_mu",
    # H03 Clone splitters
    "split_duo",
    "split_trio",
    "split_quadro",
    "split_dekade",
    # H04 Orbit, Larpa, Boomerang & Matter-Eater modifiers
    "mod_satellit",
    "mod_larpa_chaos",
    "mod_larpa_treffer",
    "mod_bumerang_magnet",
    "mod_materie_wandler",
    # H05 Experimental triggers
    "trig_ablaufdatum",
    "trig_feindkontakt_kette",
    "trig_stoffwechsel",
    "trig_abprall",
)


def build_expansion_blocks(
    block_cls: type[Block],
    category_enum: type[Category],
    trigger_enum: type[Trigger],
) -> tuple[Block, ...]:
    """Construct all 19 Phase H expansion blocks using the core Block dataclass."""
    return (
        # H02 Copy protocols (Seltenheit 4 / tier 3 in MVP catalog scaling)
        block_cls(
            "proto_alpha",
            "Protokoll Alpha",
            category_enum.MODIFIER,
            mana=35,
            rarity=0.15,
            rarity_tier=3,
            copy_protocol="alpha",
            description_de=(
                "Kopiert das erste Modul im Waffenrahmen ohne Ladungen zu verbrauchen."
            ),
        ),
        block_cls(
            "proto_gamma",
            "Protokoll Gamma",
            category_enum.MODIFIER,
            mana=35,
            rarity=0.15,
            rarity_tier=3,
            copy_protocol="gamma",
            description_de=(
                "Kopiert das letzte Modul im Waffenrahmen ohne Ladungen zu verbrauchen."
            ),
        ),
        block_cls(
            "proto_tau",
            "Protokoll Tau",
            category_enum.MODIFIER,
            mana=45,
            rarity=0.15,
            rarity_tier=3,
            copy_protocol="tau",
            description_de="Kopiert die beiden nachfolgenden Module als synchronen Doppelschuss.",
        ),
        block_cls(
            "proto_omega",
            "Protokoll Omega",
            category_enum.MODIFIER,
            mana=85,
            rarity=0.12,
            rarity_tier=3,
            copy_protocol="omega",
            description_de="Feuert alle Module der Waffe gleichzeitig ab.",
        ),
        block_cls(
            "proto_zeta",
            "Protokoll Zeta",
            category_enum.MODIFIER,
            mana=50,
            rarity=0.15,
            rarity_tier=3,
            copy_protocol="zeta",
            description_de="Kopiert ein zufälliges Geschoss einer anderen getragenen Waffe.",
        ),
        block_cls(
            "proto_mu",
            "Protokoll Mu",
            category_enum.MODIFIER,
            mana=60,
            rarity=0.14,
            rarity_tier=3,
            copy_protocol="mu",
            description_de="Wendet alle Aufsätze der Waffe gebündelt auf das nächste Geschoss an.",
        ),
        # H03 Clone splitters (Divide By 2, 3, 4, 10)
        block_cls(
            "split_duo",
            "Klon-Splitter: Duo",
            category_enum.MODIFIER,
            mana=20,
            rarity=0.25,
            rarity_tier=3,
            split_count=2,
            split_damage_penalty=0.15,
            split_max_depth=8,
            description_de="Teilt das folgende Modul in 2 Kopien (-15 % Direktschaden).",
        ),
        block_cls(
            "split_trio",
            "Klon-Splitter: Trio",
            category_enum.MODIFIER,
            mana=35,
            rarity=0.20,
            rarity_tier=3,
            split_count=3,
            split_damage_penalty=0.30,
            split_max_depth=6,
            description_de="Teilt das folgende Modul in 3 Kopien (-30 % Direktschaden).",
        ),
        block_cls(
            "split_quadro",
            "Klon-Splitter: Quadro",
            category_enum.MODIFIER,
            mana=50,
            rarity=0.15,
            rarity_tier=3,
            split_count=4,
            split_damage_penalty=0.45,
            split_max_depth=4,
            description_de="Teilt das folgende Modul in 4 Kopien (-45 % Direktschaden).",
        ),
        block_cls(
            "split_dekade",
            "Klon-Splitter: Dekade",
            category_enum.MODIFIER,
            mana=90,
            rarity=0.10,
            rarity_tier=3,
            split_count=10,
            split_damage_penalty=0.75,
            split_max_depth=2,
            description_de="Teilt das folgende Modul in 10 Kopien (-75 % Direktschaden).",
        ),
        # H04 Satellite, Larpa, Boomerang & Matter-Eater modifiers
        block_cls(
            "mod_satellit",
            "Satelliten-Koppelung",
            category_enum.MODIFIER,
            mana=25,
            rarity=0.35,
            rarity_tier=3,
            orbit_satellites=2,
            description_de="Zwei Mini-Funken umkreisen das Geschoss im 16-px-Orbit (25 % Schaden).",
        ),
        block_cls(
            "mod_larpa_chaos",
            "Entropie-Larpa",
            category_enum.MODIFIER,
            mana=40,
            rarity=0.25,
            rarity_tier=3,
            larpa_chaos=True,
            description_de="Spuckt im Flug zweimal pro Sekunde Miniaturkopien in Zufallsrichtungen.",
        ),
        block_cls(
            "mod_larpa_treffer",
            "Aufprall-Eruption",
            category_enum.MODIFIER,
            mana=35,
            rarity=0.28,
            rarity_tier=3,
            larpa_impact=True,
            description_de="Schleudert beim Wandeinschlag 3 Mini-Kopien nach oben.",
        ),
        block_cls(
            "mod_bumerang_magnet",
            "Heimkehr-Feld",
            category_enum.MODIFIER,
            mana=25,
            rarity=0.30,
            rarity_tier=3,
            boomerang_shield=True,
            lifetime_factor=2.0,
            description_de="Geschosse kehren zu Cloita zurück und bilden für 3 s einen Orbit-Schild.",
        ),
        block_cls(
            "mod_materie_wandler",
            "Phasen-Konverter",
            category_enum.MODIFIER,
            mana=30,
            rarity=0.28,
            rarity_tier=3,
            matter_eater=2,
            description_de="Löscht beim Flug weiche Feststoffe (Erde, Papier) im 2-px-Radius.",
        ),
        # H05 Experimental triggers
        block_cls(
            "trig_ablaufdatum",
            "Zünder: Verfall",
            category_enum.TRIGGER,
            mana=15,
            rarity=0.35,
            rarity_tier=3,
            trigger=trigger_enum.TIMER,
            timer=45 / 60.0,
            description_de="Explodiert nach exakt 45 Ticks (0,75 s) und setzt die Nutzlast frei.",
        ),
        block_cls(
            "trig_feindkontakt_kette",
            "Zünder: Ansteckung",
            category_enum.TRIGGER,
            mana=25,
            rarity=0.28,
            rarity_tier=3,
            trigger=trigger_enum.IMPACT,
            contagion_delay=1.0,
            description_de="Pflanzt dem Ziel eine Mini-Ladung ein, die nach 1 s erneut zündet.",
        ),
        block_cls(
            "trig_stoffwechsel",
            "Zünder: Flüssigkeitskontakt",
            category_enum.TRIGGER,
            mana=15,
            rarity=0.35,
            rarity_tier=3,
            trigger=trigger_enum.WET,
            description_de="Zündet sofort beim Eintauchen in eine Flüssigkeit.",
        ),
        block_cls(
            "trig_abprall",
            "Zünder: Flummifeder",
            category_enum.TRIGGER,
            mana=20,
            rarity=0.30,
            rarity_tier=3,
            trigger=trigger_enum.IMPACT,
            trigger_bounces=3,
            bounce_bonus=3,
            description_de="Zündet bei jedem Abprall an einer Wand (bis zu 3 Zündungen).",
        ),
    )


def __getattr__(name: str) -> Any:
    if name in ("EXPANSION_BLOCKS", "EXPANSION_CATALOG"):
        from src.spells import CATALOG

        blocks = tuple(CATALOG[k] for k in EXPANSION_BLOCK_KEYS)
        if name == "EXPANSION_BLOCKS":
            return blocks
        return {b.key: b for b in blocks}
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
