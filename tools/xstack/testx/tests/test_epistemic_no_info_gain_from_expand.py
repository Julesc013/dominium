"""STRICT test: cohort expansion does not leak additional non-entitled epistemic data."""

from __future__ import annotations

import copy
import json
import sys


TEST_ID = "testx.civilisation.epistemic_no_info_gain_from_expand"
TEST_TAGS = ["strict", "civilisation", "cohort", "epistemics", "determinism"]


def _observer_lens() -> dict:
    return {
        "lens_id": "lens.diegetic.sensor",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
            "ch.diegetic.map_local",
        ],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }


def _epistemic_policy() -> dict:
    return {
        "epistemic_policy_id": "ep.policy.player_diegetic",
        "description": "test policy: diegetic channels only",
        "allowed_observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
            "ch.diegetic.map_local",
        ],
        "forbidden_channels": [
            "ch.core.entities",
            "ch.nondiegetic.entity_inspector",
            "ch.truth.overlay.terrain_height",
            "ch.truth.overlay.anchor_hash",
        ],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": [
            "filter.channel_allow_deny.v1",
            "filter.quantize_precision.v1",
            "filter.interest_cull.v1",
            "filter.lod_epistemic_redaction.v1",
        ],
        "extensions": {},
    }


def _retention_policy() -> dict:
    return {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "ep.decay.none",
        "eviction_rule_id": "evict.none",
        "deterministic_eviction_rule_id": "evict.none",
        "extensions": {},
    }


def _observe(state: dict, law_profile: dict, authority_context: dict):
    from tools.xstack.sessionx.observation import observe_truth

    return observe_truth(
        truth_model={
            "schema_version": "1.0.0",
            "universe_state": copy.deepcopy(state),
            "registry_payloads": {},
        },
        lens=_observer_lens(),
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(authority_context),
        viewpoint_id="viewpoint.cohort.noinfo",
        epistemic_policy=_epistemic_policy(),
        retention_policy=_retention_policy(),
    )


def _normalize_perceived(perceived: dict) -> dict:
    payload = dict(perceived or {})
    instruments = dict(payload.get("diegetic_instruments") or {})
    map_local = dict(instruments.get("instrument.map_local") or {})
    map_local_outputs = dict(map_local.get("outputs") or {}).get("ch.diegetic.map_local")
    if not isinstance(map_local_outputs, dict):
        map_local_outputs = {}
    return {
        "channels": sorted(str(item).strip() for item in list(payload.get("channels") or []) if str(item).strip()),
        "entities": dict(payload.get("entities") or {}),
        "observed_entities": list(payload.get("observed_entities") or []),
        "map_local": dict(map_local_outputs),
        "navigation": dict(payload.get("navigation") or {}),
        "truth_overlay": dict(payload.get("truth_overlay") or {}),
    }


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import authority_context, base_state, law_profile, mapping_policy_registry

    state = copy.deepcopy(base_state())
    state["cohort_assemblies"] = [
        {
            "cohort_id": "cohort.ep.noinfo.001",
            "size": 6,
            "faction_id": None,
            "territory_id": None,
            "location_ref": "region.earth",
            "demographic_tags": {},
            "skill_distribution": {},
            "refinement_state": "macro",
            "created_tick": 0,
            "extensions": {"mapping_policy_id": "cohort.map.rank_strict"},
        }
    ]

    observer_law = law_profile([])
    observer_authority = authority_context(["session.boot"], privilege_level="observer")
    before = _observe(
        state=state,
        law_profile=observer_law,
        authority_context=observer_authority,
    )
    if str(before.get("result", "")) != "complete":
        return {"result": "refused", "message": "pre-expansion observation refused"}

    expanded = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.cohort.expand.epistemic.001",
            "process_id": "process.cohort_expand_to_micro",
            "inputs": {
                "cohort_id": "cohort.ep.noinfo.001",
                "interest_region_id": "region.earth",
                "max_micro_agents": 4,
            },
        },
        law_profile=law_profile(["process.cohort_expand_to_micro"]),
        authority_context=authority_context(["entitlement.civ.admin"]),
        navigation_indices={},
        policy_context={
            "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=8),
            "pack_lock_hash": "e" * 64,
        },
    )
    if str(expanded.get("result", "")) != "complete":
        return expanded

    after = _observe(
        state=state,
        law_profile=observer_law,
        authority_context=observer_authority,
    )
    if str(after.get("result", "")) != "complete":
        return {"result": "refused", "message": "post-expansion observation refused"}

    before_perceived = dict(before.get("perceived_model") or {})
    after_perceived = dict(after.get("perceived_model") or {})
    serialized_after = json.dumps(after_perceived, sort_keys=True, separators=(",", ":")).lower()
    return {
        "result": "complete",
        "before_norm": _normalize_perceived(before_perceived),
        "after_norm": _normalize_perceived(after_perceived),
        "before_hash": str(before.get("perceived_model_hash", "")),
        "after_hash": str(after.get("perceived_model_hash", "")),
        "serialized_after": serialized_after,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "epistemic no-info-gain run failed to complete"}

    if dict(first.get("before_norm") or {}) != dict(first.get("after_norm") or {}):
        return {"status": "fail", "message": "cohort expansion changed non-time diegetic perceived payload for non-entitled observer"}
    if dict(second.get("before_norm") or {}) != dict(second.get("after_norm") or {}):
        return {"status": "fail", "message": "cohort expansion changed non-time diegetic perceived payload on repeated run"}
    if dict(first.get("after_norm") or {}) != dict(second.get("after_norm") or {}):
        return {"status": "fail", "message": "post-expansion perceived payload diverged across repeated runs"}

    serialized_after = str(first.get("serialized_after", ""))
    forbidden_tokens = (
        "parent_cohort_id",
        "cohort.ep.noinfo.001",
        "identity_exposure",
        "anonymous_micro_agents",
    )
    for token in forbidden_tokens:
        if token in serialized_after:
            return {"status": "fail", "message": "post-expansion perceived payload leaked forbidden cohort token '{}'".format(token)}
    return {"status": "pass", "message": "cohort expansion epistemic no-info-gain check passed"}
