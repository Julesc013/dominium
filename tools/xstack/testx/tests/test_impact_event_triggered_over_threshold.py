"""FAST test: EMB-2 impact events are emitted above the deterministic threshold."""

from __future__ import annotations

import sys


TEST_ID = "test_impact_event_triggered_over_threshold"
TEST_TAGS = ["fast", "embodiment", "locomotion", "impact"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.emb2_testlib import impact_event_report

    report = impact_event_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EMB-2 impact probe did not complete"}
    if not str(report.get("impact_event_id", "")).strip():
        return {"status": "fail", "message": "EMB-2 impact event id missing"}
    if int(report.get("impact_speed", 0) or 0) <= 0:
        return {"status": "fail", "message": "EMB-2 impact speed should be positive"}
    if str(report.get("impact_explain_id", "")).strip() != "explain.impact_event":
        return {"status": "fail", "message": "EMB-2 impact explain hook missing"}
    return {"status": "pass", "message": "EMB-2 impact event emitted deterministically"}
