"""STRICT test: player diegetic default observation excludes observer/non-diegetic channels."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.diegetic.player_default_no_observer_channels"
TEST_TAGS = ["strict", "observation", "diegetic"]


def _truth_payload() -> dict:
    return {
        "universe_state": {
            "simulation_time": {"tick": 7},
            "agent_states": [{"entity_id": "entity.alpha"}],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 1000, "y": 2000, "z": 3000},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.diegetic.sensor",
                }
            ],
            "instrument_assemblies": [
                {
                    "assembly_id": "instrument.compass",
                    "instrument_type": "compass",
                    "reading": {"heading_mdeg": 12345},
                    "quality": "nominal",
                    "quality_value": 1000,
                    "last_update_tick": 7,
                    "state": {},
                    "outputs": {"ch.diegetic.compass": {"heading_mdeg": 12345}},
                },
                {
                    "assembly_id": "instrument.clock",
                    "instrument_type": "clock",
                    "reading": {"tick": 7},
                    "quality": "nominal",
                    "quality_value": 1000,
                    "last_update_tick": 7,
                    "state": {},
                    "outputs": {"ch.diegetic.clock": {"tick": 7}},
                },
                {
                    "assembly_id": "instrument.map_local",
                    "instrument_type": "map_local",
                    "reading": {"tiles": []},
                    "quality": "nominal",
                    "quality_value": 1000,
                    "last_update_tick": 7,
                    "state": {"tiles": []},
                    "outputs": {"ch.diegetic.map_local": {"tiles": []}},
                },
            ],
        }
    }


def _lens_payload() -> dict:
    return {
        "lens_id": "lens.diegetic.sensor",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot", "ui.window.lab.nav"],
        "observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
            "ch.diegetic.map_local",
        ],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }


def _law_payload() -> dict:
    return {
        "law_profile_id": "law.player.diegetic_default",
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 50000, "allow_hidden_state_access": False},
    }


def _authority_payload() -> dict:
    return {
        "authority_origin": "client",
        "experience_id": "profile.player.default",
        "law_profile_id": "law.player.diegetic_default",
        "entitlements": ["session.boot", "ui.window.lab.nav"],
        "epistemic_scope": {"scope_id": "scope.player", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }


def _policy_payload() -> dict:
    return {
        "epistemic_policy_id": "ep.policy.player_diegetic",
        "allowed_observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
            "ch.diegetic.map_local",
        ],
        "forbidden_channels": [
            "ch.nondiegetic.nav",
            "ch.nondiegetic.entity_inspector",
            "ch.truth.overlay.terrain_height",
            "ch.truth.overlay.anchor_hash",
        ],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1"],
        "extensions": {},
    }


def _retention_payload() -> dict:
    return {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "ep.decay.none",
        "deterministic_eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    observed = observe_truth(
        truth_model=copy.deepcopy(_truth_payload()),
        lens=copy.deepcopy(_lens_payload()),
        law_profile=copy.deepcopy(_law_payload()),
        authority_context=copy.deepcopy(_authority_payload()),
        viewpoint_id="view.player.diegetic_default",
        epistemic_policy=copy.deepcopy(_policy_payload()),
        retention_policy=copy.deepcopy(_retention_payload()),
    )
    if str(observed.get("result", "")) != "complete":
        return {"status": "fail", "message": "player diegetic observation unexpectedly refused"}

    perceived = dict(observed.get("perceived_model") or {})
    channels = [str(item).strip() for item in list(perceived.get("channels") or []) if str(item).strip()]
    forbidden_prefixes = ("ch.nondiegetic.", "ch.truth.overlay.")
    leaked = sorted(token for token in channels if any(token.startswith(prefix) for prefix in forbidden_prefixes))
    if leaked:
        return {"status": "fail", "message": "player observation leaked forbidden channels: {}".format(",".join(leaked))}

    truth_overlay = dict(perceived.get("truth_overlay") or {})
    nonempty_truth_overlay = [key for key in sorted(truth_overlay.keys()) if truth_overlay.get(key)]
    if nonempty_truth_overlay:
        return {"status": "fail", "message": "player observation leaked truth overlay payloads"}

    return {"status": "pass", "message": "player diegetic observation excludes observer/non-diegetic channels"}
