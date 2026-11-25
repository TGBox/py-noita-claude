"""Phase H Spec Tests (H01-H05): Module mathematics, deck evaluation, protocols, splitters, triggers."""

from __future__ import annotations

import math

from src import materials as mat
from src.body import ENEMY_TEAM, PLAYER_TEAM, Body
from src.projectiles import ProjectileSystem, build
from src.spells import BLOCKS, CATALOG, Trigger
from src.wand import MAX_RECURSION_DEPTH, MAX_SHOTS_PER_CAST, Wand, WandSpec
from src.weapon_parts_expansion import EXPANSION_BLOCK_KEYS
from src.world import World


def _wand(*blocks: str, **stats: float) -> Wand:
    defaults: dict[str, float] = {"mana_max": 2000.0, "mana_regen": 0.0, "cast_delay": 0.0, "recharge": 0.0}
    defaults.update(stats)
    return Wand(WandSpec("Test", blocks, **defaults))


# ---------------------------------------------------------------------------
# Catalog integration
# ---------------------------------------------------------------------------


def test_phase_h_blocks_registered_with_valid_tiers() -> None:
    assert len(EXPANSION_BLOCK_KEYS) == 19
    for key in EXPANSION_BLOCK_KEYS:
        block = BLOCKS[key]
        assert block.key == key
        assert block.rarity_tier == 3
        assert block.name_de


# ---------------------------------------------------------------------------
# H01: Controlled single wrap, draw_count, recursion brake
# ---------------------------------------------------------------------------


def test_h01_deck_wrapping_and_draw_count() -> None:
    w = _wand("funke", "beschleunigung")
    first = w.cast()
    assert [s.form.key for s in first] == ["funke"]
    assert not w.last_wrapped
    assert w.last_draw_count == 1
    w.cooldown = 0.0
    second = w.cast()
    assert [s.form.key for s in second] == ["funke"]
    assert second[0].modifiers[0].key == "beschleunigung"
    assert w.last_wrapped is True
    assert w.last_draw_count == 2
    assert w.recharging or w.index == 0


def test_h01_modifier_only_deck_never_loops() -> None:
    w = _wand("beschleunigung", "proto_mu", "nerv_ende", recharge=0.4)
    shots = w.cast()
    assert shots == []
    assert w.last_draw_count <= len(w.blocks)


# ---------------------------------------------------------------------------
# H02: Copy protocols Alpha, Gamma, Tau, Omega, Zeta, Mu
# ---------------------------------------------------------------------------


def test_h02_proto_alpha_and_gamma_copy_without_draining_charges() -> None:
    # Alpha copies first slot without consuming limited bomb charge
    w_alpha = _wand("atombombe", "proto_alpha")
    w_alpha.charges[0] = 0  # depleted in slot 0, yet alpha casts a copy
    w_alpha.index = 1
    alpha_shots = w_alpha.cast()
    assert [s.form.key for s in alpha_shots] == ["atombombe"]
    assert w_alpha.charges[0] == 0

    # Gamma copies last slot without consuming limited charge
    w_gamma = _wand("proto_gamma", "atombombe")
    assert w_gamma.charges[1] == 1
    gamma_shots = w_gamma.cast()
    assert [s.form.key for s in gamma_shots] == ["atombombe"]
    assert w_gamma.charges[1] == 1


def test_h02_proto_tau_omega_zeta_and_mu() -> None:
    # Tau copies following two modules synchronously without draining charges
    w_tau = _wand("proto_tau", "atombombe", "funke")
    tau_shots = w_tau.cast()
    assert [s.form.key for s in tau_shots] == ["atombombe", "funke"]
    assert w_tau.charges[1] == 1

    # Omega fires all forms in the wand at once without consuming charges
    w_omega = _wand("proto_omega", "beschleunigung", "funke", "atombombe")
    omega_shots = w_omega.cast()
    assert [s.form.key for s in omega_shots] == ["funke", "atombombe"]
    assert omega_shots[0].modifiers[0].key == "beschleunigung"
    assert w_omega.charges[3] == 1

    # Zeta copies a form from another equipped wand
    secondary = _wand("kettenfunke")
    w_zeta = _wand("proto_zeta")
    zeta_shots = w_zeta.cast(other_wands=[secondary])
    assert [s.form.key for s in zeta_shots] == ["kettenfunke"]

    # Mu gathers all plain modifiers in the wand onto the next shot
    w_mu = _wand("proto_mu", "funke", "beschleunigung", "damage_plus" if "damage_plus" in CATALOG else "sprengkraft")
    mu_shots = w_mu.cast()
    assert [s.form.key for s in mu_shots] == ["funke"]
    mod_keys = {m.key for m in mu_shots[0].modifiers}
    assert "beschleunigung" in mod_keys
    assert "sprengkraft" in mod_keys


