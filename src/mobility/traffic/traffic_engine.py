"""Deterministic MOB-5 meso traffic occupancy and congestion helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.core.graph.network_graph_engine import normalize_network_graph
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MOBILITY_RESERVATION_CONFLICT = "refusal.mob.reservation_conflict"

_VALID_EVENT_KINDS = {"depart", "arrive", "edge_enter", "edge_exit"}
_DEFAULT_CONGESTION_POLICY_ID = "cong.default_linear"


class TrafficEngineError(ValueError):
    """Deterministic meso traffic refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
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


def congestion_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("congestion_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("congestion_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("congestion_policy_id", ""))):
        policy_id = str(row.get("congestion_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "congestion_policy_id": policy_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def resolve_congestion_policy(
    *,
    requested_policy_id: str | None,
    policy_rows_by_id: Mapping[str, dict] | None,
) -> dict:
    rows = dict(policy_rows_by_id or {})
    token = str(requested_policy_id or "").strip() or _DEFAULT_CONGESTION_POLICY_ID
    if rows:
        if token not in rows:
            token = sorted(rows.keys())[0]
        return dict(rows.get(token) or {})
    return {
        "schema_version": "1.0.0",
        "congestion_policy_id": token,
        "schema_ref": "dominium.schema.mobility.congestion_policy@1.0.0",
        "extensions": {
            "multiplier_formula_id": "formula.linear_over_capacity",
            "parameters": {"k_per_over_ratio_permille": 500},
        },
    }


def _policy_k_permille(policy_row: Mapping[str, object]) -> int:
    ext = _as_map(policy_row.get("extensions"))
    params = _as_map(ext.get("parameters"))
    return int(max(0, _as_int(params.get("k_per_over_ratio_permille", 500), 500)))


def resolve_edge_capacity_units(*, edge_row: Mapping[str, object], default_capacity_units: int = 1) -> int:
    edge = dict(edge_row or {})
    payload = _as_map(edge.get("payload"))
    payload_capacity = payload.get("capacity_units")
    if payload_capacity is not None:
        return int(max(1, _as_int(payload_capacity, default_capacity_units)))
    raw_capacity = edge.get("capacity")
    if raw_capacity is not None:
        return int(max(1, _as_int(raw_capacity, default_capacity_units)))
    return int(max(1, _as_int(default_capacity_units, 1)))


def compute_congestion_ratio_permille(*, current_occupancy: int, capacity_units: int) -> int:
    current = int(max(0, _as_int(current_occupancy, 0)))
    capacity = int(max(1, _as_int(capacity_units, 1)))
    return int((int(current) * 1000) // int(capacity))


def congestion_multiplier_permille(
    *,
    congestion_ratio_permille: int,
    congestion_policy_row: Mapping[str, object] | None,
) -> int:
    ratio = int(max(0, _as_int(congestion_ratio_permille, 0)))
    if ratio <= 1000:
        return 1000
    over = int(ratio - 1000)
    k_permille = _policy_k_permille(dict(congestion_policy_row or {}))
    return int(1000 + ((int(over) * int(k_permille)) // 1000))


def apply_congestion_to_speed(
    *,
    base_speed_mm_per_tick: int,
    congestion_ratio_permille: int,
    congestion_policy_row: Mapping[str, object] | None,
) -> dict:
    base_speed = int(max(1, _as_int(base_speed_mm_per_tick, 1)))
    multiplier_permille = int(
        max(
            1,
            congestion_multiplier_permille(
                congestion_ratio_permille=int(congestion_ratio_permille),
                congestion_policy_row=congestion_policy_row,
            ),
        )
    )
    adjusted_speed = int(max(1, (int(base_speed) * 1000) // int(multiplier_permille)))
    return {
        "base_speed_mm_per_tick": int(base_speed),
        "adjusted_speed_mm_per_tick": int(adjusted_speed),
        "multiplier_permille": int(multiplier_permille),
        "congestion_ratio_permille": int(max(0, _as_int(congestion_ratio_permille, 0))),
    }


def build_edge_occupancy(
    *,
    edge_id: str,
    capacity_units: int,
    current_occupancy: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    edge_token = str(edge_id or "").strip()
    capacity = int(max(1, _as_int(capacity_units, 1)))
    occupancy = int(max(0, _as_int(current_occupancy, 0)))
    ratio_permille = compute_congestion_ratio_permille(
        current_occupancy=occupancy,
        capacity_units=capacity,
    )
    payload = {
        "schema_version": "1.0.0",
        "edge_id": edge_token,
        "capacity_units": int(capacity),
        "current_occupancy": int(occupancy),
        "congestion_ratio": float(ratio_permille) / 1000.0,
        "deterministic_fingerprint": "",
        "extensions": _canon(dict(_as_map(extensions), congestion_ratio_permille=int(ratio_permille))),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_edge_occupancy_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(row.get("edge_id", "")).strip()
        if not edge_id:
            continue
        out[edge_id] = build_edge_occupancy(
            edge_id=edge_id,
            capacity_units=int(max(1, _as_int(row.get("capacity_units", 1), 1))),
            current_occupancy=int(max(0, _as_int(row.get("current_occupancy", 0), 0))),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def edge_occupancy_rows_by_edge_id(rows: object) -> Dict[str, dict]:
    return dict(
        (str(row.get("edge_id", "")).strip(), dict(row))
        for row in normalize_edge_occupancy_rows(rows)
        if str(row.get("edge_id", "")).strip()
    )


def ensure_edge_occupancy_rows(
    *,
    edge_occupancy_rows: object,
    graph_row: Mapping[str, object],
) -> List[dict]:
    graph = normalize_network_graph(graph_row)
    occupancy_by_edge = edge_occupancy_rows_by_edge_id(edge_occupancy_rows)
    for edge in sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        if edge_id in occupancy_by_edge:
            row = dict(occupancy_by_edge.get(edge_id) or {})
            occupancy_by_edge[edge_id] = build_edge_occupancy(
                edge_id=edge_id,
                capacity_units=resolve_edge_capacity_units(edge_row=edge),
                current_occupancy=int(max(0, _as_int(row.get("current_occupancy", 0), 0))),
                extensions=_as_map(row.get("extensions")),
            )
            continue
        occupancy_by_edge[edge_id] = build_edge_occupancy(
            edge_id=edge_id,
            capacity_units=resolve_edge_capacity_units(edge_row=edge),
            current_occupancy=0,
            extensions={},
        )
    return [dict(occupancy_by_edge[key]) for key in sorted(occupancy_by_edge.keys())]


def _transition_rows(travel_event_rows: object) -> List[dict]:
    out: List[dict] = []
    for row in sorted(
        (dict(item) for item in list(travel_event_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("vehicle_id", "")),
            _as_int(item.get("tick", 0), 0),
            str(item.get("event_id", "")),
        ),
    ):
        kind = str(row.get("kind", "")).strip()
        if kind not in _VALID_EVENT_KINDS:
            continue
        details = _as_map(row.get("details"))
        edge_id = str(details.get("edge_id", "")).strip()
        if not edge_id:
            continue
        if kind in {"depart", "edge_enter"}:
            delta = 1
        elif kind in {"edge_exit", "arrive"}:
            delta = -1
        else:
            continue
        out.append(
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "vehicle_id": str(row.get("vehicle_id", "")).strip(),
                "edge_id": edge_id,
                "delta": int(delta),
            }
        )
    return [dict(row) for row in out if str(row.get("event_id", "")).strip()]


def apply_traffic_events_to_occupancy(
    *,
    edge_occupancy_rows: object,
    graph_row: Mapping[str, object],
    travel_event_rows: object,
    max_events: int,
) -> dict:
    occupancies = ensure_edge_occupancy_rows(
        edge_occupancy_rows=edge_occupancy_rows,
        graph_row=graph_row,
    )
    occupancy_by_edge = edge_occupancy_rows_by_edge_id(occupancies)
    transitions = _transition_rows(travel_event_rows)
    max_events_norm = int(max(0, _as_int(max_events, 0)))
    processed_event_ids: List[str] = []
    deferred_event_ids: List[str] = []

    for idx, transition in enumerate(transitions):
        event_id = str(transition.get("event_id", "")).strip()
        if not event_id:
            continue
        if idx >= int(max_events_norm):
            deferred_event_ids.append(event_id)
            continue
        edge_id = str(transition.get("edge_id", "")).strip()
        row = dict(occupancy_by_edge.get(edge_id) or {})
        if not row:
            continue
        current = int(max(0, _as_int(row.get("current_occupancy", 0), 0)))
        next_occupancy = int(max(0, int(current) + int(_as_int(transition.get("delta", 0), 0))))
        occupancy_by_edge[edge_id] = build_edge_occupancy(
            edge_id=edge_id,
            capacity_units=int(max(1, _as_int(row.get("capacity_units", 1), 1))),
            current_occupancy=int(next_occupancy),
            extensions=_as_map(row.get("extensions")),
        )
        processed_event_ids.append(event_id)

    return {
        "edge_occupancy_rows": [dict(occupancy_by_edge[key]) for key in sorted(occupancy_by_edge.keys())],
        "processed_event_ids": _sorted_tokens(processed_event_ids),
        "deferred_event_ids": _sorted_tokens(deferred_event_ids),
        "cost_units": int(len(processed_event_ids)),
        "budget_outcome": "degraded" if deferred_event_ids else "complete",
    }


def deterministic_reservation_id(
    *,
    vehicle_id: str,
    edge_id: str,
    start_tick: int,
    end_tick: int,
) -> str:
    digest = canonical_sha256(
        {
            "vehicle_id": str(vehicle_id or "").strip(),
            "edge_id": str(edge_id or "").strip(),
            "start_tick": int(max(0, _as_int(start_tick, 0))),
            "end_tick": int(max(0, _as_int(end_tick, 0))),
        }
    )
    return "reservation.mob.{}".format(digest[:16])


def build_reservation(
    *,
    reservation_id: str,
    vehicle_id: str,
    edge_id: str,
    start_tick: int,
    end_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    start_value = int(max(0, _as_int(start_tick, 0)))
    end_value = int(max(start_value, _as_int(end_tick, start_value)))
    payload = {
        "schema_version": "1.0.0",
        "reservation_id": str(reservation_id or "").strip(),
        "vehicle_id": str(vehicle_id or "").strip(),
        "edge_id": str(edge_id or "").strip(),
        "start_tick": int(start_value),
        "end_tick": int(end_value),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_reservation_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("reservation_id", ""))):
        reservation_id = str(row.get("reservation_id", "")).strip()
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        edge_id = str(row.get("edge_id", "")).strip()
        if (not reservation_id) or (not vehicle_id) or (not edge_id):
            continue
        out[reservation_id] = build_reservation(
            reservation_id=reservation_id,
            vehicle_id=vehicle_id,
            edge_id=edge_id,
            start_tick=int(max(0, _as_int(row.get("start_tick", 0), 0))),
            end_tick=int(max(0, _as_int(row.get("end_tick", row.get("start_tick", 0)), 0))),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def _overlap(
    *,
    start_tick: int,
    end_tick: int,
    other_start_tick: int,
    other_end_tick: int,
) -> bool:
    return not (int(end_tick) < int(other_start_tick) or int(start_tick) > int(other_end_tick))


def reserve_edge_capacity(
    *,
    reservation_rows: object,
    edge_occupancy_rows: object,
    vehicle_id: str,
    edge_id: str,
    start_tick: int,
    end_tick: int,
) -> dict:
    reservations = normalize_reservation_rows(reservation_rows)
    edge_token = str(edge_id or "").strip()
    vehicle_token = str(vehicle_id or "").strip()
    if (not edge_token) or (not vehicle_token):
        raise TrafficEngineError(
            REFUSAL_MOBILITY_RESERVATION_CONFLICT,
            "reservation requires non-empty vehicle_id and edge_id",
            {"vehicle_id": vehicle_token, "edge_id": edge_token},
        )
    start_value = int(max(0, _as_int(start_tick, 0)))
    end_value = int(max(start_value, _as_int(end_tick, start_value)))
    occupancy_by_edge = edge_occupancy_rows_by_edge_id(edge_occupancy_rows)
    capacity_units = int(max(1, _as_int((dict(occupancy_by_edge.get(edge_token) or {})).get("capacity_units", 1), 1)))
    conflicting = []
    for row in reservations:
        if str(row.get("edge_id", "")).strip() != edge_token:
            continue
        if not _overlap(
            start_tick=start_value,
            end_tick=end_value,
            other_start_tick=int(max(0, _as_int(row.get("start_tick", 0), 0))),
            other_end_tick=int(max(0, _as_int(row.get("end_tick", 0), 0))),
        ):
            continue
        conflicting.append(dict(row))
    conflicting = sorted(conflicting, key=lambda row: (str(row.get("vehicle_id", "")), str(row.get("reservation_id", ""))))
    if int(len(conflicting)) >= int(capacity_units):
        raise TrafficEngineError(
            REFUSAL_MOBILITY_RESERVATION_CONFLICT,
            "reservation conflicts with deterministic edge capacity",
            {
                "vehicle_id": vehicle_token,
                "edge_id": edge_token,
                "capacity_units": int(capacity_units),
                "conflicting_reservation_ids": _sorted_tokens([row.get("reservation_id") for row in conflicting]),
            },
        )
    reservation_id = deterministic_reservation_id(
        vehicle_id=vehicle_token,
        edge_id=edge_token,
        start_tick=int(start_value),
        end_tick=int(end_value),
    )
    new_row = build_reservation(
        reservation_id=reservation_id,
        vehicle_id=vehicle_token,
        edge_id=edge_token,
        start_tick=int(start_value),
        end_tick=int(end_value),
        extensions={},
    )
    reservations = normalize_reservation_rows(list(reservations) + [dict(new_row)])
    return {
        "reservations": list(reservations),
        "reservation": dict(new_row),
        "capacity_units": int(capacity_units),
        "conflicting_count": int(len(conflicting)),
    }


__all__ = [
    "REFUSAL_MOBILITY_RESERVATION_CONFLICT",
    "TrafficEngineError",
    "apply_congestion_to_speed",
    "apply_traffic_events_to_occupancy",
    "build_edge_occupancy",
    "compute_congestion_ratio_permille",
    "congestion_multiplier_permille",
    "congestion_policy_rows_by_id",
    "deterministic_reservation_id",
    "edge_occupancy_rows_by_edge_id",
    "ensure_edge_occupancy_rows",
    "build_reservation",
    "normalize_edge_occupancy_rows",
    "normalize_reservation_rows",
    "reserve_edge_capacity",
    "resolve_congestion_policy",
    "resolve_edge_capacity_units",
]
