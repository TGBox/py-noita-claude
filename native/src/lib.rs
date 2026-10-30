//! Cloita simulation core.
//!
//! A falling-sand cellular automaton exposed through a small C ABI and loaded from
//! Python with `ctypes`. Python owns every buffer (cells, lifetimes, chunk flags) and
//! all material data; this library only applies the rules to those buffers.
//!
//! The world is split into 16x16 chunks. Only chunks whose flag is set in `active`
//! are simulated; a chunk that settles clears its flag and goes to sleep until a
//! neighbouring change wakes it again.

use std::slice;

const CHUNK_SHIFT: usize = 4;
const CHUNK_MASK: usize = (1 << CHUNK_SHIFT) - 1;
const AIR: u8 = 0;

// Material kinds, must match `src/materials.py`.
const EMPTY: u8 = 0;
const POWDER: u8 = 2;
const LIQUID: u8 = 3;
const GAS: u8 = 4;
const FLAME: u8 = 5;

// Probabilities are 16-bit fixed point: `p * 65536`.
const GAS_RISE: u16 = 22_938; // 0.35
const GAS_DRIFT: u16 = 39_322; // 0.60 (cumulative)
const EMBER_RISE: u16 = 9_830; // 0.15
const EMBER_SMOKE: u16 = 11_796; // 0.18 (cumulative)
const NEIGHBORS: [(isize, isize); 4] = [(0, -1), (0, 1), (-1, 0), (1, 0)];

/// Per-material rules, copied once from Python.
struct Rules {
    n: usize,
    kind: Vec<u8>,
    flammability: Vec<u16>,
    burn_lo: Vec<u8>,
    burn_hi: Vec<u8>,
    life_lo: Vec<u8>,
    life_hi: Vec<u8>,
    fluidity: Vec<u8>,
    mobility: Vec<u16>,
    decay_into: Vec<u8>,
    decay_chance: Vec<u16>,
    /// Reaction table, indexed `actor * n + neighbour`.
    react_a: Vec<u8>,
    react_b: Vec<u8>,
    react_chance: Vec<u16>,
    /// Derived: `fall[m * n + t]` - may falling material `m` swap into `t`?
    fall: Vec<bool>,
    /// Derived: `rise[m * n + t]` - may gas `m` swap into `t`?
    rise: Vec<bool>,
    /// Derived: does this material take part in any reaction as the actor?
    actor: Vec<bool>,
    fire: u8,
}

pub struct Sim {
    rules: Rules,
    w: usize,
    h: usize,
    chunks_x: usize,
    chunks_y: usize,
    rng: u64,
    tick: u32,
    stamp: Vec<u32>,
    order: Vec<(usize, usize)>,
}

/// Mutable views of the Python-owned buffers for one step.
struct Buffers<'a> {
    grid: &'a mut [u8],
    life: &'a mut [u8],
    active: &'a mut [u8],
}

impl Sim {
    #[inline]
    fn next(&mut self) -> u64 {
        // xorshift64*
        let mut x = self.rng;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.rng = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }

    #[inline]
    fn roll(&mut self) -> u16 {
        (self.next() >> 48) as u16
    }

    #[inline]
    fn chance(&mut self, p: u16) -> bool {
        p != 0 && self.roll() < p
    }

    #[inline]
    fn side(&mut self) -> isize {
        if self.next() >> 63 == 0 {
            -1
        } else {
            1
        }
    }

    #[inline]
    fn range(&mut self, lo: u8, hi: u8) -> u8 {
        if hi <= lo {
            lo
        } else {
            lo + (self.next() % (u64::from(hi - lo) + 1)) as u8
        }
    }

    #[inline]
    fn new_life(&mut self, m: u8) -> u8 {
        let (lo, hi) = (self.rules.life_lo[m as usize], self.rules.life_hi[m as usize]);
        self.range(lo, hi)
    }

