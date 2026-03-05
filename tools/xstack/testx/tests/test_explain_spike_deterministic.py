"""FAST test: POLL explain.pollution_spike generation is deterministic and source-traceable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_explain_spike_deterministic"
TEST_TAGS = ["fast", "pollution", "explain", "determinism"]


def _pollution_spike_rows(state: dict):
    return [
        dict(row)
        for row in list(state.get("explain_artifact_rows") or [])
        if isinstance(row, dict)
        and str((dict(row.get("extensions") or {})).get("event_kind_id", "")).strip()
        == "pollution.spike"
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_testlib import execute_pollution_emit, seed_pollution_state

    inputs = {
        "policy_id": "poll.policy.rank_strict",
        "events": [
            {
                "origin_kind": "fire",
                "origin_id": "event.fire.003",
                "pollutant_id": "pollutant.smoke_particulate",
                "emitted_mass": 12,
                "spatial_scope_id": "region.gamma",
            }
        ],
    }

    first_state = seed_pollution_state()
    second_state = seed_pollution_state()
    first_out = execute_pollution_emit(repo_root=repo_root, state=first_state, inputs=copy.deepcopy(inputs))
    second_out = execute_pollution_emit(repo_root=repo_root, state=second_state, inputs=copy.deepcopy(inputs))
    if str(first_out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first pollution emit failed: {}".format(first_out)}
    if str(second_out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second pollution emit failed: {}".format(second_out)}

    first_rows = _pollution_spike_rows(first_state)
    second_rows = _pollution_spike_rows(second_state)
    if not first_rows:
        return {"status": "fail", "message": "missing pollution spike explain row"}
    if first_rows != second_rows:
        return {"status": "fail", "message": "pollution spike explain rows drifted"}

    row = dict(first_rows[0])
    cause_chain = [str(token).strip() for token in list(row.get("cause_chain") or []) if str(token).strip()]
    if not any(token.startswith("cause.pollution.source_chain.") for token in cause_chain):
        return {"status": "fail", "message": "pollution spike explain missing source-chain cause token"}
    if not any(token.startswith("cause.pollution.policy.") for token in cause_chain):
        return {"status": "fail", "message": "pollution spike explain missing policy cause token"}
    if str((dict(row.get("extensions") or {})).get("explain_artifact_type_id", "")).strip() != "artifact.explain.pollution_spike":
        return {"status": "fail", "message": "pollution spike explain artifact type mismatch"}
    return {"status": "pass", "message": "pollution spike explain deterministic and source-traceable"}
