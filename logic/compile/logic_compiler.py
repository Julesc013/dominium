"""LOGIC-6 deterministic compiler and compiled execution helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from meta.compile import (
    REFUSAL_COMPILE_MISSING_PROOF,
    build_compile_request_row,
    build_compile_result_row,
    build_compiled_model_row,
    build_validity_domain_row,
    compiled_type_rows_by_id,
    equivalence_proof_rows_by_id,
    validity_domain_rows_by_id,
)
from meta.compute import request_compute
from meta.explain import build_explain_artifact
from system import (
    build_interface_signature_row,
    build_system_macro_capsule_row,
    normalize_system_rows,
)
from system.macro import build_forced_expand_event_row
from tools.xstack.compatx.canonical_json import canonical_sha256

from logic.eval.common import (
    as_int,
    as_list,
    as_map,
    canon,
    default_state_for_definition,
    evaluate_expression,
    fixed_ticks_for_element,
    materialize_logic_instance_state_definition,
    rows_by_id,
    signal_type_id_for_port,
    token,
    to_value_payload,
    value_ref_to_scalar,
)
from logic.eval.sense_engine import build_logic_element_index
from logic.compile.logic_proof_engine import (
    build_logic_equivalence_proof_row,
    verify_logic_equivalence_proof,
)


PROCESS_LOGIC_COMPILE_REQUEST = "process.logic_compile_request"

REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND = "refusal.logic.compile.network_not_found"
REFUSAL_LOGIC_COMPILE_NETWORK_NOT_VALIDATED = "refusal.logic.compile.network_not_validated"
REFUSAL_LOGIC_COMPILE_POLICY_UNREGISTERED = "refusal.logic.compile.policy_unregistered"
REFUSAL_LOGIC_COMPILE_INELIGIBLE = "refusal.logic.compile.ineligible"
REFUSAL_LOGIC_COMPILED_INVALID = "refusal.logic.compiled_invalid"

_BOOLEANISH_SIGNAL_TYPES = {"signal.boolean", "signal.pulse"}
_SEQUENTIAL_MODEL_KINDS = {"sequential", "timer", "counter"}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(token(item) for item in list(values or []) if token(item)))


def _binding_by_network_id(rows: object) -> Dict[str, dict]:
    return rows_by_id(rows, "network_id")


def _graph_by_id(rows: object) -> Dict[str, dict]:
    return rows_by_id(rows, "graph_id")


def _validation_record_for_network(rows: object, network_id: str) -> dict:
    selected = {}
    for row in sorted(
        (dict(item) for item in as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, as_int(item.get("validation_tick", item.get("tick", 0)), 0))),
            token(item.get("network_id")),
            token(item.get("validation_hash")),
        ),
    ):
        if token(row.get("network_id")) == token(network_id):
            selected = dict(row)
    return selected


def _rows_from_registry_payload(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
    body = as_map(payload)
    for key in keys:
        rows = body.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = as_map(body.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def build_logic_compile_policy_row(
    *,
    compile_policy_id: str,
    preferred_verification_procedure_id: str,
    allow_bounded_error: bool,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    policy_id = token(compile_policy_id)
    verifier_id = token(preferred_verification_procedure_id)
    if (not policy_id) or (not verifier_id):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "compile_policy_id": policy_id,
        "preferred_verification_procedure_id": verifier_id,
        "allow_bounded_error": bool(allow_bounded_error),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_compile_policy_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: token(item.get("compile_policy_id")),
    ):
        normalized = build_logic_compile_policy_row(
            compile_policy_id=token(row.get("compile_policy_id")),
            preferred_verification_procedure_id=token(row.get("preferred_verification_procedure_id")),
            allow_bounded_error=bool(row.get("allow_bounded_error", False)),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        policy_id = token(normalized.get("compile_policy_id"))
        if policy_id:
            out[policy_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def logic_compile_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = normalize_logic_compile_policy_rows(_rows_from_registry_payload(registry_payload, ("logic_compile_policies",)))
    return dict((token(row.get("compile_policy_id")), dict(row)) for row in rows if token(row.get("compile_policy_id")))


def _logic_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return rows_by_id(_rows_from_registry_payload(payload, ("logic_policies",)), "policy_id")


def _logic_network_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return rows_by_id(_rows_from_registry_payload(payload, ("logic_network_policies",)), "policy_id")


def _edge_payloads_for_node(*, graph_row: Mapping[str, object], node_id: str, direction: str) -> List[dict]:
    out: List[dict] = []
    graph = as_map(graph_row)
    for edge in sorted(
        (dict(item) for item in as_list(graph.get("edges")) if isinstance(item, Mapping)),
        key=lambda item: (token(item.get("edge_id")), token(item.get("from_node_id")), token(item.get("to_node_id"))),
    ):
        if direction == "in" and token(edge.get("to_node_id")) != token(node_id):
            continue
        if direction == "out" and token(edge.get("from_node_id")) != token(node_id):
            continue
        out.append(as_map(edge.get("payload")))
    return out


def _bit_width_for_signal(signal_type_id: str) -> int | None:
    if token(signal_type_id) in _BOOLEANISH_SIGNAL_TYPES:
        return 1
    return None


def _slot_id(*, element_instance_id: str, port_id: str) -> str:
    return "{}::{}".format(token(element_instance_id), token(port_id))


def _normalize_assignment(assignment: object) -> str:
    return str(assignment or "").strip()


def _evaluate_assignment(
    *,
    assignment: str,
    inputs: Mapping[str, Mapping[str, object]],
    state_values: Mapping[str, object],
    delay_fixed_ticks: int,
) -> Tuple[str, object]:
    if "=" not in assignment:
        return "", None
    field_id, expression = assignment.split("=", 1)
    return token(field_id), evaluate_expression(
        expression=str(expression).strip(),
        inputs=inputs,
        state_values=state_values,
        delay_fixed_ticks=delay_fixed_ticks,
    )


def _evaluate_state_machine_program(
    *,
    current_state: Mapping[str, object],
    inputs: Mapping[str, Mapping[str, object]],
    state_machine_row: Mapping[str, object],
    delay_fixed_ticks: int,
) -> Tuple[dict, dict]:
    state_values = dict(canon(as_map(current_state)))
    current_state_id = token(state_values.get("logic_state_id"))
    if not current_state_id:
        state_ids = [
            token(row.get("state_id"))
            for row in as_list(as_map(state_machine_row).get("states"))
            if isinstance(row, Mapping)
        ]
        current_state_id = state_ids[0] if state_ids else ""
        if current_state_id:
            state_values["logic_state_id"] = current_state_id
    next_state = dict(state_values)
    next_state_id = current_state_id
    for rule in [
        dict(row)
        for row in as_list(as_map(state_machine_row).get("transition_rules"))
        if isinstance(row, Mapping)
    ]:
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
        for assignment in [_normalize_assignment(item) for item in as_list(rule.get("state_assignments"))]:
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
    for output_rule in sorted(
        (dict(item) for item in as_list(as_map(state_machine_row).get("output_rules")) if isinstance(item, Mapping)),
        key=lambda item: token(item.get("rule_id")),
    ):
        port_id = token(output_rule.get("port_id"))
        if port_id:
            outputs[port_id] = evaluate_expression(
                expression=token(output_rule.get("expression")) or "0",
                inputs=inputs,
                state_values=next_state,
                delay_fixed_ticks=delay_fixed_ticks,
            )
    return next_state, outputs


def _evaluate_combinational_program(
    *,
    output_expressions: object,
    inputs: Mapping[str, Mapping[str, object]],
    state_values: Mapping[str, object],
    delay_fixed_ticks: int,
) -> dict:
    out: Dict[str, object] = {}
    for row in sorted(
        (dict(item) for item in as_list(output_expressions) if isinstance(item, Mapping)),
        key=lambda item: token(item.get("port_id")),
    ):
        port_id = token(row.get("port_id"))
        if port_id:
            out[port_id] = evaluate_expression(
                expression=token(row.get("expression")) or "0",
                inputs=inputs,
                state_values=state_values,
                delay_fixed_ticks=delay_fixed_ticks,
            )
    return out


def _materialize_instance_definitions(
    *,
    element_index: Sequence[Mapping[str, object]],
    state_vector_definition_rows: object,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
) -> List[dict]:
    definition_rows = normalize_state_vector_definition_rows(state_vector_definition_rows)
    definition_by_owner = rows_by_id(definition_rows, "owner_id")
    for element in element_index:
        instance_definition = materialize_logic_instance_state_definition(
            element_instance_id=token(element.get("element_instance_id")),
            element_definition_id=token(element.get("element_definition_id")),
            model_kind=token(as_map(element.get("behavior_row")).get("model_kind")).lower() or "combinational",
            state_machine_row=as_map(element.get("state_machine_row")),
            state_vector_definition_rows=definition_rows,
            build_state_vector_definition_row=build_state_vector_definition_row,
        )
        owner_id = token(instance_definition.get("owner_id"))
        if owner_id and owner_id not in definition_by_owner:
            definition_rows = normalize_state_vector_definition_rows(list(definition_rows) + [instance_definition])
            definition_by_owner = rows_by_id(definition_rows, "owner_id")
    return [dict(row) for row in definition_rows]


def _build_element_programs(
    *,
    network_id: str,
    graph_row: Mapping[str, object],
    element_index: Sequence[Mapping[str, object]],
    definition_rows: object,
) -> List[dict]:
    definition_by_owner = rows_by_id(definition_rows, "owner_id")
    programs: List[dict] = []
    for element in element_index:
        element_row = as_map(element.get("element_row"))
        behavior_row = as_map(element.get("behavior_row"))
        interface_row = as_map(element.get("interface_row"))
        state_machine_row = as_map(element.get("state_machine_row"))
        element_instance_id = token(element.get("element_instance_id"))
        output_ports = []
        for port_id, port_row in sorted(dict(element.get("output_ports") or {}).items(), key=lambda item: token(item[0])):
            node_id = token(as_map(port_row).get("node_id"))
            output_ports.append(
                {
                    "port_id": token(port_id),
                    "node_id": node_id,
                    "signal_type_id": signal_type_id_for_port(
                        node_id=node_id,
                        direction="out",
                        graph_row=graph_row,
                        element_row=element_row,
                        interface_row=interface_row,
                    ),
                }
            )
        input_ports = []
        for port_id, port_row in sorted(dict(element.get("input_ports") or {}).items(), key=lambda item: token(item[0])):
            node_id = token(as_map(port_row).get("node_id"))
            input_ports.append(
                {
                    "slot_id": _slot_id(element_instance_id=element_instance_id, port_id=token(port_id)),
                    "element_instance_id": element_instance_id,
                    "port_id": token(port_id),
                    "node_id": node_id,
                    "signal_type_id": signal_type_id_for_port(
                        node_id=node_id,
                        direction="in",
                        graph_row=graph_row,
                        element_row=element_row,
                        interface_row=interface_row,
                    ),
                    "carrier_type_ids": _sorted_tokens(
                        payload.get("carrier_type_id")
                        for payload in _edge_payloads_for_node(graph_row=graph_row, node_id=node_id, direction="in")
                    ),
                }
            )
        for row in input_ports:
            row["bit_width"] = _bit_width_for_signal(token(row.get("signal_type_id")))
        graph_node_payload = next(iter(dict(element.get("input_ports") or {}).values()), {}) or next(
            iter(dict(element.get("output_ports") or {}).values()),
            {},
        )
        program = {
            "network_id": token(network_id),
            "element_instance_id": element_instance_id,
            "element_definition_id": token(element.get("element_definition_id")),
            "behavior_model_id": token(element_row.get("behavior_model_id")),
            "model_kind": token(behavior_row.get("model_kind")).lower() or "combinational",
            "compute_cost_units": int(max(1, as_int(element_row.get("compute_cost_units"), 1))),
            "timing_policy_id": token(element_row.get("timing_policy_id")),
            "fixed_ticks": int(
                max(
                    1,
                    fixed_ticks_for_element(
                        element_row=element_row,
                        interface_row=interface_row,
                        graph_node_payload=as_map(graph_node_payload.get("payload")),
                    ),
                )
            ),
            "input_ports": input_ports,
            "output_ports": output_ports,
            "output_expressions": [
                dict(row)
                for row in sorted(
                    (dict(item) for item in as_list(as_map(behavior_row.get("model_ref")).get("outputs")) if isinstance(item, Mapping)),
                    key=lambda item: token(item.get("port_id")),
                )
            ],
            "state_machine_row": canon(state_machine_row),
            "state_vector_definition": canon(definition_by_owner.get(element_instance_id)),
        }
        program["deterministic_fingerprint"] = canonical_sha256(dict(program, deterministic_fingerprint=""))
        programs.append(program)
    return sorted(programs, key=lambda item: token(item.get("element_instance_id")))


def _build_compile_source(
    *,
    network_id: str,
    logic_network_state: Mapping[str, object] | None,
    logic_policy_registry_payload: Mapping[str, object] | None,
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    logic_element_rows: object,
    logic_behavior_model_rows: object,
    logic_interface_signature_rows: object,
    logic_state_machine_rows: object,
    state_vector_definition_rows: object,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
) -> dict:
    network_state = as_map(logic_network_state)
    binding_row = dict(_binding_by_network_id(network_state.get("logic_network_binding_rows")).get(token(network_id)) or {})
    graph_row = dict(_graph_by_id(network_state.get("logic_network_graph_rows")).get(token(binding_row.get("graph_id"))) or {})
    validation_record = _validation_record_for_network(network_state.get("logic_network_validation_records"), token(network_id))
    if not binding_row or not graph_row:
        return {}
    element_index = build_logic_element_index(
        graph_row=graph_row,
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        interface_signature_rows=logic_interface_signature_rows,
        state_machine_rows=logic_state_machine_rows,
    )
    definition_rows = _materialize_instance_definitions(
        element_index=element_index,
        state_vector_definition_rows=state_vector_definition_rows,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
    )
    element_programs = _build_element_programs(
        network_id=network_id,
        graph_row=graph_row,
        element_index=element_index,
        definition_rows=definition_rows,
    )
    graph = as_map(graph_row)
    incident_node_ids = set()
    for edge in as_list(graph.get("edges")):
        if isinstance(edge, Mapping):
            incident_node_ids.add(token(edge.get("from_node_id")))
            incident_node_ids.add(token(edge.get("to_node_id")))
    removed_node_ids = sorted(
        token(row.get("node_id"))
        for row in as_list(graph.get("nodes"))
        if isinstance(row, Mapping) and token(row.get("node_id")) and token(row.get("node_id")) not in incident_node_ids
    )
    constant_bindings = {}
    for program in element_programs:
        for output_row in as_list(program.get("output_expressions")):
            expression = token(as_map(output_row).get("expression"))
            if expression in {"0", "1"}:
                constant_bindings[_slot_id(element_instance_id=token(program.get("element_instance_id")), port_id=token(as_map(output_row).get("port_id")))] = int(expression)
    input_slots = [
        dict(row)
        for row in sorted(
            (dict(item) for program in element_programs for item in as_list(program.get("input_ports")) if isinstance(item, Mapping)),
            key=lambda item: (token(item.get("element_instance_id")), token(item.get("port_id"))),
        )
    ]
    output_slots = [
        {
            "slot_id": _slot_id(element_instance_id=token(program.get("element_instance_id")), port_id=token(row.get("port_id"))),
            "element_instance_id": token(program.get("element_instance_id")),
            "port_id": token(row.get("port_id")),
            "signal_type_id": token(row.get("signal_type_id")),
        }
        for program in element_programs
        for row in as_list(program.get("output_ports"))
        if isinstance(row, Mapping)
    ]
    output_slots = sorted(output_slots, key=lambda item: (token(item.get("element_instance_id")), token(item.get("port_id"))))
    network_policy_row = dict(
        _logic_network_policy_rows_by_id(logic_network_policy_registry_payload).get(token(binding_row.get("policy_id"))) or {}
    )
    logic_policy_id = (
        token(as_map(binding_row.get("extensions")).get("logic_policy_id"))
        or token(as_map(network_policy_row.get("extensions")).get("logic_policy_id"))
        or "logic.default"
    )
    logic_policy_row = dict(_logic_policy_rows_by_id(logic_policy_registry_payload).get(logic_policy_id) or {})
    source = {
        "network_id": token(network_id),
        "binding_row": canon(binding_row),
        "graph_row": canon(graph_row),
        "validation_record": canon(validation_record),
        "logic_policy_row": canon(logic_policy_row),
        "network_policy_row": canon(network_policy_row),
        "element_programs": canon(element_programs),
        "state_vector_definition_rows": canon(definition_rows),
        "input_slots": canon(input_slots),
        "output_slots": canon(output_slots),
        "reduced_graph_summary": {
            "removed_node_ids": removed_node_ids,
            "constant_bindings": canon(constant_bindings),
            "deduplicated_group_hashes": _sorted_tokens(
                canonical_sha256(
                    {
                        "element_definition_id": token(program.get("element_definition_id")),
                        "behavior_model_id": token(program.get("behavior_model_id")),
                        "input_shape": [token(row.get("signal_type_id")) for row in as_list(program.get("input_ports")) if isinstance(row, Mapping)],
                        "output_shape": [token(row.get("signal_type_id")) for row in as_list(program.get("output_ports")) if isinstance(row, Mapping)],
                    }
                )
                for program in element_programs
            ),
        },
    }
    source["source_hash"] = canonical_sha256(dict(source, source_hash=""))
    return source


def _validation_allows_compile(*, source: Mapping[str, object]) -> bool:
    validation_record = as_map(source.get("validation_record"))
    binding_row = as_map(source.get("binding_row"))
    network_policy_row = as_map(source.get("network_policy_row"))
    validation_status = token(as_map(binding_row.get("extensions")).get("validation_status"))
    if validation_status == "validated":
        return True
    if token(validation_record.get("reason_code")) != "refusal.logic.loop_detected":
        return False
    if token(network_policy_row.get("loop_resolution_mode")).lower() != "allow_compiled_only":
        return False
    failed_count = int(max(0, as_int(as_map(validation_record.get("extensions")).get("failed_check_count"), 0)))
    loop_count = len(as_list(validation_record.get("loop_classifications")))
    return failed_count > 0 and failed_count <= max(1, loop_count)


def _enumerate_boolean_input_vectors(input_slots: Sequence[Mapping[str, object]]) -> List[dict]:
    slots = [dict(row) for row in input_slots]
    width = len(slots)
    rows: List[dict] = []
    for raw in range(0, 1 << width):
        bits = format(raw, "0{}b".format(width)) if width else ""
        slot_values = {}
        for index, slot in enumerate(slots):
            bit = int(bits[index]) if bits else 0
            signal_type_id = token(slot.get("signal_type_id")) or "signal.boolean"
            slot_values[token(slot.get("slot_id"))] = {
                "signal_type_id": signal_type_id,
                "value_ref": {
                    "value_kind": "pulse" if signal_type_id == "signal.pulse" else "boolean",
                    **to_value_payload(signal_type_id=signal_type_id, evaluated_value=bit),
                },
            }
        rows.append({"input_bits": bits, "slot_values": slot_values})
    return rows


def _inputs_by_element(*, input_slots: Sequence[Mapping[str, object]], slot_values: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for slot in input_slots:
        slot_id = token(slot.get("slot_id"))
        element_instance_id = token(slot.get("element_instance_id"))
        port_id = token(slot.get("port_id"))
        value_ref = as_map(as_map(slot_values.get(slot_id)).get("value_ref"))
        out.setdefault(element_instance_id, {})[port_id] = value_ref
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _evaluate_programs(
    *,
    programs: Sequence[Mapping[str, object]],
    input_slots: Sequence[Mapping[str, object]],
    slot_values: Mapping[str, object],
    current_state_by_element: Mapping[str, Mapping[str, object]],
) -> List[dict]:
    inputs_by_element = _inputs_by_element(input_slots=input_slots, slot_values=slot_values)
    results: List[dict] = []
    for program in [dict(item) for item in programs]:
        element_instance_id = token(program.get("element_instance_id"))
        current_state = dict(as_map(current_state_by_element.get(element_instance_id)))
        if not current_state:
            current_state = default_state_for_definition(as_map(program.get("state_vector_definition")))
        model_kind = token(program.get("model_kind")).lower() or "combinational"
        if model_kind in _SEQUENTIAL_MODEL_KINDS:
            current_state.setdefault(
                "logic_state_id",
                token(
                    next(
                        (row.get("state_id") for row in as_list(as_map(program.get("state_machine_row")).get("states")) if isinstance(row, Mapping)),
                        "",
                    )
                ),
            )
            next_state, raw_outputs = _evaluate_state_machine_program(
                current_state=current_state,
                inputs=as_map(inputs_by_element.get(element_instance_id)),
                state_machine_row=as_map(program.get("state_machine_row")),
                delay_fixed_ticks=int(max(1, as_int(program.get("fixed_ticks"), 1))),
            )
        else:
            next_state = dict(current_state)
            raw_outputs = _evaluate_combinational_program(
                output_expressions=program.get("output_expressions"),
                inputs=as_map(inputs_by_element.get(element_instance_id)),
                state_values=current_state,
                delay_fixed_ticks=int(max(1, as_int(program.get("fixed_ticks"), 1))),
            )
        output_payloads = {}
        for output_port in as_list(program.get("output_ports")):
            if not isinstance(output_port, Mapping):
                continue
            port_id = token(output_port.get("port_id"))
            signal_type_id = token(output_port.get("signal_type_id")) or "signal.boolean"
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
                "element_definition_id": token(program.get("element_definition_id")),
                "model_kind": model_kind,
                "current_state": canon(current_state),
                "next_state": canon(next_state),
                "output_payloads": canon(output_payloads),
                "compute_request": {},
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "element_instance_id": element_instance_id,
                        "current_state": canon(current_state),
                        "next_state": canon(next_state),
                        "output_payloads": canon(output_payloads),
                    }
                ),
            }
        )
    return sorted(results, key=lambda item: token(item.get("element_instance_id")))


def _state_map_hash(state_by_element: Mapping[str, Mapping[str, object]]) -> str:
    return canonical_sha256(canon(state_by_element))


def _collect_output_vector(*, element_results: Sequence[Mapping[str, object]]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in element_results:
        element_instance_id = token(as_map(row).get("element_instance_id"))
        for port_id, payload in sorted(as_map(as_map(row).get("output_payloads")).items(), key=lambda item: token(item[0])):
            out[_slot_id(element_instance_id=element_instance_id, port_id=token(port_id))] = canon(as_map(payload))
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _compile_lookup_table(*, source: Mapping[str, object]) -> dict:
    input_slots = [dict(row) for row in as_list(source.get("input_slots")) if isinstance(row, Mapping)]
    programs = [dict(row) for row in as_list(source.get("element_programs")) if isinstance(row, Mapping)]
    table_rows = []
    for assignment in _enumerate_boolean_input_vectors(input_slots):
        element_results = _evaluate_programs(
            programs=programs,
            input_slots=input_slots,
            slot_values=as_map(assignment.get("slot_values")),
            current_state_by_element={},
        )
        table_rows.append(
            {
                "input_bits": token(assignment.get("input_bits")),
                "element_results": canon(element_results),
                "output_vector": _collect_output_vector(element_results=element_results),
            }
        )
    payload = {
        "schema_version": "1.0.0",
        "compiled_type_id": "compiled.lookup_table",
        "input_slots": canon(input_slots),
        "output_slots": canon(as_list(source.get("output_slots"))),
        "element_programs": canon(programs),
        "table_rows": canon(table_rows),
        "source_hash": token(source.get("source_hash")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _compile_automaton(*, source: Mapping[str, object], max_state_space_nodes: int) -> dict:
    input_slots = [dict(row) for row in as_list(source.get("input_slots")) if isinstance(row, Mapping)]
    programs = [dict(row) for row in as_list(source.get("element_programs")) if isinstance(row, Mapping)]
    assignments = _enumerate_boolean_input_vectors(input_slots)
    initial_state_by_element = dict(
        (
            token(program.get("element_instance_id")),
            default_state_for_definition(as_map(program.get("state_vector_definition"))),
        )
        for program in programs
    )
    queue = [dict((key, dict(initial_state_by_element[key])) for key in sorted(initial_state_by_element.keys()))]
    discovered: Dict[str, dict] = {}
    states: Dict[str, dict] = {}
    transitions: List[dict] = []

    while queue:
        current_state_by_element = queue.pop(0)
        state_hash = _state_map_hash(current_state_by_element)
        if state_hash in discovered:
            continue
        if len(discovered) >= int(max(1, as_int(max_state_space_nodes, 1))):
            return {}
        state_id = "logic_state.{}".format(state_hash[:16])
        discovered[state_hash] = {"state_id": state_id, "state_by_element": canon(current_state_by_element)}
        states[state_id] = {"state_id": state_id, "state_by_element": canon(current_state_by_element)}
        for assignment in assignments:
            element_results = _evaluate_programs(
                programs=programs,
                input_slots=input_slots,
                slot_values=as_map(assignment.get("slot_values")),
                current_state_by_element=current_state_by_element,
            )
            next_state_by_element = dict(
                (token(row.get("element_instance_id")), canon(as_map(row.get("next_state"))))
                for row in element_results
            )
            next_hash = _state_map_hash(next_state_by_element)
            next_state_id = "logic_state.{}".format(next_hash[:16])
            transitions.append(
                {
                    "state_id": state_id,
                    "input_bits": token(assignment.get("input_bits")),
                    "next_state_id": next_state_id,
                    "output_vector": _collect_output_vector(element_results=element_results),
                }
            )
            if next_hash not in discovered:
                queue.append(dict((key, dict(next_state_by_element[key])) for key in sorted(next_state_by_element.keys())))
    payload = {
        "schema_version": "1.0.0",
        "compiled_type_id": "compiled.automaton",
        "input_slots": canon(input_slots),
        "output_slots": canon(as_list(source.get("output_slots"))),
        "element_programs": canon(programs),
        "states": [dict(states[key]) for key in sorted(states.keys())],
        "transition_rows": sorted(transitions, key=lambda item: (token(item.get("state_id")), token(item.get("input_bits")))),
        "initial_state_id": "logic_state.{}".format(_state_map_hash(initial_state_by_element)[:16]),
        "source_hash": token(source.get("source_hash")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _compile_reduced_graph(*, source: Mapping[str, object]) -> dict:
    reduced_summary = as_map(source.get("reduced_graph_summary"))
    payload = {
        "schema_version": "1.0.0",
        "compiled_type_id": "compiled.reduced_graph",
        "input_slots": canon(as_list(source.get("input_slots"))),
        "output_slots": canon(as_list(source.get("output_slots"))),
        "element_programs": canon(as_list(source.get("element_programs"))),
        "removed_node_ids": _sorted_tokens(reduced_summary.get("removed_node_ids")),
        "constant_bindings": canon(as_map(reduced_summary.get("constant_bindings"))),
        "deduplicated_group_hashes": _sorted_tokens(reduced_summary.get("deduplicated_group_hashes")),
        "source_hash": token(source.get("source_hash")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _choose_compile_target(*, source: Mapping[str, object], compile_policy_row: Mapping[str, object]) -> Tuple[str, dict]:
    programs = [dict(row) for row in as_list(source.get("element_programs")) if isinstance(row, Mapping)]
    input_slots = [dict(row) for row in as_list(source.get("input_slots")) if isinstance(row, Mapping)]
    has_sequential = any(token(row.get("model_kind")) in _SEQUENTIAL_MODEL_KINDS for row in programs)
    booleanish_inputs = bool(input_slots) and all(_bit_width_for_signal(token(row.get("signal_type_id"))) == 1 for row in input_slots)
    total_input_width = sum(int(max(0, as_int(row.get("bit_width"), 0))) for row in input_slots)
    max_lookup_width = int(max(0, as_int(as_map(compile_policy_row.get("extensions")).get("max_lookup_input_width"), 0)))
    max_state_nodes = int(max(1, as_int(as_map(compile_policy_row.get("extensions")).get("max_state_space_nodes"), 1)))

    if (not has_sequential) and booleanish_inputs and total_input_width <= max_lookup_width:
        payload = _compile_lookup_table(source=source)
        if payload:
            return "compiled.lookup_table", payload
    if has_sequential and booleanish_inputs:
        payload = _compile_automaton(source=source, max_state_space_nodes=max_state_nodes)
        if payload:
            return "compiled.automaton", payload
    return "compiled.reduced_graph", _compile_reduced_graph(source=source)


def compile_logic_network(
    *,
    current_tick: int,
    compile_request: Mapping[str, object],
    logic_network_state: Mapping[str, object] | None,
    logic_policy_registry_payload: Mapping[str, object] | None,
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    logic_compile_policy_registry_payload: Mapping[str, object] | None,
    compiled_type_registry_payload: Mapping[str, object] | None,
    verification_procedure_registry_payload: Mapping[str, object] | None,
    logic_element_rows: object,
    logic_behavior_model_rows: object,
    logic_interface_signature_rows: object,
    logic_state_machine_rows: object,
    state_vector_definition_rows: object,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
) -> dict:
    tick = int(max(0, as_int(current_tick, 0)))
    request = as_map(compile_request)
    network_id = token(request.get("network_id"))
    compile_policy_id = token(request.get("compile_policy_id")) or "compile.logic.default"
    request_id = token(request.get("request_id")) or "logic_compile_request.{}".format(
        canonical_sha256({"tick": tick, "network_id": network_id, "compile_policy_id": compile_policy_id})[:16]
    )
    request_row = build_compile_request_row(
        request_id=request_id,
        source_kind="logic.network",
        source_ref={"network_id": network_id, "compile_policy_id": compile_policy_id},
        target_compiled_type_id="compiled.reduced_graph",
        error_bound_policy_id=None,
        deterministic_fingerprint="",
        extensions={"current_tick": tick, "source_tick": tick},
    )
    policy_rows = logic_compile_policy_rows_by_id(logic_compile_policy_registry_payload)
    compile_policy_row = dict(policy_rows.get(compile_policy_id) or {})
    if not network_id:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(canonical_sha256({"request_id": request_id, "reason": REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND})[:16]),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND,
                deterministic_fingerprint="",
                extensions={"request_id": request_id},
            ),
        }
    if not compile_policy_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_COMPILE_POLICY_UNREGISTERED,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(canonical_sha256({"request_id": request_id, "reason": REFUSAL_LOGIC_COMPILE_POLICY_UNREGISTERED})[:16]),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_LOGIC_COMPILE_POLICY_UNREGISTERED,
                deterministic_fingerprint="",
                extensions={"request_id": request_id, "compile_policy_id": compile_policy_id},
            ),
        }
    request_extensions = as_map(request_row.get("extensions"))
    request_extensions.update(
        {
            "compile_policy_id": compile_policy_id,
            "compile_policy_fingerprint": token(compile_policy_row.get("deterministic_fingerprint")),
        }
    )
    request_row["extensions"] = request_extensions

    source = _build_compile_source(
        network_id=network_id,
        logic_network_state=logic_network_state,
        logic_policy_registry_payload=logic_policy_registry_payload,
        logic_network_policy_registry_payload=logic_network_policy_registry_payload,
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        logic_interface_signature_rows=logic_interface_signature_rows,
        logic_state_machine_rows=logic_state_machine_rows,
        state_vector_definition_rows=state_vector_definition_rows,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
    )
    if not source:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(canonical_sha256({"request_id": request_id, "reason": REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND})[:16]),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND,
                deterministic_fingerprint="",
                extensions={"request_id": request_id},
            ),
        }
    if not _validation_allows_compile(source=source):
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_COMPILE_NETWORK_NOT_VALIDATED,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(canonical_sha256({"request_id": request_id, "reason": REFUSAL_LOGIC_COMPILE_NETWORK_NOT_VALIDATED})[:16]),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_LOGIC_COMPILE_NETWORK_NOT_VALIDATED,
                deterministic_fingerprint="",
                extensions={"request_id": request_id, "network_id": network_id},
            ),
        }

    compiled_type_id, compiled_payload = _choose_compile_target(source=source, compile_policy_row=compile_policy_row)
    if token(compiled_type_id) not in compiled_type_rows_by_id(compiled_type_registry_payload):
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_COMPILE_INELIGIBLE,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(canonical_sha256({"request_id": request_id, "reason": REFUSAL_LOGIC_COMPILE_INELIGIBLE})[:16]),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_LOGIC_COMPILE_INELIGIBLE,
                deterministic_fingerprint="",
                extensions={"request_id": request_id, "network_id": network_id},
            ),
        }
    proof_row = build_logic_equivalence_proof_row(
        request_id=request_id,
        source_hash=token(source.get("source_hash")),
        compiled_payload=compiled_payload,
        compiled_type_id=compiled_type_id,
        verification_procedure_registry_payload=verification_procedure_registry_payload,
        compile_policy_row=compile_policy_row,
    )
    if not proof_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_MISSING_PROOF,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(canonical_sha256({"request_id": request_id, "reason": REFUSAL_COMPILE_MISSING_PROOF})[:16]),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_COMPILE_MISSING_PROOF,
                deterministic_fingerprint="",
                extensions={"request_id": request_id, "network_id": network_id},
            ),
        }
    input_ranges = {}
    for row in as_list(source.get("input_slots")):
        if isinstance(row, Mapping) and _bit_width_for_signal(token(row.get("signal_type_id"))) == 1:
            input_ranges[token(row.get("slot_id"))] = {"min": 0, "max": 1}
    validity_row = build_validity_domain_row(
        domain_id="validity_domain.logic.{}".format(token(source.get("source_hash"))[:16]),
        input_ranges=input_ranges,
        timing_constraints={
            "validation_hash": token(as_map(source.get("validation_record")).get("validation_hash")),
            "logic_policy_id": token(as_map(source.get("logic_policy_row")).get("policy_id")),
        },
        environmental_constraints={
            "carrier_type_ids": _sorted_tokens(
                carrier_id
                for row in as_list(source.get("input_slots"))
                if isinstance(row, Mapping)
                for carrier_id in as_list(as_map(row).get("carrier_type_ids"))
            ),
        },
        deterministic_fingerprint="",
        extensions={
            "source_hash": token(source.get("source_hash")),
            "network_id": network_id,
            "validation_hash": token(as_map(source.get("validation_record")).get("validation_hash")),
        },
    )
    payload_hash = canonical_sha256(canon(compiled_payload))
    compiled_model_id = "compiled_model.logic.{}".format(
        canonical_sha256(
            {
                "network_id": network_id,
                "compile_policy_id": compile_policy_id,
                "compiled_type_id": compiled_type_id,
                "payload_hash": payload_hash,
                "source_hash": token(source.get("source_hash")),
            }
        )[:16]
    )
    compiled_model_row = build_compiled_model_row(
        compiled_model_id=compiled_model_id,
        source_kind="logic.network",
        source_hash=token(source.get("source_hash")),
        compiled_type_id=compiled_type_id,
        compiled_payload_ref={
            "payload_format": "inline.logic_compiled.v1",
            "payload_hash": payload_hash,
            "payload": canon(compiled_payload),
        },
        input_signature_ref="signature.logic.input.{}".format(network_id),
        output_signature_ref="signature.logic.output.{}".format(network_id),
        validity_domain_ref=token(validity_row.get("domain_id")),
        equivalence_proof_ref=token(proof_row.get("proof_id")),
        deterministic_fingerprint="",
        extensions={
            "network_id": network_id,
            "compile_policy_id": compile_policy_id,
            "compile_policy_fingerprint": token(compile_policy_row.get("deterministic_fingerprint")),
            "validation_hash": token(as_map(source.get("validation_record")).get("validation_hash")),
            "compiled_target_type": compiled_type_id,
            "proof_requirement_enforced": True,
            "prefer_compiled_runtime": bool(as_map(compile_policy_row.get("extensions")).get("prefer_compiled_runtime", True)),
        },
    )
    compile_result_row = build_compile_result_row(
        result_id="compile_result.logic.{}".format(canonical_sha256({"request_id": request_id, "compiled_model_id": compiled_model_id})[:16]),
        compiled_model_id=compiled_model_id,
        success=True,
        refusal=None,
        deterministic_fingerprint="",
        extensions={
            "request_id": request_id,
            "proof_id": token(proof_row.get("proof_id")),
            "source_tick": tick,
            "compile_policy_id": compile_policy_id,
            "compile_policy_fingerprint": token(compile_policy_row.get("deterministic_fingerprint")),
        },
    )
    network_state = as_map(logic_network_state)
    binding_row = dict(_binding_by_network_id(network_state.get("logic_network_binding_rows")).get(network_id) or {})
    binding_ext = as_map(binding_row.get("extensions"))
    binding_ext.update(
        {
            "compiled_model_id": compiled_model_id,
            "compiled_equivalence_proof_id": token(proof_row.get("proof_id")),
            "compiled_validity_domain_id": token(validity_row.get("domain_id")),
            "compile_policy_id": compile_policy_id,
            "compile_policy_fingerprint": token(compile_policy_row.get("deterministic_fingerprint")),
            "compiled_target_type": compiled_type_id,
            "compiled_source_hash": token(source.get("source_hash")),
            "compiled_payload_hash": payload_hash,
            "compiled_prefer_runtime": bool(as_map(compile_policy_row.get("extensions")).get("prefer_compiled_runtime", True)),
            "proof_requirement_enforced": True,
        }
    )
    binding_row["extensions"] = binding_ext
    logic_network_state_out = dict(
        network_state,
        logic_network_binding_rows=[
            dict(binding_row) if token(row.get("network_id")) == network_id else dict(row)
            for row in as_list(network_state.get("logic_network_binding_rows"))
            if isinstance(row, Mapping)
        ],
    )
    return {
        "result": "complete",
        "reason_code": "",
        "compile_request_row": request_row,
        "compile_result_row": compile_result_row,
        "compiled_model_row": compiled_model_row,
        "equivalence_proof_row": proof_row,
        "validity_domain_row": validity_row,
        "logic_network_state": logic_network_state_out,
        "source_hash": token(source.get("source_hash")),
        "compiled_payload": compiled_payload,
        "compiled_type_id": compiled_type_id,
        "deterministic_fingerprint": canonical_sha256(
            {
                "compile_request_row": request_row,
                "compile_result_row": compile_result_row,
                "compiled_model_row": compiled_model_row,
                "equivalence_proof_row": proof_row,
                "validity_domain_row": validity_row,
            }
        ),
    }


def _derive_current_state_by_element(
    *,
    compiled_payload: Mapping[str, object],
    state_vector_snapshot_rows: object,
    state_vector_definition_rows: object,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
    state_vector_snapshot_rows_by_owner,
    deserialize_state,
) -> Tuple[Dict[str, dict], List[dict]]:
    programs = [dict(row) for row in as_list(as_map(compiled_payload).get("element_programs")) if isinstance(row, Mapping)]
    definition_rows = normalize_state_vector_definition_rows(state_vector_definition_rows)
    definition_by_owner = rows_by_id(definition_rows, "owner_id")
    snapshot_by_owner = state_vector_snapshot_rows_by_owner(state_vector_snapshot_rows)
    state_by_element: Dict[str, dict] = {}
    for program in programs:
        element_instance_id = token(program.get("element_instance_id"))
        state_definition = as_map(program.get("state_vector_definition"))
        if state_definition and token(state_definition.get("owner_id")) not in definition_by_owner:
            definition_rows = normalize_state_vector_definition_rows(list(definition_rows) + [state_definition])
            definition_by_owner = rows_by_id(definition_rows, "owner_id")
        current_state = default_state_for_definition(state_definition)
        current_snapshot = dict(snapshot_by_owner.get(element_instance_id) or {})
        if current_snapshot:
            restored = deserialize_state(
                snapshot_row=current_snapshot,
                state_vector_definition_rows=definition_rows,
                expected_version=token(current_snapshot.get("version")) or None,
            )
            if token(restored.get("result")) == "complete":
                current_state = dict(restored.get("restored_state") or {})
        state_by_element[element_instance_id] = canon(current_state)
    return state_by_element, definition_rows


def _current_slot_values_from_snapshot(*, sense_snapshot: Mapping[str, object], input_slots: Sequence[Mapping[str, object]]) -> Dict[str, dict]:
    inputs_by_element = as_map(as_map(sense_snapshot).get("inputs_by_element"))
    out: Dict[str, dict] = {}
    for slot in input_slots:
        slot_id = token(slot.get("slot_id"))
        element_instance_id = token(slot.get("element_instance_id"))
        port_id = token(slot.get("port_id"))
        out[slot_id] = {
            "signal_type_id": token(slot.get("signal_type_id")),
            "value_ref": canon(as_map(as_map(inputs_by_element.get(element_instance_id)).get(port_id))),
        }
    return out


def _network_compute_request(
    *,
    current_tick: int,
    network_id: str,
    element_count: int,
    compiled_type_id: str,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str,
) -> dict:
    cost_multiplier = {"compiled.lookup_table": 1, "compiled.automaton": 2, "compiled.reduced_graph": 3}.get(
        token(compiled_type_id),
        3,
    )
    return request_compute(
        current_tick=int(max(0, as_int(current_tick, 0))),
        owner_kind="controller",
        owner_id="logic.compile.execute.{}".format(token(network_id)),
        instruction_units=int(max(1, cost_multiplier * max(1, element_count))),
        memory_units=int(max(1, element_count * (1 if token(compiled_type_id) == "compiled.lookup_table" else 2))),
        owner_priority=100,
        critical=False,
        compute_runtime_state=compute_runtime_state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )


def _proof_matches(*, compiled_model_row: Mapping[str, object], proof_row: Mapping[str, object]) -> bool:
    return verify_logic_equivalence_proof(
        compiled_model_row=compiled_model_row,
        proof_row=proof_row,
    )


def validate_logic_compiled_model(
    *,
    network_id: str,
    binding_row: Mapping[str, object],
    validation_record: Mapping[str, object],
    sense_snapshot: Mapping[str, object],
    compiled_model_rows: object,
    equivalence_proof_rows: object,
    validity_domain_rows: object,
    state_vector_snapshot_rows: object,
    state_vector_definition_rows: object,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
    state_vector_snapshot_rows_by_owner,
    deserialize_state,
) -> dict:
    model_id = token(as_map(binding_row.get("extensions")).get("compiled_model_id"))
    proof_id = token(as_map(binding_row.get("extensions")).get("compiled_equivalence_proof_id"))
    model_row = dict(rows_by_id(compiled_model_rows, "compiled_model_id").get(model_id) or {})
    if not model_row:
        return {"valid": False, "reason_code": REFUSAL_LOGIC_COMPILED_INVALID, "violations": ["missing_compiled_model"]}
    proof_row = dict(
        equivalence_proof_rows_by_id(equivalence_proof_rows).get(proof_id or token(model_row.get("equivalence_proof_ref"))) or {}
    )
    if not proof_row:
        return {"valid": False, "reason_code": REFUSAL_LOGIC_COMPILED_INVALID, "violations": ["missing_equivalence_proof"]}
    if not _proof_matches(compiled_model_row=model_row, proof_row=proof_row):
        return {"valid": False, "reason_code": REFUSAL_LOGIC_COMPILED_INVALID, "violations": ["proof_hash_mismatch"]}
    validity_row = dict(validity_domain_rows_by_id(validity_domain_rows).get(token(model_row.get("validity_domain_ref"))) or {})
    if not validity_row:
        return {"valid": False, "reason_code": REFUSAL_LOGIC_COMPILED_INVALID, "violations": ["missing_validity_domain"]}
    violations: List[str] = []
    if token(as_map(validity_row.get("extensions")).get("validation_hash")) != token(as_map(validation_record).get("validation_hash")):
        violations.append("validation_hash_mismatch")
    if token(as_map(binding_row.get("extensions")).get("compiled_source_hash")) != token(model_row.get("source_hash")):
        violations.append("compiled_source_hash_mismatch")
    current_inputs = _current_slot_values_from_snapshot(
        sense_snapshot=sense_snapshot,
        input_slots=as_list(as_map(as_map(model_row.get("compiled_payload_ref")).get("payload")).get("input_slots")),
    )
    for slot_id, rule in sorted(as_map(validity_row.get("input_ranges")).items(), key=lambda item: token(item[0])):
        scalar = value_ref_to_scalar(as_map(as_map(current_inputs.get(token(slot_id))).get("value_ref")))
        if "min" in as_map(rule) and scalar < int(as_int(as_map(rule).get("min"), scalar)):
            violations.append("input_range_low:{}".format(token(slot_id)))
        if "max" in as_map(rule) and scalar > int(as_int(as_map(rule).get("max"), scalar)):
            violations.append("input_range_high:{}".format(token(slot_id)))
    payload = as_map(as_map(model_row.get("compiled_payload_ref")).get("payload"))
    if token(model_row.get("compiled_type_id")) == "compiled.automaton":
        state_by_element, _ = _derive_current_state_by_element(
            compiled_payload=payload,
            state_vector_snapshot_rows=state_vector_snapshot_rows,
            state_vector_definition_rows=state_vector_definition_rows,
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
        )
        state_id = "logic_state.{}".format(_state_map_hash(state_by_element)[:16])
        if not any(token(row.get("state_id")) == state_id for row in as_list(payload.get("states")) if isinstance(row, Mapping)):
            violations.append("state_outside_automaton_domain")
    return {
        "valid": not violations,
        "reason_code": "" if not violations else REFUSAL_LOGIC_COMPILED_INVALID,
        "violations": violations,
        "compiled_model_row": model_row,
        "equivalence_proof_row": proof_row,
        "validity_domain_row": validity_row,
        "network_id": token(network_id),
    }


def _lookup_table_result(*, payload: Mapping[str, object], slot_values: Mapping[str, object]) -> List[dict]:
    input_slots = [dict(row) for row in as_list(as_map(payload).get("input_slots")) if isinstance(row, Mapping)]
    bits = []
    for slot in input_slots:
        bits.append("1" if bool(as_int(value_ref_to_scalar(as_map(as_map(slot_values.get(token(slot.get("slot_id")))).get("value_ref"))), 0)) else "0")
    lookup_bits = "".join(bits)
    for row in as_list(as_map(payload).get("table_rows")):
        if isinstance(row, Mapping) and token(row.get("input_bits")) == lookup_bits:
            return [dict(item) for item in as_list(row.get("element_results")) if isinstance(item, Mapping)]
    return []


def _automaton_result(
    *,
    payload: Mapping[str, object],
    slot_values: Mapping[str, object],
    current_state_by_element: Mapping[str, Mapping[str, object]],
) -> List[dict]:
    input_slots = [dict(row) for row in as_list(as_map(payload).get("input_slots")) if isinstance(row, Mapping)]
    programs_by_element = {
        token(row.get("element_instance_id")): dict(row)
        for row in as_list(as_map(payload).get("element_programs"))
        if isinstance(row, Mapping) and token(row.get("element_instance_id"))
    }
    bits = []
    for slot in input_slots:
        bits.append("1" if bool(as_int(value_ref_to_scalar(as_map(as_map(slot_values.get(token(slot.get("slot_id")))).get("value_ref"))), 0)) else "0")
    state_id = "logic_state.{}".format(_state_map_hash(current_state_by_element)[:16])
    transitions = {
        (token(row.get("state_id")), token(row.get("input_bits"))): dict(row)
        for row in as_list(payload.get("transition_rows"))
        if isinstance(row, Mapping)
    }
    states_by_id = rows_by_id(as_list(payload.get("states")), "state_id")
    transition = dict(transitions.get((state_id, "".join(bits))) or {})
    if not transition:
        return []
    next_state = as_map(as_map(states_by_id.get(token(transition.get("next_state_id")))).get("state_by_element"))
    output_vector = as_map(transition.get("output_vector"))
    results = []
    for element_instance_id in sorted(current_state_by_element.keys()):
        per_element_outputs = {}
        for slot_id, payload_row in sorted(output_vector.items(), key=lambda item: token(item[0])):
            slot_token = token(slot_id)
            if slot_token.startswith("{}::".format(element_instance_id)):
                per_element_outputs[slot_token.split("::", 1)[1]] = canon(as_map(payload_row))
        results.append(
            {
                "element_instance_id": element_instance_id,
                "element_definition_id": token(as_map(programs_by_element.get(element_instance_id)).get("element_definition_id")),
                "model_kind": token(as_map(programs_by_element.get(element_instance_id)).get("model_kind")) or "sequential",
                "current_state": canon(as_map(current_state_by_element.get(element_instance_id))),
                "next_state": canon(as_map(next_state.get(element_instance_id))),
                "output_payloads": canon(per_element_outputs),
                "compute_request": {},
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "element_instance_id": element_instance_id,
                        "current_state": canon(as_map(current_state_by_element.get(element_instance_id))),
                        "next_state": canon(as_map(next_state.get(element_instance_id))),
                        "output_payloads": canon(per_element_outputs),
                    }
                ),
            }
        )
    return results


def execute_logic_compiled_model(
    *,
    current_tick: int,
    network_id: str,
    binding_row: Mapping[str, object],
    validation_record: Mapping[str, object],
    sense_snapshot: Mapping[str, object],
    state_vector_snapshot_rows: object,
    state_vector_definition_rows: object,
    compiled_model_rows: object,
    equivalence_proof_rows: object,
    validity_domain_rows: object,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str,
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
    state_vector_snapshot_rows_by_owner,
    deserialize_state,
) -> dict:
    validation = validate_logic_compiled_model(
        network_id=network_id,
        binding_row=binding_row,
        validation_record=validation_record,
        sense_snapshot=sense_snapshot,
        compiled_model_rows=compiled_model_rows,
        equivalence_proof_rows=equivalence_proof_rows,
        validity_domain_rows=validity_domain_rows,
        state_vector_snapshot_rows=state_vector_snapshot_rows,
        state_vector_definition_rows=state_vector_definition_rows,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
    )
    if not bool(validation.get("valid", False)):
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_COMPILED_INVALID,
            "compiled_validation": validation,
            "element_results": [],
            "compute_runtime_state": dict(as_map(compute_runtime_state)),
            "compute_units_used": 0,
            "elements_evaluated_count": 0,
            "network_throttled": False,
            "throttle_events": [],
        }
    model_row = dict(validation.get("compiled_model_row") or {})
    payload = as_map(as_map(model_row.get("compiled_payload_ref")).get("payload"))
    state_by_element, definition_rows = _derive_current_state_by_element(
        compiled_payload=payload,
        state_vector_snapshot_rows=state_vector_snapshot_rows,
        state_vector_definition_rows=state_vector_definition_rows,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
    )
    input_slots = [dict(row) for row in as_list(payload.get("input_slots")) if isinstance(row, Mapping)]
    slot_values = _current_slot_values_from_snapshot(sense_snapshot=sense_snapshot, input_slots=input_slots)
    compute_request = _network_compute_request(
        current_tick=current_tick,
        network_id=network_id,
        element_count=max(1, len(as_list(payload.get("element_programs"))) or len(state_by_element)),
        compiled_type_id=token(model_row.get("compiled_type_id")),
        compute_runtime_state=compute_runtime_state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=compute_budget_profile_id,
    )
    if token(compute_request.get("result")).lower() in {"refused", "deferred", "shutdown"}:
        return {
            "result": "throttled",
            "reason_code": token(compute_request.get("reason_code")) or "budget_exceeded",
            "compiled_validation": validation,
            "element_results": [],
            "compute_runtime_state": dict(as_map(compute_request.get("runtime_state"))),
            "compute_units_used": int(max(0, as_int(compute_request.get("approved_instruction_units"), 0))),
            "elements_evaluated_count": 0,
            "network_throttled": True,
            "throttle_events": [
                {
                    "tick": int(max(0, as_int(current_tick, 0))),
                    "network_id": token(network_id),
                    "reason": "budget_exceeded",
                    "extensions": {
                        "compiled_model_id": token(model_row.get("compiled_model_id")),
                        "compiled_type_id": token(model_row.get("compiled_type_id")),
                        "reason_code": token(compute_request.get("reason_code")),
                    },
                }
            ],
            "state_vector_definition_rows": definition_rows,
        }
    compiled_type_id = token(model_row.get("compiled_type_id"))
    if compiled_type_id == "compiled.lookup_table":
        element_results = _lookup_table_result(payload=payload, slot_values=slot_values)
    elif compiled_type_id == "compiled.automaton":
        element_results = _automaton_result(payload=payload, slot_values=slot_values, current_state_by_element=state_by_element)
    else:
        element_results = _evaluate_programs(
            programs=as_list(payload.get("element_programs")),
            input_slots=input_slots,
            slot_values=slot_values,
            current_state_by_element=state_by_element,
        )
    for row in element_results:
        row["compute_request"] = dict(compute_request)
    return {
        "result": "complete",
        "reason_code": "",
        "compiled_validation": validation,
        "element_results": element_results,
        "compute_runtime_state": dict(as_map(compute_request.get("runtime_state"))),
        "compute_units_used": int(max(0, as_int(compute_request.get("approved_instruction_units"), 0))),
        "elements_evaluated_count": int(len(element_results)),
        "network_throttled": False,
        "throttle_events": [],
        "state_vector_definition_rows": definition_rows,
        "compiled_execution_metadata": {
            "compiled_model_id": token(model_row.get("compiled_model_id")),
            "compiled_type_id": compiled_type_id,
            "compiled_payload_hash": token(as_map(model_row.get("compiled_payload_ref")).get("payload_hash")),
        },
    }


def build_logic_controller_macro_capsule(
    *,
    system_id: str,
    network_id: str,
    interface_signature_id: str,
    compiled_model_id: str,
    compiled_model_rows: object,
    provenance_anchor_hash: str,
) -> dict:
    model_row = dict(rows_by_id(compiled_model_rows, "compiled_model_id").get(token(compiled_model_id)) or {})
    restore_ref = {
        "network_id": token(network_id),
        "compiled_model_id": token(compiled_model_id),
        "source_hash": token(model_row.get("source_hash")),
        "compiled_type_id": token(model_row.get("compiled_type_id")),
    }
    return build_system_macro_capsule_row(
        capsule_id="capsule.logic_controller.{}".format(
            canonical_sha256({"system_id": token(system_id), "network_id": token(network_id), "compiled_model_id": token(compiled_model_id)})[:16]
        ),
        system_id=token(system_id),
        interface_signature_id=token(interface_signature_id),
        macro_model_set_id="macro.logic_controller.compiled",
        model_error_bounds_ref="tol.strict",
        macro_model_bindings=[
            {
                "binding_id": "binding.logic_controller.compiled",
                "compiled_model_id": token(compiled_model_id),
                "source_network_id": token(network_id),
                "extensions": {
                    "compiled_type_id": token(model_row.get("compiled_type_id")),
                    "source_hash": token(model_row.get("source_hash")),
                },
            }
        ],
        internal_state_vector={
            "network_id": token(network_id),
            "compiled_model_id": token(compiled_model_id),
            "compiled_type_id": token(model_row.get("compiled_type_id")),
            "source_hash": token(model_row.get("source_hash")),
            "validity_domain_ref": token(model_row.get("validity_domain_ref")),
        },
        provenance_anchor_hash=token(provenance_anchor_hash),
        tier_mode="macro",
        deterministic_fingerprint="",
        extensions={
            "template_id": "template.logic_controller",
            "network_id": token(network_id),
            "compiled_model_id": token(compiled_model_id),
            "restore_ref": restore_ref,
            "validity_domain_ref": token(model_row.get("validity_domain_ref")),
            "forced_expand_triggers": [
                "logic.compiled_invalid",
                "logic.timing_anomaly",
                "inspection_request",
            ],
            "debug_expand_policy": "instrumented_only",
        },
    )


def build_logic_controller_interface_signature_row(
    *,
    system_id: str,
    compiled_model_id: str,
    compiled_model_rows: object,
    interface_signature_id: str = "",
) -> dict:
    model_row = dict(rows_by_id(compiled_model_rows, "compiled_model_id").get(token(compiled_model_id)) or {})
    if not model_row:
        return {}
    payload = as_map(as_map(model_row.get("compiled_payload_ref")).get("payload"))
    input_slots = [
        dict(row)
        for row in sorted(
            (dict(item) for item in as_list(payload.get("input_slots")) if isinstance(item, Mapping)),
            key=lambda item: token(item.get("slot_id")),
        )
    ]
    output_slots = [
        dict(row)
        for row in sorted(
            (dict(item) for item in as_list(payload.get("output_slots")) if isinstance(item, Mapping)),
            key=lambda item: token(item.get("slot_id")),
        )
    ]
    if not token(interface_signature_id):
        interface_signature_id = "iface.logic_controller.{}".format(
            canonical_sha256({"system_id": token(system_id), "compiled_model_id": token(compiled_model_id)})[:16]
        )
    port_list = []
    for slot in input_slots:
        port_list.append(
            {
                "port_id": token(slot.get("slot_id")),
                "port_type_id": "port.signal_in",
                "direction": "in",
                "allowed_bundle_ids": ["bundle.signal_logic"],
                "spec_limit_refs": ["spec.logic_interface"],
            }
        )
    for slot in output_slots:
        port_list.append(
            {
                "port_id": token(slot.get("slot_id")),
                "port_type_id": "port.signal_out",
                "direction": "out",
                "allowed_bundle_ids": ["bundle.signal_logic"],
                "spec_limit_refs": ["spec.logic_interface"],
            }
        )
    return build_interface_signature_row(
        system_id=token(system_id),
        interface_signature_id=token(interface_signature_id),
        port_list=port_list,
        signal_channels=[
            {
                "channel_id": "sig.logic_controller.{}".format(canonical_sha256({"system_id": token(system_id)})[:12]),
                "direction": "bidir",
            }
        ],
        spec_limits={
            "max_compiled_input_slots": int(len(input_slots)),
            "max_compiled_output_slots": int(len(output_slots)),
        },
        deterministic_fingerprint="",
        extensions={
            "template_id": "template.logic_controller",
            "compiled_model_id": token(compiled_model_id),
            "compiled_type_id": token(model_row.get("compiled_type_id")),
            "source_hash": token(model_row.get("source_hash")),
        },
    )


def build_logic_controller_system_bundle(
    *,
    system_id: str,
    network_id: str,
    compiled_model_id: str,
    compiled_model_rows: object,
    provenance_anchor_hash: str,
    tier_contract_id: str = "tier.logic.default",
) -> dict:
    model_row = dict(rows_by_id(compiled_model_rows, "compiled_model_id").get(token(compiled_model_id)) or {})
    if not model_row:
        return {}
    interface_row = build_logic_controller_interface_signature_row(
        system_id=token(system_id),
        compiled_model_id=token(compiled_model_id),
        compiled_model_rows=compiled_model_rows,
    )
    if not interface_row:
        return {}
    capsule_row = build_logic_controller_macro_capsule(
        system_id=token(system_id),
        network_id=token(network_id),
        interface_signature_id=token(interface_row.get("interface_signature_id")),
        compiled_model_id=token(compiled_model_id),
        compiled_model_rows=compiled_model_rows,
        provenance_anchor_hash=token(provenance_anchor_hash),
    )
    system_rows = normalize_system_rows(
        [
            {
                "schema_version": "1.0.0",
                "system_id": token(system_id),
                "root_assembly_id": "assembly.logic_controller.{}".format(
                    canonical_sha256({"system_id": token(system_id)})[:12]
                ),
                "assembly_ids": [
                    "assembly.logic_controller.{}".format(
                        canonical_sha256({"system_id": token(system_id)})[:12]
                    )
                ],
                "interface_signature_id": token(interface_row.get("interface_signature_id")),
                "boundary_invariant_ids": [],
                "tier_contract_id": token(tier_contract_id) or "tier.logic.default",
                "current_tier": "macro",
                "active_capsule_id": token(capsule_row.get("capsule_id")),
                "deterministic_fingerprint": "",
                "extensions": {
                    "template_id": "template.logic_controller",
                    "network_id": token(network_id),
                    "compiled_model_id": token(compiled_model_id),
                    "compiled_type_id": token(model_row.get("compiled_type_id")),
                    "compiled_source_hash": token(model_row.get("source_hash")),
                    "macro_model_set_id": "macro.logic_controller.compiled",
                    "restore_ref": {
                        "network_id": token(network_id),
                        "compiled_model_id": token(compiled_model_id),
                        "source_hash": token(model_row.get("source_hash")),
                    },
                },
            }
        ]
    )
    return {
        "system_row": dict(system_rows[0]) if system_rows else {},
        "interface_signature_row": dict(interface_row),
        "macro_capsule_row": dict(capsule_row),
        "restore_ref": {
            "network_id": token(network_id),
            "compiled_model_id": token(compiled_model_id),
            "source_hash": token(model_row.get("source_hash")),
        },
    }


def build_logic_compiled_forced_expand_event(
    *,
    capsule_id: str,
    tick: int,
    network_id: str,
    reason_code: str,
    compiled_model_id: str | None = None,
) -> dict:
    return build_forced_expand_event_row(
        event_id="",
        capsule_id=token(capsule_id),
        tick=int(max(0, as_int(tick, 0))),
        reason_code=token(reason_code) or REFUSAL_LOGIC_COMPILED_INVALID,
        requested_fidelity="meso",
        deterministic_fingerprint="",
        extensions={"network_id": token(network_id), "compiled_model_id": None if compiled_model_id is None else token(compiled_model_id) or None, "source": "LOGIC6"},
    )


def build_logic_compiled_invalid_explain_artifact(
    *,
    tick: int,
    network_id: str,
    compiled_model_id: str,
    violations: Sequence[object],
) -> dict:
    event_seed = {
        "tick": int(max(0, as_int(tick, 0))),
        "network_id": token(network_id),
        "compiled_model_id": token(compiled_model_id),
        "violations": _sorted_tokens(violations),
    }
    event_id = "event.logic.compiled_invalid.{}".format(canonical_sha256(event_seed)[:16])
    return build_explain_artifact(
        explain_id="explain.logic_compiled_invalid.{}".format(canonical_sha256(event_seed)[:16]),
        event_id=event_id,
        target_id=token(network_id),
        cause_chain=["cause.logic.compiled_invalid"],
        remediation_hints=["recompile the network after topology or policy changes", "force expand to L1 for inspection"],
        extensions={"event_kind_id": "logic.compiled_invalid", "compiled_model_id": token(compiled_model_id), "violations": _sorted_tokens(violations)},
    )


def build_logic_compiled_introspection_artifact(
    *,
    tick: int,
    network_id: str,
    compiled_model_row: Mapping[str, object],
    measurement_artifact_id: str = "",
) -> dict:
    model_row = as_map(compiled_model_row)
    payload = as_map(as_map(model_row.get("compiled_payload_ref")).get("payload"))
    compiled_type_id = token(model_row.get("compiled_type_id"))
    excerpt: dict
    if compiled_type_id == "compiled.lookup_table":
        excerpt = {
            "table_rows": [
                {
                    "input_bits": token(row.get("input_bits")),
                    "output_hash": canonical_sha256(canon(as_list(row.get("element_results")))),
                }
                for row in as_list(payload.get("table_rows"))[:4]
                if isinstance(row, Mapping)
            ]
        }
    elif compiled_type_id == "compiled.automaton":
        excerpt = {
            "state_count": int(len(as_list(payload.get("states")))),
            "transition_rows": [
                {
                    "state_id": token(row.get("state_id")),
                    "input_bits": token(row.get("input_bits")),
                    "next_state_id": token(row.get("next_state_id")),
                }
                for row in as_list(payload.get("transition_rows"))[:4]
                if isinstance(row, Mapping)
            ],
        }
    else:
        excerpt = {
            "removed_node_ids": _sorted_tokens(as_list(payload.get("removed_node_ids")))[:4],
            "constant_bindings": canon(
                dict(list(sorted(as_map(payload.get("constant_bindings")).items(), key=lambda item: token(item[0])))[:4])
            ),
            "element_program_ids": [
                token(row.get("element_instance_id"))
                for row in as_list(payload.get("element_programs"))[:4]
                if isinstance(row, Mapping)
            ],
        }
    artifact = {
        "artifact_id": "artifact.logic.compiled_introspection.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, as_int(tick, 0))),
                    "network_id": token(network_id),
                    "compiled_model_id": token(model_row.get("compiled_model_id")),
                    "measurement_artifact_id": token(measurement_artifact_id),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.compiled_introspection",
        "network_id": token(network_id),
        "compiled_model_id": token(model_row.get("compiled_model_id")),
        "compiled_type_id": compiled_type_id,
        "tick": int(max(0, as_int(tick, 0))),
        "measurement_artifact_id": token(measurement_artifact_id) or None,
        "deterministic_fingerprint": "",
        "extensions": {
            "excerpt": excerpt,
            "source_hash": token(model_row.get("source_hash")),
            "trace_compactable": True,
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return artifact


__all__ = [
    "PROCESS_LOGIC_COMPILE_REQUEST",
    "REFUSAL_LOGIC_COMPILE_NETWORK_NOT_FOUND",
    "REFUSAL_LOGIC_COMPILE_NETWORK_NOT_VALIDATED",
    "REFUSAL_LOGIC_COMPILE_POLICY_UNREGISTERED",
    "REFUSAL_LOGIC_COMPILE_INELIGIBLE",
    "REFUSAL_LOGIC_COMPILED_INVALID",
    "build_logic_compile_policy_row",
    "normalize_logic_compile_policy_rows",
    "logic_compile_policy_rows_by_id",
    "compile_logic_network",
    "validate_logic_compiled_model",
    "execute_logic_compiled_model",
    "build_logic_controller_macro_capsule",
    "build_logic_controller_interface_signature_row",
    "build_logic_controller_system_bundle",
    "build_logic_compiled_introspection_artifact",
    "build_logic_compiled_forced_expand_event",
    "build_logic_compiled_invalid_explain_artifact",
]
