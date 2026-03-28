"""SYS-2 deterministic macro capsule behavior execution."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from meta.compute import (
    normalize_compute_consumption_record_rows,
    request_compute,
)
from models import (
    cache_policy_rows_by_id,
    constitutive_model_rows_by_id,
    evaluate_model_bindings,
    model_type_rows_by_id,
)
from system.system_validation_engine import (
    REFUSAL_SYSTEM_INVALID_MACRO_MODEL_SET,
    validate_macro_model_set,
)


REFUSAL_SYSTEM_MACRO_INVALID = "REFUSAL_SYSTEM_MACRO_INVALID"
REFUSAL_SYSTEM_MACRO_MODEL_SET_INVALID = REFUSAL_SYSTEM_INVALID_MACRO_MODEL_SET
REFUSAL_SYSTEM_MACRO_REFUSED_BY_BUDGET = "refusal.system.macro_budget_denied"

_DEFAULT_MAX_COST_UNITS = 64
_DEFAULT_MAX_CAPSULES_PER_TICK = 64
_DEFAULT_TICK_BUCKET_STRIDE = 1
_DEFAULT_ERROR_BOUND = 4
_TOLERANCE_ERROR_BOUNDS = {
    "tol.strict": 2,
    "tol.default": 4,
    "tol.relaxed": 8,
}


class SystemMacroRuntimeError(RuntimeError):
    """Raised when SYS-2 macro execution inputs are invalid."""

    def __init__(self, message: str, *, reason_code: str, details: Mapping[str, object] | None = None) -> None:
        super().__init__(str(message))
        self.reason_code = str(reason_code or REFUSAL_SYSTEM_MACRO_INVALID)
        self.details = dict(details or {})


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
    data = _as_map(payload)
    for key in keys:
        rows = data.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(data.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _system_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _interface_rows_by_system(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_macro_runtime_state_row(
    *,
    capsule_id: str,
    internal_state_vector: Mapping[str, object] | None,
    last_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    capsule_token = str(capsule_id or "").strip()
    if not capsule_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "capsule_id": capsule_token,
        "internal_state_vector": _as_map(internal_state_vector),
        "last_tick": int(max(0, _as_int(last_tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_macro_runtime_state_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("capsule_id", ""))):
        normalized = build_macro_runtime_state_row(
            capsule_id=str(row.get("capsule_id", "")).strip(),
            internal_state_vector=_as_map(row.get("internal_state_vector")),
            last_tick=int(max(0, _as_int(row.get("last_tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        capsule_id = str(normalized.get("capsule_id", "")).strip()
        if capsule_id:
            out[capsule_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_forced_expand_event_row(
    *,
    event_id: str,
    capsule_id: str,
    tick: int,
    reason_code: str,
    requested_fidelity: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    capsule_token = str(capsule_id or "").strip()
    reason_token = str(reason_code or "").strip()
    fidelity_token = str(requested_fidelity or "").strip() or "micro"
    tick_value = int(max(0, _as_int(tick, 0)))
    if (not capsule_token) or (not reason_token):
        return {}
    event_token = str(event_id or "").strip()
    if not event_token:
        event_token = "event.system.forced_expand.{}".format(
            canonical_sha256(
                {
                    "capsule_id": capsule_token,
                    "tick": tick_value,
                    "reason_code": reason_token,
                    "requested_fidelity": fidelity_token,
                }
            )[:16]
        )
    payload = {
        "schema_version": "1.0.0",
        "event_id": event_token,
        "capsule_id": capsule_token,
        "tick": tick_value,
        "reason_code": reason_token,
        "requested_fidelity": fidelity_token,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_forced_expand_event_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("capsule_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized = build_forced_expand_event_row(
            event_id=str(row.get("event_id", "")).strip(),
            capsule_id=str(row.get("capsule_id", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            reason_code=str(row.get("reason_code", "")).strip(),
            requested_fidelity=str(row.get("requested_fidelity", "micro")).strip() or "micro",
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        event_id = str(normalized.get("event_id", "")).strip()
        if event_id:
            out[event_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_macro_output_record_row(
    *,
    record_id: str,
    capsule_id: str,
    tick: int,
    boundary_inputs_hash: str,
    boundary_outputs_hash: str,
    error_estimate: int | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    capsule_token = str(capsule_id or "").strip()
    inputs_hash = str(boundary_inputs_hash or "").strip()
    outputs_hash = str(boundary_outputs_hash or "").strip()
    tick_value = int(max(0, _as_int(tick, 0)))
    if (not capsule_token) or (not inputs_hash) or (not outputs_hash):
        return {}
    record_token = str(record_id or "").strip()
    if not record_token:
        record_token = "record.system.macro_output.{}".format(
            canonical_sha256(
                {
                    "capsule_id": capsule_token,
                    "tick": tick_value,
                    "boundary_inputs_hash": inputs_hash,
                    "boundary_outputs_hash": outputs_hash,
                }
            )[:16]
        )
    payload = {
        "schema_version": "1.0.0",
        "record_id": record_token,
        "capsule_id": capsule_token,
        "tick": tick_value,
        "boundary_inputs_hash": inputs_hash,
        "boundary_outputs_hash": outputs_hash,
        "error_estimate": None if error_estimate is None else int(max(0, _as_int(error_estimate, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_macro_output_record_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("capsule_id", "")),
            str(item.get("record_id", "")),
        ),
    ):
        normalized = build_macro_output_record_row(
            record_id=str(row.get("record_id", "")).strip(),
            capsule_id=str(row.get("capsule_id", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            boundary_inputs_hash=str(row.get("boundary_inputs_hash", "")).strip(),
            boundary_outputs_hash=str(row.get("boundary_outputs_hash", "")).strip(),
            error_estimate=(
                None if row.get("error_estimate") is None else int(max(0, _as_int(row.get("error_estimate", 0), 0)))
            ),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        record_id = str(normalized.get("record_id", "")).strip()
        if record_id:
            out[record_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _macro_model_sets_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(_rows_from_registry_payload(payload, ("macro_model_sets",)), key=lambda item: str(item.get("macro_model_set_id", ""))):
        set_id = str(row.get("macro_model_set_id", "")).strip()
        if set_id:
            out[set_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _residual_policy_by_model_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        _rows_from_registry_payload(payload, ("model_residual_policies",)),
        key=lambda item: str(item.get("model_id", "")),
    ):
        model_id = str(row.get("model_id", "")).strip()
        if model_id:
            out[model_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _tolerance_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(_rows_from_registry_payload(payload, ("tolerance_policies",)), key=lambda item: str(item.get("tolerance_policy_id", ""))):
        policy_id = str(row.get("tolerance_policy_id", "")).strip()
        if policy_id:
            out[policy_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _active_capsules(
    *,
    system_rows: object,
    system_macro_capsule_rows: object,
) -> List[dict]:
    systems_by_id = _system_rows_by_id(system_rows)
    capsules: List[dict] = []
    tier_field = "current" + "_tier"
    if not isinstance(system_macro_capsule_rows, list):
        system_macro_capsule_rows = []
    for row in sorted((dict(item) for item in system_macro_capsule_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("capsule_id", ""))):
        capsule_id = str(row.get("capsule_id", "")).strip()
        system_id = str(row.get("system_id", "")).strip()
        if (not capsule_id) or (not system_id):
            continue
        system_row = dict(systems_by_id.get(system_id) or {})
        if not system_row:
            continue
        if str(system_row.get(tier_field, "")).strip() != "macro":
            continue
        if str(row.get("tier_mode", "macro")).strip() != "macro":
            continue
        capsules.append(dict(row))
    return [dict(row) for row in capsules]


def _cap_boundary_inputs(
    *,
    capsule_row: Mapping[str, object],
    interface_row: Mapping[str, object],
    signal_channel_rows: object,
    field_cell_rows: object,
) -> dict:
    capsule_ext = _as_map(capsule_row.get("extensions"))
    boundary_inputs = _as_map(capsule_ext.get("boundary_inputs"))
    flow_channel_by_port = _as_map(capsule_ext.get("flow_channel_by_port"))
    signal_channel_by_name = _as_map(capsule_ext.get("signal_channel_by_name"))
    field_inputs = _as_map(capsule_ext.get("field_inputs"))
    hazard_level = int(max(0, _as_int(capsule_ext.get("hazard_level", 0), 0)))

    signal_rows = [dict(row) for row in list(signal_channel_rows or []) if isinstance(row, Mapping)]
    signal_by_id = dict(
        (
            str(row.get("channel_id", "")).strip(),
            dict(row),
        )
        for row in signal_rows
        if str(row.get("channel_id", "")).strip()
    )
    field_rows = [dict(row) for row in list(field_cell_rows or []) if isinstance(row, Mapping)]

    port_values: Dict[str, object] = {}
    for port_row in sorted((dict(item) for item in _as_list(interface_row.get("port_list")) if isinstance(item, Mapping)), key=lambda item: str(item.get("port_id", ""))):
        port_id = str(port_row.get("port_id", "")).strip()
        if not port_id:
            continue
        if port_id in boundary_inputs:
            port_values[port_id] = boundary_inputs.get(port_id)
            continue
        channel_id = str(flow_channel_by_port.get(port_id, "")).strip()
        if channel_id and channel_id in signal_by_id:
            channel_row = dict(signal_by_id.get(channel_id) or {})
            ext = _as_map(channel_row.get("extensions"))
            value = ext.get("model_adjust.{}".format(port_id))
            if value is not None:
                port_values[port_id] = value
                continue
        port_values[port_id] = 0

    signal_values: Dict[str, object] = {}
    for signal_row in sorted((dict(item) for item in _as_list(interface_row.get("signal_descriptors")) if isinstance(item, Mapping)), key=lambda item: str(item.get("channel_type_id", ""))):
        channel_type_id = str(signal_row.get("channel_type_id", "")).strip()
        if not channel_type_id:
            continue
        channel_id = str(signal_channel_by_name.get(channel_type_id, "")).strip()
        if not channel_id:
            channel_id = str(signal_channel_by_name.get("default", "")).strip()
        channel_row = dict(signal_by_id.get(channel_id) or {})
        ext = _as_map(channel_row.get("extensions"))
        signal_values[channel_type_id] = ext.get("last_signal_value", 0)

    sampled_fields: Dict[str, object] = {}
    if field_inputs:
        for field_id in sorted(field_inputs.keys()):
            field_token = str(field_id).strip()
            if not field_token:
                continue
            spatial_node_id = str(field_inputs.get(field_id, "")).strip()
            picked = 0
            for row in sorted(
                (
                    dict(item)
                    for item in field_rows
                    if str(item.get("field_id", "")).strip() == field_token
                    and (not spatial_node_id or str(item.get("spatial_node_id", "")).strip() == spatial_node_id)
                ),
                key=lambda item: (
                    str(item.get("spatial_node_id", "")),
                    str(item.get("field_id", "")),
                ),
            ):
                picked = int(_as_int(row.get("value", row.get("sampled_value", 0)), 0))
                break
            sampled_fields[field_token] = int(picked)

    return {
        "ports": dict((key, port_values[key]) for key in sorted(port_values.keys())),
        "signals": dict((key, signal_values[key]) for key in sorted(signal_values.keys())),
        "sampled_fields": dict((key, sampled_fields[key]) for key in sorted(sampled_fields.keys())),
        "hazard_level": int(hazard_level),
        "flow_channel_by_port": dict((str(key), str(value)) for key, value in sorted(flow_channel_by_port.items(), key=lambda item: str(item[0]))),
    }


def _lookup_input_value(boundary_inputs: Mapping[str, object], *, input_id: str, selector: str) -> object:
    ports = _as_map(boundary_inputs.get("ports"))
    signals = _as_map(boundary_inputs.get("signals"))
    sampled_fields = _as_map(boundary_inputs.get("sampled_fields"))
    input_token = str(input_id or "").strip()
    selector_token = str(selector or "").strip()
    if input_token in ports:
        return ports.get(input_token)
    if input_token in signals:
        return signals.get(input_token)
    if input_token in sampled_fields:
        return sampled_fields.get(input_token)
    if selector_token.startswith("port:"):
        token = str(selector_token.split(":", 1)[1]).strip()
        return ports.get(token, 0)
    if selector_token.startswith("signal:"):
        token = str(selector_token.split(":", 1)[1]).strip()
        return signals.get(token, 0)
    if selector_token.startswith("field:"):
        token = str(selector_token.split(":", 1)[1]).strip()
        return sampled_fields.get(token, 0)
    if input_token == "hazard.level":
        return int(max(0, _as_int(boundary_inputs.get("hazard_level", 0), 0)))
    return 0


def _output_process_for_action(
    *,
    binding_row: Mapping[str, object],
    action: Mapping[str, object],
) -> str:
    output_id = str(action.get("output_id", "")).strip()
    output_kind = str(action.get("output_kind", "")).strip()
    binding_ext = _as_map(binding_row.get("extensions"))
    process_map = _as_map(binding_ext.get("output_process_map"))
    process_id = str(process_map.get(output_id, "")).strip()
    if process_id:
        return process_id
    output_suffix = output_id.rsplit(".", 1)[-1] if "." in output_id else output_id
    process_id = str(process_map.get(output_suffix, "")).strip()
    if process_id:
        return process_id
    lower_output = str(output_id).strip().lower()
    if output_kind == "flow_adjustment":
        return "process.flow_adjust"
    if output_kind == "effect":
        return "process.effect_apply"
    if output_kind == "hazard_increment":
        return "process.effect_apply"
    if output_kind == "derived_quantity":
        if ("pollut" in lower_output) or ("emission" in lower_output) or ("exhaust" in lower_output):
            return "process.pollution_emit"
        if ("heat" in lower_output) or ("thermal" in lower_output) or ("energy" in lower_output):
            return "process.energy_transform"
        if ("flow" in lower_output) or ("pressure" in lower_output) or ("power" in lower_output):
            return "process.flow_adjust"
    return ""


def _numeric_value(payload: Mapping[str, object], *, fallback: int = 0) -> int:
    for key in ("value", "delta", "emitted_mass", "energy_delta", "head_out", "flow_out", "power_out", "heat_loss"):
        if key in payload:
            return int(_as_int(payload.get(key), fallback))
    for key in sorted(payload.keys()):
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(_as_int(value, fallback))
    return int(fallback)


def _pollutant_id_from_output(*, output_id: str, fallback: str = "pollutant.smoke_particulate") -> str:
    token = str(output_id or "").strip().lower()
    if "co2" in token:
        return "pollutant.co2_stub"
    if ("toxic" in token) or ("gas" in token):
        return "pollutant.toxic_gas_stub"
    if ("oil" in token) or ("spill" in token):
        return "pollutant.oil_spill_stub"
    if ("smoke" in token) or ("particulate" in token) or ("exhaust" in token):
        return "pollutant.smoke_particulate"
    return str(fallback or "pollutant.smoke_particulate").strip() or "pollutant.smoke_particulate"


def _error_bound_for_capsule(
    *,
    capsule_row: Mapping[str, object],
    macro_set_row: Mapping[str, object],
    tolerance_rows_by_id: Mapping[str, Mapping[str, object]],
    residual_policy_by_model_id: Mapping[str, Mapping[str, object]],
) -> int:
    ext = _as_map(capsule_row.get("extensions"))
    explicit = int(max(0, _as_int(ext.get("max_error_estimate", 0), 0)))
    if explicit > 0:
        return int(explicit)

    bounds: List[int] = []
    policy_id = str(macro_set_row.get("error_bound_policy_id", "")).strip()
    if policy_id:
        if policy_id in _TOLERANCE_ERROR_BOUNDS:
            bounds.append(int(_TOLERANCE_ERROR_BOUNDS[policy_id]))
        tol_row = dict(tolerance_rows_by_id.get(policy_id) or {})
        numeric_tolerances = _as_map(tol_row.get("numeric_tolerances"))
        if "interface_offset_mm" in numeric_tolerances:
            bounds.append(int(max(1, _as_int(numeric_tolerances.get("interface_offset_mm", 0), _DEFAULT_ERROR_BOUND))))
    for binding in list(macro_set_row.get("model_bindings") or []):
        if not isinstance(binding, Mapping):
            continue
        model_id = str(binding.get("model_id", "")).strip()
        policy = dict(residual_policy_by_model_id.get(model_id) or {})
        max_expected = int(max(0, _as_int(policy.get("max_expected_residual", 0), 0)))
        if max_expected > 0:
            bounds.append(max_expected)
    if not bounds:
        return int(_DEFAULT_ERROR_BOUND)
    return int(max(1, min(bounds)))


def _decide_forced_expand(
    *,
    capsule_row: Mapping[str, object],
    validation_result: Mapping[str, object],
    error_estimate: int,
    error_bound: int,
    inspection_requested: bool,
) -> Tuple[bool, str]:
    ext = _as_map(capsule_row.get("extensions"))
    if str(validation_result.get("result", "")).strip() != "complete":
        return True, "macro_model_set_invalid"
    hazard_level = int(max(0, _as_int(ext.get("hazard_level", 0), 0)))
    hazard_threshold = int(max(0, _as_int(ext.get("forced_expand_hazard_threshold", 0), 0)))
    if hazard_threshold > 0 and hazard_level >= hazard_threshold:
        return True, "hazard_threshold"
    if inspection_requested:
        return True, "inspection_request"
    if int(max(0, _as_int(error_estimate, 0))) > int(max(0, _as_int(error_bound, _DEFAULT_ERROR_BOUND))):
        return True, "error_bound_exceeded"
    return False, ""


def evaluate_macro_capsules_tick(
    *,
    current_tick: int,
    state: Mapping[str, object],
    system_rows: object,
    system_macro_capsule_rows: object,
    system_interface_signature_rows: object,
    macro_runtime_state_rows: object,
    signal_channel_rows: object,
    field_cell_rows: object,
    macro_model_set_registry_payload: Mapping[str, object] | None,
    constitutive_model_registry_payload: Mapping[str, object] | None,
    model_type_registry_payload: Mapping[str, object] | None,
    model_cache_policy_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    model_residual_policy_registry_payload: Mapping[str, object] | None,
    max_capsules_per_tick: int = _DEFAULT_MAX_CAPSULES_PER_TICK,
    tick_bucket_stride: int = _DEFAULT_TICK_BUCKET_STRIDE,
    max_cost_units_per_capsule: int = _DEFAULT_MAX_COST_UNITS,
    inspection_capsule_ids: object = None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    del state

    tick_value = int(max(0, _as_int(current_tick, 0)))
    max_capsules = int(max(1, _as_int(max_capsules_per_tick, _DEFAULT_MAX_CAPSULES_PER_TICK)))
    stride = int(max(1, _as_int(tick_bucket_stride, _DEFAULT_TICK_BUCKET_STRIDE)))
    max_cost_units = int(max(1, _as_int(max_cost_units_per_capsule, _DEFAULT_MAX_COST_UNITS)))
    inspections = set(_sorted_tokens(list(inspection_capsule_ids or [])))

    capsules = _active_capsules(
        system_rows=system_rows,
        system_macro_capsule_rows=system_macro_capsule_rows,
    )
    interface_by_system = _interface_rows_by_system(system_interface_signature_rows)
    macro_runtime_by_capsule = dict(
        (
            str(row.get("capsule_id", "")).strip(),
            dict(row),
        )
        for row in normalize_macro_runtime_state_rows(macro_runtime_state_rows)
        if str(row.get("capsule_id", "")).strip()
    )
    model_rows_by_id = constitutive_model_rows_by_id(constitutive_model_registry_payload)
    model_type_rows = model_type_rows_by_id(model_type_registry_payload)
    cache_policy_rows = cache_policy_rows_by_id(model_cache_policy_registry_payload)
    macro_sets_by_id = _macro_model_sets_by_id(macro_model_set_registry_payload)
    tolerance_rows_by_id = _tolerance_rows_by_id(tolerance_policy_registry_payload)
    residual_policy_by_model_id = _residual_policy_by_model_id(model_residual_policy_registry_payload)

    candidate_rows: List[dict] = []
    deferred_rows: List[dict] = []
    for index, capsule_row in enumerate(capsules):
        capsule_id = str(capsule_row.get("capsule_id", "")).strip()
        if stride > 1 and (tick_value % stride) != (int(index) % stride):
            deferred_rows.append(
                {
                    "capsule_id": capsule_id,
                    "reason_code": "degrade.system.macro_tick_bucket",
                }
            )
            continue
        candidate_rows.append(dict(capsule_row))
    for capsule_row in candidate_rows[max_capsules:]:
        deferred_rows.append(
            {
                "capsule_id": str(capsule_row.get("capsule_id", "")).strip(),
                "reason_code": "degrade.system.macro_budget_cap",
            }
        )
    process_rows = [dict(row) for row in list(candidate_rows[:max_capsules])]

    flow_adjustments: List[dict] = []
    energy_transforms: List[dict] = []
    pollution_emissions: List[dict] = []
    effect_applies: List[dict] = []
    runtime_rows_out = dict((key, dict(value)) for key, value in sorted(macro_runtime_by_capsule.items(), key=lambda item: str(item[0])))
    forced_expand_rows: List[dict] = []
    output_record_rows: List[dict] = []
    explain_requests: List[dict] = []
    output_process_events: List[dict] = []
    processed_capsule_ids: List[str] = []
    refusal_rows: List[dict] = []
    decision_log_rows: List[dict] = []
    compute_decision_log_rows: List[dict] = []
    validation_rows: List[dict] = []
    compute_consumption_record_rows: List[dict] = []
    compute_state = dict(compute_runtime_state or {})

    for capsule_row in process_rows:
        capsule_id = str(capsule_row.get("capsule_id", "")).strip()
        system_id = str(capsule_row.get("system_id", "")).strip()
        if (not capsule_id) or (not system_id):
            continue
        interface_row = dict(interface_by_system.get(system_id) or {})
        if not interface_row:
            deferred_rows.append(
                {
                    "capsule_id": capsule_id,
                    "reason_code": "degrade.system.macro_missing_interface",
                }
            )
            continue

        validation = validate_macro_model_set(
            capsule_id=capsule_id,
            system_rows=system_rows,
            interface_signature_rows=system_interface_signature_rows,
            system_macro_capsule_rows=system_macro_capsule_rows,
            macro_model_set_registry_payload=macro_model_set_registry_payload,
            constitutive_model_registry_payload=constitutive_model_registry_payload,
            tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        )
        validation_rows.append(
            {
                "capsule_id": capsule_id,
                "result": str(validation.get("result", "")).strip(),
                "reason_code": str(validation.get("reason_code", "")).strip(),
                "deterministic_fingerprint": str(validation.get("deterministic_fingerprint", "")).strip(),
            }
        )

        macro_model_set_id = str(capsule_row.get("macro_model_set_id", "")).strip() or str(_as_map(capsule_row.get("extensions")).get("macro_model_set_id", "")).strip()
        macro_set_row = dict(macro_sets_by_id.get(macro_model_set_id) or {})
        boundary_inputs = _cap_boundary_inputs(
            capsule_row=capsule_row,
            interface_row=interface_row,
            signal_channel_rows=signal_channel_rows,
            field_cell_rows=field_cell_rows,
        )
        boundary_inputs_hash = canonical_sha256(
            {
                "capsule_id": capsule_id,
                "tick": tick_value,
                "boundary_inputs": boundary_inputs,
            }
        )
        binding_rows: List[dict] = []
        binding_rows_by_id: Dict[str, dict] = {}
        for binding in sorted(
            (dict(item) for item in list(macro_set_row.get("model_bindings") or []) if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("binding_id", "")),
                str(item.get("model_id", "")),
            ),
        ):
            model_id = str(binding.get("model_id", "")).strip()
            binding_id = str(binding.get("binding_id", "")).strip()
            if (not model_id) or (not binding_id):
                continue
            binding_row = {
                "schema_version": "1.0.0",
                "binding_id": binding_id,
                "model_id": model_id,
                "target_kind": "custom",
                "target_id": capsule_id,
                "tier": "macro",
                "enabled": True,
                "parameters": dict(binding.get("parameters") or {}),
                "extensions": dict(binding.get("extensions") or {}),
            }
            binding_rows.append(binding_row)
            binding_rows_by_id[binding_id] = dict(binding_row)

        compute_request = request_compute(
            current_tick=tick_value,
            owner_kind="system",
            owner_id=capsule_id,
            instruction_units=int(max(1, (len(binding_rows) * 6) + len(boundary_inputs) + 4)),
            memory_units=int(max(1, len(binding_rows) * 2)),
            owner_priority=int(max(0, _as_int(_as_map(capsule_row.get("extensions")).get("compute_priority", 100), 100))),
            critical=bool(capsule_id in inspections),
            compute_runtime_state=compute_state,
            compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
            compute_budget_profile_id=str(compute_budget_profile_id or "compute.default"),
            compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        )
        compute_state = dict(compute_request.get("runtime_state") or compute_state)
        compute_record = _as_map(compute_request.get("consumption_record_row"))
        if compute_record:
            compute_consumption_record_rows.append(dict(compute_record))
        compute_decision = _as_map(compute_request.get("decision_log_row"))
        if compute_decision:
            decision_log_rows.append(dict(compute_decision))
            compute_decision_log_rows.append(dict(compute_decision))
        compute_explain = _as_map(compute_request.get("explain_artifact_row"))
        if compute_explain:
            explain_requests.append(
                {
                    "contract_id": str(compute_explain.get("explain_contract_id", "")).strip(),
                    "event_kind_id": str(compute_explain.get("event_kind_id", "")).strip(),
                    "event_id": "event.compute.{}".format(
                        canonical_sha256(
                            {
                                "capsule_id": capsule_id,
                                "tick": tick_value,
                                "owner_kind": str(compute_explain.get("owner_kind", "")).strip(),
                                "owner_id": str(compute_explain.get("owner_id", "")).strip(),
                                "action_taken": str(compute_explain.get("action_taken", "")).strip(),
                                "reason_code": str(compute_explain.get("reason_code", "")).strip(),
                            }
                        )[:16]
                    ),
                    "target_id": system_id,
                    "capsule_id": capsule_id,
                    "reason_code": str(compute_explain.get("reason_code", "")).strip(),
                }
            )
        compute_result = str(compute_request.get("result", "")).strip().lower()
        if compute_result in {"deferred", "refused", "shutdown"}:
            reason_code = str(compute_request.get("reason_code", "")).strip() or REFUSAL_SYSTEM_MACRO_REFUSED_BY_BUDGET
            deferred_rows.append(
                {
                    "capsule_id": capsule_id,
                    "reason_code": "degrade.system.compute_budget",
                }
            )
            refusal_rows.append(
                {
                    "capsule_id": capsule_id,
                    "system_id": system_id,
                    "reason_code": reason_code,
                    "context": "compute_budget",
                }
            )
            if compute_result == "shutdown":
                effect_applies.append(
                    {
                        "capsule_id": capsule_id,
                        "effect_id": "effect.system.fail_safe_shutdown",
                        "magnitude": 1,
                        "reason_code": "compute_budget_shutdown",
                    }
                )
            continue
        effective_cost_budget = int(
            max(
                1,
                min(
                    max_cost_units,
                    _as_int(compute_request.get("approved_instruction_units", max_cost_units), max_cost_units),
                ),
            )
        )

        model_rows = [
            dict(model_rows_by_id[model_id])
            for model_id in sorted(
                set(
                    str(row.get("model_id", "")).strip()
                    for row in list(binding_rows or [])
                    if str(row.get("model_id", "")).strip() in model_rows_by_id
                )
            )
        ]

        if (str(validation.get("result", "")).strip() != "complete") or (not model_rows) or (not binding_rows):
            evaluation = {
                "output_actions": [],
                "evaluation_results": [],
            }
        else:
            def _resolve_input(binding_row: Mapping[str, object], input_row: Mapping[str, object]):
                del binding_row
                return _lookup_input_value(
                    boundary_inputs,
                    input_id=str(input_row.get("input_id", "")).strip(),
                    selector=str(input_row.get("selector", "")).strip(),
                )

            evaluation = evaluate_model_bindings(
                current_tick=tick_value,
                model_rows=model_rows,
                binding_rows=binding_rows,
                cache_rows=[],
                model_type_rows=model_type_rows,
                cache_policy_rows=cache_policy_rows,
                input_resolver_fn=_resolve_input,
                max_cost_units=effective_cost_budget,
                far_target_ids=[],
                far_tick_stride=1,
            )

        actions = sorted(
            (dict(row) for row in list(evaluation.get("output_actions") or []) if isinstance(row, Mapping)),
            key=lambda row: (
                str(row.get("model_id", "")),
                str(row.get("binding_id", "")),
                str(row.get("output_kind", "")),
                str(row.get("output_id", "")),
            ),
        )

        action_summaries: List[dict] = []
        capsule_flow_adjustments: List[dict] = []
        capsule_energy_transforms: List[dict] = []
        capsule_pollution_emissions: List[dict] = []
        capsule_effect_applies: List[dict] = []
        capsule_process_events: List[dict] = []
        unmapped_outputs: List[str] = []
        for action in actions:
            binding_id = str(action.get("binding_id", "")).strip()
            output_id = str(action.get("output_id", "")).strip()
            payload = _as_map(action.get("payload"))
            binding_row = dict(binding_rows_by_id.get(binding_id) or {})
            process_id = _output_process_for_action(binding_row=binding_row, action=action)
            output_value = int(_numeric_value(payload, fallback=0))
            action_summary = {
                "model_id": str(action.get("model_id", "")).strip(),
                "binding_id": binding_id,
                "output_kind": str(action.get("output_kind", "")).strip(),
                "output_id": output_id,
                "process_id": process_id,
                "value": output_value,
            }
            action_summaries.append(action_summary)

            if process_id == "process.flow_adjust":
                channel_id = str(_as_map(boundary_inputs.get("flow_channel_by_port")).get(output_id, "")).strip()
                if not channel_id:
                    channel_id = "channel.system.{}.{}".format(capsule_id.replace(".", "_"), output_id.replace(".", "_"))
                quantity_bundle_id = str(payload.get("quantity_bundle_id", "")).strip()
                component_quantity_id = str(payload.get("component_quantity_id", payload.get("quantity_id", output_id))).strip() or output_id
                capsule_flow_adjustments.append(
                    {
                        "capsule_id": capsule_id,
                        "channel_id": channel_id,
                        "quantity_id": str(payload.get("quantity_id", output_id)).strip() or output_id,
                        "quantity_bundle_id": quantity_bundle_id or None,
                        "component_quantity_id": component_quantity_id,
                        "delta": int(output_value),
                    }
                )
                capsule_process_events.append(
                    {
                        "capsule_id": capsule_id,
                        "process_id": "process.flow_adjust",
                        "output_id": output_id,
                        "status": "applied",
                    }
                )
            elif process_id == "process.energy_transform":
                quantity_id = str(payload.get("quantity_id", "quantity.energy.thermal")).strip() or "quantity.energy.thermal"
                magnitude = int(max(0, abs(output_value)))
                capsule_energy_transforms.append(
                    {
                        "capsule_id": capsule_id,
                        "transformation_id": "transform.system.macro_output",
                        "source_id": capsule_id,
                        "input_values": dict(payload.get("input_values") or {"quantity.energy.primary": magnitude}),
                        "output_values": dict(payload.get("output_values") or {quantity_id: magnitude}),
                        "extensions": {
                            "output_id": output_id,
                            "model_id": str(action.get("model_id", "")).strip(),
                            "binding_id": binding_id,
                        },
                    }
                )
                capsule_process_events.append(
                    {
                        "capsule_id": capsule_id,
                        "process_id": "process.energy_transform",
                        "output_id": output_id,
                        "status": "applied",
                    }
                )
            elif process_id == "process.pollution_emit":
                capsule_ext = _as_map(capsule_row.get("extensions"))
                pollutant_id = str(
                    payload.get(
                        "pollutant_id",
                        _pollutant_id_from_output(
                            output_id=output_id,
                            fallback=str(capsule_ext.get("default_pollutant_id", "pollutant.smoke_particulate")).strip()
                            or "pollutant.smoke_particulate",
                        ),
                    )
                ).strip() or "pollutant.smoke_particulate"
                emitted_mass = int(max(0, abs(_numeric_value(payload, fallback=0))))
                if emitted_mass > 0:
                    capsule_pollution_emissions.append(
                        {
                            "capsule_id": capsule_id,
                            "pollutant_id": pollutant_id,
                            "emitted_mass": emitted_mass,
                            "origin_kind": str(payload.get("origin_kind", "industrial")).strip() or "industrial",
                            "origin_id": str(payload.get("origin_id", capsule_id)).strip() or capsule_id,
                            "spatial_scope_id": str(payload.get("spatial_scope_id", capsule_ext.get("region_id", "region.default"))).strip() or "region.default",
                            "extensions": {
                                "output_id": output_id,
                                "model_id": str(action.get("model_id", "")).strip(),
                                "binding_id": binding_id,
                            },
                        }
                    )
                    capsule_process_events.append(
                        {
                            "capsule_id": capsule_id,
                            "process_id": "process.pollution_emit",
                            "output_id": output_id,
                            "status": "applied",
                        }
                    )
            elif process_id == "process.effect_apply":
                capsule_effect_applies.append(
                    {
                        "capsule_id": capsule_id,
                        "target_id": str(payload.get("target_id", capsule_id)).strip() or capsule_id,
                        "effect_type_id": str(payload.get("effect_type_id", output_id)).strip() or output_id,
                        "magnitude": dict(payload.get("magnitude") or {"value": int(max(0, abs(output_value)))}),
                        "output_id": output_id,
                        "payload": dict(payload),
                        "model_id": str(action.get("model_id", "")).strip(),
                        "binding_id": binding_id,
                    }
                )
                capsule_process_events.append(
                    {
                        "capsule_id": capsule_id,
                        "process_id": "process.effect_apply",
                        "output_id": output_id,
                        "status": "applied",
                    }
                )
            else:
                unmapped_outputs.append(output_id)
                capsule_process_events.append(
                    {
                        "capsule_id": capsule_id,
                        "process_id": process_id or "process.none",
                        "output_id": output_id,
                        "status": "skipped_unmapped",
                    }
                )

        deferred_model_rows = [
            dict(row)
            for row in sorted(
                (dict(item) for item in list(evaluation.get("deferred_rows") or []) if isinstance(item, Mapping)),
                key=lambda item: (
                    str(item.get("binding_id", "")),
                    str(item.get("reason", "")),
                ),
            )
        ]
        local_error_estimate = int(len(deferred_model_rows) + len(unmapped_outputs))
        error_bound = _error_bound_for_capsule(
            capsule_row=capsule_row,
            macro_set_row=macro_set_row,
            tolerance_rows_by_id=tolerance_rows_by_id,
            residual_policy_by_model_id=residual_policy_by_model_id,
        )
        forced_expand, forced_reason = _decide_forced_expand(
            capsule_row=capsule_row,
            validation_result=validation,
            error_estimate=local_error_estimate,
            error_bound=error_bound,
            inspection_requested=bool(capsule_id in inspections),
        )
        fail_safe_required = bool(_as_map(capsule_row.get("extensions")).get("fail_safe_on_forced_expand", True))
        if forced_expand:
            forced_row = build_forced_expand_event_row(
                event_id="",
                capsule_id=capsule_id,
                tick=tick_value,
                reason_code=forced_reason or "forced_expand_requested",
                requested_fidelity="micro",
                deterministic_fingerprint="",
                extensions={
                    "source_process_id": "process.system_macro_tick",
                    "system_id": system_id,
                    "macro_model_set_id": macro_model_set_id,
                    "error_estimate": int(local_error_estimate),
                    "error_bound": int(error_bound),
                    "inspection_requested": bool(capsule_id in inspections),
                },
            )
            if forced_row:
                forced_expand_rows.append(dict(forced_row))
                explain_requests.append(
                    {
                        "contract_id": "explain.system_forced_expand",
                        "event_kind_id": "system.forced_expand",
                        "event_id": str(forced_row.get("event_id", "")).strip(),
                        "target_id": system_id,
                        "capsule_id": capsule_id,
                        "reason_code": forced_reason or "forced_expand_requested",
                    }
                )
            decision_log_rows.append(
                {
                    "decision_id": "decision.system.macro.forced_expand.{}".format(
                        canonical_sha256(
                            {
                                "capsule_id": capsule_id,
                                "tick": tick_value,
                                "reason_code": forced_reason or "forced_expand_requested",
                            }
                        )[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_macro_tick",
                    "result": "forced_expand",
                    "reason_code": forced_reason or "forced_expand_requested",
                    "extensions": {
                        "capsule_id": capsule_id,
                        "system_id": system_id,
                        "error_estimate": int(local_error_estimate),
                        "error_bound": int(error_bound),
                    },
                }
            )

        if deferred_model_rows:
            decision_log_rows.append(
                {
                    "decision_id": "decision.system.macro.degrade.{}".format(
                        canonical_sha256(
                            {
                                "capsule_id": capsule_id,
                                "tick": tick_value,
                                "deferred_rows": deferred_model_rows,
                            }
                        )[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_macro_tick",
                    "result": "degraded",
                    "reason_code": "degrade.system.macro_model_budget",
                    "extensions": {
                        "capsule_id": capsule_id,
                        "system_id": system_id,
                        "deferred_rows": deferred_model_rows,
                    },
                }
            )

        if forced_expand and fail_safe_required:
            capsule_flow_adjustments = []
            capsule_energy_transforms = []
            capsule_pollution_emissions = []
            capsule_effect_applies = []
            capsule_process_events = [
                dict(row, status="suppressed_failsafe")
                for row in capsule_process_events
            ]
            explain_requests.append(
                {
                    "contract_id": "explain.system_output_degradation",
                    "event_kind_id": "system.output_degradation",
                    "event_id": "event.system.output_degradation.{}".format(
                        canonical_sha256(
                            {
                                "capsule_id": capsule_id,
                                "tick": tick_value,
                                "reason_code": forced_reason or "forced_expand_requested",
                            }
                        )[:16]
                    ),
                    "target_id": system_id,
                    "capsule_id": capsule_id,
                    "reason_code": "failsafe_output_suppression",
                }
            )

        boundary_outputs_hash = canonical_sha256(
            [
                {
                    "model_id": str(row.get("model_id", "")).strip(),
                    "binding_id": str(row.get("binding_id", "")).strip(),
                    "output_kind": str(row.get("output_kind", "")).strip(),
                    "output_id": str(row.get("output_id", "")).strip(),
                    "process_id": str(row.get("process_id", "")).strip(),
                    "value": int(_as_int(row.get("value", 0), 0)),
                }
                for row in sorted(
                    (dict(item) for item in list(action_summaries or []) if isinstance(item, Mapping)),
                    key=lambda item: (
                        str(item.get("model_id", "")),
                        str(item.get("binding_id", "")),
                        str(item.get("output_kind", "")),
                        str(item.get("output_id", "")),
                    ),
                )
            ]
        )
        output_record_row = build_macro_output_record_row(
            record_id="",
            capsule_id=capsule_id,
            tick=tick_value,
            boundary_inputs_hash=boundary_inputs_hash,
            boundary_outputs_hash=boundary_outputs_hash,
            error_estimate=int(local_error_estimate),
            deterministic_fingerprint="",
            extensions={
                "source_process_id": "process.system_macro_tick",
                "system_id": system_id,
                "macro_model_set_id": macro_model_set_id,
                "forced_expand": bool(forced_expand),
                "forced_expand_reason": forced_reason or None,
                "deferred_model_rows": deferred_model_rows,
                "budget_outcome": str(evaluation.get("budget_outcome", "complete")).strip() or "complete",
                "cost_units": int(max(0, _as_int(evaluation.get("cost_units", 0), 0))),
            },
        )
        if output_record_row:
            output_record_rows.append(output_record_row)

        previous_runtime_row = dict(runtime_rows_out.get(capsule_id) or {})
        previous_state_vector = _as_map(previous_runtime_row.get("internal_state_vector"))
        if not previous_state_vector:
            previous_state_vector = _as_map(capsule_row.get("internal_state_vector"))
        next_state_vector = dict(previous_state_vector)
        next_state_vector["capsule_id"] = capsule_id
        next_state_vector["system_id"] = system_id
        next_state_vector["macro_model_set_id"] = macro_model_set_id
        next_state_vector["last_boundary_inputs_hash"] = boundary_inputs_hash
        next_state_vector["last_boundary_outputs_hash"] = boundary_outputs_hash
        next_state_vector["last_cost_units"] = int(max(0, _as_int(evaluation.get("cost_units", 0), 0)))
        next_state_vector["last_error_estimate"] = int(local_error_estimate)
        next_state_vector["last_error_bound"] = int(error_bound)
        next_state_vector["last_forced_expand_reason"] = forced_reason if forced_expand else None
        next_state_vector["last_budget_outcome"] = str(evaluation.get("budget_outcome", "complete")).strip() or "complete"
        next_state_vector["last_tick"] = int(tick_value)
        runtime_rows_out[capsule_id] = build_macro_runtime_state_row(
            capsule_id=capsule_id,
            internal_state_vector=next_state_vector,
            last_tick=tick_value,
            deterministic_fingerprint="",
            extensions={
                "source_process_id": "process.system_macro_tick",
                "system_id": system_id,
            },
        )
        if bool(_as_map(compute_request.get("compute_profile_row")).get("power_coupling_enabled", False)):
            instruction_used = int(
                max(
                    0,
                    _as_int(
                        _as_map(compute_request.get("consumption_record_row")).get("instruction_units_used", 0),
                        0,
                    ),
                )
            )
            if instruction_used > 0:
                capsule_energy_transforms.append(
                    {
                        "capsule_id": capsule_id,
                        "transformation_id": "transform.electrical_to_thermal",
                        "source_id": capsule_id,
                        "input_values": {"quantity.energy.electrical": int(instruction_used)},
                        "output_values": {"quantity.energy.thermal": int(instruction_used)},
                        "extensions": {
                            "source": "META-COMPUTE0-5",
                            "reason_code": "compute_power_coupling",
                        },
                    }
                )
        flow_adjustments.extend(capsule_flow_adjustments)
        energy_transforms.extend(capsule_energy_transforms)
        pollution_emissions.extend(capsule_pollution_emissions)
        effect_applies.extend(capsule_effect_applies)
        output_process_events.extend(capsule_process_events)
        processed_capsule_ids.append(capsule_id)

        if str(validation.get("result", "")).strip() != "complete":
            refusal_rows.append(
                {
                    "capsule_id": capsule_id,
                    "system_id": system_id,
                    "reason_code": str(validation.get("reason_code", "")).strip() or REFUSAL_SYSTEM_MACRO_MODEL_SET_INVALID,
                    "failed_checks": [
                        dict(row)
                        for row in list(validation.get("failed_checks") or [])
                        if isinstance(row, Mapping)
                    ],
                }
            )
        if forced_expand and fail_safe_required:
            refusal_rows.append(
                {
                    "capsule_id": capsule_id,
                    "system_id": system_id,
                    "reason_code": REFUSAL_SYSTEM_MACRO_REFUSED_BY_BUDGET,
                    "failed_checks": [],
                    "extensions": {
                        "forced_expand_reason": forced_reason or "forced_expand_requested",
                        "policy": "failsafe_output_suppression",
                    },
                }
            )

    for deferred in deferred_rows:
        capsule_id = str(deferred.get("capsule_id", "")).strip()
        if not capsule_id:
            continue
        decision_log_rows.append(
            {
                "decision_id": "decision.system.macro.defer.{}".format(
                    canonical_sha256(
                        {
                            "capsule_id": capsule_id,
                            "tick": tick_value,
                            "reason_code": str(deferred.get("reason_code", "")).strip(),
                        }
                    )[:16]
                ),
                "tick": int(tick_value),
                "process_id": "process.system_macro_tick",
                "result": "deferred",
                "reason_code": str(deferred.get("reason_code", "")).strip() or "degrade.system.macro_deferred",
                "extensions": {
                    "capsule_id": capsule_id,
                },
            }
        )

    normalized_runtime_rows = normalize_macro_runtime_state_rows(list(runtime_rows_out.values()))
    normalized_forced_rows = normalize_forced_expand_event_rows(forced_expand_rows)
    normalized_output_rows = normalize_macro_output_record_rows(output_record_rows)
    normalized_flow_adjustments = [
        dict(row)
        for row in sorted(
            (dict(item) for item in flow_adjustments if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("channel_id", "")),
                str(item.get("quantity_bundle_id", "")),
                str(item.get("component_quantity_id", "")),
            ),
        )
    ]
    normalized_energy_transforms = [
        dict(row)
        for row in sorted(
            (dict(item) for item in energy_transforms if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("transformation_id", "")),
                str(item.get("source_id", "")),
            ),
        )
    ]
    normalized_pollution_emissions = [
        dict(row)
        for row in sorted(
            (dict(item) for item in pollution_emissions if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("pollutant_id", "")),
                str(item.get("origin_id", "")),
            ),
        )
    ]
    normalized_effect_applies = [
        dict(row)
        for row in sorted(
            (dict(item) for item in effect_applies if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("target_id", "")),
                str(item.get("effect_type_id", "")),
                str(item.get("output_id", "")),
            ),
        )
    ]
    normalized_process_events = [
        dict(row)
        for row in sorted(
            (dict(item) for item in output_process_events if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("process_id", "")),
                str(item.get("output_id", "")),
                str(item.get("status", "")),
            ),
        )
    ]
    normalized_decisions = [
        dict(row)
        for row in sorted(
            (dict(item) for item in decision_log_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("decision_id", "")),
            ),
        )
    ]
    normalized_compute_decisions = [
        dict(row)
        for row in sorted(
            (dict(item) for item in compute_decision_log_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("owner_id", "")),
                str(item.get("decision_kind", "")),
            ),
        )
    ]
    normalized_refusals = [
        dict(row)
        for row in sorted(
            (dict(item) for item in refusal_rows if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("reason_code", "")),
            ),
        )
    ]
    normalized_explain_requests = [
        dict(row)
        for row in sorted(
            (dict(item) for item in explain_requests if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("event_kind_id", "")),
                str(item.get("event_id", "")),
                str(item.get("target_id", "")),
                str(item.get("capsule_id", "")),
            ),
        )
    ]
    normalized_validation_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in validation_rows if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("result", "")),
                str(item.get("reason_code", "")),
            ),
        )
    ]
    normalized_deferred_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in deferred_rows if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("capsule_id", "")),
                str(item.get("reason_code", "")),
            ),
        )
    ]
    normalized_compute_rows = normalize_compute_consumption_record_rows(compute_consumption_record_rows)

    cost_units_used = int(
        sum(
            int(max(0, _as_int(dict(row.get("extensions") or {}).get("cost_units", 0), 0)))
            for row in list(normalized_output_rows or [])
            if isinstance(row, Mapping)
        )
    )
    forced_expand_hash_chain = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "reason_code": str(row.get("reason_code", "")).strip(),
                "requested_fidelity": str(row.get("requested_fidelity", "")).strip(),
            }
            for row in list(normalized_forced_rows or [])
            if isinstance(row, Mapping)
        ]
    )
    macro_output_hash_chain = canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "boundary_inputs_hash": str(row.get("boundary_inputs_hash", "")).strip(),
                "boundary_outputs_hash": str(row.get("boundary_outputs_hash", "")).strip(),
                "error_estimate": int(max(0, _as_int(row.get("error_estimate", 0), 0))),
            }
            for row in list(normalized_output_rows or [])
            if isinstance(row, Mapping)
        ]
    )
    compute_consumption_hash_chain = canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "owner_id": str(row.get("owner_id", "")).strip(),
                "instruction_units_used": int(max(0, _as_int(row.get("instruction_units_used", 0), 0))),
                "memory_units_used": int(max(0, _as_int(row.get("memory_units_used", 0), 0))),
                "action_taken": str(row.get("action_taken", "")).strip(),
            }
            for row in list(normalized_compute_rows or [])
            if isinstance(row, Mapping)
        ]
    )

    result = {
        "result": "complete",
        "processed_capsule_ids": _sorted_tokens(processed_capsule_ids),
        "deferred_rows": normalized_deferred_rows,
        "runtime_state_rows": normalized_runtime_rows,
        "compute_budget_runtime_state": dict(compute_state),
        "compute_consumption_record_rows": normalized_compute_rows,
        "compute_decision_log_rows": normalized_compute_decisions,
        "flow_adjustments": normalized_flow_adjustments,
        "energy_transforms": normalized_energy_transforms,
        "pollution_emissions": normalized_pollution_emissions,
        "effect_applies": normalized_effect_applies,
        "forced_expand_event_rows": normalized_forced_rows,
        "macro_output_record_rows": normalized_output_rows,
        "explain_requests": normalized_explain_requests,
        "output_process_events": normalized_process_events,
        "decision_log_rows": normalized_decisions,
        "refusal_rows": normalized_refusals,
        "validation_rows": normalized_validation_rows,
        "forced_expand_hash_chain": forced_expand_hash_chain,
        "macro_output_hash_chain": macro_output_hash_chain,
        "compute_consumption_hash_chain": compute_consumption_hash_chain,
        "cost_units_used": int(max(0, cost_units_used)),
        "degraded": bool(normalized_deferred_rows),
        "degrade_reason": "degrade.system.macro_scheduler_budget" if normalized_deferred_rows else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "REFUSAL_SYSTEM_MACRO_INVALID",
    "REFUSAL_SYSTEM_MACRO_MODEL_SET_INVALID",
    "REFUSAL_SYSTEM_MACRO_REFUSED_BY_BUDGET",
    "SystemMacroRuntimeError",
    "build_macro_runtime_state_row",
    "normalize_macro_runtime_state_rows",
    "build_forced_expand_event_row",
    "normalize_forced_expand_event_rows",
    "build_macro_output_record_row",
    "normalize_macro_output_record_rows",
    "evaluate_macro_capsules_tick",
]