    fn wake(&self, active: &mut [u8], x: usize, y: usize) {
        let (cx, cy) = (x >> CHUNK_SHIFT, y >> CHUNK_SHIFT);
        let (lx, ly) = (x & CHUNK_MASK, y & CHUNK_MASK);
        let x_lo = if lx == 0 && cx > 0 { cx - 1 } else { cx };
        let x_hi = if lx == CHUNK_MASK && cx + 1 < self.chunks_x { cx + 1 } else { cx };
        let y_lo = if ly == 0 && cy > 0 { cy - 1 } else { cy };
        let y_hi = if ly == CHUNK_MASK && cy + 1 < self.chunks_y { cy + 1 } else { cy };
        for b in y_lo..=y_hi {
            for a in x_lo..=x_hi {
                active[b * self.chunks_x + a] = 1;
            }
        }
    }

    /// Replace the cell at `i` and give it a fresh lifetime.
    #[inline]
    fn put(&mut self, buf: &mut Buffers, i: usize, m: u8) {
        buf.grid[i] = m;
        buf.life[i] = self.new_life(m);
        self.stamp[i] = self.tick;
        self.wake(buf.active, i % self.w, i / self.w);
    }

    fn swap(&mut self, buf: &mut Buffers, i: usize, j: usize) {
        buf.grid.swap(i, j);
        buf.life.swap(i, j);
        self.stamp[i] = self.tick;
        self.stamp[j] = self.tick;
        self.wake(buf.active, i % self.w, i / self.w);
        self.wake(buf.active, j % self.w, j / self.w);
    }

    fn ignite(&mut self, buf: &mut Buffers, j: usize, fuel: u8) {
        let (lo, hi) = (self.rules.burn_lo[fuel as usize], self.rules.burn_hi[fuel as usize]);
        buf.grid[j] = self.rules.fire;
        buf.life[j] = self.range(lo, hi);
        self.stamp[j] = self.tick;
        self.wake(buf.active, j % self.w, j / self.w);
    }

    #[inline]
    fn neighbour(&self, x: usize, y: usize, d: (isize, isize)) -> Option<usize> {
        let nx = x as isize + d.0;
        let ny = y as isize + d.1;
        if nx < 0 || ny < 0 || nx as usize >= self.w || ny as usize >= self.h {
            None
        } else {
            Some(ny as usize * self.w + nx as usize)
        }
    }

    fn step(&mut self, buf: &mut Buffers, region: (usize, usize, usize, usize)) -> u32 {
        self.tick = self.tick.wrapping_add(1);
        if self.tick == 0 {
            self.stamp.iter_mut().for_each(|s| *s = 0);
            self.tick = 1;
        }
        let (cx0, cy0) = (region.0.min(self.chunks_x), region.1.min(self.chunks_y));
        let (cx1, cy1) = (region.2.min(self.chunks_x), region.3.min(self.chunks_y));
        let mut order = std::mem::take(&mut self.order);
        order.clear();
        for cy in (cy0..cy1).rev() {
            for cx in cx0..cx1 {
                let k = cy * self.chunks_x + cx;
                if buf.active[k] != 0 {
                    buf.active[k] = 0;
                    order.push((cx, cy));
                }
            }
        }
        for &(cx, cy) in &order {
            if self.update_chunk(buf, cx, cy) {
                buf.active[cy * self.chunks_x + cx] = 1;
            }
        }
        let count = order.len() as u32;
        self.order = order;
        count
    }

    /// Simulate one chunk bottom-up. Returns true if it must stay awake.
    fn update_chunk(&mut self, buf: &mut Buffers, cx: usize, cy: usize) -> bool {
        let x0 = cx << CHUNK_SHIFT;
        let x1 = (x0 + CHUNK_MASK + 1).min(self.w);
        let y0 = cy << CHUNK_SHIFT;
        let y1 = (y0 + CHUNK_MASK + 1).min(self.h);
        let forward = self.tick & 1 == 1;
        let mut keep = false;
        for y in (y0..y1).rev() {
            for k in 0..(x1 - x0) {
                let x = if forward { x0 + k } else { x1 - 1 - k };
                let i = y * self.w + x;
                let m = buf.grid[i];
                if m == AIR || self.stamp[i] == self.tick {
                    continue;
                }
                let mi = m as usize;
                let kind = self.rules.kind[mi];
                if self.rules.actor[mi] {
                    let (changed, partner) = self.react(buf, i, x, y, m);
                    keep |= partner;
                    if changed {
                        continue;
                    }
                }
                match kind {
                    POWDER => self.fall(buf, i, x, y, m, 0),
                    LIQUID => {
                        let mobility = self.rules.mobility[mi];
                        if mobility < u16::MAX {
                            keep = true;
                            if !self.chance(mobility) {
                                continue;
                            }
                        }
                        let spread = self.rules.fluidity[mi];
                        self.fall(buf, i, x, y, m, spread);
                    }
                    GAS => {
                        keep = true;
                        self.gas(buf, i, x, y, m);
                    }
                    FLAME => {
                        keep = true;
                        self.flame(buf, i, x, y);
                    }
                    _ => {}
                }
            }
        }
        keep
    }

