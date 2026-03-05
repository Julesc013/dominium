"""FAST test: process.pollution_emit produces deterministic outputs for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_pollution_emit_deterministic"
TEST_TAGS = ["fast", "pollution", "determinism"]


def _snapshot(state: dict) -> dict:
    return {
        "pollution_source_event_rows": [dict(row) for row in list(state.get("pollution_source_event_rows") or []) if isinstance(row, dict)],
        "pollution_total_rows": [dict(row) for row in list(state.get("pollution_total_rows") or []) if isinstance(row, dict)],
        "pollution_source_hash_chain": str(state.get("pollution_source_hash_chain", "")).strip(),
        "pollution_total_hash_chain": str(state.get("pollution_total_hash_chain", "")).strip(),
        "pollution_explain_hash_chain": str(state.get("pollution_explain_hash_chain", "")).strip(),
        "explain_artifact_rows": [dict(row) for row in list(state.get("explain_artifact_rows") or []) if isinstance(row, dict)],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_testlib import execute_pollution_emit, seed_pollution_state

    inputs = {
        "policy_id": "poll.policy.coarse_diffuse",
        "events": [
            {
                "origin_kind": "fire",
                "origin_id": "event.fire.alpha",
                "pollutant_id": "pollutant.smoke_particulate",
                "emitted_mass": 14,
                "spatial_scope_id": "region.alpha",
            },
            {
                "origin_kind": "reaction",
                "origin_id": "run.chem.alpha",
                "pollutant_id": "pollutant.co2_stub",
                "emitted_mass": 9,
                "spatial_scope_id": "region.alpha",
            },
        ],
    }

    state_a = seed_pollution_state()
    state_b = seed_pollution_state()
    out_a = execute_pollution_emit(repo_root=repo_root, state=state_a, inputs=copy.deepcopy(inputs))
    out_b = execute_pollution_emit(repo_root=repo_root, state=state_b, inputs=copy.deepcopy(inputs))
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first pollution emit failed: {}".format(out_a)}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second pollution emit failed: {}".format(out_b)}

    snap_a = _snapshot(state_a)
    snap_b = _snapshot(state_b)
    if snap_a != snap_b:
        return {"status": "fail", "message": "pollution emit state drifted across equivalent runs"}
    return {"status": "pass", "message": "pollution emit deterministic snapshot stable"}
