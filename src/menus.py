"""Title screen and pause menu overlays."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from src.enemies import SPECIES
from src.records import Records
from src.settings import COLOR_ACCENT, COLOR_TEXT
from src.spells import BLOCKS, Category

CATEGORY_DE = {
    Category.FORM: "Drüse",
    Category.MODIFIER: "Mutation",
    Category.TRIGGER: "Nerv",
    Category.PAYLOAD: "Sekret",
}
DIM = (110, 96, 92)


def title_lines(saved_depth: int | None) -> list[str]:
    """Menu entries of the title screen (``saved_depth``: depth a saved run continues at)."""
    lines = ["Enter / Leertaste: Neuer Lauf"]
    if saved_depth is not None:
        lines.append(f"F: Lauf fortsetzen (vor Tiefe {saved_depth})")
    lines += ["K: Kodex", "ESC: Beenden"]
    return lines


def codex_entries(records: Records) -> tuple[list[tuple[str, bool]], list[tuple[str, bool]]]:
    """(text, known) for every block and every creature, in catalogue order."""
    blocks = [
        (f"{block.name_de} ({CATEGORY_DE[block.category]})", True)
        if block.key in records.blocks
        else (UNKNOWN, False)
        for block in BLOCKS
    ]
    creatures = [
        (f"{spec.name_de}: {records.creatures[spec.key]} getötet", True)
        if spec.key in records.creatures
        else (UNKNOWN, False)
        for spec in SPECIES.values()
    ]
    return blocks, creatures


SHADE = (6, 2, 4, 200)
CODEX_COLUMNS = 3
UNKNOWN = "???"
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

    def draw_title(
        self,
        screen: pygame.Surface,
        pulse: float,
        records: Sequence[str] = (),
        lines: Sequence[str] = (),
    ) -> None:
        self._shade(screen)
        height = screen.get_height()
        red = (int(150 + 60 * pulse), 20, 36)
        self._centered(screen, self.title_font.render("CLOITA", True, red), height * 0.3)
        subtitle = self.font.render("Ein Abstieg in das lebende Fleisch", True, COLOR_TEXT)
        self._centered(screen, subtitle, height * 0.3 + 70)
        for index, line in enumerate(lines):
            self._centered(
                screen, self.big_font.render(line, True, COLOR_TEXT), height * 0.5 + index * 40
            )
        for index, line in enumerate(CONTROLS):
            self._centered(
                screen, self.font.render(line, True, COLOR_TEXT), height * 0.78 + index * 26
            )
        for index, line in enumerate(records):
            self._centered(
                screen, self.font.render(line, True, COLOR_ACCENT), height * 0.3 + 105 + index * 24
            )

    def draw_codex(self, screen: pygame.Surface, records: Records) -> None:
        self._shade(screen)
        self._shade(screen)
        width, height = screen.get_size()
        blocks, creatures = codex_entries(records)
        known = sum(1 for _, seen in blocks if seen)
        self._centered(screen, self.big_font.render("Kodex", True, COLOR_ACCENT), height * 0.08)
        heading = f"Bausteine: {known}/{len(blocks)}"
        self._centered(screen, self.font.render(heading, True, COLOR_TEXT), height * 0.15)
        column_width = width / (CODEX_COLUMNS + 0.5)
        rows = -(-len(blocks) // CODEX_COLUMNS)
        top = height * 0.2
        for index, (text, seen) in enumerate(blocks):
            column, row = divmod(index, rows)
            x = width * 0.25 / (CODEX_COLUMNS + 0.5) * 2 + column * column_width
            screen.blit(
                self.font.render(text, True, COLOR_TEXT if seen else DIM), (x, top + row * 24)
            )
        top += rows * 24 + 24
        met = sum(1 for _, seen in creatures if seen)
        self._centered(
            screen, self.font.render(f"Kreaturen: {met}/{len(creatures)}", True, COLOR_TEXT), top
        )
        for index, (text, seen) in enumerate(creatures):
            column, row = index % CODEX_COLUMNS, index // CODEX_COLUMNS
            x = width * 0.25 / (CODEX_COLUMNS + 0.5) * 2 + column * column_width
            screen.blit(
                self.font.render(text, True, COLOR_TEXT if seen else DIM), (x, top + 20 + row * 24)
            )
        self._centered(screen, self.font.render("ESC / K: Zurück", True, COLOR_TEXT), height * 0.95)

    def draw_pause(self, screen: pygame.Surface) -> None:
        self._shade(screen)
        height = screen.get_height()
        self._centered(screen, self.big_font.render("Pause", True, COLOR_ACCENT), height * 0.32)
        for index, line in enumerate(PAUSE_LINES):
            self._centered(
                screen, self.font.render(line, True, COLOR_TEXT), height * 0.42 + index * 30
            )
