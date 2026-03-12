"""FAST test: EARTH-10 material proxy replay remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_material_proxy_deterministic"
TEST_TAGS = ["fast", "earth", "material_proxy", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth10_testlib import material_proxy_replay_report

    report = material_proxy_replay_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-10 material proxy replay did not complete"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "EARTH-10 material proxy replay drifted across repeated runs"}
    return {"status": "pass", "message": "EARTH-10 material proxy replay is deterministic"}