    /// Try the reaction table against all four neighbours.
    /// Returns (cell changed, a reaction partner is adjacent).
    fn react(&mut self, buf: &mut Buffers, i: usize, x: usize, y: usize, m: u8) -> (bool, bool) {
        let n = self.rules.n;
        let mut partner = false;
        let start = (self.next() & 3) as usize;
        for k in 0..4 {
            let Some(j) = self.neighbour(x, y, NEIGHBORS[(start + k) & 3]) else {
                continue;
            };
            let t = buf.grid[j] as usize;
            let rule = m as usize * n + t;
            let p = self.rules.react_chance[rule];
            if p == 0 {
                continue;
            }
            partner = true;
            if self.stamp[j] != self.tick && self.chance(p) {
                let (a, b) = (self.rules.react_a[rule], self.rules.react_b[rule]);
                if b != t as u8 {
                    self.put(buf, j, b);
                }
                if a != m {
                    self.put(buf, i, a);
                    return (true, true);
                }
                self.stamp[i] = self.tick;
                return (false, true);
            }
        }
        (false, partner)
    }

    /// Powders and liquids: fall, slide diagonally, then (liquids) spread sideways.
    fn fall(&mut self, buf: &mut Buffers, i: usize, x: usize, y: usize, m: u8, spread: u8) {
        let n = self.rules.n;
        let w = self.w;
        let row = m as usize * n;
        if y + 1 < self.h {
            let below = i + w;
            if self.rules.fall[row + buf.grid[below] as usize] {
                self.swap(buf, i, below);
                return;
            }
            let first = self.side();
            for dx in [first, -first] {
                let nx = x as isize + dx;
                if nx >= 0 && (nx as usize) < w {
                    let j = (below as isize + dx) as usize;
                    if self.rules.fall[row + buf.grid[j] as usize] {
                        self.swap(buf, i, j);
                        return;
                    }
                }
            }
        }
        if spread == 0 {
            return;
        }
        let first = self.side();
        for dx in [first, -first] {
            let mut far = 0isize;
            for k in 1..=spread as isize {
                let nx = x as isize + dx * k;
                if nx < 0 || nx as usize >= w {
                    break;
                }
                let t = buf.grid[y * w + nx as usize];
                let tk = self.rules.kind[t as usize];
                if tk == EMPTY || tk == GAS {
                    far = k;
                } else {
                    break;
                }
            }
            if far > 0 {
                let j = y * w + (x as isize + dx * far) as usize;
                self.swap(buf, i, j);
                return;
            }
        }
    }

    /// Decay a cell whose lifetime ran out.
    fn decay(&mut self, buf: &mut Buffers, i: usize, m: u8) {
        let mi = m as usize;
        let into = if self.chance(self.rules.decay_chance[mi]) {
            self.rules.decay_into[mi]
        } else {
            AIR
        };
        self.put(buf, i, into);
    }

    /// Gases: rise, drift and dissipate.
    fn gas(&mut self, buf: &mut Buffers, i: usize, x: usize, y: usize, m: u8) {
        if buf.life[i] <= 1 {
            self.decay(buf, i, m);
            return;
        }
        buf.life[i] -= 1;
        let row = m as usize * self.rules.n;
        let roll = self.roll();
        let side = self.side();
        let w = self.w;
        if roll < GAS_RISE {
            if y == 0 {
                return;
            }
            let up = i - w;
            if self.rules.rise[row + buf.grid[up] as usize] {
                self.swap(buf, i, up);
                return;
            }
            let nx = x as isize + side;
            if nx >= 0 && (nx as usize) < w {
                let j = (up as isize + side) as usize;
                if self.rules.rise[row + buf.grid[j] as usize] {
                    self.swap(buf, i, j);
                }
            }
        } else if roll < GAS_DRIFT {
            let nx = x as isize + side;
            if nx >= 0 && (nx as usize) < w {
                let j = (i as isize + side) as usize;
                if self.rules.rise[row + buf.grid[j] as usize] {
                    self.swap(buf, i, j);
                }
            }
        }
    }

