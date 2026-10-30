"""Heads-up display drawn in window space on top of the scaled game picture."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.player import MAX_ENERGY, MAX_HP, Player
from src.rendering import block_color
from src.settings import COLOR_ACCENT, COLOR_TEXT
from src.viewport import Viewport
from src.wand import Wand

BAR_BACK = (34, 22, 26)
ENERGY_COLOR = (176, 160, 130)
MANA_COLOR = (90, 120, 200)
RECHARGE_COLOR = (200, 170, 70)
SLOT_SIZE = 18
HELP_LINES = (
    "A/D: Laufen | W/Leertaste: Springen, halten zum Schweben",
    "Linke Maus: Zaubern | Q/E: Augmentation wechseln",
    "Rechte Maus: Malen | Mittlere Maus: Radieren | 1-0: Material | Mausrad: Größe",
    "R: Wiederbeleben | N: Neue Welt | H: Hilfe | F11: Vollbild | ESC: Beenden",
)


@dataclass
class HudState:
    """Everything the HUD shows, collected by the game each frame."""

    player: Player
    wands: list[Wand]
    wand_index: int
    paint_name: str
    paint_slot: int
    brush: int
    fps: float
    chunks: int
    show_help: bool


class Hud:
    def __init__(self) -> None:
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 40)

    def draw(self, screen: pygame.Surface, viewport: Viewport, state: HudState) -> None:
        left, top = viewport.offset_x + 14, viewport.offset_y + 12
        self._bar(screen, left, top, 180, 12, state.player.hp / MAX_HP, COLOR_ACCENT)
        self._bar(screen, left, top + 18, 180, 7, state.player.energy / MAX_ENERGY, ENERGY_COLOR)

        status = (
            f"Pinsel: {state.paint_name} ({state.paint_slot}) | Größe {state.brush} | "
            f"FPS {state.fps:.0f} | aktive Chunks {state.chunks}"
        )
        self._text(screen, status, left, top + 34)
        if state.show_help:
            for index, line in enumerate(HELP_LINES):
                self._text(screen, line, left, top + 52 + index * 18)

        self._wand_panel(screen, viewport, state)
        if state.player.dead:
            text = self.big_font.render("Du bist gestorben - R zum Wiederbeleben", True, COLOR_ACCENT)
            screen.blit(text, text.get_rect(center=screen.get_rect().center))

    def _wand_panel(self, screen: pygame.Surface, viewport: Viewport, state: HudState) -> None:
        wand = state.wands[state.wand_index]
        left = viewport.offset_x + 14
        bottom = viewport.offset_y + viewport.target_height - 14
        top = bottom - 74

        title = f"Augmentation {state.wand_index + 1}/{len(state.wands)}: {wand.spec.name_de}"
        self._text(screen, title, left, top)
        self._bar(screen, left, top + 18, 180, 6, wand.mana / wand.spec.mana_max, MANA_COLOR)
        if wand.recharging:
            fraction = 1 - wand.recharge_left / wand.spec.recharge
            self._bar(screen, left + 190, top + 18, 60, 6, fraction, RECHARGE_COLOR)

        y = top + 30
        for index, block in enumerate(wand.blocks):
            x = left + index * (SLOT_SIZE + 4)
            rect = pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)
            pygame.draw.rect(screen, BAR_BACK, rect)
            pygame.draw.rect(screen, block_color(block), rect.inflate(-6, -6))
            if index == wand.index and not wand.recharging:
                pygame.draw.rect(screen, COLOR_TEXT, rect, 1)
        names = " > ".join(block.name_de for block in wand.blocks)
        self._text(screen, names, left, y + SLOT_SIZE + 6)

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
