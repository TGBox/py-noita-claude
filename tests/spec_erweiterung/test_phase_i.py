"""Phase I Spec Tests (I01-I04): Secret Alchemy, Cauldron, Pressurized Flasks & Reality Shifts."""

from __future__ import annotations

import random

from src import materials as mat
from src.alchemy_advanced import (
    BREW_TIME,
    Cauldron,
    SecretAlchemyEngine,
    generate_cauldron_room,
    shatter_pressurized_flask,
)
from src.body import Body
from src.flask import CAPACITY, Flask, ThrownFlask
from src.reality_shift import (
    MAX_SHIFTS_PER_RUN,
    SHIFT_COOLDOWN,
    VISION_DURATION,
    RealityShiftManager,
)
from src.workshop import ALL_STATIONS, EXPANSION_STATIONS
from src.world import World


def test_i01_seed_alchemy_budget_and_shield_tonic() -> None:
    try:
        mat.activate_key("aktenhalde")
        r1 = SecretAlchemyEngine.recipes_for_seed(42, mat.KEYS)
        r2 = SecretAlchemyEngine.recipes_for_seed(42, mat.KEYS)
        assert r1 == r2
        active = set(mat.KEYS)
        assert set(r1.schutztonikum_zutaten).issubset(active)
        assert set(r1.midas_schmelze_zutaten).issubset(active)
        assert len(set(r1.schutztonikum_zutaten)) == 3
        assert len(set(r1.midas_schmelze_zutaten)) == 3
    finally:
        mat.activate(mat.DEFAULT_SET)

    # Schutztonikum grants shield + flux boost, never heals HP without perks
    body = Body(10, 10, 8, 12, 100.0)
    body.hp = 50.0
    SecretAlchemyEngine.drink_schutztonikum(body, perks=())
    assert body.shield_hp == 40.0
    assert body.flux_boost_time == 25.0
    assert body.hp == 50.0
    body.hurt(30.0, "test")
    assert body.shield_hp == 10.0
    assert body.hp == 50.0  # absorbed by shield

    # With blutsauger perk it also heals +20 HP
    SecretAlchemyEngine.drink_schutztonikum(body, perks=("blutsauger",))
    assert body.hp == 70.0


def test_i01_midas_reaction_turns_solids_into_gold_vein() -> None:
    try:
        world = World(40, 40, seed=1)
        recipes = SecretAlchemyEngine.recipes_for_seed(7, mat.KEYS)
        s0, s1, s2 = recipes.midas_schmelze_zutaten
        world.set_cell(20, 20, mat.MAT_ID[s0])
        world.set_cell(21, 20, mat.MAT_ID[s1])
        world.set_cell(19, 20, mat.MAT_ID[s2])
        world.set_cell(20, 21, mat.MAT_ID["rock"])
        result = SecretAlchemyEngine.check_world_reaction(world, 20, 20, recipes)
        assert result == "gold_vein"
        assert world.get(20, 21) == mat.MAT_ID["gold_vein"]
    finally:
        mat.activate(mat.DEFAULT_SET)


def test_i02_cauldron_brewing_and_room_generation() -> None:
    assert "ws_kessel" in EXPANSION_STATIONS
    assert "ws_kessel" in ALL_STATIONS
    world = World(120, 90, seed=5)
    assert generate_cauldron_room(world, 1, random.Random(1)) is None
    room = generate_cauldron_room(world, 2, random.Random(1))
    assert room is not None

    recipes = SecretAlchemyEngine.recipes_for_seed(99, mat.KEYS)
    cauldron = Cauldron()
    assert cauldron.capacity_per_funnel == CAPACITY == 300
    for key in recipes.schutztonikum_zutaten:
        assert cauldron.add_from_flask(Flask(key, 60), amount=30)
    assert cauldron.ignite() is True
    assert cauldron.update(BREW_TIME - 0.5, recipes) is None
    assert cauldron.update(0.6, recipes) == "schutztonikum"

    # Wrong ingredients produce smoke_fail
    bad = Cauldron()
    bad.add_reagent("water", 30)
    bad.add_reagent("dirt", 30)
    bad.add_reagent("sand", 30)
    bad.ignite()
    res = bad.update(BREW_TIME + 0.1, recipes, world=world, cx=room.cauldron_pos[0], cy=room.cauldron_pos[1])
    assert res == "smoke_fail"


def test_i03_pressurized_flask_mix_and_60px_shatter() -> None:
    world = World(140, 100, seed=2)
    world.fill_rect(80, 30, 90, 70, mat.ROCK)
    flask = Flask("acid", 60)
    pressure = flask.mix("brausesirup", 40)
    assert pressure >= 50.0
    assert flask.is_pressurized

    enemy = Body(72, 48, 8, 8, 50.0)
    hits = shatter_pressurized_flask(world, 70.0, 50.0, flask, (enemy,))
    assert hits == 1
    assert enemy.hp < 50.0
    assert flask.empty and not flask.is_pressurized

    # Also test ThrownFlask pressurized shatter
    thrown_flask = Flask("acid", 60)
    thrown_flask.mix("brausesirup", 40)
    thrown = ThrownFlask(thrown_flask, 75.0, 50.0, 200.0, 0.0)
    shattered = False
    for _ in range(10):
        if thrown.update(world, 1 / 60, [enemy]):
            shattered = True
            break
    assert shattered
    assert thrown_flask.empty


def test_i04_reality_shift_palette_bound_cooldown_and_persistence() -> None:
    try:
        world = World(60, 60, seed=1)
        src_key, dst_key = "bone_dust", "flesh"
        world.fill_rect(10, 10, 20, 20, mat.MAT_ID[src_key])
        before_cells = world.count(mat.MAT_ID[src_key])
        mgr = RealityShiftManager()
        rec = mgr.trigger_shift(
            world,
            random.Random(3),
            active_keys=mat.KEYS,
            held_flask_key=src_key,
            elapsed_time=0.0,
            source_override=src_key,
            target_override=dst_key,
        )
        assert rec is not None
        assert rec.source == src_key and rec.target == dst_key
        assert rec.cells_changed == before_cells
        assert world.count(mat.MAT_ID[src_key]) == 0
        assert mgr.vision_timer == VISION_DURATION
        assert mat.resolve_shift_alias(src_key) == dst_key

        # Cooldown blocks immediate second shift
        assert mgr.can_shift(elapsed_time=30.0) is False
        assert mgr.can_shift(elapsed_time=SHIFT_COOLDOWN + 1.0) is True

        # Max 5 shifts per run enforced
        for _idx in range(1, MAX_SHIFTS_PER_RUN):
            mgr.last_shift_time = -SHIFT_COOLDOWN
            mgr.shifts.append(rec)
        assert len(mgr.shifts) == MAX_SHIFTS_PER_RUN
        assert mgr.can_shift(elapsed_time=10_000.0) is False

        # Save/load roundtrip preserves aliases and shift history
        restored = RealityShiftManager.from_data(mgr.to_data())
        assert restored.material_aliases[src_key] == dst_key
        assert len(restored.shifts) == MAX_SHIFTS_PER_RUN
    finally:
        mat.REALITY_ALIASES.clear()
        mat.activate(mat.DEFAULT_SET)
