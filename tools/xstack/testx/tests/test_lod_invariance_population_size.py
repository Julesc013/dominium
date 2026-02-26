"""STRICT test: cohort expansion does not leak exact hidden population size."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.lod_invariance_population_size"
TEST_TAGS = ["strict", "civilisation", "epistemics", "lod", "demography"]


def _observe_population(state: dict):
    from tools.xstack.sessionx.observation import observe_truth

    truth = {
        "universe_state": dict(state),
    }
    lens = {
        "lens_id": "lens.test.demography",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": ["ch.core.time", "ch.camera.state", "ch.diegetic.map_local"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited"},
    }
    law = {
        "law_profile_id": "law.test.demography",
        "allowed_lenses": ["lens.test.demography"],
        "epistemic_limits": {"max_view_radius_km": 1000000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "tool",
        "peer_id": "peer.test.demography",
        "experience_id": "profile.test.demography",
        "law_profile_id": "law.test.demography",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.test.demography", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.test.demography",
        "allowed_observation_channels": ["ch.core.time", "ch.camera.state", "ch.diegetic.map_local"],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": [
            "filter.channel_allow_deny.v1",
            "filter.quantize_precision.v1",
            "filter.interest_cull.v1",
        ],
        "extensions": {},
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "none",
        "deterministic_eviction_rule_id": "evict.none",
        "extensions": {},
    }
    observed = observe_truth(
        truth_model=truth,
        lens=lens,
        law_profile=law,
        authority_context=authority,
        viewpoint_id="view.demography.lod",
        epistemic_policy=epistemic_policy,
        retention_policy=retention_policy,
    )
    if str(observed.get("result", "")) != "complete":
        return {
            "result": "refused",
            "reason_code": str(((observed.get("refusal") or {}).get("reason_code", ""))),
        }
    populations = dict((dict(observed.get("perceived_model") or {})).get("populations") or {})
    entries = [dict(row) for row in list(populations.get("entries") or []) if isinstance(row, dict)]
    if not entries:
        return {"result": "refused", "reason_code": "missing_population_entry"}
    row = entries[0]
    return {
        "result": "complete",
        "estimate": int(row.get("population_estimate", 0) or 0),
        "has_exact": bool("population_exact" in row),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import replay_intent_script
    from tools.xstack.testx.tests.demography_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_cohort,
    )

    state_before = with_cohort(base_state(), "cohort.demo.007", size=347, location_ref="region.alpha")
    before = _observe_population(state_before)
    if str(before.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline observation failed ({})".format(str(before.get("reason_code", "")))}

    expanded = replay_intent_script(
        universe_state=copy.deepcopy(state_before),
        law_profile=law_profile(["process.cohort_expand_to_micro"], births_allowed=True),
        authority_context=authority_context(["entitlement.civ.admin"], privilege_level="operator"),
        intents=[
            {
                "intent_id": "intent.cohort.expand.007",
                "process_id": "process.cohort_expand_to_micro",
                "inputs": {
                    "cohort_id": "cohort.demo.007",
                    "interest_region_id": "region.alpha",
                    "max_micro_agents": 8,
                },
            }
        ],
        navigation_indices={},
        policy_context=policy_context(parameter_bundle_id="params.civ.basic_births"),
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "cohort expansion failed before LOD invariance check"}

    state_after = dict(expanded.get("universe_state") or {})
    after = _observe_population(state_after)
    if str(after.get("result", "")) != "complete":
        return {"status": "fail", "message": "post-expand observation failed ({})".format(str(after.get("reason_code", "")))}

    if int(before.get("estimate", -1) or -1) != int(after.get("estimate", -2) or -2):
        return {"status": "fail", "message": "population estimate changed due to expansion-only LOD transition"}
    if bool(before.get("has_exact", False)) or bool(after.get("has_exact", False)):
        return {"status": "fail", "message": "non-entitled observer should not receive population_exact before/after expansion"}
    return {"status": "pass", "message": "LOD population-size invariance passed"}
