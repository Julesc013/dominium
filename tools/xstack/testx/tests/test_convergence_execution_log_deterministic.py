"""FAST test: XI-4 convergence execution log matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_convergence_execution_log_deterministic"
TEST_TAGS = ["fast", "xi", "convergence", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_execution_testlib import committed_convergence_execution_log, fresh_snapshot

    committed = committed_convergence_execution_log(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("convergence_execution_log") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4 convergence execution log fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "XI-4 convergence execution log is deterministic"}
