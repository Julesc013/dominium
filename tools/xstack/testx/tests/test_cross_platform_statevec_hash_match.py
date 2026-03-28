"""FAST test: STATEVEC0 hash chains are stable across equivalent input ordering."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_cross_platform_statevec_hash_match"
TEST_TAGS = ["fast", "statevec", "determinism", "replay"]


def _build_state(repo_root: str, *, reorder: bool) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system.statevec import (
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
    )
    from tools.xstack.testx.tests.statevec0_testlib import (
        source_state_payload,
        state_vector_definition_rows,
    )

    owner_id = "system.system.engine.alpha"
    definitions = normalize_state_vector_definition_rows(state_vector_definition_rows(owner_id=owner_id))
    source = source_state_payload()
    if reorder:
        source = {
            "root_assembly_id": source.get("root_assembly_id"),
            "assembly_rows": copy.deepcopy(source.get("assembly_rows")),
            "captured_tick": source.get("captured_tick"),
        }

    serialized = serialize_state(
        owner_id=owner_id,
        source_state=source,
        state_vector_definition_rows=definitions,
        current_tick=23,
        expected_version="1.0.0",
    )
    snapshot_rows = normalize_state_vector_snapshot_rows([dict(serialized.get("snapshot_row") or {})])
    return {
        "state_vector_definition_rows": definitions,
        "state_vector_snapshot_rows": snapshot_rows,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_verify_statevec_roundtrip import verify_statevec_roundtrip

    state_a = _build_state(repo_root, reorder=False)
    state_b = _build_state(repo_root, reorder=True)

    report = verify_statevec_roundtrip(state_payload=state_a, expected_payload=state_b)
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "statevec replay verifier reported violations: {}".format(
                report.get("violations", [])
            ),
        }

    observed = dict(report.get("observed") or {})
    expected = dict(report.get("expected") or {})
    if str(observed.get("state_vector_definition_hash_chain", "")).strip().lower() != str(
        expected.get("state_vector_definition_hash_chain", "")
    ).strip().lower():
        return {"status": "fail", "message": "definition hash chain mismatch"}
    if str(observed.get("state_vector_snapshot_hash_chain", "")).strip().lower() != str(
        expected.get("state_vector_snapshot_hash_chain", "")
    ).strip().lower():
        return {"status": "fail", "message": "snapshot hash chain mismatch"}

    return {"status": "pass", "message": "state vector hash chains stable across equivalent ordering"}
