"""Contract V17: the authority headquarters and the Ober-Cloita (Cards F09, F10)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src import materials as mat
from src.bosses.evil_selves import EVIL_HP, EVIL_SELVES, final_evil_self

if TYPE_CHECKING:
    from ..run import Run
    from ..world import World

HQ_STAGES: tuple[str, ...] = (
    "anhoerung",
    "boese_ichs",
    "ober_cloita",
)
COUNCIL_SIZE = 5
OBER_CLOITA_HP = 6000
HALL_SIZE = (960, 360)  # the endless file hall
DESK_SIZE = (120, 32)  # the council's desk at its right end
WAVE_INTERVAL = 10.0  # seconds between agent waves while a councillor lives
HQ_SELF_HP_FACTOR = 0.5

UNMASKED_DE: tuple[str, ...] = (
    "Ich war die Cloita, die nie einen Fehler zugab.",
    "Ich war die Cloita, die jede Regel selbst geschrieben hat.",
    "Ich war die Cloita, die Klonita nie zugehört hat.",
    "Ich war die Cloita, die lieber stempelte als forschte.",
    "Ich war die Cloita, die Angst vor dir hatte.",
)


def can_enter_headquarters(run: Run) -> bool:
    """6 memory shards, 3 badges or 4 wanted stars (bible 02)."""
    return run.memory_shards >= 6 or run.badges >= 3 or run.wanted.stars >= 4


def _hall(world: World) -> tuple[int, int, int, int]:
    """The hall's interior, centred in the world."""
    wide, high = min(HALL_SIZE[0], world.width - 16), min(HALL_SIZE[1], world.height - 16)
    x0, y0 = (world.width - wide) // 2, (world.height - high) // 2
    return (x0, y0, x0 + wide, y0 + high)


def generate_headquarters_arena(world: World) -> tuple[int, int]:
    """Build the 960x360 file hall in world and return the player spawn."""
    wall = mat.MAT_ID.get("aktendeckel", mat.MAT_ID.get("bone", mat.BEDROCK))
    world.reset(wall)
    x0, y0, x1, y1 = _hall(world)
    world.fill_rect(x0, y0, x1, y1, mat.AIR)
    desk_w, desk_h = DESK_SIZE
    world.fill_rect(x1 - desk_w - 20, y1 - desk_h, x1 - 20, y1, wall)  # the council's desk
    for x in range(x0 + 160, x1 - desk_w - 80, 150):  # file shelves to jump on
        world.fill_rect(x, y1 - 70, x + 46, y1 - 66, wall)
        world.fill_rect(x + 60, y1 - 140, x + 106, y1 - 136, wall)
    world.wake_all()
    return (x0 + 40, y1 - 20)


class HeadquartersController:
    def __init__(self) -> None:
        self.stage_index: int = 0
        self.completed: bool = False
        self.wave_timer: float = WAVE_INTERVAL
        self._spawned: bool = False
        self._queue: list[str] = []  # stage 2: the evil selves still to come
        self._alive: list = []  # the creatures that must fall to clear the stage

    @property
    def stage(self) -> str:
        return HQ_STAGES[min(self.stage_index, len(HQ_STAGES) - 1)]

    def spawn_stage(self, run: Run) -> None:
        """Spawn the enemies of HQ_STAGES[self.stage_index]."""
        from src.bosses import make_boss_script

        self._spawned = True
        x0, _y0, x1, y1 = _hall(run.world)
        desk_top = y1 - DESK_SIZE[1]
        stage = self.stage
        if stage == "anhoerung":
            self._alive = [
                run.enemies.spawn("ratsmitglied", x1 - 130 + i * 22, desk_top - 26)
                for i in range(COUNCIL_SIZE)
            ]
            self.wave_timer = WAVE_INTERVAL
            return
        if stage == "boese_ichs" and not self._queue:
            self._queue = [key for key in EVIL_SELVES if key != final_evil_self(run)]
        species = self._queue.pop(0) if stage == "boese_ichs" else "ober_cloita"
        boss = run.enemies.spawn(species, x1 - 260, y1 - 90)
        if stage == "boese_ichs":
            boss.echo = True  # two phases, like an echo (V16)
            boss.max_hp = boss.hp = EVIL_HP[species] * HQ_SELF_HP_FACTOR
        else:
            boss.max_hp = boss.hp = float(OBER_CLOITA_HP)
        boss.in_headquarters = True
        self._alive = [boss]
        script = make_boss_script(boss)
        if script is not None:
            run.extra_scripts.append(script)

    def update(self, dt: float, run: Run) -> None:
        """Advance to the next stage once the current one is cleared."""
        if self.completed:
            return
        if not self._spawned:
            self.spawn_stage(run)
            return
        before = len(self._alive)
        self._alive = [c for c in self._alive if not c.dead and c in run.enemies.creatures]
        if self.stage == "anhoerung":
            for _ in range(before - len(self._alive)):  # a councillor fell: the mask comes off
                px, py = run.player.center
                fallen = COUNCIL_SIZE - len(self._alive) - 1
                run.say("Ratsmitglied", UNMASKED_DE[fallen % len(UNMASKED_DE)], px, py - 30)
            if self._alive:
                self.wave_timer -= dt
                if self.wave_timer <= 0:  # agents and a rain of forms while the council sits
                    self.wave_timer = WAVE_INTERVAL
                    x0, y0, _x1, y1 = _hall(run.world)
                    for i in range(2):
                        run.enemies.spawn("agent_streife", x0 + 60 + 40 * i, y1 - 30)
                    paper = mat.MAT_ID.get("papier")
                    if paper is not None:
                        for _ in range(40):
                            x = run.rng.randint(x0 + 4, _x1 - 4)
                            if run.world.get(x, y0 + 2) == mat.AIR:
                                run.world.set_cell(x, y0 + 2, paper)
        if self._alive:
            return
        if self.stage == "boese_ichs" and self._queue:
            self.spawn_stage(run)  # the second evil self
            return
        if self.stage_index >= len(HQ_STAGES) - 1:
            self.completed = True
            run.victory = True
            run.true_ending = True
            run.ending = "wahr"
            run.outcome = "victory"
            run.records.discover("ending", "wahr")
            return
        self.stage_index += 1
        self.spawn_stage(run)
