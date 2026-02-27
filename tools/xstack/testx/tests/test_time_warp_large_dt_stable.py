"""FAST test: large dt decay integration remains deterministic and stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.time_warp_large_dt_stable"
TEST_TAGS = ["fast", "materials", "maintenance", "time_warp", "determinism"]


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
        asset_id="asset.health.timewarp",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=0,
        wear_by_mode={"failure.wear.general": 0},
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.decay.timewarp.001",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 50_000},
        },
        law_profile=law_profile(["process.decay_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices={},
        policy_context=policy_context(failure_threshold_raw=1_000_000_000, failure_base_rate_raw=8_000),
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
        return {"status": "fail", "message": "large dt decay tick should complete"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "large dt decay state hash diverged"}
    if str(first_result.get("ledger_hash", "")) != str(second_result.get("ledger_hash", "")):
        return {"status": "fail", "message": "large dt decay ledger hash diverged"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "large dt decay mutated state non-deterministically"}

    rows = sorted(
        (dict(row) for row in list(first_state.get("asset_health_states") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("asset_id", "")),
    )
    if not rows:
        return {"status": "fail", "message": "asset health row missing after large dt decay"}
    row = dict(rows[0])
    wear_raw = int((dict(row.get("accumulated_wear") or {})).get("failure.wear.general", 0) or 0)
    backlog_raw = int(row.get("maintenance_backlog", 0) or 0)
    if wear_raw <= 0 or backlog_raw <= 0:
        return {"status": "fail", "message": "large dt decay should increase wear/backlog deterministically"}
    if wear_raw < backlog_raw:
        return {"status": "fail", "message": "large dt decay produced unstable wear/backlog relationship"}
    return {"status": "pass", "message": "large dt time-warp decay stability passed"}

