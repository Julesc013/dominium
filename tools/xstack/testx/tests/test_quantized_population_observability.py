"""STRICT test: population observability is quantized for non-entitled observers."""

from __future__ import annotations

import sys


TEST_ID = "testx.civilisation.quantized_population_observability"
TEST_TAGS = ["strict", "civilisation", "epistemics", "demography"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = {
        "universe_state": {
            "simulation_time": {"tick": 11},
            "agent_states": [],
            "cohort_assemblies": [
                {
                    "cohort_id": "cohort.pop.001",
                    "size": 347,
                    "faction_id": "faction.alpha",
                    "territory_id": None,
                    "location_ref": "region.alpha",
                    "demographic_tags": {},
                    "skill_distribution": {},
                    "refinement_state": "macro",
                    "created_tick": 0,
                    "extensions": {},
                }
            ],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 150000, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.test.demography",
                }
            ],
            "instrument_assemblies": [],
        }
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
        viewpoint_id="view.demography.quantized",
        epistemic_policy=epistemic_policy,
        retention_policy=retention_policy,
    )
    if str(observed.get("result", "")) != "complete":
        return {"status": "fail", "message": "observation refused for quantized population test"}

    populations = dict((dict(observed.get("perceived_model") or {})).get("populations") or {})
    entries = [dict(row) for row in list(populations.get("entries") or []) if isinstance(row, dict)]
    if len(entries) != 1:
        return {"status": "fail", "message": "expected one visible population entry"}
    entry = entries[0]
    estimate = int(entry.get("population_estimate", -1) or -1)
    if estimate != 350:
        return {"status": "fail", "message": "expected quantized population estimate 350, got {}".format(estimate)}
    if "population_exact" in entry:
        return {"status": "fail", "message": "non-entitled observer should not receive population_exact"}
    if str(entry.get("population_band", "")) != "hundreds":
        return {"status": "fail", "message": "expected hundreds population band"}
    return {"status": "pass", "message": "population observability quantization passed"}

