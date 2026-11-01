"""Heads-up display drawn in window space on top of the scaled game picture."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pygame

from src import ui
from src.enemies import Creature
from src.flask import CAPACITY as FLASK_CAPACITY
from src.flask import Flask
from src.floaters import Floater
from src.hover import HoverInfo
from src.inventory import Inventory
from src.materials import MATERIALS
from src.player import Player
from src.spells import CATALOG
from src.viewport import Viewport

PLAYER_DAMAGE = (255, 90, 80)
ENEMY_DAMAGE = (240, 226, 200)
LOW_HEALTH = 0.3  # share of max health below which the screen pulses red
VIGNETTE_STEPS = 6
HEALTH_COLOR = (196, 30, 42)
ENERGY_COLOR = (186, 168, 128)
MANA_COLOR = (84, 118, 210)
RECHARGE_COLOR = (214, 172, 70)
PEARL_COLOR = (226, 60, 74)
GLASS = (200, 214, 220)
STATUS_COLORS = {
    "Brennt!": (255, 150, 50),
    "Nass": (120, 150, 220),
    "Ölig": (196, 174, 118),
    "Verschleimt": (176, 172, 120),
    "Vergiftet": (170, 200, 80),
    "Verwandelt": (200, 120, 230),
}
SLOT = 26


@dataclass
class HudState:
    """Everything the HUD shows, collected by the game each frame."""

    player: Player
    inventory: Inventory
    depth_name: str
    depth_number: int
    depth_total: int
    fps: float
    sandbox: bool = False
    banner: str = ""
    prompt: str = ""
    boss: Creature | None = None
    outcome: str = ""  # "", "dead", "victory" or "true_victory"
    pearls: int = 0
    perks: tuple[tuple[str, tuple[int, int, int]], ...] = ()
    stats: str = ""
    notice: str = ""
    flask: Flask | None = None
    flasks: Sequence[Flask] = ()
    flask_index: int = 0
    pulse: float = 0.0  # 0..1 heartbeat phase for low-health effects
    sandbox_lines: Sequence[str] = ()
    hover: HoverInfo | None = None
    cursor: tuple[int, int] = (0, 0)  # window position of the cursor (for the tooltip)
    outcome_keys: str = ""  # e.g. "N: Noch tiefer | R: Neuer Lauf"
    rule_line: str = ""  # the universe rule (e.g. "Bass (Rang 1)")
    breath: float | None = None  # 0..1 air left (rule_flooded), None: not shown
    beat: float = 0.0  # 1 on the beat, fading to 0 (rule_beat)
    log_path: str = ""
    eyes: int = 0


def statuses(player: Player) -> list[str]:
    return [
        label
        for active, label in (
            (player.burning > 0, "Brennt!"),
            (player.wet > 0, "Nass"),
            (player.oily > 0, "Ölig"),
            (player.slimed > 0, "Verschleimt"),
            (player.poisoned > 0, "Vergiftet"),
            (player.polymorphed > 0, "Verwandelt"),
        )
        if active
    ]


class Hud:
    def draw(self, screen: pygame.Surface, viewport: Viewport, state: HudState) -> None:
        s = ui.scale_of(screen)
        left, top = viewport.offset_x + round(10 * s), viewport.offset_y + round(10 * s)
        right = viewport.offset_x + viewport.target_width - round(10 * s)
        bottom = viewport.offset_y + viewport.target_height - round(10 * s)
        player = state.player
        if 0 < player.hp < player.max_hp * LOW_HEALTH and not state.outcome:
            self._danger_vignette(screen, viewport, state.pulse)

        self._vitals(screen, state, left, top, s)
        depth_end = self._depth_panel(screen, state, right, top, s)
        if state.rule_line:
            self._rule_panel(screen, state, right, depth_end + round(6 * s), s)
        if state.boss is not None:
            self._boss_bar(screen, viewport, state.boss, s)
        self._wand_panel(screen, state.inventory, left, bottom, s)
        self._flask_panel(screen, state, right, bottom, s)
        if state.sandbox:
            self._sandbox_panel(screen, state, left, top + round(96 * s), s)

        centre_x = viewport.offset_x + viewport.target_width // 2
        height = viewport.target_height
        y0 = viewport.offset_y
        if state.outcome:
            self._outcome(screen, state, s)
            return
        if state.prompt:
            ui.text(
                screen, state.prompt, (centre_x, y0 + height * 0.64), round(19 * s), anchor="center"
            )
        if state.notice:
            ui.text(screen, state.notice, (centre_x, y0 + height * 0.36), round(20 * s), ui.GOLD,
                    heading=True, anchor="center")  # fmt: skip
        if state.banner:
            ui.text(screen, state.banner, (centre_x, y0 + height * 0.26), round(46 * s), ui.TEXT,
                    heading=True, anchor="center")  # fmt: skip
        if state.hover is not None:
            ui.tooltip(screen, state.hover, state.cursor, width=round(300 * s))

    # ----------------------------------------------------------------- parts

    def _vitals(self, screen: pygame.Surface, state: HudState, x: int, y: int, s: float) -> None:
        player = state.player
        width, height = round(250 * s), round(86 * s)
        ui.panel(screen, (x, y, width, height), alpha=200)
        icon = max(2, round(2 * s))
        bar_x = x + round(30 * s)
        bar_w = width - round(42 * s)
        health = f"{player.hp:.0f} / {player.max_hp:.0f}"
        rows = (
            ("herz", HEALTH_COLOR, player.hp / player.max_hp, health, 14),
            ("fluegel", ENERGY_COLOR, player.energy / player.energy_max, "", 8),
        )
        cy = y + round(12 * s)
        for name, color, fraction, label, bar_h in rows:
            screen.blit(ui.pixel_icon(name, color, icon), (x + round(10 * s), cy + 1))
            ui.bar(screen, (bar_x, cy + 1, bar_w, round(bar_h * s)), fraction, color, label=label,
                   label_size=round(13 * s))  # fmt: skip
            cy += round((bar_h + 10) * s)
        chips = statuses(player)
        cx = x + round(10 * s)
        cy = y + height - round(26 * s)
        chip_h = round(18 * s)
        for label in chips:
            w = ui.font(round(13 * s), bold=True).size(label)[0] + round(10 * s)
            color = STATUS_COLORS.get(label, ui.TEXT)
            pygame.draw.rect(screen, ui.PANEL_DARK, (cx, cy, w, chip_h))
            pygame.draw.rect(screen, color, (cx, cy, w, chip_h), 1)
            ui.text(screen, label, (cx + w // 2, cy + chip_h // 2), round(13 * s), color, bold=True,
                    anchor="center")  # fmt: skip
            cx += w + round(5 * s)
        if not chips and state.eyes:
            ui.text(
                screen, f"Uraugen: {state.eyes}", (x + round(10 * s), cy), round(13 * s), ui.DIM
            )

    def _rule_panel(
        self, screen: pygame.Surface, state: HudState, right: int, y: int, s: float
    ) -> None:
        width = round(270 * s)
        rows = 2 if state.breath is not None else 1
        height = round((8 + 18 * rows) * s)
        x = right - width
        ui.panel(screen, (x, y, width, height), alpha=190)
        ui.text(
            screen, state.rule_line, (x + round(10 * s), y + round(5 * s)), round(13 * s), ui.GOLD
        )
        if state.beat > 0:
            radius = max(2, round((3 + 3 * state.beat) * s))
            pygame.draw.circle(
                screen, ui.GOLD, (x + width - round(16 * s), y + round(13 * s)), radius
            )
        if state.breath is not None:
            bar = (x + round(52 * s), y + round(26 * s), width - round(64 * s), round(8 * s))
            ui.text(screen, "Atem", (x + round(10 * s), y + round(22 * s)), round(12 * s), ui.DIM)
            ui.bar(screen, bar, state.breath, (120, 190, 230))

    def _depth_panel(
        self, screen: pygame.Surface, state: HudState, right: int, y: int, s: float
    ) -> int:
        width = round(270 * s)
        perk_rows = (len(state.perks) + 1) // 2
        height = round((52 + 17 * perk_rows) * s) + (round(6 * s) if perk_rows else 0)
        x = right - width
        ui.panel(screen, (x, y, width, height), alpha=200)
        number = f"Tiefe {state.depth_number}/{state.depth_total}"
        ui.text(screen, number, (x + round(10 * s), y + round(7 * s)), round(13 * s), ui.DIM)
        ui.text(screen, state.depth_name, (x + round(10 * s), y + round(22 * s)), round(19 * s),
                heading=True)  # fmt: skip
        pearl = ui.pixel_icon("perle", PEARL_COLOR, max(2, round(3 * s)))
        pearls = f"{state.pearls}"
        text_w = ui.font(round(18 * s), bold=True).size(pearls)[0]
        px = x + width - round(12 * s) - text_w
        ui.text(screen, pearls, (px, y + round(7 * s)), round(18 * s), PEARL_COLOR, bold=True)
        screen.blit(pearl, (px - pearl.get_width() - round(6 * s), y + round(11 * s)))
        ui.text(screen, f"FPS {state.fps:.0f}", (x + width - round(12 * s), y + round(31 * s)),
                round(12 * s), ui.DIM, anchor="topright")  # fmt: skip
        for index, (name, color) in enumerate(state.perks):
            column, row = index % 2, index // 2
            cx = x + round(10 * s) + column * (width // 2)
            cy = y + round((50 + row * 17) * s)
            box = (cx, cy + round(3 * s), round(9 * s), round(9 * s))
            pygame.draw.rect(screen, color, box)
            pygame.draw.rect(screen, ui.PANEL_DARK, box, 1)
            ui.text(screen, name, (cx + round(14 * s), cy), round(13 * s))
        return y + height

    def _boss_bar(
        self, screen: pygame.Surface, viewport: Viewport, boss: Creature, s: float
    ) -> None:
        width = int(viewport.target_width * 0.42)
        x = viewport.offset_x + (viewport.target_width - width) // 2
        y = viewport.offset_y + round(34 * s)
        ui.text(screen, boss.spec.name_de, (x + width // 2, y - round(4 * s)), round(20 * s), ui.GOLD,
                heading=True, anchor="midbottom")  # fmt: skip
        ui.bar(screen, (x, y, width, round(12 * s)), boss.hp / boss.max_hp, ui.ACCENT)

    def _wand_panel(
        self, screen: pygame.Surface, inventory: Inventory, left: int, bottom: int, s: float
    ) -> None:
        wand = inventory.wand
        slot = round(SLOT * s)
        gap = round(3 * s)
        slots = max(len(wand.slots), 4)
        width = max(round(300 * s), slots * (slot + gap) + round(20 * s))
        height = round(92 * s)
        x, y = left, bottom - height
        ui.panel(screen, (x, y, width, height), alpha=205)
        tx = x + round(10 * s)  # tabs: which augmentation is in hand
        for index in range(len(inventory.wands)):
            active = index == inventory.active
            rect = pygame.Rect(tx, y + round(8 * s), round(18 * s), round(18 * s))
            pygame.draw.rect(screen, ui.SELECT if active else ui.PANEL_DARK, rect)
            pygame.draw.rect(screen, ui.SELECT_EDGE if active else ui.PANEL_EDGE, rect, 1)
            ui.text(screen, str(index + 1), rect.center, round(13 * s), ui.GOLD if active else ui.DIM,
                    bold=True, anchor="center")  # fmt: skip
            tx += rect.width + round(4 * s)
        ui.text(screen, wand.spec.name_de, (tx + round(6 * s), y + round(7 * s)), round(16 * s),
                heading=True)  # fmt: skip
        my = y + round(32 * s)
        drop = ui.pixel_icon("tropfen", MANA_COLOR, max(2, round(2 * s)))
        screen.blit(drop, (x + round(10 * s), my - round(2 * s)))
        recharge_w = round(62 * s) if wand.recharging else 0
        mana_w = width - round(40 * s) - (recharge_w + round(6 * s) if recharge_w else 0)
        ui.bar(screen, (x + round(28 * s), my, mana_w, round(7 * s)), wand.mana / wand.spec.mana_max,
               MANA_COLOR)  # fmt: skip
        if wand.recharging:
            fraction = 1 - wand.recharge_left / max(wand.spec.recharge, 1e-6)
            rx = x + round(34 * s) + mana_w
            ui.bar(screen, (rx, my, recharge_w, round(7 * s)), fraction, RECHARGE_COLOR)
        sy = y + round(50 * s)
        block_index = -1
        next_key = wand.next_block
        for index, key in enumerate(wand.slots):
            rect = pygame.Rect(x + round(10 * s) + index * (slot + gap), sy, slot, slot)
            pygame.draw.rect(screen, ui.PANEL_DARK, rect)
            pygame.draw.rect(screen, ui.PANEL_EDGE, rect, 1)
            if key is None:
                continue
            block_index += 1
            screen.blit(ui.block_icon(key, slot - 4), (rect.x + 2, rect.y + 2))
            if block_index == next_key:
                pygame.draw.rect(screen, ui.GOLD, rect, 2)
            if CATALOG[key].uses:
                left_charges = wand.charges[block_index]
                color = ui.TEXT if left_charges else ui.ACCENT
                ui.text(screen, str(left_charges), (rect.right - 2, rect.bottom), round(12 * s), color,
                        bold=True, anchor="bottomright")  # fmt: skip

    def _flask_panel(
        self, screen: pygame.Surface, state: HudState, right: int, bottom: int, s: float
    ) -> None:
        flasks = list(state.flasks)
        size = round(24 * s)
        gap = round(8 * s)
        width = max(round(210 * s), len(flasks) * (size + gap) + round(20 * s))
        height = round(76 * s)
        x, y = right - width, bottom - height
        ui.panel(screen, (x, y, width, height), alpha=205)
        for index, flask in enumerate(flasks):
            rect = pygame.Rect(
                x + round(12 * s) + index * (size + gap), y + round(10 * s), size, round(32 * s)
            )
            draw_flask_icon(screen, rect, flask, index == state.flask_index)
        active = state.flask
        label = active.label_de if active is not None else "Keine Phiole"
        ui.text(screen, label, (x + round(10 * s), y + height - round(24 * s)), round(14 * s))

    def _sandbox_panel(
        self, screen: pygame.Surface, state: HudState, x: int, y: int, s: float
    ) -> None:
        lines = list(state.sandbox_lines)
        row = round(16 * s)
        width = round(370 * s)
        height = round(30 * s) + row * len(lines)
        ui.panel(screen, (x, y, width, height), alpha=180, studs=False)
        ui.text(screen, "Sandbox", (x + round(10 * s), y + round(5 * s)), round(15 * s), ui.GOLD,
                heading=True)  # fmt: skip
        cy = y + round(26 * s)
        for line in lines:
            ui.text(screen, line, (x + round(10 * s), cy), round(12 * s), ui.TEXT)
            cy += row

    def _outcome(self, screen: pygame.Surface, state: HudState, s: float) -> None:
        title, sub = {
            "dead": ("Du bist gestorben", "Das Fleisch hat dich verschlungen."),
            "victory": ("Das Herz ist zerstört", "Du hast Cloita besiegt!"),
            "true_victory": ("Alle Uraugen sehen durch dich", "Cloita gehört dir."),
        }[state.outcome]
        width, height = round(640 * s), round(210 * s)
        sw, sh = screen.get_size()
        rect = ui.panel(screen, ((sw - width) // 2, (sh - height) // 2, width, height))
        ui.text(screen, title, (rect.centerx, rect.y + round(18 * s)), round(40 * s), ui.ACCENT,
                heading=True, anchor="midtop")  # fmt: skip
        ui.text(screen, sub, (rect.centerx, rect.y + round(70 * s)), round(18 * s), anchor="midtop")
        if state.stats:
            ui.text(screen, state.stats, (rect.centerx, rect.y + round(100 * s)), round(15 * s), ui.DIM,
                    anchor="midtop")  # fmt: skip
        if state.outcome_keys:
            ui.text(screen, state.outcome_keys, (rect.centerx, rect.y + round(132 * s)), round(17 * s),
                    ui.GOLD, anchor="midtop")  # fmt: skip
        if state.log_path:
            ui.text(screen, f"Protokoll: {state.log_path}", (rect.centerx, rect.bottom - round(26 * s)),
                    round(11 * s), ui.DIM, anchor="midtop")  # fmt: skip

    def _danger_vignette(self, screen: pygame.Surface, viewport: Viewport, pulse: float) -> None:
        """A red, pulsing frame while you are close to death."""
        width, height = viewport.target_width, viewport.target_height
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        strength = 0.5 + 0.5 * pulse
        for k in range(VIGNETTE_STEPS):
            alpha = int(90 * strength * (1 - k / VIGNETTE_STEPS))
            inset = k * 4
            rect = (inset, inset, width - 2 * inset, height - 2 * inset)
            pygame.draw.rect(frame, (140, 0, 10, alpha), rect, 4)
        screen.blit(frame, (viewport.offset_x, viewport.offset_y))

    def draw_floaters(
        self,
        screen: pygame.Surface,
        viewport: Viewport,
        floaters: list[Floater],
        cam: tuple[int, int],
    ) -> None:
        """Damage numbers in screen space (crisp text at any window size)."""
        size = round(17 * ui.scale_of(screen))
        for item in floaters:
            sx = viewport.offset_x + (item.x - cam[0]) * viewport.scale
            sy = viewport.offset_y + (item.y - cam[1]) * viewport.scale
            if not (viewport.offset_x <= sx <= viewport.offset_x + viewport.target_width):
                continue
            color = PLAYER_DAMAGE if item.player else ENEMY_DAMAGE
            surface = ui.font(size, bold=True).render(item.text, True, color)
            surface.set_alpha(int(255 * item.alpha))
            screen.blit(surface, surface.get_rect(center=(int(sx), int(sy))))


def draw_flask_icon(screen: pygame.Surface, rect: pygame.Rect, flask: Flask, active: bool) -> None:
    """A bottle in window space; the liquid shows content and fill level."""
    rect = pygame.Rect(rect)
    if active:
        frame = rect.inflate(8, 8)
        pygame.draw.rect(screen, ui.SELECT, frame)
        pygame.draw.rect(screen, ui.SELECT_EDGE, frame, 1)
    neck_w = max(4, rect.width // 3)
    neck = pygame.Rect(rect.centerx - neck_w // 2, rect.y, neck_w, rect.height // 4)
    body = pygame.Rect(rect.x + 1, neck.bottom, rect.width - 2, rect.bottom - neck.bottom)
    pygame.draw.rect(screen, ui.PANEL_DARK, body)
    if not flask.empty:
        level = max(2, round((body.height - 4) * flask.amount / FLASK_CAPACITY))
        color = MATERIALS[flask.material].color
        top = body.bottom - 2 - level
        pygame.draw.rect(screen, color, (body.x + 2, top, body.width - 4, level))
        light = tuple(min(255, c + 70) for c in color)
        pygame.draw.line(screen, light, (body.x + 2, top), (body.right - 3, top))
    pygame.draw.rect(screen, GLASS, body, 1)
    pygame.draw.rect(screen, GLASS, neck, 1)
    pygame.draw.line(
        screen, (255, 255, 255), (body.x + 3, body.y + 3), (body.x + 3, body.y + body.height // 2)
    )


@dataclass
class SpeechBubble:
    """Floating speech bubble above a speaker in world coordinates (Contract V21, Card G02)."""

    speaker: str
    text: str
    world_x: float
    world_y: float
    remaining: float = 2.8


def draw_speech_bubbles(
    surface: pygame.Surface,
    font: pygame.font.Font,
    bubbles: list[SpeechBubble],
    cam_x: float,
    cam_y: float,
) -> None:
    """Render active speech bubbles onto ``surface`` (Card G02)."""
    raise NotImplementedError("Card G02")


def draw_boss_banner(
    surface: pygame.Surface,
    font: pygame.font.Font,
    banner: tuple[str, float] | None,
) -> None:
    """Render boss phase banner onto ``surface`` (Card G02)."""
    raise NotImplementedError("Card G02")
