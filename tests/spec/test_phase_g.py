from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def test_g01_hud_gold_stars_samples_and_banners() -> None:
    from src.rendering import Renderer
    from src.run import Run

    surf = pygame.Surface((640, 360))
    run = Run(seed=1)
    run.gold = 77
    run.wanted.add(3.0, "Test")
    Renderer(surf).draw(run)


def test_g02_hud_speech_bubbles_and_boss_banner() -> None:
    from src.hud import SpeechBubble, draw_boss_banner, draw_speech_bubbles
    from src.run import Run

    surf = pygame.Surface((640, 360))
    font = pygame.font.SysFont("consolas", 14)
    run = Run(seed=2)
    run.bubbles.append(SpeechBubble("Klonita", "Vorsicht!", run.player.x, run.player.y))
    run.boss_banner = ("Das Weltenherz — Phase 2", 2.5)

    draw_speech_bubbles(surf, font, run.bubbles, 0.0, 0.0)
    draw_boss_banner(surf, font, run.boss_banner)


def test_g03_hover_inspection_for_samples_stations_and_stances() -> None:
    from src.hover import describe_pickup, inspect_world
    from src.loot import Pickup
    from src.run import Run

    p = Pickup(10.0, 10.0, kind="sample", item_key="probe_gallenstein", amount=2)
    info = describe_pickup(p)
    assert len(info.title) > 0

    run = Run(seed=3)
    run.enter_workshop()
    assert run.workshop_layout is not None
    st = (
        run.workshop_layout.stations.get("ws_fabrikator")
        or run.workshop_layout.stations["ws_fabricator"]
    )
    cx = (st.rect[0] + st.rect[2]) // 2
    cy = (st.rect[1] + st.rect[3]) // 2
    st_info = inspect_world(
        run.world,
        cx,
        cy,
        run.player,
        run.enemies.creatures,
        run.pickups,
        workshop_layout=run.workshop_layout,
    )
    assert "Fabrikator" in st_info.title


def test_g04_records_discover_and_ranks() -> None:
    from src.records import Records, compute_score, rank_for_score

    rec = Records()
    rec.discover("block", "funke")
    rec.discover("blueprint", "nadel")
    rec.discover("universe", "sporenklub")
    rec.discover("evil_self", "boese_kaiserin")
    rec.discover("badge", "dienstausweis")
    rec.discover("ending", "boese")
    rec.discover("creature", "fleischmade")

    assert "funke" in rec.blocks
    assert "nadel" in rec.blueprints
    assert "sporenklub" in rec.universes
    assert "boese_kaiserin" in rec.evil_selves
    assert rec.badges == 1
    assert rec.endings == ["boese"]
    assert rec.creatures["fleischmade"] == 1
    assert "sporenklub" not in rec.creatures

    score = compute_score(
        depth=5,
        kills=40,
        gold=300,
        samples_collected=15,
        challenges_won=3,
        bosses_killed=5,
        victory=True,
        true_ending=True,
    )
    assert rank_for_score(score) == "Realitäts-Rebellin"


def test_g05_archive_menu_5_tabs() -> None:
    from src.menus import draw_archive_menu
    from src.records import Records

    surf = pygame.Surface((640, 360))
    font = pygame.font.SysFont("consolas", 16)
    small_font = pygame.font.SysFont("consolas", 12)
    rec = Records()
    rec.discover("universe", "fleischwelt")
    for tab_idx in range(5):
        draw_archive_menu(surf, font, small_font, rec, tab_idx)


def test_g06_victory_and_game_over_score_summary() -> None:
    from src.run import Run

    run = Run(seed=6)
    run.victory = True
    run.true_ending = True
    assert run.final_score() > 0
    assert isinstance(run.final_rank(), str)


def test_g07_save_load_run_and_level_fields() -> None:
    from src.run import Run

    run = Run(seed=7, universe_key="kruemelreich")
    run.gold = 145
    run.badges = 2
    run.inventory.add_sample("probe_zuckerkristall", 7)

    saved = run.save_state()
    run2 = Run(seed=1)
    run2.restore(saved)

    assert run2.gold == 145
    assert run2.badges == 2
    assert run2.inventory.sample_count("probe_zuckerkristall") == 7
    assert run2.level.universe_key == "kruemelreich"


