"""Deterministic TEMP-2 time mapping evaluation helpers."""

from __future__ import annotations

from typing import Callable, Dict, List, Mapping

from src.meta.numeric import deterministic_mul_div
from src.models import constitutive_model_rows_by_id, evaluate_time_mapping_model, model_type_rows_by_id
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_rate_permille(value: object, default_value: int = 1000) -> int:
    if isinstance(value, bool):
        return int(max(0, int(default_value)))
    if isinstance(value, int):
        return int(max(0, int(value) * 1000))
    token = str(value or "").strip()
    if not token:
        return int(max(0, int(default_value)))
    sign = 1
    if token.startswith("-"):
        sign = -1
        token = token[1:]
    elif token.startswith("+"):
        token = token[1:]
    if not token:
        return int(max(0, int(default_value)))
    if "." not in token:
        try:
            whole = int(token)
        except ValueError:
            return int(max(0, int(default_value)))
        return int(max(0, sign * whole * 1000))
    head, tail = token.split(".", 1)
    if not head:
        head = "0"
    if (not head.isdigit()) or (tail and not tail.isdigit()):
        return int(max(0, int(default_value)))
    whole = int(head)
    frac_digits = tail[:6] if tail else ""
    frac_milli = int((frac_digits + "000")[:3]) if frac_digits else 0
    permille = int(sign * (whole * 1000 + frac_milli))
    return int(max(0, permille))


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


def _normalize_scope_selector(value: object) -> str:
    token = str(value or "").strip()
    if token in {"global", "per_spatial", "per_assembly", "per_session"}:
        return token
    return "global"


