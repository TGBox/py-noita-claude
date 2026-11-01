from __future__ import annotations

import json
import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

pygame.init()


# ---------------------------------------------------------------------------
# A01 — Kanonische Proben- & Regions-Schlüssel in catalog.py (V0a)
# ---------------------------------------------------------------------------
def test_a01_catalog_keys_and_region_order() -> None:
    from src.universes.catalog import UNIVERSES

    expected_samples = {
        "schrott": "probe_rost",
        "myzel": "probe_pilz",
        "magen": "probe_saft",
        "amt": "probe_papier",
        "kuchen": "probe_zucker",
        "abtei": "probe_salz",
        "ameisen": "probe_harz",
        "spule": "probe_spule",
        "glibber": "probe_bunt",
    }
    expected_regions = {
        "schrott": ["halde", "schmelze", "kernwerk"],
        "myzel": ["kappenwald", "sporennebel", "wurzelherz"],
        "magen": ["schlund", "zotten", "pfuetze"],
        "amt": ["wartezone", "registratur", "chefbueros"],
        "kuchen": ["glasur", "biskuit", "boden"],
        "abtei": ["schiff", "kreuzgang", "krypta"],
        "ameisen": ["oberbau", "gaenge", "thronsaal"],
        "spule": ["spulenwald", "kondensator", "kern"],
        "glibber": ["zelt", "backstage", "manege"],
    }
    for u_key, sample_key in expected_samples.items():
        u = UNIVERSES[u_key]
        assert u.sample_key == sample_key, f"{u_key}.sample_key mismatch"
        assert [r.key for r in u.regions] == expected_regions[u_key]

    krypta = UNIVERSES["abtei"].regions[2]
    assert krypta.key == "krypta"
    assert krypta.param("current_vx") == pytest.approx(28.0)


# ---------------------------------------------------------------------------
# A02 — Block.rarity_tier (1..3) & MODULE_ALIASES in src/spells.py (V0b, V23)
# ---------------------------------------------------------------------------
def test_a02_spells_rarity_tiers_and_aliases() -> None:
    from src.spells import BLOCKS, MODULE_ALIASES, blocks_of_tier, resolve_block_key

    for key, block in BLOCKS.items():
        assert block.rarity_tier in (1, 2, 3), f"{key} has invalid rarity_tier"

    t1 = set(blocks_of_tier(1))
    t2 = set(blocks_of_tier(2))
    t3 = set(blocks_of_tier(3))
    assert t1 and t2 and t3
    assert t1.isdisjoint(t2) and t1.isdisjoint(t3) and t2.isdisjoint(t3)
    assert (t1 | t2 | t3) == set(BLOCKS.keys())

    assert MODULE_ALIASES["funken"] == "spark"
    assert resolve_block_key("funken") == "spark"
    assert resolve_block_key("spark") == "spark"


# ---------------------------------------------------------------------------
# A03 — World.take_destroyed_cells() & gold_vein-Zählung in src/world.py (V0c)
# ---------------------------------------------------------------------------
def test_a03_world_destroyed_cells_tracking() -> None:
    from src.materials import MAT_ID
    from src.world import World

    w = World(64, 64)
    w.fill_rect(10, 10, 20, 20, MAT_ID["stone"])
    w.fill_rect(20, 10, 25, 20, MAT_ID["gold_vein"])

    assert w.take_destroyed_cells() == 0
    assert w.take_destroyed_gold_vein_cells() == 0

    w.explode(20, 15, 6)
    total = w.take_destroyed_cells()
    gold = w.take_destroyed_gold_vein_cells()
    assert total > 0
    assert gold > 0
    assert total >= gold
    # Reset after take
    assert w.take_destroyed_cells() == 0
    assert w.take_destroyed_gold_vein_cells() == 0