# ---------------------------------------------------------------------------
# H03: Clone splitters (Duo, Trio, Quadro, Dekade) & recursion brake
# ---------------------------------------------------------------------------


def test_h03_clone_splitters_multiply_and_scale_damage() -> None:
    cases = [
        ("split_duo", 2, 0.85),
        ("split_trio", 3, 0.70),
        ("split_quadro", 4, 0.55),
        ("split_dekade", 10, 0.25),
    ]
    base_dmg = CATALOG["funke"].damage
    for key, count, scale in cases:
        w = _wand(key, "funke")
        shots = w.cast()
        assert len(shots) == count
        proj = build(shots[0], 0.0, 0.0, 0.0)
        assert math.isclose(proj.damage, base_dmg * scale, rel_tol=1e-6)


def test_h03_nested_splitters_cap_at_24_and_cutoff_recursion() -> None:
    # Nested duo * trio = 6 shots
    nested = _wand("split_duo", "split_trio", "funke")
    shots = nested.cast()
    assert len(shots) == 6
    assert math.isclose(shots[0].damage_scale, 0.85 * 0.70, rel_tol=1e-6)

    # Dekade * Trio = 30 -> capped safely to MAX_SHOTS_PER_CAST (24)
    capped = _wand("split_dekade", "split_trio", "funke")
    assert len(capped.cast()) == MAX_SHOTS_PER_CAST

    # Exceeding split_dekade max depth (2) triggers cutoff
    too_deep_dekade = _wand("split_dekade", "split_dekade", "split_dekade", "funke")
    assert too_deep_dekade.cast() == []
    assert too_deep_dekade.last_cutoff is True

    # Exceeding global MAX_RECURSION_DEPTH (8) triggers cutoff
    too_deep_duo = _wand(*(["split_duo"] * (MAX_RECURSION_DEPTH + 1)), "funke")
    assert too_deep_duo.cast() == []
    assert too_deep_duo.last_cutoff is True


# ---------------------------------------------------------------------------
# H04: Satellite orbit, Entropy/Impact Larpa, Boomerang shield, Matter-Eater
# ---------------------------------------------------------------------------


def test_h04_orbit_satellites_and_larpa_effects() -> None:
    world = World(800, 200)
    ps = ProjectileSystem()
    # Satellites spawn 2 orbiting mini sparks around parent at 25% damage
    sat_shots = _wand("mod_satellit", "funke").cast()
    ps.spawn(sat_shots, 40.0, 100.0, 0.0)
    ps.update(world, 0.016, (200.0, 100.0), ())
    minis = [p for p in ps.items if p.orbit_parent is not None]
    assert len(minis) == 2
    assert math.isclose(minis[0].damage, CATALOG["funke"].damage * 0.25, rel_tol=1e-6)

    # Entropy Larpa spawns mini copies in flight over 1 second
    ps.clear()
    chaos_shots = _wand("mod_larpa_chaos", "sporenball").cast()
    ps.spawn(chaos_shots, 40.0, 100.0, 0.0)
    for _ in range(60):
        ps.update(world, 1 / 60, (200.0, 100.0), ())
    assert len(ps.items) >= 3  # parent + >= 2 spawned mini copies

    # Impact Larpa spawns 3 upward mini copies when hitting a wall
    ps.clear()
    world.fill_rect(80, 70, 90, 130, mat.ROCK)
    impact_shots = _wand("mod_larpa_treffer", "funke").cast()
    ps.spawn(impact_shots, 72.0, 100.0, 0.0)
    upward: list[object] = []
    for _ in range(10):
        ps.update(world, 1 / 60, (200.0, 100.0), ())
        upward = [p for p in ps.items if p.is_mini and p.vy < -50.0]
        if upward:
            break
    assert len(upward) == 3


