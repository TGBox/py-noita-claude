"""The inventory screen: look into the bag anywhere, rebuild augmentations in a sanctum.

Everything is drag and drop: blocks between slots, a wand by its grip (to reorder or
throw it away), flasks between their places. Dropping something on the "Ablegen"
field or outside the panel throws it into the world. A click on a grip or a flask
takes it into your hand.
"""

from __future__ import annotations

import pygame

from src import ui
from src.editor_layout import Layout, hit_any, layout
from src.hover import HoverInfo, block_lines, compare, wand_values
from src.hud import draw_flask_icon
from src.inventory import spec_of
from src.spells import CATALOG

NOTICE_TIME = 2.5
SLOT_BACK = (34, 18, 22)
SLOT_EDGE = (82, 40, 46)
LOCKED = (0, 0, 0, 110)


class WandEditor:
    def __init__(self) -> None:
        self.open = False
        self.dragging: tuple[str, object] | None = None
        self.notice = ""
        self.notice_time = 0.0

    def toggle(self) -> None:
        self.open = not self.open
        self.dragging = None

    def update(self, dt: float) -> None:
        self.notice_time = max(0.0, self.notice_time - dt)

    def _layout(self, run) -> Layout:
        width, height = pygame.display.get_surface().get_size()
        return layout(width, height, run.inventory)

    def handle_event(self, event: pygame.event.Event, run) -> None:
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) or event.button != 1:
            return
        current = self._layout(run)
        target = hit_any(current, *event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = None
            if target is None:
                return
            kind, value = target
            if kind == "slot" and run.inventory.get(value) or kind == "wand" or kind == "flask" and value < len(run.flasks):
                self.dragging = target
            return
        source, self.dragging = self.dragging, None
        if source is None:
            return
        if target == source:  # a click: take the wand or flask into your hand
            if source[0] == "wand":
                run.inventory.select(source[1])
            elif source[0] == "flask":
                run.select_flask(source[1])
            return
        note = run.inventory_drop(source, target)
        if note:
            self.notice, self.notice_time = note, NOTICE_TIME

    # ------------------------------------------------------------------- draw

    def draw(self, screen: pygame.Surface, run) -> None:
        inventory = run.inventory
        editable = run.can_edit_wands
        current = layout(*screen.get_size(), inventory)
        s = current.scale
        ui.shade(screen, 150)
        panel = ui.panel(screen, current.panel, alpha=244)
        title = "Rucksack" + (" – Sanktum: Augmentationen umbauen" if editable else "")
        ui.text(screen, title, (panel.x + round(18 * s), panel.y + round(12 * s)), round(26 * s), ui.GOLD,
                heading=True)  # fmt: skip
        sub = (
            "Bausteine zwischen Augmentationen und Beutel ziehen."
            if editable
            else "Ansehen und Beutel ordnen. Augmentationen umbauen geht nur im Sanktum."
        )
        ui.text(screen, sub, (panel.x + round(18 * s), panel.y + round(42 * s)), round(15 * s), ui.DIM)

        mouse = pygame.mouse.get_pos()
        hovered = hit_any(current, *mouse)
        active_spec = spec_of(inventory.wand)
        for index, (x, y) in current.wand_titles:
            wand = inventory.wands[index]
            active = index == inventory.active
            label = f"{index + 1}. {wand.spec.name_de}" + ("  (in der Hand)" if active else "")
            ui.text(screen, label, (x, y), round(16 * s), ui.GOLD if active else ui.TEXT, heading=True)
        for index, rect in current.handles:
            self._handle(screen, pygame.Rect(rect), index == inventory.active, hovered == ("wand", index))
        for index, rect in current.stats:
            other = None if index == inventory.active else active_spec
            self._stats(screen, pygame.Rect(rect), spec_of(inventory.wands[index]), other, s)
        ui.text(screen, f"Beutel ({sum(1 for k in inventory.bag if k)}/{len(inventory.bag)})",
                current.bag_title, round(16 * s), heading=True)  # fmt: skip
        for ref, rect in current.slots:
            rect = pygame.Rect(rect)
            is_wand = ref.kind == "wand"
            pygame.draw.rect(screen, SLOT_BACK, rect)
            edge = ui.SELECT_EDGE if hovered == ("slot", ref) else SLOT_EDGE
            pygame.draw.rect(screen, edge, rect, 1)
            key = inventory.get(ref)
            if key is not None and self.dragging != ("slot", ref):
                screen.blit(ui.block_icon(key, rect.width - 4), (rect.x + 2, rect.y + 2))
            if is_wand and not editable:
                veil = pygame.Surface(rect.size, pygame.SRCALPHA)
                veil.fill(LOCKED)
                screen.blit(veil, rect.topleft)
        ui.text(screen, f"Phiolen ({len(run.flasks)}/{len(current.flasks)})", current.flask_title,
                round(16 * s), heading=True)  # fmt: skip
        for index, rect in current.flasks:
            rect = pygame.Rect(rect)
            pygame.draw.rect(screen, SLOT_BACK, rect.inflate(6, 6))
            pygame.draw.rect(screen, SLOT_EDGE, rect.inflate(6, 6), 1)
            if index < len(run.flasks) and self.dragging != ("flask", index):
                draw_flask_icon(screen, rect.inflate(-6, -6), run.flasks[index], index == run.flask_index)
        drop = pygame.Rect(current.drop)
        dragging = self.dragging is not None
        pygame.draw.rect(screen, (60, 14, 18) if dragging else SLOT_BACK, drop)
        pygame.draw.rect(screen, ui.ACCENT if dragging else SLOT_EDGE, drop, 2 if dragging else 1)
        ui.text(screen, "Hierher ziehen: ablegen", drop.center, round(15 * s), ui.TEXT if dragging else ui.DIM,
                anchor="center")  # fmt: skip
        hint = "Ziehen: verschieben | Klick auf Griff oder Phiole: in die Hand | Tab / ESC: schließen"
        ui.text(screen, hint, (panel.centerx, panel.bottom - round(24 * s)), round(14 * s), ui.DIM,
                anchor="midtop")  # fmt: skip
        if self.notice_time > 0:
            ui.text(screen, self.notice, (panel.centerx, panel.y + round(14 * s)), round(17 * s), ui.ACCENT,
                    bold=True, anchor="midtop")  # fmt: skip

        if self.dragging is not None:
            self._dragged(screen, run, mouse, current.slot)
        elif hovered is not None:
            info = self._info(run, hovered)
            if info is not None:
                ui.tooltip(screen, info, mouse, width=round(300 * s))

    def _handle(self, screen: pygame.Surface, rect: pygame.Rect, active: bool, hovered: bool) -> None:
        """The grip of a wand: a little fleshy stump to drag the whole augmentation."""
        pygame.draw.rect(screen, ui.SELECT if active else SLOT_BACK, rect)
        pygame.draw.rect(screen, ui.SELECT_EDGE if active or hovered else SLOT_EDGE, rect, 1)
        cx, cy = rect.center
        r = rect.width // 2
        pygame.draw.line(screen, (150, 84, 86), (cx - r + 5, cy + r - 6), (cx + r - 6, cy - r + 6), max(3, r // 3))
        pygame.draw.circle(screen, (255, 196, 150) if active else (120, 70, 72), (cx + r - 7, cy - r + 7), max(2, r // 5))

    def _stats(self, screen: pygame.Surface, rect: pygame.Rect, spec, other, s: float) -> None:
        """Wand stats as two columns of small bars, coloured against the wand in hand."""
        rows = wand_values(spec)
        others = wand_values(other) if other is not None else None
        half = (len(rows) + 1) // 2
        column_w = rect.width // 2
        row_h = max(12, rect.height // half)
        for index, (label, value, fill, higher, shown) in enumerate(rows):
            column, row = divmod(index, half)
            x = rect.x + column * column_w
            y = rect.y + row * row_h
            color = ui.TEXT
            marker = None
            if others is not None:
                _l, other_value, other_fill, _h, _s = others[index]
                verdict = compare(value, other_value, higher)
                color = ui.GOOD if verdict > 0 else ui.BAD if verdict < 0 else ui.TEXT
                marker = other_fill
            ui.text(screen, label, (x, y), round(12 * s), ui.DIM)
            bar_x = x + round(72 * s)
            bar_w = column_w - round(72 * s) - round(52 * s)
            ui.bar(screen, (bar_x, y + round(4 * s), bar_w, round(6 * s)), fill, (176, 70, 70), marker=marker)
            ui.text(screen, shown, (bar_x + bar_w + round(4 * s), y), round(12 * s), color)
        shuffle = "mischt" if spec.shuffle else "feste Folge"
        x = rect.x + column_w
        y = rect.y + (half - 1) * row_h if len(rows) % 2 else rect.y + half * row_h
        ui.text(screen, shuffle, (x, y), round(12 * s), ui.GOLD if spec.shuffle else ui.DIM)

    def _dragged(self, screen: pygame.Surface, run, mouse: tuple[int, int], size: int) -> None:
        kind, value = self.dragging
        rect = pygame.Rect(mouse[0] - size // 2, mouse[1] - size // 2, size, size)
        if kind == "slot":
            key = run.inventory.get(value)
            if key is not None:
                screen.blit(ui.block_icon(key, size), rect.topleft)
        elif kind == "wand":
            self._handle(screen, rect, True, True)
        elif kind == "flask" and value < len(run.flasks):
            draw_flask_icon(screen, rect, run.flasks[value], False)

    def _info(self, run, hovered: tuple[str, object]) -> HoverInfo | None:
        kind, value = hovered
        if kind == "slot":
            key = run.inventory.get(value)
            if key is None:
                return None
            block = CATALOG[key]
            return HoverInfo(block.name_de, block_lines(block), (232, 214, 180), "pickup", block=key)
        if kind == "wand":
            wand = run.inventory.wands[value]
            names = [CATALOG[k].name_de for k in wand.slots if k]
            lines = ["Ziehen: Reihenfolge ändern oder ablegen", "Klick: in die Hand nehmen"]
            if names:
                lines.insert(0, " > ".join(names))
            return HoverInfo(wand.spec.name_de, lines, (232, 214, 180), "pickup")
        if kind == "flask" and value < len(run.flasks):
            flask = run.flasks[value]
            return HoverInfo(flask.label_de, ["Klick: in die Hand nehmen", "Ziehen: ablegen"], (200, 214, 220))
        if kind == "drop":
            return HoverInfo("Ablegen", ["Was du hierher ziehst, fällt vor dir auf den Boden."])
        return None
