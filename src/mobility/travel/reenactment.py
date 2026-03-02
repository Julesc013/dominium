"""Deterministic MOB-11 mobility reenactment descriptor helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from ..traffic.traffic_engine import normalize_edge_occupancy_rows
from .travel_engine import normalize_travel_event_rows


_FIDELITY_LEVELS = ("macro", "meso", "micro")


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


def _normalize_fidelity_level(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in _FIDELITY_LEVELS:
        return token
    return "macro"


def _fidelity_index(level: str) -> int:
    token = _normalize_fidelity_level(level)
    return list(_FIDELITY_LEVELS).index(token)


def _clamp_fidelity(*, requested_level: str, max_level: str) -> str:
    requested = _normalize_fidelity_level(requested_level)
    max_token = _normalize_fidelity_level(max_level)
    if _fidelity_index(requested) > _fidelity_index(max_token):
        return max_token
    return requested


def _available_fidelity_levels(max_level: str) -> List[str]:
    max_token = _normalize_fidelity_level(max_level)
    max_index = _fidelity_index(max_token)
    return [level for level in _FIDELITY_LEVELS if _fidelity_index(level) <= max_index]


def _event_rows_for_target(*, rows: object, target_id: str) -> List[dict]:
    normalized = normalize_travel_event_rows(rows)
    token = str(target_id or "").strip()
    if not token:
        return [dict(row) for row in normalized]
    out = []
    for row in normalized:
        ext = _as_map(row.get("extensions"))
        if (
            str(row.get("vehicle_id", "")).strip() == token
            or str(row.get("itinerary_id", "")).strip() == token
            or str(ext.get("target_semantic_id", "")).strip() == token
        ):
            out.append(dict(row))
    return out


def _event_kind_counts(rows: object) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        kind = str(row.get("kind", "incident_stub")).strip() or "incident_stub"
        out[kind] = int(out.get(kind, 0) + 1)
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def _signal_rows_surface(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        machine = _as_map(row.get("state_machine"))
        if not machine and isinstance(row.get("state_machine_id"), str):
            machine = {"state_machine_id": str(row.get("state_machine_id", "")).strip()}
        out.append(
            {
                "signal_id": str(row.get("signal_id", "")).strip(),
                "signal_type_id": str(row.get("signal_type_id", "")).strip(),
                "rule_policy_id": str(row.get("rule_policy_id", "")).strip(),
                "state_machine_id": str(
                    row.get("state_machine_id", "") if row.get("state_machine_id") is not None else machine.get("state_machine_id", "")
                ).strip(),
                "state_id": str(machine.get("state_id", "")).strip(),
            }
        )
    return sorted(
        out,
        key=lambda item: (
            str(item.get("signal_id", "")),
            str(item.get("state_machine_id", "")),
            str(item.get("state_id", "")),
        ),
    )


def compute_mobility_proof_hashes(
    *,
    travel_event_rows: object,
    edge_occupancy_rows: object = None,
    signal_state_rows: object = None,
) -> dict:
    """Compute deterministic mobility proof hashes from event/state surfaces."""

    events = normalize_travel_event_rows(travel_event_rows)
    occupancy = normalize_edge_occupancy_rows(edge_occupancy_rows)
    signal_surface = _signal_rows_surface(signal_state_rows)

    congestion_delay_rows = []
    derailment_rows = []
    for row in events:
        details = _as_map(row.get("details"))
        if str(row.get("kind", "")).strip() == "delay" and str(details.get("reason", "")).strip() == "event.delay.congestion":
            congestion_delay_rows.append(
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "vehicle_id": str(row.get("vehicle_id", "")).strip(),
                    "itinerary_id": str(row.get("itinerary_id", "")).strip(),
                    "edge_id": str(details.get("edge_id", "")).strip(),
                    "edge_index": int(_as_int(details.get("edge_index", 0), 0)),
                    "delta_ticks": int(_as_int(details.get("delta_ticks", 0), 0)),
                    "congestion_ratio_permille": int(_as_int(details.get("congestion_ratio_permille", 0), 0)),
                }
            )
        reason_code = str(details.get("reason_code", "")).strip()
        if str(row.get("kind", "")).strip() == "incident_stub" and reason_code.startswith("incident.derailment."):
            derailment_rows.append(
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "vehicle_id": str(row.get("vehicle_id", "")).strip(),
                    "itinerary_id": str(row.get("itinerary_id", "")).strip(),
                    "reason_code": reason_code,
                    "geometry_id": str(details.get("geometry_id", "")).strip(),
                    "radius_mm": int(_as_int(details.get("radius_mm", 0), 0)),
                    "speed_mm_per_tick": int(_as_int(details.get("speed_mm_per_tick", details.get("velocity", 0)), 0)),
                    "track_wear_permille": int(_as_int(details.get("track_wear_permille", 0), 0)),
                    "friction_permille": int(_as_int(details.get("friction_permille", 0), 0)),
                }
            )

    congestion_surface = {
        "delay_rows": sorted(
            congestion_delay_rows,
            key=lambda item: (
                str(item.get("vehicle_id", "")),
                str(item.get("itinerary_id", "")),
                str(item.get("edge_id", "")),
                int(_as_int(item.get("edge_index", 0), 0)),
                str(item.get("event_id", "")),
            ),
        ),
        "occupancy_rows": [
            {
                "edge_id": str(row.get("edge_id", "")).strip(),
                "capacity_units": int(max(1, _as_int(row.get("capacity_units", 1), 1))),
                "current_occupancy": int(max(0, _as_int(row.get("current_occupancy", 0), 0))),
                "congestion_ratio_permille": int(max(0, _as_int(row.get("congestion_ratio_permille", 0), 0))),
            }
            for row in occupancy
        ],
    }

    return {
        "mobility_event_hash": canonical_sha256(events),
        "congestion_hash": canonical_sha256(congestion_surface),
        "signal_state_hash": canonical_sha256(signal_surface),
        "derailment_hash": canonical_sha256(
            sorted(derailment_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))
        ),
    }


def build_mobility_reenactment_descriptor(
    *,
    descriptor_id: str,
    target_id: str,
    tick_start: int,
    tick_end: int,
    travel_event_rows: object,
    edge_occupancy_rows: object = None,
    signal_state_rows: object = None,
    requested_fidelity_level: str = "macro",
    max_fidelity_level: str = "micro",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    """Build deterministic mobility reenactment descriptor for replay handoff."""

    target_token = str(target_id or "").strip()
    filtered_events = _event_rows_for_target(rows=travel_event_rows, target_id=target_token)
    proof_hashes = compute_mobility_proof_hashes(
        travel_event_rows=filtered_events,
        edge_occupancy_rows=edge_occupancy_rows,
        signal_state_rows=signal_state_rows,
    )
    event_ids = sorted(
        set(str(row.get("event_id", "")).strip() for row in filtered_events if str(row.get("event_id", "")).strip())
    )
    event_stream_hash = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "vehicle_id": str(row.get("vehicle_id", "")).strip(),
                "itinerary_id": str(row.get("itinerary_id", "")).strip(),
                "kind": str(row.get("kind", "")).strip(),
                "details": _canon(_as_map(row.get("details"))),
            }
            for row in filtered_events
        ]
    )
    max_level = _normalize_fidelity_level(max_fidelity_level)
    requested = _normalize_fidelity_level(requested_fidelity_level)
    resolved = _clamp_fidelity(requested_level=requested, max_level=max_level)
    payload = {
        "schema_version": "1.0.0",
        "descriptor_id": str(descriptor_id).strip(),
        "target_id": target_token,
        "tick_range": {
            "start_tick": int(max(0, _as_int(tick_start, 0))),
            "end_tick": int(max(0, _as_int(tick_end, tick_start))),
        },
        "event_ids": list(event_ids),
        "event_kind_counts": _event_kind_counts(filtered_events),
        "available_fidelity_levels": _available_fidelity_levels(max_level),
        "default_fidelity_level": "macro",
        "requested_fidelity_level": requested,
        "resolved_fidelity_level": resolved,
        "event_stream_hash": event_stream_hash,
        "mobility_event_hash": str(proof_hashes.get("mobility_event_hash", "")).strip(),
        "congestion_hash": str(proof_hashes.get("congestion_hash", "")).strip(),
        "signal_state_hash": str(proof_hashes.get("signal_state_hash", "")).strip(),
        "derailment_hash": str(proof_hashes.get("derailment_hash", "")).strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not str(payload.get("descriptor_id", "")).strip():
        payload["descriptor_id"] = "mob.reenactment.{}".format(
            canonical_sha256(
                {
                    "target_id": str(payload.get("target_id", "")),
                    "tick_range": dict(payload.get("tick_range") or {}),
                    "event_stream_hash": str(payload.get("event_stream_hash", "")),
                    "resolved_fidelity_level": str(payload.get("resolved_fidelity_level", "")),
                }
            )[:16]
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_mobility_reenactment_descriptor_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("descriptor_id", ""))):
        descriptor_id = str(row.get("descriptor_id", "")).strip()
        if not descriptor_id:
            continue
        tick_range = _as_map(row.get("tick_range"))
        out[descriptor_id] = build_mobility_reenactment_descriptor(
            descriptor_id=descriptor_id,
            target_id=str(row.get("target_id", "")).strip(),
            tick_start=int(max(0, _as_int(tick_range.get("start_tick", 0), 0))),
            tick_end=int(max(0, _as_int(tick_range.get("end_tick", 0), 0))),
            travel_event_rows=[],
            edge_occupancy_rows=[],
            signal_state_rows=[],
            requested_fidelity_level=str(row.get("requested_fidelity_level", "macro")).strip() or "macro",
            max_fidelity_level=str(row.get("resolved_fidelity_level", "micro")).strip() or "micro",
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


__all__ = [
    "build_mobility_reenactment_descriptor",
    "compute_mobility_proof_hashes",
    "normalize_mobility_reenactment_descriptor_rows",
]