    /// Fire: burn down, ignite flammable neighbours, drift upwards as embers.
    fn flame(&mut self, buf: &mut Buffers, i: usize, x: usize, y: usize) {
        let fire = self.rules.fire;
        if buf.life[i] <= 1 {
            self.decay(buf, i, fire);
            return;
        }
        buf.life[i] -= 1;
        let mut near_fuel = false;
        let mut above = None;
        for (k, d) in NEIGHBORS.iter().enumerate() {
            let Some(j) = self.neighbour(x, y, *d) else {
                continue;
            };
            let t = buf.grid[j];
            let p = self.rules.flammability[t as usize];
            if p != 0 {
                near_fuel = true;
                if self.stamp[j] != self.tick && self.chance(p) {
                    self.ignite(buf, j, t);
                }
            } else if t == AIR && k == 0 {
                above = Some(j);
            }
        }
        let Some(up) = above else {
            return;
        };
        if near_fuel {
            return;
        }
        let roll = self.roll();
        if roll < EMBER_RISE {
            self.swap(buf, i, up);
        } else if roll < EMBER_SMOKE {
            let smoke = self.rules.decay_into[fire as usize];
            self.put(buf, up, smoke);
        }
    }
}

unsafe fn copy<T: Copy>(ptr: *const T, len: usize) -> Vec<T> {
    slice::from_raw_parts(ptr, len).to_vec()
}

/// Version of the C ABI, checked by Python on load.
#[no_mangle]
pub extern "C" fn cloita_abi_version() -> u32 {
    5
}

/// Create a simulation for a `w` x `h` world with `n` materials.
///
/// # Safety
/// Every pointer must reference `n` (per-material) or `n * n` (reaction table)
/// readable elements. The data is copied, the pointers are not retained.
#[no_mangle]
pub unsafe extern "C" fn cloita_new(
    w: usize,
    h: usize,
    seed: u64,
    n: usize,
    kind: *const u8,
    density: *const i16,
    flammability: *const u16,
    burn_lo: *const u8,
    burn_hi: *const u8,
    life_lo: *const u8,
    life_hi: *const u8,
    fluidity: *const u8,
    mobility: *const u16,
    decay_into: *const u8,
    decay_chance: *const u16,
    react_a: *const u8,
    react_b: *const u8,
    react_chance: *const u16,
) -> *mut Sim {
    let kind = copy(kind, n);
    let density = copy(density, n);
    let react_chance = copy(react_chance, n * n);
    let mut fall = vec![false; n * n];
    let mut rise = vec![false; n * n];
    for m in 0..n {
        for t in 0..n {
            let open = matches!(kind[t], EMPTY | LIQUID | GAS);
            fall[m * n + t] = matches!(kind[m], POWDER | LIQUID) && open && density[t] < density[m];
            rise[m * n + t] = kind[m] == GAS && open && density[t] > density[m];
        }
    }
    let actor = (0..n).map(|m| react_chance[m * n..(m + 1) * n].iter().any(|&p| p != 0)).collect();
    let fire = kind.iter().position(|&k| k == FLAME).unwrap_or(0) as u8;
    let rules = Rules {
        n,
        kind,
        flammability: copy(flammability, n),
        burn_lo: copy(burn_lo, n),
        burn_hi: copy(burn_hi, n),
        life_lo: copy(life_lo, n),
        life_hi: copy(life_hi, n),
        fluidity: copy(fluidity, n),
        mobility: copy(mobility, n),
        decay_into: copy(decay_into, n),
        decay_chance: copy(decay_chance, n),
        react_a: copy(react_a, n * n),
        react_b: copy(react_b, n * n),
        react_chance,
        fall,
        rise,
        actor,
        fire,
    };
    let chunks_x = (w + CHUNK_MASK) >> CHUNK_SHIFT;
    let chunks_y = (h + CHUNK_MASK) >> CHUNK_SHIFT;
    let sim = Sim {
        rules,
        w,
        h,
        chunks_x,
        chunks_y,
        rng: 0,
        tick: 0,
        stamp: vec![0; w * h],
        order: Vec::new(),
    };
    let mut boxed = Box::new(sim);
    cloita_seed(boxed.as_mut(), seed);
    Box::into_raw(boxed)
}