def test_g08_save_load_wanted_klonita_and_status_timers() -> None:
    from src.run import Run

    run = Run(seed=8, universe_key="aktenhalde")
    run.wanted.add(2.5, "Sachbeschädigung")
    run.player.body.stamped_good = 15.0
    run.klonita.toggle()

    saved = run.save_state()
    run2 = Run(seed=1)
    run2.restore(saved)

    assert run2.wanted.stars == 2
    assert run2.player.body.stamped_good >= 14.0
    assert run2.klonita.state == "dismissed"


def test_g09_menu_keyboard_navigation() -> None:
    from src.run import Run

    run = Run(seed=9)
    for mode in ("portal_select", "fabricator", "trader", "empress_bargain", "archive"):
        run.menu_mode = mode
        assert run.handle_menu_input(pygame.K_ESCAPE) is True
        assert run.menu_mode == ""


def test_g10_full_acceptance_bot_across_all_6_mvp_universes() -> None:
    from src.bot import run_bot
    from src.universes.catalog import UNIVERSES

    assert len(UNIVERSES) == 6
    for u in UNIVERSES.values():
        rep = run_bot(u.key, seed=42, max_seconds=8.0)
        assert rep.errors == [], f"Errors in {u.key}: {rep.errors}"
        assert rep.stuck_ratio < 0.85, f"Bot stuck in {u.key}: {rep.stuck_ratio}"


# ---------------------------------------------------------------------------
# G11–G13 — Anzeigenamen der Module nach Bibel 06 (V0e). Schlüssel = heutiger Code-Schlüssel.
# ---------------------------------------------------------------------------
FORM_NAMES = {
    "funke": (
        "Flux-Funke",
        "Schneller Funke, kleine Explosion. Das Brot und Butter jeder Wissenschaftlerin.",
    ),
    "nadel": ("Nadelschuss", "Sehr schnell, kratzt kaum an Wänden."),
    "gallenblase": ("Hüpfgranate", "Prallt ab und platzt nach kurzer Zeit gewaltig."),
    "klumpen": ("Matschbatzen", "Fliegt im Bogen und zerplatzt zu einer Pfütze (Wasser)."),
    "knochensplitter": ("Schrotladung", "Fünf Kugeln auf kurze Distanz."),
    "zahnbohrer": ("Bohrkopf", "Frisst sich ein Stück weit durch Weiches und Hartes."),
    "blutegel": ("Lebenssauger", "Langsam; heilt dich um die Hälfte seines Schadens."),
    "teleportbolzen": ("Sprungbolzen (L15)", "Wo er einschlägt, reißt er dich hin."),
    "knochensaege": ("Kreissäge", "Prallt oft ab und schneidet durch alles Lebendige."),
    "sporenmine": ("Haftmine", "Bleibt liegen und platzt, wenn etwas naht."),
    "fressgeschwuer": ("Tunnelfresser (L6)", "Träge Kugel, frisst einen breiten Gang."),
    "knochenspeer": ("Durchschlagbolzen", "Spießt alles in seiner Bahn auf."),
    "mikrofunke": ("Mikrofunke", "Winzig, billig, schnell."),
    "feuerball": ("Feuerball", "Glühender Klumpen, brennende Explosion."),
    "knochenbombe": ("Kraterbombe (L8)", "Prallt einmal ab, dann ein riesiger Krater."),
    "nadelregen": ("Nadelregen", "Acht Nadeln auf einmal."),
    "schleimkugel": ("Klebekugel", "Macht Gegner klebrig, löscht Brände."),
    "nervenstrom": ("Stromstoß", "Ein Blitz; in Wasser und Metall läuft er weiter."),
    "wandlungsdruese": ("Wandelstrahl (L5)", "Wen er trifft, der wird zu etwas anderem."),
    "tauschdruese": ("Tauschstrahl (L15)", "Du tauschst den Platz mit dem Getroffenen."),
    "kettenfunke": ("Kettenblitz", "Springt auf bis zu drei weitere Kreaturen."),
    "leuchtkugel": ("Leuchtfackel", "Schwebt lange und erhellt die Dunkelheit."),
    "zahnrad": ("Mahlwerk", "Ein Zahnrad, das lange durch Wände mahlt."),
    "gelenkkugel": ("Flummi", "Prallt immer wieder ab."),
}

