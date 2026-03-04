"""CHEM-3 deterministic corrosion/fouling/scaling degradation helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from src.control.effects import build_effect, normalize_effect_rows
from src.models.model_engine import (
    cache_policy_rows_by_id,
    constitutive_model_rows_by_id,
    evaluate_model_bindings,
    model_type_rows_by_id,
    normalize_constitutive_model_rows,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_KINDS = {"corrosion", "fouling", "scaling"}
_KIND_TO_HAZARD_ID = {
    "corrosion": "hazard.corrosion_level",
    "fouling": "hazard.fouling_level",
    "scaling": "hazard.scaling_level",
}
_KIND_TO_EFFECT_OUTPUT_IDS = {
    "corrosion": ("effect.strength_reduction", "effect.insulation_breakdown_risk"),
    "fouling": ("effect.conductance_reduction", "effect.pipe_loss_increase"),
    "scaling": ("effect.pipe_capacity_reduction",),
}
_EFFECT_OUTPUT_TO_MODIFIER = {
    "effect.strength_reduction": "strength_reduction_permille",
    "effect.insulation_breakdown_risk": "insulation_breakdown_risk_permille",
    "effect.conductance_reduction": "conductance_reduction_permille",
    "effect.pipe_loss_increase": "pipe_loss_increase_permille",
    "effect.pipe_capacity_reduction": "pipe_capacity_reduction_permille",
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    out: List[str] = []
    for item in values:
        token = str(item or "").strip()
        if token and token not in out:
            out.append(token)
    return sorted(out)


def _normalize_kind_id(value: object) -> str:
    token = str(value or "").strip().lower()
    if token.startswith("degr."):
        token = str(token.split(".", 1)[1]).strip().lower()
    return token


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def build_degradation_state(
    *,
    target_id: str,
    degradation_kind_id: str,
    level_value: int,
    last_update_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    target_token = str(target_id or "").strip()
    kind_token = _normalize_kind_id(degradation_kind_id)
    if not target_token or kind_token not in _VALID_KINDS:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "target_id": target_token,
        "degradation_kind_id": kind_token,
        "level_value": int(max(0, min(1000, _as_int(level_value, 0)))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_degradation_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_id", "")),
            str(item.get("degradation_kind_id", "")),
        ),
    ):
        normalized = build_degradation_state(
            target_id=str(row.get("target_id", "")).strip(),
            degradation_kind_id=str(row.get("degradation_kind_id", "")).strip(),
            level_value=_as_int(row.get("level_value", 0), 0),
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        key = "{}::{}".format(
            str(normalized.get("target_id", "")).strip(),
            str(normalized.get("degradation_kind_id", "")).strip(),
        )
        out[key] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def degradation_profile_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = dict(registry_payload or {})
    rows = payload.get("degradation_profiles")
    if not isinstance(rows, list):
        rows = dict(payload.get("record") or {}).get("degradation_profiles")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("profile_id", "")),
    ):
        profile_id = str(row.get("profile_id", "")).strip()
        kind_id = _normalize_kind_id(row.get("degradation_kind_id", ""))
        rate_model_id = str(row.get("rate_model_id", "")).strip()
        if (not profile_id) or (kind_id not in _VALID_KINDS) or (not rate_model_id):
            continue
        out[profile_id] = {
            "schema_version": "1.0.0",
            "profile_id": profile_id,
            "degradation_kind_id": kind_id,
            "rate_model_id": rate_model_id,
            "thresholds": _as_map(row.get("thresholds")),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _effect_magnitude_payload(*, output_id: str, magnitude_permille: int) -> dict:
    key = str(_EFFECT_OUTPUT_TO_MODIFIER.get(str(output_id).strip(), "value"))
    magnitude = int(max(0, min(1000, _as_int(magnitude_permille, 0))))
    payload = {
        "value": int(magnitude),
        "magnitude_permille": int(magnitude),
    }
    payload[key] = int(magnitude)
    return payload


def _build_binding_row(
    *,
    target_id: str,
    profile_row: Mapping[str, object],
    target_row: Mapping[str, object],
) -> dict:
    profile = dict(profile_row or {})
    target = dict(target_row or {})
    profile_id = str(profile.get("profile_id", "")).strip()
    kind_id = str(profile.get("degradation_kind_id", "")).strip()
    model_id = str(profile.get("rate_model_id", "")).strip()
    if (not profile_id) or (kind_id not in _VALID_KINDS) or (not model_id):
        return {}
    target_token = str(target_id or "").strip()
    if not target_token:
        return {}
    params = _as_map(profile.get("extensions"))
    params.update(_as_map(target.get("parameters")))
    params.update(_as_map(target.get("extensions")))
    params["degradation_kind_id"] = kind_id
    params["profile_id"] = profile_id
    params["target_id"] = target_token
    params["temperature"] = _as_int(params.get("temperature", 29315), 29315)
    params["moisture"] = int(max(0, _as_int(params.get("moisture", 0), 0)))
    params["radiation_intensity"] = int(max(0, _as_int(params.get("radiation_intensity", 0), 0)))
    params["entropy_value"] = int(max(0, _as_int(params.get("entropy_value", 0), 0)))
    params["mass_flow"] = int(max(0, _as_int(params.get("mass_flow", 0), 0)))
    params["hardness_tag"] = str(params.get("hardness_tag", "")).strip()
    params["fluid_composition_tags"] = _sorted_tokens(params.get("fluid_composition_tags"))
    params["contaminant_tags"] = _sorted_tokens(params.get("contaminant_tags"))
    return {
        "schema_version": "1.0.0",
        "binding_id": "binding.chem.degradation.{}.{}.{}".format(
            kind_id,
            target_token.replace(":", "_"),
            canonical_sha256({"profile_id": profile_id, "target_id": target_token})[:8],
        ),
        "model_id": model_id,
        "target_kind": str(target.get("target_kind", "custom")).strip() or "custom",
        "target_id": target_token,
        "tier": str(target.get("tier", "meso")).strip() or "meso",
        "enabled": bool(target.get("enabled", True)),
        "parameters": _canon(params),
        "extensions": {
            "profile_id": profile_id,
            "degradation_kind_id": kind_id,
        },
    }


def _resolve_binding_input(binding_row: Mapping[str, object], input_ref: Mapping[str, object]):
    params = _as_map(binding_row.get("parameters"))
    input_id = str(input_ref.get("input_id", "")).strip()
    if input_id == "field.temperature":
        return int(_as_int(params.get("temperature", 29315), 29315))
    if input_id == "field.moisture":
        return int(max(0, _as_int(params.get("moisture", 0), 0)))
    if input_id == "field.radiation_intensity":
        return int(max(0, _as_int(params.get("radiation_intensity", 0), 0)))
    if input_id == "quantity.entropy_index":
        return int(max(0, _as_int(params.get("entropy_value", 0), 0)))
    if input_id == "quantity.mass_flow":
        return int(max(0, _as_int(params.get("mass_flow", 0), 0)))
    if input_id == "derived.chem.fluid_composition_tags":
        return list(_sorted_tokens(params.get("fluid_composition_tags")))
    if input_id == "derived.chem.contaminant_tags":
        return list(_sorted_tokens(params.get("contaminant_tags")))
    if input_id == "derived.chem.hardness_tag":
        return str(params.get("hardness_tag", "")).strip()
    if input_id in params:
        return params.get(input_id)
    return 0


def _state_key(*, target_id: str, kind_id: str) -> str:
    return "{}::{}".format(str(target_id or "").strip(), str(kind_id or "").strip())


def evaluate_degradation_tick(
    *,
    current_tick: int,
    degradation_target_rows: object,
    degradation_state_rows: object,
    degradation_profile_registry: Mapping[str, object] | None,
    model_type_registry: Mapping[str, object] | None,
    model_cache_policy_registry: Mapping[str, object] | None,
    constitutive_model_registry: Mapping[str, object] | None,
    model_cache_rows: object = None,
    hazard_rows: object = None,
    effect_rows: object = None,
    max_target_updates_per_tick: int = 256,
    max_cost_units: int = 512,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    profiles_by_id = degradation_profile_rows_by_id(degradation_profile_registry)
    model_rows_by_id = constitutive_model_rows_by_id(constitutive_model_registry)
    selected_model_rows: List[dict] = []
    for profile in profiles_by_id.values():
        model_id = str(profile.get("rate_model_id", "")).strip()
        row = dict(model_rows_by_id.get(model_id) or {})
        if row:
            selected_model_rows.append(row)
    model_rows = normalize_constitutive_model_rows(selected_model_rows)
    model_type_rows = model_type_rows_by_id(model_type_registry)
    cache_policy_rows = cache_policy_rows_by_id(model_cache_policy_registry)

    normalized_states = normalize_degradation_state_rows(degradation_state_rows)
    state_by_key = dict(
        (
            _state_key(
                target_id=str(row.get("target_id", "")),
                kind_id=str(row.get("degradation_kind_id", "")),
            ),
            dict(row),
        )
        for row in normalized_states
    )
    target_rows = []
    if isinstance(degradation_target_rows, list):
        for row in degradation_target_rows:
            if not isinstance(row, Mapping):
                continue
            target_id = str(row.get("target_id", "")).strip()
            profile_id = str(row.get("profile_id", "")).strip()
            if target_id and profile_id and profile_id in profiles_by_id:
                target_rows.append(dict(row))
    target_rows = sorted(
        target_rows,
        key=lambda row: (
            str(row.get("target_id", "")),
            str(row.get("profile_id", "")),
        ),
    )

    cap = int(max(1, _as_int(max_target_updates_per_tick, 256)))
    active_targets = list(target_rows[:cap])
    deferred_targets = list(target_rows[cap:])
    binding_rows: List[dict] = []
    binding_kind_by_id: Dict[str, Tuple[str, str]] = {}
    for target_row in active_targets:
        target_id = str(target_row.get("target_id", "")).strip()
        profile_id = str(target_row.get("profile_id", "")).strip()
        profile_row = dict(profiles_by_id.get(profile_id) or {})
        binding_row = _build_binding_row(
            target_id=target_id,
            profile_row=profile_row,
            target_row=target_row,
        )
        if not binding_row:
            continue
        binding_id = str(binding_row.get("binding_id", "")).strip()
        kind_id = str(profile_row.get("degradation_kind_id", "")).strip()
        if binding_id and kind_id in _VALID_KINDS:
            binding_kind_by_id[binding_id] = (target_id, kind_id)
        binding_rows.append(binding_row)

    eval_result = {
        "evaluation_results": [],
        "output_actions": [],
        "observation_rows": [],
        "cache_rows": [dict(row) for row in list(model_cache_rows or []) if isinstance(row, Mapping)],
        "cost_units": 0,
        "budget_outcome": "complete",
        "deferred_binding_rows": [],
    }
    if binding_rows and model_rows:
        eval_result = evaluate_model_bindings(
            current_tick=int(tick),
            model_rows=model_rows,
            binding_rows=binding_rows,
            cache_rows=model_cache_rows,
            model_type_rows=model_type_rows,
            cache_policy_rows=cache_policy_rows,
            input_resolver_fn=_resolve_binding_input,
            max_cost_units=int(max(1, _as_int(max_cost_units, 512))),
        )

    hazard_by_key = dict(
        (
            "{}::{}".format(
                str(row.get("target_id", "")).strip(),
                str(row.get("hazard_type_id", "")).strip(),
            ),
            dict(row),
        )
        for row in list(hazard_rows or [])
        if isinstance(row, Mapping)
        and str(row.get("target_id", "")).strip()
        and str(row.get("hazard_type_id", "")).strip()
    )
    effect_runtime_rows = normalize_effect_rows(effect_rows)
    degradation_event_rows: List[dict] = []

    output_actions = sorted(
        (dict(row) for row in list(eval_result.get("output_actions") or []) if isinstance(row, Mapping)),
        key=lambda row: (
            str(row.get("model_id", "")),
            str(row.get("binding_id", "")),
            str(row.get("output_kind", "")),
            str(row.get("output_id", "")),
        ),
    )
    binding_row_by_id = dict(
        (
            str(row.get("binding_id", "")).strip(),
            dict(row),
        )
        for row in binding_rows
        if isinstance(row, Mapping) and str(row.get("binding_id", "")).strip()
    )
    for action in output_actions:
        binding_id = str(action.get("binding_id", "")).strip()
        target_id = str(action.get("target_id", "")).strip()
        if not target_id and binding_id in binding_kind_by_id:
            target_id = str(binding_kind_by_id[binding_id][0]).strip()
        kind_id = ""
        if binding_id in binding_kind_by_id:
            kind_id = str(binding_kind_by_id[binding_id][1]).strip()
        if kind_id not in _VALID_KINDS:
            continue
        state_key = _state_key(target_id=target_id, kind_id=kind_id)
        current_state = dict(state_by_key.get(state_key) or {})
        previous_level = int(max(0, min(1000, _as_int(current_state.get("level_value", 0), 0))))
        payload = _as_map(action.get("payload"))
        output_kind = str(action.get("output_kind", "")).strip()
        output_id = str(action.get("output_id", "")).strip()
        delta_applied = 0

        if output_kind == "hazard_increment":
            hazard_type_id = str(payload.get("hazard_type_id", output_id)).strip() or output_id
            delta = int(max(0, _as_int(payload.get("delta", 0), 0)))
            hazard_key = "{}::{}".format(target_id, hazard_type_id)
            current_hazard = dict(hazard_by_key.get(hazard_key) or {})
            next_value = int(
                max(0, _as_int(current_hazard.get("accumulated_value", 0), 0) + delta)
            )
            hazard_row = {
                "schema_version": "1.0.0",
                "target_id": target_id,
                "hazard_type_id": hazard_type_id,
                "accumulated_value": int(next_value),
                "last_update_tick": int(tick),
                "deterministic_fingerprint": "",
                "extensions": {
                    **_as_map(current_hazard.get("extensions")),
                    "source_process_id": "process.degradation_tick",
                    "source_model_id": str(action.get("model_id", "")).strip(),
                },
            }
            hazard_row["deterministic_fingerprint"] = canonical_sha256(
                dict(hazard_row, deterministic_fingerprint="")
            )
            hazard_by_key[hazard_key] = hazard_row
            delta_applied = int(max(0, delta))
            next_level = int(max(0, min(1000, previous_level + delta_applied)))
            state_by_key[state_key] = build_degradation_state(
                target_id=target_id,
                degradation_kind_id=kind_id,
                level_value=next_level,
                last_update_tick=int(tick),
                extensions={
                    **_as_map(current_state.get("extensions")),
                    "profile_id": str(
                        _as_map(
                            _as_map(binding_row_by_id.get(binding_id, {})).get("extensions")
                        ).get("profile_id", "")
                    ).strip()
                    or None,
                },
            )
            degradation_event_rows.append(
                {
                    "schema_version": "1.0.0",
                    "event_id": "event.chem.degradation.{}".format(
                        canonical_sha256(
                            {
                                "tick": int(tick),
                                "target_id": target_id,
                                "kind_id": kind_id,
                                "hazard_type_id": hazard_type_id,
                                "delta": int(delta_applied),
                            }
                        )[:16]
                    ),
                    "tick": int(tick),
                    "target_id": target_id,
                    "degradation_kind_id": kind_id,
                    "hazard_type_id": hazard_type_id,
                    "level_before": int(previous_level),
                    "level_after": int(next_level),
                    "delta": int(delta_applied),
                    "deterministic_fingerprint": "",
                    "extensions": {
                        "source_model_id": str(action.get("model_id", "")).strip(),
                        "source_binding_id": str(binding_id),
                    },
                }
            )
            continue

        if output_kind == "effect":
            magnitude_permille = int(
                max(
                    0,
                    min(
                        1000,
                        _as_int(payload.get("magnitude_permille", payload.get("value", 0)), 0),
                    ),
                )
            )
            effect_row = build_effect(
                effect_id="",
                effect_type_id=output_id,
                target_id=target_id,
                applied_tick=int(tick),
                duration_ticks=1,
                stacking_policy_id="stack.replace_latest",
                magnitude=_effect_magnitude_payload(
                    output_id=output_id,
                    magnitude_permille=int(magnitude_permille),
                ),
                source_event_id=None,
                extensions={
                    "source_process_id": "process.degradation_tick",
                    "source_model_id": str(action.get("model_id", "")).strip(),
                    "source_binding_id": str(binding_id),
                    "degradation_kind_id": kind_id,
                },
            )
            effect_runtime_rows = normalize_effect_rows(
                list(effect_runtime_rows or []) + [effect_row]
            )
            degradation_event_rows.append(
                {
                    "schema_version": "1.0.0",
                    "event_id": "event.chem.degradation.effect.{}".format(
                        canonical_sha256(
                            {
                                "tick": int(tick),
                                "target_id": target_id,
                                "kind_id": kind_id,
                                "effect_type_id": output_id,
                                "magnitude_permille": int(magnitude_permille),
                            }
                        )[:16]
                    ),
                    "tick": int(tick),
                    "target_id": target_id,
                    "degradation_kind_id": kind_id,
                    "effect_type_id": output_id,
                    "magnitude_permille": int(magnitude_permille),
                    "deterministic_fingerprint": "",
                    "extensions": {
                        "source_model_id": str(action.get("model_id", "")).strip(),
                        "source_binding_id": str(binding_id),
                    },
                }
            )

    for row in degradation_event_rows:
        row["deterministic_fingerprint"] = canonical_sha256(
            dict(row, deterministic_fingerprint="")
        )

    normalized_degradation_states = normalize_degradation_state_rows(
        list(state_by_key.values())
    )
    normalized_hazards = sorted(
        [dict(hazard_by_key[key]) for key in sorted(hazard_by_key.keys())],
        key=lambda row: (
            str(row.get("target_id", "")),
            str(row.get("hazard_type_id", "")),
        ),
    )
    degraded = bool(
        deferred_targets
        or list(eval_result.get("deferred_binding_rows") or [])
    )
    decision_log_rows: List[dict] = []
    if deferred_targets:
        decision_log_rows.append(
            {
                "decision_id": "decision.chem.degradation.degrade.targets.{}".format(
                    canonical_sha256(
                        {
                            "tick": int(tick),
                            "deferred_targets": [
                                "{}::{}".format(
                                    str(row.get("target_id", "")).strip(),
                                    str(row.get("profile_id", "")).strip(),
                                )
                                for row in deferred_targets
                            ],
                        }
                    )[:16]
                ),
                "tick": int(tick),
                "reason_code": "degrade.chem.degradation_target_budget",
                "details": {
                    "max_target_updates_per_tick": int(cap),
                    "deferred_target_ids": _sorted_tokens(
                        [str(row.get("target_id", "")).strip() for row in deferred_targets]
                    ),
                    "mode": "degradation_subset",
                },
                "deterministic_fingerprint": "",
            }
        )
    if list(eval_result.get("deferred_binding_rows") or []):
        decision_log_rows.append(
            {
                "decision_id": "decision.chem.degradation.degrade.models.{}".format(
                    canonical_sha256(
                        {
                            "tick": int(tick),
                            "deferred_count": int(
                                len(list(eval_result.get("deferred_binding_rows") or []))
                            ),
                        }
                    )[:16]
                ),
                "tick": int(tick),
                "reason_code": "degrade.chem.degradation_model_budget",
                "details": {
                    "deferred_binding_count": int(
                        len(list(eval_result.get("deferred_binding_rows") or []))
                    ),
                    "max_cost_units": int(max(1, _as_int(max_cost_units, 512))),
                    "mode": "degradation_subset",
                },
                "deterministic_fingerprint": "",
            }
        )
    for row in decision_log_rows:
        row["deterministic_fingerprint"] = canonical_sha256(
            dict(row, deterministic_fingerprint="")
        )

    return {
        "degradation_state_rows": [dict(row) for row in normalized_degradation_states],
        "hazard_rows": [dict(row) for row in normalized_hazards],
        "effect_rows": [dict(row) for row in list(effect_runtime_rows or []) if isinstance(row, Mapping)],
        "degradation_event_rows": sorted(
            [dict(row) for row in degradation_event_rows if isinstance(row, Mapping)],
            key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("event_id", "")),
            ),
        ),
        "decision_log_rows": sorted(
            [dict(row) for row in decision_log_rows if isinstance(row, Mapping)],
            key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("decision_id", "")),
            ),
        ),
        "processed_target_ids": _sorted_tokens(
            [str(row.get("target_id", "")).strip() for row in active_targets]
        ),
        "deferred_target_ids": _sorted_tokens(
            [str(row.get("target_id", "")).strip() for row in deferred_targets]
        ),
        "evaluation_results": [
            dict(row)
            for row in list(eval_result.get("evaluation_results") or [])
            if isinstance(row, Mapping)
        ],
        "output_actions": [
            dict(row)
            for row in list(eval_result.get("output_actions") or [])
            if isinstance(row, Mapping)
        ],
        "observation_rows": [
            dict(row)
            for row in list(eval_result.get("observation_rows") or [])
            if isinstance(row, Mapping)
        ],
        "cache_rows": [
            dict(row)
            for row in list(eval_result.get("cache_rows") or [])
            if isinstance(row, Mapping)
        ],
        "cost_units": int(max(0, _as_int(eval_result.get("cost_units", 0), 0))),
        "budget_outcome": "degraded" if degraded else "complete",
        "degraded": bool(degraded),
    }


__all__ = [
    "build_degradation_state",
    "degradation_profile_rows_by_id",
    "evaluate_degradation_tick",
    "normalize_degradation_state_rows",
]
