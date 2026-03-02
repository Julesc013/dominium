"""Deterministic MOB-3 vehicle assembly and motion-state helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MOBILITY_SPEC_NONCOMPLIANT = "refusal.mob.spec_noncompliant"
REFUSAL_MOBILITY_NETWORK_INVALID = "refusal.mob.network_invalid"

_VALID_MOTION_TIERS = {"macro", "meso", "micro"}
_VALID_SUPPORTED_MOTION_MODES = {"rail_constrained", "corridor", "free", "orbit"}


class VehicleError(ValueError):
    """Deterministic vehicle-domain refusal."""

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


def _normalize_tier(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_MOTION_TIERS:
        return token
    return "macro"


def _normalize_supported_motion_modes(values: object) -> List[str]:
    rows = _sorted_tokens(values)
    normalized = [token for token in rows if token in _VALID_SUPPORTED_MOTION_MODES]
    if normalized:
        return normalized
    return ["free"]


def deterministic_vehicle_id(
    *,
    parent_structure_instance_id: str | None,
    vehicle_class_id: str,
    spatial_id: str,
    created_tick_bucket: int,
) -> str:
    digest = canonical_sha256(
        {
            "parent_structure_instance_id": str(parent_structure_instance_id or "").strip(),
            "vehicle_class_id": str(vehicle_class_id or "").strip(),
            "spatial_id": str(spatial_id or "").strip(),
            "created_tick_bucket": int(max(0, _as_int(created_tick_bucket, 0))),
        }
    )
    return "vehicle.{}".format(digest[:16])


def deterministic_motion_state_ref(*, vehicle_id: str) -> str:
    digest = canonical_sha256({"vehicle_id": str(vehicle_id or "").strip()})
    return "motion_state.{}".format(digest[:16])


def build_motion_state(
    *,
    vehicle_id: str,
    tier: str,
    macro_state: Mapping[str, object] | None = None,
    meso_state: Mapping[str, object] | None = None,
    micro_state: Mapping[str, object] | None = None,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    macro = _as_map(macro_state)
    meso = _as_map(meso_state)
    micro = _as_map(micro_state)
    payload = {
        "schema_version": "1.0.0",
        "vehicle_id": str(vehicle_id).strip(),
        "tier": _normalize_tier(tier),
        "macro_state": {
            "itinerary_id": None
            if macro.get("itinerary_id") is None
            else str(macro.get("itinerary_id", "")).strip() or None,
            "eta_tick": (
                None
                if macro.get("eta_tick") is None
                else int(max(0, _as_int(macro.get("eta_tick", 0), 0)))
            ),
            "current_edge_id": None
            if macro.get("current_edge_id") is None
            else str(macro.get("current_edge_id", "")).strip() or None,
            "current_edge_index": (
                None
                if macro.get("current_edge_index") is None
                else int(max(0, _as_int(macro.get("current_edge_index", 0), 0)))
            ),
            "current_node_id": None
            if macro.get("current_node_id") is None
            else str(macro.get("current_node_id", "")).strip() or None,
            "progress_fraction_q16": int(max(0, min(65535, _as_int(macro.get("progress_fraction_q16", 0), 0)))),
            "edge_elapsed_ticks": int(max(0, _as_int(macro.get("edge_elapsed_ticks", 0), 0))),
            "edge_eta_ticks": int(max(0, _as_int(macro.get("edge_eta_ticks", 0), 0))),
            "started_tick": (
                None
                if macro.get("started_tick") is None
                else int(max(0, _as_int(macro.get("started_tick", 0), 0)))
            ),
            "last_progress_tick": (
                None
                if macro.get("last_progress_tick") is None
                else int(max(0, _as_int(macro.get("last_progress_tick", 0), 0)))
            ),
        },
        "meso_state": {
            "current_edge_id": None
            if meso.get("current_edge_id") is None
            else str(meso.get("current_edge_id", "")).strip() or None,
            "occupancy_token_id": None
            if meso.get("occupancy_token_id") is None
            else str(meso.get("occupancy_token_id", "")).strip() or None,
        },
        "micro_state": {
            "geometry_id": None
            if micro.get("geometry_id") is None
            else str(micro.get("geometry_id", "")).strip() or None,
            "s_param": None
            if micro.get("s_param") is None
            else int(max(0, _as_int(micro.get("s_param", 0), 0))),
            "body_ref": None if micro.get("body_ref") is None else str(micro.get("body_ref", "")).strip() or None,
            "position_mm": _canon(_as_map(micro.get("position_mm"))) if isinstance(micro.get("position_mm"), Mapping) else None,
            "orientation_mdeg": _canon(_as_map(micro.get("orientation_mdeg"))) if isinstance(micro.get("orientation_mdeg"), Mapping) else None,
            "velocity_mm_per_tick": _canon(_as_map(micro.get("velocity_mm_per_tick"))) if isinstance(micro.get("velocity_mm_per_tick"), Mapping) else None,
            "accel_mm_per_tick2": _canon(_as_map(micro.get("accel_mm_per_tick2"))) if isinstance(micro.get("accel_mm_per_tick2"), Mapping) else None,
        },
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_motion_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("vehicle_id", ""))):
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        if not vehicle_id:
            continue
        out[vehicle_id] = build_motion_state(
            vehicle_id=vehicle_id,
            tier=str(row.get("tier", "macro")).strip() or "macro",
            macro_state=_as_map(row.get("macro_state")),
            meso_state=_as_map(row.get("meso_state")),
            micro_state=_as_map(row.get("micro_state")),
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def build_vehicle(
    *,
    vehicle_id: str,
    parent_structure_instance_id: str | None,
    vehicle_class_id: str,
    spatial_id: str,
    spec_ids: object,
    capability_bindings: Mapping[str, object] | None = None,
    port_ids: object = None,
    interior_graph_id: str | None = None,
    pose_slot_ids: object = None,
    mount_point_ids: object = None,
    motion_state_ref: str,
    hazard_ids: object = None,
    maintenance_policy_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "vehicle_id": str(vehicle_id).strip(),
        "parent_structure_instance_id": (
            None if parent_structure_instance_id is None else str(parent_structure_instance_id).strip() or None
        ),
        "vehicle_class_id": str(vehicle_class_id).strip(),
        "spatial_id": str(spatial_id).strip(),
        "spec_ids": _sorted_tokens(spec_ids),
        "capability_bindings": _canon(_as_map(capability_bindings)) if isinstance(capability_bindings, Mapping) else None,
        "port_ids": _sorted_tokens(port_ids),
        "interior_graph_id": None if interior_graph_id is None else str(interior_graph_id).strip() or None,
        "pose_slot_ids": _sorted_tokens(pose_slot_ids),
        "mount_point_ids": _sorted_tokens(mount_point_ids),
        "motion_state_ref": str(motion_state_ref).strip(),
        "hazard_ids": _sorted_tokens(hazard_ids),
        "maintenance_policy_id": str(maintenance_policy_id).strip() or "maintenance.policy.default",
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_vehicle_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("vehicle_id", ""))):
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        vehicle_class_id = str(row.get("vehicle_class_id", "")).strip()
        spatial_id = str(row.get("spatial_id", "")).strip()
        motion_state_ref = str(row.get("motion_state_ref", "")).strip()
        if (not vehicle_id) or (not vehicle_class_id) or (not spatial_id) or (not motion_state_ref):
            continue
        out[vehicle_id] = build_vehicle(
            vehicle_id=vehicle_id,
            parent_structure_instance_id=(
                None
                if row.get("parent_structure_instance_id") is None
                else str(row.get("parent_structure_instance_id", "")).strip() or None
            ),
            vehicle_class_id=vehicle_class_id,
            spatial_id=spatial_id,
            spec_ids=row.get("spec_ids"),
            capability_bindings=_as_map(row.get("capability_bindings")) if isinstance(row.get("capability_bindings"), Mapping) else None,
            port_ids=row.get("port_ids"),
            interior_graph_id=(None if row.get("interior_graph_id") is None else str(row.get("interior_graph_id", "")).strip() or None),
            pose_slot_ids=row.get("pose_slot_ids"),
            mount_point_ids=row.get("mount_point_ids"),
            motion_state_ref=motion_state_ref,
            hazard_ids=row.get("hazard_ids"),
            maintenance_policy_id=str(row.get("maintenance_policy_id", "")).strip() or "maintenance.policy.default",
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def vehicle_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_vehicle_rows(rows)
    return dict((str(row.get("vehicle_id", "")).strip(), dict(row)) for row in normalized if str(row.get("vehicle_id", "")).strip())


def motion_state_rows_by_vehicle_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_motion_state_rows(rows)
    return dict((str(row.get("vehicle_id", "")).strip(), dict(row)) for row in normalized if str(row.get("vehicle_id", "")).strip())


def vehicle_class_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("vehicle_classes")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("vehicle_classes")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("vehicle_class_id", ""))):
        vehicle_class_id = str(row.get("vehicle_class_id", "")).strip()
        if not vehicle_class_id:
            continue
        out[vehicle_class_id] = {
            "schema_version": "1.0.0",
            "vehicle_class_id": vehicle_class_id,
            "description": str(row.get("description", "")).strip(),
            "supported_motion_modes": _normalize_supported_motion_modes(row.get("supported_motion_modes")),
            "required_specs": _sorted_tokens(row.get("required_specs")),
            "default_ports": _sorted_tokens(row.get("default_ports")),
            "default_pose_bindings": _sorted_tokens(row.get("default_pose_bindings")),
            "default_hazard_modes": _sorted_tokens(row.get("default_hazard_modes")),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def get_vehicle_capabilities(
    *,
    vehicle_rows: object,
    vehicle_class_registry_payload: Mapping[str, object] | None,
    vehicle_id: str,
) -> dict:
    by_id = vehicle_rows_by_id(vehicle_rows)
    row = dict(by_id.get(str(vehicle_id).strip()) or {})
    if not row:
        return {}
    class_rows = vehicle_class_rows_by_id(vehicle_class_registry_payload)
    class_row = dict(class_rows.get(str(row.get("vehicle_class_id", "")).strip()) or {})
    return {
        "vehicle_id": str(row.get("vehicle_id", "")).strip(),
        "vehicle_class_id": str(row.get("vehicle_class_id", "")).strip(),
        "supported_motion_modes": _normalize_supported_motion_modes(class_row.get("supported_motion_modes")),
        "capability_bindings": _canon(_as_map(row.get("capability_bindings"))),
        "spec_ids": _sorted_tokens(row.get("spec_ids")),
    }


def get_vehicle_ports(*, vehicle_rows: object, vehicle_id: str) -> List[str]:
    by_id = vehicle_rows_by_id(vehicle_rows)
    row = dict(by_id.get(str(vehicle_id).strip()) or {})
    return _sorted_tokens(row.get("port_ids"))


def get_vehicle_interior(*, vehicle_rows: object, vehicle_id: str) -> str | None:
    by_id = vehicle_rows_by_id(vehicle_rows)
    row = dict(by_id.get(str(vehicle_id).strip()) or {})
    if not row:
        return None
    token = str(row.get("interior_graph_id", "")).strip()
    return token or None


def get_vehicle_driver_pose_slots(
    *,
    vehicle_rows: object,
    pose_slot_rows: object,
    vehicle_id: str,
) -> List[str]:
    by_id = vehicle_rows_by_id(vehicle_rows)
    row = dict(by_id.get(str(vehicle_id).strip()) or {})
    if not row:
        return []
    declared = _sorted_tokens(row.get("pose_slot_ids"))
    slots_by_id = dict(
        (
            str(slot.get("pose_slot_id", "")).strip(),
            dict(slot),
        )
        for slot in list(pose_slot_rows or [])
        if isinstance(slot, Mapping) and str(slot.get("pose_slot_id", "")).strip()
    )
    out: List[str] = []
    for slot_id in declared:
        slot = dict(slots_by_id.get(slot_id) or {})
        ext = _as_map(slot.get("extensions"))
        control_binding_id = str(slot.get("control_binding_id", "")).strip()
        posture_rows = _sorted_tokens(slot.get("allowed_postures"))
        is_driver = bool(ext.get("driver_station", False)) or bool(control_binding_id) or bool("sit" in posture_rows)
        if is_driver:
            out.append(slot_id)
    return sorted(set(out))


def _first_numeric(parameters: Mapping[str, object], keys: Tuple[str, ...]) -> int | None:
    for key in keys:
        value = parameters.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
    return None


def _spec_numeric(spec_row: Mapping[str, object], keys: Tuple[str, ...]) -> int | None:
    parameters = _as_map(spec_row.get("parameters"))
    return _first_numeric(parameters, keys)


def _compatible_gauge(
    *,
    vehicle_spec_rows: List[dict],
    edge_spec_rows: List[dict],
) -> Tuple[bool, int | None, int | None]:
    vehicle_gauge = None
    edge_gauge = None
    for row in vehicle_spec_rows:
        value = _spec_numeric(row, ("gauge_mm", "track_gauge_mm", "interface_gauge_mm"))
        if value is not None:
            vehicle_gauge = int(value)
            break
    for row in edge_spec_rows:
        value = _spec_numeric(row, ("gauge_mm", "track_gauge_mm", "interface_gauge_mm"))
        if value is not None:
            edge_gauge = int(value)
            break
    if vehicle_gauge is None or edge_gauge is None:
        return True, vehicle_gauge, edge_gauge
    return bool(int(vehicle_gauge) == int(edge_gauge)), vehicle_gauge, edge_gauge


def _compatible_clearance(
    *,
    vehicle_spec_rows: List[dict],
    geometry_metric_row: Mapping[str, object] | None,
) -> Tuple[bool, int | None, int | None, int | None, int | None]:
    req_width = None
    req_height = None
    for row in vehicle_spec_rows:
        params = _as_map(row.get("parameters"))
        if req_width is None:
            req_width = _first_numeric(
                params,
                (
                    "clearance_width_mm",
                    "min_clearance_mm",
                    "width_mm",
                ),
            )
        if req_height is None:
            req_height = _first_numeric(
                params,
                (
                    "clearance_height_mm",
                    "min_clearance_height_mm",
                    "height_mm",
                ),
            )
        if req_width is not None and req_height is not None:
            break
    clearance = _as_map(_as_map(geometry_metric_row).get("clearance_envelope"))
    measured_width = _as_int(clearance.get("width_mm", 0), 0) if clearance else None
    measured_height = _as_int(clearance.get("height_mm", 0), 0) if clearance else None
    width_ok = True if req_width is None or measured_width is None else int(measured_width) >= int(req_width)
    height_ok = True if req_height is None or measured_height is None else int(measured_height) >= int(req_height)
    return bool(width_ok and height_ok), req_width, req_height, measured_width, measured_height


def evaluate_vehicle_edge_compatibility(
    *,
    vehicle_row: Mapping[str, object],
    target_edge_row: Mapping[str, object],
    spec_rows_by_id: Mapping[str, dict],
    guide_geometry_rows_by_id: Mapping[str, dict],
    geometry_metric_rows_by_geometry_id: Mapping[str, dict],
) -> dict:
    row_vehicle = dict(vehicle_row or {})
    row_edge = dict(target_edge_row or {})
    vehicle_id = str(row_vehicle.get("vehicle_id", "")).strip()
    edge_id = str(row_edge.get("edge_id", "")).strip()
    if not vehicle_id or not edge_id:
        raise VehicleError(
            REFUSAL_MOBILITY_NETWORK_INVALID,
            "vehicle compatibility requires vehicle and edge rows",
            {"vehicle_id": vehicle_id, "edge_id": edge_id},
        )
    payload = _as_map(row_edge.get("payload"))
    geometry_id = str(payload.get("guide_geometry_id", "")).strip()
    geometry_row = dict(guide_geometry_rows_by_id.get(geometry_id) or {})
    metric_row = dict(geometry_metric_rows_by_geometry_id.get(geometry_id) or {})

    vehicle_spec_rows = [
        dict(spec_rows_by_id.get(spec_id) or {})
        for spec_id in _sorted_tokens(row_vehicle.get("spec_ids"))
        if dict(spec_rows_by_id.get(spec_id) or {})
    ]
    edge_spec_ids = []
    edge_spec_token = str(payload.get("spec_id", "")).strip()
    if edge_spec_token:
        edge_spec_ids.append(edge_spec_token)
    geometry_spec_token = str(geometry_row.get("spec_id", "")).strip()
    if geometry_spec_token:
        edge_spec_ids.append(geometry_spec_token)
    edge_spec_rows = [
        dict(spec_rows_by_id.get(spec_id) or {})
        for spec_id in sorted(set(edge_spec_ids))
        if dict(spec_rows_by_id.get(spec_id) or {})
    ]

    gauge_ok, vehicle_gauge, edge_gauge = _compatible_gauge(
        vehicle_spec_rows=vehicle_spec_rows,
        edge_spec_rows=edge_spec_rows,
    )
    clearance_ok, req_width, req_height, measured_width, measured_height = _compatible_clearance(
        vehicle_spec_rows=vehicle_spec_rows,
        geometry_metric_row=metric_row,
    )
    compatible = bool(gauge_ok and clearance_ok)
    details = {
        "vehicle_id": vehicle_id,
        "target_edge_id": edge_id,
        "guide_geometry_id": geometry_id or None,
        "gauge_compatible": bool(gauge_ok),
        "vehicle_gauge_mm": vehicle_gauge,
        "edge_gauge_mm": edge_gauge,
        "clearance_compatible": bool(clearance_ok),
        "required_clearance_width_mm": req_width,
        "required_clearance_height_mm": req_height,
        "measured_clearance_width_mm": measured_width,
        "measured_clearance_height_mm": measured_height,
    }
    result = {
        "schema_version": "1.0.0",
        "vehicle_id": vehicle_id,
        "target_edge_id": edge_id,
        "compatible": compatible,
        "reason_code": None if compatible else REFUSAL_MOBILITY_SPEC_NONCOMPLIANT,
        "details": _canon(details),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "REFUSAL_MOBILITY_NETWORK_INVALID",
    "REFUSAL_MOBILITY_SPEC_NONCOMPLIANT",
    "VehicleError",
    "build_motion_state",
    "build_vehicle",
    "deterministic_motion_state_ref",
    "deterministic_vehicle_id",
    "evaluate_vehicle_edge_compatibility",
    "get_vehicle_capabilities",
    "get_vehicle_driver_pose_slots",
    "get_vehicle_interior",
    "get_vehicle_ports",
    "motion_state_rows_by_vehicle_id",
    "normalize_motion_state_rows",
    "normalize_vehicle_rows",
    "vehicle_class_rows_by_id",
    "vehicle_rows_by_id",
]
