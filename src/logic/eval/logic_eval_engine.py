"""LOGIC-4 deterministic evaluation orchestration."""

from __future__ import annotations

from typing import Mapping

from src.meta.explain import build_explain_artifact
from tools.xstack.compatx.canonical_json import canonical_sha256
from src.logic.protocol import arbitrate_logic_protocol_frames, transport_logic_sig_receipts

from .common import as_int, as_list, as_map, canon, rows_by_id, token
from .commit_engine import (
    PROCESS_STATEVEC_UPDATE,
    attach_instance_definitions_to_compute_result,
    commit_logic_state_updates,
    process_statevec_update,
)
from .compute_engine import evaluate_logic_compute_phase
from .propagate_engine import flush_due_logic_signal_updates, schedule_logic_output_propagation
from .runtime_state import (
    build_logic_eval_record_row,
    build_logic_network_runtime_state_row,
    build_logic_oscillation_record_row,
    build_logic_timing_violation_event_row,
    build_logic_throttle_event_row,
    build_logic_watchdog_timeout_event_row,
    normalize_logic_eval_state,
    normalize_logic_network_runtime_state_rows,
    normalize_logic_noise_decision_rows,
    normalize_logic_oscillation_record_rows,
    normalize_logic_protocol_event_record_rows,
    normalize_logic_protocol_frame_rows,
    normalize_arbitration_state_rows,
    normalize_logic_security_fail_rows,
    normalize_logic_timing_violation_event_rows,
    normalize_logic_throttle_event_rows,
    normalize_logic_watchdog_timeout_event_rows,
)
from .sense_engine import build_logic_sense_snapshot
from src.logic.timing import (
    detect_watchdog_timeout_transitions,
    detect_network_oscillation,
    evaluate_logic_timing_constraints,
    request_logic_timing_compute,
)


PROCESS_LOGIC_NETWORK_EVALUATE = "process.logic_network_evaluate"
REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND = "refusal.logic.eval.network_not_found"
REFUSAL_LOGIC_EVAL_NETWORK_NOT_VALIDATED = "refusal.logic.eval.network_not_validated"
REFUSAL_LOGIC_EVAL_LOOP_POLICY = "refusal.logic.eval.loop_policy"
REFUSAL_LOGIC_EVAL_TIMING_VIOLATION = "refusal.logic.eval.timing_violation"


def _binding_by_network_id(rows: object) -> dict:
    return rows_by_id(rows, "network_id")


def _graph_by_id(rows: object) -> dict:
    return rows_by_id(rows, "graph_id")


def _validation_record_for_network(rows: object, network_id: str) -> dict:
    selected = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: (as_int(item.get("tick"), 0), token(item.get("network_id")), token(item.get("validation_hash")))):
        if token(row.get("network_id")) == token(network_id):
            selected = dict(row)
    return selected


def _logic_policy_rows_by_id(payload: Mapping[str, object] | None) -> dict:
    body = as_map(payload)
    rows = body.get("logic_policies")
    if not isinstance(rows, list):
        rows = as_map(body.get("record")).get("logic_policies")
    return rows_by_id(rows or [], "policy_id")


def _logic_network_policy_rows_by_id(payload: Mapping[str, object] | None) -> dict:
    body = as_map(payload)
    rows = body.get("logic_network_policies")
    if not isinstance(rows, list):
        rows = as_map(body.get("record")).get("logic_network_policies")
    return rows_by_id(rows or [], "policy_id")


def _compiled_capsule_id(network_id: str) -> str:
    return "capsule.logic_controller.{}".format(canonical_sha256({"network_id": token(network_id)})[:16])


def _compiled_eval_validation_gate(
    *,
    binding_row: Mapping[str, object],
    validation_record: Mapping[str, object],
    network_policy_row: Mapping[str, object],
) -> bool:
    validation_status = token(as_map(binding_row.get("extensions")).get("validation_status"))
    if validation_status == "validated":
        return True
    return bool(
        token(as_map(binding_row.get("extensions")).get("compiled_model_id"))
        and token(validation_record.get("reason_code")) == "refusal.logic.loop_detected"
        and token(network_policy_row.get("loop_resolution_mode")).lower() == "allow_compiled_only"
    )


def _loop_policy_refusal(
    *,
    current_tick: int,
    network_id: str,
    validation_record: Mapping[str, object],
    network_policy_row: Mapping[str, object],
    compiled_runtime_ready: bool,
) -> dict:
    loop_classifications = [dict(item) for item in as_list(as_map(validation_record).get("loop_classifications")) if isinstance(item, Mapping)]
    loop_mode = token(network_policy_row.get("loop_resolution_mode")).lower() or "refuse"
    for row in loop_classifications:
        resolution = token(row.get("policy_resolution"))
        if compiled_runtime_ready and loop_mode == "allow_compiled_only" and token(row.get("classification")) in {"combinational", "mixed"}:
            continue
        if resolution == "refuse":
            return {
                "result": "refused",
                "reason_code": REFUSAL_LOGIC_EVAL_LOOP_POLICY,
                "explain_artifact_rows": [
                    build_explain_artifact(
                        explain_id="explain.logic_loop_detected.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(current_tick),
                                    "network_id": token(network_id),
                                    "loop_classification": canon(row),
                                }
                            )[:16]
                        ),
                        event_id="event.logic.loop_detected.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(current_tick),
                                    "network_id": token(network_id),
                                    "loop_classification": canon(row),
                                }
                            )[:16]
                        ),
                        target_id=token(network_id),
                        cause_chain=["cause.logic.loop_detected"],
                        remediation_hints=["validate network under a non-looping policy or move to LOGIC-6 compiled execution"],
                        extensions={
                            "event_kind_id": "explain.logic_loop_detected",
                            "loop_classification": canon(row),
                        },
                    )
                ],
            }
        if resolution == "force_roi" or resolution == "allow_compiled_only":
            hint = (
                "route this network through future LOGIC-5/6 ROI handling"
                if resolution == "force_roi"
                else "compiled-only loop networks remain gated until LOGIC-6 compiled execution is available"
            )
            return {
                "result": "refused",
                "reason_code": REFUSAL_LOGIC_EVAL_LOOP_POLICY,
                "explain_artifact_rows": [
                    build_explain_artifact(
                        explain_id="explain.logic_loop_policy_refused.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(current_tick),
                                    "network_id": token(network_id),
                                    "loop_classification": canon(row),
                                }
                            )[:16]
                        ),
                        event_id="event.logic.loop_policy_refused.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(current_tick),
                                    "network_id": token(network_id),
                                    "loop_classification": canon(row),
                                }
                            )[:16]
                        ),
                        target_id=token(network_id),
                        cause_chain=["cause.logic.loop_policy_refused"],
                        remediation_hints=[hint],
                        extensions={
                            "event_kind_id": "explain.logic_timing_violation",
                            "loop_classification": canon(row),
                        },
                    )
                ],
            }
    return {"result": "complete", "reason_code": "", "explain_artifact_rows": []}