MODIFIER_NAMES = {
    "beschleunigung": ("Turbo", "Nächstes Geschoss fliegt schneller."),
    "beschleunigung_stark": ("Überturbo", "Zweieinhalbmal so schnell. Hält nicht lange."),
    "sprengkraft": ("Sprengladung", "Größere Explosion."),
    "sprengkern": ("Taschen-Atomkern", "Viel größere Explosion. Nicht schütteln."),
    "umkehr": ("Antigrav", "Nächstes Geschoss fällt nach oben."),
    "schwerelos": ("Schwebefeld", "Nächstes Geschoss fällt gar nicht."),
    "schwere_ladung": ("Bleimantel", "Mehr Schaden, aber langsamer."),
    "zielsuche": ("Zielsuchkopf", "Lenkt zum Mauszeiger."),
    "doppel": ("Doppellauf", "Zwei Gruppen auf einmal."),
    "dreifach": ("Dreifachlauf", "Drei Gruppen auf einmal."),
    "achterkreis": ("Rundumschlag (L15)", "Acht Gruppen im Kreis um dich."),
    "faecher": ("Fächerdüse", "Fünf Gruppen, weit aufgefächert."),
    "vorne_hinten": ("Rückspiegel", "Eine Gruppe nach vorn, eine nach hinten."),
    "durchbohren": ("Panzerbrechend", "Fliegt durch Kreaturen hindurch."),
    "abprall": ("Gummierung", "Prallt dreimal von Wänden ab."),
    "brandbeschleuniger": ("Brandsatz", "Getroffene fangen Feuer."),
    "langlebigkeit": ("Langstrecke", "Fliegt doppelt so lange, aber langsamer."),
    "kurzlebig": ("Kurzstrecke", "Vergeht nach halber Zeit, dafür schneller schießen."),
    "giftzahn": ("Wucht", "Trifft deutlich härter."),
    "blutpreis": ("Fluxpumpe", "Gibt 60 Flux, kostet eine längere Pause."),
    "dauerladung": ("Schnelllader", "Lädt nach diesem Durchgang fast sofort."),
    "hast": ("Abzugsfeder", "Kürzere Pause bis zum nächsten Schuss."),
}

TRIGGER_NAMES = {
    "nerv_aufprall": ("Aufschlagzünder", "Setzt die nächste Gruppe beim Aufprall frei."),
    "nerv_zeit": ("Zeitzünder", "Nach kurzer Zeit."),
    "nerv_ende": ("Endzünder", "Am Ende des Flugs."),
    "nerv_naesse": ("Nässezünder", "Sobald das Geschoss in Flüssigkeit eintaucht."),
}


def _check_names(table: dict[str, tuple[str, str]]) -> None:
    from src.spells import BLOCKS

    for key, (name, description) in table.items():
        block = BLOCKS[key]
        assert block.key == key
        assert block.name_de == name, key
        assert block.description_de == description, key


def test_g11_form_names() -> None:
    _check_names(FORM_NAMES)


def test_g12_modifier_names() -> None:
    _check_names(MODIFIER_NAMES)


def test_g13_trigger_and_payload_names() -> None:
    from src.spells import BLOCKS

    _check_names(TRIGGER_NAMES)
    assert BLOCKS["sekret_feuer"].name_de == "Feuerfüllung"
    assert BLOCKS["sekret_rauch"].name_de == "Rauchfüllung"