def _normalize_sync_strategy(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in {"observe", "adjust", "reject"}:
        return token
    return "observe"


def _normalize_temporal_domain_id(value: object) -> str:
    token = str(value or "").strip()
    return token or "time.canonical_tick"


def _normalize_domain_value(value: object, default_value: int = 0):
    if isinstance(value, Mapping):
        payload = dict(value)
        for key in ("domain_time_value", "value", "ticks", "seconds"):
            if key in payload:
                return int(_as_int(payload.get(key), default_value))
    if isinstance(value, (int, str)):
        return int(_as_int(value, default_value))
    return int(default_value)


def normalize_temporal_domain_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("temporal_domain_id", ""))):
        domain_id = _normalize_temporal_domain_id(row.get("temporal_domain_id"))
        if not domain_id:
            continue
        payload = {
            "schema_version": "1.0.0",
            "temporal_domain_id": domain_id,
            "description": str(row.get("description", "")).strip(),
            "scope_kind": _normalize_scope_selector(row.get("scope_kind")),
            "deterministic_fingerprint": "",
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[domain_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_drift_policy_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("drift_policy_id", ""))):
        drift_policy_id = str(row.get("drift_policy_id", "")).strip()
        if not drift_policy_id:
            continue
        base_rate_multiplier_permille = _as_rate_permille(row.get("base_rate_multiplier", 1), 1000)
        payload = {
            "schema_version": "1.0.0",
            "drift_policy_id": drift_policy_id,
            "base_rate_multiplier": str(row.get("base_rate_multiplier", "1")).strip() or "1",
            "base_rate_multiplier_permille": int(base_rate_multiplier_permille),
            "deterministic_rng_stream": str(row.get("deterministic_rng_stream", "")).strip(),
            "max_skew_allowed": int(max(0, _as_int(row.get("max_skew_allowed", 0), 0))),
            "deterministic_fingerprint": "",
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[drift_policy_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_sync_policy_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("sync_policy_id", ""))):
        sync_policy_id = str(row.get("sync_policy_id", "")).strip()
        if not sync_policy_id:
            continue
        payload = {
            "schema_version": "1.0.0",
            "sync_policy_id": sync_policy_id,
            "adjustment_strategy": _normalize_sync_strategy(row.get("adjustment_strategy")),
            "max_adjust_per_tick": int(max(0, _as_int(row.get("max_adjust_per_tick", 0), 0))),
            "deterministic_fingerprint": "",
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[sync_policy_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_time_mapping_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("mapping_id", ""))):
        mapping_id = str(row.get("mapping_id", "")).strip()
        model_id = str(row.get("model_id", "")).strip()
        to_domain_id = _normalize_temporal_domain_id(row.get("to_domain_id"))
        if (not mapping_id) or (not model_id) or (not to_domain_id):
            continue
        payload = {
            "schema_version": "1.0.0",
            "mapping_id": mapping_id,
            "from_domain_id": _normalize_temporal_domain_id(row.get("from_domain_id")),
            "to_domain_id": to_domain_id,
            "model_id": model_id,
            "scope_selector": _normalize_scope_selector(row.get("scope_selector")),
            "drift_policy_id": str(row.get("drift_policy_id", "")).strip(),
            "parameters": _canon(_as_map(row.get("parameters"))),
            "deterministic_fingerprint": "",
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        if payload["from_domain_id"] != "time.canonical_tick":
            continue
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[mapping_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def build_time_mapping_cache_row(
    *,
    mapping_id: str,
    temporal_domain_id: str,
    scope_id: str,
    canonical_tick: int,
    domain_time_value: object,
    delta_domain_time: int,
    model_id: str,
    drift_policy_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "mapping_id": str(mapping_id or "").strip(),
        "temporal_domain_id": _normalize_temporal_domain_id(temporal_domain_id),
        "scope_id": str(scope_id or "").strip() or "global",
        "canonical_tick": int(max(0, _as_int(canonical_tick, 0))),
        "domain_time_value": _normalize_domain_value(domain_time_value, 0),
        "delta_domain_time": int(_as_int(delta_domain_time, 0)),
        "model_id": str(model_id or "").strip(),
        "drift_policy_id": str(drift_policy_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["mapping_id"]) or (not payload["temporal_domain_id"]) or (not payload["model_id"]):
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_time_mapping_cache_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("mapping_id", "")),
            str(item.get("scope_id", "")),
            int(max(0, _as_int(item.get("canonical_tick", 0), 0))),
        ),
    ):
        payload = build_time_mapping_cache_row(
            mapping_id=str(row.get("mapping_id", "")).strip(),
            temporal_domain_id=str(row.get("temporal_domain_id", "")).strip(),
            scope_id=str(row.get("scope_id", "")).strip(),
            canonical_tick=int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
            domain_time_value=row.get("domain_time_value", 0),
            delta_domain_time=int(_as_int(row.get("delta_domain_time", 0), 0)),
            model_id=str(row.get("model_id", "")).strip(),
            drift_policy_id=str(row.get("drift_policy_id", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not payload:
            continue
        key = "{}::{}::{}".format(
            str(payload.get("mapping_id", "")).strip(),
            str(payload.get("scope_id", "")).strip(),
            int(payload.get("canonical_tick", 0)),
        )
        out[key] = payload
    return [
        dict(out[key])
        for key in sorted(
            out.keys(),
            key=lambda token: (
                str((token.split("::", 2) + ["", "", ""])[0]),
                str((token.split("::", 2) + ["", "", ""])[1]),
                int(_as_int((token.split("::", 2) + ["0", "0", "0"])[2], 0)),
            ),
        )
    ]


def build_time_stamp_artifact(
    *,
    stamp_id: str,
    temporal_domain_id: str,
    canonical_tick: int,
    domain_time_value: object,
    issuer_subject_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stamp_id": str(stamp_id or "").strip(),
        "temporal_domain_id": _normalize_temporal_domain_id(temporal_domain_id),
        "canonical_tick": int(max(0, _as_int(canonical_tick, 0))),
        "domain_time_value": _normalize_domain_value(domain_time_value, 0),
        "issuer_subject_id": str(issuer_subject_id or "").strip() or "system.time_mapping_engine",
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["stamp_id"]) or (not payload["temporal_domain_id"]) or (not payload["issuer_subject_id"]):
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_time_stamp_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("canonical_tick", 0), 0))),
            str(item.get("stamp_id", "")),
        ),
    ):
        payload = build_time_stamp_artifact(
            stamp_id=str(row.get("stamp_id", "")).strip(),
            temporal_domain_id=str(row.get("temporal_domain_id", "")).strip(),
            canonical_tick=int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
            domain_time_value=row.get("domain_time_value", 0),
            issuer_subject_id=str(row.get("issuer_subject_id", "")).strip() or "system.time_mapping_engine",
            extensions=_as_map(row.get("extensions")),
        )
        if not payload:
            continue
        out[str(payload.get("stamp_id", "")).strip()] = payload
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (int(_as_int(out[key].get("canonical_tick", 0), 0)), key))]


