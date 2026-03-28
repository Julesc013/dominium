"""Deterministic InteriorVolumeGraph engine (INT-1)."""

from __future__ import annotations

from typing import Dict, List, Mapping

from core.spatial.spatial_engine import SpatialError, compose_transforms, resolve_world_transform
from core.state.state_machine_engine import StateMachineError, apply_transition, normalize_state_machine
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_INTERIOR_INVALID = "refusal.interior.invalid"
REFUSAL_INTERIOR_PATH_NOT_FOUND = "refusal.interior.path_not_found"
REFUSAL_INTERIOR_STATE_TRANSITION = "refusal.interior.state_transition_invalid"

_PORTAL_BLOCKED_STATES = {"closed", "locked", "damaged", "blocked"}
_PORTAL_OPEN_STATES = {"open", "opening", "unlocked", "permeable"}


class InteriorError(ValueError):
    """Deterministic interior subsystem refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _normalize_transform(row: object) -> dict:
    payload = dict(row or {}) if isinstance(row, dict) else {}
    translation = dict(payload.get("translation_mm") or {})
    rotation = dict(payload.get("rotation_mdeg") or {})
    scale_permille = max(1, _as_int(payload.get("scale_permille", 1000), 1000))
    return {
        "translation_mm": {
            "x": _as_int(translation.get("x", 0), 0),
            "y": _as_int(translation.get("y", 0), 0),
            "z": _as_int(translation.get("z", 0), 0),
        },
        "rotation_mdeg": {
            "yaw": _as_int(rotation.get("yaw", 0), 0),
            "pitch": _as_int(rotation.get("pitch", 0), 0),
            "roll": _as_int(rotation.get("roll", 0), 0),
        },
        "scale_permille": int(scale_permille),
    }


def normalize_interior_volume(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    volume_id = str(payload.get("volume_id", "")).strip()
    parent_spatial_id = str(payload.get("parent_spatial_id", "")).strip()
    volume_type_id = str(payload.get("volume_type_id", "")).strip()
    if not volume_id or not parent_spatial_id or not volume_type_id:
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "interior volume missing required identifiers",
            {
                "volume_id": volume_id,
                "parent_spatial_id": parent_spatial_id,
                "volume_type_id": volume_type_id,
            },
        )
    bounding_shape = dict(payload.get("bounding_shape") or {})
    if not isinstance(bounding_shape, dict) or not str(bounding_shape.get("shape_type", "")).strip():
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "interior volume requires bounding_shape.shape_type",
            {"volume_id": volume_id},
        )
    shape_type = str(bounding_shape.get("shape_type", "")).strip()
    if shape_type not in {"aabb", "convex_hull"}:
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "interior volume bounding shape_type must be aabb or convex_hull",
            {"volume_id": volume_id, "shape_type": shape_type},
        )
    shape_data = bounding_shape.get("shape_data")
    if not isinstance(shape_data, dict):
        shape_data = {}

    return {
        "schema_version": "1.0.0",
        "volume_id": volume_id,
        "parent_spatial_id": parent_spatial_id,
        "local_transform": _normalize_transform(payload.get("local_transform")),
        "bounding_shape": {
            "shape_type": shape_type,
            "shape_data": dict(shape_data),
        },
        "volume_type_id": volume_type_id,
        "tags": _sorted_unique_strings(payload.get("tags")),
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_portal(row: Mapping[str, object], volume_ids: set[str] | None = None) -> dict:
    payload = dict(row or {})
    portal_id = str(payload.get("portal_id", "")).strip()
    from_volume_id = str(payload.get("from_volume_id", "")).strip()
    to_volume_id = str(payload.get("to_volume_id", "")).strip()
    portal_type_id = str(payload.get("portal_type_id", "")).strip()
    state_machine_id = str(payload.get("state_machine_id", "")).strip()
    if not portal_id or not from_volume_id or not to_volume_id or not portal_type_id or not state_machine_id:
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "portal missing required identifiers",
            {
                "portal_id": portal_id,
                "from_volume_id": from_volume_id,
                "to_volume_id": to_volume_id,
                "portal_type_id": portal_type_id,
                "state_machine_id": state_machine_id,
            },
        )
    if volume_ids is not None:
        if from_volume_id not in volume_ids or to_volume_id not in volume_ids:
            raise InteriorError(
                REFUSAL_INTERIOR_INVALID,
                "portal references unknown interior volume",
                {
                    "portal_id": portal_id,
                    "from_volume_id": from_volume_id,
                    "to_volume_id": to_volume_id,
                },
            )
    sealing_coefficient = max(0, _as_int(payload.get("sealing_coefficient", 0), 0))
    return {
        "schema_version": "1.0.0",
        "portal_id": portal_id,
        "from_volume_id": from_volume_id,
        "to_volume_id": to_volume_id,
        "portal_type_id": portal_type_id,
        "state_machine_id": state_machine_id,
        "sealing_coefficient": int(sealing_coefficient),
        "tags": _sorted_unique_strings(payload.get("tags")),
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_interior_graph(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    graph_id = str(payload.get("graph_id", "")).strip()
    if not graph_id:
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "interior graph missing graph_id",
            {},
        )
    volume_ids = _sorted_unique_strings(payload.get("volumes"))
    portal_ids = _sorted_unique_strings(payload.get("portals"))
    return {
        "schema_version": "1.0.0",
        "graph_id": graph_id,
        "volumes": list(volume_ids),
        "portals": list(portal_ids),
        "extensions": dict(payload.get("extensions") or {}),
    }


def volume_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("volume_id", ""))):
        normalized = normalize_interior_volume(row)
        out[str(normalized.get("volume_id", ""))] = normalized
    return out


def portal_rows_by_id(rows: object, *, volume_rows: Mapping[str, object] | None = None) -> Dict[str, dict]:
    volume_ids = set(str(key).strip() for key in dict(volume_rows or {}).keys() if str(key).strip())
    check_volume_ids = volume_ids if volume_ids else None
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("portal_id", ""))):
        normalized = normalize_portal(row, check_volume_ids)
        out[str(normalized.get("portal_id", ""))] = normalized
    return out


def interior_graph_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("graph_id", ""))):
        normalized = normalize_interior_graph(row)
        out[str(normalized.get("graph_id", ""))] = normalized
    return out


def _state_machine_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("machine_id", ""))):
        try:
            normalized = normalize_state_machine(row)
        except StateMachineError:
            continue
        out[str(normalized.get("machine_id", ""))] = normalized
    return out


def _portal_state_id(portal_row: Mapping[str, object], portal_state_rows_by_id: Mapping[str, object] | None) -> str:
    portal = dict(portal_row or {})
    state_rows = dict(portal_state_rows_by_id or {})
    machine_id = str(portal.get("state_machine_id", "")).strip()
    if machine_id:
        machine_row = dict(state_rows.get(machine_id) or {})
        if machine_row:
            try:
                normalized = normalize_state_machine(machine_row)
                token = str(normalized.get("state_id", "")).strip()
                if token:
                    return token
            except StateMachineError:
                pass
    ext = dict(portal.get("extensions") or {})
    token = str(ext.get("state_id", "")).strip()
    return token or "open"


def portal_allows_connectivity(
    portal_row: Mapping[str, object],
    *,
    portal_state_rows_by_id: Mapping[str, object] | None = None,
) -> bool:
    portal = dict(portal_row or {})
    ext = dict(portal.get("extensions") or {})
    permeable_when_closed = bool(ext.get("permeable_when_closed", False)) or ("permeable" in set(_sorted_unique_strings(portal.get("tags"))))
    state_id = _portal_state_id(portal, portal_state_rows_by_id)
    if state_id in _PORTAL_OPEN_STATES:
        return True
    if state_id in _PORTAL_BLOCKED_STATES:
        return bool(permeable_when_closed)
    return bool(permeable_when_closed)


def _graph_portal_adjacency(
    *,
    graph_row: Mapping[str, object],
    volume_index: Mapping[str, object],
    portal_index: Mapping[str, object],
    portal_state_rows_by_id: Mapping[str, object] | None,
) -> Dict[str, List[dict]]:
    graph = normalize_interior_graph(graph_row)
    graph_volume_ids = set(str(item).strip() for item in list(graph.get("volumes") or []) if str(item).strip())
    graph_portal_ids = [str(item).strip() for item in list(graph.get("portals") or []) if str(item).strip()]
    adjacency: Dict[str, List[dict]] = {}
    for volume_id in sorted(graph_volume_ids):
        adjacency[volume_id] = []

    for portal_id in sorted(graph_portal_ids):
        portal = dict(portal_index.get(portal_id) or {})
        if not portal:
            continue
        from_volume_id = str(portal.get("from_volume_id", "")).strip()
        to_volume_id = str(portal.get("to_volume_id", "")).strip()
        if from_volume_id not in set(volume_index.keys()) or to_volume_id not in set(volume_index.keys()):
            continue
        if from_volume_id not in graph_volume_ids or to_volume_id not in graph_volume_ids:
            continue
        if not portal_allows_connectivity(portal, portal_state_rows_by_id=portal_state_rows_by_id):
            continue
        adjacency.setdefault(from_volume_id, []).append({"portal_id": portal_id, "neighbor_volume_id": to_volume_id})
        adjacency.setdefault(to_volume_id, []).append({"portal_id": portal_id, "neighbor_volume_id": from_volume_id})

    for volume_id in sorted(adjacency.keys()):
        adjacency[volume_id] = sorted(
            list(adjacency[volume_id]),
            key=lambda item: (str(item.get("neighbor_volume_id", "")), str(item.get("portal_id", ""))),
        )
    return adjacency


def reachable_volumes(
    *,
    graph_row: Mapping[str, object],
    volume_rows: object,
    portal_rows: object,
    start_volume_id: str,
    portal_state_rows: object | None = None,
    max_visits: int | None = None,
    cost_units_per_query: int = 1,
) -> dict:
    graph = normalize_interior_graph(graph_row)
    volume_index = volume_rows_by_id(volume_rows)
    portal_index = portal_rows_by_id(portal_rows, volume_rows=volume_index)
    state_machine_index = _state_machine_rows_by_id(portal_state_rows)

    start_id = str(start_volume_id).strip()
    if start_id not in set(graph.get("volumes") or []):
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "start volume is not in target interior graph",
            {"graph_id": str(graph.get("graph_id", "")), "start_volume_id": start_id},
        )
    if start_id not in set(volume_index.keys()):
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "start volume row is missing",
            {"graph_id": str(graph.get("graph_id", "")), "start_volume_id": start_id},
        )

    adjacency = _graph_portal_adjacency(
        graph_row=graph,
        volume_index=volume_index,
        portal_index=portal_index,
        portal_state_rows_by_id=state_machine_index,
    )
    ordered_volume_ids = sorted(set(str(item).strip() for item in list(graph.get("volumes") or []) if str(item).strip()))

    visit_limit = len(ordered_volume_ids)
    if max_visits is not None:
        visit_limit = min(visit_limit, max(0, _as_int(max_visits, visit_limit)))

    queue = [start_id]
    seen = {start_id}
    processed = 0
    while queue and processed < visit_limit:
        current = str(queue.pop(0)).strip()
        processed += 1
        for edge in adjacency.get(current, []):
            neighbor = str(edge.get("neighbor_volume_id", "")).strip()
            if not neighbor or neighbor in seen:
                continue
            seen.add(neighbor)
            queue.append(neighbor)

    reachable = sorted(seen)
    deferred_count = max(0, len(ordered_volume_ids) - processed)
    return {
        "graph_id": str(graph.get("graph_id", "")).strip(),
        "start_volume_id": start_id,
        "reachable_volume_ids": reachable,
        "reachable_count": int(len(reachable)),
        "processed_count": int(processed),
        "deferred_count": int(deferred_count),
        "cost_units": int(max(0, _as_int(cost_units_per_query, 1))) * int(max(1, processed)),
        "budget_outcome": "complete" if deferred_count == 0 else "degraded",
    }


def path_exists(
    *,
    graph_row: Mapping[str, object],
    volume_rows: object,
    portal_rows: object,
    from_volume_id: str,
    to_volume_id: str,
    portal_state_rows: object | None = None,
) -> bool:
    from_id = str(from_volume_id).strip()
    to_id = str(to_volume_id).strip()
    if from_id == to_id:
        return True
    reachable = reachable_volumes(
        graph_row=graph_row,
        volume_rows=volume_rows,
        portal_rows=portal_rows,
        start_volume_id=from_id,
        portal_state_rows=portal_state_rows,
        max_visits=None,
    )
    return to_id in set(reachable.get("reachable_volume_ids") or [])


def resolve_volume_world_transform(*, volume_row: Mapping[str, object], spatial_nodes: object) -> dict:
    volume = normalize_interior_volume(volume_row)
    parent_spatial_id = str(volume.get("parent_spatial_id", "")).strip()
    try:
        parent_world = resolve_world_transform(spatial_nodes, target_spatial_id=parent_spatial_id)
    except SpatialError as err:
        raise InteriorError(
            REFUSAL_INTERIOR_INVALID,
            "unable to resolve parent spatial transform for interior volume",
            {
                "volume_id": str(volume.get("volume_id", "")),
                "parent_spatial_id": parent_spatial_id,
                "reason_code": str(err.reason_code),
            },
        ) from err
    world_transform = compose_transforms(
        dict(parent_world.get("world_transform") or {}),
        dict(volume.get("local_transform") or {}),
    )
    return {
        "volume_id": str(volume.get("volume_id", "")).strip(),
        "parent_spatial_id": parent_spatial_id,
        "world_transform": world_transform,
        "depth": int(max(0, _as_int(parent_world.get("depth", 0), 0))) + 1,
    }


def build_connectivity_cache_key(
    *,
    graph_row: Mapping[str, object],
    portal_rows: object,
    portal_state_rows: object | None,
    start_volume_id: str,
) -> str:
    graph = normalize_interior_graph(graph_row)
    portal_index = portal_rows_by_id(portal_rows)
    state_machine_index = _state_machine_rows_by_id(portal_state_rows)
    open_state_by_portal = {}
    for portal_id, portal in sorted(portal_index.items(), key=lambda item: str(item[0])):
        open_state_by_portal[str(portal_id)] = {
            "state_id": _portal_state_id(portal, state_machine_index),
            "allows_connectivity": bool(portal_allows_connectivity(portal, portal_state_rows_by_id=state_machine_index)),
        }
    return canonical_sha256(
        {
            "graph": graph,
            "start_volume_id": str(start_volume_id).strip(),
            "portal_open_state": open_state_by_portal,
        }
    )


def _default_portal_state_machine(portal_row: Mapping[str, object]) -> dict:
    portal = dict(portal_row or {})
    machine_id = str(portal.get("state_machine_id", "")).strip() or "state_machine.portal.unknown"
    return {
        "schema_version": "1.0.0",
        "machine_id": machine_id,
        "machine_type_id": "state_machine.portal",
        "state_id": str((dict(portal.get("extensions") or {})).get("state_id", "open")).strip() or "open",
        "transitions": [
            {
                "transition_id": "transition.portal.open_to_closed",
                "from_state": "open",
                "to_state": "closed",
                "trigger_process_id": "process.portal_close",
                "guard_conditions": {},
                "priority": 10,
                "extensions": {},
            },
            {
                "transition_id": "transition.portal.closed_to_open",
                "from_state": "closed",
                "to_state": "open",
                "trigger_process_id": "process.portal_open",
                "guard_conditions": {},
                "priority": 10,
                "extensions": {},
            },
            {
                "transition_id": "transition.portal.close_locked",
                "from_state": "closed",
                "to_state": "locked",
                "trigger_process_id": "process.portal_lock",
                "guard_conditions": {},
                "priority": 8,
                "extensions": {},
            },
            {
                "transition_id": "transition.portal.locked_closed",
                "from_state": "locked",
                "to_state": "closed",
                "trigger_process_id": "process.portal_unlock",
                "guard_conditions": {},
                "priority": 8,
                "extensions": {},
            },
        ],
        "extensions": {},
    }


def apply_portal_transition(
    *,
    portal_row: Mapping[str, object],
    portal_state_rows: object,
    trigger_process_id: str,
    current_tick: int,
) -> dict:
    portal = normalize_portal(portal_row)
    machine_id = str(portal.get("state_machine_id", "")).strip()
    state_rows = _state_machine_rows_by_id(portal_state_rows)
    machine = dict(state_rows.get(machine_id) or _default_portal_state_machine(portal))
    try:
        transitioned = apply_transition(
            machine,
            trigger_process_id=str(trigger_process_id).strip(),
            current_tick=int(max(0, _as_int(current_tick, 0))),
        )
    except StateMachineError as err:
        raise InteriorError(
            REFUSAL_INTERIOR_STATE_TRANSITION,
            "portal transition is invalid for requested trigger",
            {
                "portal_id": str(portal.get("portal_id", "")),
                "state_machine_id": machine_id,
                "trigger_process_id": str(trigger_process_id),
                "reason_code": str(err.reason_code),
            },
        ) from err

    machine_next = dict(transitioned.get("machine") or {})
    portal_next = dict(portal)
    ext = dict(portal_next.get("extensions") or {})
    ext["state_id"] = str(machine_next.get("state_id", "")).strip() or "open"
    portal_next["extensions"] = ext

    return {
        "portal": portal_next,
        "state_machine": machine_next,
        "applied_transition": dict(transitioned.get("applied_transition") or {}),
    }
