"""Klonita expansion dialogue cascades for cauldron, shifts, and Phase J universes (K03)."""

from __future__ import annotations

import random

EXPANSION_DIALOGUES: dict[str, tuple[str, ...]] = {
    # Cauldron & Alchemy (bibel/erweiterung 04)
    "cauldron_boil": ("Es blubbert so schön! Riecht wie Pfefferminztee!",),
    "cauldron_danger": ("Cloita? Warum wird der Kessel so rot? Soll der zittern?!",),
    "alchemy_schutztonikum": ("Ooooh, das glitzert wie Limonade! Schmeckt bestimmt lecker!",),
    "alchemy_gold_vein": ("Guck mal, die Steine glänzen! Können wir daraus Schmuck basteln?",),
    # Reality shifts
    "shift_start": ("Wooooah... Cloita! Die Decke tanzt Walzer!",),
    "shift_acid_water": ("Juhu! Wir können gefahrlos planschen! Das Leben ist schön!",),
    "shift_paper_cover": ("Oh, die Akten sind jetzt viel stabiler! Da knickt nichts mehr um!",),
    # The 6 pool universes
    "enter_schrott": ("Hier liegt bestimmt mein alter Dreirad-Lenker! Ich geh mal suchen!",),
    "enter_kuchen": ("Ich hab an der Wand geleckt. Schmeckt nach Vanille und etwas Asche!",),
    "enter_spule": ("Meine Zunge schmeckt nach 9-Volt-Batterie! Willst du mal probieren?",),
    "enter_uhrwerkwueste": ("Tick... tack... Cloita, warum laufen wir auf einmal so laaaangsam?",),
    "enter_suppenmeer": ("Guck mal! Die Nudeln da drüben sagen Hallo! Ich winke zurück!",),
    "enter_freizeitpark": ("Können wir Riesenrad fahren?! Bitte, bitte! Nur drei Runden!",),
}


def expansion_line_for(topic: str, rng: random.Random | None = None) -> str:
    """Return a German Klonita line for an expansion topic or universe key."""
    lines = EXPANSION_DIALOGUES.get(topic) or EXPANSION_DIALOGUES.get(f"enter_{topic}", ())
    if not lines:
        return ""
    chooser = rng or random.Random(0)
    return chooser.choice(lines)
