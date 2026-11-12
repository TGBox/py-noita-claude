from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def _check_universe_generator(u_key: str) -> None:
    from src.materials import MAT_ID
    from src.universes.catalog import ALL_UNIVERSES
    from src.universes.gen import GENERATORS, generate_universe
    from src.world import World

    assert u_key in GENERATORS
    u = ALL_UNIVERSES[u_key]
    w = World(320, 200)
    lvl = generate_universe(w, u, 1, 42)

    assert lvl.universe_key == u.key
    assert [r[0] for r in lvl.regions] == [r.key for r in u.regions]
    sx, sy = lvl.spawn
    ex, ey = lvl.exit_point
    assert w.get(sx, sy) == MAT_ID["air"]
    assert w.get(ex, ey) == MAT_ID["air"]
    for rect in (lvl.mid_boss_arena, lvl.boss_arena):
        assert 0 <= rect[0] < rect[2] <= w.width
        assert 0 <= rect[1] < rect[3] <= w.height


# V9 section 4 "Inhalts-Abnahme": topology, per-region material shares (sampled every 2 px),
# props and quest giver of every MVP generator. Shares are lower bounds unless noted.
GENERATOR_CONTENT: dict[str, dict] = {
    "fleischwelt": {
        "topology": "vertical",
        "regions": {
            "schlund": [(("enamel",), 0.005)],
            "magen": [(("acid",), 0.01), (("tallow",), 0.005)],
            "knochenmark": [(("bone",), 0.15), (("enamel",), 0.003)],
        },
        "world": [(("flesh",), 0.20)],
        "props": ("saeure_behaelter", "magen_zotte"),
    },
    "aktenhalde": {
        "topology": "horizontal",
        "regions": {
            "registratur": [(("aktendeckel",), 0.02), (("papier",), 0.05)],
            "grossraumbuero": [(("air",), 0.25)],
            "archivkeller": [(("tinte",), 0.02)],
        },
        "world": [],
        "props": ("akten_regal", "amt_uhr"),
    },
    "glibbria": {
        "topology": "islands",
        "regions": {
            "gelee_huegel": [(("glibber", "glibber_rot"), 0.10), (("zuckerguss",), 0.003)],
            "kaugummi_hoehlen": [(("kaugummi",), 0.01)],
            "sirupkueste": [(("brausesirup",), 0.05)],
        },
        "world": [],
        "props": ("glibber_ballon",),
    },
    "kruemelreich": {
        "topology": "top_split",
        "regions": {
            "fliesenwueste": [(("fliese",), 0.05), (("kruemel",), 0.005), (("zucker",), 0.003)],
            "unter_kuehlschrank": [(("staubfluse",), 0.01)],
            "ameisenbau": [(("brosel", "kruemel"), 0.15)],
        },
        "world": [],
        "props": ("ameisen_kokon",),
    },
    "sporenklub": {
        "topology": "vertical",
        "regions": {
            "lautsprechertuerme": [(("pilzhut",), 0.05)],
            "tanzflaeche": [(("leuchtsporen",), 0.003), (("air",), 0.30)],
            "hinterzimmer": [(("pilzfleisch",), 0.15)],
        },
        "world": [],
        "props": ("sporen_knolle", "pilz_laterne"),
    },
    "abtei": {
        "topology": "vertical",
        "regions": {
            "glockenturm": [(("glockenbronze",), 0.003)],
            "kirchenschiff": [(("mauerwerk",), 0.05), (("buntglas",), 0.003), (("water",), 0.20)],
            "krypta": [(("algen",), 0.003)],
        },
        "world": [(("kerzenwachs",), 0.0005)],
        "props": ("abtei_glocke",),
    },
}


def _share(w, rect: tuple[int, int, int, int], keys: tuple[str, ...], step: int = 2) -> float:
    from src import materials as mat

    want = {mat.MAT_ID[k] for k in keys}
    x0, y0, x1, y1 = rect
    total = hit = 0
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            total += 1
            hit += w.get(x, y) in want
    return hit / max(1, total)


