"""STRICT test: cohort migration delay is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.migration_delay_deterministic"
TEST_TAGS = ["strict", "civilisation", "migration", "determinism"]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script
    from tools.xstack.testx.tests.demography_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_cohort,
    )

    state = with_cohort(base_state(), "cohort.demo.005", size=12, location_ref="region.alpha")
    return replay_intent_script(
        universe_state=copy.deepcopy(state),
        law_profile=law_profile(["process.cohort_relocate"], migration_allowed=True),
        authority_context=authority_context(["entitlement.civ.order"], privilege_level="operator"),
        intents=[
            {
                "intent_id": "intent.migration.005",
                "process_id": "process.cohort_relocate",
                "inputs": {
                    "cohort_id": "cohort.demo.005",
                    "destination": "region.beta",
                    "migration_model_id": "demo.migration.banded",
                },
            }
        ],
        navigation_indices={},
        policy_context=policy_context(parameter_bundle_id="params.civ.basic_births"),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "migration replay must complete in both runs"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "migration final hash diverged across deterministic runs"}

    first_state = dict(first.get("universe_state") or {})
    second_state = dict(second.get("universe_state") or {})
    first_rows = [dict(row) for row in list(first_state.get("cohort_assemblies") or []) if isinstance(row, dict)]
    second_rows = [dict(row) for row in list(second_state.get("cohort_assemblies") or []) if isinstance(row, dict)]
    if len(first_rows) != 1 or len(second_rows) != 1:
        return {"status": "fail", "message": "expected one cohort row in migration deterministic test"}
    first_migration = dict((dict(first_rows[0].get("extensions") or {})).get("migration") or {})
    second_migration = dict((dict(second_rows[0].get("extensions") or {})).get("migration") or {})
    first_ticks = int(first_migration.get("travel_ticks", -1) or -1)
    second_ticks = int(second_migration.get("travel_ticks", -1) or -1)
    first_arrival = int(first_migration.get("in_transit_until_tick", -1) or -1)
    second_arrival = int(second_migration.get("in_transit_until_tick", -1) or -1)
    if first_ticks != second_ticks:
        return {"status": "fail", "message": "travel_ticks diverged across deterministic runs"}
    if first_arrival != second_arrival:
        return {"status": "fail", "message": "arrival tick diverged across deterministic runs"}
    if first_ticks < 0:
        return {"status": "fail", "message": "travel_ticks must be non-negative"}
    return {"status": "pass", "message": "migration delay deterministic baseline passed"}
