"""FAST test: deterministic threshold crossing emits stable failure events."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.failure_trigger_threshold_deterministic"
TEST_TAGS = ["fast", "materials", "maintenance", "determinism"]


def _run_once() -> dict:
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
        asset_id="asset.health.threshold",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=0,
        wear_by_mode={"failure.wear.general": 0},
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.decay.threshold.001",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 2},
        },
        law_profile=law_profile(["process.decay_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices={},
        policy_context=policy_context(failure_threshold_raw=6_000, failure_base_rate_raw=4_000),
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
        return {"status": "fail", "message": "threshold crossing fixture must complete"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "failure threshold crossing state hash diverged"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "failure threshold crossing mutated state non-deterministically"}

    failure_rows = sorted(
        (dict(row) for row in list(first_state.get("failure_events") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("event_id", "")),
    )
    if len(failure_rows) != 1:
        return {"status": "fail", "message": "deterministic threshold crossing should emit exactly one failure event"}
    failure_row = dict(failure_rows[0])
    if str(failure_row.get("failure_mode_id", "")).strip() != "failure.wear.general":
        return {"status": "fail", "message": "failure event mode id mismatch"}
    if int(failure_row.get("severity", 0) or 0) < 1:
        return {"status": "fail", "message": "failure event severity must be >= 1"}
    if not str(failure_row.get("provenance_event_id", "")).strip():
        return {"status": "fail", "message": "failure event must link provenance_event_id"}

    asset_rows = sorted(
        (dict(row) for row in list(first_state.get("asset_health_states") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("asset_id", "")),
    )
    if not asset_rows:
        return {"status": "fail", "message": "asset health rows missing after threshold crossing"}
    failed_mode_ids = set(
        str(item).strip()
        for item in list((dict(asset_rows[0].get("hazard_state") or {})).get("failed_mode_ids") or [])
        if str(item).strip()
    )
    if "failure.wear.general" not in failed_mode_ids:
        return {"status": "fail", "message": "threshold crossing must mark failed_mode_ids"}
    return {"status": "pass", "message": "failure threshold crossing determinism passed"}

