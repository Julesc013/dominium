"""FAST test: PROC-5 out-of-domain capsule execution forces deterministic expand."""

from __future__ import annotations

import sys


TEST_ID = "test_capsule_out_of_domain_forces_expand"
TEST_TAGS = ["fast", "proc", "proc5", "capsule", "forced_expand"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc5_testlib import run_proc5_capsule_case

    payload = run_proc5_capsule_case(
        repo_root=repo_root,
        out_of_domain=True,
    )
    generation = dict(payload.get("generation") or {})
    execution = dict(payload.get("execution") or {})
    if str(generation.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "capsule generation failed before out-of-domain execution"}
    if str(execution.get("result", "")).strip() != "forced_expand":
        return {"status": "fail", "message": "out-of-domain execution should force expand"}
    if str(execution.get("reason_code", "")).strip() != "refusal.process.capsule.out_of_domain":
        return {"status": "fail", "message": "forced-expand reason code mismatch"}
    forced_row = dict(execution.get("forced_expand_event_row") or {})
    if str(forced_row.get("reason_code", "")).strip() != "refusal.process.capsule.out_of_domain":
        return {"status": "fail", "message": "forced expand event missing out-of-domain reason code"}
    return {"status": "pass", "message": "out-of-domain capsule execution forces deterministic expand"}

