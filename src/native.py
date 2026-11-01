"""Loads the Rust simulation core (``native/``) via ctypes, building it if needed.

The core has no dependencies besides the Rust standard library, so ``cargo`` is
the only tool required. Python keeps ownership of all buffers; the core reads and
writes them in place.
"""

from __future__ import annotations

import contextlib
import ctypes
import subprocess
import sys
from functools import cache
from pathlib import Path

from src import materials as mat
from src.materials import DECAY_INTO, MATERIALS
from src.reactions import build_tables, to_fixed

ABI_VERSION = 7
NATIVE_DIR = Path(__file__).resolve().parent.parent / "native"
LIBRARY_NAME = {
    "win32": "cloita_core.dll",
    "darwin": "libcloita_core.dylib",
}.get(sys.platform, "libcloita_core.so")

_u8p = ctypes.POINTER(ctypes.c_uint8)
_u16p = ctypes.POINTER(ctypes.c_uint16)
_i16p = ctypes.POINTER(ctypes.c_int16)
_size = ctypes.c_size_t


def library_path() -> Path:
    """Where the compiled core is expected (inside the bundle when frozen)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", ".")) / LIBRARY_NAME
    return NATIVE_DIR / "target" / "release" / LIBRARY_NAME


def _sources() -> list[Path]:
    return [NATIVE_DIR / "Cargo.toml", *sorted((NATIVE_DIR / "src").rglob("*.rs"))]


def needs_build() -> bool:
    """True if the library is missing or older than its sources."""
    if getattr(sys, "frozen", False):
        return False
    library = library_path()
    if not library.exists():
        return True
    built = library.stat().st_mtime
    return any(source.stat().st_mtime > built for source in _sources())


def build() -> None:
    """Compile the core with cargo (release profile)."""
    print("Baue den Simulationskern (Rust) ...", flush=True)
    command = ["cargo", "build", "--release", "--manifest-path", str(NATIVE_DIR / "Cargo.toml")]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            "Rust (cargo) wurde nicht gefunden. Installiere Rust über https://rustup.rs "
            "und starte das Spiel danach erneut."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "Der Simulationskern konnte nicht gebaut werden. Details stehen in der "
            "cargo-Ausgabe oben."
        ) from error
    # cargo leaves an up-to-date library untouched; mark it fresh so that newer source
    # timestamps (e.g. after a git checkout) do not trigger a build on every start.
    if library_path().exists():
        library_path().touch()


@cache
def load() -> ctypes.CDLL:
    """Return the loaded core, building it first if necessary."""
    if needs_build():
        build()
    library = ctypes.CDLL(str(library_path()))
    library.cloita_abi_version.restype = ctypes.c_uint32
    version = library.cloita_abi_version()
    if version != ABI_VERSION:
        raise RuntimeError(
            f"Der Simulationskern hat die falsche Version ({version}, erwartet {ABI_VERSION}). "
            "Bitte 'uv run build-native' ausführen."
        )
    library.cloita_new.restype = ctypes.c_void_p
    library.cloita_new.argtypes = [
        _size, _size, ctypes.c_uint64, _size,
        _u8p, _i16p, _u16p, _u8p, _u8p, _u8p, _u8p, _u8p, _u16p, _u8p, _u16p,
        _u8p, _u8p, _u16p,
    ]
    library.cloita_free.argtypes = [ctypes.c_void_p]
    library.cloita_seed.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
    library.cloita_step.restype = ctypes.c_uint32
    library.cloita_step.argtypes = [
        ctypes.c_void_p, _u8p, _u8p, _u8p, _size, _size, _size, _size,
    ]
    library.cloita_grain.argtypes = [_u8p, _size, _size, ctypes.c_uint64, ctypes.c_uint8]
    library.cloita_render_lit.argtypes = [
        _u8p, _u8p, _u8p, _size, _size, _size, _size, _size, ctypes.c_uint8, ctypes.c_uint8,
        _u8p, _u8p, _size, ctypes.POINTER(ctypes.c_float), _size, ctypes.c_float,
    ]  # fmt: skip
    library.cloita_reachable.restype = ctypes.c_uint32
    library.cloita_reachable.argtypes = [
        _u8p, _size, _size, _u8p, _size, _size, _size, _size, _size, _size, _size,
        ctypes.POINTER(_size), ctypes.POINTER(_size),
    ]  # fmt: skip
    library.cloita_loose.restype = ctypes.c_size_t
    library.cloita_loose.argtypes = [
        _u8p, _size, _size, _u8p, _size, _size, _size, _size, _size, _size, _size,
        ctypes.POINTER(ctypes.c_uint32), _u16p, _size,
    ]  # fmt: skip
    library.cloita_render.argtypes = [
        _u8p, _u8p, _u8p, _size, _size, _size, _size, _size, ctypes.c_uint8,
    ]
    return library


def _array(ctype: type, values: list[int]) -> ctypes.Array:
    return (ctype * len(values))(*values)


def byte_view(buffer: bytearray) -> ctypes.Array:
    """Zero-copy ctypes view of a bytearray (the bytearray must not be resized)."""
    return (ctypes.c_uint8 * len(buffer)).from_buffer(buffer)


class Core:
    """One simulation instance bound to a world's buffers."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int,
        grid: bytearray,
        life: bytearray,
        active: bytearray,
    ) -> None:
        self._lib = load()
        self._grid = byte_view(grid)
        self._life = byte_view(life)
        self._active = byte_view(active)
        react_a, react_b, react_chance = build_tables()
        u8, u16, i16 = ctypes.c_uint8, ctypes.c_uint16, ctypes.c_int16
        handle = self._lib.cloita_new(
            width,
            height,
            seed & 0xFFFF_FFFF_FFFF_FFFF,
            mat.MATERIAL_COUNT,
            _array(u8, [m.kind for m in MATERIALS]),
            _array(i16, [m.density for m in MATERIALS]),
            _array(u16, [to_fixed(m.flammability) for m in MATERIALS]),
            _array(u8, [m.burn_life[0] for m in MATERIALS]),
            _array(u8, [m.burn_life[1] for m in MATERIALS]),
            _array(u8, [m.life[0] for m in MATERIALS]),
            _array(u8, [m.life[1] for m in MATERIALS]),
            _array(u8, [m.fluidity for m in MATERIALS]),
            _array(u16, [65535 if m.mobility >= 1 else to_fixed(m.mobility) for m in MATERIALS]),
            _array(u8, DECAY_INTO),
            _array(u16, [to_fixed(m.decay_chance) for m in MATERIALS]),
            _array(u8, react_a),
            _array(u8, react_b),
            _array(u16, react_chance),
        )
        if not handle:
            raise RuntimeError("Der Simulationskern konnte nicht gestartet werden.")
        self._handle = ctypes.c_void_p(handle)

    def seed(self, seed: int) -> None:
        self._lib.cloita_seed(self._handle, seed & 0xFFFF_FFFF_FFFF_FFFF)

    def step(self, cx0: int, cy0: int, cx1: int, cy1: int) -> int:
        """Simulate the chunk rectangle [cx0, cx1) x [cy0, cy1). Returns chunks processed."""
        return self._lib.cloita_step(
            self._handle, self._grid, self._life, self._active, cx0, cy0, cx1, cy1
        )

    def close(self) -> None:
        if self._handle:
            self._lib.cloita_free(self._handle)
            self._handle = ctypes.c_void_p()

    def __del__(self) -> None:
        # At interpreter shutdown the library or ctypes globals may already be gone.
        with contextlib.suppress(AttributeError, TypeError, OSError):
            self.close()


