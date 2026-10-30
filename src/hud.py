"""Heads-up display drawn in window space on top of the scaled game picture."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.enemies import Creature
from src.inventory import Inventory
from src.player import Player
from src.rendering import block_color
from src.settings import COLOR_ACCENT, COLOR_TEXT
from src.spells import CATALOG
from src.viewport import Viewport

BAR_BACK = (34, 22, 26)
ENERGY_COLOR = (176, 160, 130)
MANA_COLOR = (90, 120, 200)
RECHARGE_COLOR = (200, 170, 70)
PEARL_TEXT = (230, 90, 100)
EMPTY_SLOT = (52, 36, 40)
SLOT_SIZE = 18
HELP_LINES = (
    "A/D: Laufen | W/Leertaste: Springen, halten zum Schweben | Linke Maus: Zaubern",
    "1-4 / Mausrad: Augmentation wählen | E: Aufheben | Tab: Umbauen | F1: Sandbox",
    "R: Neuer Lauf | L: Licht | M: Ton | H: Hilfe | F11: Vollbild | ESC: Pause",
)
SANDBOX_LINES = (
    "SANDBOX: Rechte Maus: Malen | Mittlere Maus: Radieren | 1-0: Material",
    "Mausrad: Pinselgröße | N: Neue Welt | F1: Sandbox beenden",
)


@dataclass
class HudState:
    """Everything the HUD shows, collected by the game each frame."""

    player: Player
    inventory: Inventory
    depth_name: str
    depth_number: int
    depth_total: int
    fps: float
    chunks: int
    show_help: bool
    sandbox: bool = False
    paint_name: str = ""
    paint_slot: int = 0
    brush: int = 0
    banner: str = ""
    prompt: str = ""
    boss: Creature | None = None
    outcome: str = ""  # "", "dead" or "victory"
    pearls: int = 0
    perks: tuple[str, ...] = ()
    stats: str = ""
    notice: str = ""


class Hud:
    def __init__(self) -> None:
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 44)

    def draw(self, screen: pygame.Surface, viewport: Viewport, state: HudState) -> None:
        left, top = viewport.offset_x + 14, viewport.offset_y + 12
        right = viewport.offset_x + viewport.target_width - 14
        player = state.player
        self._bar(screen, left, top, 180, 12, player.hp / player.max_hp, COLOR_ACCENT)
        self._bar(screen, left, top + 18, 180, 7, player.energy / player.energy_max, ENERGY_COLOR)

        status = [
            label
            for active, label in ((state.player.burning > 0, "Brennt!"), (state.player.wet > 0, "Nass"))
            if active
        ]
        if status:
            self._text(screen, "  ".join(status), left + 190, top)

        depth = f"Tiefe {state.depth_number}/{state.depth_total}: {state.depth_name}"
        info = self.font.render(f"{depth} | FPS {state.fps:.0f}", True, COLOR_TEXT)
        screen.blit(info, (right - info.get_width(), top))
        pearls = self.font.render(f"Blutperlen: {state.pearls}", True, PEARL_TEXT)
        screen.blit(pearls, (right - pearls.get_width(), top + 18))
        for index, name in enumerate(state.perks):
            perk = self.font.render(name, True, COLOR_TEXT)
            screen.blit(perk, (right - perk.get_width(), top + 40 + index * 18))

        y = top + 34
        if state.sandbox:
            self._text(screen, f"Pinsel: {state.paint_name} ({state.paint_slot}) | Größe {state.brush}", left, y)
            y += 18
            for line in SANDBOX_LINES:
                self._text(screen, line, left, y)
                y += 18
        if state.show_help:
            for line in HELP_LINES:
                self._text(screen, line, left, y)
                y += 18

        if state.boss is not None:
            self._boss_bar(screen, viewport, state.boss)
        self._wand_panel(screen, viewport, state.inventory)
        centre_x = viewport.offset_x + viewport.target_width // 2
        if state.prompt:
            text = self.font.render(state.prompt, True, COLOR_TEXT)
            screen.blit(text, text.get_rect(center=(centre_x, viewport.offset_y + viewport.target_height * 0.62)))
        if state.notice:
            text = self.font.render(state.notice, True, COLOR_ACCENT)
            screen.blit(text, text.get_rect(center=(centre_x, viewport.offset_y + viewport.target_height * 0.38)))
        if state.banner:
            text = self.big_font.render(state.banner, True, COLOR_TEXT)
            screen.blit(text, text.get_rect(center=(centre_x, viewport.offset_y + viewport.target_height * 0.3)))
        if state.outcome:
            message = {
                "dead": "Du bist gestorben. R: Neuer Lauf",
                "victory": "Das Herz ist zerstört. Du hast Cloita besiegt! R: Neuer Lauf",
            }[state.outcome]
            text = self.big_font.render(message, True, COLOR_ACCENT)
            centre = screen.get_rect().center
            screen.blit(text, text.get_rect(center=centre))
            if state.stats:
                stats = self.font.render(state.stats, True, COLOR_TEXT)
                screen.blit(stats, stats.get_rect(center=(centre[0], centre[1] + 36)))

    def _boss_bar(self, screen: pygame.Surface, viewport: Viewport, boss: Creature) -> None:
        width = int(viewport.target_width * 0.5)
        x = viewport.offset_x + (viewport.target_width - width) // 2
        y = viewport.offset_y + 40
        name = self.font.render(boss.spec.name_de, True, COLOR_TEXT)
        screen.blit(name, name.get_rect(midbottom=(x + width // 2, y - 2)))
        self._bar(screen, x, y, width, 10, boss.hp / boss.max_hp, COLOR_ACCENT)

    def _wand_panel(self, screen: pygame.Surface, viewport: Viewport, inventory: Inventory) -> None:
        wand = inventory.wand
        left = viewport.offset_x + 14
        bottom = viewport.offset_y + viewport.target_height - 14
        top = bottom - 74

        title = f"Augmentation {inventory.active + 1}/{len(inventory.wands)}: {wand.spec.name_de}"
        self._text(screen, title, left, top)
        self._bar(screen, left, top + 18, 180, 6, wand.mana / wand.spec.mana_max, MANA_COLOR)
        if wand.recharging:
            fraction = 1 - wand.recharge_left / max(wand.spec.recharge, 1e-6)
            self._bar(screen, left + 190, top + 18, 60, 6, fraction, RECHARGE_COLOR)

        y = top + 30
        next_key = wand.next_block
        block_index = -1
        names = []
        for slot, key in enumerate(wand.slots):
            x = left + slot * (SLOT_SIZE + 4)
            rect = pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)
            pygame.draw.rect(screen, BAR_BACK, rect)
            if key is None:
                pygame.draw.rect(screen, EMPTY_SLOT, rect.inflate(-10, -10))
                continue
            block_index += 1
            block = CATALOG[key]
            names.append(block.name_de)
            pygame.draw.rect(screen, block_color(block), rect.inflate(-6, -6))
            if block_index == next_key:
                pygame.draw.rect(screen, COLOR_TEXT, rect, 1)
        self._text(screen, " > ".join(names), left, y + SLOT_SIZE + 6)

    def _text(self, screen: pygame.Surface, text: str, x: int, y: int) -> None:
        screen.blit(self.font.render(text, True, COLOR_TEXT), (x, y))

    @staticmethod
    def _bar(
        screen: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        fraction: float,
        color: tuple[int, int, int],
    ) -> None:
        fraction = min(max(fraction, 0.0), 1.0)
        pygame.draw.rect(screen, BAR_BACK, (x, y, width, height))
        pygame.draw.rect(screen, color, (x, y, int(width * fraction), height))
