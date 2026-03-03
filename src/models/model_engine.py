"""Deterministic META-MODEL-1 constitutive model helpers."""

from __future__ import annotations

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
                    payload = {"quantity_id": output_id, "delta": int((value % 21) - 10)}
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
    "model_type_rows_by_id",
    "normalize_constitutive_model_rows",
    "normalize_input_ref",
    "normalize_model_binding_rows",
    "normalize_model_evaluation_result_rows",
    "normalize_output_ref",
]
