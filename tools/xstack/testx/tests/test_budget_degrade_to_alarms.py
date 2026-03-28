"""FAST test: INT-3 interior inspection degrades to coarse alarm summaries under tight budget."""

from __future__ import annotations

import sys


TEST_ID = "testx.interior.budget_degrade_to_alarms"
TEST_TAGS = ["fast", "interior", "inspection", "budget", "degrade"]


def _state() -> dict:
    return {
        "interior_graphs": [
            {
                "schema_version": "1.0.0",
                "graph_id": "interior.graph.test.budget",
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
        "compartment_states": [
            {
                "schema_version": "1.0.0",
                "volume_id": "volume.a",
                "air_mass": 800,
                "water_volume": 650,
                "temperature": None,
                "oxygen_fraction": 175,
                "smoke_density": 260,
                "derived_pressure": 800,
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
    }


def _request() -> dict:
    return {
        "schema_version": "1.0.0",
        "request_id": "inspect.req.interior.budget.1",
        "requester_subject_id": "subject.player",
        "target_kind": "interior_graph",
        "target_id": "interior.graph.test.budget",
        "desired_fidelity": "micro",
        "tick": 10,
        "max_cost_units": 1,
        "extensions": {},
    }


def _target_payload() -> dict:
    return {
        "target_kind": "interior_graph",
        "target_id": "interior.graph.test.budget",
        "collection": "interior_graphs",
        "row": {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.test.budget",
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

    from inspection.inspection_engine import build_inspection_snapshot_artifact

    snapshot, _ = build_inspection_snapshot_artifact(
        request_row=_request(),
        target_payload=_target_payload(),
        state=_state(),
        truth_hash_anchor="hash.truth.int3.budget",
        ledger_hash="hash.ledger.int3.budget",
        section_registry_payload={},
        policy_context={"epistemic_policy_id": "ep.policy.default"},
        law_profile={"epistemic_policy_id": "ep.policy.default", "epistemic_limits": {"allow_hidden_state_access": True}},
        authority_context={"entitlements": ["entitlement.inspect"], "epistemic_scope": {"visibility_level": "diegetic"}},
        physics_profile_id="physics.test",
        pack_lock_hash="lock.test",
        cache_policy_id="cache.off",
        strict_budget=False,
    )

    if str(snapshot.get("achieved_fidelity", "")) == "micro":
        return {"status": "fail", "message": "tight budget should degrade interior inspection below micro fidelity"}
    if not bool(dict(snapshot.get("extensions") or {}).get("degraded", False)):
        return {"status": "fail", "message": "snapshot should mark degraded under tight budget"}

    sections = dict(snapshot.get("summary_sections") or {})
    if "section.interior.pressure_summary" not in sections:
        return {"status": "fail", "message": "degraded interior inspection should still include coarse pressure summary"}
    if "section.interior.flow_summary" in sections:
        return {"status": "fail", "message": "degraded alarm-oriented inspection should not include interior flow internals"}

    return {"status": "pass", "message": "interior budget degradation falls back to coarse alarm sections"}

