"""SYS-6 deterministic reliability evaluation and forced-expand triggers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.system.macro.macro_capsule_engine import build_forced_expand_event_row


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    token = str(value or "").strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return bool(value)


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


def reliability_profile_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        _rows_from_registry_payload(registry_payload, ("reliability_profiles",)),
        key=lambda item: str(item.get("reliability_profile_id", "")),
    ):
        profile_id = str(row.get("reliability_profile_id", "")).strip()
        if not profile_id:
            continue
        failure_modes = []
        for mode in sorted(
            (dict(item) for item in _as_list(row.get("failure_modes")) if isinstance(item, Mapping)),
            key=lambda item: str(item.get("failure_mode_id", "")),
        ):
            mode_id = str(mode.get("failure_mode_id", "")).strip()
            if not mode_id:
                continue
            failure_modes.append(
                {
                    "failure_mode_id": mode_id,
                    "hazard_ids": _sorted_tokens(mode.get("hazard_ids")),
                    "warning_threshold": int(max(0, _as_int(mode.get("warning_threshold", 0), 0))),
                    "forced_expand_threshold": int(max(0, _as_int(mode.get("forced_expand_threshold", 0), 0))),
                    "failure_threshold": int(max(0, _as_int(mode.get("failure_threshold", 0), 0))),
                    "stochastic_curve_permille": int(
                        max(0, min(1000, _as_int(mode.get("stochastic_curve_permille", 0), 0)))
                    ),
                    "extensions": _as_map(mode.get("extensions")),
                }
            )
        payload = {
            "schema_version": "1.0.0",
            "reliability_profile_id": profile_id,
            "failure_modes": failure_modes,
            "trigger_rules": _as_map(row.get("trigger_rules")),
            "stochastic_allowed": bool(_as_bool(row.get("stochastic_allowed", False))),
            "rng_stream_name": (
                None
                if row.get("rng_stream_name") is None
                else str(row.get("rng_stream_name", "")).strip() or None
            ),
            "safe_fallback_actions": _sorted_tokens(row.get("safe_fallback_actions")),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[profile_id] = payload
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_system_failure_event_row(
    *,
    event_id: str,
    system_id: str,
    failure_mode_id: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    system_token = str(system_id or "").strip()
    failure_mode_token = str(failure_mode_id or "").strip()
    tick_value = int(max(0, _as_int(tick, 0)))
    if (not system_token) or (not failure_mode_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id or "").strip(),
        "system_id": system_token,
        "failure_mode_id": failure_mode_token,
        "tick": tick_value,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"]:
        payload["event_id"] = "event.system.failure.{}".format(
            canonical_sha256(
                {
                    "system_id": system_token,
                    "failure_mode_id": failure_mode_token,
                    "tick": tick_value,
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_failure_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    by_id: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("failure_mode_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized = build_system_failure_event_row(
            event_id=str(row.get("event_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            failure_mode_id=str(row.get("failure_mode_id", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        event_id = str(normalized.get("event_id", "")).strip()
        if event_id:
            by_id[event_id] = normalized
    return [dict(by_id[key]) for key in sorted(by_id.keys())]


def _system_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("system_id", "")),
    ):
        system_id = str(row.get("system_id", "")).strip()
        if not system_id:
            continue
        out.append(row)
    return out


def _capsule_by_system(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("system_id", "")),
    ):
        system_id = str(row.get("system_id", "")).strip()
        capsule_id = str(row.get("capsule_id", "")).strip()
        if system_id and capsule_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _health_by_system(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _fallback_profile(profile_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "reliability_profile_id": profile_id,
        "failure_modes": [
            {
                "failure_mode_id": "failure.mode.control_loss",
                "hazard_ids": ["hazard.system.unresolved", "hazard.system.capsule"],
                "warning_threshold": 500,
                "forced_expand_threshold": 700,
                "failure_threshold": 900,
                "stochastic_curve_permille": 0,
                "extensions": {},
            }
        ],
        "trigger_rules": {
            "default_warning_threshold": 500,
            "default_forced_expand_threshold": 700,
            "default_failure_threshold": 900,
        },
        "stochastic_allowed": False,
        "rng_stream_name": None,
        "safe_fallback_actions": ["safety.fail_safe_stop"],
        "deterministic_fingerprint": "",
        "extensions": {"source": "SYS6-fallback"},
    }


def _resolve_profile_id(*, system_row: Mapping[str, object]) -> str:
    ext = _as_map(system_row.get("extensions"))
    declared = str(ext.get("reliability_profile_id", "")).strip()
    if declared:
        return declared
    system_id = str(system_row.get("system_id", "")).strip().lower()
    if "reactor" in system_id:
        return "reliability.reactor_stub"
    if "pump" in system_id:
        return "reliability.pump_basic"
    if ("power" in system_id) or ("generator" in system_id):
        return "reliability.power_system_basic"
    if ("pressure" in system_id) or ("vessel" in system_id):
        return "reliability.pressure_system_basic"
    return "reliability.engine_basic"


def _mode_threshold(mode: Mapping[str, object], trigger_rules: Mapping[str, object], token: str, default_value: int) -> int:
    own = mode.get(token)
    if own is not None:
        return int(max(0, _as_int(own, default_value)))
    fallback = trigger_rules.get("default_{}".format(token), default_value)
    return int(max(0, _as_int(fallback, default_value)))


def _max_hazard_for_mode(mode: Mapping[str, object], hazards: Mapping[str, object]) -> int:
    hazard_ids = _sorted_tokens(mode.get("hazard_ids"))
    hazard_map = _as_map(hazards)
    if not hazard_ids:
        return 0
    value = 0
    for hazard_id in hazard_ids:
        value = max(value, int(max(0, _as_int(hazard_map.get(hazard_id, 0), 0))))
    return value


def _rng_roll(
    *,
    system_id: str,
    tick: int,
    profile_id: str,
    failure_mode_id: str,
    rng_stream_name: str,
) -> int:
    seed = canonical_sha256(
        {
            "system_id": str(system_id),
            "tick": int(tick),
            "profile_id": str(profile_id),
            "failure_mode_id": str(failure_mode_id),
            "rng_stream_name": str(rng_stream_name),
        }
    )
    return int(seed[:8], 16) % 1000


def evaluate_system_reliability_tick(
    *,
    current_tick: int,
    system_rows: object,
    system_macro_capsule_rows: object,
    system_health_state_rows: object,
    reliability_profile_registry_payload: Mapping[str, object] | None,
    existing_failure_event_rows: object = None,
    denied_expand_system_ids: object = None,
    inspection_requested_system_ids: object = None,
    max_system_evaluations_per_tick: int = 256,
    tick_bucket_stride: int = 1,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    max_evals = int(max(1, _as_int(max_system_evaluations_per_tick, 256)))
    bucket_stride = int(max(1, _as_int(tick_bucket_stride, 1)))
    denied_expand = set(_sorted_tokens(list(denied_expand_system_ids or [])))
    inspections = set(_sorted_tokens(list(inspection_requested_system_ids or [])))

    systems = _system_rows(system_rows)
    capsules_by_system = _capsule_by_system(system_macro_capsule_rows)
    health_by_system = _health_by_system(system_health_state_rows)
    profiles_by_id = reliability_profile_rows_by_id(reliability_profile_registry_payload)

    failure_by_id = dict(
        (
            str(row.get("event_id", "")).strip(),
            dict(row),
        )
        for row in normalize_system_failure_event_rows(existing_failure_event_rows)
        if str(row.get("event_id", "")).strip()
    )

    warning_rows: List[dict] = []
    forced_expand_rows: List[dict] = []
    safe_fallback_rows: List[dict] = []
    output_adjustment_rows: List[dict] = []
    decision_rows: List[dict] = []
    explain_requests: List[dict] = []
    rng_outcome_rows: List[dict] = []
    deferred_rows: List[dict] = []
    processed_system_ids: List[str] = []

    eval_count = 0
    for idx, system_row in enumerate(systems):
        system_id = str(system_row.get("system_id", "")).strip()
        if not system_id:
            continue
        current_tier = str(system_row.get("current_tier", "")).strip().lower() or "micro"
        if current_tier != "macro":
            continue
        if (tick + idx) % bucket_stride != 0:
            deferred_rows.append(
                {
                    "system_id": system_id,
                    "reason_code": "degrade.system.reliability_tick_bucket",
                }
            )
            continue
        if eval_count >= max_evals:
            deferred_rows.append(
                {
                    "system_id": system_id,
                    "reason_code": "degrade.system.reliability_budget",
                }
            )
            continue
        eval_count += 1

        processed_system_ids.append(system_id)
        system_ext = _as_map(system_row.get("extensions"))
        profile_id = _resolve_profile_id(system_row=system_row)
        profile = dict(profiles_by_id.get(profile_id) or _fallback_profile(profile_id))
        trigger_rules = _as_map(profile.get("trigger_rules"))
        safe_fallback_actions = _sorted_tokens(profile.get("safe_fallback_actions"))
        stochastic_allowed = bool(_as_bool(profile.get("stochastic_allowed", False)))
        rng_stream_name = str(profile.get("rng_stream_name", "")).strip() or "rng.system.reliability.default"
        health_row = dict(health_by_system.get(system_id) or {})
        hazards = _as_map(health_row.get("aggregated_hazard_levels"))
        capsule_row = dict(capsules_by_system.get(system_id) or {})
        capsule_id = str(capsule_row.get("capsule_id", "")).strip() or str(system_row.get("active_capsule_id", "")).strip()

        warning_mode = ""
        forced_mode = ""
        failure_modes_hit: List[str] = []
        fallback_required = False
        output_scale_permille = 1000
        extra_heat_loss = 0

        for mode in sorted(
            (dict(item) for item in _as_list(profile.get("failure_modes")) if isinstance(item, Mapping)),
            key=lambda item: str(item.get("failure_mode_id", "")),
        ):
            mode_id = str(mode.get("failure_mode_id", "")).strip()
            if not mode_id:
                continue
            warning_threshold = _mode_threshold(mode, trigger_rules, "warning_threshold", 500)
            forced_threshold = _mode_threshold(mode, trigger_rules, "forced_expand_threshold", 700)
            failure_threshold = _mode_threshold(mode, trigger_rules, "failure_threshold", 900)
            hazard_value = _max_hazard_for_mode(mode, hazards)
            stochastic_hit = False
            stochastic_permille = int(max(0, min(1000, _as_int(mode.get("stochastic_curve_permille", 0), 0))))
            rng_roll_value = None
            if stochastic_allowed and stochastic_permille > 0 and hazard_value >= warning_threshold:
                rng_roll_value = _rng_roll(
                    system_id=system_id,
                    tick=tick,
                    profile_id=profile_id,
                    failure_mode_id=mode_id,
                    rng_stream_name=rng_stream_name,
                )
                stochastic_hit = rng_roll_value < stochastic_permille
                rng_outcome_rows.append(
                    {
                        "system_id": system_id,
                        "tick": int(tick),
                        "reliability_profile_id": profile_id,
                        "failure_mode_id": mode_id,
                        "rng_stream_name": rng_stream_name,
                        "roll_permille": int(rng_roll_value),
                        "threshold_permille": int(stochastic_permille),
                        "hit": bool(stochastic_hit),
                    }
                )

            if hazard_value >= warning_threshold:
                warning_mode = warning_mode or mode_id
                warning_rows.append(
                    {
                        "warning_id": "warning.system.reliability.{}".format(
                            canonical_sha256({"system_id": system_id, "mode": mode_id, "tick": tick})[:16]
                        ),
                        "system_id": system_id,
                        "capsule_id": capsule_id or None,
                        "failure_mode_id": mode_id,
                        "hazard_value": int(hazard_value),
                        "warning_threshold": int(warning_threshold),
                        "tick": int(tick),
                    }
                )
                output_scale_permille = min(output_scale_permille, 800)
                extra_heat_loss = max(extra_heat_loss, 25)
                explain_requests.append(
                    {
                        "contract_id": "explain.system_warning",
                        "event_kind_id": "system.warning",
                        "event_id": "event.system.warning.{}".format(
                            canonical_sha256({"system_id": system_id, "mode": mode_id, "tick": tick})[:16]
                        ),
                        "target_id": system_id,
                        "system_id": system_id,
                        "capsule_id": capsule_id,
                        "reason_code": mode_id,
                    }
                )

            forced_requested = (hazard_value >= forced_threshold) or (system_id in inspections)
            if forced_requested:
                forced_mode = forced_mode or mode_id or "failure.mode.control_loss"
                reason_code = "reliability.forced_expand.{}".format((forced_mode or "unknown").split(".")[-1])
                forced_row = build_forced_expand_event_row(
                    event_id="",
                    capsule_id=capsule_id or "capsule.unknown",
                    tick=tick,
                    reason_code=reason_code,
                    requested_fidelity="micro",
                    deterministic_fingerprint="",
                    extensions={
                        "source_process_id": "process.system_reliability_tick",
                        "system_id": system_id,
                        "reliability_profile_id": profile_id,
                        "failure_mode_id": forced_mode or None,
                        "hazard_value": int(hazard_value),
                        "forced_expand_threshold": int(forced_threshold),
                        "inspection_requested": bool(system_id in inspections),
                    },
                )
                if forced_row:
                    forced_expand_rows.append(dict(forced_row))
                explain_requests.append(
                    {
                        "contract_id": "explain.system_forced_expand",
                        "event_kind_id": "system.forced_expand",
                        "event_id": str(forced_row.get("event_id", "")).strip() if forced_row else "",
                        "target_id": system_id,
                        "system_id": system_id,
                        "capsule_id": capsule_id,
                        "reason_code": reason_code,
                    }
                )
                output_scale_permille = min(output_scale_permille, 400)
                extra_heat_loss = max(extra_heat_loss, 50)

            failed = (hazard_value >= failure_threshold) or stochastic_hit
            if failed:
                failure_modes_hit.append(mode_id)
                failure_row = build_system_failure_event_row(
                    event_id="",
                    system_id=system_id,
                    failure_mode_id=mode_id,
                    tick=tick,
                    deterministic_fingerprint="",
                    extensions={
                        "source_process_id": "process.system_reliability_tick",
                        "reliability_profile_id": profile_id,
                        "hazard_value": int(hazard_value),
                        "failure_threshold": int(failure_threshold),
                        "stochastic_triggered": bool(stochastic_hit),
                        "rng_roll_permille": None if rng_roll_value is None else int(rng_roll_value),
                    },
                )
                if failure_row:
                    failure_by_id[str(failure_row.get("event_id", "")).strip()] = dict(failure_row)
                explain_requests.append(
                    {
                        "contract_id": "explain.system_failure",
                        "event_kind_id": "system.failure",
                        "event_id": str(failure_row.get("event_id", "")).strip() if failure_row else "",
                        "target_id": system_id,
                        "system_id": system_id,
                        "capsule_id": capsule_id,
                        "reason_code": mode_id,
                    }
                )
                fallback_required = True
                output_scale_permille = min(output_scale_permille, 0)
                extra_heat_loss = max(extra_heat_loss, 80)

        if forced_mode and (system_id in denied_expand):
            fallback_required = True
            decision_rows.append(
                {
                    "decision_id": "decision.system.reliability.expand_denied.{}".format(
                        canonical_sha256({"tick": tick, "system_id": system_id, "mode": forced_mode})[:16]
                    ),
                    "tick": int(tick),
                    "process_id": "process.system_reliability_tick",
                    "result": "denied",
                    "reason_code": "refusal.system.reliability.expand_denied",
                    "extensions": {
                        "system_id": system_id,
                        "capsule_id": capsule_id,
                        "failure_mode_id": forced_mode,
                        "safe_fallback_actions": list(safe_fallback_actions),
                    },
                }
            )

        if fallback_required:
            safe_fallback_rows.append(
                {
                    "system_id": system_id,
                    "capsule_id": capsule_id or None,
                    "reliability_profile_id": profile_id,
                    "safe_fallback_actions": list(safe_fallback_actions),
                    "failure_modes": _sorted_tokens(failure_modes_hit),
                    "tick": int(tick),
                }
            )
            explain_requests.append(
                {
                    "contract_id": "explain.system_failure",
                    "event_kind_id": "system.safety_shutdown",
                    "event_id": "event.system.safety_shutdown.{}".format(
                        canonical_sha256({"system_id": system_id, "tick": tick})[:16]
                    ),
                    "target_id": system_id,
                    "system_id": system_id,
                    "capsule_id": capsule_id,
                    "reason_code": "safety_fallback",
                }
            )

        if (output_scale_permille < 1000) or (extra_heat_loss > 0):
            output_adjustment_rows.append(
                {
                    "system_id": system_id,
                    "capsule_id": capsule_id or None,
                    "output_scale_permille": int(max(0, min(1000, output_scale_permille))),
                    "extra_heat_loss": int(max(0, extra_heat_loss)),
                    "forced_mode_id": forced_mode or None,
                    "warning_mode_id": warning_mode or None,
                    "safe_fallback": bool(fallback_required),
                }
            )

    normalized_forced_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in forced_expand_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("capsule_id", "")),
                str(item.get("event_id", "")),
            ),
        )
    ]
    normalized_warning_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in warning_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("system_id", "")),
                str(item.get("failure_mode_id", "")),
            ),
        )
    ]
    normalized_safe_fallback_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in safe_fallback_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("system_id", "")),
            ),
        )
    ]
    normalized_output_adjustments = [
        dict(row)
        for row in sorted(
            (dict(item) for item in output_adjustment_rows if isinstance(item, Mapping)),
            key=lambda item: (str(item.get("system_id", "")), str(item.get("capsule_id", ""))),
        )
    ]
    normalized_decisions = [
        dict(row)
        for row in sorted(
            (dict(item) for item in decision_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("decision_id", "")),
            ),
        )
    ]
    normalized_explain = [
        dict(row)
        for row in sorted(
            (
                dict(item)
                for item in explain_requests
                if isinstance(item, Mapping)
                and str(item.get("event_id", "")).strip()
                and str(item.get("target_id", "")).strip()
            ),
            key=lambda item: (
                str(item.get("event_kind_id", "")),
                str(item.get("event_id", "")),
                str(item.get("target_id", "")),
            ),
        )
    ]
    normalized_rng_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in rng_outcome_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("system_id", "")),
                str(item.get("failure_mode_id", "")),
            ),
        )
    ]
    normalized_deferred_rows = [
        dict(row)
        for row in sorted(
            (dict(item) for item in deferred_rows if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("system_id", "")),
                str(item.get("reason_code", "")),
            ),
        )
    ]

    result = {
        "result": "complete",
        "processed_system_ids": _sorted_tokens(processed_system_ids),
        "warning_rows": normalized_warning_rows,
        "forced_expand_request_rows": normalized_forced_rows,
        "failure_event_rows": normalize_system_failure_event_rows(list(failure_by_id.values())),
        "safe_fallback_rows": normalized_safe_fallback_rows,
        "output_adjustment_rows": normalized_output_adjustments,
        "decision_log_rows": normalized_decisions,
        "explain_requests": normalized_explain,
        "rng_outcome_rows": normalized_rng_rows,
        "deferred_rows": normalized_deferred_rows,
        "degraded": bool(normalized_deferred_rows),
        "degrade_reason": "degrade.system.reliability_scheduler_budget" if normalized_deferred_rows else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "reliability_profile_rows_by_id",
    "build_system_failure_event_row",
    "normalize_system_failure_event_rows",
    "evaluate_system_reliability_tick",
]
