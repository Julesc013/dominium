"""FAST test: PROC-7 candidate promotion enforces replication thresholds."""

from __future__ import annotations

import sys


TEST_ID = "test_promotion_requires_replication"
TEST_TAGS = ["fast", "proc", "proc7", "promotion", "replication"]


def _contains_process_definition(rows: list[dict], process_id: str, version: str) -> bool:
    for row in rows:
        if str(row.get("process_id", "")).strip() != str(process_id).strip():
            continue
        if str(row.get("version", "")).strip() != str(version).strip():
            continue
        return True
    return False


def _refusal_reason(result: dict) -> str:
    if not isinstance(result, dict):
        return ""
    top = str(result.get("reason_code", "")).strip()
    if top:
        return top
    refusal = dict(result.get("refusal") or {})
    return str(refusal.get("reason_code", "")).strip()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc7_testlib import (
        cloned_state,
        execute_process,
        seed_candidate_for_promotion,
    )

    candidate_id = "candidate.process.proc7.replication"
    process_id = "proc.test.proc7.promoted"
    version = "1.0.0"

    low_rep_state = cloned_state(repo_root, process_id=process_id, version=version)
    seed_candidate_for_promotion(
        repo_root=repo_root,
        state=low_rep_state,
        candidate_id=candidate_id,
        process_id=process_id,
        version=version,
        replications=2,
    )
    denied = execute_process(
        repo_root=repo_root,
        state=low_rep_state,
        process_id="process.candidate_promote_to_defined",
        inputs={
            "candidate_id": candidate_id,
            "required_replications": 3,
            "min_qc_pass_rate": 700,
            "min_stabilization_score": 650,
        },
    )
    if str(denied.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "promotion should refuse below replication threshold"}
    if _refusal_reason(denied) != "refusal.process.candidate.promotion_denied":
        return {"status": "fail", "message": "unexpected refusal code for replication-gated promotion"}

    passing_state = cloned_state(repo_root, process_id=process_id, version=version)
    seed_candidate_for_promotion(
        repo_root=repo_root,
        state=passing_state,
        candidate_id=candidate_id,
        process_id=process_id,
        version=version,
        replications=3,
    )
    promoted = execute_process(
        repo_root=repo_root,
        state=passing_state,
        process_id="process.candidate_promote_to_defined",
        inputs={
            "candidate_id": candidate_id,
            "required_replications": 3,
            "min_qc_pass_rate": 700,
            "min_stabilization_score": 650,
        },
    )
    if str(promoted.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "promotion should complete at replication threshold"}

    promotion_rows = [
        dict(row)
        for row in list(passing_state.get("candidate_promotion_record_rows") or [])
        if isinstance(row, dict)
    ]
    if not promotion_rows:
        return {"status": "fail", "message": "successful promotion did not emit canonical promotion record"}

    process_rows = [
        dict(row)
        for row in list(passing_state.get("process_definition_rows") or [])
        if isinstance(row, dict)
    ]
    if not _contains_process_definition(process_rows, process_id=process_id, version=version):
        return {"status": "fail", "message": "successful promotion did not materialize process definition"}

    return {"status": "pass", "message": "PROC-7 promotion replication gate enforced"}