# ---------------------------------------------------------------------------
# A04 — Proben-Katalog (src/samples.py) & Inventar-Proben-Slots (V11)
# ---------------------------------------------------------------------------
def test_a04_samples_and_inventory_slots() -> None:
    from src.inventory import Inventory
    from src.samples import SAMPLE_SLOTS, SAMPLE_STACK, SAMPLES
    from src.universes.catalog import UNIVERSES

    assert SAMPLE_SLOTS == 12
    assert SAMPLE_STACK == 99
    assert len(SAMPLES) == 14
    for u in UNIVERSES.values():
        assert u.sample_key in SAMPLES

    inv = Inventory()
    assert len(inv.samples) == 12
    added = inv.add_sample("probe_rost", 120)
    assert added == 120
    assert inv.sample_count("probe_rost") == 120
    assert inv.samples[0] == ("probe_rost", 99)
    assert inv.samples[1] == ("probe_rost", 21)

    assert not inv.take_samples({"probe_rost": 121})
    assert inv.sample_count("probe_rost") == 120
    assert inv.take_samples({"probe_rost": 100})
    assert inv.sample_count("probe_rost") == 20
    assert inv.total_samples() == {"probe_rost": 20}


# ---------------------------------------------------------------------------
# A05 — Vereinheitlichtes Pickup-Schema in src/loot.py (V11)
# ---------------------------------------------------------------------------
def test_a05_unified_pickup_and_sprite_keys() -> None:
    from src.loot import Pickup, pickup_sprite_key

    p_legacy_block = Pickup(10.0, 20.0, block="spark")
    assert p_legacy_block.kind == "block"
    assert p_legacy_block.item_key == "spark"
    assert pickup_sprite_key(p_legacy_block) == "modul"

    p_new_block = Pickup(10.0, 20.0, kind="block", item_key="orb")
    assert p_new_block.block == "orb"

    p_sample = Pickup(0.0, 0.0, kind="sample", item_key="probe_rost", amount=3)
    assert pickup_sprite_key(p_sample) == "probe_rost"

    assert pickup_sprite_key(Pickup(0.0, 0.0, kind="gold", amount=5)) == "gold_klein"
    assert pickup_sprite_key(Pickup(0.0, 0.0, kind="gold", amount=15)) == "gold_mittel"
    assert pickup_sprite_key(Pickup(0.0, 0.0, kind="gold", amount=40)) == "gold_gross"
    assert pickup_sprite_key(Pickup(0.0, 0.0, kind="badge", amount=1)) == "dienstmarke"
    assert pickup_sprite_key(Pickup(0.0, 0.0, kind="crate", amount=1)) == "beutekiste"


# ---------------------------------------------------------------------------
# A06 — Neue Pickup-Arten in Run._pick_up & Save/Load (src/run.py) (V11)
# ---------------------------------------------------------------------------
def test_a06_run_pick_up_new_kinds() -> None:
    from src.loot import Pickup
    from src.run import Run

    run = Run(seed=11)
    assert run._pick_up(Pickup(run.player.x, run.player.y, kind="gold", amount=25))
    assert run.gold == 25

    assert run._pick_up(
        Pickup(run.player.x, run.player.y, kind="sample", item_key="probe_rost", amount=4)
    )
    assert run.inventory.sample_count("probe_rost") == 4

    assert run._pick_up(Pickup(run.player.x, run.player.y, kind="blueprint_shard", amount=3))
    assert run.blueprint_shards == 0
    assert len(run.records.blueprints) >= 1

    p_badge = Pickup(12.0, 34.0, kind="badge", amount=1)
    restored = run._pickup_from(run._pickup_data(p_badge))
    assert restored.kind == "badge"
    assert restored.amount == 1


# ---------------------------------------------------------------------------
# A07 — Gameplay-Ereignisbus Run.emit & Run.listeners in src/run.py (V12)
# ---------------------------------------------------------------------------
def test_a07_event_bus_and_audio_events_preserved() -> None:
    from src.run import Run

    run = Run(seed=12)
    received: list[tuple[str, dict[str, object]]] = []
    run.listeners.append(lambda name, data: received.append((name, data)))

    run.events.append("cast")
    run.emit("gold", amount=10, source="pickup")

    assert "cast" in run.events
    assert all(isinstance(e, str) for e in run.events)
    assert ("gold", {"amount": 10, "source": "pickup"}) in received
    assert ("gold", {"amount": 10, "source": "pickup"}) in run.emitted_events


