"""Title screen, pause menu, options, controls and Kodex.

Every menu is a list of entries that can be chosen with the arrow keys, the mouse or
a gamepad. Drawing returns the screen rectangle of each entry so the game can tell
which one the mouse is over.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import pygame

from src import ui
from src.enemies import SPECIES
from src.keybinds import ACTIONS, Bindings
from src.options import Options
from src.records import BOSS_PEARLS, Records
from src.spells import BLOCKS, Category

CATEGORY_DE = {
    Category.FORM: "Drüse",
    Category.MODIFIER: "Mutation",
    Category.TRIGGER: "Nerv",
    Category.PAYLOAD: "Sekret",
}
UNKNOWN = "???"
CODEX_COLUMNS = 5

MenuItem = tuple[str, str]  # (key, German label)


def title_items(saved_depth: int | None) -> list[MenuItem]:
    """Entries of the title menu (``saved_depth``: depth a saved run continues at)."""
    items = [("new", "Neuer Lauf")]
    if saved_depth is not None:
        items.append(("continue", f"Lauf fortsetzen (vor Tiefe {saved_depth})"))
    items += [
        ("sandbox", "Sandbox"),
        ("codex", "Kodex"),
        ("controls", "Steuerung"),
        ("options", "Optionen"),
        ("quit", "Beenden"),
    ]
    return items


PAUSE_ITEMS: tuple[MenuItem, ...] = (
    ("resume", "Weiter"),
    ("inventory", "Rucksack"),
    ("controls", "Steuerung"),
    ("options", "Optionen"),
    ("restart", "Neuer Lauf"),
    ("title", "Zum Titel"),
    ("quit", "Beenden"),
)


def controls_rows() -> list[tuple[str, str]]:
    """(key, label) of every row of the controls screen: actions, then two buttons."""
    return [(a.key, a.label_de) for a in ACTIONS] + [("reset", "Alle zurücksetzen"), ("back", "Zurück")]


def help_lines(bindings: Bindings, pad: bool = False) -> list[tuple[str, str]]:
    """(binding, action) pairs for the controls overview in the pause menu.

    Only one device is shown: keyboard and mouse, or the gamepad once one is connected.
    """
    if pad:
        lines = [("Linker Stick", "Laufen"), ("Rechter Stick", "Zielen")]
        lines += [
            (bindings.describe_pad(a.key), a.label_de)
            for a in ACTIONS
            if bindings.pad.get(a.key) and a.key not in ("left", "right")
        ]
        lines.append(("Start", "Pause"))
        return lines
    lines = [(bindings.describe(a.key), a.label_de) for a in ACTIONS if bindings.keys.get(a.key)]
    lines.insert(4, ("1-4 / Mausrad", "Augmentation wählen"))
    lines.insert(12, ("5-8", "Phiole wählen"))
    lines.append(("ESC", "Pause"))
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


class Menus:
    def _list(
        self,
        screen: pygame.Surface,
        items: Sequence[MenuItem],
        selected: int,
        top: float,
        *,
        width: int,
        height: int,
        x: int | None = None,
    ) -> list[pygame.Rect]:
        s = ui.scale_of(screen)
        rects = []
        left = x if x is not None else (screen.get_width() - width) // 2
        for index, (_key, label) in enumerate(items):
            rect = pygame.Rect(left, int(top + index * (height + 8 * s)), width, height)
            ui.button(screen, rect, label, selected=index == selected, size=round(22 * s))
            rects.append(rect)
        return rects

    # ------------------------------------------------------------------ title

    def draw_title(
        self,
        screen: pygame.Surface,
        pulse: float,
        records: Sequence[str],
        items: Sequence[MenuItem],
        selected: int,
        clock: float = 0.0,
    ) -> list[pygame.Rect]:
        ui.shade(screen, 170)
        s = ui.scale_of(screen)
        width, height = screen.get_size()
        cx = width // 2
        # the logo: a pulsing, dripping word
        red = (int(150 + 70 * pulse), 18, 34)
        size = round(128 * s)
        logo = ui.text(screen, "CLOITA", (cx, height * 0.2), size, red, heading=True, bold=True, anchor="center")
        for k in range(7):  # blood running down from the letters
            x = logo.x + (k * 0.153 + 0.05) * logo.width
            length = (math.sin(clock * 0.7 + k * 1.7) * 0.5 + 0.5) * 34 * s + 6 * s
            pygame.draw.line(screen, (120, 10, 24), (x, logo.bottom - 18 * s), (x, logo.bottom - 18 * s + length), max(2, round(3 * s)))
            pygame.draw.circle(screen, (150, 14, 30), (int(x), int(logo.bottom - 18 * s + length)), max(2, round(3 * s)))
        ui.text(screen, "Ein Abstieg in das lebende Fleisch", (cx, logo.bottom + 4 * s), round(20 * s), ui.DIM,
                heading=True, anchor="midtop")  # fmt: skip
        rects = self._list(screen, items, selected, height * 0.36, width=round(360 * s), height=round(36 * s))
        if records:
            box_h = round((18 + 22 * len(records)) * s)
            box = ui.panel(screen, (cx - round(330 * s), height - box_h - round(54 * s), round(660 * s), box_h),
                           alpha=200, studs=False)  # fmt: skip
            for index, line in enumerate(records):
                ui.text(screen, line, (cx, box.y + round((10 + index * 22) * s)), round(15 * s), ui.TEXT,
                        anchor="midtop")  # fmt: skip
        hint = "Pfeiltasten / Maus / Controller: wählen | Enter: bestätigen"
        ui.text(screen, hint, (cx, height - round(30 * s)), round(14 * s), ui.DIM, anchor="midtop")
        return rects

    # ------------------------------------------------------------------ pause

    def draw_pause(
        self,
        screen: pygame.Surface,
        summary: Sequence[str],
        selected: int,
        controls: Sequence[tuple[str, str]],
    ) -> list[pygame.Rect]:
        ui.shade(screen, 190)
        s = ui.scale_of(screen)
        width = screen.get_width()
        column = round(300 * s)
        gap = round(30 * s)
        info_w = round(640 * s)
        total = column + gap + info_w
        left = (width - total) // 2
        top = round(70 * s)
        ui.text(screen, "Pause", (left, top - round(50 * s)), round(44 * s), ui.ACCENT, heading=True)
        rects = self._list(screen, PAUSE_ITEMS, selected, top + round(10 * s), width=column,
                           height=round(38 * s), x=left)  # fmt: skip
        # the run so far
        info_x = left + column + gap
        info_h = round((34 + 22 * len(summary)) * s)
        box = ui.panel(screen, (info_x, top, info_w, info_h), title="Dieser Lauf")
        for index, line in enumerate(summary):
            ui.text(screen, line, (box.x + round(14 * s), box.y + round((34 + index * 22) * s)), round(15 * s))
        # the controls, always at hand
        rows = (len(controls) + 1) // 2
        controls_top = box.bottom + round(16 * s)
        row_h = round(18 * s)
        box = ui.panel(screen, (info_x, controls_top, info_w, round(40 * s) + rows * row_h), title="Steuerung")
        for index, (binding, action) in enumerate(controls):
            column_x = box.x + round(14 * s) + (index // rows) * (info_w // 2)
            y = box.y + round(32 * s) + (index % rows) * row_h
            ui.text(screen, binding, (column_x, y), round(12 * s), bold=True)
            ui.text(screen, action, (column_x + round(140 * s), y), round(12 * s), ui.DIM)
        return rects

    # ---------------------------------------------------------------- options

    def draw_options(self, screen: pygame.Surface, options: Options, selected: int) -> list[pygame.Rect]:
        ui.shade(screen, 200)
        s = ui.scale_of(screen)
        width, height = screen.get_size()
        panel_w, row_h = round(520 * s), round(40 * s)
        entries = Options.ENTRIES
        panel_h = round(100 * s) + len(entries) * (row_h + round(8 * s))
        box = ui.panel(screen, ((width - panel_w) // 2, round(height * 0.16), panel_w, panel_h))
        ui.text(screen, "Optionen", (box.centerx, box.y + round(14 * s)), round(32 * s), ui.ACCENT, heading=True,
                anchor="midtop")  # fmt: skip
        rects = []
        for index, (name, title) in enumerate(entries):
            rect = pygame.Rect(box.x + round(30 * s), box.y + round(66 * s) + index * (row_h + round(8 * s)),
                               panel_w - round(60 * s), row_h)  # fmt: skip
            ui.button(screen, rect, "", selected=index == selected)
            ui.text(screen, title, (rect.x + round(14 * s), rect.centery), round(19 * s), anchor="midleft")
            value = getattr(options, name)
            if isinstance(value, bool):
                ui.text(screen, "an" if value else "aus", (rect.right - round(16 * s), rect.centery), round(19 * s),
                        ui.GOLD if value else ui.DIM, bold=True, anchor="midright")  # fmt: skip
            else:
                bar = (rect.right - round(196 * s), rect.centery - round(5 * s), round(180 * s), round(10 * s))
                ui.bar(screen, bar, value / 10, (176, 70, 70))
            rects.append(rect)
        hint = "Hoch/Runter: wählen | Links/Rechts oder Klick: ändern | ESC: zurück"
        ui.text(screen, hint, (box.centerx, box.bottom + round(12 * s)), round(14 * s), ui.DIM, anchor="midtop")
        return rects

    # --------------------------------------------------------------- controls

    def draw_controls(
        self, screen: pygame.Surface, bindings: Bindings, selected: int, capturing: bool, note: str = ""
    ) -> list[pygame.Rect]:
        ui.shade(screen, 210)
        s = ui.scale_of(screen)
        width, height = screen.get_size()
        rows = controls_rows()
        panel_w = round(820 * s)
        top = round(20 * s)
        box = ui.panel(screen, ((width - panel_w) // 2, top, panel_w, height - 2 * top))
        ui.text(screen, "Steuerung", (box.x + round(20 * s), box.y + round(10 * s)), round(30 * s), ui.ACCENT,
                heading=True)  # fmt: skip
        header_y = box.y + round(52 * s)
        key_x = box.x + round(360 * s)
        pad_x = box.x + round(600 * s)
        ui.text(screen, "Tastatur / Maus", (key_x, header_y), round(14 * s), ui.GOLD, bold=True)
        ui.text(screen, "Controller", (pad_x, header_y), round(14 * s), ui.GOLD, bold=True)
        list_top = header_y + round(24 * s)
        room = box.bottom - round(64 * s) - list_top
        row_h = max(round(18 * s), min(round(25 * s), room // len(rows)))
        visible = max(5, (box.bottom - round(64 * s) - list_top) // row_h)
        first = min(max(0, selected - visible // 2), max(0, len(rows) - visible))
        rects: list[pygame.Rect] = [pygame.Rect(0, 0, 0, 0)] * len(rows)
        group = ""
        action_groups = {a.key: a.group for a in ACTIONS}
        for index in range(first, min(len(rows), first + visible)):
            key, label = rows[index]
            y = list_top + (index - first) * row_h
            rect = pygame.Rect(box.x + round(20 * s), y, panel_w - round(40 * s), row_h - round(3 * s))
            rects[index] = rect
            chosen = index == selected
            if chosen:
                pygame.draw.rect(screen, ui.SELECT, rect)
                pygame.draw.rect(screen, ui.SELECT_EDGE, rect, 1)
            if key in action_groups and action_groups[key] != group:
                group = action_groups[key]
            if key in action_groups:
                ui.text(screen, label, (rect.x + round(10 * s), rect.centery), round(15 * s), anchor="midleft")
                binding = "Taste drücken ..." if chosen and capturing else bindings.describe(key)
                ui.text(screen, binding, (key_x, rect.centery), round(15 * s), ui.GOLD if chosen else ui.TEXT,
                        bold=True, anchor="midleft")  # fmt: skip
                pad = "Knopf drücken ..." if chosen and capturing else bindings.describe_pad(key)
                ui.text(screen, pad, (pad_x, rect.centery), round(15 * s), ui.GOLD if chosen else ui.DIM,
                        anchor="midleft")  # fmt: skip
            else:
                ui.text(screen, label, rect.center, round(16 * s), ui.GOLD if chosen else ui.TEXT, heading=True,
                        anchor="center")  # fmt: skip
        hint = (
            "Enter / Klick: neu belegen (Taste, Maustaste oder Controller-Knopf) | Entf: Standard | ESC: zurück"
            if not capturing
            else "Drücke die neue Taste oder den Controller-Knopf | ESC: abbrechen"
        )
        ui.text(screen, note or hint, (box.centerx, box.bottom - round(50 * s)), round(14 * s),
                ui.ACCENT if note else ui.DIM, anchor="midtop")  # fmt: skip
        fixed = "Fest: ESC Pause | 1-4 / Mausrad Augmentation | 5-8 Phiole | Controller: linker Stick laufen, rechter Stick zielen"
        ui.text(screen, fixed, (box.centerx, box.bottom - round(28 * s)), round(13 * s), ui.DIM, anchor="midtop")
        return rects

    # ------------------------------------------------------------------ codex

    def draw_codex(self, screen: pygame.Surface, records: Records) -> None:
        ui.shade(screen, 220)
        s = ui.scale_of(screen)
        width, height = screen.get_size()
        box = ui.panel(screen, (round(20 * s), round(16 * s), width - round(40 * s), height - round(32 * s)))
        blocks, creatures = codex_entries(records)
        known = sum(1 for _, seen in blocks if seen)
        ui.text(screen, "Kodex", (box.centerx, box.y + round(10 * s)), round(34 * s), ui.ACCENT, heading=True,
                anchor="midtop")  # fmt: skip
        counts = []
        for category in Category:
            pool = [b for b in BLOCKS if b.category is category]
            found = sum(1 for b in pool if b.key in records.blocks)
            counts.append(f"{CATEGORY_DE[category]}: {found}/{len(pool)}")
        heading = f"Bausteine: {known}/{len(blocks)}   –   " + "   ".join(counts)
        ui.text(screen, heading, (box.centerx, box.y + round(54 * s)), round(16 * s), ui.GOLD, anchor="midtop")
        left, right = box.x + round(20 * s), box.right - round(20 * s)
        column_width = (right - left) / CODEX_COLUMNS
        found = [b for b in BLOCKS if b.key in records.blocks]
        top, line = box.y + round(84 * s), round(20 * s)
        rows = max(1, int((height * 0.62 - top) // line))
        shown = found[: rows * CODEX_COLUMNS]
        for index, block in enumerate(shown):
            column, row = divmod(index, rows)
            x, y = left + column * column_width, top + row * line
            screen.blit(ui.block_icon(block.key, line - 4), (x, y))
            ui.text(screen, block.name_de, (x + line + 2, y), round(14 * s))
        if len(found) > len(shown):
            more = f"... und {len(found) - len(shown)} weitere"
            ui.text(screen, more, (box.centerx, height * 0.63), round(14 * s), ui.DIM, anchor="midtop")
        if not found:
            ui.text(screen, "Noch nichts gefunden.", (box.centerx, top + 20), round(16 * s), ui.DIM, anchor="midtop")
        top = height * 0.68
        met = sum(1 for _, seen in creatures if seen)
        ui.text(screen, f"Kreaturen: {met}/{len(creatures)}", (box.centerx, top), round(16 * s), ui.GOLD,
                anchor="midtop")  # fmt: skip
        creature_rows = -(-len(creatures) // CODEX_COLUMNS)
        for index, (label, seen) in enumerate(creatures):
            column, row = divmod(index, creature_rows)
            ui.text(screen, label, (left + column * column_width, top + round(24 * s) + row * line), round(14 * s),
                    ui.TEXT if seen else ui.DIM)  # fmt: skip
        ui.text(screen, unlock_line(records), (box.centerx, box.bottom - round(56 * s)), round(15 * s), ui.ACCENT,
                anchor="midtop")  # fmt: skip
        ui.text(screen, "ESC: Zurück", (box.centerx, box.bottom - round(30 * s)), round(15 * s), anchor="midtop")