def _check_generator_content(u_key: str) -> tuple:
    from src import materials as mat
    from src.universes.catalog import ALL_UNIVERSES
    from src.universes.gen import generate_universe
    from src.universes.gen.common import region_bands
    from src.world import World

    spec = GENERATOR_CONTENT[u_key]
    w = World(320, 200)
    lvl = generate_universe(w, ALL_UNIVERSES[u_key], 1, 42)
    assert mat.ACTIVE is not None and mat.ACTIVE.key == ALL_UNIVERSES[u_key].material_set

    assert [r[1] for r in lvl.regions] == region_bands(w.width, w.height, spec["topology"]), (
        f"{u_key}: regions do not follow topology {spec['topology']!r}"
    )
    rects = dict(lvl.regions)
    for region, rules in spec["regions"].items():
        for keys, minimum in rules:
            got = _share(w, rects[region], keys)
            assert got >= minimum, f"{u_key}/{region}: {'+'.join(keys)} {got:.3f} < {minimum}"
    for keys, minimum in spec["world"]:
        got = _share(w, (0, 0, w.width, w.height), keys)
        assert got >= minimum, f"{u_key}: {'+'.join(keys)} {got:.4f} < {minimum} in the world"

    prop_keys = {key for key, _, _ in lvl.destructible_props}
    assert set(spec["props"]) <= prop_keys, f"{u_key}: props {prop_keys} miss {spec['props']}"
    for _, px, py in lvl.destructible_props:
        assert 0 <= px < w.width and 0 <= py < w.height

    assert lvl.quest_giver is not None, f"{u_key}: no quest giver"
    qx, qy = lvl.quest_giver
    air = mat.MAT_ID["air"]
    assert w.get(qx, qy) == air, f"{u_key}: quest giver stands inside material"
    assert any(w.get(qx, qy + d) != air for d in range(1, 13)), f"{u_key}: quest giver floats"
    return w, lvl


def test_d01_generator_fleischwelt() -> None:
    _check_universe_generator("fleischwelt")
    _, lvl = _check_generator_content("fleischwelt")
    assert lvl.secret is not None, "fleischwelt: sealed bone chamber (Erinnerungssplitter) missing"


