"""Cynical workshop statistics wall tracker for ws_statistik_wand (Phase T04)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorkshopStats:
    """Tracks run missteps, fines, explosions, and parasites for ws_statistik_wand."""

    total_deaths: int = 0
    clones_wasted: int = 0
    bureaucracy_fines_paid: int = 0
    explosions_caused: int = 0
    coffee_cups_drunk: int = 0
    tv_watch_seconds: float = 0.0
    parasites_exposed: int = 0

    def record_death(self, clone_wasted: bool = True) -> None:
        self.total_deaths += 1
        if clone_wasted:
            self.clones_wasted += 1

    def record_fine(self, gold_amount: int) -> None:
        self.bureaucracy_fines_paid += max(0, int(gold_amount))

    def record_explosion(self, count: int = 1) -> None:
        self.explosions_caused += max(0, int(count))

    def record_coffee(self, cups: int = 1) -> None:
        self.coffee_cups_drunk += max(0, int(cups))

    def record_tv_watch(self, seconds: float) -> None:
        self.tv_watch_seconds += max(0.0, float(seconds))

    def record_parasite(self, count: int = 1) -> None:
        self.parasites_exposed += max(0, int(count))

    def summary_lines_de(self) -> list[str]:
        return [
            f"Verbrauchte Klone (offiziell 'Umlagerungen'): {self.clones_wasted}",
            f"Dokumentierte Tode: {self.total_deaths}",
            f"Gezahlte Strafgebühren ans Patentamt: {self.bureaucracy_fines_paid} Gold",
            f"Großflächige Labor-Missgeschicke: {self.explosions_caused}",
            f"Notfall-Kaffees konsumiert: {self.coffee_cups_drunk}",
            f"Fernsehzeit statt Forschung: {self.tv_watch_seconds:.0f}s",
            f"Enttarnte Erinnerungs-Parasiten: {self.parasites_exposed}",
        ]

    def to_data(self) -> dict[str, int | float]:
        return {
            "total_deaths": self.total_deaths,
            "clones_wasted": self.clones_wasted,
            "bureaucracy_fines_paid": self.bureaucracy_fines_paid,
            "explosions_caused": self.explosions_caused,
            "coffee_cups_drunk": self.coffee_cups_drunk,
            "tv_watch_seconds": self.tv_watch_seconds,
            "parasites_exposed": self.parasites_exposed,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> WorkshopStats:
        if not data:
            return cls()
        return cls(
            total_deaths=int(data.get("total_deaths", 0)),
            clones_wasted=int(data.get("clones_wasted", 0)),
            bureaucracy_fines_paid=int(data.get("bureaucracy_fines_paid", 0)),
            explosions_caused=int(data.get("explosions_caused", 0)),
            coffee_cups_drunk=int(data.get("coffee_cups_drunk", 0)),
            tv_watch_seconds=float(data.get("tv_watch_seconds", 0.0)),
            parasites_exposed=int(data.get("parasites_exposed", 0)),
        )
