# V5–V8 – Sprite-Metadaten, Zeichnen, Prozedurale Körper, Werkzeug & Waffenteile

Verbindliche Schnittstellen für `src/sprites.py`, `src/sprite_render.py`, `src/procbody.py`, `tools/palette.py`, `tools/sprites.py` und `src/weapon_parts.py`.

---

## V5 Sprite-Metadaten und Animation (`src/sprites.py`, headless)

Kein `import pygame` in `src/sprites.py`.

```python
from pathlib import Path
from dataclasses import dataclass

SPRITE_ROOT = Path("assets/sprites_png")
LOOPING: frozenset[str] = frozenset({"idle", "move", "run", "float", "swim", "hang", "latched", "carry"})

@dataclass(frozen=True)
class SheetMeta:
    key: str
    frame_w: int
    frame_h: int
    anchor: tuple[int, int]                         # (ax, ay) Fuß-/Ankerpunkt im Frame
    hitbox: tuple[int, int, int, int]               # (hx, hy, hw, hh) relativ zur oberen linken Frame-Ecke
    states: dict[str, tuple[int, int, int]]         # state -> (first_frame_idx, frame_count, fps)
    glow: dict[int, tuple[tuple[int, int], ...]]    # frame_idx -> ((px, py), ...)
    mount: tuple[int, int] | None = None            # optionaler Andockpunkt für Waffenteile

def load_meta(path: Path) -> SheetMeta: ...
def find_meta(category: str, key: str, root: Path = SPRITE_ROOT) -> SheetMeta | None: ...

class Animator:
    def __init__(self, meta: SheetMeta) -> None: ...
    @property
    def state(self) -> str: ...
    def set_state(self, state: str, *, restart: bool = False) -> None: ...  # unbekannt -> "idle"
    def update(self, dt: float) -> None: ...
    @property
    def frame(self) -> int: ...                     # absoluter Frame-Index (0 .. total_frames - 1)
    @property
    def done(self) -> bool: ...                     # True, wenn state nicht in LOOPING und letztes Frame erreicht
```

- JSON-Schema in `assets/sprites_png/<category>/<key>.json`:

  ```json
  {
    "key": "aktenfresser",
    "frame_w": 20,
    "frame_h": 17,
    "anchor": [10, 16],
    "hitbox": [2, 1, 16, 16],
    "states": {"idle": [0, 2, 4], "move": [2, 4, 8], "hurt": [6, 1, 1], "death": [7, 3, 8]},
    "glow": {"0": [[14, 5]], "1": [[14, 6]]},
    "mount": [4, 3]
  }
  ```

- `"mount"` ist optional (`null` oder weggelassen → `None`).
- Fehlt ein Pflichtfeld (`key`, `frame_w`, `frame_h`, `anchor`, `hitbox`, `states`) oder ist `"idle"` nicht in `states`, wirft `load_meta` einen `ValueError`.
- `find_meta(category, key)` prüft `root / category / f"{key}.json"` (und dass die `.png` daneben existiert); fehlt eine davon, gibt sie `None` zurück.

---

## V6 Sprite-Zeichnen (`src/sprite_render.py`, pygame)

```python
import pygame
from src.sprites import SheetMeta

class SheetCache:
    def __init__(self, root: Path = SPRITE_ROOT) -> None: ...
    def surface(self, meta: SheetMeta, category: str = "") -> pygame.Surface: ...

def blit_frame(
    canvas: pygame.Surface,
    cache: SheetCache,
    meta: SheetMeta,
    frame: int,
    x: int,
    y: int,
    *,
    flip: bool = False,
    flash_white: bool = False,
    category: str = "",
) -> None: ...

def glow_points(
    meta: SheetMeta, frame: int, x: int, y: int, flip: bool = False
) -> list[tuple[int, int]]: ...
```

- `(x, y)` ist der **Bildschirm-/Kamera-relativ umgerechnete Ankerpunkt** (d. h. `world_anchor_x - camera_x`, `world_anchor_y - camera_y`).
- Linke obere Zeichenposition des Frames:
  - `flip == False`: `draw_x = x - meta.anchor[0]`, `draw_y = y - meta.anchor[1]`.
  - `flip == True`: `draw_x = x - (meta.frame_w - 1 - meta.anchor[0])`, `draw_y = y - meta.anchor[1]`.
