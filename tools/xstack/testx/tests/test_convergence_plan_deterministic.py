"""FAST test: XI-3 convergence planning matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_convergence_plan_deterministic"
TEST_TAGS = ["fast", "xi", "duplicates", "convergence"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_plan_testlib import committed_convergence_plan, fresh_snapshot

    committed = committed_convergence_plan(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("convergence_plan") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-3 convergence plan fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "XI-3 convergence plan is deterministic"}
