"""POLL-2 deterministic pollution measurement helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.pollution.dispersion_engine import concentration_field_id_for_pollutant


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
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def pollution_sensor_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("sensor_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("sensor_types")
    if not isinstance(rows, list):
        rows = []

    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("sensor_type_id", "")),
    ):
        sensor_type_id = str(row.get("sensor_type_id", "")).strip()
        if not sensor_type_id:
            continue
        out[sensor_type_id] = {
            "schema_version": "1.0.0",
            "sensor_type_id": sensor_type_id,
            "description": str(row.get("description", "")).strip(),
            "supported_mediums": _sorted_tokens(row.get("supported_mediums")),
            "supported_pollutants": _sorted_tokens(row.get("supported_pollutants")),
            "requires_calibration": bool(row.get("requires_calibration", False)),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_pollution_measurement_row(
    *,
    measurement_id: str,
    pollutant_id: str,
    spatial_scope_id: str,
    measured_concentration: int,
    instrument_id: str | None,
    calibration_cert_id: str | None,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    pollutant_token = str(pollutant_id or "").strip()
    scope_token = str(spatial_scope_id or "").strip()
    if (not pollutant_token) or (not scope_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "measurement_id": str(measurement_id or "").strip(),
        "pollutant_id": pollutant_token,
        "spatial_scope_id": scope_token,
        "measured_concentration": int(max(0, _as_int(measured_concentration, 0))),
        "instrument_id": None if instrument_id is None else str(instrument_id).strip() or None,
        "calibration_cert_id": None if calibration_cert_id is None else str(calibration_cert_id).strip() or None,
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["measurement_id"]:
        payload["measurement_id"] = "measure.pollution.{}".format(
            canonical_sha256(
                {
                    "pollutant_id": pollutant_token,
                    "spatial_scope_id": scope_token,
                    "instrument_id": payload["instrument_id"],
                    "tick": int(payload["tick"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_pollution_measurement_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("measurement_id", "")),
        ),
    ):
        normalized = build_pollution_measurement_row(
            measurement_id=str(row.get("measurement_id", "")).strip(),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            spatial_scope_id=str(row.get("spatial_scope_id", "")).strip(),
            measured_concentration=int(max(0, _as_int(row.get("measured_concentration", 0), 0))),
            instrument_id=None if row.get("instrument_id") is None else str(row.get("instrument_id", "")).strip() or None,
            calibration_cert_id=None if row.get("calibration_cert_id") is None else str(row.get("calibration_cert_id", "")).strip() or None,
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        measurement_id = str(normalized.get("measurement_id", "")).strip()
        if measurement_id:
            out[measurement_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def sample_pollution_measurement(
    *,
    pollutant_id: str,
    spatial_scope_id: str,
    field_cell_rows: object,
) -> int:
    pollutant_token = str(pollutant_id or "").strip()
    scope_token = str(spatial_scope_id or "").strip()
    if (not pollutant_token) or (not scope_token):
        return 0
    field_id = concentration_field_id_for_pollutant(pollutant_token)
    if not field_id:
        return 0
    if not isinstance(field_cell_rows, list):
        field_cell_rows = []
    for row in sorted(
        (dict(item) for item in field_cell_rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("cell_id", "")),
    ):
        if str(row.get("field_id", "")).strip() != field_id:
            continue
        if str(row.get("cell_id", "")).strip() != scope_token:
            continue
        return int(max(0, _as_int(row.get("value", 0), 0)))
    return 0


__all__ = [
    "build_pollution_measurement_row",
    "normalize_pollution_measurement_rows",
    "pollution_sensor_type_rows_by_id",
    "sample_pollution_measurement",
]
