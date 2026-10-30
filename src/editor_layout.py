"""Screen layout of the augmentation editor (pure geometry, no pygame)."""

from __future__ import annotations

from src.inventory import Inventory, SlotRef

SLOT = 34
GAP = 6
ROW_HEIGHT = SLOT + 30
BAG_COLUMNS = 8
MARGIN = 40

Rect = tuple[int, int, int, int]


TOP = MARGIN + 40


def _left(width: int) -> int:
    return max(MARGIN, (width - (BAG_COLUMNS * (SLOT + GAP))) // 2 - 200)


def layout(width: int, height: int, inventory: Inventory) -> list[tuple[SlotRef, Rect]]:
    """Every slot of the editor with its screen rectangle (x, y, w, h)."""
    slots: list[tuple[SlotRef, Rect]] = []
    left = _left(width)
    top = TOP
    for wand_index, wand in enumerate(inventory.wands):
        y = top + wand_index * ROW_HEIGHT + 22
        for slot in range(wand.capacity):
            x = left + slot * (SLOT + GAP)
            slots.append((SlotRef("wand", slot, wand_index), (x, y, SLOT, SLOT)))
    bag_top = top + max(1, len(inventory.wands)) * ROW_HEIGHT + 40
    for index in range(len(inventory.bag)):
        row, column = divmod(index, BAG_COLUMNS)
        x = left + column * (SLOT + GAP)
        y = bag_top + row * (SLOT + GAP)
        slots.append((SlotRef("bag", index), (x, y, SLOT, SLOT)))
    return slots


def wand_title_position(width: int, wand_index: int) -> tuple[int, int]:
    return _left(width), TOP + wand_index * ROW_HEIGHT


def bag_title_position(width: int, inventory: Inventory) -> tuple[int, int]:
    return _left(width), TOP + max(1, len(inventory.wands)) * ROW_HEIGHT + 18


def hit(slots: list[tuple[SlotRef, Rect]], x: int, y: int) -> SlotRef | None:
    """The slot under the point (x, y), if any."""
    for ref, (sx, sy, sw, sh) in slots:
        if sx <= x < sx + sw and sy <= y < sy + sh:
            return ref
    return None
