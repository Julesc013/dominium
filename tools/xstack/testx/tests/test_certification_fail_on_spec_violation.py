"""FAST test: SYS-5 certification fails deterministically on SPEC violation."""

from __future__ import annotations

import sys


TEST_ID = "test_certification_fail_on_spec_violation"
TEST_TAGS = ["fast", "system", "sys5", "certification", "spec"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys5_testlib import base_state, execute_system_certification

    state = base_state(compliance_grade="fail")
    result = execute_system_certification(repo_root=repo_root, state=state)
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-5 certification process did not complete on fail-grade input"}

    rows = [dict(row) for row in list(state.get("system_certification_result_rows") or []) if isinstance(row, dict)]
    if not rows:
        return {"status": "fail", "message": "certification result row was not emitted"}
    latest = rows[-1]
    if bool(latest.get("pass", True)):
        return {"status": "fail", "message": "certification unexpectedly passed with failing SPEC compliance"}
    failed_checks = set(str(token).strip() for token in list(latest.get("failed_checks") or []) if str(token).strip())
    if "spec.compliance.pass" not in failed_checks:
        return {"status": "fail", "message": "failed checks missing spec.compliance.pass marker"}

    cert_rows = [dict(row) for row in list(state.get("system_certificate_artifact_rows") or []) if isinstance(row, dict)]
    if cert_rows:
        return {"status": "fail", "message": "certificate should not be issued when certification fails"}
    return {"status": "pass", "message": "certification fail path rejects SPEC violations deterministically"}