/// # Safety
/// `sim` must come from `cloita_new` and must not be used afterwards.
#[no_mangle]
pub unsafe extern "C" fn cloita_free(sim: *mut Sim) {
    if !sim.is_null() {
        drop(Box::from_raw(sim));
    }
}

/// Reseed the random generator (deterministic replays and tests).
///
/// # Safety
/// `sim` must be a live pointer from `cloita_new`.
#[no_mangle]
pub unsafe extern "C" fn cloita_seed(sim: *mut Sim, seed: u64) {
    let sim = &mut *sim;
    // splitmix64 so that small seeds still give well-mixed, non-zero states
    let mut z = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^= z >> 31;
    sim.rng = if z == 0 { 0x1234_5678 } else { z };
}

/// Advance the chunks inside the chunk rectangle [cx0, cx1) x [cy0, cy1) by one tick.
/// Returns the number of chunks that were simulated.
///
/// # Safety
/// `grid` and `life` must point to `w * h` bytes, `active` to one byte per chunk.
#[no_mangle]
pub unsafe extern "C" fn cloita_step(
    sim: *mut Sim,
    grid: *mut u8,
    life: *mut u8,
    active: *mut u8,
    cx0: usize,
    cy0: usize,
    cx1: usize,
    cy1: usize,
) -> u32 {
    let sim = &mut *sim;
    let cells = sim.w * sim.h;
    let mut buf = Buffers {
        grid: slice::from_raw_parts_mut(grid, cells),
        life: slice::from_raw_parts_mut(life, cells),
        active: slice::from_raw_parts_mut(active, sim.chunks_x * sim.chunks_y),
    };
    sim.step(&mut buf, (cx0, cy0, cx1, cy1))
}

/// Write palette indices (`material * variants + noise`) for a view rectangle.
///
/// # Safety
/// `grid` and `noise` must cover the `w`-wide world, `out` must hold `vw * vh`
/// bytes, and the rectangle must lie inside the world.
#[no_mangle]
pub unsafe extern "C" fn cloita_render(
    grid: *const u8,
    noise: *const u8,
    out: *mut u8,
    w: usize,
    x0: usize,
    y0: usize,
    vw: usize,
    vh: usize,
    variants: u8,
) {
    let out = slice::from_raw_parts_mut(out, vw * vh);
    for r in 0..vh {
        let src = (y0 + r) * w + x0;
        let cells = slice::from_raw_parts(grid.add(src), vw);
        let grain = slice::from_raw_parts(noise.add(src), vw);
        let dst = &mut out[r * vw..(r + 1) * vw];
        for c in 0..vw {
            dst[c] = cells[c].wrapping_mul(variants).wrapping_add(grain[c]);
        }
    }
}

#[inline]
fn hash2(x: i64, y: i64, seed: u64) -> f32 {
    let mut h = seed
        ^ (x as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15)
        ^ (y as u64).wrapping_mul(0xC2B2_AE3D_27D4_EB4F);
    h ^= h >> 33;
    h = h.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    h ^= h >> 33;
    (h >> 40) as f32 / (1u64 << 24) as f32
}

/// Smooth value noise in [0, 1) with cells of `scale` pixels.
fn value_noise(x: usize, y: usize, scale: f32, seed: u64) -> f32 {
    let fx = x as f32 / scale;
    let fy = y as f32 / scale;
    let (ix, iy) = (fx.floor() as i64, fy.floor() as i64);
    let (tx, ty) = (fx - ix as f32, fy - iy as f32);
    let (sx, sy) = (tx * tx * (3.0 - 2.0 * tx), ty * ty * (3.0 - 2.0 * ty));
    let top = hash2(ix, iy, seed) * (1.0 - sx) + hash2(ix + 1, iy, seed) * sx;
    let bottom = hash2(ix, iy + 1, seed) * (1.0 - sx) + hash2(ix + 1, iy + 1, seed) * sx;
    top * (1.0 - sy) + bottom * sy
}

