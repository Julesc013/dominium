"""Deterministic MOB-4 macro travel commitment and tick helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.mobility.travel.itinerary_engine import normalize_itinerary_rows
from src.mobility.traffic import (
    apply_congestion_to_speed,
    build_edge_occupancy,
    compute_congestion_ratio_permille,
    edge_occupancy_rows_by_edge_id,
    normalize_edge_occupancy_rows,
)
from src.mobility.vehicle.vehicle_engine import build_motion_state, normalize_motion_state_rows
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_COMMITMENT_KINDS = {"depart", "arrive", "waypoint"}
_VALID_EVENT_KINDS = {"depart", "arrive", "edge_enter", "edge_exit", "delay", "incident_stub"}


class TravelEngineError(ValueError):
    """Deterministic travel-domain refusal."""

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


def deterministic_travel_commitment_id(
    *,
    vehicle_id: str,
    itinerary_id: str,
    kind: str,
    scheduled_tick: int,
    sequence: int,
) -> str:
    digest = canonical_sha256(
        {
            "vehicle_id": str(vehicle_id or "").strip(),
            "itinerary_id": str(itinerary_id or "").strip(),
            "kind": str(kind or "").strip(),
            "scheduled_tick": int(max(0, _as_int(scheduled_tick, 0))),
            "sequence": int(max(0, _as_int(sequence, 0))),
        }
    )
    return "commitment.travel.{}".format(digest[:16])


def deterministic_travel_event_id(
    *,
    vehicle_id: str,
    itinerary_id: str,
    kind: str,
    tick: int,
    sequence: int,
) -> str:
    digest = canonical_sha256(
        {
            "vehicle_id": str(vehicle_id or "").strip(),
            "itinerary_id": str(itinerary_id or "").strip(),
            "kind": str(kind or "").strip(),
            "tick": int(max(0, _as_int(tick, 0))),
            "sequence": int(max(0, _as_int(sequence, 0))),
        }
    )
    return "event.travel.{}".format(digest[:16])


def build_travel_commitment(
    *,
    commitment_id: str,
    vehicle_id: str,
    itinerary_id: str,
    kind: str,
    scheduled_tick: int,
    status: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind_token = str(kind or "").strip()
    if kind_token not in _VALID_COMMITMENT_KINDS:
        kind_token = "waypoint"
    payload = {
        "schema_version": "1.0.0",
        "commitment_id": str(commitment_id).strip(),
        "vehicle_id": str(vehicle_id).strip(),
        "itinerary_id": str(itinerary_id).strip(),
        "kind": kind_token,
        "scheduled_tick": int(max(0, _as_int(scheduled_tick, 0))),
        "status": str(status or "").strip() or "scheduled",
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_travel_commitment_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("commitment_id", ""))):
        commitment_id = str(row.get("commitment_id", "")).strip()
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        itinerary_id = str(row.get("itinerary_id", "")).strip()
        if (not commitment_id) or (not vehicle_id) or (not itinerary_id):
            continue
        out[commitment_id] = build_travel_commitment(
            commitment_id=commitment_id,
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind=str(row.get("kind", "waypoint")).strip() or "waypoint",
            scheduled_tick=int(max(0, _as_int(row.get("scheduled_tick", 0), 0))),
            status=str(row.get("status", "scheduled")).strip() or "scheduled",
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def build_travel_event(
    *,
    event_id: str,
    tick: int,
    vehicle_id: str,
    itinerary_id: str,
    kind: str,
    details: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind_token = str(kind or "").strip()
    if kind_token not in _VALID_EVENT_KINDS:
        kind_token = "incident_stub"
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id).strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "vehicle_id": str(vehicle_id).strip(),
        "itinerary_id": str(itinerary_id).strip(),
        "kind": kind_token,
        "details": _canon(_as_map(details)),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_travel_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("event_id", ""))),
    ):
        event_id = str(row.get("event_id", "")).strip()
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        itinerary_id = str(row.get("itinerary_id", "")).strip()
        if (not event_id) or (not vehicle_id) or (not itinerary_id):
            continue
        out[event_id] = build_travel_event(
            event_id=event_id,
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind=str(row.get("kind", "incident_stub")).strip() or "incident_stub",
            details=_as_map(row.get("details")),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (_as_int(out[key].get("tick", 0), 0), str(key)))]


def _itinerary_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_itinerary_rows(rows)
    return dict(
        (str(row.get("itinerary_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("itinerary_id", "")).strip()
    )


def _motion_state_rows_by_vehicle_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_motion_state_rows(rows)
    return dict(
        (str(row.get("vehicle_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("vehicle_id", "")).strip()
    )


def _profile_rows(itinerary_row: Mapping[str, object]) -> List[dict]:
    ext = _as_map(itinerary_row.get("extensions"))
    rows = [dict(row) for row in list(ext.get("per_edge_profile") or []) if isinstance(row, Mapping)]
    return sorted(rows, key=lambda row: (_as_int(row.get("sequence", 0), 0), str(row.get("edge_id", ""))))


def _profile_row_for_edge(*, itinerary_row: Mapping[str, object], edge_id: str) -> dict:
    for row in _profile_rows(itinerary_row):
        if str(row.get("edge_id", "")).strip() == str(edge_id).strip():
            return dict(row)
    return {}


def _profile_rows_by_edge_id(itinerary_row: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _profile_rows(itinerary_row):
        edge_id = str(row.get("edge_id", "")).strip()
        if not edge_id:
            continue
        out[edge_id] = dict(row)
    return out


def _profile_eta_ticks(profile_row: Mapping[str, object], default_value: int = 1) -> int:
    return int(max(1, _as_int(profile_row.get("eta_ticks", default_value), default_value)))


def _build_waypoint_commitments(*, vehicle_id: str, itinerary_row: Mapping[str, object]) -> List[dict]:
    itinerary_id = str(itinerary_row.get("itinerary_id", "")).strip()
    departure_tick = int(max(0, _as_int(itinerary_row.get("departure_tick", 0), 0)))
    route_edge_ids = [str(item).strip() for item in list(itinerary_row.get("route_edge_ids") or []) if str(item).strip()]
    profile_by_edge = dict(
        (
            str(row.get("edge_id", "")).strip(),
            dict(row),
        )
        for row in _profile_rows(itinerary_row)
        if str(row.get("edge_id", "")).strip()
    )
    out: List[dict] = []
    cumulative = int(departure_tick)
    for idx, edge_id in enumerate(route_edge_ids):
        profile_row = dict(profile_by_edge.get(edge_id) or {})
        edge_eta = int(max(1, _as_int(profile_row.get("eta_ticks", 1), 1)))
        cumulative += int(edge_eta)
        if idx >= len(route_edge_ids) - 1:
            continue
        commitment_id = deterministic_travel_commitment_id(
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind="waypoint",
            scheduled_tick=int(cumulative),
            sequence=int(idx + 1),
        )
        out.append(
            build_travel_commitment(
                commitment_id=commitment_id,
                vehicle_id=vehicle_id,
                itinerary_id=itinerary_id,
                kind="waypoint",
                scheduled_tick=int(cumulative),
                status="scheduled",
                extensions={
                    "edge_id": edge_id,
                    "edge_index": int(idx),
                },
            )
        )
    return out


def start_macro_travel(
    *,
    vehicle_row: Mapping[str, object],
    motion_state_row: Mapping[str, object],
    itinerary_row: Mapping[str, object],
    current_tick: int,
    process_id: str,
    intent_id: str,
    decision_log_ref: str | None = None,
) -> dict:
    vehicle_id = str(vehicle_row.get("vehicle_id", "")).strip()
    itinerary_id = str(itinerary_row.get("itinerary_id", "")).strip()
    route_edge_ids = [str(item).strip() for item in list(itinerary_row.get("route_edge_ids") or []) if str(item).strip()]
    if not vehicle_id or not itinerary_id or not route_edge_ids:
        raise TravelEngineError(
            "refusal.mob.network_invalid",
            "travel start requires vehicle, itinerary, and route edges",
            {
                "vehicle_id": vehicle_id,
                "itinerary_id": itinerary_id,
            },
        )
    first_edge_id = str(route_edge_ids[0]).strip()
    profile_row = _profile_row_for_edge(itinerary_row=itinerary_row, edge_id=first_edge_id)
    first_edge_eta_ticks = int(max(1, _as_int(profile_row.get("eta_ticks", 1), 1)))
    first_geometry_id = str(profile_row.get("guide_geometry_id", "")).strip() or None
    first_planned_speed_mm_per_tick = int(max(0, _as_int(profile_row.get("allowed_speed_mm_per_tick", 0), 0)))
    arrival_tick = int(max(int(current_tick), _as_int(itinerary_row.get("estimated_arrival_tick", current_tick), current_tick)))

    next_motion_state = build_motion_state(
        vehicle_id=vehicle_id,
        tier="macro",
        macro_state={
            "itinerary_id": itinerary_id,
            "eta_tick": int(arrival_tick),
            "current_edge_id": first_edge_id,
            "current_edge_index": 0,
            "current_node_id": None,
            "progress_fraction_q16": 0,
            "edge_elapsed_ticks": 0,
            "edge_eta_ticks": int(first_edge_eta_ticks),
            "started_tick": int(max(0, _as_int(current_tick, 0))),
            "last_progress_tick": int(max(0, _as_int(current_tick, 0))),
        },
        meso_state=_as_map(motion_state_row.get("meso_state")),
        micro_state=_as_map(motion_state_row.get("micro_state")),
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=_as_map(motion_state_row.get("extensions")),
    )

    depart_commitment = build_travel_commitment(
        commitment_id=deterministic_travel_commitment_id(
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind="depart",
            scheduled_tick=int(max(0, _as_int(current_tick, 0))),
            sequence=0,
        ),
        vehicle_id=vehicle_id,
        itinerary_id=itinerary_id,
        kind="depart",
        scheduled_tick=int(max(0, _as_int(current_tick, 0))),
        status="completed",
        extensions={
            "process_id": str(process_id).strip(),
            "intent_id": str(intent_id).strip(),
            "decision_log_ref": None if decision_log_ref is None else str(decision_log_ref).strip() or None,
        },
    )
    arrive_commitment = build_travel_commitment(
        commitment_id=deterministic_travel_commitment_id(
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind="arrive",
            scheduled_tick=int(arrival_tick),
            sequence=1,
        ),
        vehicle_id=vehicle_id,
        itinerary_id=itinerary_id,
        kind="arrive",
        scheduled_tick=int(arrival_tick),
        status="scheduled",
        extensions={
            "process_id": str(process_id).strip(),
            "intent_id": str(intent_id).strip(),
            "decision_log_ref": None if decision_log_ref is None else str(decision_log_ref).strip() or None,
        },
    )

    depart_event = build_travel_event(
        event_id=deterministic_travel_event_id(
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind="depart",
            tick=int(max(0, _as_int(current_tick, 0))),
            sequence=0,
        ),
        tick=int(max(0, _as_int(current_tick, 0))),
        vehicle_id=vehicle_id,
        itinerary_id=itinerary_id,
        kind="depart",
        details={
            "edge_id": first_edge_id,
            "edge_index": 0,
            "guide_geometry_id": first_geometry_id,
            "planned_speed_mm_per_tick": int(first_planned_speed_mm_per_tick),
        },
        extensions={
            "process_id": str(process_id).strip(),
            "intent_id": str(intent_id).strip(),
            "decision_log_ref": None if decision_log_ref is None else str(decision_log_ref).strip() or None,
            "target_semantic_id": itinerary_id,
            "vehicle_id": vehicle_id,
        },
    )

    return {
        "motion_state": dict(next_motion_state),
        "travel_commitments": [dict(depart_commitment)] + _build_waypoint_commitments(vehicle_id=vehicle_id, itinerary_row=itinerary_row) + [dict(arrive_commitment)],
        "travel_events": [dict(depart_event)],
    }


def _update_commitment_status(
    *,
    commitment_rows: List[dict],
    vehicle_id: str,
    itinerary_id: str,
    kind: str,
    edge_index: int | None,
    status: str,
) -> List[dict]:
    out = [dict(row) for row in list(commitment_rows or []) if isinstance(row, Mapping)]
    for idx, row in enumerate(out):
        if str(row.get("vehicle_id", "")).strip() != str(vehicle_id).strip():
            continue
        if str(row.get("itinerary_id", "")).strip() != str(itinerary_id).strip():
            continue
        if str(row.get("kind", "")).strip() != str(kind).strip():
            continue
        if kind == "waypoint" and edge_index is not None:
            ext = _as_map(row.get("extensions"))
            if int(_as_int(ext.get("edge_index", -1), -1)) != int(edge_index):
                continue
        row["status"] = str(status or "").strip() or "scheduled"
        out[idx] = build_travel_commitment(
            commitment_id=str(row.get("commitment_id", "")).strip(),
            vehicle_id=str(row.get("vehicle_id", "")).strip(),
            itinerary_id=str(row.get("itinerary_id", "")).strip(),
            kind=str(row.get("kind", "")).strip(),
            scheduled_tick=int(max(0, _as_int(row.get("scheduled_tick", 0), 0))),
            status=str(row.get("status", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        break
    return out


def _idle_macro_state(
    *,
    vehicle_id: str,
    motion_state_row: Mapping[str, object],
    current_tick: int,
) -> dict:
    return build_motion_state(
        vehicle_id=vehicle_id,
        tier="macro",
        macro_state={
            "itinerary_id": None,
            "eta_tick": None,
            "current_edge_id": None,
            "current_edge_index": None,
            "current_node_id": None,
            "progress_fraction_q16": 0,
            "edge_elapsed_ticks": 0,
            "edge_eta_ticks": 0,
            "started_tick": None,
            "last_progress_tick": int(max(0, _as_int(current_tick, 0))),
        },
        meso_state=_as_map(motion_state_row.get("meso_state")),
        micro_state=_as_map(motion_state_row.get("micro_state")),
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=_as_map(motion_state_row.get("extensions")),
    )


def tick_macro_travel(
    *,
    itinerary_rows: object,
    motion_state_rows: object,
    travel_commitment_rows: object,
    travel_event_rows: object,
    current_tick: int,
    max_updates: int,
    forced_deferred_vehicle_ids: object = None,
    edge_occupancy_rows: object = None,
    congestion_policy_row: Mapping[str, object] | None = None,
) -> dict:
    itinerary_by_id = _itinerary_rows_by_id(itinerary_rows)
    motion_by_vehicle = _motion_state_rows_by_vehicle_id(motion_state_rows)
    commitments = normalize_travel_commitment_rows(travel_commitment_rows)
    events = normalize_travel_event_rows(travel_event_rows)
    event_index = int(len(events))
    congestion_policy = dict(congestion_policy_row or {})
    congestion_policy_id = str(congestion_policy.get("congestion_policy_id", "cong.default_linear")).strip() or "cong.default_linear"

    occupancy_by_edge = edge_occupancy_rows_by_edge_id(edge_occupancy_rows)
    for edge_id in list(occupancy_by_edge.keys()):
        row = dict(occupancy_by_edge.get(edge_id) or {})
        occupancy_by_edge[edge_id] = build_edge_occupancy(
            edge_id=edge_id,
            capacity_units=int(max(1, _as_int(row.get("capacity_units", 1), 1))),
            current_occupancy=0,
            extensions=_as_map(row.get("extensions")),
        )

    def _ensure_occupancy_row(edge_id: str) -> dict:
        edge_token = str(edge_id or "").strip()
        if not edge_token:
            return build_edge_occupancy(edge_id="", capacity_units=1, current_occupancy=0, extensions={})
        row = dict(occupancy_by_edge.get(edge_token) or {})
        if not row:
            row = build_edge_occupancy(
                edge_id=edge_token,
                capacity_units=1,
                current_occupancy=0,
                extensions={},
            )
            occupancy_by_edge[edge_token] = dict(row)
            return dict(row)
        return dict(row)

    def _remaining_base_eta_ticks(*, route_edge_ids: List[str], profile_by_edge: Mapping[str, dict], start_index: int) -> int:
        total = 0
        for idx in range(int(max(0, _as_int(start_index, 0))), len(route_edge_ids)):
            edge_id = str(route_edge_ids[idx]).strip()
            if not edge_id:
                continue
            total += _profile_eta_ticks(dict(profile_by_edge.get(edge_id) or {}), 1)
        return int(max(0, total))

    active_vehicle_ids = []
    for vehicle_id, row in sorted(motion_by_vehicle.items(), key=lambda item: str(item[0])):
        itinerary_value = _as_map(row.get("macro_state")).get("itinerary_id")
        itinerary_token = str(itinerary_value).strip() if itinerary_value is not None else ""
        if itinerary_token:
            active_vehicle_ids.append(vehicle_id)

    # Rehydrate occupancy from current active macro travel rows so depart/start transitions are reflected.
    for vehicle_id in active_vehicle_ids:
        motion_row = dict(motion_by_vehicle.get(vehicle_id) or {})
        macro = _as_map(motion_row.get("macro_state"))
        itinerary_value = macro.get("itinerary_id")
        itinerary_id = str(itinerary_value).strip() if itinerary_value is not None else ""
        itinerary_row = dict(itinerary_by_id.get(itinerary_id) or {})
        route_edge_ids = [str(item).strip() for item in list(itinerary_row.get("route_edge_ids") or []) if str(item).strip()]
        if not route_edge_ids:
            continue
        edge_index = int(max(0, _as_int(macro.get("current_edge_index", 0), 0)))
        if edge_index >= len(route_edge_ids):
            edge_index = len(route_edge_ids) - 1
        current_edge_id = str(macro.get("current_edge_id", "")).strip() or str(route_edge_ids[edge_index]).strip()
        if not current_edge_id:
            continue
        occupancy_row = _ensure_occupancy_row(current_edge_id)
        occupancy_by_edge[current_edge_id] = build_edge_occupancy(
            edge_id=current_edge_id,
            capacity_units=int(max(1, _as_int(occupancy_row.get("capacity_units", 1), 1))),
            current_occupancy=int(max(0, _as_int(occupancy_row.get("current_occupancy", 0), 0)) + 1),
            extensions=_as_map(occupancy_row.get("extensions")),
        )

    forced_deferred = set(_sorted_tokens(forced_deferred_vehicle_ids))
    processed: List[str] = []
    deferred: List[str] = []
    congestion_delay_rows: List[dict] = []
    for vehicle_id in active_vehicle_ids:
        if vehicle_id in forced_deferred:
            deferred.append(vehicle_id)
            continue
        if len(processed) >= int(max(0, _as_int(max_updates, len(active_vehicle_ids)))):
            deferred.append(vehicle_id)
            continue
        processed.append(vehicle_id)
        motion_row = dict(motion_by_vehicle.get(vehicle_id) or {})
        macro = _as_map(motion_row.get("macro_state"))
        itinerary_value = macro.get("itinerary_id")
        itinerary_id = str(itinerary_value).strip() if itinerary_value is not None else ""
        itinerary_row = dict(itinerary_by_id.get(itinerary_id) or {})
        route_edge_ids = [str(item).strip() for item in list(itinerary_row.get("route_edge_ids") or []) if str(item).strip()]
        if not itinerary_row or not route_edge_ids:
            current_edge_token = str(macro.get("current_edge_id", "")).strip()
            if current_edge_token:
                current_edge_row = _ensure_occupancy_row(current_edge_token)
                occupancy_by_edge[current_edge_token] = build_edge_occupancy(
                    edge_id=current_edge_token,
                    capacity_units=int(max(1, _as_int(current_edge_row.get("capacity_units", 1), 1))),
                    current_occupancy=int(max(0, _as_int(current_edge_row.get("current_occupancy", 0), 0) - 1)),
                    extensions=_as_map(current_edge_row.get("extensions")),
                )
            motion_by_vehicle[vehicle_id] = _idle_macro_state(
                vehicle_id=vehicle_id,
                motion_state_row=motion_row,
                current_tick=int(current_tick),
            )
            continue

        edge_index = int(max(0, _as_int(macro.get("current_edge_index", 0), 0)))
        if edge_index >= len(route_edge_ids):
            edge_index = len(route_edge_ids) - 1
        current_edge_id = str(route_edge_ids[edge_index]).strip()
        profile_by_edge = _profile_rows_by_edge_id(itinerary_row)
        profile_row = dict(profile_by_edge.get(current_edge_id) or _profile_row_for_edge(itinerary_row=itinerary_row, edge_id=current_edge_id))
        base_edge_eta_ticks = _profile_eta_ticks(
            profile_row,
            int(max(1, _as_int(macro.get("base_edge_eta_ticks", 1), 1))),
        )
        planned_speed_mm_per_tick = int(max(1, _as_int(profile_row.get("allowed_speed_mm_per_tick", 1), 1)))
        occupancy_row = _ensure_occupancy_row(current_edge_id)
        capacity_units = int(max(1, _as_int(occupancy_row.get("capacity_units", 1), 1)))
        current_occupancy = int(max(0, _as_int(occupancy_row.get("current_occupancy", 0), 0)))
        congestion_ratio_permille = compute_congestion_ratio_permille(
            current_occupancy=current_occupancy,
            capacity_units=capacity_units,
        )
        speed_eval = apply_congestion_to_speed(
            base_speed_mm_per_tick=int(planned_speed_mm_per_tick),
            congestion_ratio_permille=int(congestion_ratio_permille),
            congestion_policy_row=congestion_policy,
        )
        multiplier_permille = int(max(1, _as_int(speed_eval.get("multiplier_permille", 1000), 1000)))
        edge_eta_ticks = int(max(1, (int(base_edge_eta_ticks) * int(multiplier_permille) + 999) // 1000))
        congestion_delay_ticks = int(max(0, int(edge_eta_ticks) - int(base_edge_eta_ticks)))
        logged_edge_index = int(_as_int(macro.get("congestion_logged_edge_index", -1), -1))
        edge_elapsed_ticks = int(max(0, _as_int(macro.get("edge_elapsed_ticks", 0), 0))) + 1
        if int(congestion_delay_ticks) > 0 and int(logged_edge_index) != int(edge_index):
            events.append(
                build_travel_event(
                    event_id=deterministic_travel_event_id(
                        vehicle_id=vehicle_id,
                        itinerary_id=itinerary_id,
                        kind="delay",
                        tick=int(current_tick),
                        sequence=int(event_index),
                    ),
                    tick=int(current_tick),
                    vehicle_id=vehicle_id,
                    itinerary_id=itinerary_id,
                    kind="delay",
                    details={
                        "reason": "event.delay.congestion",
                        "edge_id": current_edge_id,
                        "edge_index": int(edge_index),
                        "delta_ticks": int(congestion_delay_ticks),
                        "congestion_ratio_permille": int(congestion_ratio_permille),
                        "multiplier_permille": int(multiplier_permille),
                        "capacity_units": int(capacity_units),
                        "current_occupancy": int(current_occupancy),
                    },
                    extensions={
                        "target_semantic_id": itinerary_id,
                        "vehicle_id": vehicle_id,
                        "congestion_policy_id": congestion_policy_id,
                    },
                )
            )
            congestion_delay_rows.append(
                {
                    "vehicle_id": vehicle_id,
                    "itinerary_id": itinerary_id,
                    "edge_id": current_edge_id,
                    "edge_index": int(edge_index),
                    "delta_ticks": int(congestion_delay_ticks),
                    "congestion_ratio_permille": int(congestion_ratio_permille),
                    "multiplier_permille": int(multiplier_permille),
                    "capacity_units": int(capacity_units),
                    "current_occupancy": int(current_occupancy),
                    "congestion_policy_id": congestion_policy_id,
                }
            )
            event_index += 1
            logged_edge_index = int(edge_index)
        elif int(congestion_delay_ticks) <= 0:
            logged_edge_index = -1

        if edge_elapsed_ticks >= edge_eta_ticks:
            # Close current edge and transition.
            events.append(
                build_travel_event(
                    event_id=deterministic_travel_event_id(
                        vehicle_id=vehicle_id,
                        itinerary_id=itinerary_id,
                        kind="edge_exit",
                        tick=int(current_tick),
                        sequence=int(event_index),
                    ),
                    tick=int(current_tick),
                    vehicle_id=vehicle_id,
                    itinerary_id=itinerary_id,
                    kind="edge_exit",
                    details={
                        "edge_id": current_edge_id,
                        "edge_index": int(edge_index),
                        "guide_geometry_id": str(profile_row.get("guide_geometry_id", "")).strip() or None,
                        "planned_speed_mm_per_tick": int(planned_speed_mm_per_tick),
                        "congestion_ratio_permille": int(congestion_ratio_permille),
                        "multiplier_permille": int(multiplier_permille),
                        "capacity_units": int(capacity_units),
                        "current_occupancy": int(current_occupancy),
                    },
                    extensions={
                        "target_semantic_id": itinerary_id,
                        "vehicle_id": vehicle_id,
                        "congestion_policy_id": congestion_policy_id,
                    },
                )
            )
            event_index += 1
            occupancy_row = _ensure_occupancy_row(current_edge_id)
            occupancy_by_edge[current_edge_id] = build_edge_occupancy(
                edge_id=current_edge_id,
                capacity_units=int(max(1, _as_int(occupancy_row.get("capacity_units", 1), 1))),
                current_occupancy=int(max(0, _as_int(occupancy_row.get("current_occupancy", 0), 0) - 1)),
                extensions=_as_map(occupancy_row.get("extensions")),
            )
            commitments = _update_commitment_status(
                commitment_rows=commitments,
                vehicle_id=vehicle_id,
                itinerary_id=itinerary_id,
                kind="waypoint",
                edge_index=int(edge_index),
                status="completed",
            )
            next_edge_index = int(edge_index + 1)
            if next_edge_index >= len(route_edge_ids):
                commitments = _update_commitment_status(
                    commitment_rows=commitments,
                    vehicle_id=vehicle_id,
                    itinerary_id=itinerary_id,
                    kind="arrive",
                    edge_index=None,
                    status="completed",
                )
                events.append(
                    build_travel_event(
                        event_id=deterministic_travel_event_id(
                            vehicle_id=vehicle_id,
                            itinerary_id=itinerary_id,
                            kind="arrive",
                            tick=int(current_tick),
                            sequence=int(event_index),
                        ),
                        tick=int(current_tick),
                        vehicle_id=vehicle_id,
                        itinerary_id=itinerary_id,
                        kind="arrive",
                        details={
                            "edge_index": int(edge_index),
                            "route_edge_count": int(len(route_edge_ids)),
                            "edge_id": current_edge_id,
                            "guide_geometry_id": str(profile_row.get("guide_geometry_id", "")).strip() or None,
                            "planned_speed_mm_per_tick": int(planned_speed_mm_per_tick),
                            "congestion_ratio_permille": int(congestion_ratio_permille),
                            "multiplier_permille": int(multiplier_permille),
                        },
                        extensions={
                            "target_semantic_id": itinerary_id,
                            "vehicle_id": vehicle_id,
                            "congestion_policy_id": congestion_policy_id,
                        },
                    )
                )
                event_index += 1
                motion_by_vehicle[vehicle_id] = _idle_macro_state(
                    vehicle_id=vehicle_id,
                    motion_state_row=motion_row,
                    current_tick=int(current_tick),
                )
                continue

            next_edge_id = str(route_edge_ids[next_edge_index]).strip()
            next_profile = dict(profile_by_edge.get(next_edge_id) or _profile_row_for_edge(itinerary_row=itinerary_row, edge_id=next_edge_id))
            next_base_edge_eta_ticks = _profile_eta_ticks(next_profile, 1)
            next_planned_speed_mm_per_tick = int(max(1, _as_int(next_profile.get("allowed_speed_mm_per_tick", 1), 1)))
            next_occupancy_row = _ensure_occupancy_row(next_edge_id)
            next_capacity_units = int(max(1, _as_int(next_occupancy_row.get("capacity_units", 1), 1)))
            next_current_occupancy = int(max(0, _as_int(next_occupancy_row.get("current_occupancy", 0), 0) + 1))
            occupancy_by_edge[next_edge_id] = build_edge_occupancy(
                edge_id=next_edge_id,
                capacity_units=int(next_capacity_units),
                current_occupancy=int(next_current_occupancy),
                extensions=_as_map(next_occupancy_row.get("extensions")),
            )
            next_congestion_ratio_permille = compute_congestion_ratio_permille(
                current_occupancy=int(next_current_occupancy),
                capacity_units=int(next_capacity_units),
            )
            next_speed_eval = apply_congestion_to_speed(
                base_speed_mm_per_tick=int(next_planned_speed_mm_per_tick),
                congestion_ratio_permille=int(next_congestion_ratio_permille),
                congestion_policy_row=congestion_policy,
            )
            next_multiplier_permille = int(max(1, _as_int(next_speed_eval.get("multiplier_permille", 1000), 1000)))
            next_eta_ticks = int(max(1, (int(next_base_edge_eta_ticks) * int(next_multiplier_permille) + 999) // 1000))
            next_congestion_delay_ticks = int(max(0, int(next_eta_ticks) - int(next_base_edge_eta_ticks)))
            events.append(
                build_travel_event(
                    event_id=deterministic_travel_event_id(
                        vehicle_id=vehicle_id,
                        itinerary_id=itinerary_id,
                        kind="edge_enter",
                        tick=int(current_tick),
                        sequence=int(event_index),
                    ),
                    tick=int(current_tick),
                    vehicle_id=vehicle_id,
                    itinerary_id=itinerary_id,
                    kind="edge_enter",
                    details={
                        "edge_id": next_edge_id,
                        "edge_index": int(next_edge_index),
                        "guide_geometry_id": str(next_profile.get("guide_geometry_id", "")).strip() or None,
                        "planned_speed_mm_per_tick": int(next_planned_speed_mm_per_tick),
                        "congestion_ratio_permille": int(next_congestion_ratio_permille),
                        "multiplier_permille": int(next_multiplier_permille),
                        "capacity_units": int(next_capacity_units),
                        "current_occupancy": int(next_current_occupancy),
                    },
                    extensions={
                        "target_semantic_id": itinerary_id,
                        "vehicle_id": vehicle_id,
                        "congestion_policy_id": congestion_policy_id,
                    },
                )
            )
            event_index += 1
            if int(next_congestion_delay_ticks) > 0:
                events.append(
                    build_travel_event(
                        event_id=deterministic_travel_event_id(
                            vehicle_id=vehicle_id,
                            itinerary_id=itinerary_id,
                            kind="delay",
                            tick=int(current_tick),
                            sequence=int(event_index),
                        ),
                        tick=int(current_tick),
                        vehicle_id=vehicle_id,
                        itinerary_id=itinerary_id,
                        kind="delay",
                        details={
                            "reason": "event.delay.congestion",
                            "edge_id": next_edge_id,
                            "edge_index": int(next_edge_index),
                            "delta_ticks": int(next_congestion_delay_ticks),
                            "congestion_ratio_permille": int(next_congestion_ratio_permille),
                            "multiplier_permille": int(next_multiplier_permille),
                            "capacity_units": int(next_capacity_units),
                            "current_occupancy": int(next_current_occupancy),
                        },
                        extensions={
                            "target_semantic_id": itinerary_id,
                            "vehicle_id": vehicle_id,
                            "congestion_policy_id": congestion_policy_id,
                        },
                    )
                )
                congestion_delay_rows.append(
                    {
                        "vehicle_id": vehicle_id,
                        "itinerary_id": itinerary_id,
                        "edge_id": next_edge_id,
                        "edge_index": int(next_edge_index),
                        "delta_ticks": int(next_congestion_delay_ticks),
                        "congestion_ratio_permille": int(next_congestion_ratio_permille),
                        "multiplier_permille": int(next_multiplier_permille),
                        "capacity_units": int(next_capacity_units),
                        "current_occupancy": int(next_current_occupancy),
                        "congestion_policy_id": congestion_policy_id,
                    }
                )
                event_index += 1
                logged_edge_index = int(next_edge_index)
            else:
                logged_edge_index = -1
            eta_tick = int(
                int(current_tick)
                + int(next_eta_ticks)
                + int(_remaining_base_eta_ticks(route_edge_ids=route_edge_ids, profile_by_edge=profile_by_edge, start_index=int(next_edge_index + 1)))
            )
            motion_by_vehicle[vehicle_id] = build_motion_state(
                vehicle_id=vehicle_id,
                tier="macro",
                macro_state={
                    "itinerary_id": itinerary_id,
                    "eta_tick": int(max(int(current_tick), int(eta_tick))),
                    "current_edge_id": next_edge_id,
                    "current_edge_index": int(next_edge_index),
                    "current_node_id": None,
                    "progress_fraction_q16": 0,
                    "edge_elapsed_ticks": 0,
                    "edge_eta_ticks": int(next_eta_ticks),
                    "base_edge_eta_ticks": int(next_base_edge_eta_ticks),
                    "started_tick": _as_int(macro.get("started_tick", current_tick), current_tick),
                    "last_progress_tick": int(current_tick),
                    "planned_speed_mm_per_tick": int(next_planned_speed_mm_per_tick),
                    "congestion_policy_id": congestion_policy_id,
                    "congestion_ratio_permille": int(next_congestion_ratio_permille),
                    "congestion_multiplier_permille": int(next_multiplier_permille),
                    "congestion_delay_ticks": int(next_congestion_delay_ticks),
                    "edge_capacity_units": int(next_capacity_units),
                    "edge_current_occupancy": int(next_current_occupancy),
                    "congestion_logged_edge_index": int(logged_edge_index),
                },
                meso_state=_as_map(motion_row.get("meso_state")),
                micro_state=_as_map(motion_row.get("micro_state")),
                last_update_tick=int(current_tick),
                extensions=_as_map(motion_row.get("extensions")),
            )
            continue

        progress_fraction_q16 = int((int(edge_elapsed_ticks) * 65535) // int(max(1, edge_eta_ticks)))
        eta_tick = int(
            int(current_tick)
            + int(max(0, int(edge_eta_ticks) - int(edge_elapsed_ticks)))
            + int(_remaining_base_eta_ticks(route_edge_ids=route_edge_ids, profile_by_edge=profile_by_edge, start_index=int(edge_index + 1)))
        )
        motion_by_vehicle[vehicle_id] = build_motion_state(
            vehicle_id=vehicle_id,
            tier="macro",
            macro_state={
                "itinerary_id": itinerary_id,
                "eta_tick": int(max(int(current_tick), int(eta_tick))),
                "current_edge_id": current_edge_id,
                "current_edge_index": int(edge_index),
                "current_node_id": None,
                "progress_fraction_q16": int(max(0, min(65535, progress_fraction_q16))),
                "edge_elapsed_ticks": int(edge_elapsed_ticks),
                "edge_eta_ticks": int(edge_eta_ticks),
                "base_edge_eta_ticks": int(base_edge_eta_ticks),
                "started_tick": _as_int(macro.get("started_tick", current_tick), current_tick),
                "last_progress_tick": int(current_tick),
                "planned_speed_mm_per_tick": int(planned_speed_mm_per_tick),
                "congestion_policy_id": congestion_policy_id,
                "congestion_ratio_permille": int(congestion_ratio_permille),
                "congestion_multiplier_permille": int(multiplier_permille),
                "congestion_delay_ticks": int(congestion_delay_ticks),
                "edge_capacity_units": int(capacity_units),
                "edge_current_occupancy": int(current_occupancy),
                "congestion_logged_edge_index": int(logged_edge_index),
            },
            meso_state=_as_map(motion_row.get("meso_state")),
            micro_state=_as_map(motion_row.get("micro_state")),
            last_update_tick=int(current_tick),
            extensions=_as_map(motion_row.get("extensions")),
        )

    motion_rows_out = [dict(motion_by_vehicle[key]) for key in sorted(motion_by_vehicle.keys())]
    return {
        "motion_state_rows": motion_rows_out,
        "travel_commitments": normalize_travel_commitment_rows(commitments),
        "travel_events": normalize_travel_event_rows(events),
        "edge_occupancy_rows": normalize_edge_occupancy_rows(
            [dict(occupancy_by_edge[key]) for key in sorted(occupancy_by_edge.keys())]
        ),
        "congestion_delay_rows": [
            dict(row)
            for row in sorted(
                congestion_delay_rows,
                key=lambda row: (
                    str(row.get("vehicle_id", "")),
                    str(row.get("itinerary_id", "")),
                    str(row.get("edge_id", "")),
                    _as_int(row.get("edge_index", 0), 0),
                ),
            )
        ],
        "processed_vehicle_ids": _sorted_tokens(processed),
        "deferred_vehicle_ids": _sorted_tokens(deferred),
        "budget_outcome": "degraded" if deferred else "complete",
    }


__all__ = [
    "TravelEngineError",
    "build_travel_commitment",
    "build_travel_event",
    "deterministic_travel_commitment_id",
    "deterministic_travel_event_id",
    "normalize_travel_commitment_rows",
    "normalize_travel_event_rows",
    "start_macro_travel",
    "tick_macro_travel",
]