# ---------------------------------------------------------------------------
# A08 — Neue Status-Timer auf Body & Bewegungseffekte in Player (V4b)
# ---------------------------------------------------------------------------
def test_a08_body_status_timers_and_player_modifiers() -> None:
    from src.player import Player
    from src.world import World

    world = World(64, 64)
    p = Player(32.0, 32.0)
    for attr in (
        "drunk",
        "sticky",
        "stamped_good",
        "stamped_bad",
        "marked_time",
        "frozen",
        "charged",
        "befogged",
    ):
        setattr(p.body, attr, 2.0)

    p.body.step_timers(0.5, world)
    assert p.body.frozen == pytest.approx(1.5)

    hp_before = p.body.hp
    p.body.take_damage(10.0)
    assert (hp_before - p.body.hp) == pytest.approx(12.5)


# ---------------------------------------------------------------------------
# A09 — Alle 15 Flaschen-Trinkeffekte in src/flask.py (V4b)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "liquid",
    [
        "water",
        "heal",
        "slime",
        "oil",
        "lava",
        "acid",
        "blood",
        "milk",
        "mana",
        "mud",
        "alcohol",
        "jelly",
        "steam",
        "spore",
        "honey",
    ],
)
def test_a09_all_15_flask_drink_effects(liquid: str) -> None:
    from src.flask import Flask
    from src.player import Player

    p = Player(20.0, 20.0)
    p.body.hp = 50.0
    p.body.burning = 3.0
    p.body.poisoned = 3.0
    p.mana = 10.0

    f = Flask(liquid=liquid, amount=50.0, capacity=100.0)
    msg = f.drink(p)
    assert isinstance(msg, str) and len(msg) > 0
    assert f.amount < 50.0

    if liquid == "alcohol":
        assert p.body.drunk >= 10.0
    elif liquid == "honey":
        assert p.body.sticky >= 5.0 and p.body.regen > 0.0
    elif liquid == "milk":
        assert p.body.poisoned == 0.0 and p.body.burning == 0.0


# ---------------------------------------------------------------------------
# A10 — A*-Pfadsuche für walk, fly und swim (src/pathfind.py) (V3)
# ---------------------------------------------------------------------------
def test_a10_pathfind_walk_fly_swim() -> None:
    from src.materials import MAT_ID
    from src.pathfind import PathCacheEntry, find_path, next_waypoint
    from src.world import World

    w = World(48, 32)
    # Wall with gap at top for flyer
    w.fill_rect(20, 6, 22, 31, MAT_ID["stone"])
    fly_path = find_path(w, (10, 15), (30, 15), "fly")
    assert len(fly_path) >= 2
    assert fly_path[-1] == (30, 15)

    # Water pool for swimmer
    w_swim = World(32, 24)
    w_swim.fill_rect(2, 10, 28, 20, MAT_ID["water"])
    swim_path = find_path(w_swim, (4, 15), (24, 15), "swim")
    assert swim_path[-1] == (24, 15)

    cache = PathCacheEntry()
    wp = next_waypoint(w, 10.0, 15.0, 30.0, 15.0, "fly", cache, now=1.0)
    assert len(wp) == 2


# ---------------------------------------------------------------------------
# A11 — Fraktions-Matrix & Blutfehden (src/factions.py) (V4)
# ---------------------------------------------------------------------------
def test_a11_factions_and_grudges() -> None:
    from src.factions import FACTIONS, are_hostile, record_grudge
    from src.projectiles import Projectile

    assert len(FACTIONS) == 11
    assert are_hostile("pilze", "insekten")
    assert are_hostile("behoerde", "spieler")
    assert not are_hostile("pilze", "pilze")

    grudges: set[tuple[str, str]] = set()
    assert not are_hostile("haendler", "spieler", grudges)
    record_grudge(grudges, "haendler", "spieler")
    assert are_hostile("haendler", "spieler", grudges)
    assert are_hostile("spieler", "haendler", grudges)

    proj = Projectile(x=0.0, y=0.0, vx=1.0, vy=0.0, owner_species="sporenwerfer")
    assert proj.owner_species == "sporenwerfer"


