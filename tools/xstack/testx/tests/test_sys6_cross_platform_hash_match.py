"""FAST test: SYS-6 replay window hashes match across equivalent runs."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_cross_platform_hash_match_sys6"
TEST_TAGS = ["fast", "system", "sys6", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.sys6_testlib import (
        base_state,
        execute_health_tick,
        execute_reliability_tick,
    )

    state = base_state(
        hazard_levels={
            "hazard.thermal.overheat": 960,
            "hazard.control.loss": 920,
        }
    )
    health = execute_health_tick(repo_root=repo_root, state=state)
    reliability = execute_reliability_tick(repo_root=repo_root, state=state)
    return {"state": dict(state), "health": dict(health), "reliability": dict(reliability)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_replay_system_failure_window import verify_system_failure_replay_window

    first = _run_once(repo_root)
    second = _run_once(repo_root)
    for label, payload in (("first", first), ("second", second)):
        if str(dict(payload.get("health") or {}).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} health tick failed".format(label)}
        if str(dict(payload.get("reliability") or {}).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} reliability tick failed".format(label)}

    first_state = dict(first.get("state") or {})
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    report = verify_system_failure_replay_window(
        state_payload=first_state,
        expected_payload=second_state,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-6 replay verifier reported violations: {}".format(report.get("violations", []))}
    for key in (
        "system_health_hash_chain",
        "system_failure_event_hash_chain",
        "system_forced_expand_event_hash_chain",
        "system_reliability_rng_hash_chain",
    ):
        chain = str((dict(report.get("observed") or {})).get(key, "")).strip().lower()
        if not _HASH64.fullmatch(chain):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "SYS-6 replay hashes are stable across equivalent runs"}

