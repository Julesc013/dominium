"""FAST test: XI-2 duplicate cluster rankings match a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_duplicate_cluster_ranking_stable"
TEST_TAGS = ["fast", "xi", "duplicates", "ranking"]


def run(repo_root: str):
    from tools.xstack.testx.tests.implementation_scoring_testlib import committed_duplicate_cluster_rankings, fresh_snapshot

    committed = committed_duplicate_cluster_rankings(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("duplicate_cluster_rankings") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-2 duplicate cluster rankings fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "XI-2 duplicate cluster rankings are deterministic"}
