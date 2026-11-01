from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()


def test_g01_and_g02_hud_and_speech_bubbles() -> None:
    from src.hud import SpeechBubble, draw_boss_banner, draw_speech_bubbles
    from src.rendering import Renderer
    from src.run import Run

    surf = pygame.Surface((640, 360))
    font = pygame.font.SysFont("consolas", 14)
    run = Run(seed=1)
    run.gold = 77
    run.wanted.add(3.0, "Test")
    run.bubbles.append(SpeechBubble("Klonita", "Vorsicht!", run.player.x, run.player.y))
    run.boss_banner = ("Schrottpresse — Phase 2", 2.5)

    draw_speech_bubbles(surf, font, run.bubbles, 0.0, 0.0)
    draw_boss_banner(surf, font, run.boss_banner)
    Renderer(surf).draw(run)


def test_g03_hover_inspection_for_samples_stations_and_stances() -> None:
    from src.hover import describe_pickup, inspect_world
    from src.loot import Pickup
    from src.run import Run

    p = Pickup(10.0, 10.0, kind="sample", item_key="probe_rost", amount=2)
    info = describe_pickup(p)
    assert "Rost-Span" in info.title

    run = Run(seed=3)
    run.enter_workshop()
    assert run.workshop_layout is not None
    st = run.workshop_layout.stations["ws_fabricator"]
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


def test_g04_to_g06_records_discover_and_ranks() -> None:
    from src.records import Records, compute_score, rank_for_score

    rec = Records()
    rec.discover("block", "spark")
    rec.discover("blueprint", "orb")
    rec.discover("universe", "myzel")
    rec.discover("evil_self", "boese_kaiserin")
    rec.discover("badge", "dienstmarke")
    rec.discover("creature", "rostkaefer")

    assert "spark" in rec.blocks
    assert "orb" in rec.blueprints
    assert "myzel" in rec.universes
    assert "boese_kaiserin" in rec.evil_selves
    assert rec.badges == 1
    assert rec.creatures["rostkaefer"] == 1
    assert "myzel" not in rec.creatures

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


def test_g07_and_g08_full_save_load_roundtrip() -> None:
    from src.run import Run

    run = Run(seed=8, universe_key="kuchen")
    run.gold = 145
    run.badges = 2
    run.inventory.add_sample("probe_zucker", 7)
    run.wanted.add(2.5, "Sachbeschädigung")
    run.player.body.stamped_good = 15.0
    run.klonita.toggle()

    saved = run.save_state()
    run2 = Run(seed=1)
    run2.restore(saved)

    assert run2.gold == 145
    assert run2.badges == 2
    assert run2.inventory.sample_count("probe_zucker") == 7
    assert run2.wanted.stars == 2
    assert run2.player.body.stamped_good >= 14.0
    assert run2.klonita.state == "dismissed"
    assert run2.level.universe_key == "kuchen"


def test_g09_menu_keyboard_navigation() -> None:
    from src.run import Run

    run = Run(seed=9)
    for mode in ("portal_select", "fabricator", "trader", "empress_bargain", "archive"):
        run.menu_mode = mode
        assert run.handle_menu_input(pygame.K_ESCAPE) is True
        assert run.menu_mode == ""


def test_g10_full_acceptance_bot_across_all_9_universes() -> None:
    from src.bot import run_bot
    from src.universes.catalog import UNIVERSES

    for u in UNIVERSES.values():
        rep = run_bot(u.key, seed=42, max_seconds=8.0)
        assert rep.errors == [], f"Errors in {u.key}: {rep.errors}"
        assert rep.stuck_ratio < 0.85, f"Bot stuck in {u.key}: {rep.stuck_ratio}"

