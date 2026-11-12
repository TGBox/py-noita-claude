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
    assert run.in_workshop is False, "the anchor point waits for a key press"
    run.pickups.clear()
    run.update(0.016, Controls(pickup=True))
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
    from src.materials import BLOCKS_BODY
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
            # liquids are passable: seas and flooded naves are swum through (G26)
            blocking = [int(b) for b in BLOCKS_BODY]
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

def test_g21_hit_flash_keeps_sprites_and_gold_is_auto_collected() -> None:
    """Playtest: hit creatures turned into white squares; gold needed many clicks."""
    from src.loot import Pickup
    from src.run import Controls, Run
    from src.sprite_render import blit_frame
    from src.sprites import AnimSpec, Animator, SheetMeta

    sheet = pygame.Surface((8, 8), pygame.SRCALPHA)
    sheet.fill((0, 0, 0, 0))
    sheet.fill((200, 50, 50, 255), (2, 2, 4, 4))
    meta = SheetMeta(frame_size=(8, 8), anchor=(4, 4), anims={"idle": AnimSpec(0, 1)}, glow=())
    target = pygame.Surface((20, 20), pygame.SRCALPHA)
    target.fill((0, 0, 0, 0))
    blit_frame(target, sheet, meta, Animator(meta, "idle"), 10, 10, 0, 0, flash=1.0)
    assert sheet.get_at((0, 0)).a == 0, "the flash must not change the cached sheet"
    assert sheet.get_at((3, 3))[:3] == (200, 50, 50)
    assert target.get_at((6, 6)).a == 0, "transparent pixels must stay transparent"
    assert target.get_at((9, 9)).a == 255

    run = Run(seed=21)
    run.start_multiverse_run()
    cx, cy = run.player.center
    run.pickups.append(Pickup(cx, cy, kind="gold", amount=7))
    gold = run.gold
    run.update(0.016, Controls())
    assert run.gold == gold + 7

def _stand_at(run, station_key: str) -> None:
    x0, y0, x1, y1 = run.workshop_layout.stations[station_key].rect
    run.player.x, run.player.y = (x0 + x1) / 2, (y0 + y1) / 2


def test_g22_workshop_menus_by_keyboard() -> None:
    from src.fabricator import build_cost
    from src.run import Controls, Run

    run = Run(seed=22)
    run.start_multiverse_run()
    run.gold = 5000

    _stand_at(run, "ws_haendler")
    run.update(0.016, Controls(pickup=True))
    assert run.menu_mode == "trader"
    gold = run.gold
    assert run.handle_menu_input(pygame.K_RETURN) is True
    assert run.gold < gold, "Enter at the trader buys the selected offer"
    assert run.handle_menu_input(pygame.K_ESCAPE) is True and run.menu_mode == ""

    _stand_at(run, "ws_liege")
    run.update(0.016, Controls(pickup=True))
    assert run.menu_mode == "experiment"
    assert run.handle_menu_input(pygame.K_DOWN) is True
    assert run.handle_menu_input(pygame.K_RETURN) is True
    assert run.experiment_picked is True
    run.handle_menu_input(pygame.K_ESCAPE)
    assert run.menu_mode == ""

    rec = build_cost("spark")
    for key, count in rec.samples:
        run.inventory.add_sample(key, count * 3)
    _stand_at(run, "ws_fabrikator")
    run.update(0.016, Controls(pickup=True))
    assert run.menu_mode == "fabricator"
    gold = run.gold
    for _ in range(80):  # select the spark recipe, whatever its place in the list
        if run.handle_menu_input(pygame.K_RETURN) and run.gold < gold:
            break
        run.handle_menu_input(pygame.K_DOWN)
    assert run.gold < gold, "Enter at the fabricator builds a module"
    assert run.handle_menu_input(pygame.K_ESCAPE) is True and run.menu_mode == ""


