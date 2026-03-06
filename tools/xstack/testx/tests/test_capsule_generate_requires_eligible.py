"""FAST test: PROC-5 capsule generation requires capsule_eligible maturity."""

from __future__ import annotations

import sys


TEST_ID = "test_capsule_generate_requires_eligible"
TEST_TAGS = ["fast", "proc", "proc5", "capsule", "maturity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc5_testlib import run_proc5_capsule_case

    payload = run_proc5_capsule_case(
        repo_root=repo_root,
        maturity_state="defined",
    )
    generation = dict(payload.get("generation") or {})
    if str(generation.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "capsule generation should refuse when maturity is not capsule_eligible"}
    reason_code = str(generation.get("reason_code", "")).strip()
    if reason_code != "refusal.process.capsule.ineligible":
        return {
            "status": "fail",
            "message": "unexpected refusal code for ineligible capsule generation: {}".format(reason_code),
        }
    return {"status": "pass", "message": "capsule generation correctly requires capsule_eligible maturity"}

