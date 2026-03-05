"""FAST test: SYS-5 certification replay window hash verification is stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_replay_cert_hash_match"
TEST_TAGS = ["fast", "system", "sys5", "certification", "proof", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_replay_certification_window import verify_certification_replay_window
    from tools.xstack.testx.tests.sys5_testlib import (
        base_state,
        execute_system_certification,
        execute_system_collapse,
    )

    state = base_state(compliance_grade="pass")
    cert_result = execute_system_certification(repo_root=repo_root, state=state)
    if str(cert_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "certification setup run failed"}
    collapse_result = execute_system_collapse(repo_root=repo_root, state=state, system_id="system.engine.alpha")
    if str(collapse_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "collapse setup run failed"}

    expected = copy.deepcopy(state)
    report = verify_certification_replay_window(
        state_payload=state,
        expected_payload=expected,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "certification replay verifier reported violation: {}".format(report)}
    if list(report.get("violations") or []):
        return {"status": "fail", "message": "certification replay verifier produced non-empty violations"}
    return {"status": "pass", "message": "certification replay window hash verification is stable"}