# ---------------------------------------------------------------------------
# A12 — BehaviourContext, Ability & Fähigkeiten Teil 1 (src/behaviour.py) (V1)
# ---------------------------------------------------------------------------
def test_a12_behaviour_part1_abilities() -> None:
    from src.behaviour import (
        GRAZE_MATERIAL,
        PIERCING_FORMS,
        SPLIT_SIZES,
        Ability,
        handle_eat_material,
        handle_reflect_projectiles,
        handle_split_on_death,
        handle_steal_pickup,
    )
    from src.enemies import EnemyManager
    from src.loot import Pickup
    from src.materials import MAT_ID
    from src.projectiles import Projectile
    from src.world import World

    assert GRAZE_MATERIAL["blattlaus"] == "zucker"
    assert "beam" in PIERCING_FORMS
    assert SPLIT_SIZES[0] == (1.0, 1.0)

    em = EnemyManager()
    c = em.spawn("beetle", 20.0, 20.0)
    out: list[tuple[str, dict[str, object]]] = []
    c.generation = 0
    handle_split_on_death(c, Ability("split", "beetle"), out)
    assert any(ev[0] == "split" for ev in out)

    p = Projectile(x=22.0, y=20.0, vx=-50.0, vy=0.0, from_player=True, form="spark")
    handle_reflect_projectiles(c, [p], out)
    assert p.vx > 0

    pickups = [Pickup(21.0, 20.0, kind="gold", amount=10)]
    handle_steal_pickup(c, pickups, out)
    assert c.carrying == "gold"

    w = World(32, 32)
    w.set(20, 21, MAT_ID["rust"])
    c.body.hp = 5.0
    handle_eat_material(c, "rust", w, pickups)
    assert c.body.hp > 5.0


# ---------------------------------------------------------------------------
# A13 — Verhaltens-Fähigkeiten Teil 2 (aura, teleport, summon, kamikaze, burrow, chorus)
# ---------------------------------------------------------------------------
def test_a13_behaviour_part2_abilities() -> None:
    from src.behaviour import (
        Ability,
        apply_chorus_buff,
        handle_aura,
        handle_kamikaze,
        handle_summon,
        handle_teleport,
    )
    from src.enemies import EnemyManager
    from src.player import Player
    from src.world import World

    w = World(160, 120)
    p = Player(30.0, 30.0)
    em = EnemyManager()
    c = em.spawn("beetle", 25.0, 30.0)
    out: list[tuple[str, dict[str, object]]] = []

    handle_aura(c, Ability("aura", "slow", 40.0), p, em.creatures, dt=0.5)
    assert p.body.chilled > 0.0 or p.body.sticky > 0.0

    old_pos = (c.x, c.y)
    handle_teleport(c, w, random.Random(1))
    assert (c.x, c.y) != old_pos

    handle_summon(c, Ability("summon", "beetle", 2.0), out)
    assert any(ev[0] == "summon" for ev in out)

    c_kami = em.spawn("imp", 31.0, 30.0)
    handle_kamikaze(c_kami, Ability("kamikaze", "fire", 16.0), p, w, out)
    assert c_kami.body.hp <= 0.0

    f1 = em.spawn("leech", 50.0, 50.0)
    f2 = em.spawn("leech", 60.0, 50.0)
    f3 = em.spawn("leech", 70.0, 50.0)
    f1.species = f2.species = f3.species = "moenchsfisch"
    assert apply_chorus_buff(f1, [f1, f2, f3]) == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# A14 — Erweiterte CreatureSpec, Creature-Felder & Haltungen (V1a, V1b, V1c)
