"""SYS-1 deterministic validation for interfaces, invariants, and macro model sets."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.system.system_collapse_engine import (
    _as_map,
    interface_signature_rows_by_system,
    normalize_boundary_invariant_rows,
    normalize_system_macro_capsule_rows,
    system_rows_by_id,
)


REFUSAL_SYSTEM_INVALID_INTERFACE = "refusal.system.invalid_interface"
REFUSAL_SYSTEM_INVARIANT_VIOLATION = "refusal.system.invariant_violation"
REFUSAL_SYSTEM_INVALID_MACRO_MODEL_SET = "refusal.system.invalid_macro_model_set"


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


def _bundle_ids(payload: Mapping[str, object] | None) -> List[str]:
    rows = _rows_from_registry_payload(payload, ("quantity_bundles",))
    return _sorted_tokens(str(row.get("bundle_id", "")).strip() for row in rows)


def _spec_type_ids(payload: Mapping[str, object] | None) -> List[str]:
    rows = _rows_from_registry_payload(payload, ("spec_types",))
    return _sorted_tokens(str(row.get("spec_type_id", "")).strip() for row in rows)


def _signal_channel_type_ids(payload: Mapping[str, object] | None) -> List[str]:
    rows = _rows_from_registry_payload(payload, ("signal_channel_types",))
    return _sorted_tokens(str(row.get("channel_type_id", "")).strip() for row in rows)


def _tolerance_policy_ids(payload: Mapping[str, object] | None) -> List[str]:
    rows = _rows_from_registry_payload(payload, ("tolerance_policies",))
    return _sorted_tokens(str(row.get("tolerance_policy_id", "")).strip() for row in rows)


def _constitutive_model_ids(payload: Mapping[str, object] | None) -> List[str]:
    rows = _rows_from_registry_payload(payload, ("constitutive_models",))
    return _sorted_tokens(str(row.get("model_id", "")).strip() for row in rows)


def _macro_model_sets_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(payload, ("macro_model_sets",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows), key=lambda item: str(item.get("macro_model_set_id", ""))):
        set_id = str(row.get("macro_model_set_id", "")).strip()
        if set_id:
            out[set_id] = dict(row)
    return out


def _boundary_templates_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(payload, ("boundary_invariant_templates",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows), key=lambda item: str(item.get("boundary_invariant_template_id", ""))):
        template_id = str(row.get("boundary_invariant_template_id", "")).strip()
        if template_id:
            out[template_id] = dict(row)
    return out


def validate_interface_signature(
    *,
    system_id: str,
    system_rows: object,
    interface_signature_rows: object,
    quantity_bundle_registry_payload: Mapping[str, object] | None,
    spec_type_registry_payload: Mapping[str, object] | None,
    signal_channel_type_registry_payload: Mapping[str, object] | None,
) -> dict:
    checks: List[dict] = []
    system_token = str(system_id or "").strip()
    systems = system_rows_by_id(system_rows)
    interface_by_system = interface_signature_rows_by_system(interface_signature_rows)
    system_row = dict(systems.get(system_token) or {})
    interface_row = dict(interface_by_system.get(system_token) or {})
    checks.append(_check("interface.system.present", bool(system_row), "system row lookup", {"system_id": system_token}))
    checks.append(_check("interface.signature.present", bool(interface_row), "interface signature lookup", {"system_id": system_token}))
    if (not system_row) or (not interface_row):
        return {
            "result": "refused",
            "reason_code": REFUSAL_SYSTEM_INVALID_INTERFACE,
            "system_id": system_token,
            "checks": sorted(checks, key=lambda row: str(row.get("check_id", ""))),
            "deterministic_fingerprint": canonical_sha256({"system_id": system_token, "checks": checks}),
        }

    bundle_ids = set(_bundle_ids(quantity_bundle_registry_payload))
    spec_type_ids = set(_spec_type_ids(spec_type_registry_payload))
    channel_type_ids = set(_signal_channel_type_ids(signal_channel_type_registry_payload))

    spec_compliance_ref = str(interface_row.get("spec_compliance_ref", "")).strip()
    checks.append(_check("interface.spec_compliance_ref.present", bool(spec_compliance_ref), "spec compliance reference presence"))
    checks.append(_check("interface.spec_compliance_ref.registered", spec_compliance_ref in spec_type_ids, "spec compliance reference registration", {"spec_compliance_ref": spec_compliance_ref}))

    spec_limits = _as_map(interface_row.get("spec_limits"))
    for port in sorted((dict(item) for item in list(interface_row.get("port_list") or []) if isinstance(item, Mapping)), key=lambda row: str(row.get("port_id", ""))):
        port_id = str(port.get("port_id", "")).strip() or "missing"
        port_type_id = str(port.get("port_type_id", "")).strip()
        direction = str(port.get("direction", "")).strip().lower()
        allowed_bundle_ids = _sorted_tokens(port.get("allowed_bundle_ids") or [])
        spec_limit_refs = _sorted_tokens(port.get("spec_limit_refs") or [])
        checks.append(_check("interface.port_type.present.{}".format(port_id), bool(port_type_id), "port_type_id present"))
        checks.append(_check("interface.direction.valid.{}".format(port_id), direction in {"in", "out", "bidir"}, "direction valid"))
        checks.append(_check("interface.allowed_bundle_ids.present.{}".format(port_id), bool(allowed_bundle_ids), "allowed_bundle_ids present"))
        checks.append(_check("interface.spec_limit_refs.present.{}".format(port_id), bool(spec_limit_refs), "spec_limit_refs present"))
        for bundle_id in allowed_bundle_ids:
            checks.append(_check("interface.bundle.registered.{}.{}".format(port_id, bundle_id), bundle_id in bundle_ids, "bundle registered"))
        for spec_ref in spec_limit_refs:
            checks.append(_check("interface.spec_ref.valid.{}.{}".format(port_id, spec_ref), (spec_ref in spec_type_ids) or (spec_ref in set(spec_limits.keys())), "spec reference valid"))

    signal_descriptors = [dict(item) for item in list(interface_row.get("signal_descriptors") or []) if isinstance(item, Mapping)]
    checks.append(_check("interface.signal_descriptors.present", bool(signal_descriptors), "signal_descriptors present"))
    for index, signal_row in enumerate(sorted(signal_descriptors, key=lambda row: str(row.get("channel_type_id", "")))):
        channel_type_id = str(signal_row.get("channel_type_id", "")).strip()
        access_policy_id = str(signal_row.get("access_policy_id", "")).strip()
        signal_key = "{}.{}".format(channel_type_id or "missing", index)
        checks.append(_check("interface.signal.channel_type.present.{}".format(signal_key), bool(channel_type_id), "channel_type_id present"))
        checks.append(_check("interface.signal.channel_type.registered.{}".format(signal_key), channel_type_id in channel_type_ids, "channel_type_id registered"))
        checks.append(_check("interface.signal.capacity.present.{}".format(signal_key), "capacity" in signal_row, "capacity present"))
        checks.append(_check("interface.signal.delay.present.{}".format(signal_key), "delay" in signal_row, "delay present"))
        checks.append(_check("interface.signal.access_policy.present.{}".format(signal_key), bool(access_policy_id), "access_policy_id present"))

    checks_sorted = sorted(checks, key=lambda row: str(row.get("check_id", "")))
    failed = [row for row in checks_sorted if str(row.get("status", "")).strip() != "pass"]
    return {
        "result": "complete" if not failed else "refused",
        "reason_code": "" if not failed else REFUSAL_SYSTEM_INVALID_INTERFACE,
        "system_id": system_token,
        "interface_signature_id": str(interface_row.get("interface_signature_id", "")).strip(),
        "checks": checks_sorted,
        "failed_checks": [dict(row) for row in failed],
        "deterministic_fingerprint": canonical_sha256({"system_id": system_token, "checks": checks_sorted}),
    }


def validate_boundary_invariants(
    *,
    system_id: str,
    system_rows: object,
    boundary_invariant_rows: object,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
) -> dict:
    checks: List[dict] = []
    system_token = str(system_id or "").strip()
    systems = system_rows_by_id(system_rows)
    system_row = dict(systems.get(system_token) or {})
    checks.append(_check("invariant.system.present", bool(system_row), "system row lookup", {"system_id": system_token}))
    if not system_row:
        checks_sorted = sorted(checks, key=lambda row: str(row.get("check_id", "")))
        return {
            "result": "refused",
            "reason_code": REFUSAL_SYSTEM_INVARIANT_VIOLATION,
            "system_id": system_token,
            "checks": checks_sorted,
            "deterministic_fingerprint": canonical_sha256({"system_id": system_token, "checks": checks_sorted}),
        }

    tolerance_ids = set(_tolerance_policy_ids(tolerance_policy_registry_payload))
    invariant_by_id = dict(
        (str(row.get("invariant_id", "")).strip(), dict(row))
        for row in normalize_boundary_invariant_rows(boundary_invariant_rows)
        if str(row.get("invariant_id", "")).strip()
    )
    invariant_ids = _sorted_tokens(system_row.get("boundary_invariant_ids") or [])
    checks.append(_check("invariant.ids.present", bool(invariant_ids), "boundary_invariant_ids present"))
    for invariant_id in invariant_ids:
        row = dict(invariant_by_id.get(invariant_id) or {})
        kind = str(row.get("invariant_kind", "")).strip().lower()
        tolerance_policy_id = str(row.get("tolerance_policy_id", "")).strip()
        checks.append(_check("invariant.row.present.{}".format(invariant_id), bool(row), "invariant row present"))
        checks.append(_check("invariant.kind.valid.{}".format(invariant_id), kind in {"mass", "energy", "momentum", "pollution", "safety"}, "invariant kind valid"))
        checks.append(_check("invariant.tolerance.registered.{}".format(invariant_id), tolerance_policy_id in tolerance_ids, "tolerance policy registered"))
        checks.append(_check("invariant.boundary_flux_allowed.typed.{}".format(invariant_id), isinstance(row.get("boundary_flux_allowed"), bool), "boundary_flux_allowed typed bool"))
        checks.append(_check("invariant.ledger_transform_required.typed.{}".format(invariant_id), isinstance(row.get("ledger_transform_required"), bool), "ledger_transform_required typed bool"))
        if kind == "energy":
            checks.append(_check("invariant.energy.requires_ledger.{}".format(invariant_id), bool(row.get("ledger_transform_required", False)), "energy invariants require ledger transform"))

    templates = _boundary_templates_by_id(boundary_invariant_template_registry_payload)
    template_ids = _sorted_tokens(_as_map(system_row.get("extensions")).get("boundary_invariant_template_ids") or [])
    checks.append(_check("invariant.templates.declared", bool(template_ids), "boundary invariant templates declared"))
    required_safety_pattern_ids: List[str] = []
    for template_id in template_ids:
        template_row = dict(templates.get(template_id) or {})
        checks.append(_check("invariant.template.present.{}".format(template_id), bool(template_row), "template present"))
        for required_invariant in _sorted_tokens(template_row.get("required_invariants") or []):
            checks.append(_check("invariant.template.required.{}.{}".format(template_id, required_invariant), required_invariant in set(invariant_ids), "template required invariant present"))
        required_safety_pattern_ids.extend(_sorted_tokens(template_row.get("required_safety_pattern_ids") or []))

    system_ext = _as_map(system_row.get("extensions"))
    safety_pattern_ids = _sorted_tokens(system_ext.get("safety_pattern_ids") or [])
    for pattern_id in _sorted_tokens(required_safety_pattern_ids):
        checks.append(_check("invariant.required_safety_pattern.present.{}".format(pattern_id), pattern_id in set(safety_pattern_ids), "required safety pattern present"))
    if bool(system_ext.get("emits_pollutants", False)):
        has_pollution = False
        for invariant_id in invariant_ids:
            row = dict(invariant_by_id.get(invariant_id) or {})
            if str(row.get("invariant_kind", "")).strip().lower() == "pollution" or invariant_id == "invariant.pollutant_accounted":
                has_pollution = True
                break
        checks.append(_check("invariant.pollution_accounting.required", has_pollution, "pollution accounting invariant required for emitting systems"))

    checks_sorted = sorted(checks, key=lambda row: str(row.get("check_id", "")))
    failed = [row for row in checks_sorted if str(row.get("status", "")).strip() != "pass"]
    return {
        "result": "complete" if not failed else "refused",
        "reason_code": "" if not failed else REFUSAL_SYSTEM_INVARIANT_VIOLATION,
        "system_id": system_token,
        "checks": checks_sorted,
        "failed_checks": [dict(row) for row in failed],
        "deterministic_fingerprint": canonical_sha256({"system_id": system_token, "checks": checks_sorted}),
    }


def validate_macro_model_set(
    *,
    capsule_id: str,
    system_rows: object,
    interface_signature_rows: object,
    system_macro_capsule_rows: object,
    macro_model_set_registry_payload: Mapping[str, object] | None,
    constitutive_model_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
) -> dict:
    checks: List[dict] = []
    capsule_token = str(capsule_id or "").strip()
    capsule_by_id = dict(
        (str(row.get("capsule_id", "")).strip(), dict(row))
        for row in normalize_system_macro_capsule_rows(system_macro_capsule_rows)
        if str(row.get("capsule_id", "")).strip()
    )
    capsule_row = dict(capsule_by_id.get(capsule_token) or {})
    checks.append(_check("macro.capsule.present", bool(capsule_row), "capsule row lookup", {"capsule_id": capsule_token}))
    if not capsule_row:
        checks_sorted = sorted(checks, key=lambda row: str(row.get("check_id", "")))
        return {
            "result": "refused",
            "reason_code": REFUSAL_SYSTEM_INVALID_MACRO_MODEL_SET,
            "capsule_id": capsule_token,
            "checks": checks_sorted,
            "deterministic_fingerprint": canonical_sha256({"capsule_id": capsule_token, "checks": checks_sorted}),
        }

    system_id = str(capsule_row.get("system_id", "")).strip()
    interface_row = dict(interface_signature_rows_by_system(interface_signature_rows).get(system_id) or {})
    checks.append(_check("macro.interface.present", bool(interface_row), "interface for capsule system"))
    macro_model_set_id = str(capsule_row.get("macro_model_set_id", "")).strip() or str(_as_map(capsule_row.get("extensions")).get("macro_model_set_id", "")).strip()
    model_error_bounds_ref = str(capsule_row.get("model_error_bounds_ref", "")).strip() or str(_as_map(capsule_row.get("extensions")).get("model_error_bounds_ref", "")).strip()
    checks.append(_check("macro.model_set_id.present", bool(macro_model_set_id), "macro_model_set_id present"))
    checks.append(_check("macro.error_bounds_ref.present", bool(model_error_bounds_ref), "model_error_bounds_ref present"))

    macro_sets = _macro_model_sets_by_id(macro_model_set_registry_payload)
    macro_set_row = dict(macro_sets.get(macro_model_set_id) or {})
    checks.append(_check("macro.model_set.present", bool(macro_set_row), "macro model set registry lookup"))

    tolerance_ids = set(_tolerance_policy_ids(tolerance_policy_registry_payload))
    checks.append(_check("macro.error_bounds_ref.registered", model_error_bounds_ref in tolerance_ids, "model_error_bounds_ref registry lookup"))
    checks.append(_check("macro.error_bound_policy.present", bool(str(macro_set_row.get("error_bound_policy_id", "")).strip()), "error_bound_policy_id present on macro model set"))
    checks.append(_check("macro.error_bound_policy.registered", str(macro_set_row.get("error_bound_policy_id", "")).strip() in tolerance_ids, "error_bound_policy_id registry lookup"))

    model_ids = set(_constitutive_model_ids(constitutive_model_registry_payload))
    interface_port_ids = set(_sorted_tokens(str(row.get("port_id", "")).strip() for row in list(interface_row.get("port_list") or []) if isinstance(row, Mapping)))
    for binding in sorted((dict(item) for item in list(macro_set_row.get("model_bindings") or []) if isinstance(item, Mapping)), key=lambda row: (str(row.get("model_id", "")), str(row.get("binding_id", "")))):
        binding_id = str(binding.get("binding_id", "")).strip() or str(binding.get("model_id", "")).strip() or "binding"
        model_id = str(binding.get("model_id", "")).strip()
        checks.append(_check("macro.binding.model_id.present.{}".format(binding_id), bool(model_id), "binding model_id present"))
        checks.append(_check("macro.binding.model_id.registered.{}".format(binding_id), model_id in model_ids, "binding model_id registry lookup"))
        for token in _sorted_tokens(binding.get("input_port_ids") or []):
            checks.append(_check("macro.binding.input_port.match.{}.{}".format(binding_id, token), token in interface_port_ids, "binding input port matches interface"))
        for token in _sorted_tokens(binding.get("output_port_ids") or []):
            checks.append(_check("macro.binding.output_port.match.{}.{}".format(binding_id, token), token in interface_port_ids, "binding output port matches interface"))

    checks_sorted = sorted(checks, key=lambda row: str(row.get("check_id", "")))
    failed = [row for row in checks_sorted if str(row.get("status", "")).strip() != "pass"]
    return {
        "result": "complete" if not failed else "refused",
        "reason_code": "" if not failed else REFUSAL_SYSTEM_INVALID_MACRO_MODEL_SET,
        "capsule_id": capsule_token,
        "system_id": system_id,
        "macro_model_set_id": macro_model_set_id,
        "checks": checks_sorted,
        "failed_checks": [dict(row) for row in failed],
        "deterministic_fingerprint": canonical_sha256({"capsule_id": capsule_token, "checks": checks_sorted}),
    }


__all__ = [
    "REFUSAL_SYSTEM_INVALID_INTERFACE",
    "REFUSAL_SYSTEM_INVARIANT_VIOLATION",
    "REFUSAL_SYSTEM_INVALID_MACRO_MODEL_SET",
    "validate_interface_signature",
    "validate_boundary_invariants",
    "validate_macro_model_set",
]
