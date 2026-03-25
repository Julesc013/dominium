"""FAST test: XI-1 src directory report matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_src_report_deterministic"
TEST_TAGS = ["fast", "xi", "duplicates", "src"]


def run(repo_root: str):
    from tools.xstack.testx.tests.duplicate_impl_scan_testlib import committed_src_directory_report, fresh_snapshot

    committed = committed_src_directory_report(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("src_directory_report") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-1 src directory report fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "XI-1 src directory report is deterministic"}
