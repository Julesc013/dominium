"""STRICT test: entropy hash chains are deterministic across equivalent runs."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_cross_platform_entropy_hash"
TEST_TAGS = ["strict", "physics", "entropy", "determinism", "cross_platform"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
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
        asset_id="asset.health.entropy.hash",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=9_000,
        wear_by_mode={"failure.wear.general": 16_000},
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
            "intent_id": "intent.entropy.hash.decay",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(decay_result.get("result", "")) != "complete":
        return {"result": dict(decay_result), "state": dict(state)}

    maintenance_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.entropy.hash.maint",
            "process_id": "process.maintenance_perform",
            "inputs": {
                "asset_id": "asset.health.entropy.hash",
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
    return {"result": dict(maintenance_result), "state": dict(state)}


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline entropy fixture failed: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "replay entropy fixture failed: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})

    chain_a = str(first_state.get("entropy_hash_chain", "")).strip().lower()
    chain_b = str(second_state.get("entropy_hash_chain", "")).strip().lower()
    reset_chain_a = str(first_state.get("entropy_reset_events_hash_chain", "")).strip().lower()
    reset_chain_b = str(second_state.get("entropy_reset_events_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(chain_a)) or (not _HASH64.fullmatch(chain_b)):
        return {"status": "fail", "message": "entropy_hash_chain missing/invalid"}
    if (not _HASH64.fullmatch(reset_chain_a)) or (not _HASH64.fullmatch(reset_chain_b)):
        return {"status": "fail", "message": "entropy_reset_events_hash_chain missing/invalid"}
    if chain_a != chain_b:
        return {"status": "fail", "message": "entropy_hash_chain drifted across equivalent runs"}
    if reset_chain_a != reset_chain_b:
        return {"status": "fail", "message": "entropy_reset_events_hash_chain drifted across equivalent runs"}

    if list(first_state.get("entropy_event_rows") or []) != list(second_state.get("entropy_event_rows") or []):
        return {"status": "fail", "message": "entropy_event_rows drifted across equivalent runs"}
    if list(first_state.get("entropy_reset_events") or []) != list(second_state.get("entropy_reset_events") or []):
        return {"status": "fail", "message": "entropy_reset_events drifted across equivalent runs"}
    return {"status": "pass", "message": "entropy hash chains are deterministic"}
