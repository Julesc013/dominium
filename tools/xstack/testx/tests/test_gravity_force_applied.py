"""FAST test: gravity stub applies deterministic force via model pathway."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_gravity_force_applied"
TEST_TAGS = ["fast", "physics", "model", "gravity"]


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

    from fields import build_field_cell, build_field_layer
    from physics import build_momentum_state
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
            mass_value=5,
            momentum_linear={"x": 0, "y": 0, "z": 0},
            momentum_angular=0,
            last_update_tick=0,
            extensions={},
        )
    ]

    state["field_layers"] = list(state.get("field_layers") or []) + [
        build_field_layer(
            field_id="field.gravity.vector",
            field_type_id="field.gravity.vector",
            spatial_scope_id="spatial.mob.free.alpha",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"cell_size_mm": 10000},
        )
    ]
    state["field_cells"] = list(state.get("field_cells") or []) + [
        build_field_cell(
            field_id="field.gravity.vector",
            cell_id="cell.0.0.0",
            value={"x": 0, "y": -9, "z": 0},
            last_updated_tick=0,
            value_kind="vector",
            extensions={},
        )
    ]

    law = law_profile(["process.model_evaluate_tick"])
    authority = authority_context()
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.default"

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.gravity.001",
            "process_id": "process.model_evaluate_tick",
            "inputs": {
                "gravity_target_ids": [body_id],
                "gravity_duration_ticks": 1,
                "max_cost_units": 64,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "model_evaluate_tick refused gravity test: {}".format(result)}
    if int(result.get("output_process_count", 0) or 0) < 1:
        return {"status": "fail", "message": "gravity model did not emit process-backed output"}

    force_row = _find_row(state.get("force_application_rows"), "target_assembly_id", body_id)
    if not force_row:
        return {"status": "fail", "message": "gravity model did not persist force_application row"}
    expected_force = {"x": 0, "y": -45, "z": 0}  # mass(5) * gravity(0,-9,0)
    if dict(force_row.get("force_vector") or {}) != expected_force:
        return {"status": "fail", "message": "gravity force_vector mismatch"}

    momentum_row = _find_row(state.get("momentum_states"), "assembly_id", body_id)
    if not momentum_row:
        return {"status": "fail", "message": "gravity model did not update momentum state"}
    if dict(momentum_row.get("momentum_linear") or {}) != expected_force:
        return {"status": "fail", "message": "gravity force did not translate into momentum delta"}
    return {"status": "pass", "message": "gravity stub applies force through constitutive model path"}
