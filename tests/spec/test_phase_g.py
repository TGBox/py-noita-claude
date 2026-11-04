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
    rec.discover("badge", "dienstmarke")
    rec.discover("creature", "fleischmade")

    assert "funke" in rec.blocks
    assert "nadel" in rec.blueprints
    assert "sporenklub" in rec.universes
    assert "boese_kaiserin" in rec.evil_selves
    assert rec.badges == 1
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
