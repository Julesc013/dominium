"""SYS-0 deterministic system collapse helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256
from meta.profile import apply_override
from system.system_validation_engine import (
    REFUSAL_SYSTEM_INVALID_INTERFACE,
    REFUSAL_SYSTEM_INVARIANT_VIOLATION,
    validate_boundary_invariants,
    validate_interface_signature,
)
from system.statevec import (
    REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD,
    build_state_vector_definition_row,
    detect_undeclared_output_state,
    normalize_state_vector_definition_rows,
    normalize_state_vector_snapshot_rows,
    serialize_state,
    state_vector_definition_for_owner,
)


REFUSAL_SYSTEM_COLLAPSE_INVALID = "REFUSAL_SYSTEM_COLLAPSE_INVALID"
REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE = "REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE"
REFUSAL_SYSTEM_COLLAPSE_INVALID_INTERFACE = REFUSAL_SYSTEM_INVALID_INTERFACE
REFUSAL_SYSTEM_COLLAPSE_INVARIANT_VIOLATION = REFUSAL_SYSTEM_INVARIANT_VIOLATION


class SystemCollapseError(RuntimeError):
    """Raised when a system collapse request is invalid or ineligible."""

    def __init__(self, message: str, *, reason_code: str, details: Mapping[str, object] | None = None) -> None:
        super().__init__(str(message))
        self.reason_code = str(reason_code or REFUSAL_SYSTEM_COLLAPSE_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_interface_signature_row(
    *,
    system_id: str,
    interface_signature_id: str,
    port_list: object,
    signal_channels: object,
    spec_limits: Mapping[str, object] | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    system_token = str(system_id or "").strip()
    interface_token = str(interface_signature_id or "").strip()
    if (not system_token) or (not interface_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "system_id": system_token,
        "interface_signature_id": interface_token,
        "port_list": [dict(row) for row in list(port_list or []) if isinstance(row, Mapping)],
        "signal_channels": [dict(row) for row in list(signal_channels or []) if isinstance(row, Mapping)],
        "spec_limits": _as_map(spec_limits),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_interface_signature_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            str(item.get("interface_signature_id", "")),
        ),
    ):
        normalized = build_interface_signature_row(
            system_id=str(row.get("system_id", "")).strip(),
            interface_signature_id=(
                str(row.get("interface_signature_id", "")).strip()
                or "iface.{}".format(str(row.get("system_id", "")).strip())
            ),
            port_list=row.get("port_list"),
            signal_channels=row.get("signal_channels"),
            spec_limits=_as_map(row.get("spec_limits")),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        signature_id = str(normalized.get("interface_signature_id", "")).strip()
        if signature_id:
            out[signature_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def interface_signature_rows_by_system(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_interface_signature_rows(rows):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_boundary_invariant_row(
    *,
    invariant_id: str,
    quantity_ids: object,
    tolerance_policy_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    invariant_token = str(invariant_id or "").strip()
    tolerance_token = str(tolerance_policy_id or "").strip()
    if (not invariant_token) or (not tolerance_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "invariant_id": invariant_token,
        "quantity_ids": _sorted_tokens(list(quantity_ids or [])),
        "tolerance_policy_id": tolerance_token,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_boundary_invariant_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("invariant_id", "")),
    ):
        normalized = build_boundary_invariant_row(
            invariant_id=str(row.get("invariant_id", "")).strip(),
            quantity_ids=row.get("quantity_ids"),
            tolerance_policy_id=str(row.get("tolerance_policy_id", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        invariant_id = str(normalized.get("invariant_id", "")).strip()
        if invariant_id:
            out[invariant_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def boundary_invariant_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_boundary_invariant_rows(rows):
        invariant_id = str(row.get("invariant_id", "")).strip()
        if invariant_id:
            out[invariant_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_system_state_vector_row(
    *,
    state_vector_id: str,
    system_id: str,
    serialized_internal_state: Mapping[str, object] | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    vector_token = str(state_vector_id or "").strip()
    system_token = str(system_id or "").strip()
    if (not vector_token) or (not system_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "state_vector_id": vector_token,
        "system_id": system_token,
        "serialized_internal_state": _as_map(serialized_internal_state),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_state_vector_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            str(item.get("state_vector_id", "")),
        ),
    ):
        vector_id = str(row.get("state_vector_id", "")).strip()
        if not vector_id:
            vector_id = "statevec.system.{}".format(
                canonical_sha256(
                    {
                        "system_id": str(row.get("system_id", "")).strip(),
                        "payload": _as_map(row.get("serialized_internal_state")),
                    }
                )[:16]
            )
        normalized = build_system_state_vector_row(
            state_vector_id=vector_id,
            system_id=str(row.get("system_id", "")).strip(),
            serialized_internal_state=_as_map(row.get("serialized_internal_state")),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        state_vector_id = str(normalized.get("state_vector_id", "")).strip()
        if state_vector_id:
            out[state_vector_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_system_macro_capsule_row(
    *,
    capsule_id: str,
    system_id: str,
    interface_signature_id: str,
    macro_model_set_id: str = "",
    model_error_bounds_ref: str = "",
    macro_model_bindings: object,
    internal_state_vector: Mapping[str, object] | None,
    provenance_anchor_hash: str,
    tier_mode: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    capsule_token = str(capsule_id or "").strip()
    system_token = str(system_id or "").strip()
    interface_token = str(interface_signature_id or "").strip()
    anchor_token = str(provenance_anchor_hash or "").strip()
    if (not capsule_token) or (not system_token) or (not interface_token) or (not anchor_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "capsule_id": capsule_token,
        "system_id": system_token,
        "interface_signature_id": interface_token,
        "macro_model_set_id": str(macro_model_set_id or "").strip(),
        "model_error_bounds_ref": str(model_error_bounds_ref or "").strip(),
        "macro_model_bindings": [dict(row) for row in list(macro_model_bindings or []) if isinstance(row, Mapping)],
        "internal_state_vector": _as_map(internal_state_vector),
        "provenance_anchor_hash": anchor_token,
        "tier_mode": str(tier_mode or "macro").strip() or "macro",
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_macro_capsule_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            str(item.get("capsule_id", "")),
        ),
    ):
        normalized = build_system_macro_capsule_row(
            capsule_id=str(row.get("capsule_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            interface_signature_id=str(row.get("interface_signature_id", "")).strip(),
            macro_model_set_id=str(row.get("macro_model_set_id", "")).strip(),
            model_error_bounds_ref=str(row.get("model_error_bounds_ref", "")).strip(),
            macro_model_bindings=row.get("macro_model_bindings"),
            internal_state_vector=_as_map(row.get("internal_state_vector")),
            provenance_anchor_hash=str(row.get("provenance_anchor_hash", "")).strip(),
            tier_mode=str(row.get("tier_mode", "macro")).strip() or "macro",
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        capsule_id = str(normalized.get("capsule_id", "")).strip()
        if capsule_id:
            out[capsule_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _normalize_system_row(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    system_id = str(payload.get("system_id", "")).strip()
    if not system_id:
        return {}
    ext = _as_map(payload.get("extensions"))
    return {
        "schema_version": "1.0.0",
        "system_id": system_id,
        "root_assembly_id": str(payload.get("root_assembly_id", "")).strip(),
        "assembly_ids": _sorted_tokens(payload.get("assembly_ids")),
        "interface_signature_id": str(payload.get("interface_signature_id", "")).strip() or "iface.{}".format(system_id),
        "boundary_invariant_ids": _sorted_tokens(payload.get("boundary_invariant_ids")),
        "tier_contract_id": str(payload.get("tier_contract_id", "")).strip(),
        "current_tier": str(payload.get("current_tier", "micro")).strip() or "micro",
        "active_capsule_id": str(payload.get("active_capsule_id", "")).strip(),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": ext,
    }


def normalize_system_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        normalized = _normalize_system_row(row)
        system_id = str(normalized.get("system_id", "")).strip()
        if not system_id:
            continue
        if not normalized.get("deterministic_fingerprint"):
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[system_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def system_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_system_rows(rows):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _collapse_eligibility_details(system_row: Mapping[str, object] | None) -> dict:
    row = _as_map(system_row)
    ext = _as_map(row.get("extensions"))
    return {
        "unresolved_hazard_count": int(max(0, _as_int(row.get("unresolved_hazard_count", ext.get("unresolved_hazard_count", 0)), 0))),
        "pending_internal_event_count": int(max(0, _as_int(row.get("pending_internal_event_count", ext.get("pending_internal_event_count", 0)), 0))),
        "open_scheduled_task_count": int(max(0, _as_int(row.get("open_scheduled_task_count", ext.get("open_scheduled_task_count", 0)), 0))),
        "open_branch_dependency_count": int(max(0, _as_int(row.get("open_branch_dependency_count", ext.get("open_branch_dependency_count", 0)), 0))),
    }


def _statevec_output_guard_status(
    *,
    state: Mapping[str, object] | None,
    system_id: str,
    current_tick: int,
) -> dict:
    state_row = _as_map(state)
    session_spec = _as_map(state_row.get("session_spec"))
    authority_context = _as_map(state_row.get("authority_context")) or _as_map(session_spec.get("authority_context"))
    owner_context = {
        "universe_id": (
            str(state_row.get("universe_id", "")).strip()
            or str(_as_map(state_row.get("universe_identity")).get("universe_id", "")).strip()
            or str(session_spec.get("universe_id", "")).strip()
        ),
        "session_id": (
            str(state_row.get("session_id", "")).strip()
            or str(session_spec.get("session_id", "")).strip()
            or str(session_spec.get("save_id", "")).strip()
        ),
        "authority_id": (
            str(state_row.get("authority_id", "")).strip()
            or str(authority_context.get("authority_context_id", "")).strip()
            or str(authority_context.get("authority_origin", "")).strip()
        ),
        "system_id": str(system_id or "").strip(),
        "session_spec": session_spec,
        "authority_context": authority_context,
        "profile_binding_rows": list(state_row.get("profile_binding_rows") or []),
        "profile_registry_payload": _as_map(state_row.get("profile_registry_payload")) or _as_map(state_row.get("profile_registry")),
    }
    eval_row = apply_override(
        rule_id="rule.statevec.output_guard",
        owner_id="system.{}".format(str(system_id or "").strip()),
        tick=int(max(0, _as_int(current_tick, 0))),
        owner_context=owner_context,
        profile_registry_payload=_as_map(state_row.get("profile_registry_payload")) or _as_map(state_row.get("profile_registry")),
        profile_binding_rows=list(state_row.get("profile_binding_rows") or []),
        law_profile_row=_as_map(state_row.get("law_profile")),
        details={"justification": "statevec.output_guard.evaluation"},
    )
    resolution = _as_map(eval_row.get("resolution"))
    value = resolution.get("effective_value")
    enabled = False
    if isinstance(value, bool):
        enabled = bool(value)
    elif value is not None:
        token = str(value).strip().lower()
        enabled = token in {"1", "true", "yes", "on", "enforce", "enabled", "required"}
    return {
        "enabled": bool(enabled),
        "exception_event": dict(eval_row.get("exception_event") or {}) if isinstance(eval_row.get("exception_event"), Mapping) else {},
        "resolution": resolution,
        "deterministic_fingerprint": str(eval_row.get("deterministic_fingerprint", "")).strip(),
    }


def _append_profile_exception_event(state: dict, event_row: Mapping[str, object] | None) -> None:
    row = _as_map(event_row)
    event_id = str(row.get("event_id", "")).strip()
    if (not isinstance(state, dict)) or (not event_id):
        return
    by_id: Dict[str, dict] = {}
    for existing in sorted(
        (dict(item) for item in list(state.get("profile_exception_events") or []) if isinstance(item, Mapping)),
        key=lambda item: str(item.get("event_id", "")),
    ):
        token = str(existing.get("event_id", "")).strip()
        if token:
            by_id[token] = dict(existing)
    by_id[event_id] = dict(row)
    state["profile_exception_events"] = [dict(by_id[key]) for key in sorted(by_id.keys())]


def _statevec_output_affecting_fields(
    *,
    system_row: Mapping[str, object] | None,
    fallback_payload: Mapping[str, object] | None,
) -> List[str]:
    ext = _as_map(_as_map(system_row).get("extensions"))
    declared = _sorted_tokens(
        ext.get(
            "output_affecting_state_fields",
            ext.get("state_vector_output_fields", []),
        )
    )
    if declared:
        return list(declared)
    payload = _as_map(fallback_payload)
    fallback = [
        str(key).strip()
        for key in sorted(payload.keys())
        if str(key).strip()
        and str(key).strip()
        not in {"schema_version", "encoding", "system_id"}
    ]
    return _sorted_tokens(fallback)


def _validate_collapse_eligibility(
    *,
    system_row: Mapping[str, object],
    interface_row: Mapping[str, object],
    boundary_invariant_by_id: Mapping[str, Mapping[str, object]],
) -> List[dict]:
    details = _collapse_eligibility_details(system_row)
    if int(details.get("unresolved_hazard_count", 0)) > 0:
        raise SystemCollapseError(
            "system has unresolved hazards and cannot collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE,
            details=dict(details),
        )
    if int(details.get("pending_internal_event_count", 0)) > 0:
        raise SystemCollapseError(
            "system has pending internal events and cannot collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE,
            details=dict(details),
        )
    if int(details.get("open_scheduled_task_count", 0)) > 0:
        raise SystemCollapseError(
            "system has open scheduled internal tasks and cannot collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE,
            details=dict(details),
        )
    if int(details.get("open_branch_dependency_count", 0)) > 0:
        raise SystemCollapseError(
            "system has open branch dependency and cannot collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE,
            details=dict(details),
        )

    port_list = list(interface_row.get("port_list") or [])
    if not port_list:
        raise SystemCollapseError(
            "system interface signature has no boundary ports",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"interface_signature_id": str(interface_row.get("interface_signature_id", "")).strip()},
        )

    invariant_ids = _sorted_tokens(system_row.get("boundary_invariant_ids"))
    if not invariant_ids:
        raise SystemCollapseError(
            "system boundary invariants are not declared",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"system_id": str(system_row.get("system_id", "")).strip()},
        )

    invariant_checks: List[dict] = []
    for invariant_id in invariant_ids:
        row = dict(boundary_invariant_by_id.get(invariant_id) or {})
        status = "pass" if row else "fail"
        invariant_checks.append(
            {
                "invariant_id": invariant_id,
                "status": status,
                "tolerance_policy_id": str(row.get("tolerance_policy_id", "")).strip(),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "invariant_id": invariant_id,
                        "status": status,
                        "tolerance_policy_id": str(row.get("tolerance_policy_id", "")).strip(),
                    }
                ),
            }
        )
    failed = [row for row in invariant_checks if str(row.get("status", "")).strip() == "fail"]
    if failed:
        raise SystemCollapseError(
            "system boundary invariant declaration is incomplete",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"failed_invariant_ids": [str(row.get("invariant_id", "")).strip() for row in failed]},
        )
    return sorted(invariant_checks, key=lambda row: str(row.get("invariant_id", "")))


def collapse_system_graph(
    *,
    state: dict,
    system_id: str,
    current_tick: int,
    process_id: str = "process.system_collapse",
    state_vector_definition_rows: object | None = None,
    quantity_bundle_registry_payload: Mapping[str, object] | None = None,
    spec_type_registry_payload: Mapping[str, object] | None = None,
    signal_channel_type_registry_payload: Mapping[str, object] | None = None,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    safety_pattern_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    if not isinstance(state, dict):
        raise SystemCollapseError(
            "state payload must be a mapping",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={},
        )

    system_token = str(system_id or "").strip()
    if not system_token:
        raise SystemCollapseError(
            "system_id is required for process.system_collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={},
        )

    systems_by_id = system_rows_by_id(state.get("system_rows"))
    system_row = dict(systems_by_id.get(system_token) or {})
    if not system_row:
        raise SystemCollapseError(
            "system_id is not declared in system_rows",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"system_id": system_token},
        )

    interface_by_system = interface_signature_rows_by_system(state.get("system_interface_signature_rows"))
    interface_row = dict(interface_by_system.get(system_token) or {})
    if not interface_row:
        raise SystemCollapseError(
            "system interface signature is missing",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"system_id": system_token},
        )

    interface_validation = validate_interface_signature(
        system_id=system_token,
        system_rows=state.get("system_rows") or [],
        interface_signature_rows=state.get("system_interface_signature_rows") or [],
        quantity_bundle_registry_payload=quantity_bundle_registry_payload,
        spec_type_registry_payload=spec_type_registry_payload,
        signal_channel_type_registry_payload=signal_channel_type_registry_payload,
    )
    if str(interface_validation.get("result", "")).strip() != "complete":
        raise SystemCollapseError(
            "system interface signature validation failed",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID_INTERFACE,
            details={
                "system_id": system_token,
                "failed_checks": [dict(row) for row in list(interface_validation.get("failed_checks") or []) if isinstance(row, Mapping)],
                "deterministic_fingerprint": str(interface_validation.get("deterministic_fingerprint", "")).strip(),
            },
        )

    invariant_validation = validate_boundary_invariants(
        system_id=system_token,
        system_rows=state.get("system_rows") or [],
        boundary_invariant_rows=state.get("system_boundary_invariant_rows") or state.get("boundary_invariant_rows") or [],
        boundary_invariant_template_registry_payload=boundary_invariant_template_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        safety_pattern_registry_payload=safety_pattern_registry_payload,
    )
    if str(invariant_validation.get("result", "")).strip() != "complete":
        raise SystemCollapseError(
            "system boundary invariant validation failed",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVARIANT_VIOLATION,
            details={
                "system_id": system_token,
                "failed_checks": [dict(row) for row in list(invariant_validation.get("failed_checks") or []) if isinstance(row, Mapping)],
                "deterministic_fingerprint": str(invariant_validation.get("deterministic_fingerprint", "")).strip(),
            },
        )

    if str(system_row.get("current_tier", "micro")).strip() == "macro":
        raise SystemCollapseError(
            "system is already collapsed to macro",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE,
            details={"system_id": system_token},
        )

    boundary_invariant_by_id = boundary_invariant_rows_by_id(
        state.get("system_boundary_invariant_rows") or state.get("boundary_invariant_rows") or []
    )
    invariant_checks = _validate_collapse_eligibility(
        system_row=system_row,
        interface_row=interface_row,
        boundary_invariant_by_id=boundary_invariant_by_id,
    )

    assembly_ids = _sorted_tokens(system_row.get("assembly_ids"))
    root_assembly_id = str(system_row.get("root_assembly_id", "")).strip()
    if root_assembly_id and root_assembly_id not in assembly_ids:
        assembly_ids.append(root_assembly_id)
        assembly_ids = sorted(set(assembly_ids))
    if not assembly_ids:
        raise SystemCollapseError(
            "system has no declared assembly_ids to collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"system_id": system_token},
        )

    assembly_rows = [dict(row) for row in list(state.get("assembly_rows") or []) if isinstance(row, Mapping)]
    assembly_rows_by_id = dict(
        (
            str(row.get("assembly_id", "")).strip(),
            dict(row),
        )
        for row in assembly_rows
        if str(row.get("assembly_id", "")).strip()
    )
    captured_rows = [
        dict(assembly_rows_by_id[assembly_id])
        for assembly_id in sorted(assembly_ids)
        if assembly_id in assembly_rows_by_id
    ]
    if not captured_rows:
        raise SystemCollapseError(
            "none of the declared system assembly_ids are present in assembly_rows",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={"system_id": system_token},
        )

    tick_value = int(max(0, _as_int(current_tick, 0)))
    source_state_payload = {
        "schema_version": "1.0.0",
        "encoding": "canonical_json.v1",
        "system_id": system_token,
        "captured_tick": tick_value,
        "root_assembly_id": root_assembly_id,
        "assembly_rows": [dict(row) for row in captured_rows],
    }

    declared_state_vector_definitions = normalize_state_vector_definition_rows(
        list(state.get("state_vector_definition_rows") or [])
        + list(state_vector_definition_rows or [])
    )
    state_vector_owner_id = "system.{}".format(system_token)
    owner_definition = state_vector_definition_for_owner(
        owner_id=state_vector_owner_id,
        state_vector_definition_rows=declared_state_vector_definitions,
    )
    if not owner_definition:
        fallback_definition = build_state_vector_definition_row(
            owner_id=state_vector_owner_id,
            version="1.0.0",
            state_fields=[
                {"field_id": "captured_tick", "path": "captured_tick", "field_kind": "u64", "default": 0},
                {"field_id": "assembly_rows", "path": "assembly_rows", "field_kind": "list", "default": []},
                {"field_id": "root_assembly_id", "path": "root_assembly_id", "field_kind": "id", "default": ""},
            ],
            deterministic_fingerprint="",
            extensions={"source": "system_collapse_engine.fallback_default"},
        )
        if fallback_definition:
            declared_state_vector_definitions = normalize_state_vector_definition_rows(
                list(declared_state_vector_definitions) + [fallback_definition]
            )
            owner_definition = dict(fallback_definition)

    statevec_guard_status = _statevec_output_guard_status(
        state=state,
        system_id=system_token,
        current_tick=tick_value,
    )
    _append_profile_exception_event(state, _as_map(statevec_guard_status.get("exception_event")))
    if bool(statevec_guard_status.get("enabled", False)):
        output_affecting_fields = _statevec_output_affecting_fields(
            system_row=system_row,
            fallback_payload=source_state_payload,
        )
        declaration_check = detect_undeclared_output_state(
            owner_id=state_vector_owner_id,
            output_affecting_fields=output_affecting_fields,
            state_vector_definition_rows=declared_state_vector_definitions,
        )
        if bool(declaration_check.get("violation", False)):
            tick_value = int(max(0, _as_int(current_tick, 0)))
            violation_row = {
                "schema_version": "1.0.0",
                "violation_id": "event.statevec.violation.{}".format(
                    canonical_sha256(
                        {
                            "system_id": system_token,
                            "tick": tick_value,
                            "owner_id": state_vector_owner_id,
                            "missing_fields": list(
                                declaration_check.get("missing_fields") or []
                            ),
                        }
                    )[:16]
                ),
                "owner_id": state_vector_owner_id,
                "system_id": system_token,
                "tick": tick_value,
                "reason_code": REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD,
                "missing_fields": [
                    str(item).strip()
                    for item in list(declaration_check.get("missing_fields") or [])
                    if str(item).strip()
                ],
                "deterministic_fingerprint": "",
                "extensions": {
                    "source_process_id": process_id,
                    "state_vector_owner_id": state_vector_owner_id,
                    "declaration_check_fingerprint": str(
                        declaration_check.get("deterministic_fingerprint", "")
                    ).strip(),
                },
            }
            violation_row["deterministic_fingerprint"] = canonical_sha256(
                dict(violation_row, deterministic_fingerprint="")
            )
            state["state_vector_violation_rows"] = sorted(
                [
                    dict(row)
                    for row in list(state.get("state_vector_violation_rows") or [])
                    + [violation_row]
                    if isinstance(row, Mapping)
                ],
                key=lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("violation_id", "")),
                ),
            )
            raise SystemCollapseError(
                "state vector declaration is missing output-affecting fields",
                reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
                details={
                    "system_id": system_token,
                    "state_vector_owner_id": state_vector_owner_id,
                    "statevec_reason_code": REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD,
                    "missing_fields": list(violation_row.get("missing_fields") or []),
                    "violation_id": str(violation_row.get("violation_id", "")).strip(),
                },
            )

    serialization = serialize_state(
        owner_id=state_vector_owner_id,
        source_state=source_state_payload,
        state_vector_definition_rows=declared_state_vector_definitions,
        current_tick=tick_value,
        expected_version=str(owner_definition.get("version", "")).strip() if owner_definition else None,
        extensions={
            "source_process_id": process_id,
            "system_id": system_token,
            "captured_assembly_count": int(len(captured_rows)),
        },
    )
    if str(serialization.get("result", "")).strip() != "complete":
        raise SystemCollapseError(
            "state vector serialization failed during system collapse",
            reason_code=REFUSAL_SYSTEM_COLLAPSE_INVALID,
            details={
                "system_id": system_token,
                "state_vector_owner_id": state_vector_owner_id,
                "statevec_reason_code": str(serialization.get("reason_code", "")).strip(),
                "statevec_message": str(serialization.get("message", "")).strip(),
            },
        )
    snapshot_row = dict(serialization.get("snapshot_row") or {})
    serialized_internal_state = _as_map(snapshot_row.get("serialized_state"))
    provenance_anchor_hash = str(serialization.get("anchor_hash", "")).strip() or canonical_sha256(serialized_internal_state)
    snapshot_id = str(snapshot_row.get("snapshot_id", "")).strip()
    snapshot_version = str(snapshot_row.get("version", "")).strip() or "1.0.0"
    state_vector_id = "statevec.system.{}".format(
        canonical_sha256(
            {
                "system_id": system_token,
                "tick": tick_value,
                "snapshot_id": snapshot_id,
                "anchor_hash": provenance_anchor_hash,
            }
        )[:16]
    )
    state_vector_row = build_system_state_vector_row(
        state_vector_id=state_vector_id,
        system_id=system_token,
        serialized_internal_state=serialized_internal_state,
        deterministic_fingerprint="",
        extensions={
            "source_process_id": process_id,
            "captured_assembly_count": int(len(captured_rows)),
            "anchor_hash": provenance_anchor_hash,
            "state_vector_owner_id": state_vector_owner_id,
            "state_vector_snapshot_id": snapshot_id,
            "state_vector_version": snapshot_version,
        },
    )

    capsule_id = "capsule.system.{}".format(canonical_sha256({"system_id": system_token, "tick": tick_value, "anchor": provenance_anchor_hash})[:16])
    macro_model_bindings = list(_as_map(system_row.get("extensions")).get("macro_model_bindings") or [])
    macro_model_set_id = str(_as_map(system_row.get("extensions")).get("macro_model_set_id", "")).strip()
    model_error_bounds_ref = str(_as_map(system_row.get("extensions")).get("model_error_bounds_ref", "")).strip()
    capsule_row = build_system_macro_capsule_row(
        capsule_id=capsule_id,
        system_id=system_token,
        interface_signature_id=str(interface_row.get("interface_signature_id", "")).strip(),
        macro_model_set_id=macro_model_set_id,
        model_error_bounds_ref=model_error_bounds_ref,
        macro_model_bindings=macro_model_bindings,
        internal_state_vector={
            "state_vector_id": state_vector_id,
            "anchor_hash": provenance_anchor_hash,
            "snapshot_id": snapshot_id,
            "owner_id": state_vector_owner_id,
            "state_vector_version": snapshot_version,
        },
        provenance_anchor_hash=provenance_anchor_hash,
        tier_mode="macro",
        deterministic_fingerprint="",
        extensions={
            "source_process_id": process_id,
            "captured_assembly_ids": list(assembly_ids),
            "boundary_invariant_ids": _sorted_tokens(system_row.get("boundary_invariant_ids")),
        },
    )

    placeholder_assembly_id = "assembly.system_capsule_placeholder.{}".format(system_token)
    placeholder_row = {
        "schema_version": "1.0.0",
        "assembly_id": placeholder_assembly_id,
        "assembly_type_id": "assembly.system.capsule_placeholder",
        "deterministic_fingerprint": "",
        "extensions": {
            "source_process_id": process_id,
            "system_id": system_token,
            "capsule_id": capsule_id,
            "interface_signature_id": str(interface_row.get("interface_signature_id", "")).strip(),
        },
    }
    placeholder_row["deterministic_fingerprint"] = canonical_sha256(dict(placeholder_row, deterministic_fingerprint=""))

    retained_rows = [
        dict(row)
        for row in assembly_rows
        if str(row.get("assembly_id", "")).strip() not in set(assembly_ids)
    ]
    state["assembly_rows"] = sorted(
        retained_rows + [placeholder_row],
        key=lambda row: str(row.get("assembly_id", "")),
    )

    state["system_state_vector_rows"] = normalize_system_state_vector_rows(
        list(state.get("system_state_vector_rows") or []) + [state_vector_row]
    )
    state["state_vector_snapshot_rows"] = normalize_state_vector_snapshot_rows(
        list(state.get("state_vector_snapshot_rows") or []) + [snapshot_row]
    )
    state["state_vector_definition_rows"] = normalize_state_vector_definition_rows(
        list(declared_state_vector_definitions or [])
    )
    state["system_macro_capsule_rows"] = normalize_system_macro_capsule_rows(
        list(state.get("system_macro_capsule_rows") or []) + [capsule_row]
    )

    collapse_event = {
        "schema_version": "1.0.0",
        "event_id": "event.system.collapse.{}".format(canonical_sha256({"capsule_id": capsule_id, "tick": tick_value})[:16]),
        "system_id": system_token,
        "capsule_id": capsule_id,
        "state_vector_id": state_vector_id,
        "tick": tick_value,
        "invariant_checks": [dict(row) for row in invariant_checks],
        "deterministic_fingerprint": "",
        "extensions": {
            "source_process_id": process_id,
            "placeholder_assembly_id": placeholder_assembly_id,
            "provenance_anchor_hash": provenance_anchor_hash,
            "interface_validation_fingerprint": str(interface_validation.get("deterministic_fingerprint", "")).strip(),
            "invariant_validation_fingerprint": str(invariant_validation.get("deterministic_fingerprint", "")).strip(),
        },
    }
    collapse_event["deterministic_fingerprint"] = canonical_sha256(dict(collapse_event, deterministic_fingerprint=""))
    state["system_collapse_event_rows"] = sorted(
        [
            dict(row)
            for row in list(state.get("system_collapse_event_rows") or []) + [collapse_event]
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
    artifact_id = "artifact.record.system_collapse.{}".format(canonical_sha256({"event_id": collapse_event["event_id"]})[:16])
    info_artifact_rows.append(
        {
            "artifact_id": artifact_id,
            "artifact_family_id": "RECORD",
            "extensions": {
                "artifact_type_id": "artifact.record.system_collapse",
                "event_id": str(collapse_event.get("event_id", "")).strip(),
                "system_id": system_token,
                "capsule_id": capsule_id,
                "state_vector_id": state_vector_id,
            },
        }
    )
    state["info_artifact_rows"] = sorted(
        info_artifact_rows,
        key=lambda row: (str(row.get("artifact_family_id", "")), str(row.get("artifact_id", ""))),
    )
    state["knowledge_artifacts"] = [dict(row) for row in list(state.get("info_artifact_rows") or [])]

    updated_systems = []
    for row in normalize_system_rows(state.get("system_rows")):
        system_row_token = str(row.get("system_id", "")).strip()
        if system_row_token != system_token:
            updated_systems.append(dict(row))
            continue
        ext = _as_map(row.get("extensions"))
        ext["last_collapse_tick"] = tick_value
        ext["active_state_vector_id"] = state_vector_id
        ext["placeholder_assembly_id"] = placeholder_assembly_id
        row["extensions"] = ext
        row["current_tier"] = "macro"
        row["active_capsule_id"] = capsule_id
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
        updated_systems.append(dict(row))
    state["system_rows"] = sorted(updated_systems, key=lambda row: str(row.get("system_id", "")))

    state["system_collapse_hash_chain"] = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "state_vector_id": str(row.get("state_vector_id", "")).strip(),
            }
            for row in list(state.get("system_collapse_event_rows") or [])
            if isinstance(row, Mapping)
        ]
    )

    return {
        "result": "complete",
        "system_id": system_token,
        "capsule_id": capsule_id,
        "state_vector_id": state_vector_id,
        "provenance_anchor_hash": provenance_anchor_hash,
        "event_id": str(collapse_event.get("event_id", "")).strip(),
        "invariant_checks": [dict(row) for row in invariant_checks],
        "placeholder_assembly_id": placeholder_assembly_id,
        "deterministic_fingerprint": canonical_sha256(
            {
                "system_id": system_token,
                "capsule_id": capsule_id,
                "state_vector_id": state_vector_id,
                "event_id": str(collapse_event.get("event_id", "")).strip(),
                "provenance_anchor_hash": provenance_anchor_hash,
            }
        ),
    }


__all__ = [
    "REFUSAL_SYSTEM_COLLAPSE_INVALID",
    "REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE",
    "REFUSAL_SYSTEM_COLLAPSE_INVALID_INTERFACE",
    "REFUSAL_SYSTEM_COLLAPSE_INVARIANT_VIOLATION",
    "SystemCollapseError",
    "build_interface_signature_row",
    "normalize_interface_signature_rows",
    "interface_signature_rows_by_system",
    "build_boundary_invariant_row",
    "normalize_boundary_invariant_rows",
    "boundary_invariant_rows_by_id",
    "build_system_state_vector_row",
    "normalize_system_state_vector_rows",
    "build_system_macro_capsule_row",
    "normalize_system_macro_capsule_rows",
    "normalize_system_rows",
    "system_rows_by_id",
    "collapse_system_graph",
]
