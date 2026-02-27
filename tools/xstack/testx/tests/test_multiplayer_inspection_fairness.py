"""FAST test: MAT-9 inspection arbitration enforces deterministic fair-share budget per peer."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.multiplayer_inspection_fairness"
TEST_TAGS = ["fast", "materials", "inspection", "multiplayer", "budget"]


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
        asset_id="asset.health.inspect.fairness",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=1_000,
        wear_by_mode={"failure.wear.general": 1_000},
    )
    law = law_profile(["process.inspect_generate_snapshot"])
    policy = policy_context()
    policy["connected_peer_ids"] = ["peer.alpha", "peer.beta"]
    envelope_rows = list((dict(policy.get("budget_envelope_registry") or {}).get("envelopes") or []))
    if not envelope_rows:
        return {"status": "fail", "message": "budget envelope fixture missing for multiplayer fairness test"}
    envelope_rows[0] = dict(envelope_rows[0])
    envelope_rows[0]["max_inspection_cost_units_per_tick"] = 6
    policy["budget_envelope_registry"] = {"envelopes": envelope_rows}

    authority_alpha = authority_context(["entitlement.inspect"], privilege_level="observer")
    authority_alpha["peer_id"] = "peer.alpha"
    authority_beta = authority_context(["entitlement.inspect"], privilege_level="observer")
    authority_beta["peer_id"] = "peer.beta"

    one = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.fair.alpha.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.fairness", "cost_units": 3},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority_alpha),
        navigation_indices={},
        policy_context=policy,
    )
    two = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.fair.beta.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.fairness", "cost_units": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority_beta),
        navigation_indices={},
        policy_context=policy,
    )
    three = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.fair.alpha.002",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.fairness", "cost_units": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority_alpha),
        navigation_indices={},
        policy_context=policy,
    )

    if str(one.get("result", "")) != "complete" or str(two.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline fair-share inspection requests should succeed"}
    if str(three.get("result", "")) != "refused":
        return {"status": "fail", "message": "peer exceeding deterministic fair-share cap should be refused"}
    reason_code = str(three.get("reason_code", "")).strip() or str((dict(three.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.inspect.budget_exceeded":
        return {"status": "fail", "message": "fair-share refusal should use refusal.inspect.budget_exceeded"}
    return {"status": "pass", "message": "multiplayer inspection fair-share enforcement passed"}
