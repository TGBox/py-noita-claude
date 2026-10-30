"""Title screen and pause menu overlays."""

from __future__ import annotations

import pygame

from src.settings import COLOR_ACCENT, COLOR_TEXT

SHADE = (6, 2, 4, 200)
TITLE_LINES = (
    "Enter / Leertaste: Lauf beginnen",
    "ESC: Beenden",
)
CONTROLS = (
    "A/D laufen | W/Leertaste springen, halten zum Schweben | Linke Maus zaubern",
    "1-4 / Mausrad Augmentation | E aufheben, kaufen, wählen | Tab umbauen",
    "Steig durch vier Tiefen hinab, sammle Blutperlen und zerstöre das Herz.",
)
PAUSE_LINES = (
    "ESC: Weiter",
    "R: Neuer Lauf",
    "T: Zum Titel",
    "Q: Beenden",
)


class Menus:
    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont(None, 120)
        self.big_font = pygame.font.SysFont(None, 44)
        self.font = pygame.font.SysFont(None, 26)

    def _shade(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill(SHADE)
        screen.blit(overlay, (0, 0))

    def _centered(self, screen: pygame.Surface, surface: pygame.Surface, y: float) -> None:
        screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, int(y))))

    def draw_title(self, screen: pygame.Surface, pulse: float) -> None:
        self._shade(screen)
        height = screen.get_height()
        red = (int(150 + 60 * pulse), 20, 36)
        self._centered(screen, self.title_font.render("CLOITA", True, red), height * 0.3)
        subtitle = self.font.render("Ein Abstieg in das lebende Fleisch", True, COLOR_TEXT)
        self._centered(screen, subtitle, height * 0.3 + 70)
        for index, line in enumerate(TITLE_LINES):
            self._centered(screen, self.big_font.render(line, True, COLOR_TEXT), height * 0.55 + index * 44)
        for index, line in enumerate(CONTROLS):
            self._centered(screen, self.font.render(line, True, COLOR_TEXT), height * 0.78 + index * 26)

    def draw_pause(self, screen: pygame.Surface) -> None:
        self._shade(screen)
        height = screen.get_height()
        self._centered(screen, self.big_font.render("Pause", True, COLOR_ACCENT), height * 0.32)
        for index, line in enumerate(PAUSE_LINES):
            self._centered(screen, self.font.render(line, True, COLOR_TEXT), height * 0.42 + index * 30)
