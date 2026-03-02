"""FAST test: MOB-10 vehicle dashboard instruments remain diegetic and channel-redacted."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "test_instrument_redaction"
TEST_TAGS = ["fast", "mobility", "interior", "diegetics", "epistemic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from mobility_interior_testlib import attach_field_layers, authority_context, law_profile, policy_context, seed_state
    from tools.xstack.sessionx.observation import observe_truth
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = seed_state(include_vehicle=True, vehicle_position_x=100)
    state = attach_field_layers(
        state,
        cell_id="cell.mob10.redaction",
        temperature=4,
        moisture=700,
        visibility=420,
        wind={"x": 280, "y": 0, "z": 0},
    )
    run_law = law_profile(["process.compartment_flow_tick"])
    run_auth = authority_context(["session.boot"], privilege_level="observer", visibility_level="diegetic")
    run_policy = policy_context()
    flow = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob10.instruments.tick.001",
            "process_id": "process.compartment_flow_tick",
            "inputs": {"graph_id": "interior.graph.mob10.alpha", "dt_ticks": 1},
        },
        law_profile=copy.deepcopy(run_law),
        authority_context=copy.deepcopy(run_auth),
        navigation_indices={},
        policy_context=copy.deepcopy(run_policy),
    )
    if str(flow.get("result", "")) != "complete":
        return {"status": "fail", "message": "compartment flow tick failed in instrument redaction fixture"}

    observation = observe_truth(
        truth_model={"universe_state": copy.deepcopy(state)},
        lens={
            "lens_id": "lens.diegetic.sensor",
            "lens_type": "diegetic",
            "required_entitlements": ["session.boot"],
            "observation_channels": ["ch.camera.state", "ch.diegetic.vehicle.pressure"],
            "epistemic_constraints": {"visibility_policy": "sensor_limited"},
        },
        law_profile={
            "law_profile_id": "law.test.mob10.instrument.redaction",
            "allowed_lenses": ["lens.diegetic.sensor"],
            "epistemic_limits": {"allow_hidden_state_access": False},
        },
        authority_context={
            "authority_origin": "client",
            "experience_id": "profile.test.mob10.instrument.redaction",
            "law_profile_id": "law.test.mob10.instrument.redaction",
            "entitlements": ["session.boot"],
            "epistemic_scope": {"scope_id": "scope.mob10.instrument.redaction", "visibility_level": "diegetic"},
            "privilege_level": "observer",
        },
        viewpoint_id="view.mob10.instrument.redaction",
        epistemic_policy={
            "epistemic_policy_id": "ep.policy.mob10.instrument.redaction",
            "allowed_observation_channels": ["ch.camera.state", "ch.diegetic.vehicle.pressure"],
            "forbidden_channels": [],
            "retention_policy_id": "ep.retention.none",
            "inference_policy_id": "ep.infer.none",
            "max_precision_rules": [],
            "deterministic_filters": ["filter.channel_allow_deny.v1"],
            "extensions": {},
        },
        retention_policy={
            "retention_policy_id": "ep.retention.none",
            "memory_allowed": False,
            "max_memory_items": 0,
            "decay_model_id": "none",
            "deterministic_eviction_rule_id": "evict.none",
            "extensions": {},
        },
    )
    if str(observation.get("result", "")) != "complete":
        return {"status": "fail", "message": "diegetic observation refused unexpectedly"}

    perceived = dict(observation.get("perceived_model") or {})
    instruments = dict(perceived.get("diegetic_instruments") or {})
    pressure = dict(instruments.get("instrument.vehicle.pressure") or {})
    oxygen = dict(instruments.get("instrument.vehicle.oxygen") or {})
    reading = pressure.get("reading")
    pressure_state = dict(pressure.get("state") or {})
    outputs = dict(pressure.get("outputs") or {})
    output_rows = [dict(row) for row in list(outputs.get("rows") or []) if isinstance(row, dict)]

    if not pressure:
        return {"status": "fail", "message": "requested vehicle pressure channel did not expose dashboard instrument payload"}
    if isinstance(reading, (int, float)):
        return {"status": "fail", "message": "vehicle pressure reading leaked numeric pressure values"}
    if str(pressure_state.get("status", "")).strip() not in {"OK", "WARN", "ALERT"}:
        return {"status": "fail", "message": "vehicle pressure state should be quantized to coarse status bands"}
    if output_rows and any("derived_pressure" in row for row in output_rows):
        return {"status": "fail", "message": "vehicle pressure output rows leaked compartment derived_pressure"}
    if oxygen:
        return {"status": "fail", "message": "unrequested vehicle oxygen channel should be redacted to empty payload"}

    return {"status": "pass", "message": "vehicle instruments remain diegetic and channel-redacted"}
