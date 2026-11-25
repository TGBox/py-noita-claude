"""Tests for Phase Q Cloita-Null boss fight, 4 arena capacitors, quest, and Titan-Aktenkoffer."""

from __future__ import annotations

from src.bosses.cloita_null import CloitaNullBoss
from src.quest_patentamt import PatentamtQuest
from src.weapon_parts import WEAPON_PART_KEYS, get_phase3_weapon


def test_q01_q02_cloita_null_three_phases_and_four_capacitors() -> None:
    boss = CloitaNullBoss()
    assert len(boss.capacitors) == 4
    assert boss.shield_active is True
    assert boss.phase == 1
    assert boss.attack_pattern == "bueroklammern"

    # Shielded damage is reduced to 25%.
    dealt_shielded = boss.hurt(100.0)
    assert dealt_shielded == 25.0

    # Destroy all 4 arena capacitors -> overload stun + full damage.
    for i in range(4):
        boss.destroy_capacitor(i)
    assert boss.active_capacitors == 0
    assert boss.shield_active is False
    assert boss.stun_timer > 0.0
    assert boss.step(0.5) == "ueberladen"

    # Phase 2 & Phase 3 transitions.
    boss.hurt(150.0)  # hp ~ 275 / 450 -> ~0.61 -> Phase 2
    assert boss.phase == 2
    assert boss.attack_pattern == "aktenvernichter"

    boss.hurt(150.0)  # hp ~ 125 / 450 -> ~0.27 -> Phase 3
    assert boss.phase == 3
    assert boss.attack_pattern == "total_widerruf"


def test_q03_patentamt_quest_and_weapon_reward_preserve_mvp_parts() -> None:
    assert len(WEAPON_PART_KEYS) == 20
    quest = PatentamtQuest()
    assert quest.sabotage_stamp(3) == "duell_bereit"

    boss = CloitaNullBoss()
    for i in range(4):
        boss.destroy_capacitor(i)
    boss.hurt(500.0)
    assert boss.dead is True

    reward = quest.resolve_boss_fight(boss)
    assert reward is not None
    assert quest.stage == "abgeschlossen"
    assert quest.reward_weapon_key == "waffe_patent_koffer"
    assert get_phase3_weapon("waffe_titan_koffer")["name_de"] == "Titan-Aktenkoffer-Blaster"