def test_g14_multiverse_run_starts_in_workshop_and_portal_keys() -> None:
    from src.run import Controls, Run
    from src.workshop import STATIONS

    run = Run(seed=14)
    run.start_multiverse_run()
    assert run.in_workshop is True
    assert run.plan.slot == 0
    offers = run.plan.offers()
    assert len(offers) == 2

    x0, y0, x1, y1 = STATIONS["ws_portal"].rect
    run.player.x, run.player.y = (x0 + x1) / 2, (y0 + y1) / 2
    run.update(0.016, Controls(pickup=True))
    assert run.menu_mode == "portal_select"
    assert run.handle_menu_input(pygame.K_ESCAPE) is True
    assert run.menu_mode == "" and run.in_workshop is True
    assert run.handle_menu_input(pygame.K_RETURN) is False  # no menu open

    run.menu_mode = "portal_select"
    assert run.handle_menu_input(pygame.K_DOWN) is True
    assert run.handle_menu_input(pygame.K_RETURN) is True
    assert run.in_workshop is False and run.menu_mode == ""
    assert run.universe_key == offers[1].universe

    # free slot: the anchor point is open and leads back to the workshop (bible 02)
    assert run.exit_open is True
    ex, ey = run.level.exit
    run.player.x = ex - run.player.width // 2
    run.player.y = ey - run.player.height // 2
    run.update(0.016, Controls())
    assert run.in_workshop is True and run.in_sanctum is False
    assert run.plan.slot == 1 and len(run.plan.offers()) >= 1


def test_g15_game_loop_workshop_and_portal_menu(monkeypatch) -> None:
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from src import main as game_main

    # never touch the player's real save files
    monkeypatch.setattr(game_main.records, "delete_run", lambda *a, **k: None)
    monkeypatch.setattr(game_main.records, "save_run", lambda *a, **k: None)

    game = game_main.Game()
    game._start_run()
    assert game.state == "playing" and game.run.in_workshop is True

    game.run.menu_mode = "portal_select"
    game._on_key(pygame.K_ESCAPE)
    assert game.run.menu_mode == "" and game.state == "playing"

    offers = game.run.plan.offers()
    game.run.menu_mode = "portal_select"
    hp = game.run.player.body.hp
    game.update(0.5)  # an open menu pauses the run
    assert game.run.player.body.hp == hp
    game.draw()
    game._on_key(pygame.K_RETURN)
    assert game.run.in_workshop is False
    assert game.run.universe_key == offers[0].universe
    game.update(0.016)
    game.draw()

