"""FAST test: EARTH-1 flow direction remains deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_flow_direction_deterministic"
TEST_TAGS = ["fast", "earth", "hydrology", "determinism", "worldgen"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth1_testlib import verify_hydrology_window_replay_report

    report = verify_hydrology_window_replay_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-1 hydrology window replay drifted across repeated runs"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-1 hydrology window replay reported instability"}
    if not str(report.get("window_hash", "")).strip():
        return {"status": "fail", "message": "EARTH-1 hydrology window replay omitted window_hash"}
    return {"status": "pass", "message": "EARTH-1 flow direction deterministic for identical inputs"}
