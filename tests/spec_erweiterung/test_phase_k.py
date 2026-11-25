"""Phase K Spec Tests (K01-K04): Klonita Lab Assistant Upgrades, Backpack, Dialogues & Parallel."""

from __future__ import annotations

from src import materials as mat
from src.body import Body
from src.flask import Flask
from src.klonita_dialogue import EXPANSION_DIALOGUES, expansion_line_for
from src.klonita_expansion import (
    BIO_LIGHT_RADIUS,
    KLONITA_UPGRADES,
    KlonitaAssistant,
    KlonitaBackpack,
    ParallelKlonita,
)
from src.ui import format_klonita_backpack_hud
from src.universes.catalog_expansion import EXPANSION_UNIVERSES
from src.workshop import LIEGE_TABS
from src.world import World


def test_k01_klonita_upgrades_extinguisher_comb_and_indestructible() -> None:
    assert "Assistentinnen-Ausrüstung" in LIEGE_TABS
    assert len(KLONITA_UPGRADES) == 5

    assistant = KlonitaAssistant()
    assert assistant.can_hover is False
    assert assistant.light_radius == 0.0

    for key in KLONITA_UPGRADES:
        assert assistant.equip(key)

    assert assistant.can_hover is True
    assert assistant.light_radius == BIO_LIGHT_RADIUS
    assert assistant.backpack_unlocked is True

    # Extinguisher sprays 50 water cells and puts out fire on Cloita
    world = World(80, 60, seed=1)
    player = Body(30, 30, 8, 14, 100.0)
    player.burning = 3.0
    enemy = Body(20, 20, 10, 10, 50.0)
    assistant.klonita.x, assistant.klonita.y = 22.0, 22.0

    events = assistant.tick(0.1, player, world, (enemy,))
    assert "klonita_extinguished" in events
    assert "klonita_shock_comb" in events
    assert player.burning == 0.0
    assert world.count(mat.MAT_ID["water"]) == 50
    assert enemy.charged > 0.0 and enemy.frozen > 0.0

    # Indestructible Klonita revives after 5.0 seconds
    assistant.knock_out()
    assert assistant.klonita.state == "knocked"
    assistant.tick(3.0, player, world, ())
    assert assistant.klonita.state == "knocked"
    revive_events = assistant.tick(2.1, player, world, ())
    assert "klonita_revived" in revive_events
    assert assistant.klonita.state == "follow"


def test_k02_klonita_backpack_slots_hud_and_persistence() -> None:
    bp = KlonitaBackpack()
    assert len(bp.flasks) == 2 and len(bp.samples) == 4
    assert bp.add_flask(Flask("water", 100))
    assert bp.add_flask(Flask("oil", 50))
    assert bp.add_flask(Flask("acid", 25)) is False
    assert bp.add_sample("probe_rost", 3)

    labels = format_klonita_backpack_hud(bp)
    assert len(labels) == 6
    assert any("Wasser" in lbl for lbl in labels)
    assert any("probe_rost" in lbl for lbl in labels)

    restored = KlonitaBackpack.from_data(bp.to_data())
    assert restored.flasks[0] is not None and restored.flasks[0].key == "water"
    assert restored.samples[0] == ("probe_rost", 3)


def test_k03_klonita_expansion_dialogues_complete() -> None:
    for topic in ("cauldron_boil", "cauldron_danger", "alchemy_schutztonikum", "alchemy_gold_vein", "shift_start"):
        assert topic in EXPANSION_DIALOGUES
        assert expansion_line_for(topic)
    for u in EXPANSION_UNIVERSES:
        assert expansion_line_for(u.key)


def test_k04_parallel_klonita_pacified_by_schutztonikum() -> None:
    clone = ParallelKlonita(100.0, 120.0)
    ok_bad, _ = clone.pacify_with_tonic("acid")
    assert ok_bad is False and not clone.pacified

    ok_good, line = clone.pacify_with_tonic("schutztonikum")
    assert ok_good is True and clone.pacified is True and clone.reward_given is True
    assert "schutztonikum" in line.lower() or "cloita" in line.lower()