def process_logic_network_evaluate(
    *,
    current_tick: int,
    logic_network_state: Mapping[str, object] | None,
    signal_store_state: Mapping[str, object] | None,
    logic_eval_state: Mapping[str, object] | None,
    evaluation_request: Mapping[str, object],
    signal_type_registry_payload: Mapping[str, object] | None,
    carrier_type_registry_payload: Mapping[str, object] | None,
    signal_delay_policy_registry_payload: Mapping[str, object] | None,
    signal_noise_policy_registry_payload: Mapping[str, object] | None,
    logic_noise_policy_registry_payload: Mapping[str, object] | None,
    bus_encoding_registry_payload: Mapping[str, object] | None,
    protocol_registry_payload: Mapping[str, object] | None,
    logic_policy_registry_payload: Mapping[str, object] | None,
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    logic_security_policy_registry_payload: Mapping[str, object] | None,
    logic_element_rows: object,
    logic_behavior_model_rows: object,
    logic_interface_signature_rows: object,
    logic_state_machine_rows: object,
    state_vector_definition_rows: object,
    state_vector_snapshot_rows: object,
    logic_fault_state_rows: object = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
    normalize_state_vector_snapshot_rows,
    state_vector_snapshot_rows_by_owner,
    deserialize_state,
    serialize_state,
    process_signal_set_fn,
    process_signal_emit_pulse_fn,
    signal_transport_state: Mapping[str, object] | None = None,
    arbitration_policy_registry_payload: Mapping[str, object] | None = None,
    error_detection_policy_registry_payload: Mapping[str, object] | None = None,
    loss_policy_registry_payload: Mapping[str, object] | None = None,
    routing_policy_registry_payload: Mapping[str, object] | None = None,
    attenuation_policy_registry_payload: Mapping[str, object] | None = None,
    belief_policy_registry_payload: Mapping[str, object] | None = None,
    temporal_domain_registry_payload: Mapping[str, object] | None = None,
    time_mapping_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
    model_type_registry_payload: Mapping[str, object] | None = None,
    constitutive_model_registry_payload: Mapping[str, object] | None = None,
    watchdog_definition_rows: object = None,
    session_scope_id: str = "session.default",
    compiled_model_rows: object = None,
    equivalence_proof_rows: object = None,
    validity_domain_rows: object = None,
    instrumentation_surface_registry_payload: Mapping[str, object] | None = None,
    access_policy_registry_payload: Mapping[str, object] | None = None,
    measurement_model_registry_payload: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    has_physical_access: bool = False,
    available_instrument_type_ids: object = None,
) -> dict:
    tick = int(max(0, as_int(current_tick, 0)))
    request = as_map(evaluation_request)
    network_id = token(request.get("network_id"))
    if not network_id:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND}

    network_state = as_map(logic_network_state)
    eval_state = normalize_logic_eval_state(logic_eval_state)
    bindings = _binding_by_network_id(network_state.get("logic_network_binding_rows"))
    binding_row = dict(bindings.get(network_id) or {})
    if not binding_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND,
            "logic_eval_state": eval_state,
            "signal_store_state": signal_store_state,
        }
    graph_id = token(binding_row.get("graph_id"))
    graph_row = dict(_graph_by_id(network_state.get("logic_network_graph_rows")).get(graph_id) or {})
    if not graph_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND,
            "logic_eval_state": eval_state,
            "signal_store_state": signal_store_state,
        }

    effective_signal_transport_state = dict(signal_transport_state or {})
    if "loss_policy_registry_payload" not in effective_signal_transport_state and loss_policy_registry_payload is not None:
        effective_signal_transport_state["loss_policy_registry_payload"] = loss_policy_registry_payload
    if "routing_policy_registry_payload" not in effective_signal_transport_state and routing_policy_registry_payload is not None:
        effective_signal_transport_state["routing_policy_registry_payload"] = routing_policy_registry_payload
    if "attenuation_policy_registry_payload" not in effective_signal_transport_state and attenuation_policy_registry_payload is not None:
        effective_signal_transport_state["attenuation_policy_registry_payload"] = attenuation_policy_registry_payload
    if "belief_policy_registry_payload" not in effective_signal_transport_state and belief_policy_registry_payload is not None:
        effective_signal_transport_state["belief_policy_registry_payload"] = belief_policy_registry_payload
    if "signal_trust_edge_rows" not in effective_signal_transport_state and "trust_edge_rows" in effective_signal_transport_state:
        effective_signal_transport_state["signal_trust_edge_rows"] = list(as_list(effective_signal_transport_state.get("trust_edge_rows")))
    if "belief_policy_id" not in effective_signal_transport_state:
        effective_signal_transport_state["belief_policy_id"] = "belief.default"

    protocol_transport_result = transport_logic_sig_receipts(
        current_tick=tick,
        signal_store_state=signal_store_state,
        signal_transport_state=effective_signal_transport_state,
        signal_type_registry_payload=signal_type_registry_payload,
        carrier_type_registry_payload=carrier_type_registry_payload,
        signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
        signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
        bus_encoding_registry_payload=bus_encoding_registry_payload,
        protocol_registry_payload=protocol_registry_payload,
        protocol_frame_rows=eval_state.get("logic_protocol_frame_rows"),
        protocol_event_record_rows=eval_state.get("logic_protocol_event_record_rows"),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        process_signal_set_fn=process_signal_set_fn,
    )
    updated_signal_store_state = protocol_transport_result.get("signal_store_state") or signal_store_state
    updated_signal_transport_state = dict(protocol_transport_result.get("signal_transport_state") or effective_signal_transport_state)
    eval_state["logic_protocol_frame_rows"] = list(
        protocol_transport_result.get("logic_protocol_frame_rows") or eval_state.get("logic_protocol_frame_rows") or []
    )
    eval_state["logic_protocol_event_record_rows"] = list(
        protocol_transport_result.get("logic_protocol_event_record_rows")
        or eval_state.get("logic_protocol_event_record_rows")
        or []
    )
    pre_protocol_runtime = arbitrate_logic_protocol_frames(
        current_tick=tick,
        protocol_frame_rows=eval_state.get("logic_protocol_frame_rows"),
        arbitration_state_rows=eval_state.get("logic_arbitration_state_rows"),
        protocol_event_record_rows=eval_state.get("logic_protocol_event_record_rows"),
        pending_signal_update_rows=eval_state.get("logic_pending_signal_update_rows"),
        signal_transport_state=updated_signal_transport_state,
        protocol_registry_payload=protocol_registry_payload,
        arbitration_policy_registry_payload=arbitration_policy_registry_payload,
        logic_security_policy_registry_payload=logic_security_policy_registry_payload,
    )
    pre_protocol_explain_rows = [dict(row) for row in as_list(pre_protocol_runtime.get("explain_artifact_rows")) if isinstance(row, Mapping)]
    pre_protocol_security_rows = [dict(row) for row in as_list(pre_protocol_runtime.get("logic_security_fail_rows")) if isinstance(row, Mapping)]
    eval_state["logic_protocol_frame_rows"] = list(pre_protocol_runtime.get("logic_protocol_frame_rows") or [])
    eval_state["logic_arbitration_state_rows"] = list(pre_protocol_runtime.get("logic_arbitration_state_rows") or [])
    eval_state["logic_protocol_event_record_rows"] = list(pre_protocol_runtime.get("logic_protocol_event_record_rows") or [])
    eval_state["logic_pending_signal_update_rows"] = list(pre_protocol_runtime.get("logic_pending_signal_update_rows") or [])
    updated_signal_transport_state = dict(pre_protocol_runtime.get("signal_transport_state") or updated_signal_transport_state)

    flush_result = flush_due_logic_signal_updates(
        current_tick=tick,
        signal_store_state=updated_signal_store_state,
        pending_signal_update_rows=eval_state.get("logic_pending_signal_update_rows"),
        propagation_trace_rows=eval_state.get("logic_propagation_trace_artifact_rows"),
        signal_type_registry_payload=signal_type_registry_payload,
        carrier_type_registry_payload=carrier_type_registry_payload,
        signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
        signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
        bus_encoding_registry_payload=bus_encoding_registry_payload,
        protocol_registry_payload=protocol_registry_payload,
        compute_runtime_state=eval_state.get("compute_runtime_state"),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        process_signal_set_fn=process_signal_set_fn,
        process_signal_emit_pulse_fn=process_signal_emit_pulse_fn,
    )
    updated_signal_store_state = flush_result.get("signal_store_state") or updated_signal_store_state
    eval_state["logic_pending_signal_update_rows"] = list(flush_result.get("logic_pending_signal_update_rows") or [])
    eval_state["logic_propagation_trace_artifact_rows"] = list(flush_result.get("logic_propagation_trace_artifact_rows") or [])
    eval_state["compute_runtime_state"] = dict(as_map(flush_result.get("compute_runtime_state")))

    runtime_rows = rows_by_id(eval_state.get("logic_network_runtime_state_rows"), "network_id")
    prior_runtime = dict(runtime_rows.get(network_id) or {})
    if prior_runtime and as_int(prior_runtime.get("last_evaluated_tick"), -1) >= tick:
        explain = build_explain_artifact(
            explain_id="explain.logic_timing_violation.{}".format(
                canonical_sha256({"tick": tick, "network_id": network_id, "kind": "duplicate_tick"})[:16]
            ),
            event_id="event.logic.timing_violation.{}".format(
                canonical_sha256({"tick": tick, "network_id": network_id, "kind": "duplicate_tick"})[:16]
            ),
            target_id=network_id,
            cause_chain=["cause.logic.duplicate_tick_evaluation"],
            remediation_hints=["evaluate a given network at most once per canonical tick"],
            extensions={"event_kind_id": "explain.logic_timing_violation"},
        )
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_TIMING_VIOLATION,
            "logic_eval_state": normalize_logic_eval_state(
                dict(eval_state, logic_network_runtime_state_rows=normalize_logic_network_runtime_state_rows(list(runtime_rows.values())))
            ),
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "explain_artifact_rows": [explain],
        }

    prior_runtime_extensions = as_map(prior_runtime.get("extensions"))
    if bool(prior_runtime_extensions.get("l1_timing_refused", False)) or bool(
        prior_runtime_extensions.get("requires_l2_timing", False)
    ):
        gate_reason = token(prior_runtime_extensions.get("timing_gate_reason")) or "timing_policy"
        explain_kind = (
            "explain.logic_oscillation"
            if gate_reason == "unstable_oscillation"
            else "explain.logic_timing_violation"
        )
        explain = build_explain_artifact(
            explain_id="explain.logic_timing_gate.{}".format(
                canonical_sha256({"tick": tick, "network_id": network_id, "reason": gate_reason})[:16]
            ),
            event_id="event.logic.timing_gate.{}".format(
                canonical_sha256({"tick": tick, "network_id": network_id, "reason": gate_reason})[:16]
            ),
            target_id=network_id,
            cause_chain=["cause.logic.timing_gate"],
            remediation_hints=[
                "route this network through future L2 timing or change the declared timing policy"
                if bool(prior_runtime_extensions.get("requires_l2_timing", False))
                else "resolve the unstable timing pattern before retrying L1 evaluation"
            ],
            extensions={"event_kind_id": explain_kind, "timing_gate_reason": gate_reason},
        )
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_TIMING_VIOLATION,
            "logic_eval_state": normalize_logic_eval_state(
                dict(eval_state, logic_network_runtime_state_rows=normalize_logic_network_runtime_state_rows(list(runtime_rows.values())))
            ),
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "explain_artifact_rows": [explain],
        }

    validation_record = _validation_record_for_network(network_state.get("logic_network_validation_records"), network_id)
    logic_network_policy_map = _logic_network_policy_rows_by_id(logic_network_policy_registry_payload)
    network_policy_row = dict(logic_network_policy_map.get(token(binding_row.get("policy_id"))) or {})
    logic_policy_id = (
        token(as_map(binding_row.get("extensions")).get("logic_policy_id"))
        or token(as_map(network_policy_row.get("extensions")).get("logic_policy_id"))
        or "logic.default"
    )
    logic_policy_map = _logic_policy_rows_by_id(logic_policy_registry_payload)
    logic_policy_row = dict(logic_policy_map.get(logic_policy_id) or logic_policy_map.get("logic.default") or {})

    if not _compiled_eval_validation_gate(
        binding_row=binding_row,
        validation_record=validation_record,
        network_policy_row=network_policy_row,
    ):
        explain = build_explain_artifact(
            explain_id="explain.logic_network_not_validated.{}".format(
                canonical_sha256({"tick": tick, "network_id": network_id})[:16]
            ),
            event_id="event.logic.network_not_validated.{}".format(
                canonical_sha256({"tick": tick, "network_id": network_id})[:16]
            ),
            target_id=network_id,
            cause_chain=["cause.logic.network.validation_required"],
            remediation_hints=["run process.logic_network_validate before L1 evaluation"],
            extensions={"event_kind_id": "explain.logic_command_refused"},
        )
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_NETWORK_NOT_VALIDATED,
            "logic_eval_state": eval_state,
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "explain_artifact_rows": [explain],
        }

    sense_snapshot = build_logic_sense_snapshot(
        current_tick=tick,
        network_id=network_id,
        graph_row=graph_row,
        signal_store_state=updated_signal_store_state,
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        interface_signature_rows=logic_interface_signature_rows,
        state_machine_rows=logic_state_machine_rows,
        logic_fault_state_rows=logic_fault_state_rows,
        logic_noise_policy_registry_payload=logic_noise_policy_registry_payload,
        logic_security_policy_registry_payload=logic_security_policy_registry_payload,
        evaluation_request=request,
    )
    noise_decision_rows = normalize_logic_noise_decision_rows(
        list(eval_state.get("logic_noise_decision_rows") or [])
        + [dict(row) for row in as_list(sense_snapshot.get("logic_noise_decision_rows")) if isinstance(row, Mapping)]
    )
    security_fail_rows = normalize_logic_security_fail_rows(
        list(eval_state.get("logic_security_fail_rows") or [])
        + pre_protocol_security_rows
        + [dict(row) for row in as_list(sense_snapshot.get("logic_security_fail_rows")) if isinstance(row, Mapping)]
    )
    sense_explain_rows = pre_protocol_explain_rows + [dict(row) for row in as_list(sense_snapshot.get("explain_artifact_rows")) if isinstance(row, Mapping)]
    sense_safety_rows = [dict(row) for row in as_list(sense_snapshot.get("safety_event_rows")) if isinstance(row, Mapping)]
    if token(sense_snapshot.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": token(sense_snapshot.get("reason_code")) or "refusal.logic.fault_invalid",
            "logic_eval_state": normalize_logic_eval_state(
                dict(
                    eval_state,
                    logic_noise_decision_rows=noise_decision_rows,
                    logic_security_fail_rows=security_fail_rows,
                )
            ),
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "sense_snapshot": sense_snapshot,
            "explain_artifact_rows": sense_explain_rows,
            "safety_event_rows": sense_safety_rows,
        }
    if bool(sense_snapshot.get("requires_l2_timing", False)):
        runtime_rows[network_id] = build_logic_network_runtime_state_row(
            network_id=network_id,
            last_evaluated_tick=as_int(prior_runtime.get("last_evaluated_tick"), 0),
            throttled=False,
            deterministic_fingerprint="",
            extensions={
                **as_map(prior_runtime.get("extensions")),
                "l1_timing_refused": True,
                "requires_l2_timing": bool(token(logic_policy_row.get("timing_mode")) == "roi_micro_optional"),
                "timing_gate_reason": "fault_requires_roi",
                "timing_status": "requires_l2" if token(logic_policy_row.get("timing_mode")) == "roi_micro_optional" else "l1_refused",
            },
        )
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_TIMING_VIOLATION,
            "logic_eval_state": normalize_logic_eval_state(
                dict(
                    eval_state,
                    logic_network_runtime_state_rows=normalize_logic_network_runtime_state_rows(list(runtime_rows.values())),
                    logic_noise_decision_rows=noise_decision_rows,
                    logic_security_fail_rows=security_fail_rows,
                )
            ),
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "sense_snapshot": sense_snapshot,
            "explain_artifact_rows": sense_explain_rows,
            "safety_event_rows": sense_safety_rows,
        }
    from src.logic.compile.logic_compiler import (
        REFUSAL_LOGIC_COMPILED_INVALID,
        build_logic_compiled_introspection_artifact,
        build_logic_compiled_forced_expand_event,
        build_logic_compiled_invalid_explain_artifact,
        execute_logic_compiled_model,
    )
    from src.logic.network.instrumentation_binding import authorize_logic_network_compiled_debug

    binding_extensions = as_map(binding_row.get("extensions"))
    compiled_model_id = token(binding_extensions.get("compiled_model_id"))
    debug_extensions = as_map(request.get("extensions"))
    debug_instrument_id = token(request.get("debug_instrument_id")) or token(debug_extensions.get("debug_instrument_id"))
    debug_force_expand_requested = bool(debug_extensions.get("debug_force_expand", False) or debug_instrument_id)
    debug_force_expand = False
    compiled_introspection_artifact_rows = []
    compiled_result = {}
    compiled_explain_rows = []
    forced_expand_rows = []
    compiled_runtime_ready = False
    if compiled_model_id:
        model_row = dict(rows_by_id(compiled_model_rows, "compiled_model_id").get(compiled_model_id) or {})
        if debug_force_expand_requested and model_row and debug_instrument_id:
            debug_gate = authorize_logic_network_compiled_debug(
                network_id=network_id,
                compiled_model_row=model_row,
                current_tick=tick,
                authority_context=authority_context,
                has_physical_access=bool(has_physical_access),
                available_instrument_type_ids=[token(item) for item in as_list(available_instrument_type_ids) if token(item)]
                or [debug_instrument_id],
                instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
                access_policy_registry_payload=access_policy_registry_payload,
                measurement_model_registry_payload=measurement_model_registry_payload,
            )
            debug_force_expand = token(debug_gate.get("result")) == "complete"
            if debug_force_expand:
                measurement_artifact = as_map(as_map(debug_gate.get("measurement_observation")).get("observation_artifact"))
                compiled_introspection_artifact_rows.append(
                    build_logic_compiled_introspection_artifact(
                        tick=tick,
                        network_id=network_id,
                        compiled_model_row=model_row,
                        measurement_artifact_id=token(measurement_artifact.get("artifact_id")),
                    )
                )
        if debug_force_expand:
            forced_expand_rows.append(
                build_logic_compiled_forced_expand_event(
                    capsule_id=_compiled_capsule_id(network_id),
                    tick=tick,
                    network_id=network_id,
                    reason_code="inspection_request",
                    compiled_model_id=compiled_model_id,
                )
            )
        else:
            compiled_result = execute_logic_compiled_model(
                current_tick=tick,
                network_id=network_id,
                binding_row=binding_row,
                validation_record=validation_record,
                sense_snapshot=sense_snapshot,
                state_vector_snapshot_rows=state_vector_snapshot_rows,
                state_vector_definition_rows=state_vector_definition_rows,
                compiled_model_rows=compiled_model_rows,
                equivalence_proof_rows=equivalence_proof_rows,
                validity_domain_rows=validity_domain_rows,
                compute_runtime_state=eval_state.get("compute_runtime_state"),
                compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
                compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
                compute_budget_profile_id=token(logic_policy_row.get("compute_profile_id")) or "compute.default",
                build_state_vector_definition_row=build_state_vector_definition_row,
                normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
                state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
                deserialize_state=deserialize_state,
            )
            compiled_runtime_ready = token(compiled_result.get("result")) in {"complete", "throttled"}
            if token(compiled_result.get("reason_code")) == REFUSAL_LOGIC_COMPILED_INVALID:
                compiled_validation = as_map(compiled_result.get("compiled_validation"))
                compiled_explain_rows.append(
                    build_logic_compiled_invalid_explain_artifact(
                        tick=tick,
                        network_id=network_id,
                        compiled_model_id=compiled_model_id,
                        violations=as_list(compiled_validation.get("violations")),
                    )
                )
                forced_expand_rows.append(
                    build_logic_compiled_forced_expand_event(
                        capsule_id=_compiled_capsule_id(network_id),
                        tick=tick,
                        network_id=network_id,
                        reason_code="logic.compiled_invalid",
                        compiled_model_id=compiled_model_id,
                    )
                )

    loop_gate = _loop_policy_refusal(
        current_tick=tick,
        network_id=network_id,
        validation_record=validation_record,
        network_policy_row=network_policy_row,
        compiled_runtime_ready=compiled_runtime_ready,
    )
    if token(loop_gate.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": token(loop_gate.get("reason_code")) or REFUSAL_LOGIC_EVAL_LOOP_POLICY,
            "logic_eval_state": eval_state,
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "explain_artifact_rows": list(compiled_explain_rows) + list(loop_gate.get("explain_artifact_rows") or []),
            "forced_expand_event_rows": forced_expand_rows,
            "compiled_introspection_artifact_rows": compiled_introspection_artifact_rows,
        }

    compiled_only_required = token(network_policy_row.get("loop_resolution_mode")).lower() == "allow_compiled_only"
    if compiled_model_id and token(compiled_result.get("reason_code")) == REFUSAL_LOGIC_COMPILED_INVALID and compiled_only_required:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_EVAL_LOOP_POLICY,
            "logic_eval_state": eval_state,
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
            "explain_artifact_rows": compiled_explain_rows,
            "forced_expand_event_rows": forced_expand_rows,
            "compiled_introspection_artifact_rows": compiled_introspection_artifact_rows,
        }

    compiled_path_selected = bool(compiled_runtime_ready and not debug_force_expand)
    compiled_fallback_logged = bool(
        compiled_model_id
        and token(compiled_result.get("reason_code")) == REFUSAL_LOGIC_COMPILED_INVALID
        and not compiled_only_required
    )

    if compiled_path_selected:
        compute_result = dict(compiled_result)
    else:
        compute_result = evaluate_logic_compute_phase(
            current_tick=tick,
            network_id=network_id,
            graph_row=graph_row,
            sense_snapshot=sense_snapshot,
            state_vector_definition_rows=state_vector_definition_rows,
            state_vector_snapshot_rows=state_vector_snapshot_rows,
            compute_runtime_state=eval_state.get("compute_runtime_state"),
            compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
            compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
            logic_policy_row=logic_policy_row,
            logic_element_rows=logic_element_rows,
            state_machine_rows=logic_state_machine_rows,
            build_state_vector_definition_row=build_state_vector_definition_row,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        )
    compute_result = attach_instance_definitions_to_compute_result(
        compute_result=compute_result,
        state_vector_definition_rows=compute_result.get("state_vector_definition_rows") or state_vector_definition_rows,
    )
    commit_result = commit_logic_state_updates(
        current_tick=tick,
        compute_result=compute_result,
        state_vector_definition_rows=compute_result.get("state_vector_definition_rows") or state_vector_definition_rows,
        state_vector_snapshot_rows=state_vector_snapshot_rows,
        process_statevec_update_fn=lambda **kwargs: process_statevec_update(
            **kwargs,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
            serialize_state=serialize_state,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        ),
    )
    if token(commit_result.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": token(commit_result.get("reason_code")),
            "logic_eval_state": eval_state,
            "signal_store_state": updated_signal_store_state,
            "signal_transport_state": updated_signal_transport_state,
        }
    propagation_result = schedule_logic_output_propagation(
        current_tick=tick,
        network_id=network_id,
        graph_row=graph_row,
        compute_result=compute_result,
        sense_snapshot=sense_snapshot,
        pending_signal_update_rows=eval_state.get("logic_pending_signal_update_rows"),
        protocol_frame_rows=eval_state.get("logic_protocol_frame_rows"),
        propagation_trace_rows=eval_state.get("logic_propagation_trace_artifact_rows"),
        protocol_registry_payload=protocol_registry_payload,
        temporal_domain_registry_payload=temporal_domain_registry_payload,
        time_mapping_registry_payload=time_mapping_registry_payload,
        drift_policy_registry_payload=drift_policy_registry_payload,
        model_type_registry_payload=model_type_registry_payload,
        constitutive_model_registry_payload=constitutive_model_registry_payload,
        session_scope_id=session_scope_id,
    )
    post_protocol_runtime = arbitrate_logic_protocol_frames(
        current_tick=tick,
        protocol_frame_rows=propagation_result.get("logic_protocol_frame_rows"),
        arbitration_state_rows=eval_state.get("logic_arbitration_state_rows"),
        protocol_event_record_rows=eval_state.get("logic_protocol_event_record_rows"),
        pending_signal_update_rows=propagation_result.get("logic_pending_signal_update_rows"),
        signal_transport_state=updated_signal_transport_state,
        protocol_registry_payload=protocol_registry_payload,
        arbitration_policy_registry_payload=arbitration_policy_registry_payload,
        logic_security_policy_registry_payload=logic_security_policy_registry_payload,
    )
    propagation_result = dict(
        propagation_result,
        logic_pending_signal_update_rows=post_protocol_runtime.get("logic_pending_signal_update_rows"),
        logic_protocol_frame_rows=post_protocol_runtime.get("logic_protocol_frame_rows"),
    )
    updated_signal_transport_state = dict(post_protocol_runtime.get("signal_transport_state") or updated_signal_transport_state)
    post_protocol_explain_rows = [dict(row) for row in as_list(post_protocol_runtime.get("explain_artifact_rows")) if isinstance(row, Mapping)]
    post_protocol_security_rows = [dict(row) for row in as_list(post_protocol_runtime.get("logic_security_fail_rows")) if isinstance(row, Mapping)]

    throttle_event_rows = list(eval_state.get("logic_throttle_event_rows") or [])
    oscillation_record_rows = list(eval_state.get("logic_oscillation_record_rows") or [])
    timing_violation_event_rows = list(eval_state.get("logic_timing_violation_event_rows") or [])
    watchdog_timeout_event_rows = list(eval_state.get("logic_watchdog_timeout_event_rows") or [])
    network_timing_violation_rows = []
    explain_rows = list(sense_explain_rows) + list(compiled_explain_rows) + list(post_protocol_explain_rows)
    timing_compute_units_used = 0
    for event in as_list(compute_result.get("throttle_events")):
        if not isinstance(event, Mapping):
            continue
        throttle_row = build_logic_throttle_event_row(
            tick=as_int(event.get("tick"), tick),
            network_id=token(event.get("network_id")) or network_id,
            reason=token(event.get("reason")) or "budget_exceeded",
            deterministic_fingerprint="",
            extensions=as_map(event.get("extensions")),
        )
        if throttle_row:
            throttle_event_rows.append(throttle_row)
            explain_rows.append(
                build_explain_artifact(
                    explain_id="explain.logic_compute_throttle.{}".format(
                        canonical_sha256({"event_id": throttle_row.get("event_id")})[:16]
                    ),
                    event_id=token(throttle_row.get("event_id")),
                    target_id=network_id,
                    cause_chain=["cause.logic.compute_budget"],
                    remediation_hints=["raise compute profile budget or reduce active logic controller count"],
                    extensions={
                        "event_kind_id": "explain.logic_compute_throttle",
                        "throttle_event_id": token(throttle_row.get("event_id")),
                    },
                )
            )

    timing_compute_request = request_logic_timing_compute(
        current_tick=tick,
        network_id=network_id,
        phase="analysis",
        instruction_units=int(max(1, as_int(as_map(logic_policy_row.get("extensions")).get("timing_analysis_compute_units", 4), 4))),
        compute_runtime_state=compute_result.get("compute_runtime_state"),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=token(logic_policy_row.get("compute_profile_id")) or "compute.default",
    )
    timing_analysis_allowed = token(timing_compute_request.get("result")) not in {"deferred", "refused", "shutdown"}
    timing_compute_units_used = int(max(0, as_int(timing_compute_request.get("approved_instruction_units", 0), 0)))
    timing_compute_state = as_map(timing_compute_request.get("runtime_state"))
    compute_result = dict(
        compute_result,
        compute_runtime_state=timing_compute_state,
        compute_units_used=int(max(0, as_int(compute_result.get("compute_units_used"), 0)) + int(timing_compute_units_used)),
        network_throttled=bool(compute_result.get("network_throttled", False) or (not timing_analysis_allowed)),
    )
    if token(timing_compute_request.get("result")) in {"deferred", "refused", "shutdown"}:
        throttle_row = build_logic_throttle_event_row(
            tick=tick,
            network_id=network_id,
            reason="budget_exceeded",
            deterministic_fingerprint="",
            extensions={
                "phase": "timing.analysis",
                "reason_code": token(timing_compute_request.get("reason_code")) or "refusal.compute.budget_exceeded",
            },
        )
        if throttle_row:
            throttle_event_rows.append(throttle_row)
            explain_rows.append(
                build_explain_artifact(
                    explain_id="explain.logic_compute_throttle.{}".format(
                        canonical_sha256({"event_id": throttle_row.get("event_id"), "phase": "timing.analysis"})[:16]
                    ),
                    event_id=token(throttle_row.get("event_id")),
                    target_id=network_id,
                    cause_chain=["cause.logic.compute_budget"],
                    remediation_hints=["raise compute profile budget or reduce timing-analysis load"],
                    extensions={
                        "event_kind_id": "explain.logic_compute_throttle",
                        "throttle_event_id": token(throttle_row.get("event_id")),
                    },
                )
            )

    oscillation_result = {"runtime_extensions": {}, "classification": {}, "oscillation_record_rows": [], "explain_artifact_rows": []}
    timing_enforcement = {"runtime_extensions": {}, "timing_violation_events": [], "explain_artifact_rows": []}
    watchdog_transitions = []
    if timing_analysis_allowed:
        oscillation_result = detect_network_oscillation(
            current_tick=tick,
            network_id=network_id,
            graph_row=graph_row,
            signal_store_state=updated_signal_store_state,
            pending_signal_update_rows=propagation_result.get("logic_pending_signal_update_rows"),
            state_vector_snapshot_rows=commit_result.get("state_vector_snapshot_rows") or state_vector_snapshot_rows,
            runtime_row=prior_runtime,
            logic_policy_row=logic_policy_row,
        )
        for row in as_list(oscillation_result.get("oscillation_record_rows")):
            if not isinstance(row, Mapping):
                continue
            record = build_logic_oscillation_record_row(
                tick=as_int(row.get("tick"), tick),
                network_id=token(row.get("network_id")) or network_id,
                period_ticks=as_int(row.get("period_ticks"), 1),
                stable=bool(row.get("stable", False)),
                deterministic_fingerprint="",
                extensions=as_map(row.get("extensions")),
            )
            if record:
                oscillation_record_rows.append(record)
        explain_rows.extend(
            [dict(row) for row in as_list(oscillation_result.get("explain_artifact_rows")) if isinstance(row, Mapping)]
        )

        timing_enforcement = evaluate_logic_timing_constraints(
            current_tick=tick,
            network_id=network_id,
            binding_row=binding_row,
            logic_policy_row=logic_policy_row,
            propagation_result=propagation_result,
            oscillation_classification=as_map(oscillation_result.get("classification")),
        )
        watchdog_transitions = detect_watchdog_timeout_transitions(
            current_tick=tick,
            network_id=network_id,
            compute_result=compute_result,
            logic_element_rows=logic_element_rows,
            watchdog_definition_rows=watchdog_definition_rows,
        )
    else:
        timing_enforcement = {
            "runtime_extensions": {
                "timing_status": "analysis_deferred",
                "timing_analysis_deferred": True,
            },
            "timing_violation_events": [],
            "explain_artifact_rows": [],
        }
    for event in as_list(timing_enforcement.get("timing_violation_events")):
        if not isinstance(event, Mapping):
            continue
        timing_row = build_logic_timing_violation_event_row(
            tick=as_int(event.get("tick"), tick),
            network_id=token(event.get("network_id")) or network_id,
            reason=token(event.get("reason")) or "max_propagation_ticks_exceeded",
            deterministic_fingerprint="",
            extensions=as_map(event.get("extensions")),
        )
        if timing_row:
            timing_violation_event_rows.append(timing_row)
            network_timing_violation_rows.append(timing_row)
    explain_rows.extend(
        [dict(row) for row in as_list(timing_enforcement.get("explain_artifact_rows")) if isinstance(row, Mapping)]
    )
    for event in as_list(watchdog_transitions):
        if not isinstance(event, Mapping):
            continue
        watchdog_row = build_logic_watchdog_timeout_event_row(
            tick=as_int(event.get("tick"), tick),
            network_id=token(event.get("network_id")) or network_id,
            watchdog_id=token(event.get("watchdog_id")),
            action_on_timeout=token(event.get("action_on_timeout")) or "signal_set",
            deterministic_fingerprint="",
            extensions=as_map(event.get("extensions")),
        )
        if not watchdog_row:
            continue
        watchdog_timeout_event_rows.append(watchdog_row)
        explain_rows.append(
            build_explain_artifact(
                explain_id="explain.watchdog_timeout.{}".format(
                    canonical_sha256({"event_id": watchdog_row.get("event_id")})[:16]
                ),
                event_id=token(watchdog_row.get("event_id")),
                target_id=network_id,
                cause_chain=["cause.logic.watchdog_timeout"],
                remediation_hints=["inspect the monitored signal path or widen the declared timeout window"],
                extensions={
                    "event_kind_id": "explain.watchdog_timeout",
                    "watchdog_timeout_event_id": token(watchdog_row.get("event_id")),
                    "watchdog_id": token(watchdog_row.get("watchdog_id")),
                },
            )
        )

    policy_extensions = as_map(logic_policy_row.get("extensions"))
    oscillation_classification = as_map(oscillation_result.get("classification"))
    combined_runtime_extensions = dict(as_map(oscillation_result.get("runtime_extensions")))
    combined_runtime_extensions.update(as_map(timing_enforcement.get("runtime_extensions")))
    if oscillation_classification and not bool(oscillation_classification.get("stable", False)):
        unstable_action = token(policy_extensions.get("unstable_oscillation_action")) or "force_roi"
        timing_mode = token(logic_policy_row.get("timing_mode")) or "sync_tick"
        if unstable_action == "refuse" or (unstable_action == "force_roi" and timing_mode != "roi_micro_optional"):
            combined_runtime_extensions.update(
                {
                    "l1_timing_refused": True,
                    "requires_l2_timing": False,
                    "timing_gate_reason": "unstable_oscillation",
                    "timing_status": "l1_refused",
                }
            )
        elif unstable_action == "force_roi":
            combined_runtime_extensions.update(
                {
                    "l1_timing_refused": False,
                    "requires_l2_timing": True,
                    "timing_gate_reason": "unstable_oscillation",
                    "timing_status": "requires_l2",
                }
            )
        if unstable_action in {"refuse", "force_roi"}:
            timing_row = build_logic_timing_violation_event_row(
                tick=tick,
                network_id=network_id,
                reason="unstable_oscillation",
                deterministic_fingerprint="",
                extensions={
                    "policy_action": unstable_action,
                    "timing_mode": timing_mode,
                    "oscillation_classification": canon(oscillation_classification),
                },
            )
            if timing_row:
                timing_violation_event_rows.append(timing_row)
                network_timing_violation_rows.append(timing_row)

    timing_violation_action = token(policy_extensions.get("timing_violation_action")) or "force_roi"
    timing_mode = token(logic_policy_row.get("timing_mode")) or "sync_tick"
    if network_timing_violation_rows:
        if timing_violation_action == "refuse":
            combined_runtime_extensions.update(
                {
                    "l1_timing_refused": True,
                    "requires_l2_timing": False,
                    "timing_gate_reason": "timing_violation",
                    "timing_status": "l1_refused",
                }
            )
        elif timing_violation_action == "force_roi":
            if timing_mode == "roi_micro_optional":
                combined_runtime_extensions.update(
                    {
                        "l1_timing_refused": False,
                        "requires_l2_timing": True,
                        "timing_gate_reason": "timing_violation",
                        "timing_status": "requires_l2",
                    }
                )
            else:
                combined_runtime_extensions.update(
                    {
                        "l1_timing_refused": True,
                        "requires_l2_timing": False,
                        "timing_gate_reason": "timing_violation",
                        "timing_status": "l1_refused",
                    }
                )
        elif timing_violation_action == "throttle":
            compute_result = dict(compute_result, network_throttled=True)
            combined_runtime_extensions.update(
                {
                    "l1_timing_refused": False,
                    "requires_l2_timing": False,
                    "timing_gate_reason": "timing_violation",
                    "timing_status": "throttled",
                }
            )

    security_fail_rows = normalize_logic_security_fail_rows(list(security_fail_rows) + post_protocol_security_rows)

    runtime_rows[network_id] = build_logic_network_runtime_state_row(
        network_id=network_id,
        last_evaluated_tick=tick,
        throttled=bool(compute_result.get("network_throttled", False)),
        deterministic_fingerprint="",
        extensions={
            "snapshot_hash": token(sense_snapshot.get("snapshot_hash")),
            "scheduled_outputs": int(propagation_result.get("scheduled_count", 0)),
            "delivered_inputs": int(flush_result.get("delivered_count", 0)),
            "protocol_frame_count": int(len(list(propagation_result.get("logic_protocol_frame_rows") or []))),
            "protocol_event_count": int(len(list(post_protocol_runtime.get("logic_protocol_event_record_rows") or []))),
            "compiled_model_id": compiled_model_id or None,
            "compiled_path_selected": compiled_path_selected,
            "compiled_fallback_logged": compiled_fallback_logged,
            "debug_force_expand": bool(debug_force_expand),
            "debug_instrument_id": debug_instrument_id or None,
            **combined_runtime_extensions,
        },
    )
    eval_record_rows = list(eval_state.get("logic_eval_record_rows") or []) + [
        build_logic_eval_record_row(
            tick=tick,
            network_id=network_id,
            elements_evaluated_count=as_int(compute_result.get("elements_evaluated_count"), 0),
            compute_units_used=as_int(compute_result.get("compute_units_used"), 0),
            throttled=bool(compute_result.get("network_throttled", False)),
            deterministic_fingerprint="",
            extensions={
                "scheduled_outputs": int(propagation_result.get("scheduled_count", 0)),
                "delivered_inputs": int(flush_result.get("delivered_count", 0)),
                "protocol_frame_count": int(len(list(propagation_result.get("logic_protocol_frame_rows") or []))),
                "protocol_event_count": int(len(list(post_protocol_runtime.get("logic_protocol_event_record_rows") or []))),
                "timing_violation_count": int(len(timing_violation_event_rows)),
                "timing_compute_units_used": int(timing_compute_units_used),
                "max_propagation_delay_ticks": int(propagation_result.get("max_propagation_delay_ticks", 0)),
                "compiled_model_id": compiled_model_id or None,
                "compiled_path_selected": compiled_path_selected,
                "compiled_fallback_logged": compiled_fallback_logged,
                "debug_force_expand": bool(debug_force_expand),
                "debug_instrument_id": debug_instrument_id or None,
            },
        )
    ]
    next_eval_state = normalize_logic_eval_state(
        {
            "logic_network_runtime_state_rows": list(runtime_rows.values()),
            "logic_eval_record_rows": eval_record_rows,
            "logic_throttle_event_rows": normalize_logic_throttle_event_rows(throttle_event_rows),
            "logic_oscillation_record_rows": normalize_logic_oscillation_record_rows(oscillation_record_rows),
            "logic_timing_violation_event_rows": normalize_logic_timing_violation_event_rows(timing_violation_event_rows),
            "logic_watchdog_timeout_event_rows": normalize_logic_watchdog_timeout_event_rows(watchdog_timeout_event_rows),
            "logic_state_update_record_rows": list(commit_result.get("state_update_record_rows") or []),
            "logic_noise_decision_rows": noise_decision_rows,
            "logic_security_fail_rows": security_fail_rows,
            "logic_protocol_frame_rows": propagation_result.get("logic_protocol_frame_rows"),
            "logic_arbitration_state_rows": post_protocol_runtime.get("logic_arbitration_state_rows"),
            "logic_protocol_event_record_rows": post_protocol_runtime.get("logic_protocol_event_record_rows"),
            "logic_pending_signal_update_rows": propagation_result.get("logic_pending_signal_update_rows"),
            "logic_propagation_trace_artifact_rows": propagation_result.get("logic_propagation_trace_artifact_rows"),
            "compute_runtime_state": compute_result.get("compute_runtime_state"),
        }
    )
    return {
        "result": "complete" if token(compute_result.get("result")) == "complete" else "throttled",
        "reason_code": token(compute_result.get("reason_code")),
        "logic_eval_state": next_eval_state,
        "signal_store_state": updated_signal_store_state,
        "signal_transport_state": updated_signal_transport_state,
        "state_vector_definition_rows": list(commit_result.get("state_vector_definition_rows") or state_vector_definition_rows),
        "state_vector_snapshot_rows": list(commit_result.get("state_vector_snapshot_rows") or state_vector_snapshot_rows),
        "sense_snapshot": sense_snapshot,
        "compute_result": compute_result,
        "eval_record_row": dict(eval_record_rows[-1]),
        "throttle_event_rows": normalize_logic_throttle_event_rows(throttle_event_rows),
        "explain_artifact_rows": explain_rows,
        "forced_expand_event_rows": forced_expand_rows,
        "compiled_introspection_artifact_rows": compiled_introspection_artifact_rows,
        "safety_event_rows": sense_safety_rows,
    }


__all__ = [
    "PROCESS_LOGIC_NETWORK_EVALUATE",
    "PROCESS_STATEVEC_UPDATE",
    "REFUSAL_LOGIC_EVAL_LOOP_POLICY",
    "REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND",
    "REFUSAL_LOGIC_EVAL_NETWORK_NOT_VALIDATED",
    "REFUSAL_LOGIC_EVAL_TIMING_VIOLATION",
    "normalize_logic_eval_state",
    "process_logic_network_evaluate",
    "process_statevec_update",
]
