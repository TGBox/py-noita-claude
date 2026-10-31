"""Augmentation editor: rearrange blocks between wands and the bag by drag and drop."""

from __future__ import annotations

import math

import pygame

from src.editor_layout import bag_title_position, hit, layout, wand_title_position
from src.inventory import Inventory, SlotRef
from src.rendering import block_color
from src.settings import COLOR_ACCENT, COLOR_TEXT
from src.spells import CATALOG
from src.wand import Wand

OVERLAY = (8, 3, 5, 238)  # nearly opaque: the HUD must not bleed through
SLOT_BACK = (40, 26, 30)
SLOT_ACTIVE = (90, 50, 56)
HINT = "Bausteine mit der Maus ziehen | Tab oder ESC: Schließen"


def wand_stats_de(wand: Wand) -> str:
    spec = wand.spec
    return (
        f"Mischt: {'Ja' if spec.shuffle else 'Nein'} | Zauber/Wurf: {spec.casts} | "
        f"Verzögerung: {spec.cast_delay:.2f} s | Nachladen: {spec.recharge:.2f} s | "
        f"Mana: {spec.mana_max:.0f} (+{spec.mana_regen:.0f}/s) | "
        f"Streuung: {math.degrees(spec.spread):.1f}°"
    )


class WandEditor:
    def __init__(self) -> None:
        self.open = False
        self.dragging: SlotRef | None = None
        self.font = pygame.font.SysFont(None, 22)
        self.title_font = pygame.font.SysFont(None, 34)

    def toggle(self) -> None:
        self.open = not self.open
        self.dragging = None

    def handle_event(self, event: pygame.event.Event, inventory: Inventory) -> None:
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) or event.button != 1:
            return
        width, height = pygame.display.get_surface().get_size()
        ref = hit(layout(width, height, inventory), *event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = ref if ref is not None and inventory.get(ref) else None
        else:
            if self.dragging is not None and ref is not None:
                inventory.move(self.dragging, ref)
            self.dragging = None

    def draw(self, screen: pygame.Surface, inventory: Inventory) -> None:
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        screen.blit(overlay, (0, 0))
        screen.blit(self.title_font.render("Augmentationen umbauen", True, COLOR_TEXT), (40, 30))
        screen.blit(self.font.render(HINT, True, COLOR_TEXT), (40, 60))

        for index, wand in enumerate(inventory.wands):
            x, y = wand_title_position(width, index)
            color = COLOR_ACCENT if index == inventory.active else COLOR_TEXT
            title = f"{index + 1}. {wand.spec.name_de}  -  {wand_stats_de(wand)}"
            screen.blit(self.font.render(title, True, color), (x, y))
        x, y = bag_title_position(width, inventory)
        screen.blit(self.font.render("Beutel", True, COLOR_TEXT), (x, y))

        slots = layout(width, height, inventory)
        mouse = pygame.mouse.get_pos()
        hovered = hit(slots, *mouse)
        for ref, rect in slots:
            back = SLOT_ACTIVE if ref.kind == "wand" and ref.wand == inventory.active else SLOT_BACK
            pygame.draw.rect(screen, back, rect)
            key = inventory.get(ref)
            if key is not None and ref != self.dragging:
                self._draw_block(screen, key, pygame.Rect(rect).inflate(-10, -10))
            if ref == hovered:
                pygame.draw.rect(screen, COLOR_TEXT, rect, 1)

        if self.dragging is not None:
            key = inventory.get(self.dragging)
            if key is not None:
                self._draw_block(screen, key, pygame.Rect(mouse[0] - 12, mouse[1] - 12, 24, 24))
        elif hovered is not None and inventory.get(hovered):
            self._tooltip(screen, inventory.get(hovered) or "", mouse)

    def _draw_block(self, screen: pygame.Surface, key: str, rect: pygame.Rect) -> None:
        block = CATALOG[key]
        pygame.draw.rect(screen, block_color(block), rect, border_radius=4)
        label = self.font.render(block.name_de[:2], True, (20, 10, 12))
        screen.blit(label, label.get_rect(center=rect.center))

    def _tooltip(self, screen: pygame.Surface, key: str, mouse: tuple[int, int]) -> None:
        block = CATALOG[key]
        lines = [f"{block.category.value}: {block.name_de}", f"Mana: {block.mana:g}"]
        if block.uses:
            lines.append(f"Ladungen: {block.uses} pro Sanktum")
        if block.description_de:
            lines.append(block.description_de)
        surfaces = [self.font.render(line, True, COLOR_TEXT) for line in lines]
        width = max(s.get_width() for s in surfaces) + 16
        height = 18 * len(surfaces) + 10
        x, y = mouse[0] + 16, mouse[1] + 16
        pygame.draw.rect(screen, (24, 14, 18), (x, y, width, height))
        pygame.draw.rect(screen, COLOR_TEXT, (x, y, width, height), 1)
        for index, surface in enumerate(surfaces):
            screen.blit(surface, (x + 8, y + 6 + index * 18))
