"""LOGIC-4 COMPUTE phase evaluation."""

from __future__ import annotations

from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.logic.element.compute_hooks import request_logic_element_compute
from .common import (
    as_int,
    as_list,
    as_map,
    default_state_for_definition,
    evaluate_expression,
    fixed_ticks_for_element,
    materialize_logic_instance_state_definition,
    rows_by_id,
    signal_type_id_for_port,
    token,
    to_value_payload,
)


def _state_machine_transition_order(transition_rules: object) -> list[dict]:
    return [
        dict(row)
        for row in as_list(transition_rules)
        if isinstance(row, Mapping)
    ]


def _normalize_assignments(assignments: object) -> list[str]:
    return [str(item).strip() for item in as_list(assignments) if str(item).strip()]


def _evaluate_assignment(
    *,
    assignment: str,
    inputs: Mapping[str, Mapping[str, object]],
    state_values: Mapping[str, object],
    delay_fixed_ticks: int,
) -> tuple[str, object]:
    if "=" not in assignment:
        return "", None
    field_id, expression = assignment.split("=", 1)
    return str(field_id).strip(), evaluate_expression(
        expression=str(expression).strip(),
        inputs=inputs,
        state_values=state_values,
        delay_fixed_ticks=delay_fixed_ticks,
    )


def _evaluate_state_machine(
    *,
    current_state: Mapping[str, object],
    inputs: Mapping[str, Mapping[str, object]],
    state_machine_row: Mapping[str, object],
    delay_fixed_ticks: int,
) -> tuple[dict, dict]:
    state_values = dict(default_state_for_definition({"state_fields": []}))
    state_values.update(dict(as_map(current_state)))
    current_state_id = token(state_values.get("logic_state_id"))
    if not current_state_id:
        state_ids = [token(row.get("state_id")) for row in as_list(as_map(state_machine_row).get("states")) if isinstance(row, Mapping)]
        current_state_id = state_ids[0] if state_ids else ""
        if current_state_id:
            state_values["logic_state_id"] = current_state_id
    next_state = dict(state_values)
    next_state_id = current_state_id
    for rule in _state_machine_transition_order(as_map(state_machine_row).get("transition_rules")):
        if current_state_id and token(rule.get("from_state_id")) not in {"", current_state_id}:
            continue
        guard = evaluate_expression(
            expression=token(rule.get("guard_expression")) or "0",
            inputs=inputs,
            state_values=next_state,
            delay_fixed_ticks=delay_fixed_ticks,
        )
        if not bool(as_int(guard, 0)):
            continue
        for assignment in _normalize_assignments(rule.get("state_assignments")):
            field_id, value = _evaluate_assignment(
                assignment=assignment,
                inputs=inputs,
                state_values=next_state,
                delay_fixed_ticks=delay_fixed_ticks,
            )
            if field_id:
                next_state[field_id] = value
        next_state_id = token(rule.get("to_state_id")) or next_state_id
        break
    if next_state_id:
        next_state["logic_state_id"] = next_state_id
    outputs: Dict[str, object] = {}
    for output_rule in sorted((dict(item) for item in as_list(as_map(state_machine_row).get("output_rules")) if isinstance(item, Mapping)), key=lambda item: token(item.get("rule_id"))):
        port_id = token(output_rule.get("port_id"))
        if not port_id:
            continue
        outputs[port_id] = evaluate_expression(
            expression=token(output_rule.get("expression")) or "0",
            inputs=inputs,
            state_values=next_state,
            delay_fixed_ticks=delay_fixed_ticks,
        )
    return next_state, outputs


def _evaluate_combinational_outputs(
    *,
    behavior_row: Mapping[str, object],
    inputs: Mapping[str, Mapping[str, object]],
    state_values: Mapping[str, object],
    delay_fixed_ticks: int,
) -> dict:
    out: Dict[str, object] = {}
    model_ref = as_map(behavior_row.get("model_ref"))
    for output_row in sorted((dict(item) for item in as_list(model_ref.get("outputs")) if isinstance(item, Mapping)), key=lambda item: token(item.get("port_id"))):
        port_id = token(output_row.get("port_id"))
        if not port_id:
            continue
        out[port_id] = evaluate_expression(
            expression=token(output_row.get("expression")) or "0",
            inputs=inputs,
            state_values=state_values,
            delay_fixed_ticks=delay_fixed_ticks,
        )
    return out


