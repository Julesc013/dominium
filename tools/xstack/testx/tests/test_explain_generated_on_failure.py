"""FAST test: SYS-5 certification failure emits explain artifact deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_explain_generated_on_failure"
TEST_TAGS = ["fast", "system", "sys5", "certification", "explain"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys5_testlib import base_state, execute_system_certification

    state = base_state(compliance_grade="fail")
    result = execute_system_certification(repo_root=repo_root, state=state)
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "certification process did not complete on fail path"}

    explain_rows = [dict(row) for row in list(state.get("explain_artifact_rows") or []) if isinstance(row, dict)]
    if not explain_rows:
        return {"status": "fail", "message": "expected explain artifact for certification failure"}
    if not any(
        str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip() == "system.certification_failure"
        for row in explain_rows
    ):
        return {"status": "fail", "message": "certification failure explain artifact missing event_kind_id linkage"}
    return {"status": "pass", "message": "certification failure explain artifact generated deterministically"}

