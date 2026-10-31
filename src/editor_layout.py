"""Screen layout of the inventory (pure geometry, no pygame).

Four wand rows (a grip to drag the whole wand, its slots, a stat panel), the bag
(3 rows of 12), the flasks and a drop zone. Everything scales with the window.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.inventory import BAG_SIZE, MAX_WANDS, Inventory, SlotRef

BAG_COLUMNS = 12
WAND_COLUMNS = 12  # the most slots a wand can have
MAX_FLASKS = 4

Rect = tuple[int, int, int, int]


@dataclass
class Layout:
    scale: float
    panel: Rect
    slot: int
    slots: list[tuple[SlotRef, Rect]] = field(default_factory=list)
    handles: list[tuple[int, Rect]] = field(default_factory=list)  # one grip per wand
    stats: list[tuple[int, Rect]] = field(default_factory=list)  # stat panel per wand
    wand_titles: list[tuple[int, tuple[int, int]]] = field(default_factory=list)
    flasks: list[tuple[int, Rect]] = field(default_factory=list)
    drop: Rect = (0, 0, 0, 0)
    bag_title: tuple[int, int] = (0, 0)
    flask_title: tuple[int, int] = (0, 0)


def layout(width: int, height: int, inventory: Inventory) -> Layout:
    s = max(0.7, min(1.6, height / 720))
    slot = round(34 * s)
    gap = round(6 * s)
    step = slot + gap
    title_h = round(22 * s)
    row_h = slot + title_h + round(14 * s)
    stats_w = round(320 * s)
    content_w = slot + 2 * gap + WAND_COLUMNS * step + round(16 * s) + stats_w
    if content_w > width - 20:  # narrow window: shrink everything a little
        s *= (width - 20) / content_w
        slot, gap = round(34 * s), round(6 * s)
        step, title_h = slot + gap, round(22 * s)
        row_h, stats_w = slot + title_h + round(14 * s), round(320 * s)
        content_w = slot + 2 * gap + WAND_COLUMNS * step + round(16 * s) + stats_w
    left = max(round(16 * s), (width - content_w) // 2)
    top = round(78 * s)
    panel_x, panel_y = left - round(16 * s), top - round(60 * s)
    result = Layout(s, (panel_x, panel_y, content_w + round(32 * s), 0), slot)
    slots_x = left + slot + 2 * gap
    stats_x = slots_x + WAND_COLUMNS * step + round(16 * s)
    for index in range(min(len(inventory.wands), MAX_WANDS)):
        y = top + index * row_h
        result.wand_titles.append((index, (slots_x, y)))
        sy = y + title_h
        result.handles.append((index, (left, sy, slot, slot)))
        for column in range(inventory.wands[index].capacity):
            rect = (slots_x + column * step, sy, slot, slot)
            result.slots.append((SlotRef("wand", column, index), rect))
        result.stats.append((index, (stats_x, y + round(2 * s), stats_w, row_h - round(10 * s))))
    y = top + MAX_WANDS * row_h + round(4 * s)
    result.bag_title = (left, y)
    y += title_h
    bag = min(len(inventory.bag), BAG_SIZE)
    for index in range(bag):
        row, column = divmod(index, BAG_COLUMNS)
        result.slots.append((SlotRef("bag", index), (left + column * step, y + row * step, slot, slot)))
    y += -(-bag // BAG_COLUMNS) * step + round(10 * s)
    result.flask_title = (left, y)
    y += title_h
    flask_w, flask_h = round(slot * 0.9), round(slot * 1.25)
    for index in range(MAX_FLASKS):
        result.flasks.append((index, (left + index * (flask_w + 2 * gap), y, flask_w, flask_h)))
    drop_x = left + MAX_FLASKS * (flask_w + 2 * gap) + round(30 * s)
    result.drop = (drop_x, y, round(280 * s), flask_h)
    bottom = y + flask_h + round(44 * s)
    result.panel = (panel_x, panel_y, content_w + round(32 * s), bottom - panel_y)
    return result


def _inside(rect: Rect, x: int, y: int) -> bool:
    rx, ry, rw, rh = rect
    return rx <= x < rx + rw and ry <= y < ry + rh


def hit(slots: list[tuple[SlotRef, Rect]], x: int, y: int) -> SlotRef | None:
    """The slot under the point (x, y), if any."""
    for ref, rect in slots:
        if _inside(rect, x, y):
            return ref
    return None


def hit_any(result: Layout, x: int, y: int) -> tuple[str, object] | None:
    """What is under (x, y).

    ("slot", SlotRef), ("wand", index), ("flask", index), ("drop", None),
    ("outside", None) beyond the panel, or None for empty space inside it.
    """
    ref = hit(result.slots, x, y)
    if ref is not None:
        return "slot", ref
    for index, rect in result.handles:
        if _inside(rect, x, y):
            return "wand", index
    for index, rect in result.flasks:
        if _inside(rect, x, y):
            return "flask", index
    if _inside(result.drop, x, y):
        return "drop", None
    if not _inside(result.panel, x, y):
        return "outside", None
    return None
