"""FAST test: CTRL-8 effect expiration is deterministic and tick-based only."""

from __future__ import annotations

import sys


TEST_ID = "testx.control.effects.expiration_deterministic"
TEST_TAGS = ["fast", "control", "effects", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.effects import build_effect, prune_expired_effect_rows

    target_id = "portal.alpha"
    rows = [
        build_effect(
            effect_type_id="effect.visibility_reduction",
            target_id=target_id,
            applied_tick=10,
            duration_ticks=5,
            magnitude={"visibility_permille": 700},
            stacking_policy_id="stack.min",
        ),
        build_effect(
            effect_type_id="effect.access_restricted",
            target_id=target_id,
            applied_tick=9,
            duration_ticks=None,
            magnitude={"access_restricted": 1000},
            stacking_policy_id="stack.replace_latest",
        ),
        build_effect(
            effect_type_id="effect.visibility_reduction",
            target_id=target_id,
            applied_tick=12,
            duration_ticks=1,
            magnitude={"visibility_permille": 600},
            stacking_policy_id="stack.min",
        ),
    ]
    shuffled = [rows[2], rows[0], rows[1]]

    active_tick_14_a = prune_expired_effect_rows(effect_rows=shuffled, current_tick=14)
    active_tick_14_b = prune_expired_effect_rows(effect_rows=shuffled, current_tick=14)
    if active_tick_14_a != active_tick_14_b:
        return {"status": "fail", "message": "effect expiration drift at tick 14 for identical inputs"}
    if len(active_tick_14_a) != 2:
        return {"status": "fail", "message": "expected 2 active effects at tick 14"}

    active_tick_15 = prune_expired_effect_rows(effect_rows=shuffled, current_tick=15)
    if len(active_tick_15) != 1:
        return {"status": "fail", "message": "expected 1 active effect at tick 15 after expiration boundary"}
    remaining = dict(active_tick_15[0] if active_tick_15 else {})
    if str(remaining.get("effect_type_id", "")) != "effect.access_restricted":
        return {"status": "fail", "message": "wrong effect remained after expiration boundary"}

    ordering = [
        (
            str(row.get("target_id", "")),
            str(row.get("effect_type_id", "")),
            int(row.get("applied_tick", 0) or 0),
            str(row.get("effect_id", "")),
        )
        for row in list(active_tick_14_a or [])
    ]
    if ordering != sorted(ordering):
        return {"status": "fail", "message": "active effect ordering is not deterministic"}
    return {"status": "pass", "message": "effect expiration deterministic and tick-gated"}

