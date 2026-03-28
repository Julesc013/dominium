"""STRICT test: LOGIC-7 compiled controllers expose boundary I/O only unless expanded."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_compiled_controller_io_only_without_expand"
TEST_TAGS = ["strict", "logic", "debug", "compile"]


def _load(repo_root: str, rel_path: str) -> dict:
    return json.load(open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.debug import process_logic_probe
    from tools.xstack.testx.tests._logic_eval_test_utils import compile_logic_network_fixture, make_chain_network

    _binding, logic_network_state = make_chain_network(network_id="net.logic.debug.compiled")
    fixture = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.debug.compiled",
        logic_network_state=logic_network_state,
    )
    compile_eval = dict(fixture.get("compile_eval") or {})
    compiled_model_row = dict(compile_eval.get("compiled_model_row") or {})
    compiled_logic_network_state = dict(compile_eval.get("logic_network_state") or logic_network_state)
    binding_rows = [dict(row) for row in list(compiled_logic_network_state.get("logic_network_binding_rows") or [])]
    if not compiled_model_row or not binding_rows:
        return {"status": "fail", "message": "compiled fixture missing compiled model or binding rows"}
    binding_rows[0]["extensions"] = dict(
        binding_rows[0].get("extensions") or {},
        compiled_model_id=str(compiled_model_row.get("compiled_model_id", "")).strip(),
        compiled_source_hash=str(compiled_model_row.get("source_hash", "")).strip(),
    )
    compiled_logic_network_state["logic_network_binding_rows"] = binding_rows

    surfaces = _load(repo_root, "data/registries/instrumentation_surface_registry.json")
    access = _load(repo_root, "data/registries/access_policy_registry.json")
    models = _load(repo_root, "data/registries/measurement_model_registry.json")
    inputs = fixture["inputs"]
    authority_context = {"privilege_level": "admin", "entitlements": ["entitlement.inspect", "entitlement.admin"]}

    boundary = process_logic_probe(
        current_tick=1,
        logic_debug_state=None,
        signal_store_state={},
        logic_network_state=compiled_logic_network_state,
        logic_eval_state={},
        probe_request={
            "request_id": "request.logic.debug.compiled.summary",
            "subject_id": "net.logic.debug.compiled",
            "measurement_point_id": "measure.logic.network.compiled_summary",
            "extensions": {"network_id": "net.logic.debug.compiled"},
        },
        state_vector_snapshot_rows=[],
        compiled_model_rows=[compiled_model_row],
        protocol_registry_payload=inputs["protocol_registry_payload"],
        instrumentation_surface_registry_payload=surfaces,
        access_policy_registry_payload=access,
        measurement_model_registry_payload=models,
        compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
        compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
        authority_context=authority_context,
        has_physical_access=True,
        available_instrument_type_ids=["instrument.logic_analyzer"],
    )
    if str(boundary.get("result", "")) != "complete":
        return {"status": "fail", "message": "compiled controller boundary summary should remain readable"}

    internal = process_logic_probe(
        current_tick=1,
        logic_debug_state=None,
        signal_store_state={},
        logic_network_state=compiled_logic_network_state,
        logic_eval_state={},
        probe_request={
            "request_id": "request.logic.debug.compiled.internal",
            "subject_id": "net.logic.debug.compiled",
            "measurement_point_id": "measure.logic.element.state_vector",
            "extensions": {
                "network_id": "net.logic.debug.compiled",
                "element_id": "inst.logic.and.1",
            },
        },
        state_vector_snapshot_rows=[],
        compiled_model_rows=[compiled_model_row],
        protocol_registry_payload=inputs["protocol_registry_payload"],
        instrumentation_surface_registry_payload=surfaces,
        access_policy_registry_payload=access,
        measurement_model_registry_payload=models,
        compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
        compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
        authority_context=authority_context,
        has_physical_access=True,
        available_instrument_type_ids=["instrument.logic_analyzer"],
    )
    if str(internal.get("result", "")) != "refused":
        return {"status": "fail", "message": "compiled controller internals should require explicit expand"}
    if str(internal.get("reason_code", "")) != "refusal.logic.debug_requires_expand":
        return {"status": "fail", "message": "compiled internal inspection refused for the wrong reason"}
    return {"status": "pass", "message": "compiled controllers expose boundary I/O only without expand"}