def render(
    grid: ctypes.Array,
    noise: ctypes.Array,
    out: ctypes.Array,
    world_width: int,
    x0: int,
    y0: int,
    view_width: int,
    view_height: int,
    variants: int,
) -> None:
    """Write palette indices for a view rectangle into ``out``."""
    load().cloita_render(grid, noise, out, world_width, x0, y0, view_width, view_height, variants)


def grain(out: ctypes.Array, width: int, height: int, seed: int, variants: int) -> None:
    """Fill ``out`` with a smooth colour-variant texture (one byte per cell)."""
    load().cloita_grain(out, width, height, seed & 0xFFFF_FFFF_FFFF_FFFF, variants)


def render_lit(
    grid: ctypes.Array,
    noise: ctypes.Array,
    out: ctypes.Array,
    world_width: int,
    x0: int,
    y0: int,
    view_width: int,
    view_height: int,
    variants: int,
    levels: int,
    glow: list[int],
    lights: list[tuple[float, float, float, float]],
    ambient: float,
    opaque: list[int] | None = None,
) -> None:
    """Render with lighting: ``lights`` are (x, y, radius, intensity) in world pixels.

    ``opaque`` marks materials (1 per material) that block dynamic light.
    """
    flat = [value for light in lights for value in light]
    light_array = (ctypes.c_float * max(1, len(flat)))(*flat)
    load().cloita_render_lit(
        grid, noise, out, world_width, x0, y0, view_width, view_height, variants, levels,
        _array(ctypes.c_uint8, glow), _array(ctypes.c_uint8, opaque or [0] * len(glow)),
        len(glow), light_array, len(lights), ambient,
    )  # fmt: skip


def reachable(
    grid: ctypes.Array,
    width: int,
    height: int,
    blocking: list[int],
    box: tuple[int, int],
    start: tuple[int, int],
    goal: tuple[int, int],
) -> tuple[bool, tuple[int, int]]:
    """Can a box of size ``box`` move from ``start`` to ``goal`` through free cells?

    Returns (reached, closest reachable top-left position to the goal).
    """
    out_x, out_y = ctypes.c_size_t(), ctypes.c_size_t()
    found = load().cloita_reachable(
        grid, width, height, _array(ctypes.c_uint8, blocking), len(blocking),
        box[0], box[1], max(0, start[0]), max(0, start[1]), max(0, goal[0]), max(0, goal[1]),
        ctypes.byref(out_x), ctypes.byref(out_y),
    )  # fmt: skip
    return bool(found), (out_x.value, out_y.value)


def loose_groups(
    grid: ctypes.Array,
    width: int,
    height: int,
    rigid: list[int],
    centre: tuple[int, int],
    radius: int,
    reach: int,
    min_cells: int,
    max_cells: int,
    capacity: int = 8192,
) -> list[list[int]]:
    """Cell indices of free-hanging solid groups around ``centre`` (see ``cloita_loose``)."""
    out_index = (ctypes.c_uint32 * capacity)()
    out_group = (ctypes.c_uint16 * capacity)()
    count = load().cloita_loose(
        grid, width, height, _array(ctypes.c_uint8, rigid), len(rigid),
        max(0, centre[0]), max(0, centre[1]), radius, reach, min_cells, max_cells,
        out_index, out_group, capacity,
    )  # fmt: skip
    groups: dict[int, list[int]] = {}
    for k in range(count):
        groups.setdefault(out_group[k], []).append(out_index[k])
    return list(groups.values())
