"""FAST test: EMB-1 logic probe access stays entitlement-gated and instrument-gated."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_probe_requires_access"
TEST_TAGS = ["fast", "embodiment", "toolbelt", "logic", "instrumentation"]


def _load(repo_root: str, rel_path: str) -> dict:
    return json.load(open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.embodiment import build_logic_probe_task
    from src.logic.debug import process_logic_probe
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, seed_signal_requests
    from tools.xstack.testx.tests.emb1_testlib import authority_context

    wrapper_denied = build_logic_probe_task(
        authority_context=authority_context(),
        subject_id="net.logic.debug.probe",
        measurement_point_id="measure.logic.signal",
        network_id="net.logic.debug.probe",
        element_id="inst.logic.and.1",
        port_id="out.q",
    )
    if str(wrapper_denied.get("result", "")) != "refused":
        return {"status": "fail", "message": "logic probe tool wrapper should refuse without ent.tool.logic_probe"}
    wrapper_allowed = build_logic_probe_task(
        authority_context=authority_context(entitlements=["ent.tool.logic_probe"]),
        subject_id="net.logic.debug.probe",
        measurement_point_id="measure.logic.signal",
        network_id="net.logic.debug.probe",
        element_id="inst.logic.and.1",
        port_id="out.q",
    )
    if str(wrapper_allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic probe tool wrapper should complete with ent.tool.logic_probe"}

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
    probe_request = dict(wrapper_allowed.get("probe_request") or {})
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
        authority_context={"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
        has_physical_access=True,
        available_instrument_type_ids=[],
    )
    if str(denied.get("result", "")) != "refused":
        return {"status": "fail", "message": "logic probe process should refuse without an instrument"}
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
        authority_context={"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
        has_physical_access=True,
        available_instrument_type_ids=["instrument.logic_probe"],
    )
    if str(allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic probe process should complete with access and instrument"}
    artifacts = list(dict(allowed.get("logic_debug_state") or {}).get("logic_debug_probe_artifact_rows") or [])
    if len(artifacts) != 1:
        return {"status": "fail", "message": "logic probe did not emit a bounded probe artifact"}
    return {"status": "pass", "message": "logic probe wrapper and process remain access gated"}