def test_d02_generator_aktenhalde() -> None:
    from src import materials as mat
    from src.universes.catalog import ALL_UNIVERSES
    from src.universes.gen import generate_universe
    from src.world import World

    _check_universe_generator("aktenhalde")
    _check_generator_content("aktenhalde")

    # Brandabschnitte (bible 03): no connected paper area larger than 640x360.
    w = World(1280, 720)
    generate_universe(w, ALL_UNIVERSES["aktenhalde"], 1, 42)
    paper = mat.MAT_ID["papier"]
    step = 2
    gw, gh = w.width // step, w.height // step
    seen = bytearray(gw * gh)
    for start in range(gw * gh):
        if seen[start] or w.get((start % gw) * step, (start // gw) * step) != paper:
            continue
        seen[start] = 1
        stack = [start]
        x0 = x1 = start % gw
        y0 = y1 = start // gw
        while stack:
            i = stack.pop()
            gx, gy = i % gw, i // gw
            x0, x1, y0, y1 = min(x0, gx), max(x1, gx), min(y0, gy), max(y1, gy)
            for nx, ny in ((gx + 1, gy), (gx - 1, gy), (gx, gy + 1), (gx, gy - 1)):
                j = ny * gw + nx
                if 0 <= nx < gw and 0 <= ny < gh and not seen[j]:
                    if w.get(nx * step, ny * step) == paper:
                        seen[j] = 1
                        stack.append(j)
        width, height = (x1 - x0 + 1) * step, (y1 - y0 + 1) * step
        assert width <= 640 and height <= 360, f"paper area {width}x{height} has no firebreak"


def test_d03_generator_glibbria() -> None:
    _check_universe_generator("glibbria")
    w, lvl = _check_generator_content("glibbria")
    bottom = (0, w.height * 9 // 10, w.width, w.height)
    assert _share(w, bottom, ("brausesirup",)) >= 0.3, "glibbria: no syrup sea at the bottom"
    assert lvl.quest_target is not None, "glibbria: cow escort target missing"


def test_d04_generator_kruemelreich() -> None:
    _check_universe_generator("kruemelreich")
    _check_generator_content("kruemelreich")


def test_d05_generator_sporenklub() -> None:
    _check_universe_generator("sporenklub")
    _check_generator_content("sporenklub")


def test_d06_generator_abtei() -> None:
    _check_universe_generator("abtei")
    w, lvl = _check_generator_content("abtei")
    tower = dict(lvl.regions)["glockenturm"]
    assert _share(w, tower, ("water",)) <= 0.01, "abtei: the bell tower must stay dry"


def test_d10_worldgen_dispatch_and_boss_spawns() -> None:
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    u = UNIVERSES["sporenklub"]
    run = Run(seed=10, universe_key="sporenklub")
    assert run.level.universe_key == "sporenklub"
    species_alive = [c.species for c in run.enemies.creatures]
    assert species_alive.count(u.mid_boss) == 1
    assert u.boss not in species_alive

    from src.materials import KEYS

    assert "pilzhut" in KEYS  # the universe's material set is active

    boss_run = Run(seed=10, universe_key="sporenklub", boss_slot=True)
    species_alive = [c.species for c in boss_run.enemies.creatures]
    assert u.mid_boss in species_alive
    assert species_alive.count(u.boss) == 1


def test_d11_universe_events_part1() -> None:
    from src.events import EVENTS, Event, pick_event
    from src.run import Run

    assert len(EVENTS) >= 6
    run = Run(seed=11)
    for key, spec in list(EVENTS.items())[:5]:
        ev = Event(spec=spec, remaining=spec.duration)
        ev.on_start(run)
        ev.tick(1.0, run)
        data = ev.to_data()
        restored = Event.from_data(data)
        assert restored is not None and restored.spec.key == key
        ev.on_end(run)
        assert ev.active is False

    rng = random.Random(42)
    picked = [pick_event("fleischwelt", 1, rng) for _ in range(30)]
    assert any(p is not None for p in picked)


def test_d12_universe_events_part2() -> None:
    from src.events import EVENTS, Event
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    assert set(EVENTS) == {u.event for u in UNIVERSES.values()}
    assert EVENTS["verdauung"].interval == 90.0 and EVENTS["verdauung"].duration == 20.0
    run = Run(seed=12)
    for spec in EVENTS.values():
        assert spec.interval > 0.0
        ev = Event(spec=spec, remaining=spec.duration)
        ev.on_start(run)
        ev.tick(1.0, run)
        ev.on_end(run)
        assert ev.active is False

    started: list[str] = []
    run.listeners.append(lambda name, data: started.append(name))
    step = 0.5
    for _ in range(int((EVENTS["verdauung"].interval + 1.0) / step)):
        run.update(step, None)
    assert "event_start" in started
    assert run.event is not None and run.event.spec.key == "verdauung"


def test_d13_all_6_challenges() -> None:
    from src.challenges import CHALLENGES, Challenge
    from src.run import Run

    assert set(CHALLENGES.keys()) == {
        "pacifist",
        "no_gold",
        "speed_run",
        "no_damage",
        "kill_streak",
        "dry_feet",
    }
    run = Run(seed=13)
    ch = Challenge(spec=CHALLENGES["pacifist"])
    ch.activate()
    ch.on_event(
        "leave_universe", {"universe": "fleischwelt", "depth": 1, "destination": "workshop"}, run
    )
    assert ch.completed is True


def test_d14_challenge_shrine_and_reward_in_run() -> None:
    from src.challenges import CHALLENGES, Challenge
    from src.run import Run

    run = Run(seed=14)
    ch = Challenge(spec=CHALLENGES["pacifist"])
    ch.activate()
    ch.completed = True
    gold_before = run.gold
    ch.pay_reward(run)
    assert run.gold == gold_before + CHALLENGES["pacifist"].reward_gold
    assert ch.reward_paid is True


def test_d15_playtest_bot_single_universe() -> None:
    from src.bot import run_bot

    rep = run_bot("fleischwelt", seed=1, max_seconds=10.0)
    assert rep.universe_key == "fleischwelt"
    assert rep.ticks > 0
    assert rep.errors == []


def test_d16_playtest_bot_full_run() -> None:
    from src.bot import run_full

    full = run_full(seed=1, max_seconds_per_stage=6.0)
    assert len(full) >= 1
    assert all(r.errors == [] for r in full)


def _check_material_set(
    u_key: str,
    own: tuple[str, ...],
    reactions: tuple[tuple[str, str], ...] = (),
    glowing: tuple[str, ...] = (),
) -> None:
    from src.materials import BASE_KEYS, LIBRARY, MAX_MATERIALS, SETS, activate
    from src.reactions import RULES
    from src.universes.catalog import UNIVERSES

    assert UNIVERSES[u_key].material_set == u_key
    ms = SETS[u_key]
    keys = ms.keys()
    assert set(BASE_KEYS) <= set(keys)
    extra = [k for k in keys if k not in BASE_KEYS]
    assert set(own) <= set(extra)
    assert len(extra) <= 10 and len(keys) <= MAX_MATERIALS
    pairs = {(r.actor, r.neighbour) for r in (*RULES, *ms.reactions)}
    for a, b in reactions:
        assert (a, b) in pairs or (b, a) in pairs, f"missing reaction {a} + {b}"
    for k in glowing:
        assert LIBRARY[k].glow > 0
    activate(ms)
    activate(SETS["koerper"])


def test_d17_material_set_fleischwelt() -> None:
    _check_material_set(
        "fleischwelt",
        (
            "flesh",
            "bone",
            "enamel",
            "blood",
            "acid",
            "growth",
            "spores",
            "tallow",
            "crust",
            "magma",
        ),
    )


def test_d18_material_set_glibbria() -> None:
    _check_material_set(
        "glibbria",
        ("glibber", "glibber_rot", "brausesirup", "schaum", "kaugummi", "zuckerguss"),
        (("fire", "glibber_rot"), ("fire", "brausesirup"), ("fire", "zuckerguss")),
    )


def test_d19_material_set_kruemelreich() -> None:
    _check_material_set(
        "kruemelreich",
        ("kruemel", "brosel", "zucker", "karamell", "honig", "fliese", "staubfluse"),
        (("fire", "zucker"),),
    )


def test_d20_material_set_sporenklub() -> None:
    _check_material_set(
        "sporenklub",
        ("pilzfleisch", "pilzhut", "leuchtsporen", "neonsaft", "nebel"),
        glowing=("leuchtsporen", "neonsaft"),
    )


def test_d21_material_set_abtei() -> None:
    _check_material_set(
        "abtei",
        ("mauerwerk", "buntglas", "kerzenwachs", "glockenbronze", "algen", "weihrauch"),
        (("fire", "kerzenwachs"),),  # algae no longer grow into water (playtest)
    )


# ---------------------------------------------------------------------------
# D22–D29 — Universums-Herausforderungen (src/challenges.py) (V13b)
# ---------------------------------------------------------------------------
def test_d22_quest_data_and_rewards() -> None:
    from src.challenges import QUESTS, Quest, quest_for
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    assert set(QUESTS) == {f"challenge_{u.key}" for u in UNIVERSES.values()}
    for u_key in [u.key for u in UNIVERSES.values()]:
        run = Run(seed=22, universe_key=u_key)
        q = quest_for(u_key)
        assert q.spec.universe == u_key and not q.accepted
        assert q.turn_in(run) is False
        q.accept(run)
        assert q.accepted
        q.progress = q.spec.goal
        sample_key = UNIVERSES[u_key].sample_key
        if u_key == "fleischwelt":
            run.inventory.add_sample("probe_gallenstein", 3)
        gold, pickups = run.gold, len(run.pickups)
        rerolls, samples = run.inventory.rerolls, run.inventory.sample_count(sample_key)
        assert q.turn_in(run) is True and q.reward_paid
        assert q.turn_in(run) is False
        kind, amount = q.spec.reward
        if kind == "gold":
            assert run.gold == gold + amount
        elif kind == "reroll":
            assert run.inventory.rerolls == rerolls + amount
        elif kind == "samples":
            assert run.inventory.sample_count(sample_key) == samples + amount
        elif kind == "neonsaft_gold":
            assert run.gold == gold + amount and len(run.pickups) == pickups + 1
        else:
            assert len(run.pickups) == pickups + 1
        restored = Quest.from_data(q.to_data())
        assert restored is not None and restored.reward_paid and restored.progress == q.progress


def _giver_of(run):
    spec = run.quest.spec
    return next(c for c in run.enemies.creatures if c.species == spec.giver and c.giver)


def test_d23_quest_giver_and_interaction_in_run() -> None:
    from src.run import Run
    from src.universes.catalog import UNIVERSES

    for u_key in [u.key for u in UNIVERSES.values()]:
        run = Run(seed=23, universe_key=u_key)
        assert run.quest is not None and run.quest.spec.universe == u_key
        assert _giver_of(run) is not None

    run = Run(seed=23, universe_key="aktenhalde")
    giver = _giver_of(run)
    run.player.place(int(giver.x), int(giver.y))
    assert run.try_interact_creature()
    assert run.quest.accepted
    run.quest.progress = run.quest.spec.goal
    gold = run.gold
    assert run.try_interact_creature()
    assert run.gold == gold + 150


def test_d24_quest_fleischwelt_gallstones() -> None:
    from src.run import Run

    run = Run(seed=24, universe_key="fleischwelt")
    q = run.quest
    q.accept(run)
    run.inventory.add_sample("probe_gallenstein", 3)
    q.tick(0.1, run)
    assert q.progress == 3
    before = len(run.pickups)
    assert q.turn_in(run)
    assert run.inventory.sample_count("probe_gallenstein") == 0
    assert any(p.kind == "life_capsule" for p in run.pickups[before:])


def test_d25_quest_aktenhalde_forms() -> None:
    from src.challenges import quest_for
    from src.run import Run

    run = Run(seed=25, universe_key="aktenhalde")
    q = run.quest
    q.accept(run)
    forms = [p for p in run.pickups if p.kind == "form_stamp"]
    assert len(forms) == 6
    assert run._pick_up(forms[0])
    assert q.progress == 1
    for _ in range(4):
        q.on_event("form_stamped", {"x": 0.0, "y": 0.0}, run)
    assert q.progress == 5 and not q.failed

    late = quest_for("aktenhalde")
    late.accept(run)
    late.on_event("event_start", {"key": "pruefung", "name": "Prüfung"}, run)
    assert late.failed


def test_d26_quest_glibbria_cow_escort() -> None:
    from src.challenges import quest_for
    from src.run import Run

    run = Run(seed=26, universe_key="glibbria")
    assert run.level.quest_target is not None
    q = run.quest
    q.accept(run)
    cows = [c for c in run.enemies.creatures if c.species == "glibberkuh"]
    assert len(cows) == 1
    tx, ty = run.level.quest_target
    cows[0].place(int(tx) - 8, int(ty) - 6)
    q.tick(0.1, run)
    assert q.progress == 1

    lost = quest_for("glibbria")
    lost.accept(run)
    lost.on_event("kill", {"species": "glibberkuh", "x": 0.0, "y": 0.0, "killer": "world"}, run)
    assert lost.failed


def test_d27_quest_kruemelreich_aphids() -> None:
    from src.materials import MAT_ID
    from src.run import Run

    run = Run(seed=27, universe_key="kruemelreich")
    run.enemies.creatures.clear()
    q = run.quest
    q.accept(run)
    laus = run.enemies.spawn("blattlaus", run.player.x + 60.0, run.player.y)
    cx, cy = int(laus.x) + 2, int(laus.y) - 2
    run.world.set_cell(cx, cy, MAT_ID["zucker"], force=True)
    q.tick(1.0, run)
    assert q.progress == 1
    assert run.world.get(cx, cy) != MAT_ID["zucker"]

    run.enemies.spawn("ameisenkrieger", run.player.x + 12.0, run.player.y)
    q.tick(1.0, run)
    assert q.failed


def test_d28_quest_sporenklub_dance() -> None:
    from src.run import Run

    run = Run(seed=28, universe_key="sporenklub")
    q = run.quest
    q.accept(run)
    for _ in range(4):
        q.on_event("jump", {"x": 0.0, "y": 0.0, "on_beat": True}, run)
    q.on_event("jump", {"x": 0.0, "y": 0.0, "on_beat": False}, run)
    assert q.progress == 0
    for _ in range(5):
        q.on_event("jump", {"x": 0.0, "y": 0.0, "on_beat": True}, run)
    assert q.progress >= 5


def test_d29_quest_abtei_bell() -> None:
    from src.challenges import quest_for
    from src.run import Run

    run = Run(seed=29, universe_key="abtei")
    q = run.quest
    q.accept(run)
    for _ in range(3):
        q.on_event("bell_rung", {"x": 0.0, "y": 0.0}, run)
    assert q.progress == 3 and not q.failed

    woken = quest_for("abtei")
    woken.accept(run)
    woken.on_event("creature_woke", {"species": "kirchenkrake"}, run)
    assert woken.failed
