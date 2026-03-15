"""FAST test: gc.none reports candidates without mutating the store."""

from __future__ import annotations


TEST_ID = "test_gc_none_reports_only"
TEST_TAGS = ["fast", "lib", "store", "gc"]


def run(repo_root: str):
    from tools.xstack.testx.tests.store_gc_testlib import gc_none_result

    result = gc_none_result(repo_root)
    report = dict(result.get("gc_report") or {})
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "gc.none did not complete"}
    if list(report.get("deleted_hashes") or []) or list(report.get("quarantined_hashes") or []):
        return {"status": "fail", "message": "gc.none mutated the store"}
    if not list(dict(report.get("extensions") or {}).get("candidate_hashes") or []):
        return {"status": "fail", "message": "gc.none did not report any unreachable candidates from the fixture"}
    return {"status": "pass", "message": "gc.none reports without mutating the store"}
