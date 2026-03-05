"""FAST test: SYS-8 replay window verifier reports hash match."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_replay_window_hash_match_sys8"
TEST_TAGS = ["fast", "system", "sys8", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_replay_sys_window import verify_sys_replay_window
    from tools.xstack.testx.tests.sys8_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=88117)
    report = run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-8 stress report did not complete for replay fixture"}

    replay = verify_sys_replay_window(
        state_payload=copy.deepcopy(report),
        expected_payload=copy.deepcopy(report),
    )
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-8 replay verifier returned violation"}
    if list(replay.get("violations") or []):
        return {"status": "fail", "message": "SYS-8 replay verifier produced non-empty violations"}

    return {"status": "pass", "message": "SYS-8 replay window hashes match deterministically"}
