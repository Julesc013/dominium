"""Deterministic CTRL-7 capability query engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def capability_rows_by_id(capability_registry: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = dict(capability_registry or {})
    rows = payload.get("capabilities")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("capabilities")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("capability_id", ""))):
        capability_id = str(row.get("capability_id", "")).strip() or str(row.get("id", "")).strip()
        if not capability_id:
            continue
        out[capability_id] = {
            "schema_version": "1.0.0",
            "capability_id": capability_id,
            "description": str(row.get("description", "")).strip(),
            "applicable_entity_kinds": _sorted_unique_strings(row.get("applicable_entity_kinds")),
            "parameters_schema_id": (
                str(row.get("parameters_schema_id", "")).strip()
                if str(row.get("parameters_schema_id", "")).strip()
                else None
            ),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def normalize_capability_binding_rows(rows: object) -> List[dict]:
    source_rows = []
    if isinstance(rows, list):
        source_rows = [dict(item) for item in rows if isinstance(item, Mapping)]
    out: List[dict] = []
    for row in source_rows:
        entity_id = str(row.get("entity_id", "")).strip()
        capability_id = str(row.get("capability_id", "")).strip()
        if not entity_id or not capability_id:
            continue
        parameters = _as_map(row.get("parameters"))
        extensions = _as_map(row.get("extensions"))
        created_tick = int(max(0, _as_int(row.get("created_tick", 0), 0)))
        binding_id = str(row.get("binding_id", "")).strip()
        if not binding_id:
            binding_id = "cap.bind.{}".format(
                canonical_sha256(
                    {
                        "entity_id": entity_id,
                        "capability_id": capability_id,
                        "parameters": dict(parameters),
                        "created_tick": int(created_tick),
                    }
                )[:16]
            )
        normalized = {
            "schema_version": "1.0.0",
            "binding_id": binding_id,
            "entity_id": entity_id,
            "capability_id": capability_id,
            "parameters": dict(parameters),
            "created_tick": int(created_tick),
            "deterministic_fingerprint": "",
            "extensions": dict(extensions),
        }
        seed = dict(normalized)
        seed["deterministic_fingerprint"] = ""
        normalized["deterministic_fingerprint"] = canonical_sha256(seed)
        out.append(normalized)
    return sorted(
        out,
        key=lambda row: (
            str(row.get("entity_id", "")),
            str(row.get("capability_id", "")),
            str(row.get("binding_id", "")),
        ),
    )


def capability_binding_rows(capability_binding_payload: object) -> List[dict]:
    if isinstance(capability_binding_payload, list):
        return normalize_capability_binding_rows(capability_binding_payload)
    payload = _as_map(capability_binding_payload)
    for key in ("capability_bindings", "bindings"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return normalize_capability_binding_rows(rows)
    record = _as_map(payload.get("record"))
    for key in ("capability_bindings", "bindings"):
        rows = record.get(key)
        if isinstance(rows, list):
            return normalize_capability_binding_rows(rows)
    return []


def has_capability(
    *,
    entity_id: str,
    capability_id: str,
    capability_bindings: object,
) -> bool:
    entity_token = str(entity_id or "").strip()
    capability_token = str(capability_id or "").strip()
    if not entity_token or not capability_token:
        return False
    rows = capability_binding_rows(capability_bindings)
    for row in rows:
        if str(row.get("entity_id", "")).strip() != entity_token:
            continue
        if str(row.get("capability_id", "")).strip() == capability_token:
            return True
    return False


def get_capability_params(
    *,
    entity_id: str,
    capability_id: str,
    capability_bindings: object,
) -> dict:
    entity_token = str(entity_id or "").strip()
    capability_token = str(capability_id or "").strip()
    if not entity_token or not capability_token:
        return {}
    merged: dict = {}
    rows = capability_binding_rows(capability_bindings)
    for row in rows:
        if str(row.get("entity_id", "")).strip() != entity_token:
            continue
        if str(row.get("capability_id", "")).strip() != capability_token:
            continue
        params = _as_map(row.get("parameters"))
        for key in sorted(params.keys(), key=lambda item: str(item)):
            merged[str(key)] = params[key]
    return merged


def resolve_missing_capabilities(
    *,
    entity_id: str,
    required_capabilities: object,
    capability_bindings: object,
) -> List[str]:
    entity_token = str(entity_id or "").strip()
    if not entity_token:
        return _sorted_unique_strings(required_capabilities)
    missing: List[str] = []
    for capability_id in _sorted_unique_strings(required_capabilities):
        if has_capability(
            entity_id=entity_token,
            capability_id=capability_id,
            capability_bindings=capability_bindings,
        ):
            continue
        missing.append(capability_id)
    return sorted(missing)


__all__ = [
    "capability_binding_rows",
    "capability_rows_by_id",
    "get_capability_params",
    "has_capability",
    "normalize_capability_binding_rows",
    "resolve_missing_capabilities",
]