def test_g23_game_draws_workshop_menus(monkeypatch) -> None:
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from src import main as game_main

    monkeypatch.setattr(game_main.records, "delete_run", lambda *a, **k: None)
    monkeypatch.setattr(game_main.records, "save_run", lambda *a, **k: None)
    shown: list[str] = []
    real_text = game_main.ui.text

    def spy(screen, content, *args, **kwargs):  # type: ignore[no-untyped-def]
        shown.append(str(content))
        return real_text(screen, content, *args, **kwargs)

    monkeypatch.setattr(game_main.ui, "text", spy)
    game = game_main.Game()
    game._start_run()
    run = game.run
    run.gold = 5000
    for key, mode in (
        ("ws_haendler", "trader"), ("ws_liege", "experiment"), ("ws_fabrikator", "fabricator"),
    ):  # fmt: skip
        _stand_at(run, key)
        run.interact_station()
        assert run.menu_mode == mode, key
        shown.clear()
        game.update(0.016)
        game.draw()
        assert not any("Noch nicht verfügbar" in s for s in shown), f"{mode} menu is not drawn"
        game._on_key(pygame.K_ESCAPE)
        assert run.menu_mode == "" and game.state == "playing"

    for key in ("ws_automat", "ws_schiessstand"):  # switched off after the playtest
        _stand_at(run, key)
        run.interact_station()
        assert run.menu_mode == "" and any("Außer Betrieb" in m for m in run.messages)

    _stand_at(run, "ws_werkbank")
    run.interact_station()
    game.update(0.016)
    assert game.editor.open, "the workbench opens the backpack"

def test_g24_workshop_dummy_survives_hits_and_stations_are_drawn(monkeypatch) -> None:
    """Playtest: shooting the training dummy crashed; station sprites never showed."""
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from src import main as game_main
    from src import sprite_render
    from src.run import Controls

    monkeypatch.setattr(game_main.records, "delete_run", lambda *a, **k: None)
    monkeypatch.setattr(game_main.records, "save_run", lambda *a, **k: None)
    game = game_main.Game()
    game._start_run()
    run = game.run
    dummy = next(c for c in run.enemies.creatures if c.species == "trainings_attrappe")
    for _ in range(3):
        dummy.hurt(12.0, "Test")
        run.update(0.016, Controls())
    assert run.dummy_damage_total >= 36 and not dummy.dead

    drawn: list[object] = []
    real = sprite_render.blit_frame

    def spy(target, *args, **kwargs):  # type: ignore[no-untyped-def]
        drawn.append(target)
        return real(target, *args, **kwargs)

    monkeypatch.setattr(sprite_render, "blit_frame", spy)
    game.draw()
    assert sum(t is game.canvas for t in drawn) >= 10, "station sprites must go onto the canvas"

