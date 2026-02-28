"""FAST test: interior portal occlusion filters PerceivedModel deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.interior.occlusion_in_perceived_model"
TEST_TAGS = ["fast", "interior", "epistemic", "occlusion"]


def _authority_context(entitlements: list[str]) -> dict:
    return {
        "authority_origin": "server",
        "experience_id": "exp.test",
        "law_profile_id": "law.test.interior",
        "entitlements": sorted(set(str(item).strip() for item in entitlements if str(item).strip())),
        "epistemic_scope": {
            "scope_id": "scope.test.interior",
            "visibility_level": "diegetic",
            "subject_id": "agent.alpha",
        },
        "privilege_level": "observer",
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.interior",
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.freecam"],
        "epistemic_limits": {
            "allow_hidden_state_access": False,
            "allow_freecam_occlusion_bypass": True,
        },
    }


def _epistemic_policy() -> dict:
    return {
        "epistemic_policy_id": "ep.policy.test.interior",
        "retention_policy_id": "ep.retention.none",
        "allowed_observation_channels": ["ch.core.entities", "ch.camera.state"],
        "forbidden_channels": [],
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": [],
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


def _volume(volume_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "volume_id": volume_id,
        "parent_spatial_id": "spatial.site.occlusion",
        "local_transform": {
            "translation_mm": {"x": 0, "y": 0, "z": 0},
            "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "scale_permille": 1000,
        },
        "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 1000, "y": 1000, "z": 1000}}},
        "volume_type_id": "volume.room",
        "tags": [],
        "extensions": {},
    }


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 10, "tick_dt_sim_ms": 100},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "view_mode_id": "view.mode.default",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "interior_volume_id": "volume.a",
                "extensions": {},
            }
        ],
        "agent_states": [
            {
                "schema_version": "1.0.0",
                "agent_id": "agent.alpha",
                "entity_id": "agent.alpha",
                "body_id": "body.alpha",
                "interior_volume_id": "volume.a",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "agent_id": "agent.beta",
                "entity_id": "agent.beta",
                "body_id": "body.beta",
                "interior_volume_id": "volume.b",
                "extensions": {},
            },
        ],
        "body_assemblies": [
            {"body_id": "body.alpha", "shape_type": "capsule", "transform_mm": {"x": 0, "y": 0, "z": 0}},
            {"body_id": "body.beta", "shape_type": "capsule", "transform_mm": {"x": 0, "y": 0, "z": 0}},
        ],
        "interior_graphs": [
            {
                "schema_version": "1.0.0",
                "graph_id": "interior.graph.occlusion",
                "volumes": ["volume.a", "volume.b"],
                "portals": ["portal.ab"],
                "extensions": {},
            }
        ],
        "interior_volumes": [_volume("volume.a"), _volume("volume.b")],
        "interior_portals": [
            {
                "schema_version": "1.0.0",
                "portal_id": "portal.ab",
                "from_volume_id": "volume.a",
                "to_volume_id": "volume.b",
                "portal_type_id": "portal.door",
                "state_machine_id": "state.portal.ab",
                "sealing_coefficient": 1000,
                "tags": [],
                "extensions": {},
            }
        ],
        "interior_portal_state_machines": [
            {
                "schema_version": "1.0.0",
                "machine_id": "state.portal.ab",
                "machine_type_id": "state_machine.portal",
                "state_id": "closed",
                "transitions": ["transition.portal.closed_to_open", "transition.portal.open_to_closed"],
                "transition_rows": [
                    {
                        "schema_version": "1.0.0",
                        "transition_id": "transition.portal.closed_to_open",
                        "from_state": "closed",
                        "to_state": "open",
                        "trigger_process_id": "process.portal_open",
                        "guard_conditions": {},
                        "priority": 10,
                        "extensions": {},
                    },
                    {
                        "schema_version": "1.0.0",
                        "transition_id": "transition.portal.open_to_closed",
                        "from_state": "open",
                        "to_state": "closed",
                        "trigger_process_id": "process.portal_close",
                        "guard_conditions": {},
                        "priority": 10,
                        "extensions": {},
                    },
                ],
                "extensions": {},
            }
        ],
    }


def _entity_ids(perceived_result: dict) -> list[str]:
    perceived = dict(perceived_result.get("perceived_model") or {})
    entities = list((dict(perceived.get("entities") or {})).get("entries") or [])
    out = []
    for row in entities:
        if not isinstance(row, dict):
            continue
        token = str((dict(row).get("entity_id") or dict(row).get("agent_id") or "")).strip()
        if not token.startswith("agent."):
            continue
        out.append(token)
    return sorted(out)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    state = _state()
    law = _law_profile()

    diegetic = observe_truth(
        truth_model={"schema_version": "1.0.0", "universe_state": state, "registry_payloads": {}},
        lens={
            "lens_id": "lens.diegetic.sensor",
            "lens_type": "diegetic",
            "required_entitlements": [],
            "epistemic_constraints": {"visibility_policy": "diegetic"},
            "observation_channels": ["ch.core.entities", "ch.camera.state"],
        },
        law_profile=law,
        authority_context=_authority_context([]),
        viewpoint_id="viewpoint.test.interior.diegetic",
        epistemic_policy=_epistemic_policy(),
        retention_policy=_retention_policy(),
    )
    if str(diegetic.get("result", "")) != "complete":
        return {"status": "fail", "message": "diegetic observation failed for interior occlusion baseline"}
    if _entity_ids(diegetic) != ["agent.alpha"]:
        return {"status": "fail", "message": "closed portal occlusion should hide non-reachable interior entities"}

    freecam = observe_truth(
        truth_model={"schema_version": "1.0.0", "universe_state": state, "registry_payloads": {}},
        lens={
            "lens_id": "lens.nondiegetic.freecam",
            "lens_type": "nondiegetic",
            "required_entitlements": [],
            "epistemic_constraints": {"visibility_policy": "observer"},
            "observation_channels": ["ch.core.entities", "ch.camera.state"],
        },
        law_profile=law,
        authority_context=_authority_context(["lens.nondiegetic.access"]),
        viewpoint_id="viewpoint.test.interior.freecam",
        epistemic_policy=_epistemic_policy(),
        retention_policy=_retention_policy(),
    )
    if str(freecam.get("result", "")) != "complete":
        return {"status": "fail", "message": "freecam observation failed for interior occlusion bypass baseline"}
    if _entity_ids(freecam) != ["agent.alpha", "agent.beta"]:
        return {"status": "fail", "message": "freecam lens should bypass interior occlusion when law permits"}
    return {"status": "pass", "message": "interior occlusion and freecam bypass behavior passed"}
