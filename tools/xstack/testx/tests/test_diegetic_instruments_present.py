"""STRICT test: diegetic instrument channels are exposed only when policy/lens allow them."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.diegetic_instruments_present"
TEST_TAGS = ["strict", "net", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = {
        "universe_state": {
            "simulation_time": {"tick": 5},
            "agent_states": [{"entity_id": "entity.alpha"}],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 0, "y": 0, "z": 1200},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.diegetic.sensor",
                }
            ],
            "instrument_assemblies": [
                {"assembly_id": "instrument.compass", "reading": {"heading_mdeg": 90000}, "quality": "nominal", "last_update_tick": 5},
                {"assembly_id": "instrument.clock", "reading": {"tick": 5}, "quality": "nominal", "last_update_tick": 5},
                {"assembly_id": "instrument.altimeter", "reading": {"height_mm": 1200}, "quality": "nominal", "last_update_tick": 5},
                {"assembly_id": "instrument.radio", "reading": {"signal": "clear"}, "quality": "nominal", "last_update_tick": 5},
            ],
        }
    }
    lens = {
        "lens_id": "lens.diegetic.sensor",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
            "ch.diegetic.altimeter",
            "ch.diegetic.radio",
        ],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.test.diegetic",
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.test.player",
        "law_profile_id": "law.test.diegetic",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.player", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "none",
        "deterministic_eviction_rule_id": "evict.none",
        "extensions": {},
    }

    player_policy = {
        "epistemic_policy_id": "ep.policy.player_diegetic",
        "allowed_observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
            "ch.diegetic.altimeter",
            "ch.diegetic.radio",
        ],
        "forbidden_channels": [
            "ch.nondiegetic.nav",
            "ch.truth.overlay.terrain_height",
        ],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1"],
        "extensions": {},
    }
    observed = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.player",
        epistemic_policy=copy.deepcopy(player_policy),
        retention_policy=copy.deepcopy(retention_policy),
    )
    if str(observed.get("result", "")) != "complete":
        return {"status": "fail", "message": "player diegetic observation unexpectedly refused"}
    instruments = dict((dict(observed.get("perceived_model") or {}).get("diegetic_instruments") or {}))
    compass = dict(instruments.get("instrument.compass") or {})
    if "reading" not in compass:
        return {"status": "fail", "message": "diegetic compass reading missing under player diegetic policy"}

    spectator_policy = {
        "epistemic_policy_id": "ep.policy.spectator_limited",
        "allowed_observation_channels": ["ch.core.time", "ch.camera.state"],
        "forbidden_channels": ["ch.diegetic.compass", "ch.diegetic.clock", "ch.diegetic.altimeter", "ch.diegetic.radio"],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1"],
        "extensions": {},
    }
    restricted = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.spectator",
        epistemic_policy=copy.deepcopy(spectator_policy),
        retention_policy=copy.deepcopy(retention_policy),
    )
    if str(restricted.get("result", "")) != "refused":
        return {"status": "fail", "message": "spectator policy should refuse diegetic lens channels when forbidden"}
    reason_code = str((dict(restricted.get("refusal") or {}).get("reason_code", "")))
    if reason_code != "refusal.ep.channel_forbidden":
        return {"status": "fail", "message": "unexpected spectator diegetic refusal code '{}'".format(reason_code)}
    return {"status": "pass", "message": "diegetic instrument channels are policy-gated deterministically"}