/// Fill `out` (w * h bytes) with a colour variant per cell: two octaves of smooth
/// value noise, slightly domain-warped for a fibrous look, plus fine dither.
///
/// # Safety
/// `out` must point to `w * h` writable bytes.
#[no_mangle]
pub unsafe extern "C" fn cloita_grain(out: *mut u8, w: usize, h: usize, seed: u64, variants: u8) {
    let out = slice::from_raw_parts_mut(out, w * h);
    let levels = f32::from(variants.max(1));
    for y in 0..h {
        for x in 0..w {
            let warp = value_noise(x, y, 40.0, seed ^ 0xA5A5) * 18.0;
            let wx = x + warp as usize;
            let coarse = value_noise(wx, y, 22.0, seed);
            let fine = value_noise(x, y + warp as usize / 2, 6.0, seed ^ 0x5A5A);
            let dither = hash2(x as i64, y as i64, seed ^ 0xD17) - 0.5;
            let v = (coarse * 0.62 + fine * 0.3 + dither * 0.16 + 0.04).clamp(0.0, 0.999);
            out[y * w + x] = (v * levels) as u8;
        }
    }
}

const LIGHT_CELL: usize = 4; // light map resolution in pixels
const OCCLUSION: f32 = 0.55; // light lost per fully opaque light-map cell
const EMISSIVE_RADIUS: f32 = 6.0; // light map cells
const BAYER: [f32; 16] = [
    0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0,
];

/// Add a light whose rays are dimmed by opaque light-map cells on the way.
#[allow(clippy::too_many_arguments)]
fn splat_occluded(
    light: &mut [f32],
    opacity: &[f32],
    gw: usize,
    gh: usize,
    cx: f32,
    cy: f32,
    radius: f32,
    intensity: f32,
) {
    let x0 = (cx - radius).floor().max(0.0) as usize;
    let y0 = (cy - radius).floor().max(0.0) as usize;
    let x1 = ((cx + radius).ceil().max(0.0) as usize).min(gw.saturating_sub(1));
    let y1 = ((cy + radius).ceil().max(0.0) as usize).min(gh.saturating_sub(1));
    if cx + radius < 0.0 || cy + radius < 0.0 || x0 > x1 || y0 > y1 {
        return;
    }
    for gy in y0..=y1 {
        for gx in x0..=x1 {
            let dx = gx as f32 + 0.5 - cx;
            let dy = gy as f32 + 0.5 - cy;
            let distance = (dx * dx + dy * dy).sqrt();
            let d = distance / radius;
            if d >= 1.0 {
                continue;
            }
            let steps = distance.ceil() as usize;
            let mut transmit = 1.0f32;
            for k in 1..steps {
                let t = k as f32 / steps as f32;
                let sx = cx + dx * t;
                let sy = cy + dy * t;
                if sx >= 0.0 && sy >= 0.0 && (sx as usize) < gw && (sy as usize) < gh {
                    transmit *= 1.0 - OCCLUSION * opacity[sy as usize * gw + sx as usize];
                    if transmit < 0.02 {
                        break;
                    }
                }
            }
            let f = 1.0 - d;
            light[gy * gw + gx] += intensity * f * f * transmit;
        }
    }
}

fn splat(light: &mut [f32], gw: usize, gh: usize, cx: f32, cy: f32, radius: f32, intensity: f32) {
    let x0 = (cx - radius).floor().max(0.0) as usize;
    let y0 = (cy - radius).floor().max(0.0) as usize;
    let x1 = ((cx + radius).ceil() as usize).min(gw.saturating_sub(1));
    let y1 = ((cy + radius).ceil() as usize).min(gh.saturating_sub(1));
    if cx + radius < 0.0 || cy + radius < 0.0 || x0 > x1 || y0 > y1 {
        return;
    }
    for gy in y0..=y1 {
        for gx in x0..=x1 {
            let dx = gx as f32 - cx;
            let dy = gy as f32 - cy;
            let d = (dx * dx + dy * dy).sqrt() / radius;
            if d < 1.0 {
                let f = 1.0 - d;
                light[gy * gw + gx] += intensity * f * f;
            }
        }
    }
}

