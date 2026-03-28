"""FAST test: INT-2 inspection applies epistemic redaction/quantization for interior values."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.interior.epistemic_redaction_of_values"
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
        "portal_flow_params": [
            {
                "schema_version": "1.0.0",
                "portal_id": "portal.ab",
                "conductance_air": 333,
                "conductance_water": 111,
                "conductance_smoke": 222,
                "sealing_coefficient": 901,
                "open_state_multiplier": 1000,
                "extensions": {},
            }
        ],
        "compartment_states": [
            {
                "schema_version": "1.0.0",
                "volume_id": "volume.a",
                "air_mass": 1234,
                "water_volume": 345,
                "temperature": None,
                "oxygen_fraction": 207,
                "smoke_density": 67,
                "derived_pressure": 1234,
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
                "leak_rate_air": 37,
                "leak_rate_water": 5,
                "hazard_model_id": "hazard.leak.a",
                "extensions": {},
            }
        ],
    }


def _request() -> dict:
    return {
        "schema_version": "1.0.0",
        "request_id": "inspect.req.interior.1",
        "requester_subject_id": "subject.player",
        "target_kind": "interior",
        "target_id": "interior.graph.test.alpha",
        "desired_fidelity": "meso",
        "tick": 10,
        "max_cost_units": 100,
        "extensions": {},
    }


def _target_payload() -> dict:
    return {
        "target_kind": "interior",
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

    from inspection.inspection_engine import build_inspection_snapshot_artifact

    state = _state()
    request_row = _request()
    target_payload = _target_payload()

    diegetic_snapshot, _ = build_inspection_snapshot_artifact(
        request_row=request_row,
        target_payload=target_payload,
        state=state,
        truth_hash_anchor="hash.truth.int2",
        ledger_hash="hash.ledger.int2",
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
        truth_hash_anchor="hash.truth.int2",
        ledger_hash="hash.ledger.int2",
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
    pressure_diegetic = dict(diegetic_sections.get("section.interior.pressure_map") or {})
    pressure_lab = dict(lab_sections.get("section.interior.pressure_map") or {})

    if not pressure_diegetic or not pressure_lab:
        return {"status": "fail", "message": "interior pressure_map section missing from inspection snapshots"}

    if str(pressure_diegetic.get("epistemic_redaction_level", "")) != "diegetic":
        return {"status": "fail", "message": "diegetic interior section should be redacted"}

    diegetic_rows = list((dict(pressure_diegetic.get("data") or {}).get("rows") or []))
    lab_rows = list((dict(pressure_lab.get("data") or {}).get("rows") or []))
    diegetic_row_a = next((dict(row) for row in diegetic_rows if str(row.get("volume_id", "")) == "volume.a"), {})
    lab_row_a = next((dict(row) for row in lab_rows if str(row.get("volume_id", "")) == "volume.a"), {})

    if int(diegetic_row_a.get("derived_pressure", -1) or -1) != 1200:
        return {"status": "fail", "message": "diegetic interior pressure value should be quantized to coarse step"}
    if int(lab_row_a.get("derived_pressure", -1) or -1) != 1234:
        return {"status": "fail", "message": "lab interior pressure value should retain precise reading"}

    return {"status": "pass", "message": "interior epistemic redaction/quantization passed"}
