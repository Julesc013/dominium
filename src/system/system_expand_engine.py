"""SYS-0 deterministic system expand helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.system.system_collapse_engine import (
    SystemCollapseError,
    _as_int,
    _as_map,
    interface_signature_rows_by_system,
    normalize_system_macro_capsule_rows,
    normalize_system_rows,
    normalize_system_state_vector_rows,
)
from src.system.system_validation_engine import (
    REFUSAL_SYSTEM_INVALID_INTERFACE,
    REFUSAL_SYSTEM_INVARIANT_VIOLATION,
    validate_boundary_invariants,
    validate_interface_signature,
)


REFUSAL_SYSTEM_EXPAND_INVALID = "REFUSAL_SYSTEM_EXPAND_INVALID"
REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH = "REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH"
REFUSAL_SYSTEM_EXPAND_INVALID_INTERFACE = REFUSAL_SYSTEM_INVALID_INTERFACE
REFUSAL_SYSTEM_EXPAND_INVARIANT_VIOLATION = REFUSAL_SYSTEM_INVARIANT_VIOLATION


class SystemExpandError(RuntimeError):
    """Raised when a system expand request is invalid."""

    def __init__(self, message: str, *, reason_code: str, details: Mapping[str, object] | None = None) -> None:
        super().__init__(str(message))
        self.reason_code = str(reason_code or REFUSAL_SYSTEM_EXPAND_INVALID)
        self.details = dict(details or {})


def _state_vector_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_system_state_vector_rows(rows):
        vector_id = str(row.get("state_vector_id", "")).strip()
        if vector_id:
            out[vector_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _macro_capsule_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_system_macro_capsule_rows(rows):
        capsule_id = str(row.get("capsule_id", "")).strip()
        if capsule_id:
            out[capsule_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _state_vector_for_capsule(
    *,
    capsule_row: Mapping[str, object],
    state_vector_by_id: Mapping[str, Mapping[str, object]],
) -> dict:
    internal_state_vector = _as_map(capsule_row.get("internal_state_vector"))
    state_vector_id = str(internal_state_vector.get("state_vector_id", "")).strip()
    row = dict(state_vector_by_id.get(state_vector_id) or {})
    if row:
        return row

    system_id = str(capsule_row.get("system_id", "")).strip()
    candidates = [
        dict(item)
        for item in state_vector_by_id.values()
        if isinstance(item, Mapping) and str(item.get("system_id", "")).strip() == system_id
    ]
    if not candidates:
        return {}
    return dict(
        sorted(
            candidates,
            key=lambda item: (
                str(item.get("system_id", "")),
                str(item.get("state_vector_id", "")),
            ),
        )[-1]
    )


def _validate_expand_payload(
    *,
    capsule_row: Mapping[str, object],
    state_vector_row: Mapping[str, object],
) -> List[dict]:
    system_id = str(capsule_row.get("system_id", "")).strip()
    serialized_internal_state = _as_map(state_vector_row.get("serialized_internal_state"))
    anchor_expected = str(capsule_row.get("provenance_anchor_hash", "")).strip()
    anchor_observed = canonical_sha256(serialized_internal_state)
    if anchor_expected != anchor_observed:
        raise SystemExpandError(
            "provenance anchor hash mismatch for system expand",
            reason_code=REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH,
            details={
                "system_id": system_id,
                "expected_anchor_hash": anchor_expected,
                "observed_anchor_hash": anchor_observed,
            },
        )

    assembly_rows = [
        dict(row)
        for row in list(serialized_internal_state.get("assembly_rows") or [])
        if isinstance(row, Mapping) and str(row.get("assembly_id", "")).strip()
    ]
    if not assembly_rows:
        raise SystemExpandError(
            "serialized internal state has no assembly_rows to restore",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={"system_id": system_id},
        )
    return sorted(assembly_rows, key=lambda row: str(row.get("assembly_id", "")))


def expand_system_graph(
    *,
    state: dict,
    capsule_id: str,
    current_tick: int,
    process_id: str = "process.system_expand",
    quantity_bundle_registry_payload: Mapping[str, object] | None = None,
    spec_type_registry_payload: Mapping[str, object] | None = None,
    signal_channel_type_registry_payload: Mapping[str, object] | None = None,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    safety_pattern_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    if not isinstance(state, dict):
        raise SystemExpandError(
            "state payload must be a mapping",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={},
        )

    capsule_token = str(capsule_id or "").strip()
    if not capsule_token:
        raise SystemExpandError(
            "capsule_id is required for process.system_expand",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={},
        )

    capsule_by_id = _macro_capsule_rows_by_id(state.get("system_macro_capsule_rows") or [])
    capsule_row = dict(capsule_by_id.get(capsule_token) or {})
    if not capsule_row:
        raise SystemExpandError(
            "capsule_id is not present in system_macro_capsule_rows",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={"capsule_id": capsule_token},
        )

    system_id = str(capsule_row.get("system_id", "")).strip()
    system_rows = normalize_system_rows(state.get("system_rows") or [])
    system_row_by_id = dict(
        (str(row.get("system_id", "")).strip(), dict(row))
        for row in list(system_rows or [])
        if isinstance(row, Mapping) and str(row.get("system_id", "")).strip()
    )
    if system_id not in system_row_by_id:
        raise SystemExpandError(
            "capsule system_id is not declared in system_rows",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={"capsule_id": capsule_token, "system_id": system_id},
        )

    interface_by_system = interface_signature_rows_by_system(state.get("system_interface_signature_rows") or [])
    if system_id not in interface_by_system:
        raise SystemExpandError(
            "interface signature missing for capsule system during expand",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={"system_id": system_id},
        )

    state_vector_by_id = _state_vector_rows_by_id(state.get("system_state_vector_rows") or [])
    state_vector_row = _state_vector_for_capsule(
        capsule_row=capsule_row,
        state_vector_by_id=state_vector_by_id,
    )
    if not state_vector_row:
        raise SystemExpandError(
            "state vector missing for capsule expand",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID,
            details={"capsule_id": capsule_token, "system_id": system_id},
        )

    restored_assembly_rows = _validate_expand_payload(
        capsule_row=capsule_row,
        state_vector_row=state_vector_row,
    )

    interface_validation = validate_interface_signature(
        system_id=system_id,
        system_rows=state.get("system_rows") or [],
        interface_signature_rows=state.get("system_interface_signature_rows") or [],
        quantity_bundle_registry_payload=quantity_bundle_registry_payload,
        spec_type_registry_payload=spec_type_registry_payload,
        signal_channel_type_registry_payload=signal_channel_type_registry_payload,
    )
    if str(interface_validation.get("result", "")).strip() != "complete":
        raise SystemExpandError(
            "restored system failed interface signature validation",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVALID_INTERFACE,
            details={
                "system_id": system_id,
                "capsule_id": capsule_token,
                "failed_checks": [dict(row) for row in list(interface_validation.get("failed_checks") or []) if isinstance(row, Mapping)],
                "deterministic_fingerprint": str(interface_validation.get("deterministic_fingerprint", "")).strip(),
            },
        )

    invariant_validation = validate_boundary_invariants(
        system_id=system_id,
        system_rows=state.get("system_rows") or [],
        boundary_invariant_rows=state.get("system_boundary_invariant_rows") or state.get("boundary_invariant_rows") or [],
        boundary_invariant_template_registry_payload=boundary_invariant_template_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        safety_pattern_registry_payload=safety_pattern_registry_payload,
    )
    if str(invariant_validation.get("result", "")).strip() != "complete":
        raise SystemExpandError(
            "restored system failed boundary invariant validation",
            reason_code=REFUSAL_SYSTEM_EXPAND_INVARIANT_VIOLATION,
            details={
                "system_id": system_id,
                "capsule_id": capsule_token,
                "failed_checks": [dict(row) for row in list(invariant_validation.get("failed_checks") or []) if isinstance(row, Mapping)],
                "deterministic_fingerprint": str(invariant_validation.get("deterministic_fingerprint", "")).strip(),
            },
        )

    tick_value = int(max(0, _as_int(current_tick, 0)))
    restored_assembly_ids = sorted(
        str(row.get("assembly_id", "")).strip() for row in restored_assembly_rows if str(row.get("assembly_id", "")).strip()
    )
    restored_assembly_id_set = set(restored_assembly_ids)

    placeholder_assembly_id = str(_as_map(capsule_row.get("extensions")).get("placeholder_assembly_id", "")).strip()
    if not placeholder_assembly_id:
        placeholder_assembly_id = str(_as_map(system_row_by_id.get(system_id, {}).get("extensions")).get("placeholder_assembly_id", "")).strip()

    existing_assembly_rows = [dict(row) for row in list(state.get("assembly_rows") or []) if isinstance(row, Mapping)]
    retained_rows = []
    for row in existing_assembly_rows:
        assembly_id = str(row.get("assembly_id", "")).strip()
        if not assembly_id:
            continue
        if assembly_id in restored_assembly_id_set:
            continue
        if placeholder_assembly_id and assembly_id == placeholder_assembly_id:
            continue
        retained_rows.append(dict(row))
    state["assembly_rows"] = sorted(
        retained_rows + [dict(row) for row in restored_assembly_rows],
        key=lambda row: str(row.get("assembly_id", "")),
    )

    state["system_macro_capsule_rows"] = normalize_system_macro_capsule_rows(
        [
            dict(row)
            for row in list(state.get("system_macro_capsule_rows") or [])
            if isinstance(row, Mapping) and str(row.get("capsule_id", "")).strip() != capsule_token
        ]
    )

    updated_system_rows = []
    for row in normalize_system_rows(state.get("system_rows") or []):
        row_system_id = str(row.get("system_id", "")).strip()
        if row_system_id != system_id:
            updated_system_rows.append(dict(row))
            continue
        ext = _as_map(row.get("extensions"))
        ext["last_expand_tick"] = tick_value
        ext["last_restored_capsule_id"] = capsule_token
        row["extensions"] = ext
        row["current_tier"] = "micro"
        row["active_capsule_id"] = ""
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
        updated_system_rows.append(dict(row))
    state["system_rows"] = sorted(updated_system_rows, key=lambda row: str(row.get("system_id", "")))

    expand_event = {
        "schema_version": "1.0.0",
        "event_id": "event.system.expand.{}".format(canonical_sha256({"capsule_id": capsule_token, "tick": tick_value})[:16]),
        "system_id": system_id,
        "capsule_id": capsule_token,
        "state_vector_id": str(state_vector_row.get("state_vector_id", "")).strip(),
        "tick": tick_value,
        "deterministic_fingerprint": "",
        "extensions": {
            "source_process_id": process_id,
            "ports_rebound": True,
            "signals_rebound": True,
            "restored_assembly_ids": list(restored_assembly_ids),
            "provenance_anchor_hash": str(capsule_row.get("provenance_anchor_hash", "")).strip(),
            "interface_validation_fingerprint": str(interface_validation.get("deterministic_fingerprint", "")).strip(),
            "invariant_validation_fingerprint": str(invariant_validation.get("deterministic_fingerprint", "")).strip(),
        },
    }
    expand_event["deterministic_fingerprint"] = canonical_sha256(dict(expand_event, deterministic_fingerprint=""))

    state["system_expand_event_rows"] = sorted(
        [
            dict(row)
            for row in list(state.get("system_expand_event_rows") or []) + [expand_event]
            if isinstance(row, Mapping)
        ],
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )

    info_artifact_rows = [
        dict(row)
        for row in list(state.get("info_artifact_rows") or state.get("knowledge_artifacts") or [])
        if isinstance(row, Mapping)
    ]
    artifact_id = "artifact.record.system_expand.{}".format(canonical_sha256({"event_id": expand_event["event_id"]})[:16])
    info_artifact_rows.append(
        {
            "artifact_id": artifact_id,
            "artifact_family_id": "RECORD",
            "extensions": {
                "artifact_type_id": "artifact.record.system_expand",
                "event_id": str(expand_event.get("event_id", "")).strip(),
                "system_id": system_id,
                "capsule_id": capsule_token,
                "state_vector_id": str(state_vector_row.get("state_vector_id", "")).strip(),
            },
        }
    )
    state["info_artifact_rows"] = sorted(
        info_artifact_rows,
        key=lambda row: (str(row.get("artifact_family_id", "")), str(row.get("artifact_id", ""))),
    )
    state["knowledge_artifacts"] = [dict(row) for row in list(state.get("info_artifact_rows") or [])]

    state["system_expand_hash_chain"] = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
            }
            for row in list(state.get("system_expand_event_rows") or [])
            if isinstance(row, Mapping)
        ]
    )

    return {
        "result": "complete",
        "system_id": system_id,
        "capsule_id": capsule_token,
        "state_vector_id": str(state_vector_row.get("state_vector_id", "")).strip(),
        "event_id": str(expand_event.get("event_id", "")).strip(),
        "restored_assembly_ids": list(restored_assembly_ids),
        "deterministic_fingerprint": canonical_sha256(
            {
                "system_id": system_id,
                "capsule_id": capsule_token,
                "event_id": str(expand_event.get("event_id", "")).strip(),
                "state_vector_id": str(state_vector_row.get("state_vector_id", "")).strip(),
            }
        ),
    }


__all__ = [
    "REFUSAL_SYSTEM_EXPAND_INVALID",
    "REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH",
    "REFUSAL_SYSTEM_EXPAND_INVALID_INTERFACE",
    "REFUSAL_SYSTEM_EXPAND_INVARIANT_VIOLATION",
    "SystemExpandError",
    "expand_system_graph",
]
