"""FAST test: signal processing budget degradation is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.signal.budget_degrade_deterministic"
TEST_TAGS = ["fast", "mobility", "signal", "budget", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_signal_testlib import authority_context, law_profile, policy_context, seed_signal_state

    state = seed_signal_state(signal_count=3, initial_aspect="clear", initial_velocity=0)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.tick.budget.001",
            "process_id": "process.signal_tick",
            "inputs": {"max_signal_updates_per_tick": 1},
        },
        law_profile=copy.deepcopy(law_profile(["process.signal_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "signal budget fixture failed"}
    if str(first_result.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome for max_signal_updates_per_tick=1"}
    keys = ("processed_signal_ids", "deferred_signal_ids", "budget_outcome", "cost_units")
    for key in keys:
        if first_result.get(key) != second_result.get(key):
            return {"status": "fail", "message": "signal budget field '{}' drifted across runs".format(key)}
    deferred = list(first_result.get("deferred_signal_ids") or [])
    if deferred != ["signal.mob.test.02", "signal.mob.test.03"]:
        return {"status": "fail", "message": "expected deterministic deferred signal ordering by signal_id"}
    return {"status": "pass", "message": "signal budget degradation deterministic and stable"}

