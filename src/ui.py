"""Shared UI drawing: fleshy panels, framed bars, buttons, pixel icons and tooltips.

All menus, the HUD and the inventory use these pieces, so the interface looks like
one piece: dark tissue panels with bone studs, bars with a soft gradient and a
pixel-art icon in front, crisp text with a shadow.
"""

from __future__ import annotations

from functools import cache

import pygame

from src.hover import HoverInfo, compare, wand_values
from src.icons import icon_pixels

Color = tuple[int, int, int]

TEXT = (222, 208, 190)
DIM = (140, 122, 116)
ACCENT = (214, 40, 48)
GOOD = (120, 210, 110)
BAD = (230, 90, 80)
GOLD = (232, 190, 96)
PANEL = (20, 9, 12)
PANEL_EDGE = (96, 38, 46)
PANEL_LIGHT = (150, 74, 76)
PANEL_DARK = (10, 4, 6)
STUD = (184, 168, 138)
BAR_BACK = (40, 18, 22)
SELECT = (70, 24, 30)
SELECT_EDGE = (220, 70, 70)

HEADING_FONTS = "georgia,palatinolinotype,bookantiqua,cambria,dejavuserif"
BODY_FONTS = "segoeui,calibri,tahoma,dejavusans,arial"


@cache
def font(size: int, heading: bool = False, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont(HEADING_FONTS if heading else BODY_FONTS, size, bold=bold)


def scale_of(screen: pygame.Surface) -> float:
    """UI scale for the window: 1.0 at 720 px height (never smaller than 0.75)."""
    return max(0.75, min(2.0, screen.get_height() / 720))


# ------------------------------------------------------------------------ text


def text(
    screen: pygame.Surface,
    content: str,
    pos: tuple[float, float],
    size: int = 18,
    color: Color = TEXT,
    *,
    heading: bool = False,
    bold: bool = False,
    anchor: str = "topleft",
    shadow: bool = True,
) -> pygame.Rect:
    """Draw text with a dark drop shadow; returns its rectangle."""
    face = font(size, heading, bold)
    surface = face.render(content, True, color)
    rect = surface.get_rect()
    setattr(rect, anchor, (int(pos[0]), int(pos[1])))
    if shadow:
        screen.blit(face.render(content, True, PANEL_DARK), (rect.x + 1, rect.y + 1))
    screen.blit(surface, rect)
    return rect


def wrap(content: str, size: int, width: int) -> list[str]:
    """Break text into lines no wider than ``width`` pixels."""
    face = font(size)
    lines: list[str] = []
    for paragraph in content.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = f"{line} {word}".strip()
            if line and face.size(candidate)[0] > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


# ---------------------------------------------------------------------- panels


def panel(
    screen: pygame.Surface,
    rect: pygame.Rect | tuple[int, int, int, int],
    *,
    alpha: int = 232,
    title: str = "",
    studs: bool = True,
) -> pygame.Rect:
    """A dark, slightly translucent tissue panel with a bevelled edge and bone studs."""
    rect = pygame.Rect(rect)
    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    body.fill((*PANEL, alpha))
    for k in range(6):  # a soft inner shadow at the top
        pygame.draw.line(body, (0, 0, 0, 60 - k * 10), (0, k), (rect.width, k))
    screen.blit(body, rect.topleft)
    pygame.draw.rect(screen, PANEL_EDGE, rect, 2)
    pygame.draw.line(screen, PANEL_LIGHT, (rect.x + 2, rect.y + 2), (rect.right - 3, rect.y + 2))
    pygame.draw.line(screen, PANEL_LIGHT, (rect.x + 2, rect.y + 2), (rect.x + 2, rect.bottom - 3))
    if studs:
        for x, y in ((rect.x, rect.y), (rect.right - 5, rect.y), (rect.x, rect.bottom - 5), (rect.right - 5, rect.bottom - 5)):
            pygame.draw.rect(screen, PANEL_DARK, (x, y, 5, 5))
            pygame.draw.rect(screen, STUD, (x + 1, y + 1, 3, 3))
    if title:
        text(screen, title, (rect.x + 12, rect.y + 6), 20, GOLD, heading=True)
    return rect


def shade(screen: pygame.Surface, alpha: int = 200) -> None:
    """Darken everything behind a menu."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((6, 2, 4, alpha))
    screen.blit(overlay, (0, 0))


def bar(
    screen: pygame.Surface,
    rect: pygame.Rect | tuple[int, int, int, int],
    fraction: float,
    color: Color,
    *,
    label: str = "",
    label_size: int = 14,
    marker: float | None = None,
) -> None:
    """A framed bar with a light top edge; ``marker`` draws a thin comparison line."""
    rect = pygame.Rect(rect)
    fraction = min(max(fraction, 0.0), 1.0)
    pygame.draw.rect(screen, PANEL_DARK, rect.inflate(2, 2))
    pygame.draw.rect(screen, BAR_BACK, rect)
    fill = rect.copy()
    fill.width = round(rect.width * fraction)
    if fill.width > 0:
        pygame.draw.rect(screen, color, fill)
        light = tuple(min(255, c + 60) for c in color)
        dark = tuple(c * 3 // 5 for c in color)
        pygame.draw.line(screen, light, fill.topleft, (fill.right - 1, fill.top))
        if rect.height > 4:
            pygame.draw.line(screen, dark, (fill.left, fill.bottom - 1), (fill.right - 1, fill.bottom - 1))
    if marker is not None:
        x = rect.x + round(rect.width * min(max(marker, 0.0), 1.0))
        pygame.draw.line(screen, TEXT, (x, rect.y - 2), (x, rect.bottom + 1))
    if label:
        text(screen, label, rect.center, label_size, TEXT, anchor="center")


def button(
    screen: pygame.Surface, rect: pygame.Rect, label: str, *, selected: bool, size: int = 22,
    enabled: bool = True,
) -> None:
    """A menu entry: a tissue strip that glows red when selected."""
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill((*(SELECT if selected else PANEL), 235 if selected else 170))
    screen.blit(surface, rect.topleft)
    pygame.draw.rect(screen, SELECT_EDGE if selected else PANEL_EDGE, rect, 2 if selected else 1)
    if selected:  # little bone hooks left and right
        for x in (rect.x - 10, rect.right + 4):
            pygame.draw.rect(screen, STUD, (x, rect.centery - 3, 6, 6))
    color = TEXT if enabled else DIM
    text(screen, label, rect.center, size, GOLD if selected and enabled else color, heading=True, anchor="center")


# ----------------------------------------------------------------------- icons

PIXEL_ICONS: dict[str, tuple[str, ...]] = {
    "herz": (
        ".##.##.",
        "#######",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ),
    "fluegel": (
        "#.....#",
        "##...##",
        "###.###",
        ".#####.",
        "..#.#..",
    ),
    "tropfen": (
        "...#...",
        "..###..",
        ".#####.",
        ".#####.",
        "..###..",
    ),
    "perle": (
        ".###.",
        "##.##",
        "#####",
        ".###.",
    ),
    "phiole": (
        ".###.",
        "..#..",
        ".###.",
        "#####",
        "#####",
        ".###.",
    ),
    "auge": (
        "..###..",
        ".#...#.",
        "#..#..#",
        ".#...#.",
        "..###..",
    ),
}


@cache
def pixel_icon(name: str, color: Color, scale: int) -> pygame.Surface:
    rows = PIXEL_ICONS[name]
    surface = pygame.Surface((len(rows[0]) * scale, len(rows) * scale), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, code in enumerate(row):
            if code == "#":
                surface.fill(color, (x * scale, y * scale, scale, scale))
    return surface


@cache
def block_icon(key: str, size: int) -> pygame.Surface:
    """The block's 16x16 pixel icon scaled to ``size`` pixels."""
    pixels = icon_pixels(key)
    base = pygame.Surface((16, 16), pygame.SRCALPHA)
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            if color is not None:
                base.fill(color, (x, y, 1, 1))
    if size == 16:
        return base
    return pygame.transform.scale(base, (size, size))


# --------------------------------------------------------------------- tooltip

TOOLTIP_WIDTH = 300


def tooltip(
    screen: pygame.Surface, info: HoverInfo, anchor: tuple[int, int], *, width: int = TOOLTIP_WIDTH
) -> pygame.Rect:
    """Draw ``info`` in a panel next to ``anchor`` (kept inside the screen)."""
    size = 16
    pad = 10
    icon = 32 if info.block else 0
    text_width = width - 2 * pad - (icon + 8 if icon else 0)
    lines: list[tuple[str, Color]] = []
    for line in info.lines:
        lines += [(part, TEXT) for part in wrap(line, size - 1, text_width)]
    line_height = size + 3
    height = pad + 24 + len(lines) * line_height + pad
    if info.hp is not None:
        height += 16
    stats = wand_values(info.wand) if info.wand is not None else []
    if stats:
        height += len(stats) * 17 + 8
    height = max(height, icon + 2 * pad)
    x, y = anchor[0] + 18, anchor[1] + 18
    sw, sh = screen.get_size()
    if x + width > sw - 4:
        x = anchor[0] - width - 18
    if y + height > sh - 4:
        y = max(4, sh - height - 4)
    rect = panel(screen, (x, y, width, height), alpha=240)
    left = x + pad
    if icon:
        screen.blit(block_icon(info.block, icon), (left, y + pad))
        left += icon + 8
    text(screen, info.title, (left, y + pad), 18, info.color, heading=True)
    cy = y + pad + 24
    if info.hp is not None:
        current, maximum = info.hp
        bar(screen, (left, cy + 2, width - (left - x) - pad, 10), current / max(maximum, 1.0), ACCENT,
            label=f"{current:.0f} / {maximum:.0f}", label_size=12)
        cy += 16
    for line, color in lines:
        text(screen, line, (left, cy), size - 1, color)
        cy += line_height
    if stats:
        cy += 6
        wand_bars(screen, info.wand, info.compare, (x + pad, cy), width - 2 * pad)
    return rect


def wand_bars(
    screen: pygame.Surface, spec, other, pos: tuple[int, int], width: int, row: int = 17
) -> int:
    """Stat bars of a wand; with ``other`` each value is marked better or worse."""
    label_width = 92
    value_width = 62
    bar_width = max(30, width - label_width - value_width - 6)
    other_values = wand_values(other) if other is not None else None
    x, y = pos
    for index, (label, value, fill, higher, shown) in enumerate(wand_values(spec)):
        color = TEXT
        marker = None
        if other_values is not None:
            _l, other_value, other_fill, _h, _s = other_values[index]
            verdict = compare(value, other_value, higher)
            color = GOOD if verdict > 0 else BAD if verdict < 0 else TEXT
            marker = other_fill
        text(screen, label, (x, y), 14, DIM)
        bar(screen, (x + label_width, y + 4, bar_width, 7), fill, (176, 70, 70), marker=marker)
        text(screen, shown, (x + label_width + bar_width + 6, y), 14, color)
        y += row
    return y
