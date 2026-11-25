"""Memory-parasite ambush event: Falsche Freunde im Labor (Phase T01-T02)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

SUSPECT_DEFINITIONS: dict[str, dict[str, str]] = {
    "theobald": {
        "name_de": "Onkel Theobald",
        "relation_de": "Verwandter mit Kessel-Fimmel",
        "grumpy_flashback_de": (
            "Erinnerung: Theobald hat 2019 deinen besten Kolben zerdeppert und dir die Schuld gegeben."
        ),
        "sweet_flashback_de": (
            "Erinnerung: Theobald hat dir immer perfekte Geschenke gemacht und nie geschimpft — verdächtig makellos!"
        ),
    },
    "locher": {
        "name_de": "Onkel Locher",
        "relation_de": "Ehemaliger Büro-Mentor",
        "grumpy_flashback_de": (
            "Erinnerung: Locher hat dich zwei Stunden lang Formulare nach Grauwert sortieren lassen."
        ),
        "sweet_flashback_de": (
            "Erinnerung: Locher lächelt mild und flüstert, deine Handschrift sei pure Poesie. Viel zu nett!"
        ),
    },
    "bleistift_peter": {
        "name_de": "Bleistift-Peter",
        "relation_de": "Labor-Kumpel aus dem Keller",
        "grumpy_flashback_de": (
            "Erinnerung: Peter hat heimlich deinen Notizblock gekürzt und klebrige Brösel im Regal gelassen."
        ),
        "sweet_flashback_de": (
            "Erinnerung: Peter hat dir stets jeden Fehler verziehen und deinen Stuhl vorgewärmt. Reinster Kitsch!"
        ),
    },
    "kater_klaus": {
        "name_de": "Kater-Klaus",
        "relation_de": "Chronisch beleidigter Laborkater",
        "grumpy_flashback_de": (
            "Erinnerung: Klaus hat deine Stiefel angeknabbert und die Proben vom Tisch gefegt."
        ),
        "sweet_flashback_de": (
            "Erinnerung: Klaus schnurrt wie ein Engel und bringt dir jeden Morgen frisch gebügelte Socken. Fälschung!"
        ),
    },
}

SUSPECT_KEYS: tuple[str, ...] = tuple(SUSPECT_DEFINITIONS.keys())


@dataclass(frozen=True)
class ParasiteSuspect:
    """One suspect present during event_falsche_freunde."""

    key: str
    name_de: str
    relation_de: str
    flashback_de: str
    is_parasite: bool


@dataclass
class FalscheFreundeEvent:
    """Deduction encounter where real memories contain friction and the parasite creates only sweet ones."""

    seed: int = 42
    suspects: dict[str, ParasiteSuspect] = field(default_factory=dict)
    parasite_key: str = ""
    resolved: bool = False
    correct_guess: bool | None = None
    inspected: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.suspects:
            rng = random.Random(self.seed)
            chosen = rng.choice(SUSPECT_KEYS)
            self.parasite_key = chosen
            for key, info in SUSPECT_DEFINITIONS.items():
                is_para = key == chosen
                flashback = info["sweet_flashback_de"] if is_para else info["grumpy_flashback_de"]
                self.suspects[key] = ParasiteSuspect(
                    key=key,
                    name_de=info["name_de"],
                    relation_de=info["relation_de"],
                    flashback_de=flashback,
                    is_parasite=is_para,
                )

    def inspect_suspect(self, key: str) -> ParasiteSuspect:
        if key not in self.suspects:
            raise KeyError(f"Unbekannter Verdächtiger: {key}")
        self.inspected.add(key)
        return self.suspects[key]

    def shoot_suspect(self, key: str) -> tuple[bool, str]:
        """Resolve the ambush by targeting one suspect based on memory inspection."""
        if key not in self.suspects:
            raise KeyError(f"Unbekannter Verdächtiger: {key}")
        suspect = self.suspects[key]
        self.resolved = True
        if suspect.is_parasite:
            self.correct_guess = True
            return (
                True,
                f"Treffer! {suspect.name_de} zerfällt in lila Sporen — die falschen Erinnerungen lösen sich auf.",
            )
        self.correct_guess = False
        return (
            False,
            f"Daneben! {suspect.name_de} ist zwar unleidlich, aber echt — der Parasit lacht hämisch aus dem Schatten.",
        )