# ---------------------------------------------------------------------------
def test_a14_creature_stances_and_fields() -> None:
    from src.enemies import SPECIES, CreatureSpec, EnemyManager, evaluate_stance
    from src.player import Player

    spec = SPECIES["beetle"]
    assert hasattr(spec, "stance") and hasattr(spec, "faction")
    assert isinstance(spec, CreatureSpec)

    em = EnemyManager()
    c1 = em.spawn("moth", 40.0, 40.0)
    c2 = em.spawn("moth", 50.0, 40.0)
    c1.group_id = c2.group_id = 7
    p = Player(60.0, 40.0)

    # Peaceful without aggro does not attack
    c1.aggro = False
    should_attack = evaluate_stance(c1, p, em.creatures, stance_override="peaceful")
    assert not should_attack

    # Bribed territorial does not attack
    c1.bribed = True
    assert not evaluate_stance(c1, p, em.creatures, stance_override="territorial")


# ---------------------------------------------------------------------------
# A15 — Kreaturen-Zustandsmaschine, Telegrafie & Fraktionskampf (V2, V1c)
# ---------------------------------------------------------------------------
def test_a15_enemy_fsm_and_backwards_compatible_update() -> None:
    from src.enemies import EnemyManager, begin_attack, poll_attack_ready
    from src.player import Player
    from src.world import World

    w = World(120, 80)
    p = Player(20.0, 40.0)
    em = EnemyManager()
    c = em.spawn("imp", 50.0, 40.0)

    begin_attack(c, (p.x, p.y))
    assert c.state == "windup"
    assert poll_attack_ready(c, 0.05) is None
    shot = poll_attack_ready(c, 1.0)
    assert shot == (p.x, p.y)
    assert c.state == "recover"

    # Legacy 4-arg call and extended keyword call must both work
    projs: list = []
    em.update(0.016, w, p, projs)
    out_events: list = []
    em.update(0.016, w, p, projs, grudges=set(), on_beat=True, out_events=out_events)


# ---------------------------------------------------------------------------
# A16 — Kreaturen-Sonderinteraktionen in Run (tuersteherpilz & blattlaus) (V0d)
# ---------------------------------------------------------------------------
def test_a16_bribe_and_milk_interactions() -> None:
    from src.run import Run

    run = Run(seed=16)
    run.enemies.creatures.clear()

    laus = run.enemies.spawn("beetle", run.player.x + 8.0, run.player.y)
    laus.giver = True
    hp_before = laus.body.hp
    run._kick()
    assert laus.body.hp == hp_before
    assert laus.ability_cooldowns.get("milk", 0.0) > 0.0

    pilz = run.enemies.spawn("golem", run.player.x + 12.0, run.player.y)
    pilz.species = "tuersteherpilz"
    pilz.bribed = False
    run.gold = 25
    assert run.try_interact_creature()
    assert pilz.bribed is True
    assert run.gold == 5


# ---------------------------------------------------------------------------
# A17 — Sprite-Metadaten & Animator (src/sprites.py) (V5, V0d)
# ---------------------------------------------------------------------------
def test_a17_sheet_meta_and_animator(tmp_path: Path) -> None:
    from src.sprites import Animator, load_sheet_meta

    meta_json = {
        "frame_size": [16, 20],
        "anchor": [8, 19],
        "anims": {
            "idle": {"row": 0, "frames": 4, "fps": 8.0, "loop": True},
            "attack": {"row": 1, "frames": 2, "fps": 10.0, "loop": False, "next": "idle"},
        },
        "glow": [{"offset": [2, -6], "color": [120, 240, 180], "radius": 14}],
    }
    p = tmp_path / "test.json"
    p.write_text(json.dumps(meta_json), encoding="utf-8")

    meta = load_sheet_meta(p)
    assert meta.frame_size == (16, 20)
    assert meta.anchor == (8, 19)
    assert len(meta.glow) == 1 and meta.glow[0].radius == 14

    anim = Animator(meta)
    anim.play("attack")
    anim.update(0.5)
    assert anim.state == "idle"
    assert anim.frame_rect() == (0, 0, 16, 20)


