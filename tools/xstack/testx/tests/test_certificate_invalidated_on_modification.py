"""FAST test: SYS-5 certificate invalidates on material system modification."""

from __future__ import annotations

import sys


TEST_ID = "test_certificate_invalidated_on_modification"
TEST_TAGS = ["fast", "system", "sys5", "certification", "revocation"]


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
        return {"status": "fail", "message": "baseline certification run failed"}
    cert_rows = [dict(row) for row in list(state.get("system_certificate_artifact_rows") or []) if isinstance(row, dict)]
    if not cert_rows:
        return {"status": "fail", "message": "baseline certification did not issue certificate"}
    cert_id = str(cert_rows[-1].get("cert_id", "")).strip()
    if not cert_id:
        return {"status": "fail", "message": "issued certificate row missing cert_id"}

    collapse_result = execute_system_collapse(repo_root=repo_root, state=state, system_id="system.engine.alpha")
    if str(collapse_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "system collapse failed during revocation test"}

    updated_rows = [dict(row) for row in list(state.get("system_certificate_artifact_rows") or []) if isinstance(row, dict)]
    matching = [row for row in updated_rows if str(row.get("cert_id", "")).strip() == cert_id]
    if not matching:
        return {"status": "fail", "message": "issued certificate missing after collapse"}
    status_token = str(dict(matching[-1].get("extensions") or {}).get("status", "")).strip().lower()
    if status_token != "revoked":
        return {"status": "fail", "message": "certificate not marked revoked after collapse"}

    revocation_rows = [dict(row) for row in list(state.get("system_certificate_revocation_rows") or []) if isinstance(row, dict)]
    if not any(str(row.get("cert_id", "")).strip() == cert_id for row in revocation_rows):
        return {"status": "fail", "message": "certificate revocation row missing after collapse"}
    if not str(state.get("system_certificate_revocation_hash_chain", "")).strip():
        return {"status": "fail", "message": "revocation hash chain not updated after modification"}
    return {"status": "pass", "message": "certificate invalidation on system modification is deterministic"}

