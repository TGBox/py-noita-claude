"""Title screen and pause menu overlays."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from src.enemies import SPECIES
from src.options import Options
from src.records import BOSS_PEARLS, Records
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
    lines += ["K: Kodex", "O: Optionen", "ESC: Beenden"]
    return lines


def unlock_line(records: Records) -> str:
    """What the Kodex currently grants, in German."""
    _favoured, pearls = records.unlocks()
    return (
        f"Bekannte Bausteine erscheinen häufiger im Laden | Startkapital: {pearls} Blutperlen "
        f"(je bezwungenem Wächter {BOSS_PEARLS})"
    )


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
        if not spec.prop
    ]
    return blocks, creatures

SHADE = (6, 2, 4, 200)
CODEX_COLUMNS = 5
UNKNOWN = "???"
CONTROLS = (
    "A/D laufen | W/Leertaste springen, halten zum Schweben | Linke Maus zaubern",
    "1-4 / Mausrad Augmentation | E aufheben, kaufen, wählen | Tab umbauen (im Sanktum)",
    "Steig durch sieben Tiefen hinab, sammle Blutperlen und zerstöre das Herz.",
)
PAUSE_LINES = (
    "ESC: Weiter",
    "R: Neuer Lauf",
    "T: Zum Titel",
    "O: Optionen",
    "Q: Beenden",
)


class Menus:
    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont(None, 120)
        self.big_font = pygame.font.SysFont(None, 44)
        self.font = pygame.font.SysFont(None, 26)
        self.small_font = pygame.font.SysFont(None, 20)

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
            self._centered(screen, self.big_font.render(line, True, COLOR_TEXT), height * 0.5 + index * 40)
        for index, line in enumerate(CONTROLS):
            self._centered(screen, self.font.render(line, True, COLOR_TEXT), height * 0.78 + index * 26)
        for index, line in enumerate(records):
            self._centered(screen, self.font.render(line, True, COLOR_ACCENT), height * 0.3 + 105 + index * 24)

    def draw_codex(self, screen: pygame.Surface, records: Records) -> None:
        self._shade(screen)
        self._shade(screen)
        width, height = screen.get_size()
        blocks, creatures = codex_entries(records)
        known = sum(1 for _, seen in blocks if seen)
        self._centered(screen, self.big_font.render("Kodex", True, COLOR_ACCENT), height * 0.06)
        heading = f"Bausteine: {known}/{len(blocks)}"
        self._centered(screen, self.font.render(heading, True, COLOR_TEXT), height * 0.12)
        # 400 blocks do not fit as a list: count every category, list only what was found
        counts = []
        for category in Category:
            pool = [b for b in BLOCKS if b.category is category]
            found = sum(1 for b in pool if b.key in records.blocks)
            counts.append(f"{CATEGORY_DE[category]}: {found}/{len(pool)}")
        self._centered(screen, self.font.render("   ".join(counts), True, COLOR_TEXT), height * 0.17)
        left, right = width * 0.04, width * 0.96
        column_width = (right - left) / CODEX_COLUMNS
        found_names = [text for text, seen in blocks if seen]
        top, line = height * 0.22, 20.0
        rows = int((height * 0.62 - top) // line)
        shown = found_names[: rows * CODEX_COLUMNS]
        for index, text in enumerate(shown):
            column, row = divmod(index, rows)
            screen.blit(self.small_font.render(text, True, COLOR_TEXT), (left + column * column_width, top + row * line))
        if len(found_names) > len(shown):
            more = f"... und {len(found_names) - len(shown)} weitere"
            self._centered(screen, self.small_font.render(more, True, DIM), height * 0.63)
        if not found_names:
            self._centered(screen, self.font.render("Noch nichts gefunden.", True, DIM), top + 20)
        top = height * 0.67
        met = sum(1 for _, seen in creatures if seen)
        self._centered(screen, self.font.render(f"Kreaturen: {met}/{len(creatures)}", True, COLOR_TEXT), top)
        creature_rows = -(-len(creatures) // CODEX_COLUMNS)
        for index, (text, seen) in enumerate(creatures):
            column, row = divmod(index, creature_rows)
            screen.blit(self.small_font.render(text, True, COLOR_TEXT if seen else DIM), (left + column * column_width, top + 18 + row * line))
        self._centered(screen, self.font.render(unlock_line(records), True, COLOR_ACCENT), height * 0.91)
        self._centered(screen, self.font.render("ESC / K: Zurück", True, COLOR_TEXT), height * 0.96)

    def draw_options(self, screen: pygame.Surface, options: Options, selected: int) -> None:
        self._shade(screen)
        height = screen.get_height()
        self._centered(screen, self.big_font.render("Optionen", True, COLOR_ACCENT), height * 0.25)
        for index, (name, title) in enumerate(Options.ENTRIES):
            color = COLOR_ACCENT if index == selected else COLOR_TEXT
            text = options.label(name, title)
            if index == selected:
                text = f"> {text} <"
            self._centered(screen, self.font.render(text, True, color), height * 0.36 + index * 32)
        hint = "Hoch/Runter: wählen | Links/Rechts: ändern | ESC: zurück"
        self._centered(screen, self.font.render(hint, True, COLOR_TEXT), height * 0.8)

    def draw_pause(self, screen: pygame.Surface, summary: Sequence[str] = ()) -> None:
        self._shade(screen)
        height = screen.get_height()
        self._centered(screen, self.big_font.render("Pause", True, COLOR_ACCENT), height * 0.2)
        for index, line in enumerate(PAUSE_LINES):
            self._centered(screen, self.font.render(line, True, COLOR_TEXT), height * 0.29 + index * 30)
        for index, line in enumerate(summary):  # the run so far
            color = COLOR_ACCENT if index == 0 else COLOR_TEXT
            self._centered(screen, self.font.render(line, True, color), height * 0.58 + index * 26)
