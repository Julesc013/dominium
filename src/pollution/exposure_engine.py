"""POLL-2 deterministic exposure evaluation and threshold event helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.pollution.dispersion_engine import (
    accumulate_pollution_exposure,
    normalize_pollution_exposure_state_rows,
    pollution_exposure_rows_by_key,
)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_health_risk_event_row(
    *,
    event_id: str,
    subject_id: str,
    pollutant_id: str,
    threshold_crossed: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    subject_token = str(subject_id or "").strip()
    pollutant_token = str(pollutant_id or "").strip()
    threshold_token = str(threshold_crossed or "").strip().lower()
    if threshold_token not in {"warning", "critical"}:
        threshold_token = "warning"
    if (not subject_token) or (not pollutant_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id or "").strip(),
        "subject_id": subject_token,
        "pollutant_id": pollutant_token,
        "threshold_crossed": threshold_token,
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"]:
        payload["event_id"] = "event.pollution.health_risk.{}".format(
            canonical_sha256(
                {
                    "subject_id": subject_token,
                    "pollutant_id": pollutant_token,
                    "threshold_crossed": threshold_token,
                    "tick": int(payload["tick"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_health_risk_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("subject_id", "")),
            str(item.get("pollutant_id", "")),
            str(item.get("threshold_crossed", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized = build_health_risk_event_row(
            event_id=str(row.get("event_id", "")).strip(),
            subject_id=str(row.get("subject_id", "")).strip(),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            threshold_crossed=str(row.get("threshold_crossed", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        event_id = str(normalized.get("event_id", "")).strip()
        if event_id:
            out[event_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def exposure_threshold_rows_by_pollutant(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("exposure_thresholds")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("exposure_thresholds")
    if not isinstance(rows, list):
        rows = []

    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("pollutant_id", "")),
    ):
        pollutant_id = str(row.get("pollutant_id", "")).strip()
        if not pollutant_id:
            continue
        warning_threshold = int(max(0, _as_int(row.get("warning_threshold", 0), 0)))
        critical_threshold = int(max(warning_threshold, _as_int(row.get("critical_threshold", warning_threshold), warning_threshold)))
        out[pollutant_id] = {
            "schema_version": "1.0.0",
            "pollutant_id": pollutant_id,
            "warning_threshold": warning_threshold,
            "critical_threshold": critical_threshold,
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _split_subject_work(*, subject_ids: List[str], current_tick: int, max_subject_updates_per_tick: int) -> Tuple[List[str], List[str]]:
    normalized = [str(token).strip() for token in sorted(subject_ids) if str(token).strip()]
    limit = int(max(0, _as_int(max_subject_updates_per_tick, 0)))
    if limit <= 0 or len(normalized) <= limit:
        return list(normalized), []

    bucket_count = max(1, (len(normalized) + max(1, limit) - 1) // max(1, limit))
    bucket_index = int(max(0, _as_int(current_tick, 0))) % int(bucket_count)
    selected = [subject_id for idx, subject_id in enumerate(normalized) if (idx % bucket_count) == bucket_index]
    selected_set = set(selected)
    deferred = [subject_id for subject_id in normalized if subject_id not in selected_set]
    return selected[:limit], deferred


def evaluate_pollution_exposure_tick(
    *,
    current_tick: int,
    subject_rows: object,
    field_cell_rows: object,
    pollutant_types_by_id: Mapping[str, Mapping[str, object]],
    exposure_state_rows: object,
    exposure_thresholds_by_pollutant: Mapping[str, Mapping[str, object]] | None = None,
    default_exposure_factor_permille: int = 1000,
    max_subject_updates_per_tick: int = 0,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    thresholds = dict(exposure_thresholds_by_pollutant or {})

    if not isinstance(subject_rows, list):
        subject_rows = []
    normalized_subject_rows = sorted(
        (
            {
                "subject_id": str(row.get("subject_id", "")).strip(),
                "spatial_scope_id": str(row.get("spatial_scope_id", row.get("cell_id", ""))).strip(),
                "exposure_factor_permille": int(max(0, _as_int(row.get("exposure_factor_permille", default_exposure_factor_permille), default_exposure_factor_permille))),
                "extensions": _as_map(row.get("extensions")),
            }
            for row in list(subject_rows or [])
            if isinstance(row, Mapping)
            and str(row.get("subject_id", "")).strip()
            and str(row.get("spatial_scope_id", row.get("cell_id", ""))).strip()
        ),
        key=lambda row: (str(row.get("subject_id", "")), str(row.get("spatial_scope_id", ""))),
    )

    subject_ids = _sorted_tokens([str(row.get("subject_id", "")).strip() for row in normalized_subject_rows])
    selected_subject_ids, deferred_subject_ids = _split_subject_work(
        subject_ids=subject_ids,
        current_tick=tick,
        max_subject_updates_per_tick=max_subject_updates_per_tick,
    )
    selected_subject_set = set(selected_subject_ids)
    selected_subject_rows = [
        dict(row)
        for row in normalized_subject_rows
        if str(row.get("subject_id", "")).strip() in selected_subject_set
    ]

    exposure_before_by_key = pollution_exposure_rows_by_key(exposure_state_rows)
    exposure_eval = accumulate_pollution_exposure(
        current_tick=tick,
        subject_rows=selected_subject_rows,
        field_cell_rows=field_cell_rows,
        pollutant_types_by_id=pollutant_types_by_id,
        exposure_state_rows=exposure_state_rows,
        default_exposure_factor_permille=int(max(0, _as_int(default_exposure_factor_permille, 1000))),
    )
    exposure_after_by_key = pollution_exposure_rows_by_key(exposure_eval.get("exposure_state_rows"))

    health_risk_events: List[dict] = []
    hazard_hook_rows: List[dict] = []
    for increment_row in sorted(
        (dict(item) for item in list(exposure_eval.get("exposure_increment_rows") or []) if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("subject_id", "")),
            str(item.get("pollutant_id", "")),
        ),
    ):
        subject_id = str(increment_row.get("subject_id", "")).strip()
        pollutant_id = str(increment_row.get("pollutant_id", "")).strip()
        if (not subject_id) or (not pollutant_id):
            continue
        key = "{}::{}".format(subject_id, pollutant_id)
        before_value = int(max(0, _as_int((dict(exposure_before_by_key.get(key) or {})).get("accumulated_exposure", 0), 0)))
        after_value = int(max(0, _as_int((dict(exposure_after_by_key.get(key) or {})).get("accumulated_exposure", 0), 0)))
        threshold_row = dict(thresholds.get(pollutant_id) or {})
        if not threshold_row:
            continue

        threshold_rows = (
            ("warning", int(max(0, _as_int(threshold_row.get("warning_threshold", 0), 0)))),
            ("critical", int(max(0, _as_int(threshold_row.get("critical_threshold", 0), 0)))),
        )
        for threshold_name, threshold_value in threshold_rows:
            if threshold_value <= 0:
                continue
            if before_value >= threshold_value:
                continue
            if after_value < threshold_value:
                continue
            event_row = build_health_risk_event_row(
                event_id="",
                subject_id=subject_id,
                pollutant_id=pollutant_id,
                threshold_crossed=threshold_name,
                tick=tick,
                deterministic_fingerprint="",
                extensions={
                    "source_process_id": "process.pollution_dispersion_tick",
                    "threshold_value": int(threshold_value),
                    "accumulated_exposure_before": int(before_value),
                    "accumulated_exposure_after": int(after_value),
                },
            )
            if not event_row:
                continue
            health_risk_events.append(event_row)
            hazard_hook_rows.append(
                {
                    "schema_version": "1.0.0",
                    "tick": int(tick),
                    "subject_id": subject_id,
                    "pollutant_id": pollutant_id,
                    "accumulated_exposure": int(after_value),
                    "hazard_hook_id": "hazard.health_risk_stub",
                    "deterministic_fingerprint": "",
                    "extensions": {
                        "source_process_id": "process.pollution_dispersion_tick",
                        "threshold_crossed": threshold_name,
                        "threshold_value": int(threshold_value),
                        "source_health_risk_event_id": str(event_row.get("event_id", "")).strip(),
                    },
                }
            )

    normalized_events = normalize_health_risk_event_rows(health_risk_events)
    normalized_hazard_hooks = []
    for row in sorted(
        (dict(item) for item in hazard_hook_rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("subject_id", "")),
            str(item.get("pollutant_id", "")),
            str(dict(item.get("extensions") or {}).get("threshold_crossed", "")),
        ),
    ):
        payload = {
            "schema_version": "1.0.0",
            "tick": int(max(0, _as_int(row.get("tick", tick), tick))),
            "subject_id": str(row.get("subject_id", "")).strip(),
            "pollutant_id": str(row.get("pollutant_id", "")).strip(),
            "accumulated_exposure": int(max(0, _as_int(row.get("accumulated_exposure", 0), 0))),
            "hazard_hook_id": str(row.get("hazard_hook_id", "hazard.health_risk_stub")).strip() or "hazard.health_risk_stub",
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
        if (not payload["subject_id"]) or (not payload["pollutant_id"]):
            continue
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        normalized_hazard_hooks.append(payload)

    degraded = bool(deferred_subject_ids)
    return {
        "exposure_state_rows": normalize_pollution_exposure_state_rows(exposure_eval.get("exposure_state_rows")),
        "exposure_increment_rows": [
            dict(row)
            for row in sorted(
                (dict(item) for item in list(exposure_eval.get("exposure_increment_rows") or []) if isinstance(item, Mapping)),
                key=lambda item: (
                    int(max(0, _as_int(item.get("tick", 0), 0))),
                    str(item.get("subject_id", "")),
                    str(item.get("pollutant_id", "")),
                ),
            )
        ],
        "health_risk_event_rows": normalized_events,
        "hazard_hook_rows": list(normalized_hazard_hooks),
        "degraded": degraded,
        "deferred_subject_ids": list(_sorted_tokens(deferred_subject_ids)),
        "degrade_reason": "degrade.pollution.exposure_subject_budget" if degraded else None,
        "cost_units_used": int(len(selected_subject_ids)),
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": int(tick),
                "selected_subject_ids": list(_sorted_tokens(selected_subject_ids)),
                "deferred_subject_ids": list(_sorted_tokens(deferred_subject_ids)),
                "increment_count": int(len(list(exposure_eval.get("exposure_increment_rows") or []))),
                "health_risk_event_ids": [str(row.get("event_id", "")).strip() for row in normalized_events],
            }
        ),
    }


__all__ = [
    "build_health_risk_event_row",
    "evaluate_pollution_exposure_tick",
    "exposure_threshold_rows_by_pollutant",
    "normalize_health_risk_event_rows",
]
