"""FAST test: CHEM-3 degradation replay hashes are stable across equivalent runs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_cross_platform_hash_match_degradation"
TEST_TAGS = ["fast", "chem", "degradation", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.chem_degradation_testlib import execute_process, seed_degradation_state

    state = seed_degradation_state()
    degrade = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.degradation_tick",
        inputs={
            "target_id": "edge.fluid.hash",
            "profile_id": "profile.tank_basic",
            "target_kind": "edge",
            "parameters": {
                "mass_flow": 860,
                "temperature": 38115,
                "hardness_tag": "hard_scale",
                "entropy_value": 240,
            },
        },
    )
    return {"state": dict(state), "result": dict(degrade)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.chem.tool_replay_degradation_window import verify_degradation_window

    first = _run_once(repo_root)
    second = _run_once(repo_root)
    for label, payload in (("first", first), ("second", second)):
        if str((dict(payload.get("result") or {}).get("result", "")).strip()) != "complete":
            return {"status": "fail", "message": "{} degradation_tick failed".format(label)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    report = verify_degradation_window(state_payload=first_state, expected_payload=second_state)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "degradation replay verifier reported violations: {}".format(report.get("violations", []))}

    for key in ("degradation_hash_chain", "degradation_event_hash_chain", "maintenance_action_hash_chain"):
        chain = str((dict(report.get("observed") or {})).get(key, "")).strip().lower()
        if not _HASH64.fullmatch(chain):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "CHEM-3 degradation replay hashes are stable"}
