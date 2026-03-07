"""Replay LOGIC windows through L1 and compiled paths and compare output/state hashes."""

from __future__ import annotations

import argparse
import json
import os
from typing import Iterable, Mapping

from src.logic.compile import compile_logic_network
from src.system import build_state_vector_definition_row, normalize_state_vector_definition_rows
from tools.logic.tool_replay_logic_window import _load_eval_inputs, _load_json, _write_json, replay_logic_window_from_payload
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def _strip_compiled_bindings(logic_network_state: Mapping[str, object] | None) -> dict:
    state = _as_map(logic_network_state)
    binding_rows = []
    for row in list(state.get("logic_network_binding_rows") or []):
        if not isinstance(row, Mapping):
            continue
        binding = dict(row)
        ext = dict(binding.get("extensions") or {})
        for key in (
            "compiled_model_id",
            "compiled_equivalence_proof_id",
            "compiled_validity_domain_id",
            "compile_policy_id",
            "compile_policy_fingerprint",
            "compiled_target_type",
            "compiled_source_hash",
            "compiled_payload_hash",
            "compiled_prefer_runtime",
            "proof_requirement_enforced",
        ):
            ext.pop(key, None)
        binding["extensions"] = ext
        binding_rows.append(binding)
    stripped = dict(state)
    stripped["logic_network_binding_rows"] = binding_rows
    return stripped


def _compile_requests_for_payload(payload: Mapping[str, object]) -> list[dict]:
    explicit = [
        dict(row)
        for row in list(payload.get("compile_requests") or [])
        if isinstance(row, Mapping) and _token(row.get("network_id"))
    ]
    if explicit:
        return sorted(
            explicit,
            key=lambda item: (
                _token(item.get("network_id")),
                _token(item.get("compile_policy_id")),
                _token(item.get("request_id")),
            ),
        )
    inferred = {}
    for row in list(payload.get("evaluation_requests") or []):
        if not isinstance(row, Mapping):
            continue
        network_id = _token(row.get("network_id"))
        if not network_id:
            continue
        key = (network_id, _token(row.get("compile_policy_id")) or "compile.logic.default")
        inferred[key] = {
            "network_id": network_id,
            "compile_policy_id": key[1],
        }
    return [dict(inferred[key]) for key in sorted(inferred.keys())]


def _compile_payload(repo_root: str, payload: Mapping[str, object]) -> dict:
    inputs = _load_eval_inputs(repo_root)
    logic_network_state = _strip_compiled_bindings(payload.get("logic_network_state"))
    state_vector_definition_rows = normalize_state_vector_definition_rows(
        list(inputs.get("state_vector_definition_rows") or [])
        + [dict(row) for row in list(payload.get("state_vector_definition_rows") or []) if isinstance(row, Mapping)]
    )
    compile_requests = _compile_requests_for_payload(payload)
    if not compile_requests:
        return {"result": "refused", "reason_code": "refusal.logic.compile.network_not_found"}

    compile_request_rows = []
    compile_result_rows = []
    compiled_model_rows = []
    equivalence_proof_rows = []
    validity_domain_rows = []
    for request in compile_requests:
        compile_eval = compile_logic_network(
            current_tick=int(max(0, int(request.get("tick", 0) or 0))),
            compile_request=request,
            logic_network_state=logic_network_state,
            logic_policy_registry_payload=inputs["logic_policy_registry_payload"],
            logic_network_policy_registry_payload=inputs["logic_network_policy_registry_payload"],
            logic_compile_policy_registry_payload=inputs["logic_compile_policy_registry_payload"],
            compiled_type_registry_payload=inputs["compiled_type_registry_payload"],
            verification_procedure_registry_payload=inputs["verification_procedure_registry_payload"],
            logic_element_rows=inputs["logic_element_rows"],
            logic_behavior_model_rows=inputs["logic_behavior_model_rows"],
            logic_interface_signature_rows=inputs["logic_interface_signature_rows"],
            logic_state_machine_rows=inputs["logic_state_machine_rows"],
            state_vector_definition_rows=state_vector_definition_rows,
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        )
        if _token(compile_eval.get("result")) != "complete":
            return dict(compile_eval)
        logic_network_state = dict(compile_eval.get("logic_network_state") or logic_network_state)
        compile_request_rows.append(dict(compile_eval.get("compile_request_row") or {}))
        compile_result_rows.append(dict(compile_eval.get("compile_result_row") or {}))
        compiled_model_rows.append(dict(compile_eval.get("compiled_model_row") or {}))
        equivalence_proof_rows.append(dict(compile_eval.get("equivalence_proof_row") or {}))
        validity_domain_rows.append(dict(compile_eval.get("validity_domain_row") or {}))
    return {
        "result": "complete",
        "logic_network_state": logic_network_state,
        "compile_request_rows": compile_request_rows,
        "compile_result_rows": compile_result_rows,
        "compiled_model_rows": compiled_model_rows,
        "equivalence_proof_rows": equivalence_proof_rows,
        "validity_domain_rows": validity_domain_rows,
    }


