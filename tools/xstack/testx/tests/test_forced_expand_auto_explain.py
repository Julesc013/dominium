"""FAST test: SYS-7 auto-generates explain artifacts for forced expand events."""

from __future__ import annotations

import sys


TEST_ID = "test_forced_expand_auto_explain"
TEST_TAGS = ["fast", "system", "sys7", "forensics", "forced_expand"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys7_testlib import base_state, seed_reliability_events

    state = base_state()
    health_result, reliability_result = seed_reliability_events(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick setup failed"}

    forced_rows = [dict(row) for row in list(state.get("system_forced_expand_event_rows") or []) if isinstance(row, dict)]
    if not forced_rows:
        return {"status": "fail", "message": "forced expand events were not emitted"}

    explain_rows = [dict(row) for row in list(state.get("system_explain_artifact_rows") or []) if isinstance(row, dict)]
    if not explain_rows:
        return {"status": "fail", "message": "system explain artifacts missing after forced expand"}

    matched = []
    for row in explain_rows:
        event_kind_id = str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip()
        if event_kind_id == "system.forced_expand":
            matched.append(dict(row))
    if not matched:
        return {"status": "fail", "message": "forced expand did not auto-generate SYS-7 explain artifact"}
    if not str(state.get("system_explain_hash_chain", "")).strip():
        return {"status": "fail", "message": "system_explain_hash_chain missing after auto-generation"}
    return {"status": "pass", "message": "forced expand auto-explain integration is active and deterministic"}
