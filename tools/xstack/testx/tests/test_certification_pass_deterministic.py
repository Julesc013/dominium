"""FAST test: SYS-5 certification pass path is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_certification_pass_deterministic"
TEST_TAGS = ["fast", "system", "sys5", "certification", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys5_testlib import base_state, execute_system_certification

    state_a = base_state(compliance_grade="pass")
    state_b = copy.deepcopy(state_a)
    result_a = execute_system_certification(repo_root=repo_root, state=state_a)
    result_b = execute_system_certification(repo_root=repo_root, state=state_b)
    if str(result_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first SYS-5 certification run failed"}
    if str(result_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second SYS-5 certification run failed"}

    row_a = dict((state_a.get("system_certification_result_rows") or [{}])[-1] or {})
    row_b = dict((state_b.get("system_certification_result_rows") or [{}])[-1] or {})
    if not bool(row_a.get("pass", False)) or not bool(row_b.get("pass", False)):
        return {"status": "fail", "message": "certification pass path did not pass deterministically"}

    cert_a = dict((state_a.get("system_certificate_artifact_rows") or [{}])[-1] or {})
    cert_b = dict((state_b.get("system_certificate_artifact_rows") or [{}])[-1] or {})
    if str(cert_a.get("cert_id", "")).strip() != str(cert_b.get("cert_id", "")).strip():
        return {"status": "fail", "message": "issued cert_id diverged across equivalent certification runs"}

    for key in (
        "system_certification_result_hash_chain",
        "system_certificate_artifact_hash_chain",
        "system_certificate_revocation_hash_chain",
    ):
        if str(state_a.get(key, "")).strip() != str(state_b.get(key, "")).strip():
            return {"status": "fail", "message": "hash chain '{}' diverged across equivalent certification runs".format(key)}
    return {"status": "pass", "message": "SYS-5 certification pass path is deterministic"}

