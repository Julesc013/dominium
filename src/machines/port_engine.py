"""Deterministic ACT-4 machine port normalization and mutation helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple


REFUSAL_PORT_FULL = "refusal.port.full"
REFUSAL_PORT_MATERIAL_NOT_ACCEPTED = "refusal.port.material_not_accepted"
REFUSAL_PORT_EMPTY = "refusal.port.empty"
REFUSAL_PORT_FORBIDDEN_BY_LAW = "refusal.port.forbidden_by_law"


class PortError(ValueError):
    """Deterministic machine-port refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _normalize_content_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[Tuple[str, str], int] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: (str(item.get("batch_id", "")), str(item.get("material_id", "")))):
        batch_id = str(row.get("batch_id", "")).strip()
        material_id = str(row.get("material_id", "")).strip()
        mass = max(0, _as_int(row.get("mass", 0), 0))
        if not batch_id or not material_id or mass <= 0:
            continue
        key = (batch_id, material_id)
        out[key] = int(out.get(key, 0)) + int(mass)
    return [
        {
            "batch_id": str(key[0]),
            "material_id": str(key[1]),
            "mass": int(out[key]),
        }
        for key in sorted(out.keys())
    ]


def port_total_mass(port_row: Mapping[str, object]) -> int:
    total = 0
    for row in _normalize_content_rows((dict(port_row or {})).get("current_contents")):
        total += max(0, _as_int(row.get("mass", 0), 0))
    return int(total)


