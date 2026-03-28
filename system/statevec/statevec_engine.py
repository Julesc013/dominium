"""STATEVEC-0 deterministic explicit state-vector helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_STATEVEC_INVALID = "refusal.statevec.invalid"
REFUSAL_STATEVEC_MISSING_DEFINITION = "refusal.statevec.missing_definition"
REFUSAL_STATEVEC_VERSION_MISMATCH = "refusal.statevec.version_mismatch"
REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD = "refusal.statevec.undeclared_output_field"
REFUSAL_STATEVEC_MIGRATION_UNAVAILABLE = "refusal.statevec.migration_unavailable"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _class_default_owner_id(owner_id: str) -> str:
    token = str(owner_id or "").strip()
    if token.startswith("system."):
        return "system.macro_capsule_default"
    if token.startswith("process."):
        return "process.process_capsule_default"
    if token.startswith("compiled."):
        return "compiled.compiled_model_default"
    if token.startswith("compiled_model."):
        return "compiled.compiled_model_default"
    return ""


def _normalize_value(value: object) -> object:
    if isinstance(value, Mapping):
        return dict((str(key), _normalize_value(val)) for key, val in sorted(dict(value).items(), key=lambda item: str(item[0])))
    if isinstance(value, list):
        return [_normalize_value(item) for item in list(value)]
    if isinstance(value, float):
        # Authoritative state vectors normalize float-like values into deterministic integer lattice.
        return int(round(float(value)))
    return value


def state_vector_definition_for_owner(
    *,
    owner_id: str,
    state_vector_definition_rows: object,
) -> dict:
    owner_token = str(owner_id or "").strip()
    if not owner_token:
        return {}
    by_owner = state_vector_definition_rows_by_owner(state_vector_definition_rows)
    direct = dict(by_owner.get(owner_token) or {})
    if direct:
        return direct
    fallback_owner_id = _class_default_owner_id(owner_token)
    fallback = dict(by_owner.get(fallback_owner_id) or {})
    if not fallback:
        return {}
    copied = build_state_vector_definition_row(
        owner_id=owner_token,
        version=str(fallback.get("version", "")).strip() or "1.0.0",
        state_fields=list(fallback.get("state_fields") or []),
        deterministic_fingerprint="",
        extensions=dict(_as_map(fallback.get("extensions")), owner_class_default_id=fallback_owner_id),
    )
    return dict(copied or {})


def build_state_vector_definition_row(
    *,
    owner_id: str,
    version: str,
    state_fields: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    owner_token = str(owner_id or "").strip()
    version_token = str(version or "").strip() or "1.0.0"
    if not owner_token:
        return {}
    normalized_fields: List[dict] = []
    for row in sorted((dict(item) for item in _as_list(state_fields) if isinstance(item, Mapping)), key=lambda item: str(item.get("field_id", ""))):
        field_id = str(row.get("field_id", "")).strip()
        if not field_id:
            continue
        normalized_fields.append(
            {
                "field_id": field_id,
                "path": str(row.get("path", "")).strip() or field_id,
                "field_kind": str(row.get("field_kind", "")).strip() or "opaque",
                "default": _normalize_value(row.get("default")),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip() or canonical_sha256(
                    {
                        "field_id": field_id,
                        "path": str(row.get("path", "")).strip() or field_id,
                        "field_kind": str(row.get("field_kind", "")).strip() or "opaque",
                        "default": _normalize_value(row.get("default")),
                    }
                ),
                "extensions": _as_map(row.get("extensions")),
            }
        )

    payload = {
        "schema_version": "1.0.0",
        "owner_id": owner_token,
        "version": version_token,
        "state_fields": list(normalized_fields),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_state_vector_definition_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("owner_id", ""))):
        normalized = build_state_vector_definition_row(
            owner_id=str(row.get("owner_id", "")).strip(),
            version=str(row.get("version", "")).strip() or "1.0.0",
            state_fields=row.get("state_fields"),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        owner_id = str(normalized.get("owner_id", "")).strip()
        if owner_id:
            out[owner_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def state_vector_definition_rows_by_owner(rows: object) -> Dict[str, dict]:
    return dict(
        (str(row.get("owner_id", "")).strip(), dict(row))
        for row in normalize_state_vector_definition_rows(rows)
        if str(row.get("owner_id", "")).strip()
    )


def build_state_vector_snapshot_row(
    *,
    owner_id: str,
    version: str,
    serialized_state: Mapping[str, object] | None,
    tick: int,
    snapshot_id: str = "",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    owner_token = str(owner_id or "").strip()
    version_token = str(version or "").strip() or "1.0.0"
    tick_value = int(max(0, _as_int(tick, 0)))
    if not owner_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "snapshot_id": str(snapshot_id or "").strip()
        or "statevec.snapshot.{}".format(
            canonical_sha256(
                {
                    "owner_id": owner_token,
                    "version": version_token,
                    "tick": tick_value,
                    "serialized_state": _normalize_value(_as_map(serialized_state)),
                }
            )[:16]
        ),
        "owner_id": owner_token,
        "version": version_token,
        "serialized_state": _normalize_value(_as_map(serialized_state)),
        "tick": tick_value,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_state_vector_snapshot_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("owner_id", "")),
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("snapshot_id", "")),
        ),
    ):
        normalized = build_state_vector_snapshot_row(
            owner_id=str(row.get("owner_id", "")).strip(),
            version=str(row.get("version", "")).strip() or "1.0.0",
            serialized_state=_as_map(row.get("serialized_state")),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            snapshot_id=str(row.get("snapshot_id", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        snapshot_id = str(normalized.get("snapshot_id", "")).strip()
        if snapshot_id:
            out[snapshot_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def state_vector_snapshot_rows_by_owner(rows: object) -> Dict[str, dict]:
    latest: Dict[str, dict] = {}
    for row in sorted(
        normalize_state_vector_snapshot_rows(rows),
        key=lambda item: (
            str(item.get("owner_id", "")),
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("snapshot_id", "")),
        ),
    ):
        owner_id = str(row.get("owner_id", "")).strip()
        if owner_id:
            latest[owner_id] = dict(row)
    return dict((key, dict(latest[key])) for key in sorted(latest.keys()))


def state_vector_anchor_hash(snapshot_row: Mapping[str, object] | None) -> str:
    row = _as_map(snapshot_row)
    return canonical_sha256(
        {
            "owner_id": str(row.get("owner_id", "")).strip(),
            "version": str(row.get("version", "")).strip(),
            "serialized_state": _normalize_value(_as_map(row.get("serialized_state"))),
            "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            "snapshot_id": str(row.get("snapshot_id", "")).strip(),
        }
    )


def serialize_state(
    *,
    owner_id: str,
    source_state: Mapping[str, object] | None,
    state_vector_definition_rows: object,
    current_tick: int,
    expected_version: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    owner_token = str(owner_id or "").strip()
    if not owner_token:
        return {"result": "refused", "reason_code": REFUSAL_STATEVEC_INVALID, "message": "owner_id is required"}
    definition = state_vector_definition_for_owner(
        owner_id=owner_token,
        state_vector_definition_rows=state_vector_definition_rows,
    )
    if not definition:
        return {
            "result": "refused",
            "reason_code": REFUSAL_STATEVEC_MISSING_DEFINITION,
            "message": "missing state vector definition for owner",
            "owner_id": owner_token,
        }
    version_token = str(definition.get("version", "")).strip() or "1.0.0"
    expected_token = str(expected_version or "").strip()
    if expected_token and expected_token != version_token:
        return {
            "result": "refused",
            "reason_code": REFUSAL_STATEVEC_VERSION_MISMATCH,
            "message": "state vector version mismatch",
            "owner_id": owner_token,
            "expected_version": expected_token,
            "observed_version": version_token,
        }

    source = _as_map(source_state)
    serialized: Dict[str, object] = {}
    for field in sorted(
        (dict(item) for item in list(definition.get("state_fields") or []) if isinstance(item, Mapping)),
        key=lambda item: str(item.get("field_id", "")),
    ):
        field_id = str(field.get("field_id", "")).strip()
        if not field_id:
            continue
        path = str(field.get("path", "")).strip() or field_id
        if path in source:
            value = source.get(path)
        else:
            value = field.get("default")
        serialized[field_id] = _normalize_value(value)

    snapshot = build_state_vector_snapshot_row(
        owner_id=owner_token,
        version=version_token,
        serialized_state=serialized,
        tick=int(max(0, _as_int(current_tick, 0))),
        deterministic_fingerprint="",
        extensions=dict(_as_map(extensions), owner_definition_fingerprint=str(definition.get("deterministic_fingerprint", "")).strip()),
    )
    return {
        "result": "complete",
        "reason_code": "",
        "owner_id": owner_token,
        "version": version_token,
        "snapshot_row": dict(snapshot),
        "anchor_hash": state_vector_anchor_hash(snapshot),
        "deterministic_fingerprint": canonical_sha256(
            {
                "owner_id": owner_token,
                "version": version_token,
                "snapshot_id": str(snapshot.get("snapshot_id", "")).strip(),
                "anchor_hash": state_vector_anchor_hash(snapshot),
            }
        ),
    }


def deserialize_state(
    *,
    snapshot_row: Mapping[str, object] | None,
    state_vector_definition_rows: object,
    expected_version: str | None = None,
    compat_migrations: Mapping[str, object] | None = None,
) -> dict:
    snapshot = _as_map(snapshot_row)
    owner_token = str(snapshot.get("owner_id", "")).strip()
    if not owner_token:
        return {"result": "refused", "reason_code": REFUSAL_STATEVEC_INVALID, "message": "snapshot missing owner_id"}
    definition = state_vector_definition_for_owner(
        owner_id=owner_token,
        state_vector_definition_rows=state_vector_definition_rows,
    )
    if not definition:
        return {
            "result": "refused",
            "reason_code": REFUSAL_STATEVEC_MISSING_DEFINITION,
            "message": "missing state vector definition for owner",
            "owner_id": owner_token,
        }
    snapshot_version = str(snapshot.get("version", "")).strip() or "1.0.0"
    definition_version = str(definition.get("version", "")).strip() or "1.0.0"
    expected_token = str(expected_version or "").strip()
    if expected_token and snapshot_version != expected_token:
        return {
            "result": "refused",
            "reason_code": REFUSAL_STATEVEC_VERSION_MISMATCH,
            "message": "snapshot version mismatch",
            "owner_id": owner_token,
            "expected_version": expected_token,
            "observed_version": snapshot_version,
        }
    if snapshot_version != definition_version:
        migration_key = "{}->{}".format(snapshot_version, definition_version)
        migration = _as_map(_as_map(compat_migrations).get(migration_key))
        migration_status = str(migration.get("status", "")).strip().lower()
        if migration_status in {"available", "identity", "no_op"}:
            snapshot_version = definition_version
        else:
            return {
                "result": "refused",
                "reason_code": REFUSAL_STATEVEC_MIGRATION_UNAVAILABLE,
                "message": "state vector migration route is unavailable",
                "owner_id": owner_token,
                "snapshot_version": str(snapshot.get("version", "")).strip() or "1.0.0",
                "definition_version": definition_version,
                "required_route": migration_key,
            }

    serialized = _as_map(snapshot.get("serialized_state"))
    restored: Dict[str, object] = {}
    for field in sorted(
        (dict(item) for item in list(definition.get("state_fields") or []) if isinstance(item, Mapping)),
        key=lambda item: str(item.get("field_id", "")),
    ):
        field_id = str(field.get("field_id", "")).strip()
        if not field_id:
            continue
        path = str(field.get("path", "")).strip() or field_id
        if field_id in serialized:
            restored[path] = _normalize_value(serialized.get(field_id))
        else:
            restored[path] = _normalize_value(field.get("default"))
    return {
        "result": "complete",
        "reason_code": "",
        "owner_id": owner_token,
        "version": snapshot_version,
        "restored_state": dict(restored),
        "anchor_hash": state_vector_anchor_hash(snapshot),
        "deterministic_fingerprint": canonical_sha256(
            {
                "owner_id": owner_token,
                "version": snapshot_version,
                "snapshot_id": str(snapshot.get("snapshot_id", "")).strip(),
                "restored_state": dict(restored),
            }
        ),
    }


def detect_undeclared_output_state(
    *,
    owner_id: str,
    output_affecting_fields: object,
    state_vector_definition_rows: object,
) -> dict:
    owner_token = str(owner_id or "").strip()
    definition = state_vector_definition_for_owner(
        owner_id=owner_token,
        state_vector_definition_rows=state_vector_definition_rows,
    )
    if not definition:
        return {
            "violation": True,
            "reason_code": REFUSAL_STATEVEC_MISSING_DEFINITION,
            "owner_id": owner_token,
            "missing_fields": _sorted_tokens(output_affecting_fields),
        }
    declared = set(
        _sorted_tokens(
            str(row.get("path", "")).strip() or str(row.get("field_id", "")).strip()
            for row in list(definition.get("state_fields") or [])
            if isinstance(row, Mapping)
        )
    )
    required = _sorted_tokens(output_affecting_fields)
    missing = [field for field in required if field not in declared]
    return {
        "violation": bool(missing),
        "reason_code": REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD if missing else "",
        "owner_id": owner_token,
        "missing_fields": list(missing),
        "declared_fields": sorted(declared),
        "deterministic_fingerprint": canonical_sha256(
            {
                "owner_id": owner_token,
                "missing_fields": list(missing),
                "declared_fields": sorted(declared),
            }
        ),
    }


__all__ = [
    "REFUSAL_STATEVEC_INVALID",
    "REFUSAL_STATEVEC_MISSING_DEFINITION",
    "REFUSAL_STATEVEC_VERSION_MISMATCH",
    "REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD",
    "REFUSAL_STATEVEC_MIGRATION_UNAVAILABLE",
    "build_state_vector_definition_row",
    "normalize_state_vector_definition_rows",
    "state_vector_definition_rows_by_owner",
    "state_vector_definition_for_owner",
    "build_state_vector_snapshot_row",
    "normalize_state_vector_snapshot_rows",
    "state_vector_snapshot_rows_by_owner",
    "state_vector_anchor_hash",
    "serialize_state",
    "deserialize_state",
    "detect_undeclared_output_state",
]
