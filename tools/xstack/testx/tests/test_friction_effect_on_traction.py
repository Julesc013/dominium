"""FAST test: FIELD friction/moisture modifiers reduce traction and alter mobility motion."""

from __future__ import annotations

import sys


TEST_ID = "test_friction_effect_on_traction"
TEST_TAGS = ["fast", "fields", "mobility", "effects"]


def _law_profile() -> dict:
    allowed = ["process.field_tick", "process.body_move_attempt"]
    return {
        "law_profile_id": "law.test.fields.mobility",
        "allowed_processes": list(allowed),
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.field_tick": "session.boot",
            "process.body_move_attempt": "entitlement.control.possess",
        },
        "process_privilege_requirements": {
            "process.field_tick": "observer",
            "process.body_move_attempt": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000000, "allow_hidden_state_access": False},
        "epistemic_policy_id": "ep.policy.player_diegetic",
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.fields",
        "subject_id": "subject.test.fields",
        "law_profile_id": "law.test.fields.mobility",
        "entitlements": ["session.boot", "entitlement.control.possess"],
        "epistemic_scope": {"scope_id": "scope.test.fields", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import base_state

    state = base_state()
    state["body_assemblies"] = [
        {
            "assembly_id": "aircraft.test.alpha",
            "owner_assembly_id": "aircraft.test.alpha",
            "shape_type": "capsule",
            "shape_parameters": {"radius_mm": 500, "height_mm": 1500, "half_extents_mm": {"x": 500, "y": 500, "z": 750}},
            "collision_layer": "layer.default",
            "dynamic": True,
            "ghost": False,
            "transform_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
        }
    ]
    state["field_layers"] = [
        build_field_layer(
            field_id="field.temperature.global",
            field_type_id="field.temperature",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 15},
        ),
        build_field_layer(
            field_id="field.moisture.global",
            field_type_id="field.moisture",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 800},
        ),
        build_field_layer(
            field_id="field.friction.global",
            field_type_id="field.friction",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 400},
        ),
        build_field_layer(
            field_id="field.radiation.global",
            field_type_id="field.radiation",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 0},
        ),
        build_field_layer(
            field_id="field.visibility.global",
            field_type_id="field.visibility",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 1000},
        ),
        build_field_layer(
            field_id="field.wind.global",
            field_type_id="field.wind",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": {"x": 300, "y": 100, "z": 0}},
        ),
    ]
    state["field_cells"] = [
        build_field_cell(field_id="field.temperature.global", cell_id="cell.default", value=15, last_updated_tick=0),
        build_field_cell(field_id="field.moisture.global", cell_id="cell.default", value=800, last_updated_tick=0),
        build_field_cell(field_id="field.friction.global", cell_id="cell.default", value=400, last_updated_tick=0),
        build_field_cell(field_id="field.radiation.global", cell_id="cell.default", value=0, last_updated_tick=0),
        build_field_cell(field_id="field.visibility.global", cell_id="cell.default", value=1000, last_updated_tick=0),
        build_field_cell(
            field_id="field.wind.global",
            cell_id="cell.default",
            value={"x": 300, "y": 100, "z": 0},
            value_kind="vector",
            last_updated_tick=0,
        ),
    ]
    state["effect_rows"] = []
    state["effect_provenance_events"] = []

    field_tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.mobility.001",
            "process_id": "process.field_tick",
            "inputs": {
                "sample_rows": [
                    {"target_id": "aircraft.test.alpha", "spatial_position": {"cell_id": "cell.default"}}
                ],
                "effect_duration_ticks": 3,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context={"pack_lock_hash": "a" * 64},
    )
    if str(field_tick.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.field_tick failed for friction test fixture"}

    effect_rows = [dict(row) for row in list(state.get("effect_rows") or []) if isinstance(row, dict)]
    effect_types = sorted(set(str(row.get("effect_type_id", "")).strip() for row in effect_rows if str(row.get("effect_type_id", "")).strip()))
    if "effect.traction_reduction" not in effect_types:
        return {"status": "fail", "message": "expected effect.traction_reduction from FIELD friction/moisture sample"}

    moved = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.mobility.002",
            "process_id": "process.body_move_attempt",
            "inputs": {
                "body_id": "aircraft.test.alpha",
                "delta_transform_mm": {"x": 1000, "y": 0, "z": 0},
                "dt_ticks": 1,
                "is_aircraft": True,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context={"pack_lock_hash": "a" * 64},
    )
    if str(moved.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.body_move_attempt failed after FIELD effects"}
    delta = dict(
        moved.get("movement_delta_mm")
        or (moved.get("result_metadata", {}) or {}).get("movement_delta_mm")
        or {}
    )
    moved_x = int(delta.get("x", 0))
    moved_y = int(delta.get("y", 0))
    if moved_x >= 1000:
        return {"status": "fail", "message": "traction reduction did not reduce mobility delta_x"}
    if moved_y == 0:
        return {"status": "fail", "message": "aircraft wind drift did not alter lateral delta_y"}
    return {"status": "pass", "message": "friction/moisture traction and wind drift modifiers are applied"}
