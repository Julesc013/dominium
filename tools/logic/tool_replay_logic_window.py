"""Replay a deterministic LOGIC-4 evaluation window and summarize proof hashes."""

from __future__ import annotations

import argparse
import json
import os
from typing import Iterable, Mapping

from logic.eval import normalize_logic_eval_state, process_logic_network_evaluate
from logic.signal import canonical_signal_hash, process_signal_emit_pulse, process_signal_set
from system import (
    build_state_vector_definition_row,
    deserialize_state,
    normalize_state_vector_definition_rows,
    normalize_state_vector_snapshot_rows,
    serialize_state,
    state_vector_snapshot_rows_by_owner,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _registry_rows(payload: Mapping[str, object], key: str) -> list[dict]:
    record = dict(payload.get("record") or {})
    rows = record.get(key)
    if not isinstance(rows, list):
        rows = payload.get(key)
    return [dict(item) for item in list(rows or []) if isinstance(item, Mapping)]


def _load_eval_inputs(repo_root: str) -> dict:
    def read(rel_path: str) -> dict:
        return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))

    state_vector_rows = _registry_rows(read("data/registries/state_vector_registry.json"), "state_vector_definitions")
    state_vector_rows.extend(_registry_rows(read("packs/core/pack.core.logic_base/data/logic_state_vectors.json"), "state_vector_definitions"))
    return {
        "signal_type_registry_payload": read("data/registries/signal_type_registry.json"),
        "carrier_type_registry_payload": read("data/registries/carrier_type_registry.json"),
        "signal_delay_policy_registry_payload": read("data/registries/signal_delay_policy_registry.json"),
        "signal_noise_policy_registry_payload": read("data/registries/signal_noise_policy_registry.json"),
        "logic_noise_policy_registry_payload": read("data/registries/logic_noise_policy_registry.json"),
        "logic_security_policy_registry_payload": read("data/registries/logic_security_policy_registry.json"),
        "logic_fault_kind_registry_payload": read("data/registries/logic_fault_kind_registry.json"),
        "bus_encoding_registry_payload": read("data/registries/bus_encoding_registry.json"),
        "protocol_registry_payload": read("data/registries/protocol_registry.json"),
        "arbitration_policy_registry_payload": read("data/registries/arbitration_policy_registry.json"),
        "error_detection_policy_registry_payload": read("data/registries/error_detection_policy_registry.json"),
        "logic_policy_registry_payload": read("data/registries/logic_policy_registry.json"),
        "logic_network_policy_registry_payload": read("data/registries/logic_network_policy_registry.json"),
        "logic_element_rows": _registry_rows(read("packs/core/pack.core.logic_base/data/logic_element_registry.json"), "logic_elements"),
        "logic_behavior_model_rows": _registry_rows(read("packs/core/pack.core.logic_base/data/logic_behavior_model_registry.json"), "logic_behavior_models"),
        "logic_interface_signature_rows": _registry_rows(read("packs/core/pack.core.logic_base/data/logic_interface_signatures.json"), "logic_interface_signatures"),
        "logic_state_machine_rows": _registry_rows(read("packs/core/pack.core.logic_base/data/logic_state_machine_registry.json"), "state_machine_definitions"),
        "watchdog_definition_rows": _registry_rows(read("packs/core/pack.core.logic_base/data/logic_watchdog_definitions.json"), "watchdog_definitions"),
        "state_vector_definition_rows": normalize_state_vector_definition_rows(state_vector_rows),
        "compiled_type_registry_payload": read("data/registries/compiled_type_registry.json"),
        "verification_procedure_registry_payload": read("data/registries/verification_procedure_registry.json"),
        "logic_compile_policy_registry_payload": read("data/registries/logic_compile_policy_registry.json"),
        "compute_budget_profile_registry_payload": read("data/registries/compute_budget_profile_registry.json"),
        "compute_degrade_policy_registry_payload": read("data/registries/compute_degrade_policy_registry.json"),
        "tolerance_policy_registry_payload": read("data/registries/tolerance_policy_registry.json"),
        "temporal_domain_registry_payload": read("data/registries/temporal_domain_registry.json"),
        "time_mapping_registry_payload": read("data/registries/time_mapping_registry.json"),
        "drift_policy_registry_payload": read("data/registries/drift_policy_registry.json"),
        "model_type_registry_payload": read("data/registries/model_type_registry.json"),
        "constitutive_model_registry_payload": read("data/registries/constitutive_model_registry.json"),
        "loss_policy_registry_payload": read("data/registries/loss_policy_registry.json"),
        "routing_policy_registry_payload": read("data/registries/core_routing_policy_registry.json"),
        "attenuation_policy_registry_payload": read("data/registries/attenuation_policy_registry.json"),
        "belief_policy_registry_payload": read("data/registries/belief_policy_registry.json"),
    }


