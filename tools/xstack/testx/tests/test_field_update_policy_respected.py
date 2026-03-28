"""FAST test: process.field_update respects field update policy guards."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_field_update_policy_respected"
TEST_TAGS = ["fast", "fields", "policy"]


def _cell_value(state: dict, field_id: str, cell_id: str):
    for row in list(state.get("field_cells") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("field_id", "")).strip() != str(field_id).strip():
            continue
        if str(row.get("cell_id", "")).strip() != str(cell_id).strip():
            continue
        return row.get("value")
    return None


def _run_update(repo_root: str, *, update_policy_id: str, update_value: int):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0)
    state["field_layers"] = [
        build_field_layer(
            field_id="field.irradiance.global",
            field_type_id="field.irradiance",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id=update_policy_id,
            extensions={},
        )
    ]
    state["field_cells"] = [
        build_field_cell(
            field_id="field.irradiance.global",
            cell_id="cell.0.0.0",
            value=0,
            value_kind="scalar",
            last_updated_tick=0,
            extensions={},
        )
    ]

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.policy.{}".format(update_policy_id.replace(".", "_")),
            "process_id": "process.field_update",
            "inputs": {
                "field_updates": [
                    {
                        "field_id": "field.irradiance.global",
                        "field_type_id": "field.irradiance",
                        "spatial_node_id": "cell.0.0.0",
                        "sampled_value": int(update_value),
                        "spatial_scope_id": "spatial.global",
                        "resolution_level": "macro",
                    }
                ]
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.field_update"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    return {"state": state, "result": result}


def run(repo_root: str):
    static_case = _run_update(repo_root=repo_root, update_policy_id="field.static_default", update_value=42)
    mutable_case = _run_update(repo_root=repo_root, update_policy_id="field.profile_defined", update_value=42)

    static_result = dict(static_case.get("result") or {})
    mutable_result = dict(mutable_case.get("result") or {})
    if str(static_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "static policy case refused: {}".format(static_result)}
    if str(mutable_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "profile-defined policy case refused: {}".format(mutable_result)}

    static_state = dict(static_case.get("state") or {})
    mutable_state = dict(mutable_case.get("state") or {})
    static_applied = int(max(0, int(static_result.get("applied_update_count", 0) or 0)))
    static_skipped = int(max(0, int(static_result.get("skipped_update_count", 0) or 0)))
    if static_applied != 0 or static_skipped < 1:
        return {"status": "fail", "message": "static policy should reject process.field_update writes"}
    if _cell_value(static_state, "field.irradiance.global", "cell.0.0.0") != 0:
        return {"status": "fail", "message": "static policy write unexpectedly mutated field cell value"}

    mutable_applied = int(max(0, int(mutable_result.get("applied_update_count", 0) or 0)))
    if mutable_applied < 1:
        return {"status": "fail", "message": "profile-defined policy should allow process.field_update writes"}
    if int(_cell_value(mutable_state, "field.irradiance.global", "cell.0.0.0") or 0) != 42:
        return {"status": "fail", "message": "profile-defined policy write did not mutate field cell value"}

    return {"status": "pass", "message": "field update policy guard enforced deterministically"}

