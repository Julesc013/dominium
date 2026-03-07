"""Shared deterministic helpers for LOGIC-4 evaluation."""

from __future__ import annotations

import ast
import re
from typing import Dict, Iterable, List, Mapping, Sequence

from src.logic.signal.signal_store import normalize_signal_store_state
from tools.xstack.compatx.canonical_json import canonical_sha256


SCALAR_FIXED_ONE = 1000
_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\b")
_FUNCTION_REPLACEMENTS = {
    "and": "F_and",
    "or": "F_or",
    "not": "F_not",
    "xor": "F_xor",
    "gte": "F_gte",
    "pulse": "F_pulse",
    "min": "F_min",
    "normalize": "F_normalize",
}
_PRESERVED_NAMES = set(_FUNCTION_REPLACEMENTS.values()) | {"and", "or", "not", "True", "False"}


def as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def token(value: object) -> str:
    return str(value or "").strip()


def sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(token(item) for item in list(values or []) if token(item)))


def canon(value: object) -> object:
    if isinstance(value, Mapping):
        return dict((str(key), canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [canon(item) for item in value]
    if isinstance(value, float):
        return int(round(float(value)))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def rows_by_id(rows: object, id_key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: token(item.get(id_key))):
        row_id = token(row.get(id_key))
        if row_id:
            out[row_id] = dict(row)
    return dict((row_id, dict(out[row_id])) for row_id in sorted(out.keys()))


def slot_key(*, network_id: str, element_id: str, port_id: str) -> str:
    return "|".join((token(network_id), token(element_id), token(port_id)))


def slot_from_signal_row(signal_row: Mapping[str, object]) -> str:
    slot = as_map(as_map(signal_row.get("extensions")).get("slot"))
    return slot_key(
        network_id=token(slot.get("network_id")),
        element_id=token(slot.get("element_id")),
        port_id=token(slot.get("port_id")),
    )


def active_signal_for_slot(
    *,
    signal_store_state: Mapping[str, object] | None,
    network_id: str,
    element_id: str,
    port_id: str,
    tick: int,
) -> dict:
    state = normalize_signal_store_state(signal_store_state)
    selected = {}
    target_slot = slot_key(network_id=network_id, element_id=element_id, port_id=port_id)
    target_tick = int(max(0, as_int(tick, 0)))
    for row in state.get("signal_rows") or []:
        if slot_from_signal_row(row) != target_slot:
            continue
        start_tick = as_int(row.get("valid_from_tick", 0), 0)
        end_tick = row.get("valid_until_tick")
        end_value = None if end_tick is None else as_int(end_tick, start_tick)
        if start_tick > target_tick or (end_value is not None and target_tick >= end_value):
            continue
        if (not selected) or (
            as_int(selected.get("valid_from_tick", 0), 0),
            token(selected.get("signal_id")),
        ) <= (start_tick, token(row.get("signal_id"))):
            selected = dict(row)
    return selected


def value_ref_to_scalar(value_ref: Mapping[str, object]) -> int:
    row = as_map(value_ref)
    kind = token(row.get("value_kind"))
    if kind == "boolean":
        return 1 if bool(as_int(row.get("value", 0), 0)) else 0
    if kind == "scalar":
        return int(as_int(row.get("value_fixed", 0), 0))
    if kind == "pulse":
        return 1 if as_list(row.get("edges")) else 0
    if kind == "message":
        return int(canonical_sha256(row)[:8], 16)
    if kind == "bus":
        packed = row.get("packed_fixed")
        if packed is not None:
            return int(as_int(packed, 0))
        return int(canonical_sha256(row)[:8], 16)
    return 0


def pulse_present(value_ref: Mapping[str, object]) -> bool:
    row = as_map(value_ref)
    return token(row.get("value_kind")) == "pulse" and bool(as_list(row.get("edges")))


def default_value_ref(*, signal_type_id: str, bus_id: str | None = None) -> dict:
    kind = token(signal_type_id)
    if kind == "signal.scalar":
        payload = {"value_kind": "scalar", "value_fixed": 0, "units_id": None}
    elif kind == "signal.pulse":
        payload = {"value_kind": "pulse", "edges": []}
    elif kind == "signal.message":
        payload = {"value_kind": "message", "artifact_id": "artifact.logic.message.null", "receipt_id": None, "receipt_metadata": {}}
    elif kind == "signal.bus":
        payload = {
            "value_kind": "bus",
            "bus_id": token(bus_id) or "bus.logic.default",
            "encoding_id": "encoding.struct",
            "width": None,
            "sub_signals": [],
            "packed_fixed": None,
        }
    else:
        payload = {"value_kind": "boolean", "value": 0}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def signal_type_id_for_port(
    *,
    node_id: str,
    direction: str,
    graph_row: Mapping[str, object],
    element_row: Mapping[str, object],
    interface_row: Mapping[str, object],
) -> str:
    graph = as_map(graph_row)
    candidates: List[str] = []
    for edge in as_list(graph.get("edges")):
        if not isinstance(edge, Mapping):
            continue
        payload = as_map(edge.get("payload"))
        signal_type_id = token(payload.get("signal_type_id"))
        if not signal_type_id:
            continue
        if direction == "in" and token(edge.get("to_node_id")) == node_id:
            candidates.append(signal_type_id)
        elif direction == "out" and token(edge.get("from_node_id")) == node_id:
            candidates.append(signal_type_id)
    if candidates:
        return sorted_tokens(candidates)[0]
    element_signals = sorted_tokens(as_map(element_row.get("extensions")).get("signal_type_ids"))
    if len(element_signals) == 1:
        return element_signals[0]
    interface_signals = sorted_tokens(as_map(interface_row.get("extensions")).get("signal_type_ids"))
    if interface_signals:
        return interface_signals[0]
    return "signal.boolean"


def fixed_ticks_for_element(
    *,
    element_row: Mapping[str, object],
    interface_row: Mapping[str, object],
    graph_node_payload: Mapping[str, object] | None = None,
) -> int:
    sources = (
        as_map(as_map(element_row).get("extensions")),
        as_map(as_map(interface_row).get("extensions")),
        as_map(as_map(graph_node_payload).get("extensions")),
    )
    for source in sources:
        for key in ("fixed_ticks", "delay_ticks", "timer_ticks"):
            if key in source:
                return int(max(1, as_int(source.get(key), 1)))
    return 1


def materialize_logic_instance_state_definition(
    *,
    element_instance_id: str,
    element_definition_id: str,
    model_kind: str,
    state_machine_row: Mapping[str, object] | None,
    state_vector_definition_rows: object,
    build_state_vector_definition_row,
) -> dict:
    definitions_by_owner = rows_by_id(state_vector_definition_rows, "owner_id")
    direct = dict(definitions_by_owner.get(token(element_instance_id)) or {})
    if direct:
        return direct
    base = dict(definitions_by_owner.get(token(element_definition_id)) or {})
    base_fields = [dict(item) for item in as_list(base.get("state_fields")) if isinstance(item, Mapping)]
    if token(model_kind) in {"sequential", "timer", "counter"}:
        state_ids = [token(row.get("state_id")) for row in as_list(as_map(state_machine_row).get("states")) if isinstance(row, Mapping)]
        if state_ids and "logic_state_id" not in {token(item.get("field_id")) for item in base_fields}:
            base_fields.append(
                {
                    "field_id": "logic_state_id",
                    "path": "logic_state_id",
                    "field_kind": "text",
                    "default": state_ids[0],
                    "extensions": {"runtime_materialized": True},
                }
            )
    row = build_state_vector_definition_row(
        owner_id=token(element_instance_id),
        version=token(base.get("version")) or "1.0.0",
        state_fields=base_fields,
        deterministic_fingerprint="",
        extensions=dict(
            as_map(base.get("extensions")),
            source="LOGIC4-5",
            materialized_from=token(element_definition_id),
        ),
    )
    return row


def default_state_for_definition(definition_row: Mapping[str, object]) -> dict:
    out: Dict[str, object] = {}
    for field in sorted((dict(item) for item in as_list(as_map(definition_row).get("state_fields")) if isinstance(item, Mapping)), key=lambda item: token(item.get("field_id"))):
        path = token(field.get("path")) or token(field.get("field_id"))
        if path:
            out[path] = canon(field.get("default"))
    return out


def transform_expression(expression: str) -> str:
    value = str(expression or "").strip()
    if not value:
        return "0"
    for source, target in _FUNCTION_REPLACEMENTS.items():
        value = re.sub(r"\b{}\s*\(".format(re.escape(source)), "{}(".format(target), value)

    def replace_identifier(match: re.Match[str]) -> str:
        symbol = str(match.group(0) or "")
        if symbol in _PRESERVED_NAMES:
            return symbol
        if symbol.startswith("F_"):
            return symbol
        return 'V("{}")'.format(symbol)

    return _IDENTIFIER_RE.sub(replace_identifier, value)


def evaluate_expression(
    *,
    expression: str,
    inputs: Mapping[str, Mapping[str, object]],
    state_values: Mapping[str, object],
    delay_fixed_ticks: int,
) -> object:
    transformed = transform_expression(expression)
    tree = ast.parse(transformed, mode="eval")

    def lookup(name: str) -> object:
        symbol = token(name)
        if symbol.startswith("in."):
            return value_ref_to_scalar(as_map(inputs.get(symbol)))
        if symbol == "delay.fixed_ticks":
            return int(max(1, as_int(delay_fixed_ticks, 1)))
        return canon(as_map(state_values).get(symbol, 0) if isinstance(as_map(state_values).get(symbol, 0), Mapping) else state_values.get(symbol, 0))

    def call_function(name: str, args: Sequence[object]) -> object:
        if name == "V":
            return lookup(str(args[0] if args else ""))
        if name == "F_and":
            return 1 if all(bool(as_int(arg, 0)) for arg in args) else 0
        if name == "F_or":
            return 1 if any(bool(as_int(arg, 0)) for arg in args) else 0
        if name == "F_not":
            return 0 if bool(as_int(args[0] if args else 0, 0)) else 1
        if name == "F_xor":
            values = [bool(as_int(arg, 0)) for arg in args]
            return 1 if sum(1 for item in values if item) % 2 == 1 else 0
        if name == "F_gte":
            left = as_int(args[0] if len(args) > 0 else 0, 0)
            right = as_int(args[1] if len(args) > 1 else 0, 0)
            return 1 if left >= right else 0
        if name == "F_pulse":
            signal_name = str(args[0] if args else "")
            return 1 if pulse_present(as_map(inputs.get(signal_name))) else 0
        if name == "F_min":
            return min(as_int(args[0] if len(args) > 0 else 0, 0), as_int(args[1] if len(args) > 1 else 0, 0))
        if name == "F_normalize":
            value = as_int(args[0] if len(args) > 0 else 0, 0)
            floor = as_int(args[1] if len(args) > 1 else 0, 0)
            ceiling = as_int(args[2] if len(args) > 2 else 0, 0)
            if ceiling <= floor:
                return 0
            clamped = min(max(value, floor), ceiling)
            return int(((clamped - floor) * SCALAR_FIXED_ONE) // max(1, ceiling - floor))
        raise ValueError("unsupported logic expression function '{}'".format(name))

    def eval_node(node: ast.AST) -> object:
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant):
            return canon(node.value)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("unsupported call target")
            return call_function(node.func.id, [eval_node(arg) for arg in node.args])
        if isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if isinstance(node.op, ast.Not):
                return not bool(as_int(operand, 0))
            if isinstance(node.op, ast.USub):
                return -as_int(operand, 0)
            raise ValueError("unsupported unary operator")
        if isinstance(node, ast.BoolOp):
            values = [bool(as_int(eval_node(item), 0)) for item in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
            raise ValueError("unsupported boolean operator")
        if isinstance(node, ast.BinOp):
            left = as_int(eval_node(node.left), 0)
            right = as_int(eval_node(node.right), 0)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            raise ValueError("unsupported binary operator")
        if isinstance(node, ast.Compare):
            left = eval_node(node.left)
            comparisons = zip(node.ops, node.comparators)
            current = left
            result = True
            for op, comparator in comparisons:
                right = eval_node(comparator)
                if isinstance(op, ast.Eq):
                    result = result and (current == right)
                elif isinstance(op, ast.NotEq):
                    result = result and (current != right)
                elif isinstance(op, ast.Gt):
                    result = result and (as_int(current, 0) > as_int(right, 0))
                elif isinstance(op, ast.GtE):
                    result = result and (as_int(current, 0) >= as_int(right, 0))
                elif isinstance(op, ast.Lt):
                    result = result and (as_int(current, 0) < as_int(right, 0))
                elif isinstance(op, ast.LtE):
                    result = result and (as_int(current, 0) <= as_int(right, 0))
                else:
                    raise ValueError("unsupported comparator")
                current = right
            return result
        raise ValueError("unsupported logic expression node '{}'".format(type(node).__name__))

    return eval_node(tree)


def to_value_payload(*, signal_type_id: str, evaluated_value: object, bus_id: str | None = None) -> dict:
    signal_kind = token(signal_type_id)
    if signal_kind == "signal.scalar":
        return {"value_fixed": int(as_int(evaluated_value, 0))}
    if signal_kind == "signal.pulse":
        if isinstance(evaluated_value, Mapping):
            return canon(as_map(evaluated_value))
        if isinstance(evaluated_value, list):
            return {"edges": canon(as_list(evaluated_value))}
        return {
            "edges": (
                [{"tick_offset": 0, "edge_kind": "rising"}]
                if bool(as_int(evaluated_value, 0))
                else []
            )
        }
    if signal_kind == "signal.message":
        payload = as_map(evaluated_value)
        return {
            "artifact_id": token(payload.get("artifact_id")) or "artifact.logic.message.null",
            "receipt_id": None if payload.get("receipt_id") is None else token(payload.get("receipt_id")) or None,
            "receipt_metadata": canon(as_map(payload.get("receipt_metadata"))),
        }
    if signal_kind == "signal.bus":
        payload = as_map(evaluated_value)
        return {
            "bus_id": token(payload.get("bus_id")) or token(bus_id) or "bus.logic.default",
            "encoding_id": token(payload.get("encoding_id")) or "encoding.struct",
            "width": payload.get("width"),
            "sub_signals": canon(as_list(payload.get("sub_signals"))),
            "packed_fixed": payload.get("packed_fixed"),
        }
    return {"value": 1 if bool(as_int(evaluated_value, 0)) else 0}


__all__ = [
    "SCALAR_FIXED_ONE",
    "active_signal_for_slot",
    "as_int",
    "as_list",
    "as_map",
    "canon",
    "default_state_for_definition",
    "default_value_ref",
    "evaluate_expression",
    "fixed_ticks_for_element",
    "materialize_logic_instance_state_definition",
    "pulse_present",
    "rows_by_id",
    "signal_type_id_for_port",
    "slot_from_signal_row",
    "slot_key",
    "sorted_tokens",
    "to_value_payload",
    "token",
    "value_ref_to_scalar",
]