- `glow_points` transformiert jedes `(gx, gy)` aus `meta.glow.get(frame, ())` nach derselben Spiegelungsformel in Welt- bzw. Kamerakoordinaten `(x + (meta.frame_w - 1 - gx - (meta.frame_w - 1 - meta.anchor[0]) if flip else gx - meta.anchor[0]), y + gy - meta.anchor[1])`.
- Für einen `Body` (`Creature` oder `Player`) gilt für den Welt-Ankerpunkt (Fußmitte):
  `world_anchor_x = int(body.x + body.width // 2)`, `world_anchor_y = int(body.y + body.height)`.

---

## V7 Prozedurale Körper aus Teilen (`src/procbody.py`, headless)

```python
from dataclasses import dataclass
from src.world import World

class Chain:
    """Segmente mit festem Abstand, die dem Kopf folgen (Würmer, Orgelaal, Schwänze)."""
    def __init__(self, count: int, spacing: float, x: float, y: float) -> None: ...
    def update(self, head_x: float, head_y: float) -> None: ...
    points: list[tuple[float, float]]   # Länge == count; points[0] == (head_x, head_y)

class Legs:
    """Schrittbeine mit festen Fußpunkten auf dem Boden."""
    def __init__(self, count: int, length: float, stride: float) -> None: ...
    def update(self, body_x: float, body_y: float, world: World) -> None: ...
    feet: list[tuple[float, float]]     # Länge == count

class Tentacle:
    """Gliederkette mit Sinus-Wellenbewegung und optionalem Greifziel."""
    def __init__(self, count: int, spacing: float, wave: float = 4.0, speed: float = 3.0) -> None: ...
    def update(
        self, root_x: float, root_y: float, t: float, reach: tuple[float, float] | None = None
    ) -> None: ...
    points: list[tuple[float, float]]   # Länge == count; points[0] == (root_x, root_y)

@dataclass(frozen=True)
class PartSpec:
    sprite_key: str                     # Schlüssel unter Kategorie "kreaturen" oder "bosse"
    attachment: str                     # "body" | "chain:<i>" | "tentacle:<t>:<i>" | "leg:<i>"
    offset: tuple[int, int] = (0, 0)    # Versatz relativ zum Ankerpunkt (bei flip wird offset[0] negiert)

@dataclass(frozen=True)
class PartLayout:
    key: str                            # Kreaturschlüssel, z. B. "orgelaal", "trampolinwal", "kirchenkrake"
    parts: tuple[PartSpec, ...]
    chain_count: int = 0
    chain_spacing: float = 6.0
    tentacles: int = 0
    tentacle_segments: int = 5
    tentacle_spacing: float = 5.0
    legs: int = 0
    leg_length: float = 10.0
    leg_stride: float = 8.0

LAYOUTS: dict[str, PartLayout] = {}
```

- Anbindung an `Creature`: Wenn `spec.key in LAYOUTS`, legt `Creature.__init__` eine Instanz `self.rig: ProcRig | None = ProcRig(LAYOUTS[spec.key], self.center[0], self.center[1])` an, die in `Creature.update` mit `(cx, cy, world, self.age)` aktualisiert wird und eine Methode `world_parts(cx: float, cy: float, facing: int) -> list[tuple[str, int, int, bool]]` (`(sprite_key, world_x, world_y, flip)`) für `rendering.py` bereitstellt.

---

## V8 Sprite-Quellen & Werkzeug (`tools/palette.py`, `tools/sprites.py`)

### 1. `tools/palette.py`

```python
PALETTE: dict[str, str] = {
    "ink": "#1C1420",
    "n1": "#2E2836", "n2": "#4A4452", "n3": "#77707E", "n4": "#A9A3AE", "n5": "#E6E2E8",
    "skin_l": "#F2CCA8", "skin": "#E0A982", "skin_d": "#B67A5C",
    "hair_l": "#FF9A4A", "hair": "#EC6E34", "hair_d": "#B34424",
    "coat_l": "#F6F7F2", "coat": "#D6DCD8", "coat_d": "#9AA6A8",
    "cloth": "#8C46AA", "cloth_d": "#5E2C78",
    "flux_l": "#B4FFF0", "flux": "#3CE6C8", "flux_d": "#1C9488",
    "gold_l": "#FFF09A", "gold": "#F2C230", "gold_d": "#A87A14",
    "danger_l": "#FF8A7A", "danger": "#E83A3A", "danger_d": "#9A1E28",
    "agent_l": "#9AA4C8", "agent": "#5A6490", "agent_d": "#333A5C",
    "metal_l": "#C8CED6", "metal": "#8A94A2", "metal_d": "#545C6A",
    "clone_l": "#FFE0EC", "clone": "#F6B4CC", "clone_d": "#D07EA0",
    "life_l": "#B8F59A", "life": "#6CD25A", "life_d": "#3A8A3C",
}
# Teilpaletten je Universum: Schlüssel "u1", "u2", ... in der Reihenfolge aus Bibel 03:
PALETTES: dict[str, dict[str, str]] = {
    "fleischwelt": {...},
    "aktenhalde": {...},
    "glibbria": {...},
    "kruemelreich": {...},
    "sporenklub": {...},
    "abtei": {...},
}
```

