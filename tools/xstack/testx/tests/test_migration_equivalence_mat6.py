"""FAST test: MAT-6 hazard/schedule/state migration preserves observable behavior."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.migration_equivalence_mat6"
TEST_TAGS = ["fast", "materials", "maintenance", "migration"]


def _run_fixture() -> dict:
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
        asset_id="asset.health.migration.alpha",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=0,
        wear_by_mode={"failure.wear.general": 0},
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.decay.migration.001",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 12},
        },
        law_profile=law_profile(["process.decay_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices={},
        policy_context=policy_context(failure_threshold_raw=100_000, failure_base_rate_raw=2_000),
    )
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_fixture()
    second = _run_fixture()

    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "MAT-6 migration fixture must complete"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "MAT-6 migration fixture hash diverged across identical runs"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "MAT-6 migration fixture produced non-deterministic state"}

    rows = sorted(
        (dict(row) for row in list(first_state.get("asset_health_states") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("asset_id", "")),
    )
    if len(rows) != 1:
        return {"status": "fail", "message": "MAT-6 migration fixture expected one asset health row"}
    row = dict(rows[0])
    wear = int((dict(row.get("accumulated_wear") or {})).get("failure.wear.general", 0) or 0)
    backlog = int(row.get("maintenance_backlog", 0) or 0)
    if wear != 24_000:
        return {"status": "fail", "message": "MAT-6 migration changed wear accumulation semantics"}
    if backlog != 1_200:
        return {"status": "fail", "message": "MAT-6 migration changed backlog growth semantics"}

    failure_rows = [dict(item) for item in list(first_state.get("failure_events") or []) if isinstance(item, dict)]
    if failure_rows:
        return {"status": "fail", "message": "MAT-6 migration fixture should not trigger failure below threshold"}

    hazard_state = dict(row.get("hazard_state") or {})
    machine_state = dict(hazard_state.get("state_machine") or {})
    if str(machine_state.get("machine_type_id", "")) != "state_machine.asset_health":
        return {"status": "fail", "message": "MAT-6 migration must populate asset health state machine metadata"}

    return {"status": "pass", "message": "MAT-6 migration equivalence fixture passed"}

