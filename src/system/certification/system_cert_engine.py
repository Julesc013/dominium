"""SYS-5 deterministic system certification and revocation helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.specs import latest_spec_binding_for_target, spec_sheet_rows_by_id
from src.system.system_collapse_engine import normalize_system_rows


REFUSAL_SYSTEM_CERT_INVALID = "refusal.system.certification.invalid"
REFUSAL_SYSTEM_CERT_UNKNOWN_PROFILE = "refusal.system.certification.profile_unknown"
REFUSAL_SYSTEM_CERT_SYSTEM_UNKNOWN = "refusal.system.certification.system_unknown"


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


def _rows_from_registry_payload(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
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


def _check(check_id: str, ok: bool, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "check_id": str(check_id).strip(),
        "status": "pass" if bool(ok) else "fail",
        "message": str(message).strip(),
        "details": _as_map(details),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def certification_profile_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(registry_payload, ("certification_profiles",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows), key=lambda item: str(item.get("cert_type_id", ""))):
        cert_type_id = str(row.get("cert_type_id", "")).strip()
        if not cert_type_id:
            continue
        payload = {
            "schema_version": "1.0.0",
            "cert_type_id": cert_type_id,
            "required_spec_checks": _sorted_tokens(row.get("required_spec_checks")),
            "required_safety_patterns": _sorted_tokens(row.get("required_safety_patterns")),
            "required_invariants": _sorted_tokens(row.get("required_invariants")),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[cert_type_id] = payload
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_system_certification_result_row(
    *,
    result_id: str,
    system_id: str,
    cert_type_id: str,
    passed: bool,
    failed_checks: object,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    system_token = str(system_id or "").strip()
    cert_token = str(cert_type_id or "").strip()
    if (not system_token) or (not cert_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "result_id": str(result_id or "").strip(),
        "system_id": system_token,
        "cert_type_id": cert_token,
        "pass": bool(passed),
        "failed_checks": _sorted_tokens(failed_checks),
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["result_id"]:
        payload["result_id"] = "result.system.certification.{}".format(
            canonical_sha256(
                {
                    "system_id": system_token,
                    "cert_type_id": cert_token,
                    "pass": bool(payload["pass"]),
                    "failed_checks": list(payload["failed_checks"]),
                    "tick": int(payload["tick"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_system_certification_result_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("cert_type_id", "")),
            str(item.get("result_id", "")),
        ),
    ):
        normalized = build_system_certification_result_row(
            result_id=str(row.get("result_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            cert_type_id=str(row.get("cert_type_id", "")).strip(),
            passed=bool(row.get("pass", False)),
            failed_checks=row.get("failed_checks"),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        result_id = str(normalized.get("result_id", "")).strip()
        if result_id:
            out[result_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_system_certificate_artifact_row(
    *,
    cert_id: str,
    system_id: str,
    cert_type_id: str,
    issuer_subject_id: str,
    issued_tick: int,
    valid_until_tick: int | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    system_token = str(system_id or "").strip()
    cert_type_token = str(cert_type_id or "").strip()
    issuer_token = str(issuer_subject_id or "").strip()
    if (not system_token) or (not cert_type_token) or (not issuer_token):
        return {}
    issued = int(max(0, _as_int(issued_tick, 0)))
    valid_until = None if valid_until_tick is None else int(max(issued, _as_int(valid_until_tick, issued)))
    payload = {
        "schema_version": "1.0.0",
        "cert_id": str(cert_id or "").strip(),
        "system_id": system_token,
        "cert_type_id": cert_type_token,
        "issuer_subject_id": issuer_token,
        "issued_tick": issued,
        "valid_until_tick": valid_until,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["cert_id"]:
        payload["cert_id"] = "cert.system.{}".format(
            canonical_sha256(
                {
                    "system_id": system_token,
                    "cert_type_id": cert_type_token,
                    "issuer_subject_id": issuer_token,
                    "issued_tick": int(issued),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_system_certificate_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("issued_tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("cert_type_id", "")),
            str(item.get("cert_id", "")),
        ),
    ):
        normalized = build_system_certificate_artifact_row(
            cert_id=str(row.get("cert_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            cert_type_id=str(row.get("cert_type_id", "")).strip(),
            issuer_subject_id=str(row.get("issuer_subject_id", "")).strip(),
            issued_tick=int(max(0, _as_int(row.get("issued_tick", 0), 0))),
            valid_until_tick=(
                None
                if row.get("valid_until_tick") is None
                else int(max(0, _as_int(row.get("valid_until_tick", 0), 0)))
            ),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        cert_id = str(normalized.get("cert_id", "")).strip()
        if cert_id:
            out[cert_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_system_certificate_revocation_row(
    *,
    event_id: str,
    system_id: str,
    cert_id: str,
    cert_type_id: str,
    reason_code: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    system_token = str(system_id or "").strip()
    cert_token = str(cert_id or "").strip()
    cert_type_token = str(cert_type_id or "").strip()
    reason_token = str(reason_code or "").strip() or "event.system.certificate_revoked"
    tick_value = int(max(0, _as_int(tick, 0)))
    if (not system_token) or (not cert_token) or (not cert_type_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id or "").strip(),
        "system_id": system_token,
        "cert_id": cert_token,
        "cert_type_id": cert_type_token,
        "reason_code": reason_token,
        "tick": tick_value,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"]:
        payload["event_id"] = "event.system.certificate_revocation.{}".format(
            canonical_sha256(
                {
                    "system_id": system_token,
                    "cert_id": cert_token,
                    "cert_type_id": cert_type_token,
                    "reason_code": reason_token,
                    "tick": tick_value,
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_system_certificate_revocation_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("cert_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized = build_system_certificate_revocation_row(
            event_id=str(row.get("event_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            cert_id=str(row.get("cert_id", "")).strip(),
            cert_type_id=str(row.get("cert_type_id", "")).strip(),
            reason_code=str(row.get("reason_code", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        event_id = str(normalized.get("event_id", "")).strip()
        if event_id:
            out[event_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _latest_compliance_result(
    *,
    compliance_result_rows: object,
    target_kind: str,
    target_id: str,
    spec_id: str | None = None,
) -> dict:
    token_kind = str(target_kind or "").strip()
    token_target = str(target_id or "").strip()
    token_spec = str(spec_id or "").strip()
    rows = [
        dict(item)
        for item in list(compliance_result_rows or [])
        if isinstance(item, Mapping)
        and str(item.get("target_kind", "")).strip() == token_kind
        and str(item.get("target_id", "")).strip() == token_target
        and ((not token_spec) or str(item.get("spec_id", "")).strip() == token_spec)
    ]
    if not rows:
        return {}
    return sorted(
        rows,
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("result_id", "")),
        ),
    )[-1]


def _safety_pattern_ids_for_system(
    *,
    system_id: str,
    system_row: Mapping[str, object],
    safety_instance_rows: object,
) -> List[str]:
    token = str(system_id or "").strip()
    ext = _as_map(dict(system_row or {}).get("extensions"))
    from_extensions = _sorted_tokens(
        list(ext.get("safety_pattern_ids") or []) + list(ext.get("safety_patterns") or [])
    )
    from_instances: List[str] = []
    for row in sorted(
        (dict(item) for item in list(safety_instance_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (str(item.get("pattern_id", "")), str(item.get("instance_id", ""))),
    ):
        pattern_id = str(row.get("pattern_id", "")).strip()
        if not pattern_id:
            continue
        target_ids = _sorted_tokens(list(row.get("target_ids") or []))
        if token and token in target_ids:
            from_instances.append(pattern_id)
    return _sorted_tokens(from_extensions + from_instances)


def _next_cert_version(
    *,
    system_id: str,
    cert_type_id: str,
    certificate_rows: object,
) -> int:
    token_system = str(system_id or "").strip()
    token_type = str(cert_type_id or "").strip()
    versions: List[int] = []
    for row in normalize_system_certificate_artifact_rows(certificate_rows):
        if str(row.get("system_id", "")).strip() != token_system:
            continue
        if str(row.get("cert_type_id", "")).strip() != token_type:
            continue
        ext = _as_map(row.get("extensions"))
        versions.append(int(max(0, _as_int(ext.get("cert_version", 0), 0))))
    return int(max(versions) + 1) if versions else 1


def evaluate_system_certification(
    *,
    current_tick: int,
    system_id: str,
    cert_type_id: str,
    issuer_subject_id: str,
    certification_profile_registry_payload: Mapping[str, object] | None,
    system_rows: object,
    interface_validation_result: Mapping[str, object] | None,
    invariant_validation_result: Mapping[str, object] | None,
    spec_binding_rows: object,
    spec_compliance_result_rows: object,
    spec_sheet_rows: object,
    safety_instance_rows: object,
    degradation_event_rows: object,
    existing_certificate_rows: object = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    system_token = str(system_id or "").strip()
    cert_type_token = str(cert_type_id or "").strip()
    issuer_token = str(issuer_subject_id or "").strip() or "subject.system.cert_engine"
    profiles_by_id = certification_profile_rows_by_id(certification_profile_registry_payload)
    if cert_type_token not in profiles_by_id:
        return {
            "result": "refused",
            "reason_code": REFUSAL_SYSTEM_CERT_UNKNOWN_PROFILE,
            "system_id": system_token,
            "cert_type_id": cert_type_token,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "system_id": system_token,
                    "cert_type_id": cert_type_token,
                    "reason_code": REFUSAL_SYSTEM_CERT_UNKNOWN_PROFILE,
                }
            ),
        }

    system_rows_by_id = {
        str(row.get("system_id", "")).strip(): dict(row)
        for row in normalize_system_rows(system_rows)
        if str(row.get("system_id", "")).strip()
    }
    system_row = dict(system_rows_by_id.get(system_token) or {})
    if not system_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_SYSTEM_CERT_SYSTEM_UNKNOWN,
            "system_id": system_token,
            "cert_type_id": cert_type_token,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "system_id": system_token,
                    "cert_type_id": cert_type_token,
                    "reason_code": REFUSAL_SYSTEM_CERT_SYSTEM_UNKNOWN,
                }
            ),
        }

    profile_row = dict(profiles_by_id.get(cert_type_token) or {})
    checks: List[dict] = []

    interface_ok = str(_as_map(interface_validation_result).get("result", "")).strip() == "complete"
    checks.append(
        _check(
            "interface.validation.complete",
            interface_ok,
            "interface signature validation state",
            {
                "result": str(_as_map(interface_validation_result).get("result", "")).strip(),
                "interface_signature_id": str(system_row.get("interface_signature_id", "")).strip(),
            },
        )
    )
    invariant_ok = str(_as_map(invariant_validation_result).get("result", "")).strip() == "complete"
    checks.append(
        _check(
            "invariant.validation.complete",
            invariant_ok,
            "boundary invariant validation state",
            {
                "result": str(_as_map(invariant_validation_result).get("result", "")).strip(),
                "boundary_invariant_ids": _sorted_tokens(system_row.get("boundary_invariant_ids")),
            },
        )
    )

    declared_invariants = set(_sorted_tokens(system_row.get("boundary_invariant_ids")))
    for invariant_id in _sorted_tokens(profile_row.get("required_invariants")):
        checks.append(
            _check(
                "invariant.required.{}".format(invariant_id),
                invariant_id in declared_invariants,
                "required invariant declaration",
                {"invariant_id": invariant_id},
            )
        )

    declared_safety_patterns = set(
        _safety_pattern_ids_for_system(
            system_id=system_token,
            system_row=system_row,
            safety_instance_rows=safety_instance_rows,
        )
    )
    for pattern_id in _sorted_tokens(profile_row.get("required_safety_patterns")):
        checks.append(
            _check(
                "safety.required.{}".format(pattern_id),
                pattern_id in declared_safety_patterns,
                "required safety pattern presence",
                {"pattern_id": pattern_id},
            )
        )

    system_ext = _as_map(system_row.get("extensions"))
    spec_target_kind = str(system_ext.get("spec_target_kind", "system")).strip() or "system"
    spec_target_id = str(system_ext.get("spec_target_id", system_token)).strip() or system_token
    binding_row = latest_spec_binding_for_target(
        binding_rows=spec_binding_rows,
        target_kind=spec_target_kind,
        target_id=spec_target_id,
    )
    bound_spec_id = str(binding_row.get("spec_id", "")).strip()
    spec_row = dict(spec_sheet_rows_by_id(spec_sheet_rows).get(bound_spec_id) or {})
    bound_spec_type_id = str(spec_row.get("spec_type_id", "")).strip()
    compliance_row = _latest_compliance_result(
        compliance_result_rows=spec_compliance_result_rows,
        target_kind=spec_target_kind,
        target_id=spec_target_id,
        spec_id=bound_spec_id or None,
    )
    if (not compliance_row) and bound_spec_id:
        compliance_row = _latest_compliance_result(
            compliance_result_rows=spec_compliance_result_rows,
            target_kind=spec_target_kind,
            target_id=spec_target_id,
            spec_id=None,
        )

    required_spec_checks = _sorted_tokens(profile_row.get("required_spec_checks"))
    if required_spec_checks:
        checks.append(
            _check(
                "spec.binding.present",
                bool(bound_spec_id),
                "spec binding required for certification profile",
                {
                    "target_kind": spec_target_kind,
                    "target_id": spec_target_id,
                },
            )
        )
        checks.append(
            _check(
                "spec.required_type.match",
                bool(bound_spec_type_id) and bound_spec_type_id in set(required_spec_checks),
                "bound spec_type_id must satisfy required_spec_checks",
                {
                    "bound_spec_id": bound_spec_id,
                    "bound_spec_type_id": bound_spec_type_id,
                    "required_spec_checks": list(required_spec_checks),
                },
            )
        )
        overall_grade = str(compliance_row.get("overall_grade", "")).strip().lower()
        checks.append(
            _check(
                "spec.compliance.pass",
                bool(compliance_row) and overall_grade in {"pass", "warn"},
                "spec compliance must not fail for certification",
                {
                    "result_id": str(compliance_row.get("result_id", "")).strip(),
                    "overall_grade": overall_grade,
                },
            )
        )

    degradation_threshold = int(
        max(
            1,
            _as_int(_as_map(profile_row.get("extensions")).get("degradation_failure_threshold_permille", 950), 950),
        )
    )
    degradation_breach = bool(system_ext.get("degradation_threshold_breached", False))
    if not degradation_breach:
        for row in list(degradation_event_rows or []):
            if not isinstance(row, Mapping):
                continue
            if str(row.get("target_id", "")).strip() != system_token:
                continue
            level_after = int(max(0, _as_int(row.get("level_after", 0), 0)))
            if level_after >= degradation_threshold:
                degradation_breach = True
                break
    checks.append(
        _check(
            "degradation.within_limits",
            not degradation_breach,
            "degradation threshold check",
            {"threshold_permille": int(degradation_threshold)},
        )
    )

    checks_sorted = sorted(checks, key=lambda row: str(row.get("check_id", "")))
    failed_checks = [
        str(row.get("check_id", "")).strip()
        for row in checks_sorted
        if str(row.get("status", "")).strip() != "pass"
    ]
    passed = not failed_checks

    result_row = build_system_certification_result_row(
        result_id="",
        system_id=system_token,
        cert_type_id=cert_type_token,
        passed=bool(passed),
        failed_checks=list(failed_checks),
        tick=int(tick),
        deterministic_fingerprint="",
        extensions={
            "source_process_id": "process.system_evaluate_certification",
            "spec_target_kind": spec_target_kind,
            "spec_target_id": spec_target_id,
            "bound_spec_id": bound_spec_id or None,
            "bound_spec_type_id": bound_spec_type_id or None,
            "compliance_result_id": str(compliance_row.get("result_id", "")).strip() or None,
            "check_rows": [dict(row) for row in checks_sorted],
        },
    )
    cert_row = {}
    if passed:
        validity_ticks = int(
            max(0, _as_int(_as_map(profile_row.get("extensions")).get("validity_ticks", 0), 0))
        )
        valid_until_tick = None if validity_ticks <= 0 else int(tick + validity_ticks)
        cert_version = _next_cert_version(
            system_id=system_token,
            cert_type_id=cert_type_token,
            certificate_rows=existing_certificate_rows,
        )
        cert_row = build_system_certificate_artifact_row(
            cert_id="",
            system_id=system_token,
            cert_type_id=cert_type_token,
            issuer_subject_id=issuer_token,
            issued_tick=int(tick),
            valid_until_tick=valid_until_tick,
            deterministic_fingerprint="",
            extensions={
                "status": "active",
                "cert_version": int(cert_version),
                "result_id": str(result_row.get("result_id", "")).strip(),
                "validity_conditions": {
                    "profile_id": cert_type_token,
                    "required_spec_checks": list(required_spec_checks),
                    "required_safety_patterns": _sorted_tokens(profile_row.get("required_safety_patterns")),
                    "required_invariants": _sorted_tokens(profile_row.get("required_invariants")),
                },
            },
        )

    return {
        "result": "complete",
        "reason_code": "",
        "system_id": system_token,
        "cert_type_id": cert_type_token,
        "certification_result_row": dict(result_row),
        "certificate_artifact_row": dict(cert_row),
        "check_rows": [dict(row) for row in checks_sorted],
        "failed_checks": list(failed_checks),
        "deterministic_fingerprint": canonical_sha256(
            {
                "system_id": system_token,
                "cert_type_id": cert_type_token,
                "result_id": str(result_row.get("result_id", "")).strip(),
                "cert_id": str(cert_row.get("cert_id", "")).strip(),
                "failed_checks": list(failed_checks),
            }
        ),
    }


def revoke_system_certificates(
    *,
    current_tick: int,
    system_id: str,
    reason_code: str,
    certificate_rows: object,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    system_token = str(system_id or "").strip()
    reason_token = str(reason_code or "").strip() or "event.system.certificate_revoked"
    if not system_token:
        return {
            "certificate_rows": normalize_system_certificate_artifact_rows(certificate_rows),
            "revocation_rows": [],
            "revoked_cert_ids": [],
            "deterministic_fingerprint": canonical_sha256({"system_id": system_token, "reason_code": reason_token}),
        }

    normalized_certs = normalize_system_certificate_artifact_rows(certificate_rows)
    updated_rows: List[dict] = []
    revocation_rows: List[dict] = []
    revoked_cert_ids: List[str] = []

    for row in sorted(
        (dict(item) for item in normalized_certs if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            str(item.get("cert_type_id", "")),
            str(item.get("cert_id", "")),
        ),
    ):
        row_system_id = str(row.get("system_id", "")).strip()
        if row_system_id != system_token:
            updated_rows.append(dict(row))
            continue
        ext = _as_map(row.get("extensions"))
        status = str(ext.get("status", "active")).strip().lower() or "active"
        cert_id = str(row.get("cert_id", "")).strip()
        if status != "active":
            updated_rows.append(dict(row))
            continue
        next_ext = dict(ext)
        next_ext["status"] = "revoked"
        next_ext["revoked_tick"] = int(tick)
        next_ext["revocation_reason_code"] = reason_token
        updated_row = build_system_certificate_artifact_row(
            cert_id=cert_id,
            system_id=row_system_id,
            cert_type_id=str(row.get("cert_type_id", "")).strip(),
            issuer_subject_id=str(row.get("issuer_subject_id", "")).strip(),
            issued_tick=int(max(0, _as_int(row.get("issued_tick", 0), 0))),
            valid_until_tick=(
                None
                if row.get("valid_until_tick") is None
                else int(max(0, _as_int(row.get("valid_until_tick", 0), 0)))
            ),
            deterministic_fingerprint="",
            extensions=next_ext,
        )
        if updated_row:
            updated_rows.append(updated_row)
        revocation_row = build_system_certificate_revocation_row(
            event_id="",
            system_id=row_system_id,
            cert_id=cert_id,
            cert_type_id=str(row.get("cert_type_id", "")).strip(),
            reason_code=reason_token,
            tick=int(tick),
            deterministic_fingerprint="",
            extensions={
                "source_process_id": "process.system_evaluate_certification",
            },
        )
        if revocation_row:
            revocation_rows.append(revocation_row)
            revoked_cert_ids.append(cert_id)

    return {
        "certificate_rows": normalize_system_certificate_artifact_rows(updated_rows),
        "revocation_rows": normalize_system_certificate_revocation_rows(revocation_rows),
        "revoked_cert_ids": _sorted_tokens(revoked_cert_ids),
        "deterministic_fingerprint": canonical_sha256(
            {
                "system_id": system_token,
                "reason_code": reason_token,
                "revoked_cert_ids": _sorted_tokens(revoked_cert_ids),
            }
        ),
    }


__all__ = [
    "REFUSAL_SYSTEM_CERT_INVALID",
    "REFUSAL_SYSTEM_CERT_UNKNOWN_PROFILE",
    "REFUSAL_SYSTEM_CERT_SYSTEM_UNKNOWN",
    "build_system_certification_result_row",
    "normalize_system_certification_result_rows",
    "build_system_certificate_artifact_row",
    "normalize_system_certificate_artifact_rows",
    "build_system_certificate_revocation_row",
    "normalize_system_certificate_revocation_rows",
    "certification_profile_rows_by_id",
    "evaluate_system_certification",
    "revoke_system_certificates",
]