### 2. `tools/sprites.py`

Pflicht- und optionale Konstanten einer Sprite-Quelldatei `assets/sprites/<kategorie>/<key>.py`:

- Pflicht: `PALETTE: dict[str, str]`, `SIZE: tuple[int, int]`, `ANCHOR: tuple[int, int]`, `HITBOX: tuple[int, int, int, int]`, `FPS: dict[str, int]`, `FRAMES: dict[str, list[list[str]]]`.
- Optional: `UNIVERSE: str | None = None`, `GLOW: list[str] = []`, `STATIC: bool = False`, `ATTACKS: bool = False`, `MOUNT: tuple[int, int] | None = None`.
- Mindestzustände (`CATEGORY_MIN_STATES`):
  - Kategorien `ui`, `module`, `waffenteile`, `gegenstaende`, `effekte`: nur `("idle",)`.
  - Kategorie `werkstatt`: `("idle", "use")`.
  - Kategorie `npc`: `("idle", "talk")`.
  - Alle übrigen (`figuren`, `kreaturen`, `bosse`, `boese_ichs`): `("idle", "hurt", "death")` + `("move",)` (falls nicht `STATIC = True`) + `("windup", "attack")` (falls `ATTACKS = True`).

---

## V8b Waffenteile & Zusammenbau (`src/weapon_parts.py`, headless)

```python
from dataclasses import dataclass
from src.wand import WandSpec

@dataclass(frozen=True)
class WeaponPartPlacement:
    part_key: str               # Dateiname unter assets/sprites_png/waffenteile/<part_key>
    offset_x: int               # px relativ zum Griff-/Schulter-Anker der Waffe (nach rechts)
    offset_y: int               # px relativ zum Griff-/Schulter-Anker (nach unten)

def parts_for(spec: WandSpec, seed: int = 0) -> tuple[str, ...]:
    """Return (body, barrel, muzzle, tank, grip, charm) part keys for spec (bible 06)."""
    ...

def layout_for(spec: WandSpec, seed: int = 0) -> tuple[WeaponPartPlacement, ...]:
    """Compute pixel offsets for each part relative to the weapon's grip anchor (0, 0)."""
    ...
```

Zuordnungsregeln in `parts_for(spec, seed)`:

1. **Gehäuse (`body`):** `capacity <= 4` → `"gehaeuse_kurz"` (Breite 6), `5 <= capacity <= 8` → `"gehaeuse_mittel"` (Breite 9), `>= 9` → `"gehaeuse_lang"` (Breite 12).
2. **Lauf (`barrel`):** `casts <= 1` → `"lauf_einfach"`, `casts == 2` → `"lauf_doppel"`, `casts >= 3` → `"lauf_dreifach"`.
3. **Mündung (`muzzle`):** `spread <= 0.03` → `"muendung_spitz"`, `spread <= 0.08` → `"muendung_trichter"`, `> 0.08` → `"muendung_sieb"`.
4. **Tank (`tank`):** `mana_max < 140` → `"tank_klein"`, `mana_max <= 220` → `"tank_mittel"`, `> 220` → `"tank_gross"`.
5. **Griff (`grip`):** `cast_delay <= 0.12` → `"griff_pistole"`, `cast_delay <= 0.25` → `"griff_kurbel"`, `> 0.25` → `"griff_handschuh"`.
6. **Zierteil (`charm`):** `spec.shuffle == True` → `"zier_klebeband"`, sonst deterministisch über `random.Random(seed ^ hash(spec.name_de))` aus `("zier_antenne", "zier_wackelauge", "zier_gluehbirne", "zier_schraubenzieher")`.

Anker-Geometrie in `layout_for`:

- `grip` sitzt bei `(0, 2)`, `body` bei `(0, 0)` (Breite `bw` = 6/9/12), `tank` unter dem Gehäuse bei `(bw // 3, 3)`, `barrel` rechts am Gehäuse bei `(bw, 0)` (Breite `lw` = 4), `muzzle` bei `(bw + lw, 0)`, `charm` oben auf dem Gehäuse bei `(bw // 2, -2)`.
