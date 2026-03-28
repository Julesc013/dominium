"""Deterministic MOB-4 itinerary planning helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from core.graph.routing_engine import RoutingError, query_route_result
from mobility.network.mobility_network_engine import (
    REFUSAL_MOBILITY_NETWORK_INVALID,
    REFUSAL_MOBILITY_NO_ROUTE,
    filter_graph_by_switch_state,
)
from mobility.vehicle.vehicle_engine import (
    REFUSAL_MOBILITY_SPEC_NONCOMPLIANT,
    evaluate_vehicle_edge_compatibility,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_SPEED_POLICIES = {
    "speed_policy.spec_based",
    "speed_policy.curvature_based",
    "speed_policy.conservative",
    "speed_policy.admin_override",
}

_DEFAULT_ALLOWED_SPEED_MM_PER_TICK = 1000
_CURVATURE_WARN_RADIUS_MM = 12000


class ItineraryError(ValueError):
    """Deterministic itinerary-domain refusal."""

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


def speed_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("speed_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("speed_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("speed_policy_id", ""))):
        speed_policy_id = str(row.get("speed_policy_id", "")).strip()
        if not speed_policy_id:
            continue
        out[speed_policy_id] = {
            "schema_version": "1.0.0",
            "speed_policy_id": speed_policy_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_itinerary_id(
    *,
    vehicle_id: str,
    graph_id: str,
    route_edge_ids: object,
    speed_policy_id: str,
    departure_tick: int,
) -> str:
    digest = canonical_sha256(
        {
            "vehicle_id": str(vehicle_id or "").strip(),
            "graph_id": str(graph_id or "").strip(),
            "route_edge_ids": _sorted_tokens(route_edge_ids),
            "speed_policy_id": str(speed_policy_id or "").strip(),
            "departure_tick": int(max(0, _as_int(departure_tick, 0))),
        }
    )
    return "itinerary.{}".format(digest[:16])


def build_itinerary(
    *,
    itinerary_id: str,
    vehicle_id: str,
    route_edge_ids: object,
    route_node_ids: object,
    departure_tick: int,
    estimated_arrival_tick: int,
    speed_policy_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    policy_token = str(speed_policy_id or "").strip() or "speed_policy.spec_based"
    if policy_token not in _VALID_SPEED_POLICIES:
        policy_token = "speed_policy.spec_based"
    payload = {
        "schema_version": "1.0.0",
        "itinerary_id": str(itinerary_id).strip(),
        "vehicle_id": str(vehicle_id).strip(),
        "route_edge_ids": [str(item).strip() for item in list(route_edge_ids or []) if str(item).strip()],
        "route_node_ids": [str(item).strip() for item in list(route_node_ids or []) if str(item).strip()],
        "departure_tick": int(max(0, _as_int(departure_tick, 0))),
        "estimated_arrival_tick": int(max(0, _as_int(estimated_arrival_tick, 0))),
        "speed_policy_id": policy_token,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_itinerary_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("itinerary_id", ""))):
        itinerary_id = str(row.get("itinerary_id", "")).strip()
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        route_edge_ids = [str(item).strip() for item in list(row.get("route_edge_ids") or []) if str(item).strip()]
        route_node_ids = [str(item).strip() for item in list(row.get("route_node_ids") or []) if str(item).strip()]
        if (not itinerary_id) or (not vehicle_id) or (not route_edge_ids):
            continue
        out[itinerary_id] = build_itinerary(
            itinerary_id=itinerary_id,
            vehicle_id=vehicle_id,
            route_edge_ids=route_edge_ids,
            route_node_ids=route_node_ids,
            departure_tick=int(max(0, _as_int(row.get("departure_tick", 0), 0))),
            estimated_arrival_tick=int(max(0, _as_int(row.get("estimated_arrival_tick", 0), 0))),
            speed_policy_id=str(row.get("speed_policy_id", "speed_policy.spec_based")).strip() or "speed_policy.spec_based",
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def _spec_numeric(spec_row: Mapping[str, object], keys: Tuple[str, ...]) -> int | None:
    parameters = _as_map(spec_row.get("parameters"))
    for key in keys:
        value = parameters.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
    return None


def _edge_length_mm(
    *,
    edge_row: Mapping[str, object],
    geometry_metric_rows_by_geometry_id: Mapping[str, dict],
) -> int:
    edge_payload = _as_map(edge_row.get("payload"))
    length_mm = _as_int(_as_map(edge_payload.get("extensions")).get("length_mm", 0), 0)
    if int(length_mm) > 0:
        return int(length_mm)
    geometry_id = str(edge_payload.get("guide_geometry_id", "")).strip()
    metric_row = dict(geometry_metric_rows_by_geometry_id.get(geometry_id) or {})
    return int(max(0, _as_int(metric_row.get("length_mm", 0), 0)))


def _edge_spec_speed_limit_mm_per_tick(
    *,
    edge_row: Mapping[str, object],
    guide_geometry_rows_by_id: Mapping[str, dict],
    spec_rows_by_id: Mapping[str, dict],
) -> int | None:
    edge_payload = _as_map(edge_row.get("payload"))
    edge_spec_id = str(edge_payload.get("spec_id", "")).strip()
    geometry_id = str(edge_payload.get("guide_geometry_id", "")).strip()
    geometry_row = dict(guide_geometry_rows_by_id.get(geometry_id) or {})
    geometry_spec_id = str(geometry_row.get("spec_id", "")).strip()
    spec_ids = []
    if edge_spec_id:
        spec_ids.append(edge_spec_id)
    if geometry_spec_id:
        spec_ids.append(geometry_spec_id)
    if not spec_ids:
        return None
    for spec_id in sorted(set(spec_ids)):
        spec_row = dict(spec_rows_by_id.get(spec_id) or {})
        if not spec_row:
            continue
        mm_per_tick = _spec_numeric(spec_row, ("max_speed_mm_per_tick", "max_speed", "speed_limit_mm_per_tick"))
        if mm_per_tick is not None and int(mm_per_tick) > 0:
            return int(mm_per_tick)
        mmps = _spec_numeric(spec_row, ("max_speed_mmps", "speed_limit_mmps"))
        if mmps is not None and int(mmps) > 0:
            return int(mmps)
        kph = _spec_numeric(spec_row, ("max_speed_kph", "speed_limit_kph"))
        if kph is not None and int(kph) > 0:
            converted = int((int(kph) * 1000000) // 3600)
            if converted > 0:
                return int(converted)
    return None


def _curvature_speed_limit_mm_per_tick(
    *,
    edge_row: Mapping[str, object],
    geometry_metric_rows_by_geometry_id: Mapping[str, dict],
) -> int | None:
    edge_payload = _as_map(edge_row.get("payload"))
    geometry_id = str(edge_payload.get("guide_geometry_id", "")).strip()
    metric_row = dict(geometry_metric_rows_by_geometry_id.get(geometry_id) or {})
    radius_mm = int(max(0, _as_int(metric_row.get("min_curvature_radius_mm", 0), 0)))
    if int(radius_mm) <= 0:
        return None
    # Deterministic heuristic cap derived from curvature radius.
    return int(max(200, min(3000, int(radius_mm) // 4)))


def _allowed_speed_mm_per_tick(
    *,
    edge_row: Mapping[str, object],
    speed_policy_id: str,
    guide_geometry_rows_by_id: Mapping[str, dict],
    geometry_metric_rows_by_geometry_id: Mapping[str, dict],
    spec_rows_by_id: Mapping[str, dict],
) -> int:
    policy = str(speed_policy_id or "").strip() or "speed_policy.spec_based"
    if policy not in _VALID_SPEED_POLICIES:
        policy = "speed_policy.spec_based"

    spec_limit = _edge_spec_speed_limit_mm_per_tick(
        edge_row=edge_row,
        guide_geometry_rows_by_id=guide_geometry_rows_by_id,
        spec_rows_by_id=spec_rows_by_id,
    )
    curve_limit = _curvature_speed_limit_mm_per_tick(
        edge_row=edge_row,
        geometry_metric_rows_by_geometry_id=geometry_metric_rows_by_geometry_id,
    )

    base = int(spec_limit if spec_limit is not None else _DEFAULT_ALLOWED_SPEED_MM_PER_TICK)
    if policy == "speed_policy.curvature_based":
        if curve_limit is not None:
            base = int(min(base, int(curve_limit)))
    elif policy == "speed_policy.conservative":
        if curve_limit is not None:
            base = int(min(base, int(curve_limit)))
        base = int(max(150, (int(base) * 3) // 4))
    elif policy == "speed_policy.admin_override":
        # Meta-law/admin profile may authorize this policy; keep deterministic hard floor/ceiling.
        base = int(max(300, min(5000, int(base))))

    return int(max(1, base))


def _edge_eta_ticks(
    *,
    edge_row: Mapping[str, object],
    speed_policy_id: str,
    guide_geometry_rows_by_id: Mapping[str, dict],
    geometry_metric_rows_by_geometry_id: Mapping[str, dict],
    spec_rows_by_id: Mapping[str, dict],
) -> Tuple[int, int, int]:
    length_mm = _edge_length_mm(
        edge_row=edge_row,
        geometry_metric_rows_by_geometry_id=geometry_metric_rows_by_geometry_id,
    )
    allowed_speed_mm_per_tick = _allowed_speed_mm_per_tick(
        edge_row=edge_row,
        speed_policy_id=speed_policy_id,
        guide_geometry_rows_by_id=guide_geometry_rows_by_id,
        geometry_metric_rows_by_geometry_id=geometry_metric_rows_by_geometry_id,
        spec_rows_by_id=spec_rows_by_id,
    )
    if int(length_mm) <= 0:
        return 1, int(allowed_speed_mm_per_tick), int(length_mm)
    ticks = int((int(length_mm) + int(allowed_speed_mm_per_tick) - 1) // int(allowed_speed_mm_per_tick))
    return int(max(1, ticks)), int(allowed_speed_mm_per_tick), int(length_mm)


def plan_itinerary(
    *,
    vehicle_row: Mapping[str, object],
    graph_row: Mapping[str, object],
    from_node_id: str,
    to_node_id: str,
    current_tick: int,
    departure_tick: int | None,
    speed_policy_id: str,
    route_policy_id: str,
    constraints_row: Mapping[str, object] | None,
    partition_row: Mapping[str, object] | None,
    switch_state_machine_rows: object,
    guide_geometry_rows_by_id: Mapping[str, dict],
    geometry_metric_rows_by_geometry_id: Mapping[str, dict],
    spec_rows_by_id: Mapping[str, dict],
    cache_state: Mapping[str, object] | None = None,
    max_cache_entries: int = 128,
    cost_units_per_query: int = 1,
) -> dict:
    vehicle = dict(vehicle_row or {})
    vehicle_id = str(vehicle.get("vehicle_id", "")).strip()
    if not vehicle_id:
        raise ItineraryError(
            REFUSAL_MOBILITY_NETWORK_INVALID,
            "vehicle_row is missing vehicle_id",
            {"vehicle_id": vehicle_id},
        )
    graph = dict(graph_row or {})
    graph_id = str(graph.get("graph_id", "")).strip()
    if not graph_id:
        raise ItineraryError(
            REFUSAL_MOBILITY_NETWORK_INVALID,
            "graph_row is missing graph_id",
            {},
        )
    from_token = str(from_node_id).strip()
    to_token = str(to_node_id).strip()
    if (not from_token) or (not to_token):
        raise ItineraryError(
            REFUSAL_MOBILITY_NETWORK_INVALID,
            "from_node_id and to_node_id are required",
            {"from_node_id": from_token, "to_node_id": to_token},
        )

    filtered_graph = filter_graph_by_switch_state(
        graph_row=graph,
        switch_state_machine_rows=switch_state_machine_rows,
    )
    route_policy_token = str(route_policy_id).strip() or "route.shortest_delay"
    route_policy_row = {
        "policy_id": route_policy_token,
        "allow_multi_hop": False if route_policy_token == "route.direct_only" else True,
        "optimization_metric": "min_cost_units" if route_policy_token == "route.min_cost_units" else "delay_ticks",
        "tie_break_policy": "edge_id_lexicographic",
        "extensions": {},
    }

    try:
        route_runtime_payload = query_route_result(
            graph_row=filtered_graph,
            routing_policy_row=route_policy_row,
            from_node_id=from_token,
            to_node_id=to_token,
            constraints_row=dict(constraints_row or {}),
            partition_row=dict(partition_row or {}),
            cache_state=dict(cache_state or {}),
            max_cache_entries=int(max(0, _as_int(max_cache_entries, 128))),
            cost_units_per_query=int(max(1, _as_int(cost_units_per_query, 1))),
        )
    except RoutingError as exc:
        raise ItineraryError(
            REFUSAL_MOBILITY_NO_ROUTE,
            str(exc),
            dict(getattr(exc, "details", {}) or {}),
        )

    route_result = dict(route_runtime_payload.get("route_result") or {})
    route_edge_ids = [str(item).strip() for item in list(route_result.get("path_edge_ids") or []) if str(item).strip()]
    route_node_ids = [str(item).strip() for item in list(route_result.get("path_node_ids") or []) if str(item).strip()]
    if not route_edge_ids:
        raise ItineraryError(
            REFUSAL_MOBILITY_NO_ROUTE,
            "route query returned empty edge path",
            {
                "graph_id": graph_id,
                "from_node_id": from_token,
                "to_node_id": to_token,
            },
        )

    edge_rows_by_id = {}
    for edge in list(filtered_graph.get("edges") or []):
        if not isinstance(edge, Mapping):
            continue
        edge_id = str(edge.get("edge_id", "")).strip()
        if edge_id:
            edge_rows_by_id[edge_id] = dict(edge)

    speed_policy_token = str(speed_policy_id).strip() or "speed_policy.spec_based"
    if speed_policy_token not in _VALID_SPEED_POLICIES:
        speed_policy_token = "speed_policy.spec_based"

    per_edge_rows: List[dict] = []
    total_ticks = 0
    for edge_id in route_edge_ids:
        edge_row = dict(edge_rows_by_id.get(edge_id) or {})
        if not edge_row:
            raise ItineraryError(
                REFUSAL_MOBILITY_NETWORK_INVALID,
                "route references missing edge_id '{}'".format(edge_id),
                {"edge_id": edge_id, "graph_id": graph_id},
            )
        compatibility = evaluate_vehicle_edge_compatibility(
            vehicle_row=vehicle,
            target_edge_row=edge_row,
            spec_rows_by_id=spec_rows_by_id,
            guide_geometry_rows_by_id=guide_geometry_rows_by_id,
            geometry_metric_rows_by_geometry_id=geometry_metric_rows_by_geometry_id,
        )
        if not bool(compatibility.get("compatible", False)):
            raise ItineraryError(
                REFUSAL_MOBILITY_SPEC_NONCOMPLIANT,
                "vehicle is not compatible with route edge '{}'".format(edge_id),
                {
                    "vehicle_id": vehicle_id,
                    "edge_id": edge_id,
                    "compatibility": dict(compatibility),
                },
            )
        edge_ticks, allowed_speed_mm_per_tick, length_mm = _edge_eta_ticks(
            edge_row=edge_row,
            speed_policy_id=speed_policy_token,
            guide_geometry_rows_by_id=guide_geometry_rows_by_id,
            geometry_metric_rows_by_geometry_id=geometry_metric_rows_by_geometry_id,
            spec_rows_by_id=spec_rows_by_id,
        )
        edge_payload = _as_map(edge_row.get("payload"))
        geometry_id = str(edge_payload.get("guide_geometry_id", "")).strip()
        geometry_row = dict(guide_geometry_rows_by_id.get(geometry_id) or {})
        metric_row = dict(geometry_metric_rows_by_geometry_id.get(geometry_id) or {})
        curvature_bands = _as_map(metric_row.get("curvature_bands"))
        high_band_count = int(max(0, _as_int(curvature_bands.get("high", 0), 0)))
        min_curvature_radius_mm = int(max(0, _as_int(metric_row.get("min_curvature_radius_mm", 0), 0)))
        edge_spec_id = str(edge_payload.get("spec_id", "")).strip()
        geometry_spec_id = str(geometry_row.get("spec_id", "")).strip()
        total_ticks += int(edge_ticks)
        per_edge_rows.append(
            {
                "edge_id": edge_id,
                "guide_geometry_id": geometry_id or None,
                "spec_id": edge_spec_id or geometry_spec_id or None,
                "length_mm": int(length_mm),
                "allowed_speed_mm_per_tick": int(allowed_speed_mm_per_tick),
                "eta_ticks": int(edge_ticks),
                "min_curvature_radius_mm": int(min_curvature_radius_mm),
                "curvature_high_band_count": int(high_band_count),
                "curvature_warning": bool(
                    high_band_count > 0
                    or (0 < min_curvature_radius_mm <= int(_CURVATURE_WARN_RADIUS_MM))
                ),
                "spec_warning": bool((not edge_spec_id) and (not geometry_spec_id)),
            }
        )

    depart_tick = int(max(int(current_tick), int(_as_int(departure_tick, current_tick))))
    arrival_tick = int(max(depart_tick, depart_tick + int(total_ticks)))
    curvature_warning_edge_ids = sorted(
        str(row.get("edge_id", "")).strip()
        for row in per_edge_rows
        if bool(row.get("curvature_warning", False)) and str(row.get("edge_id", "")).strip()
    )
    spec_warning_edge_ids = sorted(
        str(row.get("edge_id", "")).strip()
        for row in per_edge_rows
        if bool(row.get("spec_warning", False)) and str(row.get("edge_id", "")).strip()
    )
    route_result_with_profile = dict(route_result)
    route_result_with_profile["itinerary_id"] = ""
    route_result_with_profile["speed_policy_id"] = speed_policy_token
    route_result_with_profile["estimated_arrival_tick"] = int(arrival_tick)
    route_result_with_profile["per_edge_profile"] = [dict(row) for row in per_edge_rows]
    route_result_with_profile["curvature_warning_edge_ids"] = list(curvature_warning_edge_ids)
    route_result_with_profile["spec_warning_edge_ids"] = list(spec_warning_edge_ids)
    itinerary_id = deterministic_itinerary_id(
        vehicle_id=vehicle_id,
        graph_id=graph_id,
        route_edge_ids=route_edge_ids,
        speed_policy_id=speed_policy_token,
        departure_tick=depart_tick,
    )
    itinerary_row = build_itinerary(
        itinerary_id=itinerary_id,
        vehicle_id=vehicle_id,
        route_edge_ids=route_edge_ids,
        route_node_ids=route_node_ids,
        departure_tick=depart_tick,
        estimated_arrival_tick=arrival_tick,
        speed_policy_id=speed_policy_token,
        extensions={
            "graph_id": graph_id,
            "route_policy_id": route_policy_token,
            "route_result": dict(route_result_with_profile, itinerary_id=itinerary_id),
            "cache_hit": bool(route_runtime_payload.get("cache_hit", False)),
            "route_cost_units": int(max(0, _as_int(route_runtime_payload.get("route_cost_units", 0), 0))),
            "cross_shard_route_plan": dict(route_runtime_payload.get("cross_shard_route_plan") or {}),
            "per_edge_profile": [dict(row) for row in per_edge_rows],
        },
    )
    return {
        "itinerary": itinerary_row,
        "route_result": dict(route_result_with_profile, itinerary_id=itinerary_id),
        "cache_state": dict(route_runtime_payload.get("cache_state") or {}),
        "cache_hit": bool(route_runtime_payload.get("cache_hit", False)),
        "route_cost_units": int(max(0, _as_int(route_runtime_payload.get("route_cost_units", 0), 0))),
        "cross_shard_route_plan": dict(route_runtime_payload.get("cross_shard_route_plan") or {}),
    }


__all__ = [
    "ItineraryError",
    "build_itinerary",
    "deterministic_itinerary_id",
    "normalize_itinerary_rows",
    "plan_itinerary",
    "speed_policy_rows_by_id",
]