def test_g16_universe_entry_end_to_end() -> None:
    """Workshop -> universe -> workshop as the game does it, checked like a playtest."""
    from src import materials as mat
    from src.run import Controls, Run
    from src.universes.catalog import ALL_UNIVERSES

    run = Run(seed=16)
    run.start_multiverse_run()
    for key in ("aktenhalde", "fleischwelt", "abtei"):
        u = ALL_UNIVERSES[key]
        run.enter_universe(u)
        assert run.in_workshop is False
        # the native core must simulate the same material table Python uses
        assert mat.ACTIVE is not None and mat.ACTIVE.key.split("+")[0] == u.material_set
        core_set = run.world.material_set
        assert core_set == mat.ACTIVE.key, f"{key}: core runs {core_set}, Python {mat.ACTIVE.key}"
        assert run.level.universe_key == key
        assert run.depth.name_de == u.name_de
        species = {c.species for c in run.enemies.creatures}
        assert species & set(u.natives), f"{key}: none of its natives {u.natives} spawned"
        assert u.mid_boss in species, f"{key}: mid-boss {u.mid_boss} missing"
        for _ in range(60):  # a second of play must not crash
            run.update(0.016, Controls())
        run.enter_workshop()
        assert run.in_workshop is True
        for _ in range(30):
            run.update(0.016, Controls())

    # paper burns in the Aktenhalde (fire spreads through the native core)
    run.enter_universe(ALL_UNIVERSES["aktenhalde"])
    w = run.world
    paper = mat.MAT_ID["papier"]
    x0, y0, size = 60, 60, 24
    w.fill_rect(x0, y0, x0 + size, y0 + size, paper)
    w.wake_all()

    def paper_left() -> int:
        return sum(
            w.get(x, y) == paper for y in range(y0, y0 + size) for x in range(x0, x0 + size)
        )

    before = paper_left()
    w.ignite(x0 + size // 2, y0 + size // 2)
    for _ in range(300):
        w.step()
    assert paper_left() < before * 0.8, "fire did not burn the paper"

def test_g17_universes_are_playable_and_visible() -> None:
    """First-playtest regressions: no trapped start, no invisible creatures."""
    from src.enemies import SPECIES
    from src.materials import BLOCKS_BODY, KIND, LIQUID
    from src.native import byte_view, reachable
    from src.player import PLAYER_HEIGHT, PLAYER_WIDTH
    from src.procbody import RIG_LAYOUTS
    from src.run import Run
    from src.sprite_render import ASSET_ROOT
    from src.universes.catalog import ALL_UNIVERSES

    box = (PLAYER_WIDTH + 2, PLAYER_HEIGHT + 2)
    for seed in (1, 2, 3):
        run = Run(seed=seed)
        run.start_multiverse_run()
        for u in ALL_UNIVERSES.values():
            run.enter_universe(u)
            w, level = run.world, run.level
            blocking = [int(b or k == LIQUID) for b, k in zip(BLOCKS_BODY, KIND, strict=False)]
            goal = (level.exit[0] - PLAYER_WIDTH // 2, level.exit[1] - PLAYER_HEIGHT // 2)
            found, _ = reachable(
                byte_view(w.grid), w.width, w.height, blocking, box,
                (level.spawn[0] - 1, level.spawn[1] - 2), goal,
            )  # fmt: skip
            assert found, f"{u.key} seed {seed}: the anchor point cannot be reached from the start"

    # every creature a universe spawns has its sprite sheets on disk (otherwise it is drawn
    # as a placeholder box)
    keys = set()
    for u in ALL_UNIVERSES.values():
        keys.update(u.natives)
        keys.update(k for k in (u.big, u.mid_boss, u.boss) if k)
    for key in sorted(keys):
        assert key in SPECIES, f"{key} is spawned but not registered"
        if key in RIG_LAYOUTS:
            names = {part.sheet_name for part in RIG_LAYOUTS[key].parts}
            for name in names:
                assert any(
                    (ASSET_ROOT / cat / f"{name}.png").is_file() for cat in ("bosse", "kreaturen")
                ), f"rig sheet {name} for {key} missing"
        else:
            assert any(
                (ASSET_ROOT / cat / f"{key}.png").is_file()
                for cat in ("kreaturen", "bosse", "charaktere")
            ), f"sheet for {key} missing"

def test_g18_new_pickup_kinds_have_labels_and_tooltips() -> None:
    """Playtest crash: hovering over gold dropped by a creature raised KeyError ''."""
    from src.hover import describe_pickup
    from src.loot import Pickup

    for item in (
        Pickup(0, 0, kind="gold", amount=5),
        Pickup(0, 0, kind="sample", item_key="probe_stempelkissen", amount=1),
        Pickup(0, 0, kind="life_capsule", amount=10),
        Pickup(0, 0, kind="blueprint_shard"),
    ):
        assert item.label_de
        assert describe_pickup(item).title

def test_g20_aktenhalde_firebreaks() -> None:
    """Playtest: one fire burnt the whole Aktenhalde. Paper must come in sections."""
    from src import materials as mat
    from src.run import FIREBREAK_CELL, Run
    from src.universes.catalog import ALL_UNIVERSES

    run = Run(seed=20)
    run.start_multiverse_run()
    run.enter_universe(ALL_UNIVERSES["aktenhalde"])
    w = run.world
    paper = mat.MAT_ID["papier"]
    step = 2
    gw, gh = w.width // step, w.height // step
    seen = bytearray(gw * gh)
    for start in range(gw * gh):
        if seen[start] or w.get((start % gw) * step, (start // gw) * step) != paper:
            continue
        seen[start] = 1
        stack, x0, x1, y0, y1 = [start], gw, 0, gh, 0
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
        assert width <= FIREBREAK_CELL[0] + step and height <= FIREBREAK_CELL[1] + step, (
            f"paper section {width}x{height} has no firebreak"
        )

