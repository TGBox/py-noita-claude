"""Phase M01 Stress Matrix: Splitters, Protocols, Wrapping & Recursion Limits."""

from __future__ import annotations

from src.wand import MAX_RECURSION_DEPTH, MAX_SHOTS_PER_CAST, Wand, WandSpec


def _wand(*blocks: str, casts: int = 1) -> Wand:
    return Wand(
        WandSpec(
            "Stress",
            blocks,
            mana_max=5000.0,
            mana_regen=0.0,
            cast_delay=0.0,
            recharge=0.0,
            casts=casts,
        )
    )


def test_m01_module_math_stress_matrix() -> None:
    # Matrix of protocols combined with splitters and wrapping
    combos = [
        ("split_quadro", "split_trio", "funke"),
        ("split_dekade", "split_duo", "nadel"),
        ("proto_tau", "funke", "nadel"),
        ("proto_omega", "beschleunigung", "funke", "klumpen", "nadel"),
        ("proto_mu", "funke", "sprengkraft", "beschleunigung", "giftzahn"),
    ]
    for blocks in combos:
        w = _wand(*blocks)
        shots = w.cast()
        assert 1 <= len(shots) <= MAX_SHOTS_PER_CAST
        assert w.last_recursion_depth <= MAX_RECURSION_DEPTH

    # Self-referential protocol loops halt strictly at MAX_RECURSION_DEPTH
    loop_alpha = _wand("proto_alpha", "funke")
    assert loop_alpha.cast() == []
    assert loop_alpha.last_cutoff is True

    loop_gamma = _wand("funke", "proto_gamma")
    loop_gamma.cast()  # consume funke -> next cast hits proto_gamma copying itself
    loop_gamma.cooldown = 0.0
    assert loop_gamma.cast() == []
    assert loop_gamma.last_cutoff is True

    # Maximum depth splitter chain never exceeds 24 shots
    deep = _wand(*(["split_duo"] * MAX_RECURSION_DEPTH), "funke")
    shots = deep.cast()
    assert len(shots) == MAX_SHOTS_PER_CAST
    assert not deep.last_cutoff
