"""Deterministic SPEC-1 SpecSheet loading, binding, and compliance evaluation."""

from __future__ import annotations

import re
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_SPEC_NONCOMPLIANT = "refusal.spec.noncompliant"

_VALID_TARGET_KINDS = {"structure", "ag", "geometry", "vehicle", "network_edge"}
_GRADE_RANK = {"pass": 0, "warn": 1, "fail": 2}
_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

_BUILTIN_PARAMETER_SCHEMAS = {
    "dominium.schema.spec.params.track.v1": {
        "required_keys": ["gauge_mm"],
        "numeric_keys": ["gauge_mm", "min_clearance_mm", "min_curvature_radius_mm", "max_speed_kph"],
        "string_keys": [],
    },
    "dominium.schema.spec.params.road.v1": {
        "required_keys": ["lane_width_mm"],
        "numeric_keys": ["lane_width_mm", "lane_count", "max_speed_kph", "shoulder_width_mm"],
        "string_keys": [],
    },
    "dominium.schema.spec.params.tunnel.v1": {
        "required_keys": ["inner_width_mm", "inner_height_mm"],
        "numeric_keys": ["inner_width_mm", "inner_height_mm", "emergency_walkway_width_mm", "max_speed_kph"],
        "string_keys": [],
    },
    "dominium.schema.spec.params.bridge.v1": {
        "required_keys": [],
        "numeric_keys": ["max_span_mm", "min_load_rating_kg", "max_speed_kph"],
        "string_keys": ["interface_profile_id"],
    },
    "dominium.schema.spec.params.vehicle_interface.v1": {
        "required_keys": ["interface_profile_id"],
        "numeric_keys": ["max_speed_kph", "max_axle_load_kg"],
        "string_keys": ["interface_profile_id"],
    },
    "dominium.schema.spec.params.docking_interface.v1": {
        "required_keys": ["interface_profile_id"],
        "numeric_keys": ["alignment_tolerance_mm", "max_docking_speed_kph"],
        "string_keys": ["interface_profile_id"],
    },
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _best_grade(a: str, b: str) -> str:
    token_a = str(a).strip() if str(a).strip() in _GRADE_RANK else "pass"
    token_b = str(b).strip() if str(b).strip() in _GRADE_RANK else "pass"
    return token_a if _GRADE_RANK[token_a] >= _GRADE_RANK[token_b] else token_b


def spec_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("spec_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("spec_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("spec_type_id", ""))):
        spec_type_id = str(row.get("spec_type_id", "")).strip()
        if not spec_type_id:
            continue
        out[spec_type_id] = {
            "schema_version": "1.0.0",
            "spec_type_id": spec_type_id,
            "description": str(row.get("description", "")).strip(),
            "parameter_schema_id": str(row.get("parameter_schema_id", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def tolerance_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("tolerance_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("tolerance_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("tolerance_policy_id", ""))):
        tolerance_policy_id = str(row.get("tolerance_policy_id", "")).strip()
        if not tolerance_policy_id:
            continue
        out[tolerance_policy_id] = {
            "schema_version": "1.0.0",
            "tolerance_policy_id": tolerance_policy_id,
            "description": str(row.get("description", "")).strip(),
            "numeric_tolerances": _as_map(row.get("numeric_tolerances")),
            "rounding_rules": _as_map(row.get("rounding_rules")),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def compliance_check_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("compliance_checks")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("compliance_checks")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("check_id", ""))):
        check_id = str(row.get("check_id", "")).strip()
        if not check_id:
            continue
        output_grade = str(row.get("output_grade", "")).strip()
        if output_grade not in _GRADE_RANK:
            output_grade = "warn"
        out[check_id] = {
            "schema_version": "1.0.0",
            "check_id": check_id,
            "description": str(row.get("description", "")).strip(),
            "applies_to_target_kinds": _sorted_unique_strings(row.get("applies_to_target_kinds")),
            "required_inputs": _sorted_unique_strings(row.get("required_inputs")),
            "output_grade": output_grade,
            "failure_refusal_code": (
                None
                if row.get("failure_refusal_code") is None
                else str(row.get("failure_refusal_code", "")).strip() or None
            ),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def _validate_parameter_schema(*, parameter_schema_id: str, parameters: Mapping[str, object]) -> Tuple[bool, List[str]]:
    schema = _BUILTIN_PARAMETER_SCHEMAS.get(str(parameter_schema_id).strip())
    if not schema:
        return False, ["unknown parameter_schema_id '{}'".format(str(parameter_schema_id).strip())]
    errors: List[str] = []
    required_keys = _sorted_unique_strings(schema.get("required_keys"))
    numeric_keys = set(_sorted_unique_strings(schema.get("numeric_keys")))
    string_keys = set(_sorted_unique_strings(schema.get("string_keys")))
    params = dict(parameters or {})
    for key in required_keys:
        if key not in params:
            errors.append("missing required parameter '{}'".format(key))
    for key, value in sorted(params.items(), key=lambda item: str(item[0])):
        token = str(key).strip()
        if not token:
            errors.append("parameter key must be non-empty")
            continue
        if token in numeric_keys and (not isinstance(value, (int, float)) or isinstance(value, bool)):
            errors.append("parameter '{}' must be numeric".format(token))
        if token in string_keys and not isinstance(value, str):
            errors.append("parameter '{}' must be string".format(token))
    return len(errors) == 0, sorted(errors)


def normalize_spec_sheet_rows(
    *,
    spec_rows: object,
    spec_type_rows: Mapping[str, dict],
    tolerance_policy_rows: Mapping[str, dict],
    compliance_check_rows: Mapping[str, dict],
) -> Tuple[List[dict], List[dict]]:
    if not isinstance(spec_rows, list):
        spec_rows = []
    errors: List[dict] = []
    out_by_id: Dict[str, dict] = {}
    seen_ids = set()
    known_spec_type_ids = set(str(key).strip() for key in spec_type_rows.keys() if str(key).strip())
    known_tolerance_ids = set(str(key).strip() for key in tolerance_policy_rows.keys() if str(key).strip())
    known_check_ids = set(str(key).strip() for key in compliance_check_rows.keys() if str(key).strip())
    for row in sorted((dict(item) for item in spec_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("spec_id", ""))):
        spec_id = str(row.get("spec_id", "")).strip()
        spec_type_id = str(row.get("spec_type_id", "")).strip()
        description = str(row.get("description", "")).strip()
        parameters = row.get("parameters")
        tolerance_policy_id = row.get("tolerance_policy_id")
        compliance_ids = _sorted_unique_strings(row.get("compliance_check_ids"))
        version_introduced = str(row.get("version_introduced", "")).strip()
        deprecated = bool(row.get("deprecated", False))
        extensions = row.get("extensions")

        if (
            (not spec_id)
            or (not spec_type_id)
            or (not isinstance(parameters, Mapping))
            or (not isinstance(extensions, Mapping))
            or (not _SEMVER_RE.fullmatch(version_introduced))
        ):
            errors.append(
                {
                    "code": "refuse.spec.invalid_sheet",
                    "message": "spec sheet entry '{}' missing required fields".format(spec_id or "<missing>"),
                    "path": "$.spec_sheets",
                }
            )
            continue
        if spec_id in seen_ids:
            errors.append(
                {
                    "code": "refuse.spec.duplicate_spec_id",
                    "message": "duplicate spec_id '{}'".format(spec_id),
                    "path": "$.spec_sheets.spec_id",
                }
            )
            continue
        if spec_type_id not in known_spec_type_ids:
            errors.append(
                {
                    "code": "refuse.spec.unknown_spec_type",
                    "message": "spec '{}' references unknown spec_type_id '{}'".format(spec_id, spec_type_id),
                    "path": "$.spec_sheets.spec_type_id",
                }
            )
            continue
        tolerance_id = None if tolerance_policy_id is None else str(tolerance_policy_id).strip() or None
        if tolerance_id and tolerance_id not in known_tolerance_ids:
            errors.append(
                {
                    "code": "refuse.spec.unknown_tolerance_policy",
                    "message": "spec '{}' references unknown tolerance_policy_id '{}'".format(spec_id, tolerance_id),
                    "path": "$.spec_sheets.tolerance_policy_id",
                }
            )
            continue
        missing_check_ids = [token for token in compliance_ids if token not in known_check_ids]
        if missing_check_ids:
            errors.append(
                {
                    "code": "refuse.spec.unknown_compliance_check",
                    "message": "spec '{}' references unknown compliance checks: {}".format(
                        spec_id,
                        ",".join(sorted(missing_check_ids)),
                    ),
                    "path": "$.spec_sheets.compliance_check_ids",
                }
            )
            continue
        parameter_schema_id = str((dict(spec_type_rows.get(spec_type_id) or {}).get("parameter_schema_id", ""))).strip()
        valid_params, param_errors = _validate_parameter_schema(
            parameter_schema_id=parameter_schema_id,
            parameters=dict(parameters),
        )
        if not valid_params:
            errors.append(
                {
                    "code": "refuse.spec.invalid_parameters",
                    "message": "spec '{}' failed strict parameter validation for '{}' ({})".format(
                        spec_id,
                        parameter_schema_id,
                        "; ".join(param_errors),
                    ),
                    "path": "$.spec_sheets.parameters",
                }
            )
            continue
        normalized = {
            "schema_version": "1.0.0",
            "spec_id": spec_id,
            "spec_type_id": spec_type_id,
            "description": description,
            "parameters": _canon(dict(parameters)),
            "tolerance_policy_id": tolerance_id,
            "compliance_check_ids": list(compliance_ids),
            "version_introduced": version_introduced,
            "deprecated": bool(deprecated),
            "extensions": _canon(dict(extensions)),
        }
        out_by_id[spec_id] = normalized
        seen_ids.add(spec_id)
    out_rows = [dict(out_by_id[key]) for key in sorted(out_by_id.keys())]
    return out_rows, sorted(errors, key=lambda row: (str(row.get("code", "")), str(row.get("path", "")), str(row.get("message", ""))))


def load_spec_sheet_rows(
    *,
    inline_rows: object = None,
    pack_payloads: object = None,
    spec_type_registry: Mapping[str, object] | None,
    tolerance_policy_registry: Mapping[str, object] | None,
    compliance_check_registry: Mapping[str, object] | None,
) -> Tuple[List[dict], List[dict]]:
    rows: List[dict] = []
    if isinstance(inline_rows, list):
        rows.extend(dict(item) for item in inline_rows if isinstance(item, Mapping))
    if isinstance(pack_payloads, list):
        for payload in sorted((dict(item) for item in pack_payloads if isinstance(item, Mapping)), key=lambda item: str(item.get("pack_id", ""))):
            pack_rows = payload.get("spec_sheets")
            if not isinstance(pack_rows, list):
                pack_rows = _as_map(payload.get("payload")).get("spec_sheets")
            if not isinstance(pack_rows, list):
                continue
            rows.extend(dict(item) for item in pack_rows if isinstance(item, Mapping))
    return normalize_spec_sheet_rows(
        spec_rows=rows,
        spec_type_rows=spec_type_rows_by_id(spec_type_registry),
        tolerance_policy_rows=tolerance_policy_rows_by_id(tolerance_policy_registry),
        compliance_check_rows=compliance_check_rows_by_id(compliance_check_registry),
    )


def spec_sheet_rows_by_id(rows: object) -> Dict[str, dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("spec_id", ""))):
        spec_id = str(row.get("spec_id", "")).strip()
        if not spec_id:
            continue
        out[spec_id] = dict(row)
    return out


def build_spec_binding(
    *,
    spec_id: str,
    target_kind: str,
    target_id: str,
    applied_tick: int,
    source_event_id: str | None = None,
    binding_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    spec_token = str(spec_id).strip()
    target_kind_token = str(target_kind).strip()
    target_id_token = str(target_id).strip()
    applied = int(max(0, _as_int(applied_tick, 0)))
    source_event_token = None if source_event_id is None else str(source_event_id).strip() or None
    ext = _canon(dict(extensions or {}))
    normalized_binding_id = str(binding_id).strip()
    if not normalized_binding_id:
        normalized_binding_id = "spec.binding.{}".format(
            canonical_sha256(
                {
                    "spec_id": spec_token,
                    "target_kind": target_kind_token,
                    "target_id": target_id_token,
                    "applied_tick": int(applied),
                    "source_event_id": source_event_token,
                    "extensions": ext,
                }
            )[:16]
        )
    payload = {
        "schema_version": "1.0.0",
        "binding_id": normalized_binding_id,
        "spec_id": spec_token,
        "target_kind": target_kind_token,
        "target_id": target_id_token,
        "applied_tick": int(applied),
        "source_event_id": source_event_token,
        "deterministic_fingerprint": "",
        "extensions": ext,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_spec_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out_by_id: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_kind", "")),
            str(item.get("target_id", "")),
            _as_int(item.get("applied_tick", 0), 0),
            str(item.get("binding_id", "")),
        ),
    ):
        spec_id = str(row.get("spec_id", "")).strip()
        target_kind = str(row.get("target_kind", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        if (not spec_id) or (target_kind not in _VALID_TARGET_KINDS) or (not target_id):
            continue
        normalized = build_spec_binding(
            binding_id=str(row.get("binding_id", "")).strip(),
            spec_id=spec_id,
            target_kind=target_kind,
            target_id=target_id,
            applied_tick=_as_int(row.get("applied_tick", 0), 0),
            source_event_id=(
                None if row.get("source_event_id") is None else str(row.get("source_event_id", "")).strip() or None
            ),
            extensions=_as_map(row.get("extensions")),
        )
        out_by_id[str(normalized.get("binding_id", "")).strip()] = normalized
    return sorted(
        (dict(out_by_id[key]) for key in sorted(out_by_id.keys()) if key),
        key=lambda row: (
            str(row.get("target_kind", "")),
            str(row.get("target_id", "")),
            _as_int(row.get("applied_tick", 0), 0),
            str(row.get("binding_id", "")),
        ),
    )


def latest_spec_binding_for_target(
    *,
    binding_rows: object,
    target_kind: str,
    target_id: str,
) -> dict:
    token_kind = str(target_kind).strip()
    token_target = str(target_id).strip()
    rows = normalize_spec_binding_rows(binding_rows)
    candidates = [
        dict(row)
        for row in rows
        if str(row.get("target_kind", "")).strip() == token_kind
        and str(row.get("target_id", "")).strip() == token_target
    ]
    if not candidates:
        return {}
    return sorted(
        candidates,
        key=lambda row: (_as_int(row.get("applied_tick", 0), 0), str(row.get("binding_id", ""))),
    )[-1]


def _input_value(input_catalog: Mapping[str, object], key: str):
    return dict(input_catalog or {}).get(str(key).strip())


def _as_number(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    return None


def _check_grade_from_declared(declared_grade: str) -> str:
    token = str(declared_grade).strip()
    if token in _GRADE_RANK:
        return token
    return "warn"


def _evaluate_check(
    *,
    check_row: Mapping[str, object],
    spec_row: Mapping[str, object],
    tolerance_row: Mapping[str, object],
    input_catalog: Mapping[str, object],
) -> dict:
    check_id = str(check_row.get("check_id", "")).strip()
    declared_grade = _check_grade_from_declared(str(check_row.get("output_grade", "")).strip())
    required_inputs = _sorted_unique_strings(check_row.get("required_inputs"))
    missing_inputs = [key for key in required_inputs if _input_value(input_catalog, key) is None]
    params = _as_map(spec_row.get("parameters"))
    tolerances = _as_map(tolerance_row.get("numeric_tolerances"))
    grade = "pass"
    details = {}

    if check_id == "check.geometry.clearance":
        required_min = _as_number(params.get("min_clearance_mm"))
        if required_min is None:
            required_min = _as_number(params.get("clearance_mm"))
        measured_row = _as_map(_input_value(input_catalog, "derived.geometry.clearance_summary"))
        measured_min = _as_number(measured_row.get("min_clearance_mm"))
        tolerance = max(0, _as_int(tolerances.get("clearance_mm", 0), 0))
        details = {
            "required_min_clearance_mm": required_min,
            "measured_min_clearance_mm": measured_min,
            "tolerance_mm": int(tolerance),
        }
        if required_min is None or measured_min is None:
            grade = "warn"
        elif int(measured_min) + int(tolerance) >= int(required_min):
            grade = "pass"
        else:
            grade = "fail"
    elif check_id == "check.geometry.curvature_limit":
        required_min = _as_number(params.get("min_curvature_radius_mm"))
        measured_row = _as_map(_input_value(input_catalog, "derived.geometry.curvature_summary"))
        measured_min = _as_number(measured_row.get("min_curvature_radius_mm"))
        tolerance = max(0, _as_int(tolerances.get("curvature_radius_mm", 0), 0))
        details = {
            "required_min_curvature_radius_mm": required_min,
            "measured_min_curvature_radius_mm": measured_min,
            "tolerance_mm": int(tolerance),
        }
        if required_min is None or measured_min is None:
            grade = "warn"
        elif int(measured_min) + int(tolerance) >= int(required_min):
            grade = "pass"
        else:
            grade = "fail"
    elif check_id == "check.structure.load_rating_stub":
        required_min = _as_number(params.get("min_load_rating_kg"))
        measured_row = _as_map(_input_value(input_catalog, "derived.structure.load_summary"))
        measured_rating = _as_number(measured_row.get("load_rating_kg"))
        measured_stress = _as_number(measured_row.get("max_stress_ratio_permille"))
        measured_derailment = _as_number(measured_row.get("derailment_risk_permille"))
        details = {
            "required_min_load_rating_kg": required_min,
            "measured_load_rating_kg": measured_rating,
            "measured_max_stress_ratio_permille": measured_stress,
            "stress_limit_permille": 1000,
            "measured_derailment_risk_permille": measured_derailment,
        }
        if required_min is None and measured_rating is None and measured_stress is None:
            grade = "warn"
        elif measured_stress is not None and int(measured_stress) > 1000:
            grade = "fail"
        elif required_min is None:
            grade = "pass" if measured_rating is not None else "warn"
        elif measured_rating is None:
            grade = "warn"
        elif int(measured_rating) >= int(required_min):
            grade = "pass" if measured_stress is None or int(measured_stress) <= 1000 else "fail"
        else:
            grade = "fail"
        if measured_derailment is not None and int(measured_derailment) >= 900 and grade == "pass":
            grade = "warn"
    elif check_id == "check.interface.compatibility":
        required_profile = str(params.get("interface_profile_id", "")).strip()
        measured_row = _as_map(_input_value(input_catalog, "derived.interface.compatibility_summary"))
        measured_profile = str(measured_row.get("interface_profile_id", "")).strip()
        details = {
            "required_interface_profile_id": required_profile or None,
            "measured_interface_profile_id": measured_profile or None,
        }
        if (not required_profile) or (not measured_profile):
            grade = "warn"
        elif required_profile == measured_profile:
            grade = "pass"
        else:
            grade = "fail"
    elif check_id == "check.operation.max_speed_policy":
        required_max = _as_number(params.get("max_speed_kph"))
        measured_row = _as_map(_input_value(input_catalog, "derived.operation.speed_policy_context"))
        measured_max = _as_number(measured_row.get("max_speed_kph"))
        tolerance = max(0, _as_int(tolerances.get("max_speed_kph", 0), 0))
        details = {
            "required_max_speed_kph": required_max,
            "measured_max_speed_kph": measured_max,
            "tolerance_kph": int(tolerance),
        }
        if required_max is None or measured_max is None:
            grade = "warn"
        elif int(measured_max) <= int(required_max) + int(tolerance):
            grade = "pass"
        else:
            grade = "fail"
    else:
        # Generic fallback: missing required inputs downgrades to warn; otherwise use declared grade.
        grade = declared_grade if not missing_inputs else "warn"

    if missing_inputs:
        grade = _best_grade(grade, "warn")
    if declared_grade == "fail" and grade != "pass":
        grade = _best_grade(grade, "fail")
    result = {
        "check_id": check_id,
        "grade": grade,
        "required_inputs": list(required_inputs),
        "missing_inputs": list(sorted(missing_inputs)),
        "details": _canon(details),
        "declared_output_grade": declared_grade,
        "failure_refusal_code": (
            None
            if check_row.get("failure_refusal_code") is None
            else str(check_row.get("failure_refusal_code", "")).strip() or None
        ),
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def evaluate_compliance(
    *,
    spec_row: Mapping[str, object],
    target_kind: str,
    target_id: str,
    tick: int,
    tolerance_policy_rows: Mapping[str, dict],
    compliance_check_rows: Mapping[str, dict],
    input_catalog: Mapping[str, object],
    strict: bool,
) -> Tuple[dict, str | None]:
    payload = dict(spec_row or {})
    spec_id = str(payload.get("spec_id", "")).strip()
    tolerance_policy_id = str(payload.get("tolerance_policy_id", "")).strip()
    tolerance_row = dict(tolerance_policy_rows.get(tolerance_policy_id) or {})
    if not tolerance_row:
        tolerance_row = {
            "tolerance_policy_id": "tol.default",
            "numeric_tolerances": {},
            "rounding_rules": {"default_mode": "nearest_even", "scale": 1},
        }

    check_rows: List[dict] = []
    missing_declared_checks: List[str] = []
    for check_id in _sorted_unique_strings(payload.get("compliance_check_ids")):
        row = dict(compliance_check_rows.get(check_id) or {})
        if not row:
            missing_declared_checks.append(check_id)
            continue
        check_rows.append(row)

    check_results: List[dict] = []
    overall_grade = "pass"
    strict_refusal_code: str | None = None
    for check_row in check_rows:
        result_row = _evaluate_check(
            check_row=check_row,
            spec_row=payload,
            tolerance_row=tolerance_row,
            input_catalog=input_catalog,
        )
        grade = str(result_row.get("grade", "warn")).strip()
        overall_grade = _best_grade(overall_grade, grade)
        if strict and grade == "fail":
            refusal_code = str(result_row.get("failure_refusal_code", "")).strip()
            if refusal_code and strict_refusal_code is None:
                strict_refusal_code = refusal_code
        check_results.append(result_row)

    if missing_declared_checks:
        overall_grade = _best_grade(overall_grade, "fail")
        if strict_refusal_code is None and strict:
            strict_refusal_code = REFUSAL_SPEC_NONCOMPLIANT
        check_results.append(
            {
                "check_id": "check.missing_declared",
                "grade": "fail",
                "required_inputs": [],
                "missing_inputs": [],
                "details": {"missing_check_ids": list(sorted(missing_declared_checks))},
                "declared_output_grade": "fail",
                "failure_refusal_code": REFUSAL_SPEC_NONCOMPLIANT,
                "deterministic_fingerprint": canonical_sha256(
                    {"check_id": "check.missing_declared", "missing_check_ids": list(sorted(missing_declared_checks))}
                ),
            }
        )

    result_seed = {
        "schema_version": "1.0.0",
        "tick": int(max(0, _as_int(tick, 0))),
        "target_kind": str(target_kind).strip(),
        "target_id": str(target_id).strip(),
        "spec_id": spec_id,
        "check_results": list(check_results),
        "overall_grade": overall_grade,
    }
    result_id = "compliance.result.{}".format(canonical_sha256(result_seed)[:16])
    result = {
        "schema_version": "1.0.0",
        "result_id": result_id,
        "tick": int(max(0, _as_int(tick, 0))),
        "target_kind": str(target_kind).strip(),
        "target_id": str(target_id).strip(),
        "spec_id": spec_id,
        "check_results": list(check_results),
        "overall_grade": overall_grade,
        "deterministic_fingerprint": "",
        "extensions": {
            "strict": bool(strict),
            "input_catalog_keys": sorted(str(key).strip() for key in dict(input_catalog or {}).keys() if str(key).strip()),
            "tolerance_policy_id": str(tolerance_row.get("tolerance_policy_id", "")).strip() or None,
        },
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    if strict and overall_grade == "fail" and strict_refusal_code is None:
        strict_refusal_code = REFUSAL_SPEC_NONCOMPLIANT
    return result, strict_refusal_code


__all__ = [
    "REFUSAL_SPEC_NONCOMPLIANT",
    "build_spec_binding",
    "compliance_check_rows_by_id",
    "evaluate_compliance",
    "latest_spec_binding_for_target",
    "load_spec_sheet_rows",
    "normalize_spec_binding_rows",
    "normalize_spec_sheet_rows",
    "spec_sheet_rows_by_id",
    "spec_type_rows_by_id",
    "tolerance_policy_rows_by_id",
]
