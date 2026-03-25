"""FAST test: XI-1 duplicate implementation scan matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_duplicate_scan_deterministic"
TEST_TAGS = ["fast", "xi", "duplicates", "architecture"]


def run(repo_root: str):
    from tools.xstack.testx.tests.duplicate_impl_scan_testlib import committed_duplicate_impls, fresh_snapshot

    committed = committed_duplicate_impls(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("duplicate_impls") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-1 duplicate implementation scan fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "XI-1 duplicate implementation scan is deterministic"}