# ---------------------------------------------------------------------------
# A18 — SheetCache, blit_frame & glow_points (src/sprite_render.py) (V6)
# ---------------------------------------------------------------------------
def test_a18_sheet_cache_and_blit_frame(tmp_path: Path) -> None:
    from src.sprite_render import SheetCache, blit_frame, glow_points
    from src.sprites import Animator

    cache = SheetCache(root=tmp_path)
    surf, meta = cache.get("kreaturen", "fallback_test")
    anim = Animator(meta)
    target = pygame.Surface((64, 64), pygame.SRCALPHA)
    blit_frame(target, surf, meta, anim, 32.0, 32.0, 0.0, 0.0, flip_x=True, flash=0.5)

    pts = glow_points(meta, 32.0, 32.0, flip_x=True)
    assert isinstance(pts, list)


# ---------------------------------------------------------------------------
# A19 — Prozedurale Glieder: Chain, Legs & Tentacle (src/procbody.py Teil 1) (V7)
# ---------------------------------------------------------------------------
def test_a19_procbody_chain_legs_tentacle() -> None:
    import math

    from src.procbody import Chain, Legs, Tentacle

    ch = Chain(segments=[(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)], spacing=6.0)
    pts = ch.update(30.0, 10.0)
    assert len(pts) == 3
    d01 = math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
    assert d01 <= 6.0 + 1e-3

    legs = Legs(count=4, stride=8.0, step_height=3.0)
    l_pts = legs.update(0.1, 20.0, 20.0, vx=30.0)
    assert len(l_pts) == 4

    tent = Tentacle(segments=5, length=20.0)
    t_pts = tent.points(10.0, 10.0, time=1.5)
    assert len(t_pts) == 6 and t_pts[0] == (10.0, 10.0)


# ---------------------------------------------------------------------------
# A20 — Mehrteilige Körper: PartSpec, PartLayout & ProcRig (src/procbody.py Teil 2)
# ---------------------------------------------------------------------------
def test_a20_procbody_rig_and_parts() -> None:
    from src.procbody import RIG_LAYOUTS, PartLayout, PartSpec, ProcRig

    layout = PartLayout(
        parts=(
            PartSpec("hintergrund", (-4.0, 0.0), z_order=-1),
            PartSpec("kopf", (4.0, -6.0), z_order=2),
        )
    )
    rig = ProcRig(layout)
    rig.recoil("kopf", 3.0)
    rig.update(0.1, vx=10.0, vy=0.0, facing=-1)
    wp = rig.world_parts(100.0, 100.0, flip_x=True)
    assert [p[0] for p in wp] == ["hintergrund", "kopf"]

    rig.destroy_part("hintergrund")
    wp2 = rig.world_parts(100.0, 100.0)
    assert [p[0] for p in wp2] == ["kopf"]
    assert isinstance(RIG_LAYOUTS, dict)


# ---------------------------------------------------------------------------
# A21 — Farbpaletten & Shading-Helfer (tools/palette.py) (V8)
# ---------------------------------------------------------------------------
def test_a21_palette_ramps() -> None:
    from src.universes.catalog import UNIVERSES
    from tools.palette import ENTITY_PALETTES, OUTLINE_DARK, UNIVERSE_PALETTES, make_ramp

    assert OUTLINE_DARK == (18, 14, 24, 255)
    ramp = make_ramp((120, 160, 200))
    assert sum(ramp.shadow[:3]) < sum(ramp.mid[:3]) < sum(ramp.light[:3]) < sum(ramp.highlight[:3])

    for u in UNIVERSES.values():
        assert u.key in UNIVERSE_PALETTES
        for k in ("primary", "secondary", "accent", "glow"):
            assert k in UNIVERSE_PALETTES[u.key]

    assert "spielerin" in ENTITY_PALETTES


# ---------------------------------------------------------------------------
# A22 — Prozedurales Sprite-Framework & JSON-Exporter (tools/sprites.py) (V8)
# ---------------------------------------------------------------------------
def test_a22_sprite_builder_core(tmp_path: Path) -> None:
    from src.sprites import load_sheet_meta
    from tools.palette import make_ramp
    from tools.sprites import PixelCanvas, apply_dark_outline, draw_shaded_ellipse, save_sheet

    canvas = PixelCanvas(16, 16)
    ramp = make_ramp((180, 90, 60))
    draw_shaded_ellipse(canvas, 8, 8, 5, 5, ramp)
    apply_dark_outline(canvas)

    png_path, json_path = save_sheet(
        "kreaturen",
        "test_orb",
        {"idle": [canvas]},
        anchor=(8, 15),
        fps={"idle": 6.0},
        out_dir=tmp_path,
    )
    assert png_path.exists() and json_path.exists()
    meta = load_sheet_meta(json_path)
    assert meta.frame_size == (16, 16)