def test_h04_boomerang_returns_and_matter_eater_erodes_dirt() -> None:
    world = World(600, 240)
    ps = ProjectileSystem()
    caster = (120.0, 120.0)
    boom_shots = _wand("mod_bumerang_magnet", "nadel").cast()
    ps.spawn(boom_shots, 122.0, 120.0, 0.0)
    # Fly outward first, then curve back to caster and orbit as a shield
    for _ in range(50):
        ps.update(world, 0.02, (240.0, 120.0), (), caster_pos=caster)
    assert ps.items and ps.items[0].boomerang_orbit_time > 0.0

    # Matter eater digs soft dirt instead of stopping
    ps.clear()
    world.fill_rect(140, 115, 146, 125, mat.DIRT)
    before = world.count(mat.DIRT)
    eater_shots = _wand("mod_materie_wandler", "nadel").cast()
    ps.spawn(eater_shots, 130.0, 120.0, 0.0)
    for _ in range(10):
        ps.update(world, 1 / 60, (240.0, 120.0), ())
    assert world.count(mat.DIRT) < before
    assert ps.items and ps.items[0].x > 146.0


# ---------------------------------------------------------------------------
# H05: Experimental triggers (Ablaufdatum, Ansteckung, Stoffwechsel, Abprall)
# ---------------------------------------------------------------------------


def test_h05_experimental_triggers() -> None:
    world = World(600, 200)
    ps = ProjectileSystem()

    # 1. trig_ablaufdatum: releases after 45 ticks (0.75s)
    t_timer = _wand("trig_ablaufdatum", "sporenball", "funke").cast()
    assert t_timer[0].modifiers[0].trigger is Trigger.TIMER
    assert math.isclose(t_timer[0].modifiers[0].timer, 45 / 60.0, rel_tol=1e-6)
    ps.spawn(t_timer, 60.0, 100.0, 0.0)
    seen_funke = False
    for tick in range(50):
        ps.update(world, 1 / 60, (200.0, 100.0), ())
        if tick == 30:
            assert len(ps.items) == 1  # not yet released before 45 ticks
        if any(p.form.key == "funke" for p in ps.items):
            seen_funke = True
    assert seen_funke

    # 2. trig_stoffwechsel: releases immediately upon liquid contact
    ps.clear()
    world.fill_rect(50, 60, 70, 80, mat.WATER)
    t_wet = _wand("trig_stoffwechsel", "nadel", "klumpen").cast()
    ps.spawn(t_wet, 40.0, 70.0, 0.0)
    for _ in range(10):
        ps.update(world, 1 / 60, (140.0, 70.0), ())
    assert any(p.form.key == "klumpen" for p in ps.items)

    # 3. trig_feindkontakt_kette: fires on hit and re-fires contagion payload after 1.0s
    ps.clear()
    enemy = Body(60, 64, 12, 12, hp=100.0)
    enemy.team = ENEMY_TEAM
    t_contagion = _wand("trig_feindkontakt_kette", "nadel", "funke").cast()
    ps.spawn(t_contagion, 35.0, 70.0, 0.0, team=PLAYER_TEAM)
    for _ in range(10):
        ps.update(world, 1 / 60, (140.0, 70.0), (enemy,))
    ps.items.clear()  # clear initial impact payload to observe delayed contagion trigger
    hp_before = enemy.hp
    for _ in range(65):
        ps.update(world, 1 / 60, (140.0, 70.0), (enemy,))
    assert enemy.hp < hp_before

    # 4. trig_abprall: triggers up to 3 times on wall bounces
    ps.clear()
    world2 = World(100, 100)
    world2.fill_rect(60, 10, 70, 90, mat.ROCK)
    world2.fill_rect(20, 10, 30, 90, mat.ROCK)
    t_bounce = _wand("trig_abprall", "nadel", "klumpen").cast()
    ps.spawn(t_bounce, 45.0, 50.0, 0.0)
    released_klumpen = 0
    seen: set[int] = set()
    for _ in range(60):
        ps.update(world2, 1 / 60, (80.0, 50.0), ())
        for p in ps.items:
            if p.form.key == "klumpen" and id(p) not in seen:
                seen.add(id(p))
                released_klumpen += 1
    assert released_klumpen >= 2 and released_klumpen <= 3
