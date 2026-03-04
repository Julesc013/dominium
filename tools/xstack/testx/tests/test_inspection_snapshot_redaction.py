"""FAST test: INT-3 interior inspection snapshot redaction is epistemic-safe."""

from __future__ import annotations

import sys


TEST_ID = "testx.interior.inspection_snapshot_redaction"
TEST_TAGS = ["fast", "interior", "inspection", "epistemic"]


def _state() -> dict:
    return {
        "interior_graphs": [
            {
                "schema_version": "1.0.0",
                "graph_id": "interior.graph.test.alpha",
                "volumes": ["volume.a", "volume.b"],
                "portals": ["portal.ab"],
                "extensions": {},
            }
        ],
        "interior_volumes": [
            {
                "schema_version": "1.0.0",
                "volume_id": "volume.a",
                "parent_spatial_id": "spatial.site.alpha",
                "local_transform": {
                    "translation_mm": {"x": 0, "y": 0, "z": 0},
                    "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 1000, "y": 1000, "z": 1000}}},
                "volume_type_id": "volume.room",
                "tags": [],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "volume_id": "volume.b",
                "parent_spatial_id": "spatial.site.alpha",
                "local_transform": {
                    "translation_mm": {"x": 0, "y": 0, "z": 0},
                    "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 1000, "y": 1000, "z": 1000}}},
                "volume_type_id": "volume.room",
                "tags": [],
                "extensions": {},
            },
        ],
        "interior_portals": [
            {
                "schema_version": "1.0.0",
                "portal_id": "portal.ab",
                "from_volume_id": "volume.a",
                "to_volume_id": "volume.b",
                "portal_type_id": "portal.door",
                "state_machine_id": "state.portal.ab",
                "sealing_coefficient": 900,
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
                "transitions": [],
                "extensions": {},
            }
        ],
        "portal_flow_params": [
            {
                "schema_version": "1.0.0",
                "portal_id": "portal.ab",
                "conductance_air": 300,
                "conductance_water": 80,
                "conductance_smoke": 150,
                "sealing_coefficient": 900,
                "open_state_multiplier": 1000,
                "extensions": {},
            }
        ],
        "compartment_states": [
            {
                "schema_version": "1.0.0",
                "volume_id": "volume.a",
                "air_mass": 1200,
                "water_volume": 300,
                "temperature": None,
                "oxygen_fraction": 205,
                "smoke_density": 220,
                "derived_pressure": 1200,
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "volume_id": "volume.b",
                "air_mass": 900,
                "water_volume": 0,
                "temperature": None,
                "oxygen_fraction": 210,
                "smoke_density": 0,
                "derived_pressure": 900,
                "extensions": {},
            },
        ],
        "interior_leak_hazards": [
            {
                "schema_version": "1.0.0",
                "leak_id": "leak.a",
                "volume_id": "volume.a",
                "leak_rate_air": 20,
                "leak_rate_water": 4,
                "hazard_model_id": "hazard.leak.a",
                "extensions": {},
            }
        ],
    }


def _request() -> dict:
    return {
        "schema_version": "1.0.0",
        "request_id": "inspect.req.interior.redaction.1",
        "requester_subject_id": "subject.player",
        "target_kind": "interior_graph",
        "target_id": "interior.graph.test.alpha",
        "desired_fidelity": "meso",
        "tick": 10,
        "max_cost_units": 200,
        "extensions": {},
    }


def _target_payload() -> dict:
    return {
        "target_kind": "interior_graph",
        "target_id": "interior.graph.test.alpha",
        "collection": "interior_graphs",
        "row": {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.test.alpha",
            "volumes": ["volume.a", "volume.b"],
            "portals": ["portal.ab"],
            "extensions": {},
        },
        "exists": True,
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.inspection.inspection_engine import build_inspection_snapshot_artifact

    state = _state()
    request_row = _request()
    target_payload = _target_payload()

    diegetic_snapshot, _ = build_inspection_snapshot_artifact(
        request_row=request_row,
        target_payload=target_payload,
        state=state,
        truth_hash_anchor="hash.truth.int3",
        ledger_hash="hash.ledger.int3",
        section_registry_payload={},
        policy_context={"epistemic_policy_id": "ep.policy.default"},
        law_profile={"epistemic_policy_id": "ep.policy.default", "epistemic_limits": {"allow_hidden_state_access": False}},
        authority_context={"entitlements": ["entitlement.inspect"], "epistemic_scope": {"visibility_level": "diegetic"}},
        physics_profile_id="physics.test",
        pack_lock_hash="lock.test",
        cache_policy_id="cache.off",
        strict_budget=False,
    )
    lab_snapshot, _ = build_inspection_snapshot_artifact(
        request_row=request_row,
        target_payload=target_payload,
        state=state,
        truth_hash_anchor="hash.truth.int3",
        ledger_hash="hash.ledger.int3",
        section_registry_payload={},
        policy_context={"epistemic_policy_id": "ep.policy.default"},
        law_profile={"epistemic_policy_id": "ep.policy.default", "epistemic_limits": {"allow_hidden_state_access": True}},
        authority_context={"entitlements": ["entitlement.inspect"], "epistemic_scope": {"visibility_level": "lab"}},
        physics_profile_id="physics.test",
        pack_lock_hash="lock.test",
        cache_policy_id="cache.off",
        strict_budget=False,
    )

    diegetic_sections = dict(diegetic_snapshot.get("summary_sections") or {})
    lab_sections = dict(lab_snapshot.get("summary_sections") or {})
    diegetic_flow = dict(diegetic_sections.get("section.interior.flow_summary") or {})
    lab_flow = dict(lab_sections.get("section.interior.flow_summary") or {})

    if not diegetic_flow or not lab_flow:
        return {"status": "fail", "message": "interior flow summary section missing from snapshots"}

    diegetic_data = dict(diegetic_flow.get("data") or {})
    lab_data = dict(lab_flow.get("data") or {})
    if not bool(diegetic_data.get("redacted", False)):
        return {"status": "fail", "message": "diegetic interior flow summary should be redacted"}
    if bool(lab_data.get("redacted", False)):
        return {"status": "fail", "message": "lab interior flow summary should expose detailed values"}
    if not list(lab_data.get("portal_flow_rows") or []):
        return {"status": "fail", "message": "lab interior flow summary should include portal flow rows"}

    return {"status": "pass", "message": "interior snapshot redaction is policy-gated"}

