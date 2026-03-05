"""FAST test: SYS-7 auto-generates explain artifacts for certificate revocations."""

from __future__ import annotations

import sys


TEST_ID = "test_certificate_revocation_explain"
TEST_TAGS = ["fast", "system", "sys7", "forensics", "certification"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys5_testlib import (
        base_state,
        execute_system_certification,
        execute_system_collapse,
    )

    state = base_state(compliance_grade="pass")
    cert_result = execute_system_certification(repo_root=repo_root, state=state)
    if str(cert_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "certification pass path failed"}

    cert_rows = [dict(row) for row in list(state.get("system_certificate_artifact_rows") or []) if isinstance(row, dict)]
    if not cert_rows:
        return {"status": "fail", "message": "certificate issuance missing before revocation test"}

    collapse_result = execute_system_collapse(repo_root=repo_root, state=state)
    if str(collapse_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "system collapse failed for revocation trigger"}

    revocation_rows = [dict(row) for row in list(state.get("system_certificate_revocation_rows") or []) if isinstance(row, dict)]
    if not revocation_rows:
        return {"status": "fail", "message": "certificate revocation rows missing after collapse"}

    explain_rows = [dict(row) for row in list(state.get("system_explain_artifact_rows") or []) if isinstance(row, dict)]
    if not explain_rows:
        return {"status": "fail", "message": "system explain artifacts missing after revocation"}
    matched = []
    for row in explain_rows:
        event_kind_id = str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip()
        if event_kind_id == "system.certificate_revocation":
            matched.append(dict(row))
    if not matched:
        return {"status": "fail", "message": "certificate revocation did not auto-generate SYS-7 explain artifact"}
    if not str(state.get("system_explain_hash_chain", "")).strip():
        return {"status": "fail", "message": "system_explain_hash_chain missing after revocation explain"}
    return {"status": "pass", "message": "certificate revocation explain integration is deterministic and active"}