def normalize_port_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    port_id = str(payload.get("port_id", "")).strip()
    if not port_id:
        raise PortError(
            REFUSAL_PORT_FORBIDDEN_BY_LAW,
            "port row missing port_id",
            {"field": "port_id"},
        )
    machine_id_raw = payload.get("machine_id")
    machine_id = None if machine_id_raw is None else str(machine_id_raw).strip() or None
    parent_raw = payload.get("parent_structure_id")
    parent_structure_id = None if parent_raw is None else str(parent_raw).strip() or None
    if not machine_id and not parent_structure_id:
        raise PortError(
            REFUSAL_PORT_FORBIDDEN_BY_LAW,
            "port row must include machine_id or parent_structure_id",
            {"port_id": port_id},
        )
    port_type_id = str(payload.get("port_type_id", "")).strip()
    if not port_type_id:
        raise PortError(
            REFUSAL_PORT_FORBIDDEN_BY_LAW,
            "port row missing port_type_id",
            {"port_id": port_id},
        )
    capacity_raw = payload.get("capacity_mass")
    capacity_mass = None
    if capacity_raw is not None:
        capacity_mass = max(0, _as_int(capacity_raw, 0))
    return {
        "schema_version": "1.0.0",
        "port_id": port_id,
        "machine_id": machine_id,
        "parent_structure_id": parent_structure_id,
        "port_type_id": port_type_id,
        "accepted_material_tags": _sorted_unique_strings(payload.get("accepted_material_tags")),
        "accepted_material_ids": _sorted_unique_strings(payload.get("accepted_material_ids")),
        "capacity_mass": capacity_mass,
        "current_contents": _normalize_content_rows(payload.get("current_contents")),
        "connected_to": None if payload.get("connected_to") is None else str(payload.get("connected_to", "")).strip() or None,
        "visibility_policy_id": None if payload.get("visibility_policy_id") is None else str(payload.get("visibility_policy_id", "")).strip() or None,
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_machine_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    machine_id = str(payload.get("machine_id", "")).strip()
    machine_type_id = str(payload.get("machine_type_id", "")).strip()
    if not machine_id or not machine_type_id:
        raise PortError(
            REFUSAL_PORT_FORBIDDEN_BY_LAW,
            "machine row missing machine_id or machine_type_id",
            {"machine_id": machine_id, "machine_type_id": machine_type_id},
        )
    operational_state = str(payload.get("operational_state", "idle")).strip() or "idle"
    if operational_state not in ("idle", "running", "blocked", "failed"):
        operational_state = "idle"
    return {
        "schema_version": "1.0.0",
        "machine_id": machine_id,
        "machine_type_id": machine_type_id,
        "ports": _sorted_unique_strings(payload.get("ports")),
        "operational_state": operational_state,
        "policy_ids": _sorted_unique_strings(payload.get("policy_ids")),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_port_connection_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    connection_id = str(payload.get("connection_id", "")).strip()
    from_port_id = str(payload.get("from_port_id", "")).strip()
    if not connection_id or not from_port_id:
        raise PortError(
            REFUSAL_PORT_FORBIDDEN_BY_LAW,
            "port connection missing connection_id or from_port_id",
            {"connection_id": connection_id, "from_port_id": from_port_id},
        )
    to_port_id = None if payload.get("to_port_id") is None else str(payload.get("to_port_id", "")).strip() or None
    logistics_node_id = (
        None
        if payload.get("logistics_node_id") is None
        else str(payload.get("logistics_node_id", "")).strip() or None
    )
    if bool(to_port_id) == bool(logistics_node_id):
        raise PortError(
            REFUSAL_PORT_FORBIDDEN_BY_LAW,
            "port connection must target either to_port_id or logistics_node_id",
            {"connection_id": connection_id},
        )
    connection_kind = str(payload.get("connection_kind", "direct")).strip() or "direct"
    if connection_kind not in ("direct", "pipe", "wire", "hose"):
        connection_kind = "direct"
    return {
        "schema_version": "1.0.0",
        "connection_id": connection_id,
        "from_port_id": from_port_id,
        "to_port_id": to_port_id,
        "logistics_node_id": logistics_node_id,
        "connection_kind": connection_kind,
        "created_tick": max(0, _as_int(payload.get("created_tick", 0), 0)),
        "active": bool(payload.get("active", False)),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_port_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("port_id", ""))):
        normalized = normalize_port_row(row)
        out[str(normalized.get("port_id", ""))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_machine_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("machine_id", ""))):
        normalized = normalize_machine_row(row)
        out[str(normalized.get("machine_id", ""))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_port_connection_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("connection_id", ""))):
        normalized = normalize_port_connection_row(row)
        out[str(normalized.get("connection_id", ""))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def port_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_port_rows(rows):
        out[str(row.get("port_id", ""))] = dict(row)
    return out


def machine_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_machine_rows(rows):
        out[str(row.get("machine_id", ""))] = dict(row)
    return out


def port_connection_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_port_connection_rows(rows):
        out[str(row.get("connection_id", ""))] = dict(row)
    return out


def port_rows_for_machine(port_rows: object, machine_id: str) -> List[dict]:
    token = str(machine_id).strip()
    if not token:
        return []
    rows = []
    for row in normalize_port_rows(port_rows):
        if str(row.get("machine_id", "")).strip() == token:
            rows.append(dict(row))
    return sorted(rows, key=lambda item: str(item.get("port_id", "")))


def material_tag_index(material_registry_payload: Mapping[str, object] | None) -> Dict[str, List[str]]:
    root = dict(material_registry_payload or {})
    rows = root.get("materials")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("materials")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, List[str]] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("material_id", ""))):
        material_id = str(row.get("material_id", "")).strip()
        if not material_id:
            continue
        out[material_id] = _sorted_unique_strings(row.get("tags"))
    return out


def port_type_rows_by_id(port_type_registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(port_type_registry_payload or {})
    rows = root.get("port_types")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("port_types")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("port_type_id", ""))):
        port_type_id = str(row.get("port_type_id", "")).strip()
        if not port_type_id:
            continue
        out[port_type_id] = {
            "schema_version": "1.0.0",
            "port_type_id": port_type_id,
            "description": str(row.get("description", "")).strip(),
            "direction": str(row.get("direction", "")).strip() or "in",
            "payload_kind": str(row.get("payload_kind", "")).strip() or "material",
            "extensions": dict(row.get("extensions") or {}),
        }
    return out


