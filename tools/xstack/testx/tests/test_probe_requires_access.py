"""STRICT test: LOGIC-7 probes require lawful access and instrumentation."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_probe_requires_access"
TEST_TAGS = ["strict", "logic", "debug", "instrumentation"]


def _load(repo_root: str, rel_path: str) -> dict:
    return json.load(open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.debug import process_logic_probe
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, seed_signal_requests

    inputs = load_eval_inputs(repo_root)
    signal_store_state = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "tick": 0,
                "network_id": "net.logic.debug.probe",
                "element_id": "inst.logic.and.1",
                "port_id": "out.q",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            }
        ],
        inputs=inputs,
    )
    surfaces = _load(repo_root, "data/registries/instrumentation_surface_registry.json")
    access = _load(repo_root, "data/registries/access_policy_registry.json")
    models = _load(repo_root, "data/registries/measurement_model_registry.json")
    probe_request = {
        "request_id": "request.logic.debug.probe.access",
        "subject_id": "net.logic.debug.probe",
        "measurement_point_id": "measure.logic.signal",
        "extensions": {
            "network_id": "net.logic.debug.probe",
            "element_id": "inst.logic.and.1",
            "port_id": "out.q",
        },
    }
    authority_context = {"privilege_level": "operator", "entitlements": ["entitlement.inspect"]}
    denied = process_logic_probe(
        current_tick=1,
        logic_debug_state=None,
        signal_store_state=signal_store_state,
        logic_network_state={},
        logic_eval_state={},
        probe_request=probe_request,
        state_vector_snapshot_rows=[],
        compiled_model_rows=[],
        protocol_registry_payload=inputs["protocol_registry_payload"],
        instrumentation_surface_registry_payload=surfaces,
        access_policy_registry_payload=access,
        measurement_model_registry_payload=models,
        compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
        compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
        authority_context=authority_context,
        has_physical_access=True,
        available_instrument_type_ids=[],
    )
    if str(denied.get("result", "")) != "refused":
        return {"status": "fail", "message": "logic probe should refuse without an instrument"}
    allowed = process_logic_probe(
        current_tick=1,
        logic_debug_state=None,
        signal_store_state=signal_store_state,
        logic_network_state={},
        logic_eval_state={},
        probe_request=probe_request,
        state_vector_snapshot_rows=[],
        compiled_model_rows=[],
        protocol_registry_payload=inputs["protocol_registry_payload"],
        instrumentation_surface_registry_payload=surfaces,
        access_policy_registry_payload=access,
        measurement_model_registry_payload=models,
        compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
        compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
        authority_context=authority_context,
        has_physical_access=True,
        available_instrument_type_ids=["instrument.logic_probe"],
    )
    if str(allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic probe should complete with access and the correct instrument"}
    artifacts = list(dict(allowed.get("logic_debug_state") or {}).get("logic_debug_probe_artifact_rows") or [])
    if len(artifacts) != 1:
        return {"status": "fail", "message": "logic probe did not emit a bounded probe artifact"}
    return {"status": "pass", "message": "logic probes require instrumentation and lawful access"}
