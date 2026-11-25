"""Phase L Spec Tests (L01-L05): Sabotage Alarm, Chef-Prüfer, Parallel Worlds & Coffee Sun."""

from __future__ import annotations

from src.authority_expansion import (
    ALARM_BANNER_DE,
    SABOTAGE_STATIONS,
    SokoParagraf,
    WorkshopAlarmManager,
    effective_flux_cost,
)
from src.body import Body
from src.bosses.chef_pruefer import ChefPruefer
from src.materials import BEDROCK
from src.parallel_worlds import (
    BORDER_ZONE_WIDTH,
    PARALLEL_HP_MULTIPLIER,
    ParallelWorldManager,
)
from src.quest_coffee_sun import (
    ENDING_KEY,
    ESSENCE_KEYS,
    FLUX_BONUS_PER_S,
    REQUIRED_LIQUID_UNITS,
    UrPerkolator,
)
from src.records import Records
from src.wand import Wand, WandSpec
from src.world import World


def test_l01_l02_workshop_sabotage_alarm_soko_and_chef_pruefer() -> None:
    mgr = WorkshopAlarmManager()
    assert mgr.report_station_sabotage("ws_couch") is None  # couch is peaceful
    assert not mgr.alarm_active

    # First sabotage spawns SokoParagraf
    boss1 = mgr.report_station_sabotage(SABOTAGE_STATIONS[0])
    assert mgr.alarm_active is True
    assert mgr.banner_de == ALARM_BANNER_DE
    assert isinstance(boss1, SokoParagraf)

    # Frontal shield reflects frontal hits; back hit damages SokoParagraf
    reflected, dmg = boss1.take_hit(50.0, attacker_x=boss1.x + 20.0)
    assert reflected is True and dmg == 0.0
    reflected_back, dmg_back = boss1.take_hit(50.0, attacker_x=boss1.x - 20.0)
    assert reflected_back is False and dmg_back == 50.0

    # Subpoena applies +40% flux debuff (status_pfaendung)
    player = Body(10, 10, 8, 12, 100.0)
    boss1.subpoena_hit(player)
    assert getattr(player, "status_pfaendung", 0.0) == 10.0
    assert effective_flux_cost(50.0, getattr(player, "status_pfaendung", 0.0)) == 70.0

    # Repeat sabotage spawns ChefPruefer (vulnerable from behind or acid)
    boss2 = mgr.report_station_sabotage("ws_archiv")
    assert isinstance(boss2, ChefPruefer)
    assert boss2.dissolves_projectile(boss2.x + 15.0, boss2.y, is_acid=False) is True
    assert boss2.take_hit(40.0, attacker_x=boss2.x + 15.0, damage_type="normal") == 0.0
    assert boss2.take_hit(40.0, attacker_x=boss2.x - 15.0, damage_type="normal") == 40.0
    assert boss2.take_hit(25.0, attacker_x=boss2.x + 15.0, damage_type="acid") == 25.0

    # Bedrock remains indestructible
    w = World(40, 40, seed=1)
    w.fill_rect(0, 0, 40, 10, BEDROCK)
    before = w.count(BEDROCK)
    w.explode(20, 5, 10)
    assert w.count(BEDROCK) == before


def test_l03_parallel_worlds_border_hazard_and_scaling() -> None:
    world = World(160, 100, seed=11)
    mgr = ParallelWorldManager()
    player = Body(10, 50, 8, 12, 100.0)
    dmg = mgr.check_border_hazard(BORDER_ZONE_WIDTH - 5.0, world.width, 1.0, player)
    assert dmg > 0.0 and player.hp < 100.0

    enemy = Body(80, 50, 10, 10, 100.0)
    state = mgr.enter_parallel(base_seed=42, direction=1, world=world, bodies=(enemy,))
    assert state.parallel_index == 1
    assert state.mirrored is True
    assert enemy.max_hp == 100.0 * PARALLEL_HP_MULTIPLIER
    assert state.parallel_klonita.pacified is False


def test_l04_l05_cosmic_quest_ur_perkolator_and_black_coffee_sun() -> None:
    perk = UrPerkolator()
    assert not perk.is_ready_to_ignite()

    for ess in ESSENCE_KEYS:
        assert perk.insert_essence(ess)
    perk.add_liquid("fluessig_zeit", REQUIRED_LIQUID_UNITS)
    perk.add_liquid("schutztonikum", REQUIRED_LIQUID_UNITS)
    assert perk.is_ready_to_ignite()

    # Non-electric ignition does not trigger the ritual
    assert perk.ignite("water") is None
    sun = perk.ignite("plasma")
    assert sun is not None
    assert sun.flux_bonus == FLUX_BONUS_PER_S

    wand = Wand(WandSpec("Test", ("funke",), mana_max=500.0, mana_regen=0.0))
    wand.mana = 100.0
    gained = sun.apply_flux_boost(wand, 1.0)
    assert gained == FLUX_BONUS_PER_S
    assert wand.mana == 220.0

    records = Records()
    assert sun.unlock_ending(records) is True
    assert ENDING_KEY in records.endings
