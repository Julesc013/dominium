"""FAST test: MAT-10 stress hash anchors remain stable for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.hash_anchors_stable_under_stress"
TEST_TAGS = ["fast", "materials", "mat10", "stress", "hash"]


def _run_once():
    from tools.xstack.testx.tests.mat_scale_testlib import base_scenario, run_report

    scenario = base_scenario(seed=733, factory_complex_count=14, logistics_node_count=70, active_project_count=50, player_count=36)
    return run_report(scenario=scenario, tick_count=18)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    one = _run_once()
    two = _run_once()
    if list(one.get("hash_anchor_stream") or []) != list(two.get("hash_anchor_stream") or []):
        return {"status": "fail", "message": "hash anchor stream diverged across identical stress runs"}
    if str(one.get("deterministic_fingerprint", "")) != str(two.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "stress deterministic fingerprint diverged"}
    if copy.deepcopy(dict(one)) != copy.deepcopy(dict(two)):
        return {"status": "fail", "message": "stress report payload diverged across identical runs"}
    return {"status": "pass", "message": "hash anchors stable under stress passed"}