def replay_compiled_logic_window_from_payload(*, repo_root: str, payload: Mapping[str, object]) -> dict:
    baseline_payload = dict(payload)
    baseline_payload["logic_network_state"] = _strip_compiled_bindings(payload.get("logic_network_state"))
    baseline_payload["compile_request_rows"] = []
    baseline_payload["compile_result_rows"] = []
    baseline_payload["compiled_model_rows"] = []
    baseline_payload["equivalence_proof_rows"] = []
    baseline_payload["validity_domain_rows"] = []
    l1_report = replay_logic_window_from_payload(repo_root=repo_root, payload=baseline_payload)
    if _token(l1_report.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": _token(l1_report.get("reason_code")) or "refusal.logic.eval.network_not_validated",
            "l1_report": l1_report,
        }

    compile_payload = _compile_payload(repo_root, baseline_payload)
    if _token(compile_payload.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": _token(compile_payload.get("reason_code")) or "refusal.logic.compile.ineligible",
            "l1_report": l1_report,
            "compile_payload": compile_payload,
        }

    compiled_payload = dict(baseline_payload)
    compiled_payload["logic_network_state"] = dict(compile_payload.get("logic_network_state") or {})
    compiled_payload["compile_request_rows"] = list(compile_payload.get("compile_request_rows") or [])
    compiled_payload["compile_result_rows"] = list(compile_payload.get("compile_result_rows") or [])
    compiled_payload["compiled_model_rows"] = list(compile_payload.get("compiled_model_rows") or [])
    compiled_payload["equivalence_proof_rows"] = list(compile_payload.get("equivalence_proof_rows") or [])
    compiled_payload["validity_domain_rows"] = list(compile_payload.get("validity_domain_rows") or [])
    compiled_report = replay_logic_window_from_payload(repo_root=repo_root, payload=compiled_payload)
    if _token(compiled_report.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": _token(compiled_report.get("reason_code")) or "refusal.logic.compiled_invalid",
            "l1_report": l1_report,
            "compiled_report": compiled_report,
        }
    compiled_path_observed = any(
        bool(dict(row.get("extensions") or {}).get("compiled_path_selected", False))
        for row in list(dict(compiled_report.get("final_logic_eval_state") or {}).get("logic_network_runtime_state_rows") or [])
        if isinstance(row, Mapping)
    )
    if not compiled_path_observed:
        return {
            "result": "refused",
            "reason_code": "refusal.logic.compiled_invalid",
            "l1_report": l1_report,
            "compiled_report": compiled_report,
        }

    l1_tick_signal_hashes = [
        (_token(row.get("network_id")), int(row.get("tick", 0) or 0), _token(row.get("signal_hash")))
        for row in list(l1_report.get("tick_reports") or [])
        if isinstance(row, Mapping)
    ]
    compiled_tick_signal_hashes = [
        (_token(row.get("network_id")), int(row.get("tick", 0) or 0), _token(row.get("signal_hash")))
        for row in list(compiled_report.get("tick_reports") or [])
        if isinstance(row, Mapping)
    ]
    signals_match = _token(l1_report.get("final_signal_hash")) == _token(compiled_report.get("final_signal_hash"))
    states_match = _token(l1_report.get("final_state_vector_snapshot_hash")) == _token(
        compiled_report.get("final_state_vector_snapshot_hash")
    )
    tick_signal_match = l1_tick_signal_hashes == compiled_tick_signal_hashes
    match = bool(signals_match and states_match and tick_signal_match)
    report = {
        "result": "complete" if match else "mismatch",
        "reason_code": "" if match else "logic.compiled_replay_mismatch",
        "signals_match": signals_match,
        "states_match": states_match,
        "tick_signal_match": tick_signal_match,
        "l1_final_signal_hash": _token(l1_report.get("final_signal_hash")),
        "compiled_final_signal_hash": _token(compiled_report.get("final_signal_hash")),
        "l1_final_state_vector_snapshot_hash": _token(l1_report.get("final_state_vector_snapshot_hash")),
        "compiled_final_state_vector_snapshot_hash": _token(compiled_report.get("final_state_vector_snapshot_hash")),
        "compiled_model_ids": sorted(
            _token(row.get("compiled_model_id"))
            for row in list(compile_payload.get("compiled_model_rows") or [])
            if isinstance(row, Mapping) and _token(row.get("compiled_model_id"))
        ),
        "compiled_type_ids": sorted(
            _token(row.get("compiled_type_id"))
            for row in list(compile_payload.get("compiled_model_rows") or [])
            if isinstance(row, Mapping) and _token(row.get("compiled_type_id"))
        ),
        "compiled_path_observed": compiled_path_observed,
        "compile_result_hash_chain": _token(compiled_report.get("compile_result_hash_chain")),
        "compiled_model_hash_chain": _token(compiled_report.get("compiled_model_hash_chain")),
        "equivalence_proof_hash_chain": _token(compiled_report.get("equivalence_proof_hash_chain")),
        "logic_compile_policy_hash_chain": _token(compiled_report.get("logic_compile_policy_hash_chain")),
        "forced_expand_event_hash_chain": _token(compiled_report.get("forced_expand_event_hash_chain")),
        "l1_report": l1_report,
        "compiled_report": compiled_report,
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        {
            "signals_match": report["signals_match"],
            "states_match": report["states_match"],
            "tick_signal_match": report["tick_signal_match"],
            "l1_final_signal_hash": report["l1_final_signal_hash"],
            "compiled_final_signal_hash": report["compiled_final_signal_hash"],
            "compiled_model_hash_chain": report["compiled_model_hash_chain"],
            "equivalence_proof_hash_chain": report["equivalence_proof_hash_chain"],
            "logic_compile_policy_hash_chain": report["logic_compile_policy_hash_chain"],
            "forced_expand_event_hash_chain": report["forced_expand_event_hash_chain"],
        }
    )
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--scenario-json", required=True)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = _load_json(os.path.join(args.repo_root, args.scenario_json.replace("/", os.sep)))
    report = replay_compiled_logic_window_from_payload(repo_root=args.repo_root, payload=payload)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if _token(report.get("result")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
