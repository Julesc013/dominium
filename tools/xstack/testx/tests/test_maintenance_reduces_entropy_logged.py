"""FAST test: maintenance reset reduces entropy and emits deterministic reset records."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_maintenance_reduces_entropy_logged"
TEST_TAGS = ["fast", "physics", "entropy", "maintenance", "logging"]


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
        asset_id="asset.health.entropy.reset",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=10_000,
        wear_by_mode={"failure.wear.general": 18_000},
    )
    law = law_profile(["process.decay_tick", "process.maintenance_perform"])
    authority = authority_context(
        ["session.boot", "entitlement.control.admin"],
        privilege_level="operator",
    )
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.default"

    decay_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.entropy.reset.pre.decay",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(decay_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "pre-maintenance decay_tick refused: {}".format(decay_result)}

    before_rows = [
        dict(row)
        for row in list(state.get("entropy_state_rows") or [])
        if isinstance(row, dict) and str(row.get("target_id", "")).strip() == "asset.health.entropy.reset"
    ]
    if not before_rows:
        return {"status": "fail", "message": "entropy state missing before maintenance"}
    entropy_before = int(max(0, int(before_rows[0].get("entropy_value", 0) or 0)))
    if entropy_before <= 0:
        return {"status": "fail", "message": "pre-maintenance entropy should be > 0"}

    maintenance_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.entropy.reset.perform",
            "process_id": "process.maintenance_perform",
            "inputs": {
                "asset_id": "asset.health.entropy.reset",
                "required_materials": {},
                "reset_fraction_numerator": 1,
                "reset_fraction_denominator": 2,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(maintenance_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "maintenance_perform refused: {}".format(maintenance_result)}

    after_rows = [
        dict(row)
        for row in list(state.get("entropy_state_rows") or [])
        if isinstance(row, dict) and str(row.get("target_id", "")).strip() == "asset.health.entropy.reset"
    ]
    if not after_rows:
        return {"status": "fail", "message": "entropy state missing after maintenance"}
    entropy_after = int(max(0, int(after_rows[0].get("entropy_value", 0) or 0)))
    if entropy_after >= entropy_before:
        return {"status": "fail", "message": "maintenance should reduce entropy ({}, {})".format(entropy_before, entropy_after)}

    reset_rows = [
        dict(row)
        for row in list(state.get("entropy_reset_events") or [])
        if isinstance(row, dict) and str(row.get("target_id", "")).strip() == "asset.health.entropy.reset"
    ]
    if not reset_rows:
        return {"status": "fail", "message": "entropy_reset_events missing maintenance reset record"}
    reset_row = sorted(reset_rows, key=lambda row: (int(row.get("tick", 0) or 0), str(row.get("event_id", ""))))[-1]
    if int(max(0, int(reset_row.get("reset_delta", 0) or 0))) <= 0:
        return {"status": "fail", "message": "reset_delta must be positive"}

    artifact_types = sorted(
        set(
            str((dict(row.get("extensions") or {})).get("artifact_type_id", "")).strip()
            for row in list(state.get("info_artifact_rows") or [])
            if isinstance(row, dict)
        )
    )
    if "artifact.entropy_reset_event" not in set(artifact_types):
        return {"status": "fail", "message": "entropy reset artifact was not emitted"}

    return {"status": "pass", "message": "maintenance entropy reset logging verified"}
