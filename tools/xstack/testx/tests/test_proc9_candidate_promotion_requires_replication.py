"""FAST test: candidate promotion remains replication-gated under PROC envelope."""

from __future__ import annotations

import sys


TEST_ID = "test_candidate_promotion_requires_replication_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "research", "promotion"]


def _refusal_reason(result: dict) -> str:
    if not isinstance(result, dict):
        return ""
    top = str(result.get("reason_code", "")).strip()
    if top:
        return top
    refusal = dict(result.get("refusal") or {})
    return str(refusal.get("reason_code", "")).strip()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc7_testlib

    state = proc7_testlib.cloned_state(
        repo_root=repo_root,
        process_id="proc.test.proc9.promotion",
        version="1.0.0",
        experiment_id="experiment.proc9.promotion",
    )
    proc7_testlib.seed_candidate_for_promotion(
        repo_root=repo_root,
        state=state,
        candidate_id="candidate.proc9.replication_gate",
        process_id="proc.test.proc9.promotion",
        replications=1,
    )
    result = proc7_testlib.execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.candidate_promote_to_defined",
        inputs={"candidate_id": "candidate.proc9.replication_gate"},
        policy_context=proc7_testlib.disallow_destructive_policy_context(),
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "promotion should refuse when replication threshold is not met"}
    code = _refusal_reason(result)
    if code != "refusal.process.candidate.promotion_denied":
        return {"status": "fail", "message": "unexpected refusal code: {}".format(code)}
    return {"status": "pass", "message": "candidate promotion requires replication"}
