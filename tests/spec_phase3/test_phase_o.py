"""Tests for Phase O workshop TV stations, 12 channels, buffs, and promo code discount."""

from __future__ import annotations

from types import SimpleNamespace

from src.fabricator import discounted_gold
from src.player import Player
from src.tv_channels import PROMO_DISCOUNTS, TV_CHANNELS
from src.tv_engine import WATCH_BUFF_THRESHOLD_SEC, TVEngine
from src.workshop import ALL_STATIONS, PHASE3_STATIONS, STATIONS


def test_o01_workshop_stations_keep_mvp_12_and_expose_phase3() -> None:
    assert len(STATIONS) == 12
    assert "ws_tv" in PHASE3_STATIONS
    assert "ws_statistik_wand" in PHASE3_STATIONS
    assert "ws_tv" in ALL_STATIONS
    assert "ws_statistik_wand" in ALL_STATIONS


def test_o02_twelve_original_tv_channels_and_promo() -> None:
    assert len(TV_CHANNELS) == 12
    numbers = [ch.number for ch in TV_CHANNELS]
    assert numbers == list(range(1, 13))
    promo_channels = [ch for ch in TV_CHANNELS if ch.promo_code == "RABATT-42-GLIBBER"]
    assert len(promo_channels) == 1
    assert PROMO_DISCOUNTS["RABATT-42-GLIBBER"] == 0.42


def test_o03_o04_tv_engine_watch_buff_and_fabricator_discount() -> None:
    tv = TVEngine()
    player = Player(40, 40)
    tv.turn_on()
    assert tv.current_channel.number == 1

    tv.next_channel()
    assert tv.current_channel.number == 2  # Kochen mit Gallenstein -> +15 shield

    # Before 15s, no buff yet.
    assert tv.step(10.0, player) is None
    assert player.tv_buff is None

    # Crossing 15s grants the buff.
    granted = tv.step(WATCH_BUFF_THRESHOLD_SEC, player)
    assert granted is not None
    assert player.tv_buff is not None
    assert player.tv_buff["buff_key"] == "buff_magenstaerke"
    assert player.shield_hp >= 15.0

    # Redeem promo code.
    fake_run = SimpleNamespace(tv_promo_discount=0.0, tv_promo_single_use=True)
    ok, msg = tv.redeem_promo_code("rabatt-42-glibber", fake_run)
    assert ok is True
    assert "42%" in msg
    assert fake_run.tv_promo_discount == 0.42
    assert discounted_gold(100, fake_run) == 58

    # Duplicate redemption fails.
    ok2, _ = tv.redeem_promo_code("RABATT-42-GLIBBER", fake_run)
    assert ok2 is False
