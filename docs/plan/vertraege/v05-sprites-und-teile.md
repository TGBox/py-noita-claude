# V5–V8 – Sprite-Metadaten, Zeichnen, Prozedurale Körper, Werkzeug & Waffenteile

Verbindliche Schnittstellen für `src/sprites.py`, `src/sprite_render.py`, `src/procbody.py`, `tools/palette.py`, `tools/sprites.py` und `src/weapon_parts.py`.

---

## V5 Sprite-Metadaten und Animation (`src/sprites.py`, headless)

Kein `import pygame` in `src/sprites.py`.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AnimSpec:
    row: int
    frames: int
    fps: float = 8.0
    loop: bool = True
    next_anim: str = "idle"


@dataclass(frozen=True)
class GlowPoint:
    offset: tuple[int, int]
    color: tuple[int, int, int]
    radius: int = 12


@dataclass(frozen=True)
class SheetMeta:
    frame_size: tuple[int, int]
    anchor: tuple[int, int]
    anims: dict[str, AnimSpec] = field(default_factory=dict)
    glow: tuple[GlowPoint, ...] = ()


def load_sheet_meta(json_path: Path) -> SheetMeta:
    """Load SheetMeta from a JSON sidecar file."""
    ...


class Animator:
    def __init__(self, meta: SheetMeta, initial: str = "idle") -> None:
        self.meta: SheetMeta = meta
        self.state: str = initial
        self.frame_index: int = 0
        self.timer: float = 0.0
        self.finished: bool = False

    def play(self, state: str, *, restart: bool = False) -> None:
        """Switch to animation state (ignored if already in state unless restart=True)."""
        ...

    def update(self, dt: float) -> None:
        """Advance animation timer and frame_index by dt seconds."""
        ...

    def frame_rect(self) -> tuple[int, int, int, int]:
        """Return (x, y, w, h) pixel rectangle on the sprite sheet."""
        ...
```

- **JSON-Sidecar-Format (`<name>.json`):**

  ```json
  {
    "frame_size": [16, 20],
    "anchor": [8, 18],
    "anims": {
      "idle": {"row": 0, "frames": 4, "fps": 6.0, "loop": true},
      "attack": {"row": 1, "frames": 3, "fps": 10.0, "loop": false, "next_anim": "idle"}
    },
    "glow": [{"offset": [2, -6], "color": [120, 240, 200], "radius": 14}]
  }
  ```

- `Animator.play(state, restart=False)` wechselt in `state` (oder fällt auf `"idle"` zurück, falls `state` unbekannt ist). Wenn `loop == False`, stoppt die Animation am letzten Frame, setzt `finished = True` und wechselt automatisch nach `next_anim` (`"idle"`).

---

## V6 Sprite-Zeichnen (`src/sprite_render.py`, pygame)

```python
from __future__ import annotations

from pathlib import Path
import pygame
from .sprites import Animator, SheetMeta

ASSET_ROOT: Path = Path(__file__).resolve().parent.parent / "assets" / "sprites"


class SheetCache:
    def __init__(self, root: Path = ASSET_ROOT) -> None:
        self.root: Path = root
        self._cache: dict[tuple[str, str], tuple[pygame.Surface, SheetMeta]] = {}

    def get(self, category: str, name: str) -> tuple[pygame.Surface, SheetMeta]:
        """Return cached (Surface, SheetMeta) for category/name, with headless fallback."""
        ...


def blit_frame(
    target: pygame.Surface,
    sheet: pygame.Surface,
    meta: SheetMeta,
    animator: Animator,
    world_x: float,
    world_y: float,
    cam_x: float,
    cam_y: float,
    *,
    flip_x: bool = False,
    angle_deg: float = 0.0,
    flash: float = 0.0,
    tint: tuple[int, int, int] | None = None,
) -> None:
    """Blit the current animator frame anchored at (world_x - cam_x, world_y - cam_y)."""
    ...


def glow_points(
    meta: SheetMeta,
    world_x: float,
    world_y: float,
    flip_x: bool = False,
) -> list[tuple[float, float, tuple[int, int, int], int]]:
    """Return world-space glow tuples (wx, wy, color, radius) for meta.glow."""
    ...
```

- Bei `flip_x == True` wird `offset[0]` in `glow_points` horizontal gespiegelt (`world_x - offset[0]`, sonst `world_x + offset[0]`).

---

## V7 Prozedurale Körper aus Teilen (`src/procbody.py`, headless)

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chain:
    segments: list[tuple[float, float]] = field(default_factory=list)
    spacing: float = 6.0

    def update(self, head_x: float, head_y: float) -> list[tuple[float, float]]:
        """Pull chain segments towards (head_x, head_y) keeping spacing distance."""
        ...


@dataclass
class Legs:
    count: int = 4
    stride: float = 8.0
    step_height: float = 3.0
    phase: float = 0.0

    def update(
        self,
        dt: float,
        body_x: float,
        body_y: float,
        vx: float = 0.0,
    ) -> list[tuple[float, float, float, float]]:
        """Return (hip_x, hip_y, foot_x, foot_y) tuples for each leg."""
        ...


@dataclass
class Tentacle:
    segments: int = 5
    length: float = 20.0
    amp: float = 4.0
    freq: float = 3.0
    phase: float = 0.0

    def points(self, root_x: float, root_y: float, time: float) -> list[tuple[float, float]]:
        """Return segments + 1 points starting at (root_x, root_y)."""
        ...


@dataclass(frozen=True)
class PartSpec:
    key: str
    offset: tuple[float, float]
    z_order: int = 0
    sheet_name: str = ""
    bob_amp: float = 1.0
    bob_freq: float = 2.5
    destructible: bool = False


@dataclass(frozen=True)
class PartLayout:
    parts: tuple[PartSpec, ...] = ()


class ProcRig:
    def __init__(self, layout: PartLayout) -> None:
        self.layout: PartLayout = layout
        self.time: float = 0.0
        self.destroyed: set[str] = set()
        self.recoils: dict[str, float] = {}

    def update(self, dt: float, vx: float = 0.0, vy: float = 0.0, facing: int = 1) -> None: ...
    def recoil(self, part_key: str, amount: float) -> None: ...
    def destroy_part(self, part_key: str) -> None: ...
    def world_parts(
        self,
        root_x: float,
        root_y: float,
        flip_x: bool = False,
    ) -> list[tuple[str, float, float, str]]:
        """Return z-ordered (part_key, wx, wy, sheet_name) for all non-destroyed parts."""
        ...


RIG_LAYOUTS: dict[str, PartLayout] = {}
```

