"""FAST test: entropy is monotonic non-decreasing when no reset process is executed."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_entropy_monotonic_without_reset"
TEST_TAGS = ["fast", "physics", "entropy", "maintenance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.maintenance_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_asset_health,
    )

    state = with_asset_health(
        base_state(),
        asset_id="asset.health.entropy.mono",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=6_000,
        wear_by_mode={"failure.wear.general": 14_000},
    )
    law = law_profile(["process.decay_tick"])
    authority = authority_context(["session.boot"], privilege_level="observer")
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.default"

    values = []
    for index in range(3):
        result = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.entropy.mono.{}".format(index + 1),
                "process_id": "process.decay_tick",
                "inputs": {"dt_ticks": 1},
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "decay_tick refused during monotonicity check: {}".format(result)}
        rows = [
            dict(row)
            for row in list(state.get("entropy_state_rows") or [])
            if isinstance(row, dict) and str(row.get("target_id", "")).strip() == "asset.health.entropy.mono"
        ]
        if not rows:
            return {"status": "fail", "message": "entropy_state_rows missing target after decay tick"}
        values.append(int(max(0, int(rows[0].get("entropy_value", 0) or 0))))

    if values[1] < values[0] or values[2] < values[1]:
        return {"status": "fail", "message": "entropy values must be monotonic without reset: {}".format(values)}
    reset_rows = [dict(row) for row in list(state.get("entropy_reset_events") or []) if isinstance(row, dict)]
    if reset_rows:
        return {"status": "fail", "message": "entropy_reset_events should be empty in monotonicity test"}
    return {"status": "pass", "message": "entropy monotonicity without reset verified"}
