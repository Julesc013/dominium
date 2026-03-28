"""FAST test: CTRL-8 stacking order and reduction are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.control.effects.stacking_deterministic"
TEST_TAGS = ["fast", "control", "effects", "determinism"]


def _effect_type_registry() -> dict:
    return {
        "effect_types": [
            {
                "schema_version": "1.0.0",
                "effect_type_id": "effect.machine_degraded",
                "description": "test machine degradation",
                "applies_to": ["machine"],
                "modifies": ["machine_output_permille"],
                "default_visibility_policy_id": "effect.visibility.admin_numeric",
                "extensions": {},
            }
        ]
    }


def _stacking_policy_registry() -> dict:
    return {
        "stacking_policies": [
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.add",
                "mode": "add",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.min",
                "mode": "min",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.multiply",
                "mode": "multiply",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            },
        ]
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.effects import build_effect, get_effective_modifier

    target_id = "machine.alpha"
    rows = [
        build_effect(
            effect_type_id="effect.machine_degraded",
            target_id=target_id,
            applied_tick=10,
            magnitude={"machine_output_permille": 900},
            stacking_policy_id="stack.multiply",
        ),
        build_effect(
            effect_type_id="effect.machine_degraded",
            target_id=target_id,
            applied_tick=11,
            magnitude={"machine_output_permille": 800},
            stacking_policy_id="stack.multiply",
        ),
        build_effect(
            effect_type_id="effect.machine_degraded",
            target_id=target_id,
            applied_tick=12,
            magnitude={"machine_output_permille": 30},
            stacking_policy_id="stack.add",
        ),
        build_effect(
            effect_type_id="effect.machine_degraded",
            target_id=target_id,
            applied_tick=13,
            magnitude={"machine_output_permille": 700},
            stacking_policy_id="stack.min",
        ),
    ]
    first = get_effective_modifier(
        target_id=target_id,
        key="machine_output_permille",
        effect_rows=[rows[2], rows[0], rows[3], rows[1]],
        current_tick=20,
        effect_type_registry=_effect_type_registry(),
        stacking_policy_registry=_stacking_policy_registry(),
    )
    second = get_effective_modifier(
        target_id=target_id,
        key="machine_output_permille",
        effect_rows=[rows[1], rows[3], rows[0], rows[2]],
        current_tick=20,
        effect_type_registry=_effect_type_registry(),
        stacking_policy_registry=_stacking_policy_registry(),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "stacked modifier result drifted across input permutations"}
    if int(first.get("value", -1)) != 700:
        return {
            "status": "fail",
            "message": "unexpected stacked value {}, expected 700".format(int(first.get("value", -1))),
        }
    if list(first.get("stacking_modes") or []) != ["multiply", "multiply", "add", "min"]:
        return {"status": "fail", "message": "unexpected stacking mode order"}
    if len(list(first.get("applied_effect_ids") or [])) != 4:
        return {"status": "fail", "message": "expected all effect ids to participate in stacking result"}
    return {"status": "pass", "message": "effect stacking deterministic under canonical ordering"}

