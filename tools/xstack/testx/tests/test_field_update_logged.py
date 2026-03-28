"""FAST test: field updates emit deterministic update events and RECORD artifacts."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_field_update_logged"
TEST_TAGS = ["fast", "fields", "proof"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _build_state(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    state["field_layers"] = [
        build_field_layer(
            field_id="field.irradiance.global",
            field_type_id="field.irradiance",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.profile_defined",
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
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
    )

    state = _build_state(repo_root)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field_update.logged",
            "process_id": "process.field_update",
            "inputs": {
                "field_updates": [
                    {
                        "field_id": "field.irradiance.global",
                        "field_type_id": "field.irradiance",
                        "spatial_node_id": "cell.0.0.0",
                        "sampled_value": 275,
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

    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.field_update refused: {}".format(result)}
    if int(result.get("applied_update_count", 0) or 0) < 1:
        return {"status": "fail", "message": "field update was not applied"}

    update_rows = [dict(row) for row in list(state.get("field_update_events") or []) if isinstance(row, dict)]
    if not update_rows:
        return {"status": "fail", "message": "field_update_events missing after process.field_update"}
    event_row = dict(update_rows[-1])
    if str(event_row.get("source_process_id", "")).strip() != "process.field_update":
        return {"status": "fail", "message": "field update event source_process_id mismatch"}
    if str(event_row.get("update_kind", "")).strip() != "process_update":
        return {"status": "fail", "message": "field update event kind mismatch"}

    artifact_rows = [dict(row) for row in list(state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    has_event_artifact = False
    for row in artifact_rows:
        ext = dict(row.get("extensions") or {})
        if str(ext.get("artifact_type_id", "")).strip() == "artifact.field_update_event":
            has_event_artifact = True
            break
    if not has_event_artifact:
        return {"status": "fail", "message": "field update RECORD artifact was not emitted"}

    for key in ("field_update_hash_chain", "field_sample_hash_chain", "boundary_field_exchange_hash_chain"):
        token = str(state.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing/invalid {} after field update".format(key)}

    return {"status": "pass", "message": "field updates logged with deterministic event/artifact/hash chains"}

