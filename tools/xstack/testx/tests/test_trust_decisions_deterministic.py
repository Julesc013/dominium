"""FAST test: trust strict decisions remain deterministic across reruns."""

from __future__ import annotations


TEST_ID = "test_trust_decisions_deterministic"
TEST_TAGS = ["fast", "omega", "trust", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.trust_strict_testlib import committed_baseline, reports_match

    if not reports_match(repo_root):
        return {"status": "fail", "message": "trust strict report drifted across identical reruns"}
    baseline = committed_baseline(repo_root)
    if str(baseline.get("result", "")).strip() not in {"", "complete"}:
        return {"status": "fail", "message": "committed trust strict baseline must be complete when present"}
    return {"status": "pass", "message": "trust strict decisions are deterministic"}