# ---------------------------------------------------------------------------
# A23 — Modulare Waffenteile & Slot-Layout (src/weapon_parts.py) (V8b)
# ---------------------------------------------------------------------------
def test_a23_weapon_parts_layout() -> None:
    from src.wand import Wand, WandSpec
    from src.weapon_parts import WEAPON_PART_KEYS, layout_for, parts_for


    assert len(WEAPON_PART_KEYS) == 10
    w = Wand(WandSpec("Test", 4, 100.0, 30.0, 0.1, 0.2, 0.0), ["chain", "spark"])
    parts = parts_for(w)
    assert len(parts) >= 3
    assert all(p in WEAPON_PART_KEYS for p in parts)

    placements = layout_for(w)
    xs = [pl.offset_x for pl in placements]
    assert xs == sorted(xs)


# ---------------------------------------------------------------------------
# A24 — Level-Datenstruktur & Run._mirror_level erweitern (V9)
# ---------------------------------------------------------------------------
def test_a24_level_struct_and_mirror() -> None:
    from src.run import Run
    from src.worldgen import Level

    lvl = Level(
        spawn=(10, 10),
        exit_point=(90, 90),
        arena=(20, 20),
        secret=(5, 5),
        vault=(60, 60),
        universe_key="myzel",
        mid_boss_arena=(10, 20, 30, 40),
        boss_arena=(50, 60, 80, 90),
        trader_nook=(12, 12, 22, 22),
        challenge_shrine=(32, 32, 42, 42),
        regions=[("kappenwald", (0, 0, 50, 50))],
        destructible_props=[("pilz_laterne", 15, 25)],
    )
    run = Run(seed=24)
    run.level = lvl
    run._mirror_level()
    assert run.level.mid_boss_arena[0] < run.level.mid_boss_arena[2]
    assert run.level.boss_arena[0] < run.level.boss_arena[2]
    assert run.level.regions[0][1][0] < run.level.regions[0][1][2]


# ---------------------------------------------------------------------------
# A25 — Generator-Dispatcher & Topologie-Helfer (src/universes/gen/) (V9)
# ---------------------------------------------------------------------------
def test_a25_gen_common_topologies() -> None:
    from src.universes.catalog import UNIVERSES
    from src.universes.gen import generate_universe
    from src.universes.gen.common import region_bands
    from src.world import World

    for topo in ("vertical", "horizontal", "concentric", "columns", "top_split", "islands"):
        bands = region_bands(300, 180, topo)
        assert len(bands) == 3
        for x0, y0, x1, y1 in bands:
            assert 0 <= x0 < x1 <= 300
            assert 0 <= y0 < y1 <= 180

    w = World(320, 200)
    lvl = generate_universe(w, UNIVERSES["schrott"], 1, 42)
    assert lvl.universe_key == "schrott"
    assert len(lvl.regions) == 3


# ---------------------------------------------------------------------------
# A26 — Regionen-Erkennung & Strömungsregel (current_vx) in Run (V0d, V9)
# ---------------------------------------------------------------------------
def test_a26_region_lookup_and_current_vx() -> None:
    from src.materials import MAT_ID
    from src.rules import apply_player_rules
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    run = Run(seed=26, universe_key="abtei")
    krypta = UNIVERSES["abtei"].regions[2]
    px, py = int(run.player.x), int(run.player.y)
    run.world.fill_rect(px - 4, py - 4, px + 4, py + 4, MAT_ID["water"])

    vx_before = run.player.body.vx
    apply_player_rules(run.player, run.world, run.universe.rule, 0.1, region=krypta)
    assert run.player.body.vx > vx_before