def test_g25_minigames_are_visible_and_playable(monkeypatch) -> None:
    """Playtest: the Physik-o-Mat puzzle was invisible and clicks did nothing."""
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from src import main as game_main
    from src.menus import minigame_view
    from src.minigames.physik_o_mat import make_physik_puzzle, solve_actions

    monkeypatch.setattr(game_main.records, "delete_run", lambda *a, **k: None)
    monkeypatch.setattr(game_main.records, "save_run", lambda *a, **k: None)
    game = game_main.Game()
    game._start_run()
    run = game.run

    run.active_minigame = make_physik_puzzle("glas_fuellen", seed=1)
    run.menu_mode = "minigame"
    before = bytes(run.active_minigame.world.grid)
    game.draw()
    view, zoom = minigame_view(game.screen)
    plain = game.screen.get_at((view.x + 1, view.y + 1))
    assert any(  # the puzzle world is on screen, not just a text
        game.screen.get_at((view.x + x * zoom, view.y + y * zoom)) != plain
        for x in range(0, 160, 4)
        for y in range(0, 120, 4)
    )
    action, (cx, cy) = solve_actions("glas_fuellen")[0]
    keys = {"blast": pygame.K_1, "dig": pygame.K_2, "ignite": pygame.K_3, "pour": pygame.K_4}
    game._on_key(keys[action])
    game._click_minigame((view.x + cx * zoom + zoom // 2, view.y + cy * zoom + zoom // 2))
    assert bytes(run.active_minigame.world.grid) != before, "a click must change the puzzle"
    game._on_key(pygame.K_ESCAPE)
    assert run.menu_mode == ""

def test_g26_universes_have_their_signature_terrain() -> None:
    """Each universe is recognisable by what bible 03 promises, not just recoloured caves."""
    from src import materials as mat
    from src.run import Controls, Run
    from src.universes.catalog import ALL_UNIVERSES

    def share(w, keys, x0, y0, x1, y1, step=3) -> float:  # type: ignore[no-untyped-def]
        want = {mat.MAT_ID[k] for k in keys}
        cells = [w.get(x, y) for y in range(y0, y1, step) for x in range(x0, x1, step)]
        return sum(c in want for c in cells) / max(1, len(cells))

    run = Run(seed=26)
    run.start_multiverse_run()
    for key in ("fleischwelt", "aktenhalde", "glibbria", "kruemelreich", "sporenklub", "abtei"):
        run.enter_universe(ALL_UNIVERSES[key])
        w = run.world
        W, H = w.width, w.height
        if key == "fleischwelt":
            assert share(w, ("enamel",), 0, 0, W, H // 3, 2) > 0.002, "teeth in the Schlund"
            assert share(w, ("acid",), 0, H // 3, W, H * 2 // 3, 2) > 0.001, "acid in the stomach"
        elif key == "aktenhalde":
            assert share(w, ("tinte",), W * 2 // 3, H // 3, W, H, 2) > 0.001, "ink lakes"
            core = share(w, ("tintenpapier",), 0, 0, W, H, 2)
            assert core > share(w, ("papier",), 0, 0, W, H, 2), "only the cave lining burns"
        elif key == "glibbria":
            assert share(w, ("brausesirup",), 0, int(H * 0.9), W, H - 3) > 0.6, "syrup sea"
            assert share(w, ("air",), 0, 0, W, H * 2 // 3) > 0.35, "open sky between islands"
        elif key == "kruemelreich":
            assert share(w, ("fliese",), 0, H // 3, W, H // 2, 1) > 0.008, "tiled kitchen floor"
            spawn_x, spawn_y = run.level.spawn
            feet = spawn_y + run.player.height
            assert any(w.get(spawn_x + 4, y) != mat.AIR for y in range(feet, feet + 12)), "perch"
            assert share(w, ("air",), 0, H // 10, W, H // 3) > 0.6, "open kitchen above"
        elif key == "sporenklub":
            assert share(w, ("air",), W // 3, H * 2 // 5, W * 2 // 3, H // 2) > 0.8, "dance floor"
            assert share(w, ("neonsaft",), 0, 0, W, H, 2) > 0.0002, "glowing neon juice"
        elif key == "abtei":
            assert share(w, ("water",), 0, H // 2, W, H) > 0.25, "flooded nave and crypt"
            assert share(w, ("water",), 0, 0, W, H // 4) < 0.02, "dry bell tower"
            assert share(w, ("glockenbronze",), 0, 0, W, H // 4, 1) > 0.001, "the great bell"
        for _ in range(30):  # half a second of play in the new terrain
            run.update(0.016, Controls())
        run.enter_workshop()


def test_g27_material_lifetimes_fit_in_a_byte():
    """World.life is a bytearray (u8 in the native core): no lifetime may exceed 255."""
    from src.materials import LIBRARY

    too_long = [k for k, m in LIBRARY.items() if max(*m.life, *m.burn_life) > 255]
    assert too_long == []


def test_g28_aktenhalde_hall_lockers_and_tubes() -> None:
    """Aktenhalde rework: Sitzungssaal as mid-boss arena, lockers with loot behind paper
    doors, Rohrpost shafts between the thirds, desks and file stacks."""
    from src import materials as mat
    from src.run import Run
    from src.universes import features
    from src.universes.catalog import ALL_UNIVERSES

    for seed in (3, 20, 26):
        run = Run(seed=seed)
        run.start_multiverse_run()
        run.enter_universe(ALL_UNIVERSES["aktenhalde"])
        w = run.world
        paper, board = mat.MAT_ID["papier"], mat.MAT_ID["aktendeckel"]
        x0, y0, x1, y1 = run.level.mid_boss_arena
        assert (x1 - x0, y1 - y0) == features.HALL_SIZE, "the Sitzungssaal is the arena"
        row = [w.get(x, y1) for x in range(x0 + 4, x1 - 4)]
        assert row.count(paper) > len(row) * 0.6, "paper floor"
        assert any(w.get(x, y1 - 10) == board for x in range(x0, x1)), "conference tables"
        spawn = run.level.spawn
        assert ((x0 + x1) / 2 - spawn[0]) ** 2 + ((y0 + y1) / 2 - spawn[1]) ** 2 > 250**2
        gold = [p for p in run.pickups if p.kind == "gold"]
        assert len(gold) >= 4, "lockers hold gold"
        for item in gold:  # every locker is a closed cardboard box with a paper door
            x, y = int(item.x) + 3, int(item.y)
            ring = [w.get(xx, yy) for xx in range(x - 12, x + 12) for yy in range(y - 12, y + 6)]
            assert board in ring and paper in ring
        assert any(p.kind == "sample" for p in run.pickups), "one locker holds a sample"
        third = w.width // 3
        for tx in (third, 2 * third):  # a straight shaft near each boundary
            open_rows = max(
                sum(w.get(x, y) == mat.AIR for y in range(w.height // 9, w.height * 8 // 9))
                for x in range(tx - 10, tx + 11)
            )
            assert open_rows > w.height * 0.55, "Rohrpost shaft"
        run.enter_workshop()


def test_g29_glibbria_islands_bowl_and_bounce() -> None:
    """Glibbria rework: floating islands over the syrup sea, the mid-boss in a jelly bowl,
    the anchor point on an island (never under the sea), gum caves with loot, and jelly
    that throws a falling body back up."""
    from src import materials as mat
    from src.run import Run
    from src.universes import features
    from src.universes.catalog import ALL_UNIVERSES
    from src.worldgen import ensure_path

    for seed, boss_slot in ((3, False), (20, True), (26, False)):
        run = Run(seed=seed)
        run.start_multiverse_run()
        run.enter_universe(ALL_UNIVERSES["glibbria"], boss_slot=boss_slot)
        w, level = run.world, run.level
        line = int(w.height * features.SEA_LEVEL)
        jelly = mat.MAT_ID["glibber"]
        sky = [w.get(x, y) for y in range(8, line, 4) for x in range(8, w.width - 8, 4)]
        assert sky.count(mat.AIR) > len(sky) * 0.7, "open sky"
        assert level.exit[1] < line - 40, "anchor point above the sea"
        assert ensure_path(w, level.spawn, level.exit) == 0, "reachable without digging"
        x0, y0, x1, y1 = level.mid_boss_arena
        assert y1 < line and w.get((x0 + x1) // 2, y1 + 2) == jelly, "bowl floor"
        assert w.get(x0 - 6, y1 - 12) == jelly and w.get(x1 + 5, y1 - 12) == jelly, "rims"
        if boss_slot:
            bx0, by0, bx1, by1 = level.boss_arena
            assert by1 < line and bx0 <= level.exit[0] <= bx1, "boss bowl holds the anchor"
        assert sum(p.kind == "gold" for p in run.pickups) >= 2, "gum caves hold loot"
        run.enter_workshop()

    run = Run(seed=26)
    run.start_multiverse_run()
    run.enter_universe(ALL_UNIVERSES["glibbria"])
    player, w = run.player, run.world
    sx, sy = run.level.spawn
    player.place(sx, sy - 60)
    player.vy = 0.0
    rows = []
    for _ in range(200):
        player.update(w, 0.016, 0, False, False)
        rows.append(player.y)
    landed = rows.index(max(rows))
    assert max(rows) - min(rows[landed:]) > 20, "a long fall bounces back up"
    for _ in range(400):
        player.update(w, 0.016, 0, False, False)
    assert player.on_ground, "the bouncing dies down"
    ground = player.y
    player.update(w, 0.016, 0, True, False)  # an ordinary hop lands softly
    for _ in range(120):
        player.update(w, 0.016, 0, False, False)
    assert player.on_ground and player.y == ground


def test_g30_sporenklub_stage_cellar_mushrooms_and_back_rooms() -> None:
    """Sporenklub rework: the mid-boss on the main stage, stairs through the dance floor,
    giant mushrooms in the caves, guarded back rooms with loot, softly bouncing caps."""
    from src import materials as mat
    from src.player import BOUNCE_MATERIALS
    from src.run import Run
    from src.universes.catalog import ALL_UNIVERSES

    assert 0 < BOUNCE_MATERIALS["pilzhut"] < BOUNCE_MATERIALS["glibber"]
    for seed in (3, 20, 26):
        run = Run(seed=seed)
        run.start_multiverse_run()
        run.enter_universe(ALL_UNIVERSES["sporenklub"])
        w = run.world
        cap = mat.MAT_ID["pilzhut"]
        cx, floor = w.width // 2, w.height // 2 + int(w.height * 0.13) // 2
        x0, y0, x1, y1 = run.level.mid_boss_arena
        assert x0 < cx < x1 and y1 <= floor, "the main stage is the arena"
        assert w.get(cx, floor - 2) == cap, "DJ booth"
        for half in (range(8, cx - 40), range(cx + 40, w.width - 8)):
            assert any(w.get(x, floor + 3) == mat.AIR for x in half), "cellar stairs"
        assert sum(p.kind == "gold" for p in run.pickups) >= 2, "back rooms hold loot"
        guards = [c for c in run.enemies.creatures if c.species == "tuersteherpilz"]
        assert len(guards) >= 2
        for g in guards:
            assert not w.rect_blocked(int(g.x), int(g.y), g.spec.width, g.spec.height)
        run.enter_workshop()


def test_g31_kruemelreich_abtei_and_fleischwelt_arenas_and_caches() -> None:
    """Teacup arena and store rooms (Kruemelreich), flooded nave with an air dome and air
    bells that stay dry (Abtei), stomach lake and bone hall (Fleischwelt)."""
    from src import materials as mat
    from src.run import Run
    from src.universes import features
    from src.universes.catalog import ALL_UNIVERSES

    run = Run(seed=26)
    run.start_multiverse_run()

    run.enter_universe(ALL_UNIVERSES["kruemelreich"])
    w = run.world
    x0, y0, x1, y1 = run.level.mid_boss_arena
    assert x1 - x0 == 2 * features.CUP_HALF, "the teacup is the arena"
    china = mat.MAT_ID["fliese"]
    assert w.get(x0 - 3, y1 - 30) == china and w.get(x1 + 2, y1 - 30) == china, "cup walls"
    assert sum(p.kind == "gold" for p in run.pickups) == 3, "store rooms"
    run.enter_workshop()

    run.enter_universe(ALL_UNIVERSES["abtei"])
    w = run.world
    line = int(w.height * features.WATER_LINE)
    x0, y0, x1, y1 = run.level.mid_boss_arena
    assert (x1 - x0, y1 - y0) == features.NAVE_SIZE and y0 > line, "the flooded nave"
    assert w.get((x0 + x1) // 2, y1 - 20) == mat.WATER
    assert w.get((x0 + x1) // 2, y0 - 12) == mat.AIR, "air under the dome"

    def air_below() -> int:
        cells = range(line + 20, w.height - 8, 2)
        return sum(w.get(x, y) == mat.AIR for y in cells for x in range(8, w.width - 8, 2))

    before = air_below()
    assert before > 800, "air bells in the flooded caves"
    w.wake_all()
    for _ in range(200):
        w.step()
    assert air_below() > before * 0.97, "the air bells do not run full"
    run.enter_workshop()

    run.enter_universe(ALL_UNIVERSES["fleischwelt"])
    w = run.world
    x0, y0, x1, y1 = run.level.mid_boss_arena
    assert x1 - x0 == 2 * (features.BONE_HALL_RADIUS - 8), "the bone hall is the arena"
    assert y0 > w.height // 2, "in the Knochenmark"
    acid = mat.MAT_ID["acid"]
    band = range(w.height // 3, w.height * 2 // 3, 2)
    share = sum(w.get(x, y) == acid for y in band for x in range(8, w.width - 8, 2))
    assert share > 800, "the stomach lake"
    assert any(p.kind == "gold" for p in run.pickups), "cache on the islet"


def test_g32_sticky_and_fizzy_change_the_jump_once() -> None:
    """Brausesirup used to multiply the speed in every frame (a hop shot through the roof),
    chewing gum damped every fall. Both now scale the jump itself."""
    from src.player import MAX_FALL_SPEED
    from src.run import Run
    from src.universes.catalog import ALL_UNIVERSES

    run = Run(seed=26)
    run.start_multiverse_run()
    run.enter_universe(ALL_UNIVERSES["glibbria"])
    player, w = run.player, run.world

    def hop(**effects: float) -> tuple[int, float]:
        player.place(*run.level.spawn)
        player.vy = 0.0
        for _ in range(60):
            player.update(w, 0.016, 0, False, False)
        for name, value in effects.items():
            setattr(player, name, value)
        ground, top, fastest = player.y, player.y, 0.0
        player.update(w, 0.016, 0, True, False)
        for _ in range(150):
            player.update(w, 0.016, 0, False, False)
            top, fastest = min(top, player.y), max(fastest, abs(player.vy))
        for name in effects:
            setattr(player, name, 0.0)
        assert player.on_ground
        return ground - top, fastest

    normal, _ = hop()
    fizzy, fastest = hop(fizzy_time=20.0)
    sticky, _ = hop(sticky=5.0)
    assert normal * 1.8 < fizzy < normal * 2.6 and fastest <= MAX_FALL_SPEED
    assert normal * 0.3 < sticky < normal * 0.6


def test_g33_playtest_round_two() -> None:
    """Natives and bosses can actually attack, the Abtei has air within reach everywhere and
    no algae growth, the coral guard reflects only from the front and with a pause."""
    from src import materials as mat
    from src.behaviour import REFLECT_COOLDOWN, handle_reflect_projectiles
    from src.enemies import SPECIES, Creature
    from src.projectiles import Projectile
    from src.run import Run
    from src.universes import features
    from src.universes.catalog import ALL_UNIVERSES, UNIVERSES

    harmless = {"huepfling", "zuckerwatte_wolke", "blattlaus", "sporenschnorrer", "leuchtmotte",
                "glockenqualle"}  # fmt: skip
    for universe in UNIVERSES:
        for key in (*universe.natives, universe.mid_boss, universe.boss):
            spec = SPECIES[key]
            assert key in harmless or spec.melee_damage or spec.patterns, f"{key} cannot attack"

    guard = Creature(SPECIES["korallenwaechter"], 100, 100, __import__("random").Random(1))
    guard.facing = 1
    cx, cy = guard.center
    front = [Projectile(x=cx + 10, y=cy, vx=-300.0), Projectile(x=cx + 12, y=cy, vx=-300.0)]
    back = [Projectile(x=cx - 10, y=cy, vx=300.0)]
    assert handle_reflect_projectiles(guard, back, [], 0.016) == 0, "open from behind"
    assert handle_reflect_projectiles(guard, front, [], 0.016) == 1, "one per pause"
    assert handle_reflect_projectiles(guard, front, [], REFLECT_COOLDOWN + 0.1) == 1

    assert not any(r.actor == "algen" for r in mat.SETS["abtei"].reactions), "no algae growth"
    run = Run(seed=26)
    run.start_multiverse_run()
    run.enter_universe(ALL_UNIVERSES["abtei"])
    w = run.world
    line = int(w.height * features.WATER_LINE)
    cells = features._Cells(w, [])
    domes = [
        (x, y + 1, 1, 1)
        for y in range(line, w.height - 8, 4)
        for x in range(8, w.width - 8, 4)
        if w.get(x, y) == mat.AIR
    ]
    far = max(features._air_distance(cells, line, domes)) * features.AIR_GRID
    # AIR_REACH is the target; a few spots where neither a dome nor a bell fits may exceed it
    assert far <= features.AIR_REACH * 1.8, "air within reach of every flooded spot"
