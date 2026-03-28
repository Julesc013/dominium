"""META-INSTR0 deterministic instrumentation lookup, access, measurement, and forensics routing."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from meta.explain import generate_explain_artifact, redact_explain_artifact
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_INSTRUMENTATION_SURFACE_MISSING = "refusal.instrumentation.surface_missing"
REFUSAL_INSTRUMENTATION_CONTROL_NOT_FOUND = "refusal.instrumentation.control_not_found"
REFUSAL_INSTRUMENTATION_MEASUREMENT_NOT_FOUND = "refusal.instrumentation.measurement_not_found"
REFUSAL_INSTRUMENTATION_FORENSICS_NOT_FOUND = "refusal.instrumentation.forensics_not_found"
REFUSAL_INSTRUMENTATION_ACCESS_DENIED = "refusal.instrumentation.access_denied"
REFUSAL_INSTRUMENTATION_INSTRUMENT_REQUIRED = "refusal.instrumentation.instrument_required"
REFUSAL_INSTRUMENTATION_EXPLAIN_CONTRACT_MISSING = "refusal.instrumentation.explain_contract_missing"

_PRIVILEGE_RANK = {"observer": 0, "operator": 1, "admin": 2}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _rows_from_registry(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
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


def _owner_key(owner_kind: object, owner_id: object) -> str:
    return "{}::{}".format(str(owner_kind or "").strip().lower(), str(owner_id or "").strip())


def _quantize(value: int, step: int) -> int:
    quantum = int(max(1, _as_int(step, 1)))
    token = int(_as_int(value, 0))
    return int(round(float(token) / float(quantum)) * quantum)


def _deterministic_error(
    *,
    owner_kind: str,
    owner_id: str,
    measurement_point_id: str,
    tick: int,
    error_bound: int,
) -> int:
    bound = int(max(0, _as_int(error_bound, 0)))
    if bound <= 0:
        return 0
    marker = canonical_sha256(
        {
            "owner_kind": str(owner_kind),
            "owner_id": str(owner_id),
            "measurement_point_id": str(measurement_point_id),
            "tick": int(max(0, _as_int(tick, 0))),
        }
    )
    span = int(bound * 2 + 1)
    value = int(int(marker[:8], 16) % span)
    return int(value - bound)


def build_control_point_row(
    *,
    control_point_id: str,
    action_template_id: str,
    required_access_policy_id: str,
    safety_interlock_refs: object,
    deterministic_fingerprint: str = "",
) -> dict:
    payload = {
        "control_point_id": str(control_point_id or "").strip(),
        "action_template_id": str(action_template_id or "").strip(),
        "required_access_policy_id": str(required_access_policy_id or "").strip(),
        "safety_interlock_refs": _tokens(safety_interlock_refs),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
    }
    if (not payload["control_point_id"]) or (not payload["action_template_id"]) or (not payload["required_access_policy_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_measurement_point_row(
    *,
    measurement_point_id: str,
    quantity_id: str,
    instrument_type_id: str,
    measurement_model_id: str,
    destructive: bool,
    redaction_policy_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "measurement_point_id": str(measurement_point_id or "").strip(),
        "quantity_id": str(quantity_id or "").strip(),
        "instrument_type_id": str(instrument_type_id or "").strip(),
        "measurement_model_id": str(measurement_model_id or "").strip(),
        "destructive": bool(destructive),
        "redaction_policy_id": str(redaction_policy_id or "").strip(),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (
        (not payload["measurement_point_id"])
        or (not payload["quantity_id"])
        or (not payload["instrument_type_id"])
        or (not payload["measurement_model_id"])
        or (not payload["redaction_policy_id"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_forensics_point_row(
    *,
    forensics_point_id: str,
    explain_contract_id: str,
    redaction_policy_id: str,
    deterministic_fingerprint: str = "",
) -> dict:
    payload = {
        "forensics_point_id": str(forensics_point_id or "").strip(),
        "explain_contract_id": str(explain_contract_id or "").strip(),
        "redaction_policy_id": str(redaction_policy_id or "").strip(),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
    }
    if (not payload["forensics_point_id"]) or (not payload["explain_contract_id"]) or (not payload["redaction_policy_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_instrumentation_surface_row(
    *,
    owner_kind: str,
    owner_id: str,
    control_points: object,
    measurement_points: object,
    forensics_points: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    controls = [
        build_control_point_row(
            control_point_id=str(dict(row).get("control_point_id", "")).strip(),
            action_template_id=str(dict(row).get("action_template_id", "")).strip(),
            required_access_policy_id=str(dict(row).get("required_access_policy_id", "")).strip(),
            safety_interlock_refs=list(dict(row).get("safety_interlock_refs") or []),
            deterministic_fingerprint=str(dict(row).get("deterministic_fingerprint", "")).strip(),
        )
        for row in _as_list(control_points)
        if isinstance(row, Mapping)
    ]
    controls = sorted((row for row in controls if row), key=lambda row: str(row.get("control_point_id", "")))
    measures = [
        build_measurement_point_row(
            measurement_point_id=str(dict(row).get("measurement_point_id", "")).strip(),
            quantity_id=str(dict(row).get("quantity_id", "")).strip(),
            instrument_type_id=str(dict(row).get("instrument_type_id", "")).strip(),
            measurement_model_id=str(dict(row).get("measurement_model_id", "")).strip(),
            destructive=bool(dict(row).get("destructive", False)),
            redaction_policy_id=str(dict(row).get("redaction_policy_id", "")).strip(),
            deterministic_fingerprint=str(dict(row).get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(dict(row).get("extensions")),
        )
        for row in _as_list(measurement_points)
        if isinstance(row, Mapping)
    ]
    measures = sorted((row for row in measures if row), key=lambda row: str(row.get("measurement_point_id", "")))
    forensics = [
        build_forensics_point_row(
            forensics_point_id=str(dict(row).get("forensics_point_id", "")).strip(),
            explain_contract_id=str(dict(row).get("explain_contract_id", "")).strip(),
            redaction_policy_id=str(dict(row).get("redaction_policy_id", "")).strip(),
            deterministic_fingerprint=str(dict(row).get("deterministic_fingerprint", "")).strip(),
        )
        for row in _as_list(forensics_points)
        if isinstance(row, Mapping)
    ]
    forensics = sorted((row for row in forensics if row), key=lambda row: str(row.get("forensics_point_id", "")))

    payload = {
        "owner_kind": str(owner_kind or "").strip().lower(),
        "owner_id": str(owner_id or "").strip(),
        "control_points": controls,
        "measurement_points": measures,
        "forensics_points": forensics,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["owner_kind"]) or (not payload["owner_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_instrumentation_surface_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("owner_kind", "")),
            str(item.get("owner_id", "")),
        ),
    ):
        normalized = build_instrumentation_surface_row(
            owner_kind=str(row.get("owner_kind", "")).strip().lower(),
            owner_id=str(row.get("owner_id", "")).strip(),
            control_points=list(row.get("control_points") or []),
            measurement_points=list(row.get("measurement_points") or []),
            forensics_points=list(row.get("forensics_points") or []),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        key = _owner_key(normalized.get("owner_kind"), normalized.get("owner_id"))
        if key and normalized:
            out[key] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def instrumentation_surfaces_by_owner(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(registry_payload, ("instrumentation_surfaces",))
    normalized = normalize_instrumentation_surface_rows(rows)
    return dict((_owner_key(row.get("owner_kind"), row.get("owner_id")), dict(row)) for row in normalized)


def resolve_instrumentation_surface(
    *,
    owner_kind: str,
    owner_id: str,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
) -> dict:
    rows = instrumentation_surfaces_by_owner(instrumentation_surface_registry_payload)
    return dict(rows.get(_owner_key(owner_kind, owner_id)) or {})


def access_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(payload, ("access_policies",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows), key=lambda item: str(item.get("access_policy_id", ""))):
        token = str(row.get("access_policy_id", "")).strip()
        if token:
            out[token] = dict(row)
    return out


def measurement_model_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(payload, ("measurement_models",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows), key=lambda item: str(item.get("measurement_model_id", ""))):
        token = str(row.get("measurement_model_id", "")).strip()
        if token:
            out[token] = dict(row)
    return out


def explain_contract_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(payload, ("explain_contracts",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows), key=lambda item: str(item.get("contract_id", ""))):
        token = str(row.get("contract_id", "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _policy_allows(
    *,
    access_policy_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    access_policy_registry_payload: Mapping[str, object] | None,
) -> Tuple[bool, str]:
    policy_rows = access_policy_rows_by_id(access_policy_registry_payload)
    policy_id = str(access_policy_id or "").strip()
    policy = dict(policy_rows.get(policy_id) or {})
    if not policy:
        return False, "missing_access_policy"

    required_entitlements = set(_tokens(policy.get("required_entitlements") or []))
    actor_entitlements = set(_tokens(_as_map(authority_context).get("entitlements") or []))
    missing_entitlements = sorted(required_entitlements - actor_entitlements)
    if missing_entitlements:
        return False, "missing_entitlements"

    required_privilege = str(policy.get("required_privilege_level", "")).strip().lower() or "observer"
    actor_privilege = str(_as_map(authority_context).get("privilege_level", "")).strip().lower() or "observer"
    if int(_PRIVILEGE_RANK.get(actor_privilege, -1)) < int(_PRIVILEGE_RANK.get(required_privilege, 0)):
        return False, "insufficient_privilege"

    if bool(policy.get("physical_access_required", False)) and (not bool(has_physical_access)):
        return False, "physical_access_required"
    return True, ""


def validate_control_access(
    *,
    owner_kind: str,
    owner_id: str,
    control_point_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
) -> dict:
    surface = resolve_instrumentation_surface(
        owner_kind=owner_kind,
        owner_id=owner_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if not surface:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_SURFACE_MISSING}
    points = dict(
        (
            str(point.get("control_point_id", "")).strip(),
            dict(point),
        )
        for point in list(surface.get("control_points") or [])
        if isinstance(point, Mapping)
    )
    point_id = str(control_point_id or "").strip()
    point = dict(points.get(point_id) or {})
    if not point:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_CONTROL_NOT_FOUND}

    allowed, reason = _policy_allows(
        access_policy_id=str(point.get("required_access_policy_id", "")).strip(),
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        access_policy_registry_payload=access_policy_registry_payload,
    )
    return {
        "result": "complete" if allowed else "refused",
        "reason_code": "" if allowed else REFUSAL_INSTRUMENTATION_ACCESS_DENIED,
        "control_point": point,
        "access_reason": str(reason),
    }


def _measurement_lookup(
    *,
    owner_kind: str,
    owner_id: str,
    measurement_point_id: str,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
) -> Tuple[dict, dict]:
    surface = resolve_instrumentation_surface(
        owner_kind=owner_kind,
        owner_id=owner_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if not surface:
        return {}, {}
    points = dict(
        (
            str(point.get("measurement_point_id", "")).strip(),
            dict(point),
        )
        for point in list(surface.get("measurement_points") or [])
        if isinstance(point, Mapping)
    )
    point = dict(points.get(str(measurement_point_id or "").strip()) or {})
    return surface, point


def _measurement_redaction(
    *,
    measured_value: int,
    redaction_policy_id: str,
    privilege_level: str,
    quantization_step: int,
) -> Tuple[object, bool, str]:
    policy_id = str(redaction_policy_id or "").strip().lower()
    privilege = str(privilege_level or "").strip().lower() or "observer"

    if policy_id == "redact.none":
        return int(measured_value), False, "none"
    if privilege == "admin":
        return int(measured_value), False, "none"
    if policy_id == "redact.inspector_default" and privilege == "operator":
        return int(measured_value), False, "none"
    if policy_id == "redact.inspector_default":
        return None, True, "masked"
    if policy_id == "redact.diegetic_quantized":
        coarse = int(max(1, _as_int(quantization_step, 1) * 10))
        return int(_quantize(int(measured_value), coarse)), True, "diegetic_quantized"
    return None, True, "masked"


def generate_measurement_observation(
    *,
    owner_kind: str,
    owner_id: str,
    measurement_point_id: str,
    raw_value: int,
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
) -> dict:
    surface, point = _measurement_lookup(
        owner_kind=owner_kind,
        owner_id=owner_id,
        measurement_point_id=measurement_point_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if not surface:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_SURFACE_MISSING}
    if not point:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_MEASUREMENT_NOT_FOUND}

    required_instrument = str(point.get("instrument_type_id", "")).strip()
    available_instruments = set(_tokens(available_instrument_type_ids))
    if required_instrument not in available_instruments:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_INSTRUMENT_REQUIRED}

    point_ext = _as_map(point.get("extensions"))
    access_policy_id = str(point_ext.get("required_access_policy_id", "")).strip() or "access.role_required"
    allowed, reason = _policy_allows(
        access_policy_id=access_policy_id,
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        access_policy_registry_payload=access_policy_registry_payload,
    )
    if not allowed:
        return {
            "result": "refused",
            "reason_code": REFUSAL_INSTRUMENTATION_ACCESS_DENIED,
            "access_reason": str(reason),
        }

    model_rows = measurement_model_rows_by_id(measurement_model_registry_payload)
    model_id = str(point.get("measurement_model_id", "")).strip()
    model_row = dict(model_rows.get(model_id) or {})
    quant_step = int(max(1, _as_int(model_row.get("quantization_step", 1), 1)))
    error_bound = int(max(0, _as_int(model_row.get("absolute_error_bound", 0), 0)))
    tick = int(max(0, _as_int(current_tick, 0)))

    error_term = _deterministic_error(
        owner_kind=str(owner_kind or "").strip().lower(),
        owner_id=str(owner_id or "").strip(),
        measurement_point_id=str(measurement_point_id or "").strip(),
        tick=tick,
        error_bound=error_bound,
    )
    measured = int(_quantize(int(_as_int(raw_value, 0)) + int(error_term), quant_step))
    privilege_level = str(_as_map(authority_context).get("privilege_level", "")).strip().lower() or "observer"
    value_out, redacted, redaction_mode = _measurement_redaction(
        measured_value=measured,
        redaction_policy_id=str(point.get("redaction_policy_id", "")).strip(),
        privilege_level=privilege_level,
        quantization_step=quant_step,
    )
    artifact_id = "artifact.observation.instrument.{}".format(
        canonical_sha256(
            {
                "owner_kind": str(owner_kind or "").strip().lower(),
                "owner_id": str(owner_id or "").strip(),
                "measurement_point_id": str(measurement_point_id or "").strip(),
                "tick": tick,
                "value": value_out,
            }
        )[:16]
    )
    artifact = {
        "artifact_id": artifact_id,
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.measurement",
        "owner_kind": str(owner_kind or "").strip().lower(),
        "owner_id": str(owner_id or "").strip(),
        "measurement_point_id": str(point.get("measurement_point_id", "")).strip(),
        "quantity_id": str(point.get("quantity_id", "")).strip(),
        "instrument_type_id": required_instrument,
        "measurement_model_id": model_id,
        "value": value_out,
        "tick": tick,
        "deterministic_fingerprint": "",
        "extensions": {
            "redaction_policy_id": str(point.get("redaction_policy_id", "")).strip(),
            "redaction_applied": bool(redacted),
            "redaction_mode": str(redaction_mode),
            "raw_value_hash": canonical_sha256(
                {
                    "owner_kind": str(owner_kind or "").strip().lower(),
                    "owner_id": str(owner_id or "").strip(),
                    "measurement_point_id": str(measurement_point_id or "").strip(),
                    "raw_value": int(_as_int(raw_value, 0)),
                    "measured_unredacted": int(measured),
                }
            ),
            "destructive": bool(point.get("destructive", False)),
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return {
        "result": "complete",
        "reason_code": "",
        "surface": surface,
        "measurement_point": point,
        "observation_artifact": artifact,
    }


def route_forensics_request(
    *,
    owner_kind: str,
    owner_id: str,
    forensics_point_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    explain_contract_registry_payload: Mapping[str, object] | None,
    event_id: str,
    target_id: str,
    event_kind_id: str,
    truth_hash_anchor: str,
    epistemic_policy_id: str,
    decision_log_rows: object = None,
    safety_event_rows: object = None,
    hazard_rows: object = None,
    compliance_rows: object = None,
    model_result_rows: object = None,
) -> dict:
    surface = resolve_instrumentation_surface(
        owner_kind=owner_kind,
        owner_id=owner_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if not surface:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_SURFACE_MISSING}

    points = dict(
        (
            str(point.get("forensics_point_id", "")).strip(),
            dict(point),
        )
        for point in list(surface.get("forensics_points") or [])
        if isinstance(point, Mapping)
    )
    point = dict(points.get(str(forensics_point_id or "").strip()) or {})
    if not point:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_FORENSICS_NOT_FOUND}

    access_policy_id = str(_as_map(point.get("extensions")).get("required_access_policy_id", "")).strip() or "access.role_required"
    allowed, reason = _policy_allows(
        access_policy_id=access_policy_id,
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        access_policy_registry_payload=access_policy_registry_payload,
    )
    if not allowed:
        return {
            "result": "refused",
            "reason_code": REFUSAL_INSTRUMENTATION_ACCESS_DENIED,
            "access_reason": str(reason),
        }

    explain_contract_id = str(point.get("explain_contract_id", "")).strip()
    contract_rows = explain_contract_rows_by_id(explain_contract_registry_payload)
    contract = dict(contract_rows.get(explain_contract_id) or {})
    if not contract:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_EXPLAIN_CONTRACT_MISSING}

    artifact = generate_explain_artifact(
        event_id=str(event_id or "").strip(),
        target_id=str(target_id or "").strip(),
        event_kind_id=str(event_kind_id or "").strip(),
        truth_hash_anchor=str(truth_hash_anchor or "").strip(),
        epistemic_policy_id=str(epistemic_policy_id or "").strip(),
        explain_contract_row=contract,
        decision_log_rows=decision_log_rows,
        safety_event_rows=safety_event_rows,
        hazard_rows=hazard_rows,
        compliance_rows=compliance_rows,
        model_result_rows=model_result_rows,
    )
    if not artifact:
        return {"result": "refused", "reason_code": REFUSAL_INSTRUMENTATION_EXPLAIN_CONTRACT_MISSING}

    redaction_policy_id = str(point.get("redaction_policy_id", "")).strip()
    policy_row = {}
    if redaction_policy_id in {"redact.diegetic_quantized", "redact.none"}:
        policy_row = {"max_inspection_level": "meso"}
    elif redaction_policy_id == "redact.inspector_default":
        privilege = str(_as_map(authority_context).get("privilege_level", "")).strip().lower() or "observer"
        policy_row = {"max_inspection_level": "micro" if privilege in {"operator", "admin"} else "meso"}
    redacted = redact_explain_artifact(
        explain_artifact_row=artifact,
        epistemic_policy_id=str(epistemic_policy_id or "").strip(),
        policy_row=policy_row,
    )
    return {
        "result": "complete",
        "reason_code": "",
        "forensics_point": point,
        "explain_artifact": redacted,
    }


__all__ = [
    "REFUSAL_INSTRUMENTATION_SURFACE_MISSING",
    "REFUSAL_INSTRUMENTATION_CONTROL_NOT_FOUND",
    "REFUSAL_INSTRUMENTATION_MEASUREMENT_NOT_FOUND",
    "REFUSAL_INSTRUMENTATION_FORENSICS_NOT_FOUND",
    "REFUSAL_INSTRUMENTATION_ACCESS_DENIED",
    "REFUSAL_INSTRUMENTATION_INSTRUMENT_REQUIRED",
    "REFUSAL_INSTRUMENTATION_EXPLAIN_CONTRACT_MISSING",
    "build_control_point_row",
    "build_measurement_point_row",
    "build_forensics_point_row",
    "build_instrumentation_surface_row",
    "normalize_instrumentation_surface_rows",
    "instrumentation_surfaces_by_owner",
    "resolve_instrumentation_surface",
    "access_policy_rows_by_id",
    "measurement_model_rows_by_id",
    "explain_contract_rows_by_id",
    "validate_control_access",
    "generate_measurement_observation",
    "route_forensics_request",
]
