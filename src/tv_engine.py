"""Interdimensional TV engine: channel zapping, CRT overlay state, watch buffs, and promo codes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.tv_channels import PROMO_DISCOUNTS, TV_CHANNELS, TVChannel

WATCH_BUFF_THRESHOLD_SEC = 15.0


@dataclass
class TVEngine:
    """State machine for the workshop interdimensional television (ws_tv)."""

    channels: tuple[TVChannel, ...] = TV_CHANNELS
    channel_index: int = 0
    is_on: bool = False
    watch_elapsed: float = 0.0
    active_buff: dict[str, Any] | None = None
    redeemed_codes: set[str] = field(default_factory=set)
    scanline_phase: float = 0.0

    @property
    def current_channel(self) -> TVChannel:
        return self.channels[self.channel_index % len(self.channels)]

    def turn_on(self) -> TVChannel:
        self.is_on = True
        return self.current_channel

    def turn_off(self) -> None:
        self.is_on = False

    def select_channel(self, index_or_key: int | str) -> TVChannel:
        if isinstance(index_or_key, int):
            self.channel_index = index_or_key % len(self.channels)
        else:
            for idx, ch in enumerate(self.channels):
                if ch.key == index_or_key:
                    self.channel_index = idx
                    break
            else:
                raise KeyError(f"Unbekannter TV-Kanal: {index_or_key}")
        self.watch_elapsed = 0.0
        self.is_on = True
        return self.current_channel

    def next_channel(self) -> TVChannel:
        return self.select_channel((self.channel_index + 1) % len(self.channels))

    def prev_channel(self) -> TVChannel:
        return self.select_channel((self.channel_index - 1) % len(self.channels))

    def step(self, dt: float, player: Any | None = None) -> dict[str, Any] | None:
        """Advance CRT scanlines and grant channel buff after 15 seconds of watching."""
        if not self.is_on or dt <= 0.0:
            return None
        self.scanline_phase = (self.scanline_phase + dt * 48.0) % 24.0
        self.watch_elapsed += dt
        if self.watch_elapsed >= WATCH_BUFF_THRESHOLD_SEC:
            ch = self.current_channel
            buff_payload = {
                "channel": ch.key,
                "title_de": ch.title_de,
                "buff_key": ch.buff_key,
                "buff_desc_de": ch.buff_desc_de,
                "effect": dict(ch.buff_effect),
            }
            if self.active_buff is None or self.active_buff.get("buff_key") != ch.buff_key:
                self.active_buff = buff_payload
                if player is not None:
                    player.tv_buff = buff_payload
                    if "shield_hp" in ch.buff_effect and hasattr(player, "shield_hp"):
                        player.shield_hp = max(
                            float(getattr(player, "shield_hp", 0.0)),
                            float(ch.buff_effect["shield_hp"]),
                        )
                return buff_payload
        return None

    def redeem_promo_code(self, code: str, run: Any | None = None) -> tuple[bool, str]:
        """Validate and apply an interdimensional teleshopping promo code."""
        normalized = code.strip().upper()
        if normalized not in PROMO_DISCOUNTS:
            return False, "Ungültiger Aktionscode. Das Amt lehnt Ihre Sparfantasie ab."
        if normalized in self.redeemed_codes:
            return False, "Aktionscode bereits eingelöst."
        discount = PROMO_DISCOUNTS[normalized]
        self.redeemed_codes.add(normalized)
        if run is not None:
            run.tv_promo_discount = discount
            run.tv_promo_single_use = True
        pct = round(discount * 100)
        return True, f"Aktionscode {normalized} akzeptiert: {pct}% Fabrikator-Rabatt aktiviert!"

    def render_state(self) -> dict[str, Any]:
        """Structured state for HUD/CRT overlay rendering."""
        ch = self.current_channel
        return {
            "is_on": self.is_on,
            "channel_number": ch.number,
            "channel_key": ch.key,
            "title_de": ch.title_de,
            "tagline_de": ch.tagline_de,
            "lines_de": ch.lines_de,
            "promo_code": ch.promo_code,
            "watch_progress": min(1.0, self.watch_elapsed / WATCH_BUFF_THRESHOLD_SEC),
            "buff_unlocked": self.active_buff is not None
            and self.active_buff.get("buff_key") == ch.buff_key,
            "scanline_phase": self.scanline_phase,
        }