def machine_type_rows_by_id(machine_type_registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(machine_type_registry_payload or {})
    rows = root.get("machine_types")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("machine_types")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("machine_type_id", ""))):
        machine_type_id = str(row.get("machine_type_id", "")).strip()
        if not machine_type_id:
            continue
        out[machine_type_id] = {
            "schema_version": "1.0.0",
            "machine_type_id": machine_type_id,
            "description": str(row.get("description", "")).strip(),
            "required_ports": _sorted_unique_strings(row.get("required_ports")),
            "supported_process_ids": _sorted_unique_strings(row.get("supported_process_ids")),
            "default_rate_params": dict(row.get("default_rate_params") or {}),
            "extensions": dict(row.get("extensions") or {}),
        }
    return out


def machine_operation_rows_by_id(machine_operation_registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(machine_operation_registry_payload or {})
    rows = root.get("operations")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("operations")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("operation_id", ""))):
        operation_id = str(row.get("operation_id", "")).strip()
        if not operation_id:
            continue
        input_materials = {
            str(key).strip(): max(0, _as_int(value, 0))
            for key, value in sorted((dict(row.get("input_materials") or {})).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        }
        output_materials = {
            str(key).strip(): max(0, _as_int(value, 0))
            for key, value in sorted((dict(row.get("output_materials") or {})).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        }
        out[operation_id] = {
            "schema_version": "1.0.0",
            "operation_id": operation_id,
            "description": str(row.get("description", "")).strip(),
            "machine_type_ids": _sorted_unique_strings(row.get("machine_type_ids")),
            "input_materials": input_materials,
            "output_materials": output_materials,
            "energy_delta_raw": _as_int(row.get("energy_delta_raw", 0), 0),
            "extensions": dict(row.get("extensions") or {}),
        }
    return out


def validate_port_accepts_material(
    *,
    port_row: Mapping[str, object],
    material_id: str,
    material_tags: List[str] | None = None,
) -> None:
    port = normalize_port_row(port_row)
    material_token = str(material_id).strip()
    if not material_token:
        raise PortError(
            REFUSAL_PORT_MATERIAL_NOT_ACCEPTED,
            "material_id is required for port transfer",
            {"port_id": str(port.get("port_id", ""))},
        )
    accepted_ids = set(_sorted_unique_strings(port.get("accepted_material_ids")))
    if accepted_ids and material_token not in accepted_ids:
        raise PortError(
            REFUSAL_PORT_MATERIAL_NOT_ACCEPTED,
            "material is not accepted by port accepted_material_ids",
            {"port_id": str(port.get("port_id", "")), "material_id": material_token},
        )
    accepted_tags = set(_sorted_unique_strings(port.get("accepted_material_tags")))
    if accepted_tags:
        row_tags = set(_sorted_unique_strings(material_tags))
        if not row_tags.intersection(accepted_tags):
            raise PortError(
                REFUSAL_PORT_MATERIAL_NOT_ACCEPTED,
                "material tags do not satisfy port accepted_material_tags",
                {
                    "port_id": str(port.get("port_id", "")),
                    "material_id": material_token,
                },
            )


def insert_into_port(
    *,
    port_row: Mapping[str, object],
    batch_id: str,
    material_id: str,
    mass: int,
    material_tags: List[str] | None = None,
) -> dict:
    port = normalize_port_row(port_row)
    batch_token = str(batch_id).strip()
    material_token = str(material_id).strip()
    mass_raw = max(0, _as_int(mass, 0))
    if not batch_token or not material_token or mass_raw <= 0:
        raise PortError(
            REFUSAL_PORT_MATERIAL_NOT_ACCEPTED,
            "insert_into_port requires batch_id, material_id, and mass > 0",
            {"port_id": str(port.get("port_id", ""))},
        )
    validate_port_accepts_material(port_row=port, material_id=material_token, material_tags=material_tags)
    current_total = port_total_mass(port)
    capacity_mass = port.get("capacity_mass")
    if capacity_mass is not None and current_total + mass_raw > max(0, _as_int(capacity_mass, 0)):
        raise PortError(
            REFUSAL_PORT_FULL,
            "port capacity exceeded",
            {
                "port_id": str(port.get("port_id", "")),
                "capacity_mass": str(max(0, _as_int(capacity_mass, 0))),
                "requested_mass": str(mass_raw),
            },
        )
    entries = _normalize_content_rows(port.get("current_contents"))
    merged: Dict[Tuple[str, str], int] = {}
    for row in entries:
        key = (str(row.get("batch_id", "")), str(row.get("material_id", "")))
        merged[key] = int(max(0, _as_int(row.get("mass", 0), 0)))
    key = (batch_token, material_token)
    merged[key] = int(merged.get(key, 0)) + int(mass_raw)
    port["current_contents"] = [
        {
            "batch_id": str(token[0]),
            "material_id": str(token[1]),
            "mass": int(merged[token]),
        }
        for token in sorted(merged.keys())
        if int(merged[token]) > 0
    ]
    return port


def extract_from_port(
    *,
    port_row: Mapping[str, object],
    mass: int,
    batch_id: str = "",
    material_id: str = "",
) -> Tuple[dict, List[dict]]:
    port = normalize_port_row(port_row)
    mass_raw = max(0, _as_int(mass, 0))
    if mass_raw <= 0:
        raise PortError(
            REFUSAL_PORT_EMPTY,
            "extract_from_port requires mass > 0",
            {"port_id": str(port.get("port_id", ""))},
        )
    rows = _normalize_content_rows(port.get("current_contents"))
    if not rows:
        raise PortError(
            REFUSAL_PORT_EMPTY,
            "port has no contents to extract",
            {"port_id": str(port.get("port_id", ""))},
        )
    batch_filter = str(batch_id).strip()
    material_filter = str(material_id).strip()
    candidates = []
    for row in rows:
        if batch_filter and str(row.get("batch_id", "")) != batch_filter:
            continue
        if material_filter and str(row.get("material_id", "")) != material_filter:
            continue
        candidates.append(dict(row))
    if not candidates:
        raise PortError(
            REFUSAL_PORT_EMPTY,
            "requested batch/material not present in port",
            {
                "port_id": str(port.get("port_id", "")),
                "batch_id": batch_filter,
                "material_id": material_filter,
            },
        )
    remaining = int(mass_raw)
    extracted: List[dict] = []
    rows_by_key: Dict[Tuple[str, str], int] = {
        (str(row.get("batch_id", "")), str(row.get("material_id", ""))): int(max(0, _as_int(row.get("mass", 0), 0)))
        for row in rows
    }
    for row in sorted(candidates, key=lambda item: (str(item.get("batch_id", "")), str(item.get("material_id", "")))):
        if remaining <= 0:
            break
        key = (str(row.get("batch_id", "")), str(row.get("material_id", "")))
        available = int(rows_by_key.get(key, 0))
        if available <= 0:
            continue
        taken = min(available, remaining)
        rows_by_key[key] = int(available - taken)
        remaining -= int(taken)
        extracted.append(
            {
                "batch_id": str(key[0]),
                "material_id": str(key[1]),
                "mass": int(taken),
            }
        )
    if remaining > 0:
        raise PortError(
            REFUSAL_PORT_EMPTY,
            "port does not contain requested extraction mass",
            {
                "port_id": str(port.get("port_id", "")),
                "requested_mass": str(mass_raw),
                "available_mass": str(mass_raw - remaining),
            },
        )
    port["current_contents"] = [
        {
            "batch_id": str(key[0]),
            "material_id": str(key[1]),
            "mass": int(rows_by_key[key]),
        }
        for key in sorted(rows_by_key.keys())
        if int(rows_by_key[key]) > 0
    ]
    return port, extracted