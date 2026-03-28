"""STRICT test: field replay hashes are stable across equivalent ordering variants."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_replay_field_hash_match"
TEST_TAGS = ["strict", "fields", "proof", "replay", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_variant(repo_root: str, *, reverse_order: bool):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer
    from tools.physics.tool_replay_field_window import verify_field_replay_window
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
            update_policy_id="field.profile_defined",
            extensions={},
        )
    ]
    state["field_cells"] = [
        build_field_cell(
            field_id="field.irradiance.global",
            cell_id="cell.a",
            value=0,
            value_kind="scalar",
            last_updated_tick=0,
            extensions={},
        ),
        build_field_cell(
            field_id="field.irradiance.global",
            cell_id="cell.b",
            value=0,
            value_kind="scalar",
            last_updated_tick=0,
            extensions={},
        ),
    ]

    updates = [
        {
            "field_id": "field.irradiance.global",
            "field_type_id": "field.irradiance",
            "spatial_node_id": "cell.a",
            "sampled_value": 175,
            "spatial_scope_id": "spatial.global",
            "resolution_level": "macro",
        },
        {
            "field_id": "field.irradiance.global",
            "field_type_id": "field.irradiance",
            "spatial_node_id": "cell.b",
            "sampled_value": 325,
            "spatial_scope_id": "spatial.global",
            "resolution_level": "macro",
        },
    ]
    if reverse_order:
        updates = list(reversed(updates))

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.replay.hash.{}".format("b" if reverse_order else "a"),
            "process_id": "process.field_update",
            "inputs": {
                "field_updates": list(updates),
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.field_update"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    replay_report = verify_field_replay_window(state_payload=dict(state), expected_payload=None)
    return {"state": state, "result": dict(result), "replay_report": dict(replay_report)}


def _chain(state: dict, key: str) -> str:
    return str(state.get(key, "")).strip().lower()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.physics.tool_replay_field_window import verify_field_replay_window

    first = _run_variant(repo_root=repo_root, reverse_order=False)
    second = _run_variant(repo_root=repo_root, reverse_order=True)

    result_a = dict(first.get("result") or {})
    result_b = dict(second.get("result") or {})
    if str(result_a.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline field replay run refused: {}".format(result_a)}
    if str(result_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "reordered field replay run refused: {}".format(result_b)}

    report_a = dict(first.get("replay_report") or {})
    report_b = dict(second.get("replay_report") or {})
    if str(report_a.get("result", "")) != "complete":
        return {"status": "fail", "message": "tool_replay_field_window failed baseline variant: {}".format(report_a)}
    if str(report_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "tool_replay_field_window failed reorder variant: {}".format(report_b)}

    state_a = dict(first.get("state") or {})
    state_b = dict(second.get("state") or {})
    for key in ("field_update_hash_chain", "field_sample_hash_chain", "boundary_field_exchange_hash_chain"):
        token_a = _chain(state_a, key)
        token_b = _chain(state_b, key)
        if (not _HASH64.fullmatch(token_a)) or (not _HASH64.fullmatch(token_b)):
            return {"status": "fail", "message": "missing or invalid {} on replay variants".format(key)}
        if token_a != token_b:
            return {"status": "fail", "message": "{} diverged across equivalent ordering variants".format(key)}

    cross_report = verify_field_replay_window(state_payload=state_a, expected_payload=state_b)
    if str(cross_report.get("result", "")) != "complete":
        return {
            "status": "fail",
            "message": "cross-variant field replay verification mismatch: {}".format(cross_report),
        }

    return {"status": "pass", "message": "field replay hash chains stable across ordering variants"}

