"""FAST test: canonical gravity force model applies deterministic momentum delta."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_gravity_force_model_applies"
TEST_TAGS = ["fast", "physics", "field", "gravity"]


def _find_row(rows: object, key: str, value: str) -> dict:
    token = str(value or "").strip()
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        if str(row.get(key, "")).strip() == token:
            return dict(row)
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.fields import build_field_cell, build_field_layer
    from src.physics import build_momentum_state
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0)
    body_id = "body.vehicle.mob.free.alpha"
    state["momentum_states"] = [
        build_momentum_state(
            assembly_id=body_id,
            mass_value=4,
            momentum_linear={"x": 0, "y": 0, "z": 0},
            momentum_angular=0,
            last_update_tick=0,
            extensions={},
        )
    ]
    state["field_layers"] = list(state.get("field_layers") or []) + [
        build_field_layer(
            field_id="field.gravity_vector.global",
            field_type_id="field.gravity_vector",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static_default",
            extensions={"cell_size_mm": 10000},
        )
    ]
    state["field_cells"] = list(state.get("field_cells") or []) + [
        build_field_cell(
            field_id="field.gravity_vector.global",
            cell_id="cell.0.0.0",
            value={"x": 0, "y": -9, "z": 0},
            value_kind="vector",
            last_updated_tick=0,
            extensions={},
        )
    ]

    policy = copy.deepcopy(policy_context())
    policy["physics_profile_id"] = "phys.realistic.default"
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.gravity.canonical.001",
            "process_id": "process.model_evaluate_tick",
            "inputs": {
                "gravity_target_ids": [body_id],
                "gravity_duration_ticks": 1,
                "max_cost_units": 64,
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.model_evaluate_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=policy,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "model_evaluate_tick refused: {}".format(result)}
    if int(result.get("output_process_count", 0) or 0) < 1:
        return {"status": "fail", "message": "gravity model did not emit process-backed outputs"}

    force_row = _find_row(state.get("force_application_rows"), "target_assembly_id", body_id)
    if not force_row:
        return {"status": "fail", "message": "missing force application row after gravity model"}
    expected_force = {"x": 0, "y": -36, "z": 0}
    if dict(force_row.get("force_vector") or {}) != expected_force:
        return {"status": "fail", "message": "gravity force vector mismatch for canonical model"}

    momentum_row = _find_row(state.get("momentum_states"), "assembly_id", body_id)
    if not momentum_row:
        return {"status": "fail", "message": "missing momentum row after gravity model"}
    if dict(momentum_row.get("momentum_linear") or {}) != expected_force:
        return {"status": "fail", "message": "gravity model did not translate force to momentum delta"}

    return {"status": "pass", "message": "canonical gravity model applies deterministic force via process path"}