---

## V8 Sprite-Quellen & Werkzeug (`tools/palette.py`, `tools/sprites.py`)

### 1. Farbpaletten (`tools/palette.py`)

```python
OUTLINE_DARK: tuple[int, int, int, int] = (18, 14, 24, 255)


@dataclass(frozen=True)
class PaletteRamp:
    shadow: tuple[int, int, int, int]
    mid: tuple[int, int, int, int]
    light: tuple[int, int, int, int]
    highlight: tuple[int, int, int, int]
    rim: tuple[int, int, int, int]


def make_ramp(base_rgb: tuple[int, int, int]) -> PaletteRamp:
    """Create a 5-stop PaletteRamp from base_rgb with monotonically increasing brightness."""
    ...


UNIVERSE_PALETTES: dict[str, dict[str, PaletteRamp]] = {
    # Enthält mindestens alle 6 MVP-Universen ("fleischwelt", "aktenhalde", "glibbria",
    # "kruemelreich", "sporenklub", "abtei") sowie die Pool-Universen ("schrott", "kuchen", "spule")
    ...
}

ENTITY_PALETTES: dict[str, dict[str, PaletteRamp]] = {
    # "player", "klonita", "authority", "evil_kaiserin", "evil_gute", "evil_omega", "ober_cloita"
    ...
}
```

### 2. Pixel-Canvas & Sprite-Builder (`tools/sprites.py`)

```python
class PixelCanvas:
    def __init__(self, width: int, height: int) -> None: ...
    def set_px(self, x: int, y: int, rgba: tuple[int, int, int, int]) -> None: ...
    def get_px(self, x: int, y: int) -> tuple[int, int, int, int]: ...

def draw_shaded_ellipse(canvas: PixelCanvas, cx: int, cy: int, rx: int, ry: int, ramp: PaletteRamp) -> None: ...
def draw_shaded_rect(canvas: PixelCanvas, x0: int, y0: int, x1: int, y1: int, ramp: PaletteRamp) -> None: ...
def draw_segment_line(canvas: PixelCanvas, x0: int, y0: int, x1: int, y1: int, rgba: tuple[int, int, int, int], thickness: int = 1) -> None: ...
def apply_dark_outline(canvas: PixelCanvas) -> None: ...
def add_dither(canvas: PixelCanvas, intensity: int = 8) -> None: ...
def save_sheet(
    category: str,
    name: str,
    frames: dict[str, list[PixelCanvas]],
    *,
    anchor: tuple[int, int],
    fps: dict[str, float] | None = None,
    loops: dict[str, bool] | None = None,
    next_anims: dict[str, str] | None = None,
    glow: list[dict[str, object]] | None = None,
    out_dir: Path = ASSET_ROOT,
) -> tuple[Path, Path]: ...
def build_all(out_dir: Path = ASSET_ROOT) -> list[Path]: ...
```

---

## V8b Waffenteile & Zusammenbau (`src/weapon_parts.py`, headless)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .spells import Wand

WEAPON_PART_KEYS: tuple[str, ...] = (
    # Kanonische Bibel-Waffenteile (Kap. 06) + kompakte Stab-Teile:
    "griff_holz",
    "griff_eisen",
    "griff_knochen",
    "griff_pistole",
    "griff_kurbel",
    "griff_handschuh",
    "gehaeuse_kurz",
    "gehaeuse_mittel",
    "gehaeuse_lang",
    "kern_rubin",
    "kern_spule",
    "kern_auge",
    "kern_leere",
    "lauf_einfach",
    "lauf_doppel",
    "lauf_dreifach",
    "muendung_spitz",
    "muendung_trichter",
    "muendung_sieb",
    "spitz_prisma",
    "spitz_gabel",
    "spitz_zahn",
    "tank_klein",
    "tank_mittel",
    "tank_gross",
    "zier_antenne",
    "zier_wackelauge",
    "zier_gluehbirne",
    "zier_schraubenzieher",
    "zier_klebeband",
)


@dataclass(frozen=True)
class WeaponPartPlacement:
    part_key: str
    offset_x: int
    offset_y: int


def parts_for(wand: Wand) -> list[str]:
    """Select >= 3 valid WEAPON_PART_KEYS for wand based on its stats and blocks."""
    ...


def layout_for(wand: Wand) -> list[WeaponPartPlacement]:
    """Return ordered WeaponPartPlacement entries with ascending offset_x."""
    ...
```
