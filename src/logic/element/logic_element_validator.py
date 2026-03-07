"""LOGIC-2 deterministic logic element definition validators."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from src.system import state_vector_definition_rows_by_owner, validate_interface_signature
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_LOGIC_INVALID_ELEMENT_DEFINITION = "refusal.logic.invalid_element_definition"

_BEHAVIOR_KINDS = {"combinational", "sequential", "timer", "counter", "mux"}
_FORBIDDEN_PHYSICAL_TOKENS = (
    "voltage",
    "current",
    "ampere",
    "ohm",
    "pressure",
    "pascal",
    "joule",
    "watt",
    "quantity.energy",
    "quantity.force",
    "quantity.pressure",
    "quantity.pressure_head",
    "unit.j",
    "unit.w",
    "unit.pa",
)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(_token(item) for item in list(values or []) if _token(item)))


def _canon(value: object) -> object:
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if isinstance(value, float):
        return int(round(float(value)))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def _rows_from_payload(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
    body = _as_map(payload)
    for key in keys:
        rows = body.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def build_logic_element_definition_row(
    *,
    element_id: str,
    description: str,
    interface_signature_id: str,
    state_vector_definition_id: str,
    behavior_model_id: str,
    compute_cost_units: int,
    timing_policy_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "element_id": _token(element_id),
        "description": _token(description),
        "interface_signature_id": _token(interface_signature_id),
        "state_vector_definition_id": _token(state_vector_definition_id),
        "behavior_model_id": _token(behavior_model_id),
        "compute_cost_units": int(max(0, _as_int(compute_cost_units, 0))),
        "timing_policy_id": _token(timing_policy_id),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (
        (not payload["element_id"])
        or (not payload["description"])
        or (not payload["interface_signature_id"])
        or (not payload["state_vector_definition_id"])
        or (not payload["behavior_model_id"])
        or (not payload["timing_policy_id"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_element_definition_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("element_id"))):
        normalized = build_logic_element_definition_row(
            element_id=_token(row.get("element_id")),
            description=_token(row.get("description")),
            interface_signature_id=_token(row.get("interface_signature_id")),
            state_vector_definition_id=_token(row.get("state_vector_definition_id")),
            behavior_model_id=_token(row.get("behavior_model_id")),
            compute_cost_units=_as_int(row.get("compute_cost_units"), 0),
            timing_policy_id=_token(row.get("timing_policy_id")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        token = _token(normalized.get("element_id"))
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_behavior_model_row(
    *,
    behavior_model_id: str,
    model_kind: str,
    model_ref: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "behavior_model_id": _token(behavior_model_id),
        "model_kind": _token(model_kind).lower(),
        "model_ref": _canon(model_ref),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["behavior_model_id"]) or (payload["model_kind"] not in _BEHAVIOR_KINDS) or (not payload["model_ref"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_behavior_model_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("behavior_model_id"))):
        normalized = build_logic_behavior_model_row(
            behavior_model_id=_token(row.get("behavior_model_id")),
            model_kind=_token(row.get("model_kind")),
            model_ref=row.get("model_ref"),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        token = _token(normalized.get("behavior_model_id"))
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def build_state_machine_definition_row(
    *,
    sm_id: str,
    states: object,
    transition_rules: object,
    output_rules: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "sm_id": _token(sm_id),
        "states": [_canon(dict(item)) for item in sorted((dict(item) for item in _as_list(states) if isinstance(item, Mapping)), key=lambda item: _token(item.get("state_id")))],
        "transition_rules": [_canon(dict(item)) for item in sorted((dict(item) for item in _as_list(transition_rules) if isinstance(item, Mapping)), key=lambda item: _token(item.get("rule_id")))],
        "output_rules": [_canon(dict(item)) for item in sorted((dict(item) for item in _as_list(output_rules) if isinstance(item, Mapping)), key=lambda item: _token(item.get("rule_id")))],
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["sm_id"]) or (not payload["states"]) or (not payload["output_rules"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_state_machine_definition_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("sm_id"))):
        normalized = build_state_machine_definition_row(
            sm_id=_token(row.get("sm_id")),
            states=row.get("states"),
            transition_rules=row.get("transition_rules"),
            output_rules=row.get("output_rules"),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        token = _token(normalized.get("sm_id"))
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def _rows_by_id(rows: object, id_key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get(id_key))):
        token = _token(row.get(id_key))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _interface_rows_by_system(rows: object) -> Dict[str, dict]:
    return _rows_by_id(rows, "system_id")


def _port_type_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return _rows_by_id(_rows_from_payload(payload, ("port_types",)), "port_type_id")


def _string_tokens(value: object) -> List[str]:
    tokens: List[str] = []
    if isinstance(value, Mapping):
        for key in sorted(value.keys(), key=lambda item: str(item)):
            tokens.extend(_string_tokens(key))
            tokens.extend(_string_tokens(value[key]))
    elif isinstance(value, list):
        for item in list(value):
            tokens.extend(_string_tokens(item))
    elif isinstance(value, str):
        tokens.append(value)
    return tokens


def _physical_token_hits(*rows: object) -> List[str]:
    found = set()
    for row in rows:
        for token in _string_tokens(_canon(row)):
            token_lower = str(token or "").strip().lower()
            if not token_lower:
                continue
            for forbidden in _FORBIDDEN_PHYSICAL_TOKENS:
                if forbidden in token_lower:
                    found.add(forbidden)
    return sorted(found)


def validate_logic_element_definitions(
    *,
    logic_element_rows: object,
    logic_behavior_model_rows: object,
    state_machine_definition_rows: object,
    assembly_rows: object,
    interface_signature_rows: object,
    state_vector_definition_rows: object,
    quantity_bundle_registry_payload: Mapping[str, object] | None,
    spec_type_registry_payload: Mapping[str, object] | None,
    signal_channel_type_registry_payload: Mapping[str, object] | None,
    port_type_registry_payload: Mapping[str, object] | None,
) -> dict:
    normalized_elements = normalize_logic_element_definition_rows(logic_element_rows)
    normalized_behaviors = normalize_logic_behavior_model_rows(logic_behavior_model_rows)
    normalized_state_machines = normalize_state_machine_definition_rows(state_machine_definition_rows)
    normalized_assemblies = [dict(row) for row in _as_list(assembly_rows) if isinstance(row, Mapping)]
    normalized_interfaces = [dict(row) for row in _as_list(interface_signature_rows) if isinstance(row, Mapping)]
    behavior_by_id = _rows_by_id(normalized_behaviors, "behavior_model_id")
    state_machine_by_id = _rows_by_id(normalized_state_machines, "sm_id")
    assembly_by_id = _rows_by_id(normalized_assemblies, "assembly_id")
    interface_by_system = _interface_rows_by_system(normalized_interfaces)
    state_vector_by_owner = state_vector_definition_rows_by_owner(state_vector_definition_rows)
    port_type_by_id = _port_type_rows_by_id(port_type_registry_payload)

    checks: List[dict] = []
    failed_element_ids: List[str] = []

    for element_row in normalized_elements:
        element_id = _token(element_row.get("element_id"))
        behavior_row = dict(behavior_by_id.get(_token(element_row.get("behavior_model_id"))) or {})
        interface_row = dict(interface_by_system.get(element_id) or {})
        state_vector_row = dict(state_vector_by_owner.get(element_id) or {})
        assembly_id = _token(_as_map(element_row.get("extensions")).get("assembly_id")) or element_id
        assembly_row = dict(assembly_by_id.get(assembly_id) or {})
        state_vector_id = _token(_as_map(state_vector_row.get("extensions")).get("state_vector_definition_id"))
        element_failures: List[str] = []

        if not assembly_row:
            element_failures.append("assembly_missing")
        if not interface_row:
            element_failures.append("interface_missing")
        if not state_vector_row:
            element_failures.append("state_vector_missing")
        if not behavior_row:
            element_failures.append("behavior_model_missing")
        if int(max(0, _as_int(element_row.get("compute_cost_units"), 0))) <= 0:
            element_failures.append("compute_cost_missing")
        if state_vector_row and state_vector_id and state_vector_id != _token(element_row.get("state_vector_definition_id")):
            element_failures.append("state_vector_id_mismatch")

        if interface_row:
            port_list = [dict(item) for item in list(interface_row.get("port_list") or []) if isinstance(item, Mapping)]
            if not port_list:
                element_failures.append("port_list_missing")
            for port_row in port_list:
                port_type_row = dict(port_type_by_id.get(_token(port_row.get("port_type_id"))) or {})
                if not port_type_row:
                    element_failures.append("port_type_unregistered")
                    continue
                if _token(port_type_row.get("payload_kind")).lower() != "signal":
                    element_failures.append("nonsignal_port")
            interface_validation = validate_interface_signature(
                system_id=element_id,
                system_rows=[{"system_id": element_id}],
                interface_signature_rows=[interface_row],
                quantity_bundle_registry_payload=quantity_bundle_registry_payload,
                spec_type_registry_payload=spec_type_registry_payload,
                signal_channel_type_registry_payload=signal_channel_type_registry_payload,
            )
            if _token(interface_validation.get("result")) != "complete":
                element_failures.append("interface_signature_invalid")

        if behavior_row:
            model_ref = _as_map(behavior_row.get("model_ref"))
            if _token(behavior_row.get("model_kind")) in {"sequential", "timer", "counter", "mux"}:
                state_machine_id = _token(model_ref.get("ref_id"))
                if (not state_machine_id) or (state_machine_id not in state_machine_by_id):
                    element_failures.append("state_machine_missing")
            physical_hits = _physical_token_hits(element_row, behavior_row, state_machine_by_id.get(_token(model_ref.get("ref_id"))))
            if physical_hits:
                element_failures.append("physical_quantity_leak")

        checks.append(
            {
                "element_id": element_id,
                "status": "pass" if not element_failures else "fail",
                "failures": sorted(set(element_failures)),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "element_id": element_id,
                        "failures": sorted(set(element_failures)),
                    }
                ),
            }
        )
        if element_failures:
            failed_element_ids.append(element_id)

    checks = sorted(checks, key=lambda row: _token(row.get("element_id")))
    result = "complete" if normalized_elements and not failed_element_ids else "refused"
    return {
        "result": result,
        "reason_code": "" if result == "complete" else REFUSAL_LOGIC_INVALID_ELEMENT_DEFINITION,
        "checks": checks,
        "failed_element_ids": sorted(set(failed_element_ids)),
        "logic_element_rows": normalized_elements,
        "logic_behavior_model_rows": normalized_behaviors,
        "state_machine_definition_rows": normalized_state_machines,
        "deterministic_fingerprint": canonical_sha256(
            {
                "result": result,
                "failed_element_ids": sorted(set(failed_element_ids)),
                "checks": checks,
            }
        ),
    }


__all__ = [
    "REFUSAL_LOGIC_INVALID_ELEMENT_DEFINITION",
    "build_logic_element_definition_row",
    "normalize_logic_element_definition_rows",
    "build_logic_behavior_model_row",
    "normalize_logic_behavior_model_rows",
    "build_state_machine_definition_row",
    "normalize_state_machine_definition_rows",
    "validate_logic_element_definitions",
]
