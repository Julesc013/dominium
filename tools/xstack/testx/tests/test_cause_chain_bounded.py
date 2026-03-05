"""FAST test: SYS-7 cause chains are deterministically bounded."""

from __future__ import annotations

import sys


TEST_ID = "test_cause_chain_bounded"
TEST_TAGS = ["fast", "system", "sys7", "forensics", "bounded"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys7_testlib import (
        base_state,
        execute_system_explain,
        seed_reliability_events,
    )

    state = base_state()
    health_result, reliability_result = seed_reliability_events(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick setup failed"}

    system_rows = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, dict)]
    system_id = str((system_rows[0] if system_rows else {}).get("system_id", "")).strip()
    if not system_id:
        return {"status": "fail", "message": "system_id missing from seeded state"}

    explain_result = execute_system_explain(
        repo_root=repo_root,
        state=state,
        system_id=system_id,
        explain_level="L3",
        requester_policy_id="policy.epistemic.admin",
        requester_subject_id="admin.sys7",
        max_cause_entries=3,
    )
    if str(explain_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process.system_generate_explain did not complete"}
    artifact = dict(explain_result.get("sys7_explain_artifact") or {})
    if not artifact:
        return {"status": "fail", "message": "system explain artifact row not persisted"}

    cause_chain = list(artifact.get("cause_chain") or [])
    if len(cause_chain) > 3:
        return {"status": "fail", "message": "cause_chain exceeded max_cause_entries bound"}
    if len(list(artifact.get("referenced_event_ids") or [])) > 3:
        return {"status": "fail", "message": "referenced_event_ids exceeded bounded selection"}
    if len(list(artifact.get("referenced_specs") or [])) > 3:
        return {"status": "fail", "message": "referenced_specs exceeded bounded selection"}
    return {"status": "pass", "message": "SYS-7 cause chain bounding is deterministic and enforced"}