def evaluate_logic_compute_phase(
    *,
    current_tick: int,
    network_id: str,
    graph_row: Mapping[str, object],
    sense_snapshot: Mapping[str, object],
    state_vector_definition_rows: object,
    state_vector_snapshot_rows: object,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    logic_policy_row: Mapping[str, object],
    logic_element_rows: object,
    state_machine_rows: object,
    build_state_vector_definition_row,
    state_vector_snapshot_rows_by_owner,
    deserialize_state,
    normalize_state_vector_definition_rows,
) -> dict:
    graph = as_map(graph_row)
    snapshot = as_map(sense_snapshot)
    state_machine_by_id = rows_by_id(state_machine_rows, "sm_id")
    snapshot_by_owner = state_vector_snapshot_rows_by_owner(state_vector_snapshot_rows)
    definition_rows = normalize_state_vector_definition_rows(state_vector_definition_rows)
    definition_by_owner = rows_by_id(definition_rows, "owner_id")
    compute_profile_id = token(logic_policy_row.get("compute_profile_id")) or "compute.default"
    network_compute_cap_units = as_int(as_map(logic_policy_row.get("extensions")).get("network_compute_cap_units"), 0)

    results = []
    throttle_events = []
    compute_state = as_map(compute_runtime_state)
    total_compute_units = 0
    network_throttled = False
    stop_reason = ""

    for element in snapshot.get("elements") or []:
        element_row = dict(as_map(element.get("element_row")))
        interface_row = dict(as_map(element.get("interface_row")))
        behavior_row = dict(as_map(element.get("behavior_row")))
        state_machine_row = dict(as_map(element.get("state_machine_row")))
        element_instance_id = token(element.get("element_instance_id"))
        element_definition_id = token(element.get("element_definition_id"))
        model_kind = token(behavior_row.get("model_kind")).lower() or "combinational"
        delay_fixed_ticks = fixed_ticks_for_element(
            element_row=element_row,
            interface_row=interface_row,
            graph_node_payload=next(iter(dict(element.get("input_ports") or {}).values()), {}),
        )
        instance_definition = materialize_logic_instance_state_definition(
            element_instance_id=element_instance_id,
            element_definition_id=element_definition_id,
            model_kind=model_kind,
            state_machine_row=state_machine_row,
            state_vector_definition_rows=definition_rows,
            build_state_vector_definition_row=build_state_vector_definition_row,
        )
        if instance_definition and token(instance_definition.get("owner_id")) not in definition_by_owner:
            definition_rows = normalize_state_vector_definition_rows(list(definition_rows) + [instance_definition])
            definition_by_owner = rows_by_id(definition_rows, "owner_id")

        current_state = default_state_for_definition(instance_definition)
        current_snapshot = dict(snapshot_by_owner.get(element_instance_id) or {})
        if current_snapshot:
            restored = deserialize_state(
                snapshot_row=current_snapshot,
                state_vector_definition_rows=definition_rows,
                expected_version=token(current_snapshot.get("version")) or None,
            )
            if token(restored.get("result")) == "complete":
                current_state = dict(restored.get("restored_state") or {})

        compute_request = request_logic_element_compute(
            current_tick=current_tick,
            element_row=element_row,
            state_vector_definition_rows=definition_rows,
            compute_runtime_state=compute_state,
            compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
            compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
            compute_budget_profile_id=compute_profile_id,
            network_id=network_id,
        )
        compute_state = as_map(compute_request.get("runtime_state"))
        approved_units = int(max(0, as_int(compute_request.get("approved_instruction_units"), 0)))
        total_compute_units += approved_units
        if token(compute_request.get("result")) == "throttled":
            network_throttled = True
            throttle_events.append(
                {
                    "tick": int(current_tick),
                    "network_id": network_id,
                    "reason": "budget_exceeded",
                    "extensions": {
                        "element_instance_id": element_instance_id,
                        "compute_result": token(compute_request.get("result")),
                        "reason_code": token(compute_request.get("reason_code")),
                    },
                }
            )
        if network_compute_cap_units > 0 and total_compute_units > network_compute_cap_units:
            network_throttled = True
            stop_reason = "budget_exceeded"
            throttle_events.append(
                {
                    "tick": int(current_tick),
                    "network_id": network_id,
                    "reason": "budget_exceeded",
                    "extensions": {
                        "element_instance_id": element_instance_id,
                        "cap_kind": "per_network",
                        "network_compute_cap_units": int(network_compute_cap_units),
                        "compute_units_used": int(total_compute_units),
                    },
                }
            )
            break
        if token(compute_request.get("result")) not in {"complete", "throttled"}:
            network_throttled = True
            stop_reason = token(compute_request.get("reason_code")) or "budget_exceeded"
            throttle_events.append(
                {
                    "tick": int(current_tick),
                    "network_id": network_id,
                    "reason": "budget_exceeded",
                    "extensions": {
                        "element_instance_id": element_instance_id,
                        "compute_result": token(compute_request.get("result")),
                        "reason_code": token(compute_request.get("reason_code")),
                    },
                }
            )
            break

        inputs = dict((str(port_id), dict(value_ref)) for port_id, value_ref in dict(snapshot.get("inputs_by_element", {}).get(element_instance_id) or {}).items())
        if model_kind in {"sequential", "timer", "counter"}:
            current_state.setdefault(
                "logic_state_id",
                token(next((row.get("state_id") for row in as_list(state_machine_row.get("states")) if isinstance(row, Mapping)), "")),
            )
            next_state, raw_outputs = _evaluate_state_machine(
                current_state=current_state,
                inputs=inputs,
                state_machine_row=state_machine_row or state_machine_by_id.get(token(as_map(behavior_row.get("model_ref")).get("ref_id"))) or {},
                delay_fixed_ticks=delay_fixed_ticks,
            )
        else:
            next_state = dict(current_state)
            raw_outputs = _evaluate_combinational_outputs(
                behavior_row=behavior_row,
                inputs=inputs,
                state_values=current_state,
                delay_fixed_ticks=delay_fixed_ticks,
            )
        output_payloads: Dict[str, dict] = {}
        for port_id, port_row in dict(element.get("output_ports") or {}).items():
            node_id = token(as_map(port_row).get("node_id"))
            signal_type_id = signal_type_id_for_port(
                node_id=node_id,
                direction="out",
                graph_row=graph,
                element_row=element_row,
                interface_row=interface_row,
            )
            output_payloads[port_id] = {
                "signal_type_id": signal_type_id,
                "value_payload": to_value_payload(
                    signal_type_id=signal_type_id,
                    evaluated_value=raw_outputs.get(port_id, 0),
                ),
            }
        results.append(
            {
                "element_instance_id": element_instance_id,
                "element_definition_id": element_definition_id,
                "model_kind": model_kind,
                "next_state": next_state,
                "current_state": current_state,
                "output_payloads": output_payloads,
                "compute_request": dict(compute_request),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "element_instance_id": element_instance_id,
                        "model_kind": model_kind,
                        "next_state": next_state,
                        "output_payloads": output_payloads,
                    }
                ),
            }
        )

    return {
        "result": "complete" if not stop_reason else "throttled",
        "reason_code": stop_reason,
        "element_results": results,
        "compute_runtime_state": compute_state,
        "compute_units_used": int(total_compute_units),
        "elements_evaluated_count": int(len(results)),
        "network_throttled": bool(network_throttled),
        "throttle_events": throttle_events,
        "state_vector_definition_rows": definition_rows,
    }


__all__ = [
    "evaluate_logic_compute_phase",
]
