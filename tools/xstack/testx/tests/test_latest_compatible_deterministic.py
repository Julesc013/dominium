"""FAST test: latest-compatible update simulation remains deterministic."""

from __future__ import annotations


TEST_ID = "test_latest_compatible_deterministic"
TEST_TAGS = ["fast", "release", "update", "omega"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_sim_testlib import build_report

    report = build_report(repo_root, suffix="latest_compatible_deterministic")
    scenario = dict(report.get("latest_compatible_upgrade") or {})
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "update simulation report must complete"}
    if str(scenario.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "latest-compatible scenario must complete"}
    if not bool(scenario.get("deterministic_replay_match")):
        return {"status": "fail", "message": "latest-compatible scenario drifted across identical reruns"}
    if str(scenario.get("selected_client_version", "")).strip() != "0.0.1":
        return {"status": "fail", "message": "latest-compatible scenario did not select the expected client version"}
    return {"status": "pass", "message": "latest-compatible update simulation is deterministic"}