def build_proper_time_state(
    *,
    target_id: str,
    accumulated_proper_time: int,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "target_id": str(target_id or "").strip(),
        "accumulated_proper_time": int(max(0, _as_int(accumulated_proper_time, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["target_id"]:
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_proper_time_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("target_id", ""))):
        payload = build_proper_time_state(
            target_id=str(row.get("target_id", "")).strip(),
            accumulated_proper_time=int(max(0, _as_int(row.get("accumulated_proper_time", 0), 0))),
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            extensions=_as_map(row.get("extensions")),
        )
        if not payload:
            continue
        out[str(payload.get("target_id", "")).strip()] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def build_time_adjust_event(
    *,
    adjust_id: str,
    target_id: str,
    previous_domain_time: int,
    new_domain_time: int,
    adjustment_delta: int,
    originating_receipt_id: str,
    sync_policy_id: str,
    temporal_domain_id: str,
    canonical_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "adjust_id": str(adjust_id or "").strip(),
        "target_id": str(target_id or "").strip(),
        "temporal_domain_id": _normalize_temporal_domain_id(temporal_domain_id),
        "canonical_tick": int(max(0, _as_int(canonical_tick, 0))),
        "previous_domain_time": int(_as_int(previous_domain_time, 0)),
        "new_domain_time": int(_as_int(new_domain_time, 0)),
        "adjustment_delta": int(_as_int(adjustment_delta, 0)),
        "originating_receipt_id": str(originating_receipt_id or "").strip(),
        "sync_policy_id": str(sync_policy_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if (
        (not payload["adjust_id"])
        or (not payload["target_id"])
        or (not payload["originating_receipt_id"])
        or (not payload["sync_policy_id"])
    ):
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_time_adjust_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("canonical_tick", 0), 0))),
            str(item.get("adjust_id", "")),
        ),
    ):
        payload = build_time_adjust_event(
            adjust_id=str(row.get("adjust_id", "")).strip(),
            target_id=str(row.get("target_id", "")).strip(),
            previous_domain_time=int(_as_int(row.get("previous_domain_time", 0), 0)),
            new_domain_time=int(_as_int(row.get("new_domain_time", 0), 0)),
            adjustment_delta=int(_as_int(row.get("adjustment_delta", 0), 0)),
            originating_receipt_id=str(row.get("originating_receipt_id", "")).strip(),
            sync_policy_id=str(row.get("sync_policy_id", "")).strip(),
            temporal_domain_id=str(row.get("temporal_domain_id", "")).strip(),
            canonical_tick=int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
            extensions=_as_map(row.get("extensions")),
        )
        if not payload:
            continue
        out[str(payload.get("adjust_id", "")).strip()] = payload
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (int(_as_int(out[key].get("canonical_tick", 0), 0)), key))]


def _apply_drift_policy(
    *,
    base_delta: int,
    mapping_id: str,
    scope_id: str,
    canonical_tick: int,
    drift_policy_row: Mapping[str, object] | None,
) -> tuple[int, dict]:
    policy = dict(drift_policy_row or {})
    base_delta_int = int(max(0, _as_int(base_delta, 0)))
    if not policy:
        return base_delta_int, {
            "drift_applied": False,
            "base_delta": int(base_delta_int),
            "effective_delta": int(base_delta_int),
            "jitter": 0,
        }

    base_multiplier_permille = _as_rate_permille(
        policy.get("base_rate_multiplier_permille", policy.get("base_rate_multiplier", 1)),
        1000,
    )
    effective_delta = int(
        max(
            0,
            deterministic_mul_div(
                int(base_delta_int),
                int(base_multiplier_permille),
                1000,
                rounding_mode="round_half_to_even",
            ),
        )
    )

    rng_stream = str(policy.get("deterministic_rng_stream", "")).strip()
    jitter = 0
    if rng_stream:
        jitter_seed = canonical_sha256(
            {
                "mapping_id": str(mapping_id or "").strip(),
                "scope_id": str(scope_id or "").strip(),
                "canonical_tick": int(max(0, _as_int(canonical_tick, 0))),
                "deterministic_rng_stream": rng_stream,
            }
        )
        jitter = int(int(jitter_seed[:2], 16) % 3) - 1
        effective_delta = int(max(0, int(effective_delta) + int(jitter)))

    max_skew_allowed = int(max(0, _as_int(policy.get("max_skew_allowed", 0), 0)))
    if max_skew_allowed > 0:
        drift_delta = int(effective_delta) - int(base_delta_int)
        if drift_delta > max_skew_allowed:
            effective_delta = int(base_delta_int + max_skew_allowed)
        elif drift_delta < (0 - max_skew_allowed):
            effective_delta = int(max(0, base_delta_int - max_skew_allowed))

    return int(effective_delta), {
        "drift_applied": True,
        "base_delta": int(base_delta_int),
        "effective_delta": int(effective_delta),
        "base_rate_multiplier_permille": int(base_multiplier_permille),
        "deterministic_rng_stream": rng_stream,
        "max_skew_allowed": int(max_skew_allowed),
        "jitter": int(jitter),
    }


