"""POLL-2 deterministic compliance report helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.pollution.dispersion_engine import concentration_field_id_for_pollutant


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _concentration_by_cell(*, field_cell_rows: object, field_id: str) -> Dict[str, int]:
    if not isinstance(field_cell_rows, list):
        field_cell_rows = []
    out: Dict[str, int] = {}
    for row in sorted(
        (dict(item) for item in field_cell_rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("cell_id", "")),
    ):
        if str(row.get("field_id", "")).strip() != str(field_id).strip():
            continue
        cell_id = str(row.get("cell_id", "")).strip()
        if not cell_id:
            continue
        out[cell_id] = int(max(0, _as_int(row.get("value", 0), 0)))
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def build_pollution_compliance_report_row(
    *,
    report_id: str,
    region_id: str,
    pollutant_id: str,
    observed_statistic: str,
    threshold: int,
    status: str,
    tick_range: Mapping[str, object],
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    region_token = str(region_id or "").strip()
    pollutant_token = str(pollutant_id or "").strip()
    stat_token = str(observed_statistic or "avg").strip().lower() or "avg"
    if stat_token not in {"avg", "max"}:
        stat_token = "avg"
    status_token = str(status or "ok").strip().lower() or "ok"
    if status_token not in {"ok", "warning", "violation"}:
        status_token = "ok"
    if (not region_token) or (not pollutant_token):
        return {}

    tick_map = _as_map(tick_range)
    start_tick = int(max(0, _as_int(tick_map.get("start_tick", tick_map.get("from", 0)), 0)))
    end_tick = int(max(start_tick, _as_int(tick_map.get("end_tick", tick_map.get("to", start_tick)), start_tick)))

    payload = {
        "schema_version": "1.0.0",
        "report_id": str(report_id or "").strip(),
        "region_id": region_token,
        "pollutant_id": pollutant_token,
        "observed_statistic": stat_token,
        "threshold": int(max(0, _as_int(threshold, 0))),
        "status": status_token,
        "tick_range": {
            "start_tick": int(start_tick),
            "end_tick": int(end_tick),
        },
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["report_id"]:
        payload["report_id"] = "report.pollution.compliance.{}".format(
            canonical_sha256(
                {
                    "region_id": region_token,
                    "pollutant_id": pollutant_token,
                    "observed_statistic": stat_token,
                    "threshold": int(payload["threshold"]),
                    "tick_range": dict(payload["tick_range"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_pollution_compliance_report_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("region_id", "")),
            str(item.get("pollutant_id", "")),
            str(item.get("report_id", "")),
        ),
    ):
        normalized = build_pollution_compliance_report_row(
            report_id=str(row.get("report_id", "")).strip(),
            region_id=str(row.get("region_id", "")).strip(),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            observed_statistic=str(row.get("observed_statistic", "avg")).strip(),
            threshold=int(max(0, _as_int(row.get("threshold", 0), 0))),
            status=str(row.get("status", "ok")).strip(),
            tick_range=_as_map(row.get("tick_range")),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        report_id = str(normalized.get("report_id", "")).strip()
        if report_id:
            out[report_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def evaluate_pollution_compliance_tick(
    *,
    current_tick: int,
    pollutant_types_by_id: Mapping[str, Mapping[str, object]],
    exposure_thresholds_by_pollutant: Mapping[str, Mapping[str, object]],
    field_cell_rows: object,
    observed_statistic: str = "avg",
    region_cell_map: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    stat_token = str(observed_statistic or "avg").strip().lower() or "avg"
    if stat_token not in {"avg", "max"}:
        stat_token = "avg"

    region_map_input = dict(region_cell_map or {})
    report_rows: List[dict] = []

    for pollutant_id in sorted(
        str(token).strip()
        for token in pollutant_types_by_id.keys()
        if str(token).strip()
    ):
        field_id = concentration_field_id_for_pollutant(pollutant_id)
        if not field_id:
            continue
        concentration_by_cell = _concentration_by_cell(
            field_cell_rows=field_cell_rows,
            field_id=field_id,
        )
        if not concentration_by_cell:
            continue

        threshold_row = dict(exposure_thresholds_by_pollutant.get(pollutant_id) or {})
        warning_threshold = int(max(0, _as_int(threshold_row.get("warning_threshold", 0), 0)))
        critical_threshold = int(
            max(
                warning_threshold,
                _as_int(threshold_row.get("critical_threshold", warning_threshold), warning_threshold),
            )
        )
        if critical_threshold <= 0:
            critical_threshold = int(max(1, warning_threshold))

        active_region_map = {}
        if region_map_input:
            for region_id, cell_ids in region_map_input.items():
                token = str(region_id).strip()
                if not token:
                    continue
                active_region_map[token] = [
                    str(cell_id).strip()
                    for cell_id in list(cell_ids or [])
                    if str(cell_id).strip() in concentration_by_cell
                ]
        if not active_region_map:
            active_region_map = dict(
                (cell_id, [cell_id])
                for cell_id in sorted(concentration_by_cell.keys())
            )

        for region_id in sorted(active_region_map.keys()):
            cells = [
                str(cell_id).strip()
                for cell_id in list(active_region_map.get(region_id) or [])
                if str(cell_id).strip() in concentration_by_cell
            ]
            if not cells:
                continue
            values = [int(max(0, _as_int(concentration_by_cell.get(cell_id, 0), 0))) for cell_id in sorted(cells)]
            if not values:
                continue
            observed_value = int(max(values) if stat_token == "max" else (sum(values) // max(1, len(values))))
            status = "ok"
            threshold = int(warning_threshold)
            if observed_value >= critical_threshold:
                status = "violation"
                threshold = int(critical_threshold)
            elif observed_value >= warning_threshold:
                status = "warning"
                threshold = int(warning_threshold)
            report_row = build_pollution_compliance_report_row(
                report_id="",
                region_id=region_id,
                pollutant_id=pollutant_id,
                observed_statistic=stat_token,
                threshold=int(threshold),
                status=status,
                tick_range={"start_tick": int(tick), "end_tick": int(tick)},
                deterministic_fingerprint="",
                extensions={
                    "observed_value": int(observed_value),
                    "sample_count": int(len(values)),
                    "sample_cell_ids": [str(cell_id) for cell_id in sorted(cells)],
                },
            )
            if report_row:
                report_rows.append(report_row)

    normalized_rows = normalize_pollution_compliance_report_rows(report_rows)
    return {
        "compliance_report_rows": normalized_rows,
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": int(tick),
                "observed_statistic": stat_token,
                "report_rows": [dict(row) for row in normalized_rows],
            }
        ),
    }


__all__ = [
    "build_pollution_compliance_report_row",
    "evaluate_pollution_compliance_tick",
    "normalize_pollution_compliance_report_rows",
]
