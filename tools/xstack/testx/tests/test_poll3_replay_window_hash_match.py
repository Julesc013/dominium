"""FAST test: POLL-3 replay window verifier reports stable hash matches."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_poll3_replay_window_hash_match"
TEST_TAGS = ["fast", "pollution", "poll3", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.pollution.tool_replay_poll_window import verify_poll_replay_window
    from tools.xstack.testx.tests.poll3_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=9301)
    report = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        budget_envelope_id="poll.envelope.standard",
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "POLL-3 stress run failed for replay fixture"}

    replay = verify_poll_replay_window(
        state_payload=copy.deepcopy(report),
        expected_payload=copy.deepcopy(report),
    )
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "POLL-3 replay window verifier returned violation"}
    if list(replay.get("violations") or []):
        return {"status": "fail", "message": "POLL-3 replay window verifier produced non-empty violations"}
    return {"status": "pass", "message": "POLL-3 replay window hash verification stable"}

