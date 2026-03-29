from __future__ import annotations

from tools.xstack.testx.tests.xi6_testlib import synthetic_drift_report

TEST_ID = "test_arch_drift_detected_without_tag"
TEST_TAGS = ["fast", "xi6", "architecture"]


def run(repo_root: str):
    report = synthetic_drift_report(repo_root)
    if str(report.get("status", "")).strip().lower() != "fail":
        return {"status": "fail", "message": "synthetic architecture drift was not detected"}
    return {"status": "pass", "message": "architecture drift requires ARCH-GRAPH-UPDATE"}
