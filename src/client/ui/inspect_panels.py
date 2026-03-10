"""Deterministic UX-0 inspection panels over snapshots, overlays, and explain tools."""

from __future__ import annotations

from typing import Mapping

from src.client.interaction import build_inspection_overlays
from tools.geo.tool_explain_property_origin import explain_property_origin_report
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _target_row(inspection_snapshot: Mapping[str, object] | None) -> tuple[dict, dict]:
    snapshot = _as_map(inspection_snapshot)
    target_payload = _as_map(snapshot.get("target_payload"))
    return target_payload, _as_map(target_payload.get("row"))


def _panel(
    *,
    panel_id: str,
    panel_kind: str,
    panel_title: str,
    visible: bool,
    rows: object = None,
    summary: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "panel_id": str(panel_id or "").strip(),
        "panel_kind": str(panel_kind or "").strip(),
        "panel_title": str(panel_title or "").strip(),
        "visible": bool(visible),
        "summary": str(summary or "").strip(),
        "rows": [dict(row) for row in _as_list(rows) if isinstance(row, Mapping)],
        "extensions": _as_map(extensions),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_celestial_object_panel(
    *,
    inspection_snapshot: Mapping[str, object] | None,
) -> dict:
    target_payload, row = _target_row(inspection_snapshot)
    object_id = str(target_payload.get("target_id", "")).strip() or str(row.get("object_id", "")).strip()
    hierarchy = _as_map(row.get("hierarchy"))
    physical = _as_map(row.get("physical"))
    orbit = _as_map(row.get("orbit"))
    rows = [
        {"key": "object_id", "value": object_id},
        {"key": "type", "value": str(row.get("object_kind_id", "")).strip() or str(row.get("type", "")).strip()},
        {"key": "parent_object_id", "value": str(hierarchy.get("parent_object_id", "")).strip()},
        {"key": "mass_kg", "value": physical.get("mass_kg")},
        {"key": "radius_km", "value": physical.get("radius_km")},
        {"key": "semi_major_axis_milli_au", "value": orbit.get("semi_major_axis_milli_au")},
        {"key": "current_lod", "value": str(row.get("lod_state", "")).strip() or str(row.get("refinement_state", "")).strip()},
    ]
    return _panel(
        panel_id="panel.inspect.celestial_object",
        panel_kind="celestial_object",
        panel_title="Celestial Object",
        visible=bool(object_id),
        rows=rows,
        summary="object {}".format(object_id or "<none>"),
        extensions={"source": "process.inspect_generate_snapshot"},
    )


def build_surface_tile_panel(*, inspection_snapshot: Mapping[str, object] | None) -> dict:
    target_payload, row = _target_row(inspection_snapshot)
    tile_id = str(target_payload.get("target_id", "")).strip() or str(row.get("tile_object_id", "")).strip()
    row_ext = _as_map(row.get("extensions"))
    rows = [
        {"key": "tile_object_id", "value": tile_id},
        {"key": "planet_object_id", "value": str(row.get("planet_object_id", "")).strip()},
        {"key": "material_baseline_id", "value": str(row.get("material_baseline_id", "")).strip()},
        {"key": "biome_stub_id", "value": str(row.get("biome_stub_id", "")).strip()},
        {"key": "river_flag", "value": row.get("river_flag")},
        {"key": "lake_flag", "value": row_ext.get("lake_flag")},
        {"key": "hydrology_structure_kind", "value": str(row_ext.get("hydrology_structure_kind", "")).strip()},
    ]
    return _panel(
        panel_id="panel.inspect.surface_tile",
        panel_kind="surface_tile",
        panel_title="Surface Tile",
        visible=bool(tile_id),
        rows=rows,
        summary="tile {}".format(tile_id or "<none>"),
    )


def build_geometry_cell_panel(*, inspection_snapshot: Mapping[str, object] | None) -> dict:
    _target_payload, row = _target_row(inspection_snapshot)
    geometry_state = _as_map(row.get("geometry_cell_state"))
    geometry_id = str(geometry_state.get("geometry_cell_id", "")).strip() or str(row.get("geometry_cell_id", "")).strip()
    rows = [
        {"key": "geometry_cell_id", "value": geometry_id},
        {"key": "occupancy_class", "value": str(geometry_state.get("occupancy_class", "")).strip()},
        {"key": "material_id", "value": str(geometry_state.get("material_id", "")).strip()},
    ]
    return _panel(
        panel_id="panel.inspect.geometry_cell",
        panel_kind="geometry_cell",
        panel_title="Geometry Cell",
        visible=bool(geometry_id),
        rows=rows,
        summary="geometry {}".format(geometry_id or "<none>"),
    )


def build_field_panel(
    *,
    field_values: Mapping[str, object] | None = None,
) -> dict:
    values = _as_map(field_values)
    rows = [
        {"key": "temperature", "value": values.get("temperature")},
        {"key": "daylight", "value": values.get("daylight")},
        {"key": "tide_height_proxy", "value": values.get("tide_height_proxy")},
        {"key": "wind_vector", "value": values.get("wind_vector")},
        {"key": "pollution", "value": values.get("pollution")},
    ]
    visible = any(row.get("value") is not None and str(row.get("value", "")).strip() != "" for row in rows)
    return _panel(
        panel_id="panel.inspect.field",
        panel_kind="field",
        panel_title="Field",
        visible=visible,
        rows=rows,
        summary="field values" if visible else "field values unavailable",
    )


def build_scan_result_panel(*, scan_result: Mapping[str, object] | None = None) -> dict:
    result = _as_map(scan_result)
    flags = _as_map(result.get("surface_flags"))
    rows = [
        {"key": "tool_id", "value": str(result.get("tool_id", "")).strip()},
        {"key": "precision_mode", "value": str(result.get("precision_mode", "")).strip()},
        {"key": "tile_cell_key", "value": _as_map(result.get("tile_cell_key"))},
        {"key": "elevation_proxy_mm", "value": result.get("elevation_proxy_mm")},
        {"key": "surface_flags", "value": flags},
        {"key": "flow_target_tile_key", "value": _as_map(result.get("flow_target_tile_key"))},
        {"key": "temperature", "value": result.get("temperature")},
        {"key": "daylight", "value": result.get("daylight")},
        {"key": "wind_vector", "value": _as_map(result.get("wind_vector"))},
        {"key": "tide_height_proxy", "value": result.get("tide_height_proxy")},
        {"key": "pollution", "value": result.get("pollution")},
    ]
    return _panel(
        panel_id="panel.inspect.scan_result",
        panel_kind="scan_result",
        panel_title="Scanner",
        visible=bool(result),
        rows=rows,
        summary="scanner {}".format(str(result.get("scan_id", "")).strip() or "<none>"),
        extensions={"used_tool_ids": _sorted_strings(result.get("used_tool_ids"))},
    )


def build_terrain_collision_panel(
    *,
    body_state: Mapping[str, object] | None = None,
    inspection_snapshot: Mapping[str, object] | None = None,
) -> dict:
    state = _as_map(body_state)
    state_ext = _as_map(state.get("extensions"))
    collision = _as_map(state_ext.get("terrain_collision_state"))
    slope = _as_map(state_ext.get("terrain_slope_response"))
    _target_payload, row = _target_row(inspection_snapshot)
    surface_tile = _as_map(row.get("surface_tile_artifact"))
    surface_height = _as_int(_as_map(surface_tile.get("elevation_params_ref")).get("height_proxy", 0), 0)
    rows = [
        {"key": "grounded", "value": collision.get("grounded")},
        {"key": "terrain_height_mm", "value": collision.get("terrain_height_mm")},
        {"key": "ground_contact_height_mm", "value": collision.get("ground_contact_height_mm")},
        {"key": "slope_angle_mdeg", "value": collision.get("slope_angle_mdeg") or slope.get("slope_angle_mdeg")},
        {"key": "accel_factor_permille", "value": slope.get("accel_factor_permille")},
        {"key": "selection_height_proxy", "value": surface_height if surface_height else None},
    ]
    visible = any(row.get("value") not in (None, "", []) for row in rows)
    return _panel(
        panel_id="panel.inspect.terrain_collision",
        panel_kind="terrain_collision",
        panel_title="Terrain Collision",
        visible=visible,
        rows=rows,
        summary="terrain collision debug" if visible else "terrain collision unavailable",
    )


def build_logic_tool_panel(
    *,
    logic_probe_surface: Mapping[str, object] | None = None,
    logic_trace_surface: Mapping[str, object] | None = None,
) -> dict:
    probe = _as_map(logic_probe_surface)
    trace = _as_map(logic_trace_surface)
    rows = [
        {"key": "probe_request_id", "value": str(_as_map(probe.get("probe_request")).get("request_id", "")).strip()},
        {"key": "trace_request_id", "value": str(_as_map(trace.get("trace_request")).get("request_id", "")).strip()},
        {"key": "trace_duration_ticks", "value": trace.get("bounded_duration_ticks")},
        {"key": "probe_process_count", "value": len(_as_list(probe.get("process_sequence")))},
        {"key": "trace_process_count", "value": len(_as_list(trace.get("process_sequence")))},
    ]
    return _panel(
        panel_id="panel.inspect.logic_tools",
        panel_kind="logic_tools",
        panel_title="Logic Tools",
        visible=bool(probe or trace),
        rows=rows,
        summary="logic probe/trace tool surface" if (probe or trace) else "logic tool surface unavailable",
        extensions={
            "used_tool_ids": _sorted_strings(
                [str(probe.get("tool_id", "")).strip(), str(trace.get("tool_id", "")).strip()]
            )
        },
    )


def build_logic_network_panel(*, inspection_snapshot: Mapping[str, object] | None) -> dict:
    snapshot = _as_map(inspection_snapshot)
    sections = _as_map(snapshot.get("summary_sections"))
    rows = []
    for key in sorted(sections.keys()):
        if "logic" not in key and "network" not in key:
            continue
        rows.append({"key": key, "value": _as_map(sections.get(key))})
    return _panel(
        panel_id="panel.inspect.logic_network",
        panel_kind="logic_network",
        panel_title="Logic / Network",
        visible=bool(rows),
        rows=rows,
        summary="logic/network sections {}".format(len(rows)),
    )


def build_system_capsule_panel(*, inspection_snapshot: Mapping[str, object] | None) -> dict:
    snapshot = _as_map(inspection_snapshot)
    sections = _as_map(snapshot.get("summary_sections"))
    rows = []
    for key in sorted(sections.keys()):
        if "system" not in key and "capsule" not in key:
            continue
        rows.append({"key": key, "value": _as_map(sections.get(key))})
    return _panel(
        panel_id="panel.inspect.system_capsule",
        panel_kind="system_capsule",
        panel_title="System / Capsule",
        visible=bool(rows),
        rows=rows,
        summary="system/capsule sections {}".format(len(rows)),
    )


def build_overlay_provenance_panel(
    *,
    property_origin_request: Mapping[str, object] | None = None,
    property_origin_result: Mapping[str, object] | None = None,
) -> dict:
    request = _as_map(property_origin_request)
    result = _as_map(property_origin_result)
    if not result and str(request.get("object_id", "")).strip() and str(request.get("property_path", "")).strip():
        result = explain_property_origin_report(
            object_id=str(request.get("object_id", "")).strip(),
            property_path=str(request.get("property_path", "")).strip(),
            merge_result=request.get("merge_result"),
        )
    report = _as_map(result.get("report"))
    prior_rows = [
        {
            "layer_id": str(_as_map(row).get("layer_id", "")).strip(),
            "value": _as_map(row).get("value"),
        }
        for row in _as_list(report.get("prior_value_chain"))
        if isinstance(row, Mapping)
    ]
    rows = [
        {"key": "tool_id", "value": "tool.geo.explain_property_origin"},
        {"key": "explain_contract_id", "value": str(result.get("explain_contract_id", "")).strip()},
        {"key": "overlay_conflict_contract_id", "value": str(result.get("overlay_conflict_contract_id", "")).strip()},
        {"key": "current_layer_id", "value": str(report.get("current_layer_id", "")).strip()},
        {"key": "prior_value_chain", "value": prior_rows},
    ]
    return _panel(
        panel_id="panel.inspect.overlay_provenance",
        panel_kind="overlay_provenance",
        panel_title="Overlay Provenance",
        visible=bool(result),
        rows=rows,
        summary="property origin chain" if result else "property origin unavailable",
        extensions={
            "tool_id": "tool.geo.explain_property_origin",
            "tool_result": dict(result),
        },
    )


def build_inspection_panel_set(
    *,
    perceived_model: Mapping[str, object] | None,
    target_semantic_id: str,
    authority_context: Mapping[str, object] | None = None,
    inspection_snapshot: Mapping[str, object] | None = None,
    property_origin_request: Mapping[str, object] | None = None,
    property_origin_result: Mapping[str, object] | None = None,
    overlay_runtime: Mapping[str, object] | None = None,
    requested_cost_units: int = 1,
    field_values: Mapping[str, object] | None = None,
    body_state: Mapping[str, object] | None = None,
    scan_result: Mapping[str, object] | None = None,
    logic_probe_surface: Mapping[str, object] | None = None,
    logic_trace_surface: Mapping[str, object] | None = None,
) -> dict:
    """Panels consume process.inspect_generate_snapshot and tool.geo.explain_property_origin outputs only."""

    overlays = {"result": "complete", "inspection_overlays": {}, "overlay_runtime": dict(overlay_runtime or {})}
    if str(target_semantic_id or "").strip() and inspection_snapshot:
        overlays = build_inspection_overlays(
            perceived_model=dict(perceived_model or {}),
            target_semantic_id=str(target_semantic_id).strip(),
            authority_context=dict(authority_context or {}),
            inspection_snapshot=dict(inspection_snapshot or {}),
            overlay_runtime=dict(overlay_runtime or {}),
            requested_cost_units=int(max(1, _as_int(requested_cost_units, 1))),
        )
    panels = [
        build_celestial_object_panel(inspection_snapshot=inspection_snapshot),
        build_surface_tile_panel(inspection_snapshot=inspection_snapshot),
        build_geometry_cell_panel(inspection_snapshot=inspection_snapshot),
        build_field_panel(field_values=field_values),
        build_scan_result_panel(scan_result=scan_result),
        build_terrain_collision_panel(body_state=body_state, inspection_snapshot=inspection_snapshot),
        build_logic_tool_panel(logic_probe_surface=logic_probe_surface, logic_trace_surface=logic_trace_surface),
        build_logic_network_panel(inspection_snapshot=inspection_snapshot),
        build_system_capsule_panel(inspection_snapshot=inspection_snapshot),
        build_overlay_provenance_panel(
            property_origin_request=property_origin_request,
            property_origin_result=property_origin_result,
        ),
    ]
    visible_panels = [dict(panel) for panel in panels if bool(panel.get("visible", False))]
    payload = {
        "result": "complete",
        "panels": visible_panels,
        "inspection_overlay_payload": dict(overlays.get("inspection_overlays") or {}),
        "inspection_overlay_runtime": dict(overlays.get("overlay_runtime") or {}),
        "used_tool_ids": _sorted_strings(
            (["tool.geo.explain_property_origin"] if property_origin_request or property_origin_result else [])
            + list(_as_map(scan_result).get("used_tool_ids") or [])
            + [
                str(_as_map(logic_probe_surface).get("tool_id", "")).strip(),
                str(_as_map(logic_trace_surface).get("tool_id", "")).strip(),
            ]
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "build_celestial_object_panel",
    "build_field_panel",
    "build_geometry_cell_panel",
    "build_inspection_panel_set",
    "build_logic_tool_panel",
    "build_logic_network_panel",
    "build_overlay_provenance_panel",
    "build_scan_result_panel",
    "build_surface_tile_panel",
    "build_system_capsule_panel",
    "build_terrain_collision_panel",
]