/// Like `cloita_render`, but with lighting: writes
/// `(material * variants + grain) * levels + light_level` per pixel.
///
/// `emissive` holds one glow value (0-255) per material; `lights` holds `n_lights`
/// quadruples `(x, y, radius, intensity)` in world pixels. Light outside sources
/// falls back to `ambient` (0..1).
///
/// # Safety
/// Same buffer requirements as `cloita_render`; `emissive` must hold
/// `n_materials` bytes and `lights` `4 * n_lights` floats.
#[no_mangle]
pub unsafe extern "C" fn cloita_render_lit(
    grid: *const u8,
    noise: *const u8,
    out: *mut u8,
    w: usize,
    x0: usize,
    y0: usize,
    vw: usize,
    vh: usize,
    variants: u8,
    levels: u8,
    emissive: *const u8,
    opaque: *const u8,
    n_materials: usize,
    lights: *const f32,
    n_lights: usize,
    ambient: f32,
) {
    let out = slice::from_raw_parts_mut(out, vw * vh);
    let emissive = slice::from_raw_parts(emissive, n_materials);
    let opaque = slice::from_raw_parts(opaque, n_materials);
    let lights = slice::from_raw_parts(lights, n_lights * 4);
    let levels = levels.max(1);
    let gw = vw / LIGHT_CELL + 2;
    let gh = vh / LIGHT_CELL + 2;
    let mut light = vec![ambient; gw * gh];
    let mut opacity = vec![0.0f32; gw * gh];
    let mut glows: Vec<(usize, usize, f32)> = Vec::new();
    let per_cell = (LIGHT_CELL * LIGHT_CELL) as f32;

    for gy in 0..vh / LIGHT_CELL {
        for gx in 0..vw / LIGHT_CELL {
            let mut glow = 0u32;
            let mut solid = 0u32;
            for dy in 0..LIGHT_CELL {
                let row = (y0 + gy * LIGHT_CELL + dy) * w + x0 + gx * LIGHT_CELL;
                let cells = slice::from_raw_parts(grid.add(row), LIGHT_CELL);
                for &m in cells {
                    if (m as usize) < n_materials {
                        glow += u32::from(emissive[m as usize]);
                        solid += u32::from(opaque[m as usize]);
                    }
                }
            }
            opacity[gy * gw + gx] = solid as f32 / per_cell;
            if glow > 0 {
                glows.push((gx, gy, glow as f32 / (255.0 * per_cell) * 3.0));
            }
        }
    }
    for &(gx, gy, intensity) in &glows {
        splat(&mut light, gw, gh, gx as f32 + 0.5, gy as f32 + 0.5, EMISSIVE_RADIUS, intensity);
    }
    let cell = LIGHT_CELL as f32;
    for l in lights.chunks_exact(4) {
        let cx = (l[0] - x0 as f32) / cell;
        let cy = (l[1] - y0 as f32) / cell;
        splat_occluded(&mut light, &opacity, gw, gh, cx, cy, l[2] / cell, l[3]);
    }

    let top = f32::from(levels - 1);
    for r in 0..vh {
        let src = (y0 + r) * w + x0;
        let cells = slice::from_raw_parts(grid.add(src), vw);
        let grain = slice::from_raw_parts(noise.add(src), vw);
        let fy = r as f32 / cell;
        let gy = (fy as usize).min(gh - 2);
        let ty = fy - gy as f32;
        for c in 0..vw {
            let m = cells[c];
            let fx = c as f32 / cell;
            let gx = (fx as usize).min(gw - 2);
            let tx = fx - gx as f32;
            let i = gy * gw + gx;
            let top_row = light[i] * (1.0 - tx) + light[i + 1] * tx;
            let bottom_row = light[i + gw] * (1.0 - tx) + light[i + gw + 1] * tx;
            let value = (top_row * (1.0 - ty) + bottom_row * ty).min(1.0);
            let level = if (m as usize) < n_materials && emissive[m as usize] > 0 {
                levels - 1
            } else {
                let dither = BAYER[(r & 3) * 4 + (c & 3)] / 16.0 - 0.5;
                (value * top + dither * 0.9 + 0.5).floor().clamp(0.0, top) as u8
            };
            let base = m.wrapping_mul(variants).wrapping_add(grain[c]);
            out[r * vw + c] = base.wrapping_mul(levels).wrapping_add(level);
        }
    }
}
