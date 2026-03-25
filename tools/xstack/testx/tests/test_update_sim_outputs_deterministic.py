"""FAST test: update simulation outputs remain deterministic across reruns."""

from __future__ import annotations


TEST_ID = "test_update_sim_outputs_deterministic"
TEST_TAGS = ["fast", "release", "update", "omega"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_sim_testlib import committed_baseline, reports_match

    if not reports_match(repo_root, left_suffix="outputs_det_a", right_suffix="outputs_det_b"):
        return {"status": "fail", "message": "update simulation report drifted across identical reruns"}
    baseline = committed_baseline(repo_root)
    if str(baseline.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "committed update simulation baseline must be complete"}
    return {"status": "pass", "message": "update simulation outputs are deterministic"}
