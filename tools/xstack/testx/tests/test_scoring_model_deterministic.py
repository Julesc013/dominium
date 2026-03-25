"""FAST test: XI-2 implementation scoring matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_scoring_model_deterministic"
TEST_TAGS = ["fast", "xi", "duplicates", "scoring"]


def run(repo_root: str):
    from tools.xstack.testx.tests.implementation_scoring_testlib import committed_implementation_scores, fresh_snapshot

    committed = committed_implementation_scores(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("implementation_scores") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-2 implementation scoring fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "XI-2 implementation scoring is deterministic"}
