"""STRICT test: LOGIC-7 trace throttling selects targets deterministically."""

from __future__ import annotations

import copy
import json
import os
import sys


TEST_ID = "test_throttle_strategy_deterministic"
TEST_TAGS = ["strict", "logic", "debug", "compute"]


def _load(repo_root: str, rel_path: str) -> dict:
    return json.load(open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.debug import process_logic_trace_start, process_logic_trace_tick
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, seed_signal_requests

    inputs = load_eval_inputs(repo_root)
    surfaces = _load(repo_root, "data/registries/instrumentation_surface_registry.json")
    access = _load(repo_root, "data/registries/access_policy_registry.json")
    models = _load(repo_root, "data/registries/measurement_model_registry.json")
    policies = _load(repo_root, "data/registries/debug_sampling_policy_registry.json")
    signal_store_state = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "tick": 0,
                "network_id": "net.logic.debug.throttle",
                "element_id": "inst.logic.tap.1",
                "port_id": "out.a",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
            {
                "tick": 0,
                "network_id": "net.logic.debug.throttle",
                "element_id": "inst.logic.tap.1",
                "port_id": "out.b",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 0},
            },
            {
                "tick": 0,
                "network_id": "net.logic.debug.throttle",
                "element_id": "inst.logic.tap.1",
                "port_id": "out.c",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
        ],
        inputs=inputs,
    )
    low_budget_profiles = copy.deepcopy(inputs["compute_budget_profile_registry_payload"])
    profile_rows = list(dict(low_budget_profiles.get("record") or {}).get("compute_budget_profiles") or [])
    for row in profile_rows:
        if str(row.get("compute_profile_id", "")).strip() == "compute.default":
            row["instruction_budget_per_tick"] = 2
            row["memory_budget_total"] = 8
            row["evaluation_cap_per_tick"] = 8
    low_budget_profiles["record"] = dict(low_budget_profiles.get("record") or {}, compute_budget_profiles=profile_rows)
    low_degrade = copy.deepcopy(inputs["compute_degrade_policy_registry_payload"])
    degrade_rows = list(dict(low_degrade.get("record") or {}).get("compute_degrade_policies") or [])
    for row in degrade_rows:
        if str(row.get("degrade_policy_id", "")).strip() == "degrade.default_order":
            row["tick_bucket_stride"] = 1
            row["allow_representation_degrade"] = True
    low_degrade["record"] = dict(low_degrade.get("record") or {}, compute_degrade_policies=degrade_rows)

    trace_request = {
        "request_id": "request.logic.trace.throttle",
        "subject_id": "net.logic.debug.throttle",
        "measurement_point_ids": ["measure.logic.signal"],
        "tick_start": 1,
        "tick_end": 1,
        "sampling_policy_id": "debug.sample.default",
        "extensions": {
            "targets": [
                {
                    "subject_id": "net.logic.debug.throttle",
                    "network_id": "net.logic.debug.throttle",
                    "element_id": "inst.logic.tap.1",
                    "port_id": "out.a",
                    "measurement_point_id": "measure.logic.signal",
                },
                {
                    "subject_id": "net.logic.debug.throttle",
                    "network_id": "net.logic.debug.throttle",
                    "element_id": "inst.logic.tap.1",
                    "port_id": "out.b",
                    "measurement_point_id": "measure.logic.signal",
                },
                {
                    "subject_id": "net.logic.debug.throttle",
                    "network_id": "net.logic.debug.throttle",
                    "element_id": "inst.logic.tap.1",
                    "port_id": "out.c",
                    "measurement_point_id": "measure.logic.signal",
                },
            ]
        },
    }

    def run_once():
        start = process_logic_trace_start(
            current_tick=0,
            logic_debug_state=None,
            logic_network_state={},
            trace_request=trace_request,
            compiled_model_rows=[],
            debug_sampling_policy_registry_payload=policies,
            compute_budget_profile_registry_payload=low_budget_profiles,
            compute_degrade_policy_registry_payload=low_degrade,
            has_physical_access=True,
        )
        session_id = str(dict(start.get("trace_session_row") or {}).get("session_id", "")).strip()
        tick = process_logic_trace_tick(
            current_tick=1,
            logic_debug_state=start.get("logic_debug_state"),
            signal_store_state=signal_store_state,
            logic_network_state={},
            logic_eval_state={},
            trace_tick_request={"session_id": session_id},
            state_vector_snapshot_rows=[],
            compiled_model_rows=[],
            protocol_registry_payload=inputs["protocol_registry_payload"],
            instrumentation_surface_registry_payload=surfaces,
            access_policy_registry_payload=access,
            measurement_model_registry_payload=models,
            compute_budget_profile_registry_payload=low_budget_profiles,
            compute_degrade_policy_registry_payload=low_degrade,
            authority_context={"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
            has_physical_access=True,
            available_instrument_type_ids=["instrument.logic_probe"],
        )
        return start, tick

    first_start, first_tick = run_once()
    second_start, second_tick = run_once()
    if str(first_start.get("result", "")) != "throttled":
        return {"status": "fail", "message": "trace start should throttle under the low budget fixture"}
    if str(first_tick.get("result", "")) != "throttled" or str(second_tick.get("result", "")) != "throttled":
        return {"status": "fail", "message": "trace tick should throttle deterministically under the low budget fixture"}
    if list(first_tick.get("trace_artifact_rows") or []) != list(second_tick.get("trace_artifact_rows") or []):
        return {"status": "fail", "message": "throttled trace artifacts drifted across equivalent runs"}
    sample_rows = list(dict(first_tick.get("trace_session_row") or {}).get("sample_rows") or [])
    if len(sample_rows) != 1 or len(list(dict(sample_rows[0]).get("values") or [])) != 1:
        return {"status": "fail", "message": "deterministic throttling should reduce the sampled target set to one value"}
    return {"status": "pass", "message": "trace throttling selects targets deterministically"}
