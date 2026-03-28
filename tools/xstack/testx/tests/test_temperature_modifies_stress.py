"""FAST test: FIELD temperature modifiers reduce mechanics stress capacity via effects."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_temperature_modifies_stress"
TEST_TAGS = ["fast", "fields", "mechanics", "effects"]


def _law_profile() -> dict:
    allowed = ["process.field_tick", "process.mechanics_tick"]
    return {
        "law_profile_id": "law.test.fields.mechanics",
        "allowed_processes": list(allowed),
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.field_tick": "session.boot",
            "process.mechanics_tick": "session.boot",
        },
        "process_privilege_requirements": {
            "process.field_tick": "observer",
            "process.mechanics_tick": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000000, "allow_hidden_state_access": False},
        "epistemic_policy_id": "ep.policy.player_diegetic",
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.fields.mechanics",
        "subject_id": "subject.test.fields.mechanics",
        "law_profile_id": "law.test.fields.mechanics",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.test.fields", "visibility_level": "nondiegetic"},
        "privilege_level": "observer",
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mechanics_testlib import base_state, policy_context

    state = copy.deepcopy(base_state())
    state["field_layers"] = [
        build_field_layer(
            field_id="field.temperature.global",
            field_type_id="field.temperature",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": -30},
        ),
        build_field_layer(
            field_id="field.moisture.global",
            field_type_id="field.moisture",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 200},
        ),
        build_field_layer(
            field_id="field.friction.global",
            field_type_id="field.friction",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 1000},
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
            extensions={"default_value": {"x": 0, "y": 0, "z": 0}},
        ),
    ]
    state["field_cells"] = [
        build_field_cell(field_id="field.temperature.global", cell_id="cell.default", value=-30, last_updated_tick=0),
        build_field_cell(field_id="field.moisture.global", cell_id="cell.default", value=200, last_updated_tick=0),
        build_field_cell(field_id="field.friction.global", cell_id="cell.default", value=1000, last_updated_tick=0),
        build_field_cell(field_id="field.radiation.global", cell_id="cell.default", value=0, last_updated_tick=0),
        build_field_cell(field_id="field.visibility.global", cell_id="cell.default", value=1000, last_updated_tick=0),
        build_field_cell(
            field_id="field.wind.global",
            cell_id="cell.default",
            value={"x": 0, "y": 0, "z": 0},
            value_kind="vector",
            last_updated_tick=0,
        ),
    ]
    state["effect_rows"] = []
    state["effect_provenance_events"] = []

    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.mechanics.001",
            "process_id": "process.field_tick",
            "inputs": {
                "sample_rows": [
                    {"target_id": "structural.graph.alpha", "spatial_position": {"cell_id": "cell.default"}}
                ],
                "effect_duration_ticks": 2,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=policy_context(),
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.field_tick failed for mechanics-temperature fixture"}

    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.mechanics.002",
            "process_id": "process.mechanics_tick",
            "inputs": {"current_tick": 1},
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=policy_context(),
    )
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.mechanics_tick failed after FIELD temperature effects"}

    edge_rows = [dict(row) for row in list(state.get("structural_edges") or []) if isinstance(row, dict)]
    if not edge_rows:
        return {"status": "fail", "message": "mechanics edge rows missing after mechanics tick"}
    edge = dict(edge_rows[0])
    effective_max = int(edge.get("effective_max_load", 0))
    base_max = int(edge.get("max_load", 0))
    if effective_max >= base_max:
        return {
            "status": "fail",
            "message": "temperature modifier did not reduce effective_max_load ({} >= {})".format(effective_max, base_max),
        }
    return {"status": "pass", "message": "temperature-driven stress modifier applied to mechanics capacity"}

