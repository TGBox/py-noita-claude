"""Contract V16: Multi-phase boss scripts and arena hazards (Cards F03..F06)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src import materials as mat

if TYPE_CHECKING:
    from ..enemies import Creature
    from ..run import Run

PHASE_INVULNERABLE = 1.0  # seconds of invulnerability at every phase change


@dataclass(frozen=True)
class BossPhase:
    index: int
    hp_threshold: float
    name_de: str
    line_de: str
    attack_interval_scale: float = 1.0
    speed_scale: float = 1.0
    summon_species: str = ""
    summon_count: int = 0
    arena_hazard: str = ""


class BossScript:
    boss_key: str = ""
    title_de: str = ""
    phases: tuple[BossPhase, ...] = ()

    def __init__(self, boss: Creature) -> None:
        self.boss: Creature = boss
        self.phase: int = 0
        self.phase_timer: float = 0.0
        self.invuln_timer: float = 0.0
        self.hazard_timer: float = 0.0
        self._guard_hp: float = boss.hp  # health the boss keeps while invulnerable
        self._last_cooldown: float = boss.ranged_cooldown
        self._started = False

    def update(self, dt: float, run: Run) -> None:
        """Check phase HP thresholds, tick invuln_timer, and execute tick_phase."""
        boss = self.boss
        if not self.phases:
            return
        if not self._started:  # the first phase has no change: its helpers come now
            self._started = True
            self._summon(self.phases[0], run)
        if self.invuln_timer > 0:
            boss.hp = max(boss.hp, self._guard_hp)  # incoming damage is blocked
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
        ratio = boss.hp / max(1.0, boss.max_hp)
        reached = max(p.index for p in self.phases if ratio <= p.hp_threshold)
        if reached > self.phase:
            self.phase_change(reached, run)
        self.phase_timer += dt
        self.tick_phase(dt, run)

    def phase_change(self, new_phase: int, run: Run) -> None:
        """Transition into new_phase with 1.0s invulnerability, summons, and boss_line."""
        phase = self.phases[new_phase]
        self.phase = new_phase
        self.phase_timer = 0.0
        self.invuln_timer = PHASE_INVULNERABLE
        self._guard_hp = max(1.0, self.boss.hp)
        self.boss.hp = self._guard_hp
        run.boss_line(f"{self.title_de}: {phase.line_de}")
        run.emit(
            "boss_phase", species=self.boss_key, phase=new_phase, name=phase.name_de,
            hazard=phase.arena_hazard,
        )  # fmt: skip
        self._summon(phase, run)

    def _summon(self, phase: BossPhase, run: Run) -> None:
        cx, cy = self.boss.center
        for i in range(phase.summon_count):
            side = -1 if i % 2 else 1
            run.enemies.spawn(phase.summon_species, cx + side * (18 + 10 * (i // 2)), cy - 6)

    def tick_phase(self, dt: float, run: Run) -> None:
        """Execute phase-specific attacks and arena hazards."""
        phase = self.phases[self.phase]
        boss = self.boss
        if boss.ranged_cooldown > self._last_cooldown:  # it just attacked: pace the next one
            boss.ranged_cooldown *= phase.attack_interval_scale
        self._last_cooldown = boss.ranged_cooldown
        boss.speed_scale = phase.speed_scale
        if phase.arena_hazard:
            apply_arena_hazard(phase.arena_hazard, dt, boss, run)

    def on_death(self, run: Run) -> None:
        """Handle boss defeat rewards and portal unlock."""
        run.exit_open = True
        run.boss_line(f"{self.title_de} ist besiegt.")
        run.emit("boss_defeated", species=self.boss_key, phases=self.phase + 1)


ARENA_HAZARDS: tuple[str, ...] = (
    "acid_rain",
    "magma_veins",
    "sealing_wax",
    "closing_walls",
    "rising_water",
    "electric_water",
    "bass_drop",
    "spore_cloud",
)
# seconds between two pulses of a hazard
HAZARD_INTERVAL: dict[str, float] = {
    "acid_rain": 0.12, "magma_veins": 0.9, "sealing_wax": 1.6, "closing_walls": 0.6,
    "rising_water": 1.0, "electric_water": 2.5, "bass_drop": 4.0, "spore_cloud": 0.25,
}  # fmt: skip
WALL_GAP = 70  # closing walls leave this much room in the middle (cells)
WATER_SHARE = 0.6  # rising water stops at this share of the arena height


def _arena(boss: Creature, run: Run) -> tuple[int, int, int, int]:
    """The boss arena of the level, or a box around the boss if the level has none."""
    arena = getattr(run.level, "boss_arena", None)
    if not arena or arena == (0, 0, 0, 0):
        cx, cy = (int(v) for v in boss.center)
        arena = (cx - 110, cy - 70, cx + 110, cy + 40)
    w, h = run.world.width, run.world.height
    x0, y0, x1, y1 = arena
    return (max(4, x0), max(4, y0), min(w - 4, x1), min(h - 4, y1))


def apply_arena_hazard(hazard: str, dt: float, boss: Creature, run: Run) -> None:
    """Apply periodic arena hazard effect during a boss fight."""
    if hazard not in ARENA_HAZARDS:
        return
    timers: dict[str, float] = boss.__dict__.setdefault("_hazard_timers", {})
    timers[hazard] = timers.get(hazard, 0.0) + dt
    if timers[hazard] < HAZARD_INTERVAL[hazard]:
        return
    timers[hazard] = 0.0
    world, rng, player = run.world, run.rng, run.player
    x0, y0, x1, y1 = _arena(boss, run)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return
    state: dict[str, int] = boss.__dict__.setdefault("_hazard_state", {})

    def material(key: str) -> int | None:
        return mat.MAT_ID.get(key)

    if hazard == "acid_rain":
        acid = material("acid")
        x = rng.randint(x0, x1 - 1)
        if acid is not None and world.get(x, y0 + 1) == mat.AIR:
            world.set_cell(x, y0 + 1, acid)
    elif hazard == "magma_veins":
        magma = material("magma")
        x, y = rng.randint(x0, x1 - 1), rng.randint(y0, y1 - 1)
        while y < y1 and world.get(x, y) == mat.AIR:
            y += 1  # down to the floor: the vein opens there
        if magma is not None and world.get(x, y - 1) == mat.AIR:
            world.splash(x, y - 1, 3, magma)
    elif hazard == "sealing_wax":
        wax = material("siegellack")
        px, py = (int(v) for v in player.center)
        if wax is not None:
            world.splash(px + rng.randint(-30, 30), max(y0 + 2, py - 40), 3, wax)
    elif hazard == "closing_walls":
        board = material("aktendeckel")
        step = state.get("walls", 0)
        if board is not None and 2 * step < (x1 - x0) - WALL_GAP:
            for x in (x0 + step, x1 - 1 - step):
                for y in range(y0, y1):
                    if world.get(x, y) == mat.AIR and not player.contains(x, y):
                        world.set_cell(x, y, board)
            state["walls"] = step + 1
    elif hazard == "rising_water":
        rows = state.get("water", 0)
        if rows < int((y1 - y0) * WATER_SHARE):
            y = y1 - 1 - rows
            for x in range(x0, x1):
                if world.get(x, y) == mat.AIR:
                    world.set_cell(x, y, mat.WATER)
            state["water"] = rows + 1
    elif hazard == "electric_water":
        if player.in_liquid(world) and not player.dead:
            player.hurt(8.0, "Stromschlag im Wasser")
            run.events.append("shock")
    elif hazard == "bass_drop":
        for body in (player, *run.enemies.creatures):
            if body.on_ground and not body.dead and body is not boss:
                body.vy = -230.0
        run.events.append("bass_drop")
    elif hazard == "spore_cloud":
        spores = material("leuchtsporen") or material("spores")
        cx, cy = (int(v) for v in boss.center)
        x, y = cx + rng.randint(-24, 24), cy + rng.randint(-20, 12)
        if spores is not None and world.get(x, y) == mat.AIR:
            world.set_cell(x, y, spores)
        if math.dist(player.center, boss.center) < 48:
            player.drunk = max(player.drunk, 3.0)


def _phases(*rows: tuple[str, str, dict[str, object]]) -> tuple[BossPhase, ...]:
    """Three phases at 100 %, 66 % and 33 % health (Bibel 05)."""
    thresholds = (1.0, 0.66, 0.33)
    return tuple(
        BossPhase(i, thresholds[i], name, line, **fields)  # type: ignore[arg-type]
        for i, (name, line, fields) in enumerate(rows)
    )


class Weltenherz(BossScript):
    boss_key, title_de = "weltenherz", "Das Weltenherz"
    phases = _phases(
        ("Herzschlag", "Bumm. Bumm. Hörst du mich?", {}),
        ("Glutblut-Adern", "Meine Adern brechen auf!",
         {"arena_hazard": "magma_veins", "attack_interval_scale": 0.8}),
        ("Losgerissen", "Jetzt komme ich zu dir.",
         {"summon_species": "fleischmade", "summon_count": 3, "speed_scale": 1.6,
          "attack_interval_scale": 0.6}),
    )  # fmt: skip


class DjMyzel(BossScript):
    boss_key, title_de = "dj_myzel", "DJ Myzel"
    phases = _phases(
        ("Schallringe", "Die Party hört niemals auf!", {}),
        ("Bass-Drop", "Und jetzt alle: hoch die Hüte!",
         {"arena_hazard": "bass_drop", "summon_species": "leuchtmotte", "summon_count": 4}),
        ("Zerstörtes Pult", "Mein Pult! Dann eben ohne Platten.",
         {"arena_hazard": "spore_cloud", "attack_interval_scale": 0.6, "speed_scale": 1.4}),
    )  # fmt: skip


class Oberstempler(BossScript):
    boss_key, title_de = "oberstempler", "Der Oberstempler"
    phases = _phases(
        ("Stempelschläge", "Ihr Antrag ist unvollständig.", {"arena_hazard": "sealing_wax"}),
        ("Formularflut", "Dienstaufsicht! Zwei Mann zu mir!",
         {"summon_species": "agent_streife", "summon_count": 2, "attack_interval_scale": 0.75}),
        ("Aktenschluss", "Die Akte wird geschlossen. Mit Ihnen darin.",
         {"arena_hazard": "closing_walls", "attack_interval_scale": 0.6}),
    )  # fmt: skip


class AbtKieme(BossScript):
    boss_key, title_de = "abt_kieme", "Abt Kieme"
    phases = _phases(
        ("Orgelstöße", "Schweigt. Der Chor singt.",
         {"summon_species": "moenchsfisch", "summon_count": 3}),
        ("Steigende Flut", "Das Wasser kennt den Weg nach oben.",
         {"arena_hazard": "rising_water", "attack_interval_scale": 0.8}),
        ("Glockensturm", "Hört die Glocke. Fühlt die Glocke.",
         {"arena_hazard": "electric_water", "attack_interval_scale": 0.6}),
    )  # fmt: skip


class Ameisenkoenigin(BossScript):
    boss_key, title_de = "ameisenkoenigin", "Die Ameisenkönigin"
    phases = _phases(
        ("Eiablage", "Meine Kinder haben Hunger.",
         {"summon_species": "ameisenkrieger", "summon_count": 2}),
        ("Umgraben", "Der Boden gehört mir.",
         {"summon_species": "ameisenkrieger", "summon_count": 3, "speed_scale": 1.3}),
        ("Hochzeitsflug", "Es regnet. Für dich.",
         {"arena_hazard": "acid_rain", "attack_interval_scale": 0.6, "speed_scale": 1.5}),
    )  # fmt: skip


class MutterGlibber(BossScript):
    boss_key, title_de = "mutter_glibber", "Mutter Glibber"
    phases = _phases(
        ("Druckwelle", "Komm her, lass dich drücken!", {}),
        ("Teilung", "Kinder! Mama braucht euch!",
         {"summon_species": "glibberteiler", "summon_count": 4, "attack_interval_scale": 0.8}),
        ("Walze", "Alle wieder rein. Wir rollen.",
         {"speed_scale": 1.8, "attack_interval_scale": 0.6}),
    )  # fmt: skip

    def phase_change(self, new_phase: int, run: Run) -> None:
        super().phase_change(new_phase, run)
        if new_phase == 2:  # she pulls her children back in: each one heals her a little
            for child in run.enemies.creatures:
                if child.species == "glibberteiler" and not child.dead:
                    child.hp = 0.0
                    self.boss.hp = min(self.boss.max_hp, self.boss.hp + 20.0)
            self._guard_hp = self.boss.hp


EVIL_THRESHOLDS = (1.0, 0.75, 0.50, 0.25)  # final fight in her home world
ECHO_THRESHOLDS = (1.0, 0.50)  # echoes and the evil selves in the headquarters
EVIL_PHASES: dict[str, tuple[tuple[str, str, dict[str, object]], ...]] = {
    "boese_kaiserin": (
        ("Audienz", "Knie nieder. Du bist ich, nur ärmer.", {}),
        ("Das Angebot", "Die Hälfte des Multiversums. Sag einfach ja.",
         {"summon_species": "agent_streife", "summon_count": 2}),
        ("Hofstaat", "Wachen! Entfernt diese Kopie.",
         {"summon_species": "agent_streife", "summon_count": 3, "attack_interval_scale": 0.75}),
        ("Thronkanone", "Dann eben mit dem Thron.", {"attack_interval_scale": 0.5}),
    ),
    "boese_gute": (
        ("Segen", "Ich will dir nur helfen. Halt still.", {}),
        ("Lichtstrahlen", "Sieh ins Licht.", {"attack_interval_scale": 0.8}),
        ("Bekehrung", "Klonita, komm zu mir. Hier ist es friedlich.", {"speed_scale": 1.3}),
        ("Gnadenlos gut", "Es ist zu deinem Besten.", {"attack_interval_scale": 0.5}),
    ),
    "boese_omega": (
        ("Kalibrierung", "Ziel erfasst. Ich bin die fertige Version.", {}),
        ("Pressen", "Fertigungsstraße aktiv.", {"attack_interval_scale": 0.8}),
        ("Riesenmaschine", "Bauteile: zu mir.",
         {"summon_species": "agent_drohne", "summon_count": 3, "speed_scale": 1.3}),
        ("Überlast", "Sicherungen: entfernt.", {"attack_interval_scale": 0.5, "speed_scale": 1.5}),
    ),
}  # fmt: skip


class EvilSelfBossScript(BossScript):
    """An evil self: four phases in the final fight, two as an echo or in the headquarters."""

    def __init__(self, boss: Creature, echo: bool = False) -> None:
        super().__init__(boss)
        from src.bosses.evil_selves import EVIL_SELVES

        self.boss_key = boss.species if boss.species in EVIL_SELVES else boss.spec.key
        self.title_de = boss.spec.name_de
        self.echo = echo
        rows = EVIL_PHASES[self.boss_key]
        if echo:
            rows = (rows[0], rows[1])  # the opening and the second act only
        thresholds = ECHO_THRESHOLDS if echo else EVIL_THRESHOLDS
        self.phases = tuple(
            BossPhase(i, thresholds[i], name, line, **fields)  # type: ignore[arg-type]
            for i, (name, line, fields) in enumerate(rows)
        )

    def phase_change(self, new_phase: int, run: Run) -> None:
        super().phase_change(new_phase, run)
        at_home = not getattr(self.boss, "in_headquarters", False)
        if self.boss_key == "boese_kaiserin" and new_phase == 1 and at_home:
            run.menu_mode = "empress_bargain"  # "die Hälfte des Multiversums" (V17)
            run.menu_index = 0

    def on_death(self, run: Run) -> None:
        from src.bosses.evil_selves import ECHO_GOLD, signature_wand_spec
        from src.loot import Pickup

        cx, cy = self.boss.center
        run.records.discover("evil_self", self.boss_key)
        run.boss_line(f"{self.title_de} ist besiegt.")
        run.emit("boss_defeated", species=self.boss_key, phases=self.phase + 1, echo=self.echo)
        if getattr(self.boss, "in_headquarters", False):
            return  # the headquarters controller decides what comes next
        if self.echo:
            run.pickups.append(Pickup(cx - 6, cy, kind="gold", amount=ECHO_GOLD))
            run.pickups.append(Pickup(cx + 6, cy, kind="badge", amount=1))
        else:  # the final fight: her own weapon
            run.pickups.append(Pickup(cx, cy, wand=signature_wand_spec(self.boss_key)))
            run.exit_open = True


class OberCloitaBossScript(BossScript):
    """The Ober-Cloita: one phase per evil self, the last one all of them mixed."""

    boss_key, title_de = "ober_cloita", "Die Ober-Cloita"
    phases = _phases(
        ("Kaiserliche Strenge", "Ich bin jede von euch. Zuerst die Strenge.",
         {"summon_species": "agent_streife", "summon_count": 2}),
        ("Gütige Härte", "Dann die Güte. Sie tut mehr weh.", {"attack_interval_scale": 0.75}),
        ("Alle zugleich", "Genug. Alle meine Ichs: jetzt.",
         {"attack_interval_scale": 0.5, "speed_scale": 1.4}),
    )  # fmt: skip
    SHARD_STEP = 0.10  # a head splinter falls for every tenth of her health
    SHARD_FLUX = 50.0
    HUG_TIME = 3.0  # Klonita's hug at the start of the last phase

    def __init__(self, boss: Creature) -> None:
        super().__init__(boss)
        self.shards = 0
        self.hug_timer = 0.0

    def update(self, dt: float, run: Run) -> None:
        super().update(dt, run)
        boss = self.boss
        lost = 1.0 - boss.hp / max(1.0, boss.max_hp)
        while self.shards < int(lost / self.SHARD_STEP + 1e-6) and self.shards < 9:
            self.shards += 1  # Klonita catches the splinter and hands Cloita its flux
            for wand in run.inventory.wands:
                wand.mana = min(wand.spec.mana_max, wand.mana + self.SHARD_FLUX)
            run.emit("head_shard", count=self.shards, flux=self.SHARD_FLUX)
            run.messages.append("Klonita fängt einen Kopf-Splitter: +50 Flux.")
        if self.hug_timer > 0:  # held tight: she can neither move nor attack
            self.hug_timer = max(0.0, self.hug_timer - dt)
            boss.vx = boss.vy = 0.0
            boss.ranged_cooldown = max(boss.ranged_cooldown, 0.5)
            boss.attack_cooldown = max(boss.attack_cooldown, 0.5)

    def phase_change(self, new_phase: int, run: Run) -> None:
        super().phase_change(new_phase, run)
        if new_phase == 2:
            self.hug_timer = self.HUG_TIME
            cx, cy = self.boss.center
            run.say("Klonita", "Ich halte sie! Jetzt!", cx, cy - self.boss.height)

    def on_death(self, run: Run) -> None:
        run.boss_line("Die Ober-Cloita fällt. Die Splitter erinnern sich.")
        run.emit("boss_defeated", species=self.boss_key, phases=self.phase + 1)
        run.true_ending = True


SCRIPTS: dict[str, type[BossScript]] = {
    cls.boss_key: cls
    for cls in (Weltenherz, DjMyzel, Oberstempler, AbtKieme, Ameisenkoenigin, MutterGlibber)
}


def make_boss_script(boss: Creature) -> BossScript | None:
    """Return the matching BossScript instance for boss.species, or None."""
    from src.bosses.evil_selves import EVIL_SELVES

    key = getattr(boss, "species", "") or boss.spec.key
    if key in EVIL_SELVES:
        return EvilSelfBossScript(boss, echo=bool(getattr(boss, "echo", False)))
    if key == "ober_cloita":
        return OberCloitaBossScript(boss)
    cls = SCRIPTS.get(key)
    return cls(boss) if cls is not None else None
