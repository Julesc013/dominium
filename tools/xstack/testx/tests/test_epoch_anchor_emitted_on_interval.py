"""FAST test: epoch anchors emit at the canonical interval."""

from __future__ import annotations


TEST_ID = "test_epoch_anchor_emitted_on_interval"
TEST_TAGS = ["fast", "time", "anchor", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.time_anchor_testlib import load_verify_report

    report, error = load_verify_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    checks = dict(report.get("checks") or {})
    if not bool(checks.get("interval_anchor_emitted", False)):
        return {"status": "fail", "message": "interval anchor emission check failed"}
    if not bool(checks.get("non_interval_anchor_skipped", False)):
        return {"status": "fail", "message": "non-interval anchor skip check failed"}
    interval_anchor = dict(report.get("interval_anchor") or {})
    if not str(interval_anchor.get("anchor_id", "")).strip():
        return {"status": "fail", "message": "interval anchor id missing from verify report"}
    return {"status": "pass", "message": "epoch anchors emit deterministically at the canonical interval"}