def replay_logic_window_from_payload(*, repo_root: str, payload: Mapping[str, object]) -> dict:
    inputs = _load_eval_inputs(repo_root)
    eval_inputs = dict(inputs)
    for key in (
        "compiled_type_registry_payload",
        "verification_procedure_registry_payload",
        "logic_compile_policy_registry_payload",
        "logic_fault_kind_registry_payload",
    ):
        eval_inputs.pop(key, None)
    logic_network_state = dict(payload.get("logic_network_state") or {})
    signal_store_state = dict(payload.get("signal_store_state") or {})
    logic_eval_state = dict(payload.get("logic_eval_state") or {})
    signal_transport_state = {
        "signal_channel_rows": [dict(row) for row in list(payload.get("signal_channel_rows") or []) if isinstance(row, Mapping)],
        "signal_message_envelope_rows": [dict(row) for row in list(payload.get("signal_message_envelope_rows") or []) if isinstance(row, Mapping)],
        "signal_transport_queue_rows": [dict(row) for row in list(payload.get("signal_transport_queue_rows") or []) if isinstance(row, Mapping)],
        "message_delivery_event_rows": [dict(row) for row in list(payload.get("message_delivery_event_rows") or []) if isinstance(row, Mapping)],
        "knowledge_receipt_rows": [dict(row) for row in list(payload.get("knowledge_receipt_rows") or []) if isinstance(row, Mapping)],
        "network_graph_rows": [dict(row) for row in list(payload.get("network_graph_rows") or []) if isinstance(row, Mapping)],
        "signal_trust_edge_rows": [dict(row) for row in list(payload.get("signal_trust_edge_rows") or payload.get("trust_edge_rows") or []) if isinstance(row, Mapping)],
        "loss_policy_registry_payload": inputs["loss_policy_registry_payload"],
        "routing_policy_registry_payload": inputs["routing_policy_registry_payload"],
        "attenuation_policy_registry_payload": inputs["attenuation_policy_registry_payload"],
        "belief_policy_registry_payload": inputs["belief_policy_registry_payload"],
        "belief_policy_id": str(payload.get("belief_policy_id", "")).strip() or "belief.default",
    }
    logic_fault_state_rows = [dict(row) for row in list(payload.get("logic_fault_state_rows") or []) if isinstance(row, Mapping)]
    compile_request_rows = [dict(row) for row in list(payload.get("compile_request_rows") or []) if isinstance(row, Mapping)]
    compile_result_rows = [dict(row) for row in list(payload.get("compile_result_rows") or []) if isinstance(row, Mapping)]
    compiled_model_rows = [dict(row) for row in list(payload.get("compiled_model_rows") or []) if isinstance(row, Mapping)]
    equivalence_proof_rows = [dict(row) for row in list(payload.get("equivalence_proof_rows") or []) if isinstance(row, Mapping)]
    validity_domain_rows = [dict(row) for row in list(payload.get("validity_domain_rows") or []) if isinstance(row, Mapping)]
    state_vector_definition_rows = normalize_state_vector_definition_rows(
        list(inputs.get("state_vector_definition_rows") or [])
        + [dict(row) for row in list(payload.get("state_vector_definition_rows") or []) if isinstance(row, Mapping)]
    )
    state_vector_snapshot_rows = normalize_state_vector_snapshot_rows(payload.get("state_vector_snapshot_rows") or [])
    forced_expand_event_rows = []

    evaluation_requests = [
        dict(row)
        for row in sorted(
            (dict(item) for item in list(payload.get("evaluation_requests") or []) if isinstance(item, Mapping)),
            key=lambda item: (int(item.get("tick", 0) or 0), str(item.get("network_id", ""))),
        )
    ]
    tick_reports = []
    for request in evaluation_requests:
        tick = int(request.get("tick", 0) or 0)
        result = process_logic_network_evaluate(
            current_tick=tick,
            logic_network_state=logic_network_state,
            signal_store_state=signal_store_state,
            logic_eval_state=logic_eval_state,
            evaluation_request=dict(request),
            state_vector_snapshot_rows=state_vector_snapshot_rows,
            logic_fault_state_rows=logic_fault_state_rows,
            process_signal_set_fn=process_signal_set,
            process_signal_emit_pulse_fn=process_signal_emit_pulse,
            signal_transport_state=signal_transport_state,
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
            serialize_state=serialize_state,
            compiled_model_rows=compiled_model_rows,
            equivalence_proof_rows=equivalence_proof_rows,
            validity_domain_rows=validity_domain_rows,
            **eval_inputs,
        )
        if str(result.get("result", "")) not in {"complete", "throttled"}:
            return {
                "result": "refused",
                "reason_code": str(result.get("reason_code", "")).strip() or "refusal.logic.eval.network_not_validated",
                "tick": tick,
                "network_id": str(request.get("network_id", "")).strip(),
            }
        signal_store_state = dict(result.get("signal_store_state") or signal_store_state)
        signal_transport_state = dict(result.get("signal_transport_state") or signal_transport_state)
        logic_eval_state = normalize_logic_eval_state(result.get("logic_eval_state"))
        state_vector_definition_rows = normalize_state_vector_definition_rows(
            result.get("state_vector_definition_rows") or state_vector_definition_rows
        )
        state_vector_snapshot_rows = normalize_state_vector_snapshot_rows(
            result.get("state_vector_snapshot_rows") or state_vector_snapshot_rows
        )
        forced_expand_event_rows.extend(
            dict(row) for row in list(result.get("forced_expand_event_rows") or []) if isinstance(row, Mapping)
        )
        tick_reports.append(
            {
                "tick": tick,
                "network_id": str(request.get("network_id", "")).strip(),
                "result": str(result.get("result", "")).strip(),
                "eval_record_id": str(dict(result.get("eval_record_row") or {}).get("record_id", "")).strip(),
                "signal_hash": canonical_signal_hash(state=signal_store_state, tick=tick),
                "logic_eval_hash": canonical_sha256(dict(result.get("eval_record_row") or {})),
            }
        )

    proof_surface = {
        "logic_throttle_event_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "reason": str(row.get("reason", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_throttle_event_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_state_update_hash_chain": canonical_sha256(
            [
                {
                    "update_id": str(row.get("update_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "owner_id": str(row.get("owner_id", "")).strip(),
                    "next_snapshot_hash": str(row.get("next_snapshot_hash", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_state_update_record_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_fault_state_hash_chain": canonical_sha256(
            [
                {
                    "fault_id": str(row.get("fault_id", "")).strip(),
                    "fault_kind_id": str(row.get("fault_kind_id", "")).strip(),
                    "target_kind": str(row.get("target_kind", "")).strip(),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "active": bool(row.get("active", False)),
                    "tick_set": int(row.get("tick_set", 0) or 0),
                }
                for row in list(logic_fault_state_rows or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_noise_decision_hash_chain": canonical_sha256(
            [
                {
                    "decision_id": str(row.get("decision_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "slot_key": str(row.get("slot_key", "")).strip(),
                    "noise_policy_id": str(row.get("noise_policy_id", "")).strip(),
                    "reason": str(row.get("reason", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_noise_decision_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_security_fail_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "security_policy_id": str(row.get("security_policy_id", "")).strip(),
                    "reason": str(row.get("reason", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_security_fail_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_protocol_frame_hash_chain": canonical_sha256(
            [
                {
                    "frame_id": str(row.get("frame_id", "")).strip(),
                    "protocol_id": str(row.get("protocol_id", "")).strip(),
                    "src_endpoint_id": str(row.get("src_endpoint_id", "")).strip(),
                    "tick_sent": int(row.get("tick_sent", 0) or 0),
                    "status": str(dict(row.get("extensions") or {}).get("status", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_protocol_frame_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_arbitration_state_hash_chain": canonical_sha256(
            [
                {
                    "bus_id": str(row.get("bus_id", "")).strip(),
                    "policy_id": str(row.get("policy_id", "")).strip(),
                    "token_holder": str(row.get("token_holder", "")).strip() or None,
                    "last_winner": str(row.get("last_winner", "")).strip() or None,
                }
                for row in list(logic_eval_state.get("logic_arbitration_state_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_protocol_event_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "protocol_id": str(row.get("protocol_id", "")).strip(),
                    "bus_id": str(row.get("bus_id", "")).strip(),
                    "frame_id": str(row.get("frame_id", "")).strip(),
                    "result": str(row.get("result", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                }
                for row in list(logic_eval_state.get("logic_protocol_event_record_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_output_signal_hash_chain": canonical_sha256(
            [
                {
                    "artifact_id": str(row.get("artifact_id", "")).strip(),
                    "created_tick": int(row.get("created_tick", 0) or 0),
                    "slot_key": str(row.get("slot_key", "")).strip(),
                    "signal_hash": str(row.get("signal_hash", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_propagation_trace_artifact_rows") or [])
                if isinstance(row, Mapping) and str(row.get("trace_kind", "")).strip() == "trace.logic.propagation_delivered"
            ]
        ),
        "logic_oscillation_record_hash_chain": canonical_sha256(
            [
                {
                    "record_id": str(row.get("record_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "period_ticks": int(row.get("period_ticks", 0) or 0),
                    "stable": bool(row.get("stable", False)),
                }
                for row in list(logic_eval_state.get("logic_oscillation_record_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_timing_violation_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "reason": str(row.get("reason", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_timing_violation_event_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "logic_watchdog_timeout_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "watchdog_id": str(row.get("watchdog_id", "")).strip(),
                    "action_on_timeout": str(row.get("action_on_timeout", "")).strip(),
                }
                for row in list(logic_eval_state.get("logic_watchdog_timeout_event_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "compile_result_hash_chain": canonical_sha256(
            [
                {
                    "result_id": str(row.get("result_id", "")).strip(),
                    "compiled_model_id": str(row.get("compiled_model_id", "")).strip(),
                    "success": bool(row.get("success", False)),
                    "refusal": str(row.get("refusal", "")).strip(),
                }
                for row in sorted(
                    (dict(item) for item in list(compile_result_rows or []) if isinstance(item, Mapping)),
                    key=lambda item: str(item.get("result_id", "")),
                )
            ]
        ),
        "compiled_model_hash_chain": canonical_sha256(
            [
                {
                    "compiled_model_id": str(row.get("compiled_model_id", "")).strip(),
                    "source_hash": str(row.get("source_hash", "")).strip(),
                    "compiled_type_id": str(row.get("compiled_type_id", "")).strip(),
                    "equivalence_proof_ref": str(row.get("equivalence_proof_ref", "")).strip(),
                    "validity_domain_ref": str(row.get("validity_domain_ref", "")).strip(),
                }
                for row in sorted(
                    (dict(item) for item in list(compiled_model_rows or []) if isinstance(item, Mapping)),
                    key=lambda item: str(item.get("compiled_model_id", "")),
                )
            ]
        ),
        "equivalence_proof_hash_chain": canonical_sha256(
            [
                {
                    "proof_id": str(row.get("proof_id", "")).strip(),
                    "proof_kind": str(row.get("proof_kind", "")).strip(),
                    "verification_procedure_id": str(row.get("verification_procedure_id", "")).strip(),
                    "proof_hash": str(row.get("proof_hash", "")).strip(),
                }
                for row in sorted(
                    (dict(item) for item in list(equivalence_proof_rows or []) if isinstance(item, Mapping)),
                    key=lambda item: str(item.get("proof_id", "")),
                )
            ]
        ),
        "logic_compile_policy_hash_chain": canonical_sha256(
            [
                {
                    "request_id": str(row.get("request_id", "")).strip(),
                    "compile_policy_id": str(dict(row.get("source_ref") or {}).get("compile_policy_id", "")).strip(),
                    "compile_policy_fingerprint": str(dict(row.get("extensions") or {}).get("compile_policy_fingerprint", "")).strip(),
                }
                for row in sorted(
                    (dict(item) for item in list(compile_request_rows or []) if isinstance(item, Mapping)),
                    key=lambda item: str(item.get("request_id", "")),
                )
                if str(dict(row.get("source_ref") or {}).get("compile_policy_id", "")).strip()
            ]
        ),
        "forced_expand_event_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "capsule_id": str(row.get("capsule_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "reason_code": str(row.get("reason_code", "")).strip(),
                }
                for row in sorted(
                    (dict(item) for item in list(forced_expand_event_rows or []) if isinstance(item, Mapping)),
                    key=lambda item: (
                        int(item.get("tick", 0) or 0),
                        str(item.get("capsule_id", "")),
                        str(item.get("event_id", "")),
                    ),
                )
            ]
        ),
    }
    report = {
        "result": "complete",
        "tick_reports": tick_reports,
        "final_signal_hash": canonical_signal_hash(state=signal_store_state),
        "logic_eval_record_hash_chain": canonical_sha256(
            [
                {
                    "record_id": str(row.get("record_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "network_id": str(row.get("network_id", "")).strip(),
                    "compute_units_used": int(row.get("compute_units_used", 0) or 0),
                }
                for row in list(logic_eval_state.get("logic_eval_record_rows") or [])
                if isinstance(row, Mapping)
            ]
        ),
        "compile_result_hash_chain": str(proof_surface.get("compile_result_hash_chain", "")),
        "compiled_model_hash_chain": str(proof_surface.get("compiled_model_hash_chain", "")),
        "equivalence_proof_hash_chain": str(proof_surface.get("equivalence_proof_hash_chain", "")),
        "logic_compile_policy_hash_chain": str(proof_surface.get("logic_compile_policy_hash_chain", "")),
        "forced_expand_event_hash_chain": str(proof_surface.get("forced_expand_event_hash_chain", "")),
        "logic_throttle_event_hash_chain": str(proof_surface.get("logic_throttle_event_hash_chain", "")),
        "logic_state_update_hash_chain": str(proof_surface.get("logic_state_update_hash_chain", "")),
        "logic_fault_state_hash_chain": str(proof_surface.get("logic_fault_state_hash_chain", "")),
        "logic_noise_decision_hash_chain": str(proof_surface.get("logic_noise_decision_hash_chain", "")),
        "logic_security_fail_hash_chain": str(proof_surface.get("logic_security_fail_hash_chain", "")),
        "logic_protocol_frame_hash_chain": str(proof_surface.get("logic_protocol_frame_hash_chain", "")),
        "logic_arbitration_state_hash_chain": str(proof_surface.get("logic_arbitration_state_hash_chain", "")),
        "logic_protocol_event_hash_chain": str(proof_surface.get("logic_protocol_event_hash_chain", "")),
        "logic_output_signal_hash_chain": str(proof_surface.get("logic_output_signal_hash_chain", "")),
        "logic_oscillation_record_hash_chain": str(proof_surface.get("logic_oscillation_record_hash_chain", "")),
        "logic_timing_violation_hash_chain": str(proof_surface.get("logic_timing_violation_hash_chain", "")),
        "logic_watchdog_timeout_hash_chain": str(proof_surface.get("logic_watchdog_timeout_hash_chain", "")),
        "proof_surface": proof_surface,
        "final_logic_eval_state": logic_eval_state,
        "final_signal_store_state": signal_store_state,
        "final_signal_transport_state": signal_transport_state,
        "final_state_vector_snapshot_rows": state_vector_snapshot_rows,
        "final_state_vector_snapshot_hash": canonical_sha256(state_vector_snapshot_rows),
        "forced_expand_event_rows": forced_expand_event_rows,
        "compiled_model_rows": compiled_model_rows,
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        {
            "tick_reports": tick_reports,
            "final_signal_hash": report["final_signal_hash"],
            "logic_eval_record_hash_chain": report["logic_eval_record_hash_chain"],
            "compile_result_hash_chain": report["compile_result_hash_chain"],
            "compiled_model_hash_chain": report["compiled_model_hash_chain"],
            "equivalence_proof_hash_chain": report["equivalence_proof_hash_chain"],
            "logic_compile_policy_hash_chain": report["logic_compile_policy_hash_chain"],
            "forced_expand_event_hash_chain": report["forced_expand_event_hash_chain"],
            "logic_throttle_event_hash_chain": report["logic_throttle_event_hash_chain"],
            "logic_state_update_hash_chain": report["logic_state_update_hash_chain"],
            "logic_fault_state_hash_chain": report["logic_fault_state_hash_chain"],
            "logic_noise_decision_hash_chain": report["logic_noise_decision_hash_chain"],
            "logic_security_fail_hash_chain": report["logic_security_fail_hash_chain"],
            "logic_protocol_frame_hash_chain": report["logic_protocol_frame_hash_chain"],
            "logic_arbitration_state_hash_chain": report["logic_arbitration_state_hash_chain"],
            "logic_protocol_event_hash_chain": report["logic_protocol_event_hash_chain"],
            "logic_output_signal_hash_chain": report["logic_output_signal_hash_chain"],
            "logic_oscillation_record_hash_chain": report["logic_oscillation_record_hash_chain"],
            "logic_timing_violation_hash_chain": report["logic_timing_violation_hash_chain"],
            "logic_watchdog_timeout_hash_chain": report["logic_watchdog_timeout_hash_chain"],
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
    report = replay_logic_window_from_payload(repo_root=args.repo_root, payload=payload)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