def evaluate_time_mappings(
    *,
    current_tick: int,
    time_mapping_rows: object,
    temporal_domain_rows: object,
    model_rows: object,
    model_type_rows: Mapping[str, dict] | None = None,
    drift_policy_rows: object = None,
    existing_cache_rows: object = None,
    existing_time_stamp_rows: object = None,
    existing_proper_time_rows: object = None,
    scope_rows_by_selector: Mapping[str, object] | None = None,
    input_resolver_fn: Callable[[Mapping[str, object], str], Mapping[str, object]] | None = None,
    session_id: str = "session.default",
    issuer_subject_id: str = "system.time_mapping_engine",
    max_cost_units: int = 256,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    mappings = normalize_time_mapping_rows(time_mapping_rows)
    temporal_domains = normalize_temporal_domain_rows(temporal_domain_rows)
    del temporal_domains
    models_by_id = constitutive_model_rows_by_id({"models": list(model_rows or [])})
    types_by_id = dict(model_type_rows or model_type_rows_by_id({"model_types": []}))
    drift_policies = normalize_drift_policy_rows(drift_policy_rows)
    drift_policies_by_id = dict(
        (str(row.get("drift_policy_id", "")).strip(), dict(row))
        for row in drift_policies
        if str(row.get("drift_policy_id", "")).strip()
    )

    cache_rows = normalize_time_mapping_cache_rows(existing_cache_rows)
    time_stamp_rows = normalize_time_stamp_artifact_rows(existing_time_stamp_rows)
    proper_time_rows = normalize_proper_time_state_rows(existing_proper_time_rows)
    proper_by_target = dict((str(row.get("target_id", "")).strip(), dict(row)) for row in proper_time_rows if str(row.get("target_id", "")).strip())

    cache_by_key = dict(
        (
            (
                str(row.get("mapping_id", "")).strip(),
                str(row.get("scope_id", "")).strip(),
                int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
            ),
            dict(row),
        )
        for row in cache_rows
    )
    previous_by_mapping_scope: Dict[tuple, dict] = {}
    for row in cache_rows:
        mapping_id = str(row.get("mapping_id", "")).strip()
        scope_id = str(row.get("scope_id", "")).strip()
        key = (mapping_id, scope_id)
        candidate_tick = int(max(0, _as_int(row.get("canonical_tick", 0), 0)))
        existing = dict(previous_by_mapping_scope.get(key) or {})
        if not existing:
            previous_by_mapping_scope[key] = dict(row)
            continue
        if int(max(0, _as_int(existing.get("canonical_tick", 0), 0))) <= candidate_tick:
            previous_by_mapping_scope[key] = dict(row)

    scope_payload = dict(scope_rows_by_selector or {})
    global_scope_ids = ["global"]
    session_scope_ids = _sorted_tokens(list(scope_payload.get("per_session") or [])) or [str(session_id or "").strip() or "session.default"]
    assembly_scope_ids = _sorted_tokens(list(scope_payload.get("per_assembly") or []))
    spatial_scope_ids = _sorted_tokens(list(scope_payload.get("per_spatial") or []))

    budget = int(max(1, _as_int(max_cost_units, 256)))
    spent = 0
    deferred_rows: List[dict] = []
    value_rows: List[dict] = []
    active_drift_policy_ids = set()

    for mapping in mappings:
        mapping_id = str(mapping.get("mapping_id", "")).strip()
        model_id = str(mapping.get("model_id", "")).strip()
        scope_selector = str(mapping.get("scope_selector", "global")).strip() or "global"
        if scope_selector == "global":
            scope_ids = list(global_scope_ids)
        elif scope_selector == "per_session":
            scope_ids = list(session_scope_ids)
        elif scope_selector == "per_assembly":
            scope_ids = list(assembly_scope_ids)
        elif scope_selector == "per_spatial":
            scope_ids = list(spatial_scope_ids)
        else:
            scope_ids = list(global_scope_ids)

        model_row = dict(models_by_id.get(model_id) or {})
        if not model_row:
            deferred_rows.append({"mapping_id": mapping_id, "reason": "missing_model", "model_id": model_id})
            continue
        model_type_id = str(model_row.get("model_type_id", "")).strip()
        if types_by_id and model_type_id not in types_by_id:
            deferred_rows.append({"mapping_id": mapping_id, "reason": "missing_model_type", "model_type_id": model_type_id})
            continue
        if not scope_ids:
            deferred_rows.append({"mapping_id": mapping_id, "reason": "no_scopes"})
            continue

        model_cost = int(max(1, _as_int(model_row.get("cost_units", 1), 1)))
        for scope_id in scope_ids:
            cache_key = (mapping_id, str(scope_id), int(tick))
            existing_row = dict(cache_by_key.get(cache_key) or {})
            drift_policy_id = str(mapping.get("drift_policy_id", "")).strip()
            if existing_row:
                domain_value = _normalize_domain_value(existing_row.get("domain_time_value", 0), 0)
                delta_domain_time = int(_as_int(existing_row.get("delta_domain_time", 0), 0))
                drift_policy_id = str(existing_row.get("drift_policy_id", drift_policy_id)).strip()
                if drift_policy_id:
                    active_drift_policy_ids.add(drift_policy_id)
                evaluated_payload = {
                    "domain_time_value": domain_value,
                    "delta_domain_time": delta_domain_time,
                    "deterministic_fingerprint": str(existing_row.get("deterministic_fingerprint", "")).strip(),
                }
            else:
                if (spent + model_cost) > budget:
                    deferred_rows.append({"mapping_id": mapping_id, "scope_id": str(scope_id), "reason": "degrade.time_mapping_budget"})
                    continue
                previous_row = dict(previous_by_mapping_scope.get((mapping_id, str(scope_id))) or {})
                previous_value = int(_as_int(previous_row.get("domain_time_value", 0), 0))
                if (not previous_row) and str(mapping.get("to_domain_id", "")).strip() == "time.proper":
                    previous_value = int(
                        _as_int(
                            (dict(proper_by_target.get(str(scope_id)) or {})).get("accumulated_proper_time", 0),
                            0,
                        )
                    )
                input_values = dict(input_resolver_fn(mapping, str(scope_id)) or {}) if callable(input_resolver_fn) else {}
                evaluated_payload = evaluate_time_mapping_model(
                    model_row=model_row,
                    canonical_tick=int(tick),
                    scope_id=str(scope_id),
                    parameters=dict(mapping.get("parameters") or {}),
                    input_values=input_values,
                    previous_domain_time=int(previous_value),
                )
                if not evaluated_payload:
                    deferred_rows.append({"mapping_id": mapping_id, "scope_id": str(scope_id), "reason": "evaluation_refused"})
                    continue
                base_domain_value = _normalize_domain_value(evaluated_payload.get("domain_time_value", previous_value), previous_value)
                base_delta_domain_time = int(_as_int(evaluated_payload.get("delta_domain_time", 0), 0))
                drift_policy_row = dict(drift_policies_by_id.get(drift_policy_id) or {})
                if drift_policy_id and drift_policy_row:
                    active_drift_policy_ids.add(drift_policy_id)
                adjusted_delta_domain_time, drift_components = _apply_drift_policy(
                    base_delta=int(base_delta_domain_time),
                    mapping_id=mapping_id,
                    scope_id=str(scope_id),
                    canonical_tick=int(tick),
                    drift_policy_row=drift_policy_row,
                )
                if drift_components.get("drift_applied", False):
                    domain_value = int(max(0, int(previous_value) + int(adjusted_delta_domain_time)))
                    delta_domain_time = int(adjusted_delta_domain_time)
                else:
                    domain_value = int(base_domain_value)
                    delta_domain_time = int(base_delta_domain_time)
                cache_row = build_time_mapping_cache_row(
                    mapping_id=mapping_id,
                    temporal_domain_id=str(mapping.get("to_domain_id", "")).strip(),
                    scope_id=str(scope_id),
                    canonical_tick=int(tick),
                    domain_time_value=domain_value,
                    delta_domain_time=delta_domain_time,
                    model_id=model_id,
                    drift_policy_id=drift_policy_id,
                    extensions={
                        "model_type_id": model_type_id,
                        "model_eval_fingerprint": str(evaluated_payload.get("deterministic_fingerprint", "")).strip(),
                        "base_domain_time_value": int(base_domain_value),
                        "base_delta_domain_time": int(base_delta_domain_time),
                        "drift_components": dict(drift_components),
                    },
                )
                if cache_row:
                    cache_rows.append(cache_row)
                    cache_by_key[cache_key] = dict(cache_row)
                    previous_by_mapping_scope[(mapping_id, str(scope_id))] = dict(cache_row)
                spent += model_cost

            domain_id = str(mapping.get("to_domain_id", "")).strip()
            stamp_id = "stamp.time.mapping.{}".format(
                canonical_sha256(
                    {
                        "mapping_id": mapping_id,
                        "scope_id": str(scope_id),
                        "domain_id": domain_id,
                        "tick": int(tick),
                    }
                )[:16]
            )
            time_stamp_rows.append(
                build_time_stamp_artifact(
                    stamp_id=stamp_id,
                    temporal_domain_id=domain_id,
                    canonical_tick=int(tick),
                    domain_time_value=domain_value,
                    issuer_subject_id=str(issuer_subject_id or "").strip() or "system.time_mapping_engine",
                    extensions={
                        "mapping_id": mapping_id,
                        "scope_id": str(scope_id),
                    },
                )
            )
            if domain_id == "time.proper":
                proper_by_target[str(scope_id)] = build_proper_time_state(
                    target_id=str(scope_id),
                    accumulated_proper_time=int(domain_value),
                    last_update_tick=int(tick),
                    extensions={"mapping_id": mapping_id},
                )
            value_rows.append(
                {
                    "mapping_id": mapping_id,
                    "scope_id": str(scope_id),
                    "temporal_domain_id": domain_id,
                    "domain_time_value": int(domain_value),
                    "delta_domain_time": int(delta_domain_time),
                    "drift_policy_id": drift_policy_id,
                    "canonical_tick": int(tick),
                    "deterministic_fingerprint": str(evaluated_payload.get("deterministic_fingerprint", "")).strip(),
                }
            )

    cache_rows = normalize_time_mapping_cache_rows(cache_rows)
    time_stamp_rows = normalize_time_stamp_artifact_rows(time_stamp_rows)
    proper_time_rows = normalize_proper_time_state_rows([dict(proper_by_target[key]) for key in sorted(proper_by_target.keys())])
    value_rows = sorted(
        (dict(row) for row in value_rows),
        key=lambda row: (
            str(row.get("mapping_id", "")),
            str(row.get("scope_id", "")),
            str(row.get("temporal_domain_id", "")),
            int(_as_int(row.get("canonical_tick", 0), 0)),
        ),
    )
    domain_value_index: Dict[str, int] = {}
    for row in value_rows:
        key = "{}::{}".format(str(row.get("temporal_domain_id", "")).strip(), str(row.get("scope_id", "")).strip())
        domain_value_index[key] = int(_as_int(row.get("domain_time_value", 0), 0))
    if "time.canonical_tick::global" not in domain_value_index:
        domain_value_index["time.canonical_tick::global"] = int(tick)
    if "time.canonical_tick::session.default" not in domain_value_index:
        domain_value_index["time.canonical_tick::session.default"] = int(tick)

    budget_outcome = "complete" if not deferred_rows else "degraded"
    report = {
        "cache_rows": cache_rows,
        "time_stamp_rows": time_stamp_rows,
        "proper_time_rows": proper_time_rows,
        "value_rows": value_rows,
        "domain_value_index": dict((key, int(domain_value_index[key])) for key in sorted(domain_value_index.keys())),
        "processed_count": int(len(value_rows)),
        "deferred_rows": [dict(row) for row in deferred_rows],
        "deferred_count": int(len(deferred_rows)),
        "cost_units": int(max(0, spent)),
        "budget_outcome": budget_outcome,
        "active_drift_policy_ids": sorted(str(item).strip() for item in active_drift_policy_ids if str(item).strip()),
        "time_mapping_hash_chain": canonical_sha256(list(cache_rows)),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


__all__ = [
    "build_time_adjust_event",
    "build_proper_time_state",
    "build_time_mapping_cache_row",
    "build_time_stamp_artifact",
    "evaluate_time_mappings",
    "normalize_drift_policy_rows",
    "normalize_proper_time_state_rows",
    "normalize_sync_policy_rows",
    "normalize_temporal_domain_rows",
    "normalize_time_adjust_event_rows",
    "normalize_time_mapping_cache_rows",
    "normalize_time_mapping_rows",
    "normalize_time_stamp_artifact_rows",
]
