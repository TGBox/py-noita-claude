"""Contract V14: Deterministic headless playtest bot (Cards D15, D16)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BotReport:
    universe_key: str
    seed: int
    ticks: int = 0
    reached_exit: bool = False
    died: bool = False
    kills: int = 0
    gold_collected: int = 0
    samples_collected: int = 0
    stuck_ratio: float = 0.0
    min_hp_ratio: float = 1.0
    errors: list[str] = field(default_factory=list)


TICK = 1.0 / 60.0
VIEW = (420, 260)  # half size of the simulated area around the bot (cells)


def _play(run: Any, report: BotReport, max_seconds: float) -> None:
    """Steer the player of ``run`` towards the exit until it gets there, dies or time is up.

    The bot walks and levitates towards the exit, shoots at the nearest creature it can
    see, digs with its shots when it has not moved for a while and presses [E] for loot
    and for the way on. Everything it does is derived from the run state (deterministic).
    """
    from src.run import Controls

    player, start_gold, start_kills = run.player, run.gold, run.stats["kills"]
    seen_events = len(run.emitted_events)
    stuck = still = 0
    last = player.center
    for tick in range(max(1, int(max_seconds / TICK))):
        px, py = player.center
        ex, ey = run.level.exit
        target = (float(ex), float(ey))
        aim, cast = target, False
        for creature in run.enemies.creatures:  # the nearest hostile in sight
            if creature.dead or creature.spec.prop or creature.stance == "passive":
                continue
            if math.dist(creature.center, (px, py)) < 220 and player.can_see(
                run.world, *creature.center, 220
            ):
                aim, cast = creature.center, True
                break
        if tick % 60 == 0:  # once a second: did we get anywhere?
            still = still + 1 if math.dist((px, py), last) < 6 else 0
            last = (px, py)
        if still >= 2:
            stuck += 1
            cast = True  # blast or bore a way towards the exit
            aim = target if tick % 120 < 60 else (px + (40 if tick % 240 < 120 else -40), py - 30)
        near = run.near_exit()
        controls = Controls(
            move=0 if abs(ex - px) < 3 else (1 if ex > px else -1),
            jump=player.on_ground and tick % 20 == 0,
            levitate=ey < py - 4 or (still >= 1 and tick % 90 < 45),
            cast=cast and not near,
            aim=aim,
            pickup=tick % 15 == 0,
        )
        area = (int(px) - VIEW[0], int(py) - VIEW[1], int(px) + VIEW[0], int(py) + VIEW[1])
        was_here = (run.universe_key, run.in_workshop, run.in_sanctum, run.depth_index)
        run.update(TICK, controls, area)
        report.ticks += 1
        report.min_hp_ratio = min(report.min_hp_ratio, max(0.0, player.hp) / player.max_hp)
        if player.dead or run.outcome == "dead":
            report.died = True
            break
        if (run.universe_key, run.in_workshop, run.in_sanctum, run.depth_index) != was_here:
            report.reached_exit = True  # [E] at the exit took us on
            break
    report.kills = run.stats["kills"] - start_kills
    report.gold_collected = max(0, run.gold - start_gold)
    fresh = run.emitted_events[seen_events:]
    report.samples_collected = sum(int(d.get("count", 1)) for name, d in fresh if name == "sample")
    report.stuck_ratio = stuck / max(1, report.ticks)


def run_bot(
    universe_key: str,
    seed: int = 1,
    max_seconds: float = 120.0,
) -> BotReport:
    """Run deterministic bot in a single universe and return BotReport."""
    from src.run import Run

    report = BotReport(universe_key, seed)
    try:
        _play(Run(seed=seed, universe_key=universe_key), report, max_seconds)
    except Exception as error:  # noqa: BLE001 - the report is the bot's whole purpose
        report.errors.append(f"{type(error).__name__}: {error}")
    return report


def run_full(
    seed: int = 1,
    max_seconds_per_stage: float = 120.0,
) -> list[BotReport]:
    """Run deterministic bot across the six universes of a RunPlan and return reports."""
    from src.run import Run

    reports: list[BotReport] = []
    try:
        run = Run(seed=seed)
        run.start_multiverse_run()
    except Exception as error:  # noqa: BLE001
        return [BotReport("werkstatt", seed, errors=[f"{type(error).__name__}: {error}"])]
    while run.plan is not None and not run.plan.finished:
        report = BotReport(run.plan.offers()[0].universe, seed)
        reports.append(report)
        try:
            run.choose_next_universe(0)
            _play(run, report, max_seconds_per_stage)
            if report.died:
                break
            if not run.in_workshop:  # out of time: the bot is carried back to the workshop
                run.enter_workshop()
        except Exception as error:  # noqa: BLE001
            report.errors.append(f"{type(error).__name__}: {error}")
            break
    if run.plan is not None and run.plan.finished and not (reports and reports[-1].died):
        report = BotReport(f"heimatwelt:{run.plan.evil_self}", seed)  # the final fight (F19)
        reports.append(report)
        try:
            run.choose_next_universe(0)
            _play(run, report, max_seconds_per_stage)
        except Exception as error:  # noqa: BLE001
            report.errors.append(f"{type(error).__name__}: {error}")
    return reports
