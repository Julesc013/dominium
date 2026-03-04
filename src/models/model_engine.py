"""Deterministic META-MODEL-1 constitutive model helpers."""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MODEL_INVALID = "refusal.model.invalid"
REFUSAL_MODEL_BINDING_INVALID = "refusal.model.binding_invalid"
REFUSAL_MODEL_CACHE_POLICY_INVALID = "refusal.model.cache_policy_invalid"

_VALID_TIERS = {"macro", "meso", "micro"}
_TIER_RANK = {"macro": 0, "meso": 1, "micro": 2}
_VALID_INPUT_KINDS = {
    "field",
    "flow_quantity",
    "hazard",
    "state_machine",
    "spec_param",
    "material_property",
    "derived",
}
_VALID_OUTPUT_KINDS = {
    "effect",
    "hazard_increment",
    "flow_adjustment",
    "derived_quantity",
    "compliance_signal",
}
_VALID_TARGET_KINDS = {"node", "edge", "vehicle", "structure", "volume", "channel", "custom"}
_VALID_CACHE_MODES = {"none", "by_inputs_hash"}


class ModelEngineError(ValueError):
    """Deterministic model evaluation refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_MODEL_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _tier(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in _VALID_TIERS:
        return token
    return "macro"


def normalize_input_ref(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    input_kind = str(payload.get("input_kind", "")).strip()
    input_id = str(payload.get("input_id", "")).strip()
    if input_kind not in _VALID_INPUT_KINDS or not input_id:
        raise ModelEngineError(
            REFUSAL_MODEL_INVALID,
            "input_ref requires valid input_kind and input_id",
            {"input_kind": input_kind, "input_id": input_id},
        )
    selector = payload.get("selector")
    return {
        "schema_version": "1.0.0",
        "input_kind": input_kind,
        "input_id": input_id,
        "selector": None if selector is None else str(selector).strip() or None,
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }


def normalize_output_ref(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    output_kind = str(payload.get("output_kind", "")).strip()
    output_id = str(payload.get("output_id", "")).strip()
    if output_kind not in _VALID_OUTPUT_KINDS or not output_id:
        raise ModelEngineError(
            REFUSAL_MODEL_INVALID,
            "output_ref requires valid output_kind and output_id",
            {"output_kind": output_kind, "output_id": output_id},
        )
    return {
        "schema_version": "1.0.0",
        "output_kind": output_kind,
        "output_id": output_id,
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }


def _normalize_model_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    model_id = str(payload.get("model_id", "")).strip()
    model_type_id = str(payload.get("model_type_id", "")).strip()
    cache_policy_id = str(payload.get("cache_policy_id", "")).strip()
    if (not model_id) or (not model_type_id) or (not cache_policy_id):
        raise ModelEngineError(
            REFUSAL_MODEL_INVALID,
            "model requires model_id, model_type_id, and cache_policy_id",
            {
                "model_id": model_id,
                "model_type_id": model_type_id,
                "cache_policy_id": cache_policy_id,
            },
        )
    input_signature = [
        normalize_input_ref(item)
        for item in sorted(
            (dict(item) for item in list(payload.get("input_signature") or []) if isinstance(item, Mapping)),
            key=lambda item: (str(item.get("input_kind", "")), str(item.get("input_id", "")), str(item.get("selector", ""))),
        )
    ]
    output_signature = [
        normalize_output_ref(item)
        for item in sorted(
            (dict(item) for item in list(payload.get("output_signature") or []) if isinstance(item, Mapping)),
            key=lambda item: (str(item.get("output_kind", "")), str(item.get("output_id", ""))),
        )
    ]
    if not output_signature:
        raise ModelEngineError(REFUSAL_MODEL_INVALID, "model '{}' has empty output signature".format(model_id), {"model_id": model_id})
    uses_rng_stream = bool(payload.get("uses_rng_stream", False))
    rng_stream_name = str(payload.get("rng_stream_name", "")).strip() or None
    if uses_rng_stream and not rng_stream_name:
        raise ModelEngineError(
            REFUSAL_MODEL_INVALID,
            "model '{}' uses RNG but has no rng_stream_name".format(model_id),
            {"model_id": model_id},
        )
    out = {
        "schema_version": "1.0.0",
        "model_id": model_id,
        "model_type_id": model_type_id,
        "description": str(payload.get("description", "")).strip(),
        "supported_tiers": sorted(set(_tier(item) for item in list(payload.get("supported_tiers") or []))),
        "input_signature": input_signature,
        "output_signature": output_signature,
        "cost_units": int(max(0, _as_int(payload.get("cost_units", 0), 0))),
        "cache_policy_id": cache_policy_id,
        "uses_rng_stream": bool(uses_rng_stream),
        "rng_stream_name": rng_stream_name,
        "version_introduced": str(payload.get("version_introduced", "1.0.0")).strip() or "1.0.0",
        "deprecated": bool(payload.get("deprecated", False)),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    if not out["supported_tiers"]:
        out["supported_tiers"] = ["macro"]
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def normalize_constitutive_model_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("model_id", ""))):
        model_id = str(row.get("model_id", "")).strip()
        if not model_id:
            continue
        try:
            out[model_id] = _normalize_model_row(row)
        except ModelEngineError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def constitutive_model_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("models")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("models")
    if not isinstance(rows, list):
        rows = []
    return dict((str(row.get("model_id", "")).strip(), dict(row)) for row in normalize_constitutive_model_rows(rows))


def model_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("model_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("model_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("model_type_id", ""))):
        model_type_id = str(row.get("model_type_id", "")).strip()
        if not model_type_id:
            continue
        out[model_type_id] = {
            "schema_version": "1.0.0",
            "model_type_id": model_type_id,
            "description": str(row.get("description", "")).strip(),
            "parameter_schema_id": str(row.get("parameter_schema_id", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def cache_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("cache_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("cache_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("cache_policy_id", ""))):
        cache_policy_id = str(row.get("cache_policy_id", "")).strip()
        if not cache_policy_id:
            continue
        mode = str(row.get("mode", "none")).strip().lower() or "none"
        if mode not in _VALID_CACHE_MODES:
            raise ModelEngineError(
                REFUSAL_MODEL_CACHE_POLICY_INVALID,
                "cache policy '{}' has invalid mode '{}'".format(cache_policy_id, mode),
                {"cache_policy_id": cache_policy_id, "mode": mode},
            )
        out[cache_policy_id] = {
            "schema_version": "1.0.0",
            "cache_policy_id": cache_policy_id,
            "mode": mode,
            "ttl_ticks": None if row.get("ttl_ticks") is None else int(max(0, _as_int(row.get("ttl_ticks", 0), 0))),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _normalize_binding_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    binding_id = str(payload.get("binding_id", "")).strip()
    model_id = str(payload.get("model_id", "")).strip()
    target_id = str(payload.get("target_id", "")).strip()
    target_kind = str(payload.get("target_kind", "custom")).strip().lower() or "custom"
    if target_kind not in _VALID_TARGET_KINDS:
        target_kind = "custom"
    if (not binding_id) or (not model_id) or (not target_id):
        raise ModelEngineError(
            REFUSAL_MODEL_BINDING_INVALID,
            "model binding requires binding_id, model_id, and target_id",
            {"binding_id": binding_id, "model_id": model_id, "target_id": target_id},
        )
    out = {
        "schema_version": "1.0.0",
        "binding_id": binding_id,
        "model_id": model_id,
        "target_kind": target_kind,
        "target_id": target_id,
        "tier": _tier(payload.get("tier")),
        "parameters": _canon(_as_map(payload.get("parameters"))),
        "enabled": bool(payload.get("enabled", True)),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def normalize_model_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("binding_id", ""))):
        binding_id = str(row.get("binding_id", "")).strip()
        if not binding_id:
            continue
        try:
            out[binding_id] = _normalize_binding_row(row)
        except ModelEngineError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_model_evaluation_result_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("result_id", "")))):
        model_id = str(row.get("model_id", "")).strip()
        binding_id = str(row.get("binding_id", "")).strip()
        inputs_hash = str(row.get("inputs_hash", "")).strip()
        outputs_hash = str(row.get("outputs_hash", "")).strip()
        if (not model_id) or (not binding_id) or (not inputs_hash) or (not outputs_hash):
            continue
        result_id = str(row.get("result_id", "")).strip()
        if not result_id:
            result_id = "model.eval.{}".format(
                canonical_sha256(
                    {
                        "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                        "model_id": model_id,
                        "binding_id": binding_id,
                        "inputs_hash": inputs_hash,
                    }
                )[:16]
            )
        payload = {
            "schema_version": "1.0.0",
            "result_id": result_id,
            "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            "model_id": model_id,
            "binding_id": binding_id,
            "inputs_hash": inputs_hash,
            "outputs_hash": outputs_hash,
            "derived_observation_artifact_id": (
                None
                if row.get("derived_observation_artifact_id") is None
                else str(row.get("derived_observation_artifact_id", "")).strip() or None
            ),
            "deterministic_fingerprint": "",
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[result_id] = payload
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (_as_int(out[key].get("tick", 0), 0), key))]


def _normalize_cache_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[Tuple[str, str, str, str], dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: (str(item.get("model_id", "")), str(item.get("binding_id", "")), str(item.get("tier", "")), str(item.get("inputs_hash", "")))):
        model_id = str(row.get("model_id", "")).strip()
        binding_id = str(row.get("binding_id", "")).strip()
        tier = _tier(row.get("tier"))
        inputs_hash = str(row.get("inputs_hash", "")).strip()
        outputs_hash = str(row.get("outputs_hash", "")).strip()
        if (not model_id) or (not binding_id) or (not inputs_hash) or (not outputs_hash):
            continue
        key = (model_id, binding_id, tier, inputs_hash)
        out[key] = {
            "model_id": model_id,
            "binding_id": binding_id,
            "tier": tier,
            "inputs_hash": inputs_hash,
            "outputs_hash": outputs_hash,
            "outputs": [_canon(item) for item in list(row.get("outputs") or [])],
            "computed_tick": int(max(0, _as_int(row.get("computed_tick", 0), 0))),
            "expires_tick": None if row.get("expires_tick") is None else int(max(0, _as_int(row.get("expires_tick", 0), 0))),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return [dict(out[key]) for key in sorted(out.keys())]


def _rng_permille(*, stream_name: str, inputs_hash: str, tick: int) -> int:
    digest = canonical_sha256({"stream_name": stream_name, "inputs_hash": inputs_hash, "tick": int(max(0, _as_int(tick, 0)))})
    return int(int(digest[:8], 16) % 1000)


def _resolved_input_int(
    *,
    resolved_inputs: List[dict],
    input_id: str,
    default_value: int = 0,
) -> int:
    token = str(input_id or "").strip()
    for row in list(resolved_inputs or []):
        if str(row.get("input_id", "")).strip() != token:
            continue
        return int(_as_int(row.get("value"), default_value))
    return int(default_value)


def _binding_param_int(*, binding: Mapping[str, object], key: str, default_value: int = 0) -> int:
    params = _as_map(binding.get("parameters"))
    if key not in params:
        return int(default_value)
    return int(_as_int(params.get(key), default_value))


def _resolved_input_vector3(
    *,
    resolved_inputs: List[dict],
    input_id: str,
) -> dict:
    token = str(input_id or "").strip()
    for row in list(resolved_inputs or []):
        if str(row.get("input_id", "")).strip() != token:
            continue
        value = row.get("value")
        payload = _as_map(value)
        return {
            "x": int(_as_int(payload.get("x", 0), 0)),
            "y": int(_as_int(payload.get("y", 0), 0)),
            "z": int(_as_int(payload.get("z", 0), 0)),
        }
    return {"x": 0, "y": 0, "z": 0}


def _resolved_input_any(
    *,
    resolved_inputs: List[dict],
    input_id: str,
) -> object:
    token = str(input_id or "").strip()
    for row in list(resolved_inputs or []):
        if str(row.get("input_id", "")).strip() != token:
            continue
        return row.get("value")
    return None


def evaluate_time_mapping_model(
    *,
    model_row: Mapping[str, object],
    canonical_tick: int,
    scope_id: str,
    parameters: Mapping[str, object] | None = None,
    input_values: Mapping[str, object] | None = None,
    previous_domain_time: int = 0,
) -> dict:
    """Evaluate TEMP-1 time mapping model deterministically."""

    payload = dict(model_row or {})
    params = _as_map(parameters)
    inputs = _as_map(input_values)
    model_type_id = str(payload.get("model_type_id", "")).strip()
    model_id = str(payload.get("model_id", "")).strip()
    tick = int(max(0, _as_int(canonical_tick, 0)))
    scope_token = str(scope_id or "").strip() or "global"
    prev_value = int(_as_int(previous_domain_time, 0))

    if model_type_id == "model_type.time_mapping_proper_default_stub":
        gravity_value = _as_map(inputs.get("field.gravity_vector") or inputs.get("gravity_vector") or {})
        velocity_value = _as_map(inputs.get("velocity") or inputs.get("momentum_velocity") or {})
        gravity_mag = int(
            abs(_as_int(gravity_value.get("x", 0), 0))
            + abs(_as_int(gravity_value.get("y", 0), 0))
            + abs(_as_int(gravity_value.get("z", 0), 0))
        )
        speed_mag = int(
            abs(_as_int(velocity_value.get("x", 0), 0))
            + abs(_as_int(velocity_value.get("y", 0), 0))
            + abs(_as_int(velocity_value.get("z", 0), 0))
        )
        base_delta = int(max(0, _as_int(params.get("base_delta_per_tick", 1000), 1000)))
        dilation_coefficient = int(max(0, _as_int(params.get("dilation_coefficient", 0), 0)))
        penalty = int((int(dilation_coefficient) * int(speed_mag + gravity_mag)) // 1_000_000)
        delta = int(max(0, int(base_delta) - int(penalty)))
        domain_value = int(prev_value + delta)
        out = {
            "model_id": model_id,
            "model_type_id": model_type_id,
            "canonical_tick": int(tick),
            "scope_id": scope_token,
            "domain_time_value": int(domain_value),
            "delta_domain_time": int(delta),
            "components": {
                "gravity_magnitude": int(gravity_mag),
                "speed_magnitude": int(speed_mag),
                "base_delta_per_tick": int(base_delta),
                "dilation_coefficient": int(dilation_coefficient),
                "dilation_penalty": int(penalty),
            },
            "deterministic_fingerprint": "",
        }
        out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
        return out

    if model_type_id == "model_type.time_mapping_civil_calendar_stub":
        tick_to_seconds_ratio = int(max(0, _as_int(params.get("tick_to_seconds_ratio", 1), 1)))
        calendar_offset = int(_as_int(params.get("calendar_offset", 0), 0))
        domain_value = int(calendar_offset + int(tick) * int(tick_to_seconds_ratio))
        out = {
            "model_id": model_id,
            "model_type_id": model_type_id,
            "canonical_tick": int(tick),
            "scope_id": scope_token,
            "domain_time_value": int(domain_value),
            "delta_domain_time": int(tick_to_seconds_ratio),
            "components": {
                "tick_to_seconds_ratio": int(tick_to_seconds_ratio),
                "calendar_offset": int(calendar_offset),
            },
            "deterministic_fingerprint": "",
        }
        out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
        return out

    if model_type_id == "model_type.time_mapping_warp_session_stub":
        session_warp_factor = int(
            max(
                0,
                _as_int(
                    inputs.get("session_warp_factor", params.get("session_warp_factor", 1000)),
                    1000,
                ),
            )
        )
        offset_ticks = int(_as_int(params.get("offset_ticks", 0), 0))
        domain_value = int(offset_ticks + (int(tick) * int(session_warp_factor) // 1000))
        out = {
            "model_id": model_id,
            "model_type_id": model_type_id,
            "canonical_tick": int(tick),
            "scope_id": scope_token,
            "domain_time_value": int(domain_value),
            "delta_domain_time": int(domain_value - int(prev_value)),
            "components": {
                "session_warp_factor": int(session_warp_factor),
                "offset_ticks": int(offset_ticks),
            },
            "deterministic_fingerprint": "",
        }
        out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
        return out

    return {}


def _build_output_row(
    *,
    model_id: str,
    binding_id: str,
    target_id: str,
    output_kind: str,
    output_id: str,
    payload: Mapping[str, object],
) -> dict:
    return {
        "model_id": str(model_id),
        "binding_id": str(binding_id),
        "target_id": str(target_id),
        "output_kind": str(output_kind),
        "output_id": str(output_id),
        "payload": _canon(dict(payload or {})),
    }


def _evaluate_elec_load_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    demand_p = int(max(0, _binding_param_int(binding=binding, key="demand_p", default_value=_binding_param_int(binding=binding, key="demand", default_value=0))))
    if "motor" in model_id:
        pf_permille = int(max(1, min(1000, _binding_param_int(binding=binding, key="pf_permille", default_value=850))))
        p_val = int(demand_p)
        s_val = int((p_val * 1000 + pf_permille - 1) // pf_permille) if p_val > 0 else 0
        q_val = int(math.isqrt(max(0, int(s_val * s_val) - int(p_val * p_val))))
    else:
        p_val = int(demand_p)
        q_val = int(max(0, _binding_param_int(binding=binding, key="demand_q", default_value=0)))
        s_val = int(max(p_val, math.isqrt(max(0, int(p_val * p_val) + int(q_val * q_val)))))
    pf_val = int(1000 if s_val <= 0 else max(0, min(1000, (p_val * 1000) // max(1, s_val))))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            if output_id.endswith(".active_stub"):
                delta = int(p_val)
            elif output_id.endswith(".reactive_stub"):
                delta = int(q_val)
            elif output_id.endswith(".apparent_stub"):
                delta = int(s_val)
            else:
                delta = 0
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(delta),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            value = int(pf_val if "power_factor" in output_id else s_val)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(value)},
                )
            )
        elif output_kind == "compliance_signal":
            grade = "pass" if pf_val >= 900 else "warn" if pf_val >= 750 else "fail"
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"signal_id": output_id, "grade": grade, "score_permille": int(pf_val)},
                )
            )
    return outputs


def _evaluate_elec_pf_correction_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    current_p = int(max(0, _binding_param_int(binding=binding, key="current_p", default_value=_resolved_input_int(
        resolved_inputs=resolved_inputs,
        input_id="quantity.power.active_stub",
        default_value=0,
    ))))
    current_q = int(max(0, _binding_param_int(binding=binding, key="current_q", default_value=_resolved_input_int(
        resolved_inputs=resolved_inputs,
        input_id="quantity.power.reactive_stub",
        default_value=0,
    ))))
    desired_pf = int(max(1, min(1000, _binding_param_int(binding=binding, key="desired_pf_permille", default_value=_binding_param_int(binding=binding, key="pf_target_permille", default_value=950)))))
    max_comp_permille = int(max(0, min(1000, _binding_param_int(binding=binding, key="max_compensation_permille", default_value=1000))))
    target_s = int((current_p * 1000 + desired_pf - 1) // max(1, desired_pf)) if current_p > 0 else 0
    target_q = int(math.isqrt(max(0, int(target_s * target_s) - int(current_p * current_p))))
    raw_delta = int(target_q - current_q)
    min_delta = int(-1 * ((current_q * max_comp_permille) // 1000))
    q_delta = int(max(min_delta, raw_delta))
    adjusted_q = int(max(0, current_q + q_delta))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(q_delta if output_id.endswith(".reactive_stub") else 0),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(adjusted_q)},
                )
            )
    return outputs


def _evaluate_elec_transformer_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    in_p = int(max(0, _binding_param_int(binding=binding, key="current_p", default_value=_resolved_input_int(
        resolved_inputs=resolved_inputs,
        input_id="quantity.power.active_stub",
        default_value=0,
    ))))
    in_q = int(max(0, _binding_param_int(binding=binding, key="current_q", default_value=_resolved_input_int(
        resolved_inputs=resolved_inputs,
        input_id="quantity.power.reactive_stub",
        default_value=0,
    ))))
    ratio_permille = int(max(1, _binding_param_int(binding=binding, key="transformer_ratio_permille", default_value=1000)))
    loss_coeff = int(max(0, _binding_param_int(binding=binding, key="loss_coeff_permille", default_value=15)))
    scaled_p = int((in_p * ratio_permille) // 1000)
    scaled_q = int((in_q * ratio_permille) // 1000)
    scaled_s = int(max(0, math.isqrt(max(0, int(scaled_p * scaled_p) + int(scaled_q * scaled_q)))))
    heat_loss = int((scaled_p * loss_coeff) // 1000)
    out_p = int(max(0, scaled_p - heat_loss))
    out_q = int(max(0, scaled_q))
    out_s = int(max(out_p, math.isqrt(max(0, int(out_p * out_p) + int(out_q * out_q)))))
    delta_map = {
        "quantity.power.active_stub": int(out_p - in_p),
        "quantity.power.reactive_stub": int(out_q - in_q),
        "quantity.power.apparent_stub": int(out_s - max(0, _binding_param_int(binding=binding, key="current_s", default_value=scaled_s))),
    }
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            delta = int(delta_map.get(output_id, 0))
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(delta),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            value = int(heat_loss if output_id == "quantity.thermal.heat_loss_stub" else out_s)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(value)},
                )
            )
    return outputs


def _evaluate_elec_storage_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    soc_scale = 1_000_000
    state_of_charge = int(max(0, min(soc_scale, _binding_param_int(binding=binding, key="state_of_charge", default_value=_resolved_input_int(
        resolved_inputs=resolved_inputs,
        input_id="derived.elec.storage_state_of_charge",
        default_value=0,
    )))))
    capacity_energy = int(max(0, _binding_param_int(binding=binding, key="capacity_energy", default_value=0)))
    current_p = int(max(0, _binding_param_int(binding=binding, key="current_p", default_value=_binding_param_int(binding=binding, key="demand_p", default_value=0))))
    available_energy = int((state_of_charge * capacity_energy) // soc_scale) if capacity_energy > 0 else 0
    max_discharge = int(max(0, _binding_param_int(binding=binding, key="max_discharge_p", default_value=current_p)))
    discharge = int(max(0, min(current_p, max_discharge, available_energy)))
    delta_p = int(-1 * discharge)
    delta_q = int(0)
    delta_s = int(delta_p)
    internal_resistance = int(max(0, _binding_param_int(binding=binding, key="internal_resistance_permille", default_value=_binding_param_int(binding=binding, key="internal_resistance_proxy", default_value=25))))
    heat_loss = int((discharge * internal_resistance) // 1000)
    hazard_delta = int(1 if discharge > 0 else 0)
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            if output_id.endswith(".active_stub"):
                delta = int(delta_p)
            elif output_id.endswith(".reactive_stub"):
                delta = int(delta_q)
            elif output_id.endswith(".apparent_stub"):
                delta = int(delta_s)
            else:
                delta = 0
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(delta),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            value = int(heat_loss if output_id == "quantity.thermal.heat_loss_stub" else discharge)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(value)},
                )
            )
        elif output_kind == "hazard_increment":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"hazard_type_id": output_id, "delta": int(hazard_delta)},
                )
            )
    return outputs


def _evaluate_elec_device_loss_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    current_p = int(max(0, _binding_param_int(binding=binding, key="current_p", default_value=_resolved_input_int(
        resolved_inputs=resolved_inputs,
        input_id="quantity.power.active_stub",
        default_value=0,
    ))))
    loss_coeff = int(max(0, _binding_param_int(binding=binding, key="loss_coeff_permille", default_value=20)))
    heat_loss = int((current_p * loss_coeff) // 1000)
    delta_p = int(-1 * heat_loss)
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(delta_p if output_id.endswith(".active_stub") else 0),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(heat_loss)},
                )
            )
        elif output_kind == "effect":
            magnitude = int(max(0, min(1000, heat_loss)))
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"effect_type_id": output_id, "magnitude_permille": int(magnitude)},
                )
            )
    return outputs


def _evaluate_therm_heat_capacity_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    current_energy = int(
        max(
            0,
            _binding_param_int(
                binding=binding,
                key="current_thermal_energy",
                default_value=0,
            ),
        )
    )
    heat_flow_in = int(
        max(
            0,
            _binding_param_int(
                binding=binding,
                key="heat_flow_in",
                default_value=0,
            ),
        )
    )
    heat_capacity = int(
        max(
            1,
            _binding_param_int(
                binding=binding,
                key="heat_capacity_value",
                default_value=1,
            ),
        )
    )
    ambient_temp = int(
        _binding_param_int(
            binding=binding,
            key="ambient_temperature",
            default_value=20,
        )
    )
    updated_energy = int(max(0, current_energy + heat_flow_in))
    temperature = int(ambient_temp + (updated_energy // max(1, heat_capacity)))
    delta_energy = int(max(0, updated_energy - current_energy))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(delta_energy),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            value = int(temperature if output_id == "derived.therm.temperature" else updated_energy)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(value)},
                )
            )
    return outputs


def _evaluate_therm_conductance_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    node_a_temperature = int(_binding_param_int(binding=binding, key="node_a_temperature", default_value=20))
    node_b_temperature = int(_binding_param_int(binding=binding, key="node_b_temperature", default_value=20))
    conductance = int(max(0, _binding_param_int(binding=binding, key="conductance_value", default_value=0)))
    source_node_id = str(
        _as_map(binding.get("parameters")).get("source_node_id", "")
    ).strip()
    sink_node_id = str(
        _as_map(binding.get("parameters")).get("sink_node_id", "")
    ).strip()
    if node_a_temperature >= node_b_temperature:
        from_node_id = source_node_id
        to_node_id = sink_node_id
        delta_t = int(node_a_temperature - node_b_temperature)
    else:
        from_node_id = sink_node_id
        to_node_id = source_node_id
        delta_t = int(node_b_temperature - node_a_temperature)
    transfer = int(max(0, (conductance * delta_t) // 10))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(transfer),
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(transfer),
                        "from_node_id": from_node_id,
                        "to_node_id": to_node_id,
                    },
                )
            )
    return outputs


def _evaluate_therm_loss_to_temp_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    heat_loss = int(
        max(
            0,
            _binding_param_int(
                binding=binding,
                key="heat_loss",
                default_value=_resolved_input_int(
                    resolved_inputs=resolved_inputs,
                    input_id="quantity.thermal.heat_loss_stub",
                    default_value=0,
                ),
            ),
        )
    )
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "flow_adjustment":
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": str(
                    _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
                ).strip()
                or output_id,
                "delta": int(heat_loss),
            }
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(heat_loss)},
                )
            )
    return outputs


def _evaluate_therm_phase_transition_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    temperature = int(
        _binding_param_int(
            binding=binding,
            key="temperature",
            default_value=_resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="field.temperature",
                default_value=20000,
            ),
        )
    )
    current_phase = str(params.get("current_phase", "solid")).strip() or "solid"
    freeze_point = params.get("freeze_point")
    melt_point = params.get("melt_point")
    boil_point = params.get("boil_point")
    freeze_value = None if freeze_point is None else int(_as_int(freeze_point, 0))
    melt_value = None if melt_point is None else int(_as_int(melt_point, 0))
    boil_value = None if boil_point is None else int(_as_int(boil_point, 0))
    next_phase = str(current_phase)
    if boil_value is not None and temperature >= int(boil_value):
        next_phase = "gas"
    elif melt_value is not None and temperature >= int(melt_value):
        next_phase = "liquid"
    elif freeze_value is not None and temperature <= int(freeze_value):
        next_phase = "solid"
    transition_triggered = bool(next_phase != current_phase)
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind in {"derived_quantity", "compliance_signal"}:
            payload = {
                "quantity_id": output_id,
                "value": int(1 if transition_triggered else 0),
                "temperature": int(temperature),
                "from_phase": str(current_phase),
                "to_phase": str(next_phase),
                "transition_triggered": bool(transition_triggered),
            }
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
    return outputs


def _evaluate_therm_cure_progress_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    temperature = int(
        _binding_param_int(
            binding=binding,
            key="temperature",
            default_value=_resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="field.temperature",
                default_value=29315,
            ),
        )
    )
    min_temp = int(max(-200000, _binding_param_int(binding=binding, key="cure_temp_min", default_value=27815)))
    max_temp = int(max(min_temp, _binding_param_int(binding=binding, key="cure_temp_max", default_value=30815)))
    cure_rate = int(max(0, _binding_param_int(binding=binding, key="cure_rate_permille", default_value=10)))
    defect_rate = int(max(0, _binding_param_int(binding=binding, key="defect_rate", default_value=1)))
    current_progress = int(
        max(
            0,
            min(
                1000,
                _binding_param_int(
                    binding=binding,
                    key="cure_progress",
                    default_value=_resolved_input_int(
                        resolved_inputs=resolved_inputs,
                        input_id="derived.therm.cure_progress",
                        default_value=0,
                    ),
                ),
            ),
        )
    )
    in_range = bool(int(min_temp) <= int(temperature) <= int(max_temp))
    progress_delta = int(cure_rate if in_range else 0)
    projected = int(max(0, min(1000, current_progress + progress_delta)))
    defect_delta = int(defect_rate if (not in_range) else 0)
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "derived_quantity":
            value = int(progress_delta)
            if output_id.endswith("cure_defect_delta"):
                value = int(defect_delta)
            elif output_id.endswith("cure_progress_projected"):
                value = int(projected)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(value),
                        "temperature": int(temperature),
                        "within_cure_window": bool(in_range),
                    },
                )
            )
        elif output_kind == "hazard_increment":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"hazard_type_id": output_id, "delta": int(defect_delta)},
                )
            )
    return outputs


def _evaluate_therm_insulation_modifier_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    conductance_value = int(max(0, _binding_param_int(binding=binding, key="conductance_value", default_value=0)))
    factor_permille = int(max(0, _binding_param_int(binding=binding, key="insulation_factor_permille", default_value=1000)))
    effective = int(max(0, (conductance_value * factor_permille) // 1000))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind != "derived_quantity":
            continue
        value = int(effective)
        if output_id.endswith("insulation_factor_permille"):
            value = int(factor_permille)
        outputs.append(
            _build_output_row(
                model_id=model_id,
                binding_id=binding_id,
                target_id=target_id,
                output_kind=output_kind,
                output_id=output_id,
                payload={"quantity_id": output_id, "value": int(value)},
            )
        )
    return outputs


def _evaluate_therm_ambient_exchange_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    node_temp = int(_binding_param_int(binding=binding, key="node_temperature", default_value=20))
    ambient_temp = int(_binding_param_int(binding=binding, key="ambient_temperature", default_value=20))
    coupling = int(max(0, _binding_param_int(binding=binding, key="ambient_coupling_coefficient", default_value=0)))
    insulation = int(max(0, _binding_param_int(binding=binding, key="insulation_factor_permille", default_value=1000)))
    effective_coupling = int(max(0, (int(coupling) * int(insulation)) // 1000))
    delta_t = int(node_temp - ambient_temp)
    exchange = int(max(0, (int(effective_coupling) * abs(int(delta_t))) // 1000))
    delta_energy = int(-exchange if delta_t > 0 else exchange if delta_t < 0 else 0)
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind != "derived_quantity":
            continue
        value = int(exchange)
        if output_id.endswith("delta_energy"):
            value = int(delta_energy)
        outputs.append(
            _build_output_row(
                model_id=model_id,
                binding_id=binding_id,
                target_id=target_id,
                output_kind=output_kind,
                output_id=output_id,
                payload={
                    "quantity_id": output_id,
                    "value": int(value),
                    "heat_exchange": int(exchange),
                    "delta_thermal_energy": int(delta_energy),
                    "node_temperature": int(node_temp),
                    "ambient_temperature": int(ambient_temp),
                    "ambient_coupling_coefficient": int(coupling),
                    "insulation_factor_permille": int(insulation),
                },
            )
        )
    return outputs


def _evaluate_therm_radiator_exchange_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    node_temp = int(_binding_param_int(binding=binding, key="node_temperature", default_value=20))
    ambient_temp = int(_binding_param_int(binding=binding, key="ambient_temperature", default_value=20))
    base_conductance = int(max(0, _binding_param_int(binding=binding, key="base_conductance", default_value=0)))
    forced_multiplier = int(max(0, _binding_param_int(binding=binding, key="forced_cooling_multiplier", default_value=1000)))
    fan_on = bool(params.get("fan_on", False))
    insulation = int(max(0, _binding_param_int(binding=binding, key="insulation_factor_permille", default_value=1000)))
    active_multiplier = int(forced_multiplier if fan_on else 1000)
    effective_coupling = int(max(0, ((int(base_conductance) * int(active_multiplier)) // 1000)))
    effective_coupling = int(max(0, (int(effective_coupling) * int(insulation)) // 1000))
    delta_t = int(node_temp - ambient_temp)
    exchange = int(max(0, (int(effective_coupling) * abs(int(delta_t))) // 1000))
    delta_energy = int(-exchange if delta_t > 0 else exchange if delta_t < 0 else 0)
    profile_id = str(params.get("radiator_profile_id", "")).strip() or None
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind != "derived_quantity":
            continue
        value = int(exchange)
        if output_id.endswith("delta_energy"):
            value = int(delta_energy)
        outputs.append(
            _build_output_row(
                model_id=model_id,
                binding_id=binding_id,
                target_id=target_id,
                output_kind=output_kind,
                output_id=output_id,
                payload={
                    "quantity_id": output_id,
                    "value": int(value),
                    "heat_exchange": int(exchange),
                    "delta_thermal_energy": int(delta_energy),
                    "node_temperature": int(node_temp),
                    "ambient_temperature": int(ambient_temp),
                    "base_conductance": int(base_conductance),
                    "forced_cooling_multiplier": int(forced_multiplier),
                    "forced_cooling_on": bool(fan_on),
                    "radiator_profile_id": profile_id,
                    "insulation_factor_permille": int(insulation),
                },
            )
        )
    return outputs


def _evaluate_therm_ignite_stub_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    temperature = int(
        _binding_param_int(
            binding=binding,
            key="temperature",
            default_value=_resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="field.temperature",
                default_value=29315,
            ),
        )
    )
    ignition_threshold = int(
        _binding_param_int(
            binding=binding,
            key="ignition_threshold",
            default_value=_resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="combustion.ignition_threshold",
                default_value=42315,
            ),
        )
    )
    spread_threshold = int(
        _binding_param_int(
            binding=binding,
            key="spread_threshold",
            default_value=max(0, ignition_threshold - 1500),
        )
    )
    combustible = bool(params.get("combustible", True))
    oxygen_available = bool(params.get("oxygen_available", True))
    fire_active = bool(params.get("fire_active", False))
    ignition_triggered = bool(combustible and oxygen_available and (not fire_active) and (temperature >= ignition_threshold))

    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind in {"derived_quantity", "compliance_signal"}:
            if output_id.endswith("spread_threshold"):
                value = int(spread_threshold)
            elif output_id.endswith("ignition_threshold"):
                value = int(ignition_threshold)
            else:
                value = int(1 if ignition_triggered else 0)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(value),
                        "temperature": int(temperature),
                        "ignition_threshold": int(ignition_threshold),
                        "spread_threshold": int(spread_threshold),
                        "combustible": bool(combustible),
                        "oxygen_available": bool(oxygen_available),
                        "fire_active": bool(fire_active),
                        "ignition_triggered": bool(ignition_triggered),
                    },
                )
            )
        elif output_kind == "hazard_increment":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "hazard_type_id": output_id,
                        "delta": int(1 if ignition_triggered else 0),
                    },
                )
            )
    return outputs


def _evaluate_therm_combust_stub_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    temperature = int(
        _binding_param_int(
            binding=binding,
            key="temperature",
            default_value=_resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="field.temperature",
                default_value=29315,
            ),
        )
    )
    fire_active = bool(params.get("fire_active", False))
    fuel_remaining = int(max(0, _binding_param_int(binding=binding, key="fuel_remaining", default_value=0)))
    heat_release_rate = int(max(0, _binding_param_int(binding=binding, key="heat_release_rate", default_value=0)))
    fuel_consumption_rate = int(max(1, _binding_param_int(binding=binding, key="fuel_consumption_rate", default_value=1)))
    pollutant_emission_rate = int(
        max(
            0,
            _binding_param_int(
                binding=binding,
                key="pollutant_emission_rate",
                default_value=max(1, heat_release_rate // 4) if heat_release_rate > 0 else 0,
            ),
        )
    )

    combustion_active = bool(fire_active and fuel_remaining > 0 and heat_release_rate > 0)
    fuel_consumed = int(min(fuel_remaining, fuel_consumption_rate)) if combustion_active else 0
    heat_emission = int(heat_release_rate if (combustion_active and fuel_consumed > 0) else 0)
    pollutant_emission = int(pollutant_emission_rate if combustion_active else 0)
    fuel_after = int(max(0, fuel_remaining - fuel_consumed))

    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        output_id_lower = output_id.lower()
        if output_kind == "flow_adjustment":
            quantity_bundle_id = str(_as_map(output_ref.get("extensions")).get("quantity_bundle_id", "")).strip()
            component_quantity_id = str(
                _as_map(output_ref.get("extensions")).get("component_quantity_id", output_id)
            ).strip() or output_id
            delta = int(heat_emission if "heat" in output_id_lower else pollutant_emission)
            payload = {
                "quantity_id": output_id,
                "component_quantity_id": component_quantity_id,
                "delta": int(delta),
            }
            if quantity_bundle_id:
                payload["quantity_bundle_id"] = quantity_bundle_id
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload=payload,
                )
            )
        elif output_kind == "derived_quantity":
            value = int(1 if combustion_active else 0)
            if "pollut" in output_id_lower:
                value = int(pollutant_emission)
            elif "fuel_consumed" in output_id_lower:
                value = int(fuel_consumed)
            elif "fuel_remaining" in output_id_lower:
                value = int(fuel_after)
            elif "heat" in output_id_lower:
                value = int(heat_emission)
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(value),
                        "temperature": int(temperature),
                        "fire_active": bool(fire_active),
                        "combustion_active": bool(combustion_active),
                        "fuel_remaining_before": int(fuel_remaining),
                        "fuel_consumed": int(fuel_consumed),
                        "fuel_remaining_after": int(fuel_after),
                        "heat_emission": int(heat_emission),
                        "pollutant_emission": int(pollutant_emission),
                    },
                )
            )
        elif output_kind == "hazard_increment":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "hazard_type_id": output_id,
                        "delta": int(1 if combustion_active else 0),
                    },
                )
            )
        elif output_kind == "effect":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"effect_type_id": output_id, "magnitude_permille": int(heat_emission % 1000)},
                )
            )
    return outputs


def _evaluate_phys_gravity_stub_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    gravity_vector = _as_map(params.get("gravity_vector"))
    for row in list(resolved_inputs or []):
        if not isinstance(row, Mapping):
            continue
        input_id = str(row.get("input_id", "")).strip()
        if input_id not in {"field.gravity.vector", "field.gravity_vector"}:
            continue
        candidate = _as_map(row.get("value"))
        if candidate:
            gravity_vector = candidate
            break
    gravity = {
        "x": int(_as_int(gravity_vector.get("x", 0), 0)),
        "y": int(_as_int(gravity_vector.get("y", -10), -10)),
        "z": int(_as_int(gravity_vector.get("z", 0), 0)),
    }
    mass_value = int(
        max(
            1,
            _binding_param_int(
                binding=binding,
                key="phys.mass_value",
                default_value=_resolved_input_int(
                    resolved_inputs=resolved_inputs,
                    input_id="phys.mass_value",
                    default_value=max(
                        1,
                        _resolved_input_int(
                            resolved_inputs=resolved_inputs,
                            input_id="quantity.mass",
                            default_value=1,
                        ),
                    ),
                ),
            ),
        )
    )
    duration_ticks = int(max(1, _binding_param_int(binding=binding, key="duration_ticks", default_value=1)))
    torque = int(_binding_param_int(binding=binding, key="torque", default_value=0))
    force_vector = {
        "x": int(mass_value) * int(gravity["x"]),
        "y": int(mass_value) * int(gravity["y"]),
        "z": int(mass_value) * int(gravity["z"]),
    }
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "derived_quantity" and output_id == "process.apply_force":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": "quantity.force",
                        "mass_value": int(mass_value),
                        "gravity_vector": dict(gravity),
                        "force_vector": dict(force_vector),
                        "duration_ticks": int(duration_ticks),
                        "torque": int(torque),
                    },
                )
            )
        elif output_kind in {"derived_quantity", "compliance_signal"}:
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(
                            abs(int(force_vector["x"]))
                            + abs(int(force_vector["y"]))
                            + abs(int(force_vector["z"]))
                        ),
                        "mass_value": int(mass_value),
                    },
                )
            )
    return outputs


def _evaluate_phys_radiation_damage_stub_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    radiation_intensity = int(
        max(
            0,
            _resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="field.radiation_intensity",
                default_value=_resolved_input_int(
                    resolved_inputs=resolved_inputs,
                    input_id="field.radiation",
                    default_value=0,
                ),
            ),
        )
    )
    exposure_divisor = int(max(1, _binding_param_int(binding=binding, key="radiation_delta_divisor", default_value=100)))
    hazard_delta = int(max(0, radiation_intensity // exposure_divisor))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "hazard_increment":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"hazard_type_id": output_id, "delta": int(hazard_delta)},
                )
            )
        elif output_kind == "effect":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "effect_type_id": output_id,
                        "magnitude_permille": int(max(0, min(1000, radiation_intensity))),
                    },
                )
            )
        else:
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(radiation_intensity),
                    },
                )
            )
    return outputs


def _evaluate_phys_irradiance_heating_stub_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    irradiance = int(
        max(
            0,
            _resolved_input_int(
                resolved_inputs=resolved_inputs,
                input_id="field.irradiance",
                default_value=0,
            ),
        )
    )
    scale_permille = int(max(0, _binding_param_int(binding=binding, key="irradiance_to_heat_permille", default_value=100)))
    heat_input = int(max(0, (irradiance * scale_permille) // 1000))
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "effect":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "effect_type_id": output_id,
                        "magnitude_permille": int(max(0, min(1000, heat_input))),
                        "heat_input": int(heat_input),
                    },
                )
            )
        else:
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "quantity_id": output_id,
                        "value": int(heat_input),
                        "irradiance": int(irradiance),
                    },
                )
            )
    return outputs


def _evaluate_phys_magnetic_stub_model(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    magnetic_value: Mapping[str, object] = {}
    for row in list(resolved_inputs or []):
        if str(row.get("input_id", "")).strip() != "field.magnetic_flux_stub":
            continue
        candidate = row.get("value")
        if isinstance(candidate, Mapping):
            magnetic_value = candidate
            break
    magnitude = int(
        abs(_as_int(magnetic_value.get("x", 0), 0))
        + abs(_as_int(magnetic_value.get("y", 0), 0))
        + abs(_as_int(magnetic_value.get("z", 0), 0))
    )
    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        if output_kind == "compliance_signal":
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={
                        "signal_id": output_id,
                        "grade": "pass",
                        "score_permille": int(max(0, min(1000, magnitude))),
                    },
                )
            )
        else:
            outputs.append(
                _build_output_row(
                    model_id=model_id,
                    binding_id=binding_id,
                    target_id=target_id,
                    output_kind=output_kind,
                    output_id=output_id,
                    payload={"quantity_id": output_id, "value": int(magnitude)},
                )
            )
    return outputs


def _evaluate_time_mapping_model_outputs(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict]:
    model_id = str(model_row.get("model_id", "")).strip()
    binding_id = str(binding.get("binding_id", "")).strip()
    target_id = str(binding.get("target_id", "")).strip()
    params = _as_map(binding.get("parameters"))
    canonical_tick = int(_as_int(_resolved_input_any(resolved_inputs=resolved_inputs, input_id="canonical_tick"), 0))
    previous_domain_time = int(_as_int(params.get("previous_domain_time", 0), 0))
    input_values = {
        "field.gravity_vector": _resolved_input_vector3(resolved_inputs=resolved_inputs, input_id="field.gravity_vector"),
        "velocity": _resolved_input_vector3(resolved_inputs=resolved_inputs, input_id="velocity"),
    }
    session_warp = _resolved_input_any(resolved_inputs=resolved_inputs, input_id="session_warp_factor")
    if session_warp is not None:
        input_values["session_warp_factor"] = session_warp

    evaluation = evaluate_time_mapping_model(
        model_row=model_row,
        canonical_tick=int(canonical_tick),
        scope_id=target_id,
        parameters=params,
        input_values=input_values,
        previous_domain_time=int(previous_domain_time),
    )
    domain_time_value = int(_as_int(evaluation.get("domain_time_value", 0), 0))
    delta_domain_time = int(_as_int(evaluation.get("delta_domain_time", 0), 0))

    outputs: List[dict] = []
    for output_ref in list(output_signature or []):
        output_kind = str(output_ref.get("output_kind", "")).strip()
        output_id = str(output_ref.get("output_id", "")).strip()
        outputs.append(
            _build_output_row(
                model_id=model_id,
                binding_id=binding_id,
                target_id=target_id,
                output_kind=output_kind,
                output_id=output_id,
                payload={
                    "quantity_id": output_id,
                    "domain_time_value": int(domain_time_value),
                    "delta_domain_time": int(delta_domain_time),
                    "canonical_tick": int(canonical_tick),
                    "model_eval_fingerprint": str(evaluation.get("deterministic_fingerprint", "")).strip(),
                },
            )
        )
    return outputs


def _evaluate_known_model_outputs(
    *,
    model_row: Mapping[str, object],
    binding: Mapping[str, object],
    resolved_inputs: List[dict],
    output_signature: List[dict],
) -> List[dict] | None:
    model_type_id = str(model_row.get("model_type_id", "")).strip()
    if model_type_id == "model_type.elec_load_phasor_stub":
        return _evaluate_elec_load_model(
            model_row=model_row,
            binding=binding,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.elec_pf_correction":
        return _evaluate_elec_pf_correction_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.elec_transformer_stub":
        return _evaluate_elec_transformer_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.elec_storage_battery":
        return _evaluate_elec_storage_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.elec_device_loss":
        return _evaluate_elec_device_loss_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_heat_capacity":
        return _evaluate_therm_heat_capacity_model(
            model_row=model_row,
            binding=binding,
            output_signature=output_signature,
        )
    if model_type_id in {"model_type.therm_conductance", "model_type.therm_conductance_stub"}:
        return _evaluate_therm_conductance_model(
            model_row=model_row,
            binding=binding,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_loss_to_temp":
        return _evaluate_therm_loss_to_temp_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_phase_transition":
        return _evaluate_therm_phase_transition_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_cure_progress":
        return _evaluate_therm_cure_progress_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_insulation_modifier":
        return _evaluate_therm_insulation_modifier_model(
            model_row=model_row,
            binding=binding,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_ambient_exchange":
        return _evaluate_therm_ambient_exchange_model(
            model_row=model_row,
            binding=binding,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_radiator_exchange":
        return _evaluate_therm_radiator_exchange_model(
            model_row=model_row,
            binding=binding,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_ignite_stub":
        return _evaluate_therm_ignite_stub_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.therm_combust_stub":
        return _evaluate_therm_combust_stub_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.phys_gravity_stub":
        return _evaluate_phys_gravity_stub_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.phys_radiation_damage_stub":
        return _evaluate_phys_radiation_damage_stub_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.phys_irradiance_heating_stub":
        return _evaluate_phys_irradiance_heating_stub_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id == "model_type.phys_magnetic_stub":
        return _evaluate_phys_magnetic_stub_model(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    if model_type_id in {
        "model_type.time_mapping_proper_default_stub",
        "model_type.time_mapping_civil_calendar_stub",
        "model_type.time_mapping_warp_session_stub",
    }:
        return _evaluate_time_mapping_model_outputs(
            model_row=model_row,
            binding=binding,
            resolved_inputs=resolved_inputs,
            output_signature=output_signature,
        )
    return None


def evaluate_model_bindings(
    *,
    current_tick: int,
    model_rows: object,
    binding_rows: object,
    cache_rows: object,
    model_type_rows: Mapping[str, dict] | None,
    cache_policy_rows: Mapping[str, dict] | None,
    input_resolver_fn: Callable[[Mapping[str, object], Mapping[str, object]], object] | None,
    max_cost_units: int,
    far_target_ids: object = None,
    far_tick_stride: int = 4,
) -> dict:
    models_by_id = dict((str(row.get("model_id", "")).strip(), dict(row)) for row in normalize_constitutive_model_rows(model_rows))
    bindings = normalize_model_binding_rows(binding_rows)
    type_rows = dict(model_type_rows or {})
    cache_policy_map = dict(cache_policy_rows or {})
    cache_index = dict(((row["model_id"], row["binding_id"], row["tier"], row["inputs_hash"]), dict(row)) for row in _normalize_cache_rows(cache_rows))

    budget = int(max(0, _as_int(max_cost_units, 0))) or 1_000_000_000
    far_targets = set(_sorted_tokens(list(far_target_ids or [])))
    stride = int(max(1, _as_int(far_tick_stride, 1)))

    processed_ids: List[str] = []
    deferred_rows: List[dict] = []
    output_actions: List[dict] = []
    observation_rows: List[dict] = []
    result_rows: List[dict] = []
    spent = 0

    ordered_bindings = sorted(
        (dict(row) for row in bindings),
        key=lambda row: (int(_TIER_RANK.get(str(row.get("tier", "")), 999)), str(row.get("model_id", "")), str(row.get("binding_id", ""))),
    )
    for binding in ordered_bindings:
        binding_id = str(binding.get("binding_id", "")).strip()
        model_id = str(binding.get("model_id", "")).strip()
        target_id = str(binding.get("target_id", "")).strip()
        tier = _tier(binding.get("tier"))
        if not bool(binding.get("enabled", True)):
            deferred_rows.append({"binding_id": binding_id, "reason": "disabled"})
            continue
        model_row = dict(models_by_id.get(model_id) or {})
        if not model_row:
            deferred_rows.append({"binding_id": binding_id, "reason": "missing_model"})
            continue
        model_type_id = str(model_row.get("model_type_id", "")).strip()
        if type_rows and model_type_id not in type_rows:
            deferred_rows.append({"binding_id": binding_id, "reason": "missing_model_type"})
            continue
        if tier not in set(_sorted_tokens(model_row.get("supported_tiers"))):
            deferred_rows.append({"binding_id": binding_id, "reason": "tier_not_supported"})
            continue
        if target_id in far_targets and stride > 1 and (int(current_tick) % int(stride)) != 0:
            deferred_rows.append({"binding_id": binding_id, "reason": "degrade.far_tick_bucket"})
            continue
        cost = int(max(1, _as_int(model_row.get("cost_units", 1), 1)))
        if (spent + cost) > budget:
            deferred_rows.append({"binding_id": binding_id, "reason": "degrade.model_budget"})
            continue

        resolved_inputs = []
        for input_ref in list(model_row.get("input_signature") or []):
            input_row = dict(input_ref)
            resolved = input_resolver_fn(binding, input_row) if callable(input_resolver_fn) else None
            resolved_inputs.append(
                {
                    "input_kind": str(input_row.get("input_kind", "")),
                    "input_id": str(input_row.get("input_id", "")),
                    "selector": input_row.get("selector"),
                    "value": _canon(resolved),
                }
            )
        resolved_inputs = sorted(resolved_inputs, key=lambda row: (str(row.get("input_kind", "")), str(row.get("input_id", "")), str(row.get("selector", ""))))
        inputs_hash = canonical_sha256(
            {
                "model_id": model_id,
                "binding_id": binding_id,
                "tier": tier,
                "target_id": target_id,
                "parameters": _canon(binding.get("parameters")),
                "resolved_inputs": resolved_inputs,
            }
        )

        cache_policy_id = str(model_row.get("cache_policy_id", "cache.none")).strip() or "cache.none"
        cache_policy = dict(cache_policy_map.get(cache_policy_id) or {"mode": "none", "ttl_ticks": None})
        mode = str(cache_policy.get("mode", "none")).strip().lower() or "none"
        if mode not in _VALID_CACHE_MODES:
            raise ModelEngineError(
                REFUSAL_MODEL_CACHE_POLICY_INVALID,
                "cache policy '{}' has invalid mode '{}'".format(cache_policy_id, mode),
                {"cache_policy_id": cache_policy_id, "mode": mode},
            )
        cache_key = (model_id, binding_id, tier, inputs_hash)
        outputs = []
        outputs_hash = ""
        cache_hit = False
        rng_used = False
        cached_row = dict(cache_index.get(cache_key) or {})
        if mode == "by_inputs_hash" and cached_row:
            expires_tick = cached_row.get("expires_tick")
            cache_valid = True if expires_tick is None else int(_as_int(expires_tick, 0)) >= int(current_tick)
            if cache_valid:
                outputs = [dict(item) for item in list(cached_row.get("outputs") or []) if isinstance(item, Mapping)]
                outputs_hash = str(cached_row.get("outputs_hash", "")).strip()
                cache_hit = True

        if not cache_hit:
            seed = canonical_sha256({"model_id": model_id, "binding_id": binding_id, "inputs_hash": inputs_hash})
            base_value = int(int(seed[:10], 16) % 10000)
            if bool(model_row.get("uses_rng_stream", False)):
                rng_stream_name = str(model_row.get("rng_stream_name", "")).strip()
                if rng_stream_name:
                    base_value = int((base_value + _rng_permille(stream_name=rng_stream_name, inputs_hash=inputs_hash, tick=int(current_tick))) % 10000)
                    rng_used = True
            output_signature = sorted(
                (dict(item) for item in list(model_row.get("output_signature") or []) if isinstance(item, Mapping)),
                key=lambda item: (str(item.get("output_kind", "")), str(item.get("output_id", ""))),
            )
            evaluated = _evaluate_known_model_outputs(
                model_row=model_row,
                binding=binding,
                resolved_inputs=resolved_inputs,
                output_signature=output_signature,
            )
            if evaluated is not None:
                outputs = [
                    dict(item)
                    for item in list(evaluated or [])
                    if isinstance(item, Mapping)
                ]
            else:
                for idx, output_ref in enumerate(output_signature):
                    output_kind = str(output_ref.get("output_kind", "")).strip()
                    output_id = str(output_ref.get("output_id", "")).strip()
                    discriminator = int(int(canonical_sha256({"output_id": output_id, "idx": int(idx)})[:8], 16) % 1000)
                    value = int((int(base_value) + int(discriminator)) % 10000)
                    if output_kind == "effect":
                        payload = {"effect_type_id": output_id, "magnitude_permille": int(value % 1000)}
                    elif output_kind == "hazard_increment":
                        payload = {"hazard_type_id": output_id, "delta": int(1 + (value % 17))}
                    elif output_kind == "flow_adjustment":
                        output_extensions = dict(output_ref.get("extensions") or {}) if isinstance(output_ref.get("extensions"), Mapping) else {}
                        binding_parameters = dict(binding.get("parameters") or {}) if isinstance(binding.get("parameters"), Mapping) else {}
                        quantity_bundle_id = str(
                            output_extensions.get("quantity_bundle_id")
                            or binding_parameters.get("quantity_bundle_id")
                            or ""
                        ).strip()
                        component_quantity_id = str(
                            output_extensions.get("component_quantity_id")
                            or output_extensions.get("quantity_id")
                            or binding_parameters.get("component_quantity_id")
                            or output_id
                        ).strip()
                        payload = {
                            "quantity_id": output_id,
                            "component_quantity_id": component_quantity_id or output_id,
                            "delta": int((value % 21) - 10),
                        }
                        if quantity_bundle_id:
                            payload["quantity_bundle_id"] = quantity_bundle_id
                    elif output_kind == "compliance_signal":
                        grade = ("pass", "warn", "fail")[int(value) % 3]
                        payload = {"signal_id": output_id, "grade": grade, "score_permille": int(value % 1000)}
                    else:
                        payload = {"quantity_id": output_id, "value": int(value)}
                    outputs.append(
                        {
                            "model_id": model_id,
                            "binding_id": binding_id,
                            "target_id": target_id,
                            "output_kind": output_kind,
                            "output_id": output_id,
                            "payload": payload,
                        }
                    )
            outputs_hash = canonical_sha256(outputs)
            if mode == "by_inputs_hash":
                ttl_ticks = cache_policy.get("ttl_ticks")
                ttl = None if ttl_ticks is None else int(max(0, _as_int(ttl_ticks, 0)))
                cache_index[cache_key] = {
                    "model_id": model_id,
                    "binding_id": binding_id,
                    "tier": tier,
                    "inputs_hash": inputs_hash,
                    "outputs_hash": outputs_hash,
                    "outputs": [dict(item) for item in outputs],
                    "computed_tick": int(current_tick),
                    "expires_tick": None if ttl is None or ttl <= 0 else int(current_tick + ttl),
                    "extensions": {"cache_policy_id": cache_policy_id},
                }

        observation_id = "artifact.observation.model.{}".format(
            canonical_sha256(
                {
                    "tick": int(current_tick),
                    "model_id": model_id,
                    "binding_id": binding_id,
                    "inputs_hash": inputs_hash,
                    "outputs_hash": outputs_hash,
                }
            )[:16]
        )
        observation_rows.append(
            {
                "artifact_id": observation_id,
                "artifact_family_id": "OBSERVATION",
                "extensions": {
                    "model_id": model_id,
                    "binding_id": binding_id,
                    "target_id": target_id,
                    "tier": tier,
                    "inputs_hash": inputs_hash,
                    "outputs_hash": outputs_hash,
                    "cache_hit": bool(cache_hit),
                    "rng_used": bool(rng_used),
                },
            }
        )
        result_rows.append(
            {
                "schema_version": "1.0.0",
                "result_id": "",
                "tick": int(current_tick),
                "model_id": model_id,
                "binding_id": binding_id,
                "inputs_hash": inputs_hash,
                "outputs_hash": outputs_hash,
                "derived_observation_artifact_id": observation_id,
                "extensions": {
                    "tier": tier,
                    "target_id": target_id,
                    "cache_hit": bool(cache_hit),
                    "cache_policy_id": cache_policy_id,
                },
            }
        )
        output_actions.extend(dict(item) for item in outputs)
        processed_ids.append(binding_id)
        spent += cost

    return {
        "processed_binding_ids": _sorted_tokens(processed_ids),
        "deferred_rows": sorted(
            (dict(row) for row in deferred_rows if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("binding_id", "")), str(row.get("reason", ""))),
        ),
        "evaluation_results": normalize_model_evaluation_result_rows(result_rows),
        "output_actions": sorted(
            (dict(row) for row in output_actions if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("model_id", "")), str(row.get("binding_id", "")), str(row.get("output_kind", "")), str(row.get("output_id", ""))),
        ),
        "observation_rows": sorted((dict(row) for row in observation_rows if isinstance(row, Mapping)), key=lambda row: str(row.get("artifact_id", ""))),
        "cache_rows": _normalize_cache_rows(list(cache_index.values())),
        "cost_units": int(max(0, spent)),
        "budget_outcome": "degraded" if deferred_rows else "complete",
    }


__all__ = [
    "REFUSAL_MODEL_BINDING_INVALID",
    "REFUSAL_MODEL_CACHE_POLICY_INVALID",
    "REFUSAL_MODEL_INVALID",
    "ModelEngineError",
    "cache_policy_rows_by_id",
    "constitutive_model_rows_by_id",
    "evaluate_model_bindings",
    "evaluate_time_mapping_model",
    "model_type_rows_by_id",
    "normalize_constitutive_model_rows",
    "normalize_input_ref",
    "normalize_model_binding_rows",
    "normalize_model_evaluation_result_rows",
    "normalize_output_ref",
]
