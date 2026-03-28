"""STRICT test: LOGIC-6 invalid compiled models fall back explicitly and log the path."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_invalid_compiled_falls_back_logged"
TEST_TAGS = ["strict", "logic", "compile", "fallback"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.eval import process_logic_network_evaluate
    from logic.signal import process_signal_emit_pulse, process_signal_set
    from system import (
        build_state_vector_definition_row,
        deserialize_state,
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
        state_vector_snapshot_rows_by_owner,
    )
    from tools.xstack.testx.tests._logic_eval_test_utils import (
        compile_logic_network_fixture,
        make_chain_network,
        seed_signal_requests,
    )

    _, logic_network_state = make_chain_network(network_id="net.logic.compile.runtime_invalid")
    fixture = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id="net.logic.compile.runtime_invalid",
        logic_network_state=logic_network_state,
    )
    compile_eval = dict(fixture["compile_eval"] or {})
    inputs = dict(fixture["inputs"] or {})
    if str(compile_eval.get("result", "")) != "complete":
        return {"status": "fail", "message": "compile fixture did not complete"}

    tampered_network_state = copy.deepcopy(dict(compile_eval.get("logic_network_state") or {}))
    binding_rows = list(dict(tampered_network_state).get("logic_network_binding_rows") or [])
    if not binding_rows:
        return {"status": "fail", "message": "compiled fixture missing binding rows"}
    binding_rows[0]["extensions"] = dict(binding_rows[0].get("extensions") or {}, compiled_source_hash="tampered")
    tampered_network_state["logic_network_binding_rows"] = binding_rows

    signal_store_state = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "network_id": "net.logic.compile.runtime_invalid",
                "element_id": "inst.logic.and.1",
                "port_id": "in.a",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
            {
                "network_id": "net.logic.compile.runtime_invalid",
                "element_id": "inst.logic.and.1",
                "port_id": "in.b",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
        ],
        inputs=inputs,
    )

    result = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=tampered_network_state,
        signal_store_state=signal_store_state,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.compile.runtime_invalid"},
        state_vector_snapshot_rows=[],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        compiled_model_rows=[dict(compile_eval.get("compiled_model_row") or {})],
        equivalence_proof_rows=[dict(compile_eval.get("equivalence_proof_row") or {})],
        validity_domain_rows=[dict(compile_eval.get("validity_domain_row") or {})],
        **inputs,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "invalid compiled fixture should fall back to L1 and complete"}
    ext = dict(dict(result.get("eval_record_row") or {}).get("extensions") or {})
    if bool(ext.get("compiled_path_selected", False)):
        return {"status": "fail", "message": "invalid compiled fixture should not keep compiled_path_selected"}
    if not bool(ext.get("compiled_fallback_logged", False)):
        return {"status": "fail", "message": "invalid compiled fixture must log compiled_fallback_logged"}
    if not list(result.get("forced_expand_event_rows") or []):
        return {"status": "fail", "message": "invalid compiled fixture must emit a forced expand event"}
    explain_kinds = {
        str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip()
        for row in list(result.get("explain_artifact_rows") or [])
        if isinstance(row, dict)
    }
    if "logic.compiled_invalid" not in explain_kinds:
        return {"status": "fail", "message": "invalid compiled fixture must emit logic.compiled_invalid explain artifact"}
    return {"status": "pass", "message": "invalid compiled fixtures fall back explicitly and are logged"}
