"""POLL-0 deterministic pollution bookkeeping helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_POLLUTION_INVALID = "REFUSAL_POLLUTION_INVALID"
_ORIGIN_KINDS = {"reaction", "fire", "leak", "industrial"}


class PollutionError(RuntimeError):
    """Raised when pollution payload normalization fails hard."""


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _normalize_origin_kind(origin_kind: object) -> str:
    token = str(origin_kind or "").strip().lower()
    if token in _ORIGIN_KINDS:
        return token
    return "industrial"


def build_pollution_source_event(
    *,
    source_event_id: str,
    tick: int,
    origin_kind: str,
    origin_id: str,
    pollutant_id: str,
    emitted_mass: int,
    spatial_scope_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    pollutant_token = str(pollutant_id or "").strip()
    scope_token = str(spatial_scope_id or "").strip()
    origin_token = str(origin_id or "").strip()
    if (not pollutant_token) or (not scope_token) or (not origin_token):
        return {}
    event_id = str(source_event_id or "").strip()
    if not event_id:
        event_id = "event.pollution.emit.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, _as_int(tick, 0))),
                    "origin_kind": _normalize_origin_kind(origin_kind),
                    "origin_id": origin_token,
                    "pollutant_id": pollutant_token,
                    "emitted_mass": int(max(0, _as_int(emitted_mass, 0))),
                    "spatial_scope_id": scope_token,
                }
            )[:16]
        )
    payload = {
        "schema_version": "1.0.0",
        "source_event_id": event_id,
        "tick": int(max(0, _as_int(tick, 0))),
        "origin_kind": _normalize_origin_kind(origin_kind),
        "origin_id": origin_token,
        "pollutant_id": pollutant_token,
        "emitted_mass": int(max(0, _as_int(emitted_mass, 0))),
        "spatial_scope_id": scope_token,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_pollution_source_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("source_event_id", item.get("event_id", ""))),
            str(item.get("origin_id", "")),
        ),
    ):
        normalized = build_pollution_source_event(
            source_event_id=(
                str(row.get("source_event_id", "")).strip()
                or str(row.get("event_id", "")).strip()
            ),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            origin_kind=str(row.get("origin_kind", "industrial")).strip()
            or "industrial",
            origin_id=str(row.get("origin_id", "")).strip(),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            emitted_mass=int(max(0, _as_int(row.get("emitted_mass", 0), 0))),
            spatial_scope_id=(
                str(row.get("spatial_scope_id", "")).strip()
                or str(row.get("region_id", "")).strip()
            ),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        source_event_id = str(normalized.get("source_event_id", "")).strip()
        if source_event_id:
            out[source_event_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_pollution_total_row(
    *,
    region_id: str,
    pollutant_id: str,
    pollutant_mass_total: int,
    last_update_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    region_token = str(region_id or "").strip()
    pollutant_token = str(pollutant_id or "").strip()
    if (not region_token) or (not pollutant_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "region_id": region_token,
        "pollutant_id": pollutant_token,
        "pollutant_mass_total": int(max(0, _as_int(pollutant_mass_total, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_pollution_total_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("region_id", "")),
            str(item.get("pollutant_id", "")),
        ),
    ):
        normalized = build_pollution_total_row(
            region_id=str(row.get("region_id", "")).strip(),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            pollutant_mass_total=int(max(0, _as_int(row.get("pollutant_mass_total", 0), 0))),
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        region_id = str(normalized.get("region_id", "")).strip()
        pollutant_id = str(normalized.get("pollutant_id", "")).strip()
        if region_id and pollutant_id:
            out["{}::{}".format(region_id, pollutant_id)] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def pollution_totals_by_key(rows: object) -> Dict[str, dict]:
    normalized = normalize_pollution_total_rows(rows)
    out: Dict[str, dict] = {}
    for row in normalized:
        region_id = str(row.get("region_id", "")).strip()
        pollutant_id = str(row.get("pollutant_id", "")).strip()
        if region_id and pollutant_id:
            out["{}::{}".format(region_id, pollutant_id)] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


__all__ = [
    "REFUSAL_POLLUTION_INVALID",
    "PollutionError",
    "build_pollution_source_event",
    "build_pollution_total_row",
    "normalize_pollution_source_event_rows",
    "normalize_pollution_total_rows",
    "pollution_totals_by_key",
]
