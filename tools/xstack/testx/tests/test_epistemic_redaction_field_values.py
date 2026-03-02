"""FAST test: field instrument readouts are coarse by default and precise when epistemically allowed."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_epistemic_redaction_field_values"
TEST_TAGS = ["fast", "fields", "diegetics", "epistemics"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.fields.epistemics",
        "allowed_processes": ["process.instrument_tick"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {"process.instrument_tick": "session.boot"},
        "process_privilege_requirements": {"process.instrument_tick": "observer"},
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1000000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
    }


def _authority(visibility_level: str) -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.fields.epistemics",
        "subject_id": "subject.test.fields.epistemics",
        "law_profile_id": "law.test.fields.epistemics",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.test.fields.epistemics", "visibility_level": str(visibility_level)},
        "privilege_level": "observer",
    }


def _base_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 10, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "time_control": {"rate_permille": 1000, "paused": False, "accumulator_permille": 0},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
        "instrument_assemblies": [],
        "field_modifier_rows": [
            {
                "target_id": "world.global",
                "temperature": 37,
                "moisture": 740,
                "friction": 410,
                "radiation": 320,
                "visibility": 540,
                "wind": {"x": 280, "y": 30, "z": 0},
                "traction_permille": 600,
                "wind_drift_permille": 100,
                "stress_capacity_permille": 880,
                "corrosion_risk_permille": 740,
                "icing_active": False,
            }
        ],
        "effect_rows": [],
        "effect_provenance_events": [],
        "process_log": [],
        "history_anchors": [],
    }


def _thermometer_row(state: dict) -> dict:
    for row in list(state.get("instrument_assemblies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == "instrument.meter.thermometer":
            return dict(row)
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    diegetic_state = _base_state()
    diegetic = execute_intent(
        state=diegetic_state,
        intent={"intent_id": "intent.field.epistemic.001", "process_id": "process.instrument_tick", "inputs": {}},
        law_profile=_law_profile(),
        authority_context=_authority("diegetic"),
        navigation_indices={},
        policy_context={"pack_lock_hash": "a" * 64},
    )
    if str(diegetic.get("result", "")) != "complete":
        return {"status": "fail", "message": "diegetic instrument tick failed"}
    diegetic_row = _thermometer_row(diegetic_state)
    diegetic_reading = dict(diegetic_row.get("reading") or {})
    if str(diegetic_reading.get("status", "")) != "COARSE":
        return {"status": "fail", "message": "diegetic thermometer should be coarse"}
    if "temperature_c" in diegetic_reading:
        return {"status": "fail", "message": "diegetic thermometer leaked precise temperature"}

    precise_state = copy.deepcopy(_base_state())
    precise = execute_intent(
        state=precise_state,
        intent={"intent_id": "intent.field.epistemic.002", "process_id": "process.instrument_tick", "inputs": {}},
        law_profile=_law_profile(),
        authority_context=_authority("nondiegetic"),
        navigation_indices={},
        policy_context={"pack_lock_hash": "a" * 64},
    )
    if str(precise.get("result", "")) != "complete":
        return {"status": "fail", "message": "nondiegetic instrument tick failed"}
    precise_row = _thermometer_row(precise_state)
    precise_reading = dict(precise_row.get("reading") or {})
    if str(precise_reading.get("status", "")) != "PRECISE":
        return {"status": "fail", "message": "nondiegetic thermometer should be precise"}
    if int(precise_reading.get("temperature_c", -999)) != 37:
        return {"status": "fail", "message": "nondiegetic thermometer did not report expected precise value"}
    return {"status": "pass", "message": "epistemic field readout redaction behaves as expected"}

