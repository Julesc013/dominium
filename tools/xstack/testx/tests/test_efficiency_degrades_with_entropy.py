"""FAST test: maintenance degradation effects derive from entropy policy outputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_efficiency_degrades_with_entropy"
TEST_TAGS = ["fast", "physics", "entropy", "maintenance", "effects"]


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
        asset_id="asset.health.entropy.effect",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=12_000,
        wear_by_mode={"failure.wear.general": 20_000},
    )
    law = law_profile(["process.decay_tick"])
    authority = authority_context(["session.boot"], privilege_level="observer")
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.default"

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.entropy.effect.decay",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "decay_tick refused: {}".format(result)}

    effect_rows = [
        dict(row)
        for row in list(state.get("effect_rows") or [])
        if isinstance(row, dict)
        and str(row.get("effect_type_id", "")).strip() == "effect.machine_degraded"
        and str((dict(row.get("extensions") or {})).get("effect_auto_key", "")).strip() == "maintenance_degradation"
        and str((dict(row.get("extensions") or {})).get("asset_id", "")).strip() == "asset.health.entropy.effect"
    ]
    if not effect_rows:
        return {"status": "fail", "message": "maintenance_degradation effect row missing"}
    effect_row = sorted(effect_rows, key=lambda row: str(row.get("effect_id", "")))[0]
    output_permille = int(max(0, int((dict(effect_row.get("magnitude") or {})).get("machine_output_permille", 1000) or 1000)))
    if output_permille >= 1000:
        return {"status": "fail", "message": "machine output should degrade below 1000 permille"}

    entropy_effect_rows = [
        dict(row)
        for row in list(state.get("entropy_effect_rows") or [])
        if isinstance(row, dict) and str(row.get("target_id", "")).strip() == "asset.health.entropy.effect"
    ]
    if not entropy_effect_rows:
        return {"status": "fail", "message": "entropy_effect_rows missing asset target"}
    entropy_effect_row = dict(entropy_effect_rows[0])
    efficiency_permille = int(max(0, int(entropy_effect_row.get("efficiency_multiplier_permille", 1000) or 1000)))
    if efficiency_permille != output_permille:
        return {
            "status": "fail",
            "message": "machine_output_permille should match entropy efficiency multiplier ({}, {})".format(
                output_permille,
                efficiency_permille,
            ),
        }
    return {"status": "pass", "message": "entropy-driven efficiency degradation verified"}
