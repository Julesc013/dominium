"""Derived inspection overlays for RenderModel overlay layers."""

from __future__ import annotations

import json
import os
from typing import Dict

from src.materials.blueprint_engine import (
    BlueprintCompileError,
    blueprint_bom_summary,
    build_blueprint_ghost_overlay,
    compile_blueprint_artifacts,
)
from src.performance.cost_engine import normalize_budget_envelope, reserve_inspection_budget
from src.performance.inspection_cache import (
    build_cache_key as inspection_build_cache_key,
    build_inspection_snapshot,
    cache_lookup_or_store as inspection_cache_lookup_or_store,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: list[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip())
)


def _point_mm(value: object) -> dict | None:
    if not isinstance(value, dict):
        return None
    return {
        "x": int(_to_int(value.get("x", 0), 0)),
        "y": int(_to_int(value.get("y", 0), 0)),
        "z": int(_to_int(value.get("z", 0), 0)),
    }


def _geometry_points_mm(geometry_row: dict) -> list[dict]:
    parameters = dict((dict(geometry_row or {})).get("parameters") or {})
    for key in ("control_points_mm", "points_mm", "path_points_mm"):
        rows = list(parameters.get(key) or [])
        points = [_point_mm(item) for item in rows if isinstance(item, dict)]
        points = [dict(point) for point in points if isinstance(point, dict)]
        if points:
            return points
    start_mm = _point_mm(parameters.get("start_mm"))
    end_mm = _point_mm(parameters.get("end_mm"))
    if start_mm and end_mm:
        return [start_mm, end_mm]
    return []


def _read_json_payload(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve_registry(runtime: dict, key: str, repo_root: str, fallback_rel_path: str) -> dict:
    payload = dict(runtime.get(key) or {})
    if payload:
        return payload
    if not str(repo_root).strip():
        return {}
    path = os.path.join(str(repo_root), fallback_rel_path.replace("/", os.sep))
    return _read_json_payload(path)


def _target_payload_from_perceived(perceived_model: dict, target_semantic_id: str) -> dict:
    token = str(target_semantic_id).strip()
    entities = list((dict((dict(perceived_model or {})).get("entities") or {})).get("entries") or [])
    for row in sorted((item for item in entities if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        entity_id = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
        if entity_id == token:
            return {
                "target_id": token,
                "exists": True,
                "collection": "entities.entries",
                "row": dict(row),
            }
    populations = list((dict((dict(perceived_model or {})).get("populations") or {})).get("entries") or [])
    for row in sorted((item for item in populations if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        cohort_id = str(row.get("cohort_id", "")).strip()
        population_id = str(row.get("population_id", "")).strip()
        if token in (cohort_id, population_id):
            return {
                "target_id": token,
                "exists": True,
                "collection": "populations.entries",
                "row": dict(row),
            }
    return {
        "target_id": token,
        "exists": False,
    }


def _overlay_materials(target_semantic_id: str) -> list[dict]:
    highlight_material_id = "mat.inspect.highlight.{}".format(canonical_sha256({"target": target_semantic_id})[:12])
    label_material_id = "mat.inspect.label.{}".format(canonical_sha256({"target": target_semantic_id, "label": True})[:12])
    return sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": highlight_material_id,
                "base_color": {"r": 247, "g": 208, "b": 84},
                "roughness": 320,
                "metallic": 0,
                "emission": {"r": 247, "g": 208, "b": 84, "strength": 380},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "highlight"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": label_material_id,
                "base_color": {"r": 229, "g": 236, "b": 242},
                "roughness": 260,
                "metallic": 20,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "label"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )


def _overlay_renderables(
    *,
    target_semantic_id: str,
    summary_label: str,
    mode: str,
) -> list[dict]:
    highlight_material_id = "mat.inspect.highlight.{}".format(canonical_sha256({"target": target_semantic_id})[:12])
    label_material_id = "mat.inspect.label.{}".format(canonical_sha256({"target": target_semantic_id, "label": True})[:12])
    rows = [
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.highlight.{}".format(canonical_sha256({"target": target_semantic_id})[:12]),
            "semantic_id": "overlay.inspect.highlight.{}".format(target_semantic_id),
            "primitive_id": "prim.line.debug",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": highlight_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": None,
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": True},
            "extensions": {
                "interaction_overlay": True,
                "target_semantic_id": target_semantic_id,
                "mode": mode,
            },
        },
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.label.{}".format(canonical_sha256({"target": target_semantic_id, "label": True})[:12]),
            "semantic_id": "overlay.inspect.label.{}".format(target_semantic_id),
            "primitive_id": "prim.glyph.label",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": label_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": str(summary_label),
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": False},
            "extensions": {
                "interaction_overlay": True,
                "target_semantic_id": target_semantic_id,
                "mode": mode,
            },
        },
    ]
    return sorted(rows, key=lambda row: str(row.get("renderable_id", "")))


def _color_from_seed(seed: object, floor: int = 48) -> dict:
    digest = canonical_sha256(seed)
    minimum = max(0, min(240, _to_int(floor, 48)))
    span = max(1, 256 - minimum)
    return {
        "r": minimum + (int(digest[0:2], 16) % span),
        "g": minimum + (int(digest[2:4], 16) % span),
        "b": minimum + (int(digest[4:6], 16) % span),
    }


def _logistics_graph_rows(runtime: dict, repo_root: str) -> list[dict]:
    registry = _resolve_registry(runtime, "logistics_graph_registry", repo_root, "data/registries/logistics_graph_registry.json")
    rows = list((dict(registry or {})).get("graphs") or [])
    return sorted(
        [dict(item) for item in rows if isinstance(item, dict)],
        key=lambda item: str(item.get("graph_id", "")),
    )


def _network_graph_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    graph_row = {}
    if collection == "network_graphs" and isinstance(target_row.get("nodes"), list):
        graph_row = dict(target_row)
    elif isinstance(target_row.get("nodes"), list) and isinstance(target_row.get("edges"), list):
        graph_row = dict(target_row)
    else:
        for row in sorted(
            [dict(item) for item in list(runtime.get("network_graph_rows") or []) if isinstance(item, dict)],
            key=lambda item: str(item.get("graph_id", "")),
        ):
            if str(row.get("graph_id", "")).strip() == str(target_semantic_id).strip():
                graph_row = dict(row)
                break
    if not graph_row:
        return {
            "mode": "networkgraph_overlay",
            "summary": "graph:{} unavailable".format(str(target_semantic_id)),
            "target_semantic_id": str(target_semantic_id),
            "inspection_snapshot": dict(inspection_snapshot or {}),
            "renderables": _overlay_renderables(
                target_semantic_id=str(target_semantic_id),
                summary_label="graph unavailable",
                mode="networkgraph_overlay",
            ),
            "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
            "degraded": True,
            "extensions": {"overlay_kind": "networkgraph", "graph_status": "missing"},
        }

    graph_id = str(graph_row.get("graph_id", "")).strip() or str(target_semantic_id).strip()
    node_rows = sorted(
        [dict(item) for item in list(graph_row.get("nodes") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("node_id", "")),
    )
    edge_rows = sorted(
        [dict(item) for item in list(graph_row.get("edges") or []) if isinstance(item, dict)],
        key=lambda item: (str(item.get("from_node_id", "")), str(item.get("to_node_id", "")), str(item.get("edge_id", ""))),
    )
    sections = dict((dict(inspection_snapshot or {})).get("summary_sections") or {})
    route_section = dict(sections.get("section.mob.route_result") or sections.get("section.networkgraph.route") or {})
    route_data = dict(route_section.get("data") or {})
    network_summary_section = dict(
        sections.get("section.mob.network_summary") or sections.get("section.networkgraph.summary") or {}
    )
    network_summary_data = dict(network_summary_section.get("data") or {})
    occupancy_section = dict(sections.get("section.mob.edge_occupancy") or {})
    occupancy_data = dict(occupancy_section.get("data") or {})
    occupancy_rows = [
        dict(item)
        for item in list(occupancy_data.get("edges") or [])
        if isinstance(item, dict) and str(item.get("edge_id", "")).strip()
    ]
    occupancy_by_edge = dict(
        (str(item.get("edge_id", "")).strip(), dict(item))
        for item in occupancy_rows
        if str(item.get("edge_id", "")).strip()
    )
    congestion_section = dict(sections.get("section.mob.congestion_summary") or {})
    congestion_data = dict(congestion_section.get("data") or {})
    signal_network_section = dict(sections.get("section.signal.network_summary") or {})
    signal_network_data = dict(signal_network_section.get("data") or {})
    signal_queue_section = dict(sections.get("section.signal.channel_queue_depth") or {})
    signal_queue_data = dict(signal_queue_section.get("data") or {})
    signal_delivery_section = dict(sections.get("section.signal.delivery_status") or {})
    signal_delivery_data = dict(signal_delivery_section.get("data") or {})
    signal_quality_section = dict(sections.get("section.signal.quality_summary") or {})
    signal_quality_data = dict(signal_quality_section.get("data") or {})
    elec_local_panel_section = dict(sections.get("section.elec.local_panel_state") or {})
    elec_local_panel_data = dict(elec_local_panel_section.get("data") or {})
    elec_device_states_section = dict(sections.get("section.elec.device_states") or {})
    elec_device_states_data = dict(elec_device_states_section.get("data") or {})
    elec_pf_section = dict(sections.get("section.elec.pf_summary") or {})
    elec_pf_data = dict(elec_pf_section.get("data") or {})
    elec_loss_heat_section = dict(sections.get("section.elec.loss_heat_summary") or {})
    elec_loss_heat_data = dict(elec_loss_heat_section.get("data") or {})
    elec_fault_section = dict(sections.get("section.elec.fault_summary") or {})
    elec_fault_data = dict(elec_fault_section.get("data") or {})
    elec_protection_section = dict(sections.get("section.elec.protection_device_states") or {})
    elec_protection_data = dict(elec_protection_section.get("data") or {})
    elec_compliance_section = dict(sections.get("section.elec.compliance_summary") or {})
    elec_compliance_data = dict(elec_compliance_section.get("data") or {})
    delayed_vehicle_ids = set(_sorted_unique_strings(list(congestion_data.get("delayed_vehicle_ids") or [])))
    congested_edge_ids = set(_sorted_unique_strings(list(congestion_data.get("congested_edge_ids") or [])))
    elec_fault_rows = sorted(
        [dict(item) for item in list(elec_fault_data.get("fault_rows") or []) if isinstance(item, dict)],
        key=lambda item: (str(item.get("target_id", "")), str(item.get("fault_kind_id", "")), str(item.get("fault_id", ""))),
    )
    elec_fault_rows_by_edge: Dict[str, list[dict]] = {}
    for row in elec_fault_rows:
        edge_id = str(row.get("target_id", "")).strip()
        if not edge_id:
            continue
        elec_fault_rows_by_edge.setdefault(edge_id, []).append(dict(row))
    elec_protection_rows = sorted(
        [dict(item) for item in list(elec_protection_data.get("devices") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("device_id", "")),
    )
    tripped_edge_ids = set(
        str(item.get("edge_id", "")).strip()
        for item in elec_protection_rows
        if str(item.get("edge_id", "")).strip()
        and (str(item.get("breaker_state", "")).strip() == "tripped" or bool(item.get("trip_planned", False)))
    )
    ground_fault_edge_ids = set(
        str(item.get("target_id", "")).strip()
        for item in elec_fault_rows
        if str(item.get("target_id", "")).strip() and str(item.get("fault_kind_id", "")).strip() == "fault.ground_fault"
    )
    signal_edge_queue_rows = sorted(
        [dict(item) for item in list(signal_queue_data.get("edge_queue_depth_rows") or []) if isinstance(item, dict)],
        key=lambda item: (str(item.get("edge_id", "")), _to_int(item.get("queue_depth", 0), 0)),
    )
    signal_edge_queue_by_id = dict(
        (str(item.get("edge_id", "")).strip(), dict(item))
        for item in signal_edge_queue_rows
        if str(item.get("edge_id", "")).strip()
    )
    switch_state_rows = sorted(
        [dict(item) for item in list(network_summary_data.get("switch_states") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("node_id", "")),
    )
    switch_state_by_node = dict(
        (str(item.get("node_id", "")).strip(), dict(item))
        for item in switch_state_rows
        if str(item.get("node_id", "")).strip()
    )
    route_edge_ids = set(_sorted_unique_strings(route_data.get("path_edge_ids")))
    route_spec_warning_edge_ids = set(_sorted_unique_strings(route_data.get("spec_warning_edge_ids")))
    route_curvature_warning_edge_ids = set(_sorted_unique_strings(route_data.get("curvature_warning_edge_ids")))
    edge_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_edge"}, floor=60)
    node_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_node"}, floor=72)
    route_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_route"}, floor=68)
    switch_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_switch"}, floor=70)
    spec_warn_color = {"r": 220, "g": 86, "b": 84}
    curve_warn_color = {"r": 244, "g": 176, "b": 62}
    congestion_low_color = {"r": 104, "g": 188, "b": 110}
    congestion_med_color = {"r": 236, "g": 168, "b": 78}
    congestion_high_color = {"r": 224, "g": 86, "b": 86}
    signal_queue_low_color = {"r": 110, "g": 174, "b": 228}
    signal_queue_med_color = {"r": 92, "g": 128, "b": 222}
    signal_queue_high_color = {"r": 72, "g": 96, "b": 198}
    delayed_color = {"r": 252, "g": 206, "b": 88}
    elec_fault_color = {"r": 238, "g": 78, "b": 72}
    elec_trip_color = {"r": 252, "g": 150, "b": 84}
    elec_ground_fault_color = {"r": 232, "g": 80, "b": 136}
    edge_material_id = "mat.inspect.networkgraph.edge.{}".format(canonical_sha256({"graph_id": graph_id})[:12])
    node_material_id = "mat.inspect.networkgraph.node.{}".format(canonical_sha256({"graph_id": graph_id, "node": True})[:12])
    route_material_id = "mat.inspect.networkgraph.route.{}".format(canonical_sha256({"graph_id": graph_id, "route": True})[:12])
    switch_material_id = "mat.inspect.networkgraph.switch.{}".format(canonical_sha256({"graph_id": graph_id, "switch": True})[:12])
    spec_warn_material_id = "mat.inspect.networkgraph.specwarn.{}".format(canonical_sha256({"graph_id": graph_id, "specwarn": True})[:12])
    curve_warn_material_id = "mat.inspect.networkgraph.curvewarn.{}".format(canonical_sha256({"graph_id": graph_id, "curvewarn": True})[:12])
    congestion_low_material_id = "mat.inspect.networkgraph.cong.low.{}".format(
        canonical_sha256({"graph_id": graph_id, "congestion": "low"})[:12]
    )
    congestion_med_material_id = "mat.inspect.networkgraph.cong.med.{}".format(
        canonical_sha256({"graph_id": graph_id, "congestion": "med"})[:12]
    )
    congestion_high_material_id = "mat.inspect.networkgraph.cong.high.{}".format(
        canonical_sha256({"graph_id": graph_id, "congestion": "high"})[:12]
    )
    signal_queue_low_material_id = "mat.inspect.networkgraph.signalq.low.{}".format(
        canonical_sha256({"graph_id": graph_id, "signal_queue": "low"})[:12]
    )
    signal_queue_med_material_id = "mat.inspect.networkgraph.signalq.med.{}".format(
        canonical_sha256({"graph_id": graph_id, "signal_queue": "med"})[:12]
    )
    signal_queue_high_material_id = "mat.inspect.networkgraph.signalq.high.{}".format(
        canonical_sha256({"graph_id": graph_id, "signal_queue": "high"})[:12]
    )
    delayed_material_id = "mat.inspect.networkgraph.delayed.{}".format(
        canonical_sha256({"graph_id": graph_id, "board": "delayed"})[:12]
    )
    elec_fault_material_id = "mat.inspect.networkgraph.elec.fault.{}".format(
        canonical_sha256({"graph_id": graph_id, "elec": "fault"})[:12]
    )
    elec_trip_material_id = "mat.inspect.networkgraph.elec.trip.{}".format(
        canonical_sha256({"graph_id": graph_id, "elec": "trip"})[:12]
    )
    elec_ground_fault_material_id = "mat.inspect.networkgraph.elec.ground_fault.{}".format(
        canonical_sha256({"graph_id": graph_id, "elec": "ground_fault"})[:12]
    )
    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": edge_material_id,
                "base_color": dict(edge_color),
                "roughness": 340,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_edge"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": node_material_id,
                "base_color": dict(node_color),
                "roughness": 200,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_node"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": route_material_id,
                "base_color": dict(route_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": route_color["r"], "g": route_color["g"], "b": route_color["b"], "strength": 280},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_route"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": switch_material_id,
                "base_color": dict(switch_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": switch_color["r"], "g": switch_color["g"], "b": switch_color["b"], "strength": 260},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_switch"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": spec_warn_material_id,
                "base_color": dict(spec_warn_color),
                "roughness": 240,
                "metallic": 0,
                "emission": {"r": spec_warn_color["r"], "g": spec_warn_color["g"], "b": spec_warn_color["b"], "strength": 280},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_spec_missing"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": curve_warn_material_id,
                "base_color": dict(curve_warn_color),
                "roughness": 230,
                "metallic": 0,
                "emission": {"r": curve_warn_color["r"], "g": curve_warn_color["g"], "b": curve_warn_color["b"], "strength": 280},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_curvature_warning"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": congestion_low_material_id,
                "base_color": dict(congestion_low_color),
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": congestion_low_color["r"], "g": congestion_low_color["g"], "b": congestion_low_color["b"], "strength": 180},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_congestion_low"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": congestion_med_material_id,
                "base_color": dict(congestion_med_color),
                "roughness": 250,
                "metallic": 0,
                "emission": {"r": congestion_med_color["r"], "g": congestion_med_color["g"], "b": congestion_med_color["b"], "strength": 220},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_congestion_med"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": congestion_high_material_id,
                "base_color": dict(congestion_high_color),
                "roughness": 240,
                "metallic": 0,
                "emission": {"r": congestion_high_color["r"], "g": congestion_high_color["g"], "b": congestion_high_color["b"], "strength": 260},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_congestion_high"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": signal_queue_low_material_id,
                "base_color": dict(signal_queue_low_color),
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": signal_queue_low_color["r"], "g": signal_queue_low_color["g"], "b": signal_queue_low_color["b"], "strength": 180},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "signal_queue_low"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": signal_queue_med_material_id,
                "base_color": dict(signal_queue_med_color),
                "roughness": 250,
                "metallic": 0,
                "emission": {"r": signal_queue_med_color["r"], "g": signal_queue_med_color["g"], "b": signal_queue_med_color["b"], "strength": 210},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "signal_queue_medium"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": signal_queue_high_material_id,
                "base_color": dict(signal_queue_high_color),
                "roughness": 240,
                "metallic": 0,
                "emission": {"r": signal_queue_high_color["r"], "g": signal_queue_high_color["g"], "b": signal_queue_high_color["b"], "strength": 240},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "signal_queue_high"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": delayed_material_id,
                "base_color": dict(delayed_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": delayed_color["r"], "g": delayed_color["g"], "b": delayed_color["b"], "strength": 260},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "networkgraph_delayed_board"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": elec_fault_material_id,
                "base_color": dict(elec_fault_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": elec_fault_color["r"], "g": elec_fault_color["g"], "b": elec_fault_color["b"], "strength": 280},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "elec_fault"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": elec_trip_material_id,
                "base_color": dict(elec_trip_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": elec_trip_color["r"], "g": elec_trip_color["g"], "b": elec_trip_color["b"], "strength": 260},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "elec_trip"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": elec_ground_fault_material_id,
                "base_color": dict(elec_ground_fault_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {
                    "r": elec_ground_fault_color["r"],
                    "g": elec_ground_fault_color["g"],
                    "b": elec_ground_fault_color["b"],
                    "strength": 300,
                },
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "elec_ground_fault"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )
    renderables: list[dict] = []
    spec_missing_edge_count = 0
    spec_warning_edge_count = 0
    curvature_warning_edge_count = 0
    elec_fault_edge_count = 0
    elec_trip_edge_count = 0
    elec_ground_fault_edge_count = 0
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        is_route = edge_id in route_edge_ids
        route_spec_warning = edge_id in route_spec_warning_edge_ids
        route_curvature_warning = edge_id in route_curvature_warning_edge_ids
        occupancy_row = dict(occupancy_by_edge.get(edge_id) or {})
        occupancy_capacity_units = int(max(1, _to_int(occupancy_row.get("capacity_units", 1), 1)))
        occupancy_current = int(max(0, _to_int(occupancy_row.get("current_occupancy", 0), 0)))
        occupancy_ratio_permille = int(
            max(
                0,
                _to_int(
                    occupancy_row.get(
                        "congestion_ratio_permille",
                        (dict(occupancy_row.get("extensions") or {})).get(
                            "congestion_ratio_permille",
                            (int(occupancy_current) * 1000) // int(max(1, occupancy_capacity_units)),
                        ),
                    ),
                    0,
                ),
            )
        )
        occupancy_over_capacity = bool(occupancy_ratio_permille > 1000)
        occupancy_heat_material_id = congestion_low_material_id
        if occupancy_ratio_permille > 1500:
            occupancy_heat_material_id = congestion_high_material_id
        elif occupancy_ratio_permille > 1000:
            occupancy_heat_material_id = congestion_med_material_id
        signal_queue_row = dict(signal_edge_queue_by_id.get(edge_id) or {})
        signal_queue_depth = int(max(0, _to_int(signal_queue_row.get("queue_depth", 0), 0)))
        signal_queue_heat_bucket = str(signal_queue_row.get("heat_bucket", "")).strip() or "low"
        signal_queue_material_id = signal_queue_low_material_id
        if signal_queue_heat_bucket == "high" or signal_queue_depth >= 6:
            signal_queue_material_id = signal_queue_high_material_id
        elif signal_queue_heat_bucket == "medium" or signal_queue_depth >= 3:
            signal_queue_material_id = signal_queue_med_material_id
        payload = dict(edge.get("payload") or {})
        spec_id = str(payload.get("spec_id", "")).strip() or None
        spec_missing = not bool(spec_id)
        if spec_missing:
            spec_missing_edge_count += 1
        if route_spec_warning:
            spec_warning_edge_count += 1
        if route_curvature_warning:
            curvature_warning_edge_count += 1
        fault_rows_for_edge = list(elec_fault_rows_by_edge.get(edge_id) or [])
        has_elec_fault = bool(fault_rows_for_edge)
        has_ground_fault = bool(edge_id in ground_fault_edge_ids)
        has_elec_trip = bool(edge_id in tripped_edge_ids)
        if has_elec_fault:
            elec_fault_edge_count += 1
        if has_elec_trip:
            elec_trip_edge_count += 1
        if has_ground_fault:
            elec_ground_fault_edge_count += 1
        material_id = edge_material_id
        if is_route:
            material_id = route_material_id
        if occupancy_over_capacity:
            material_id = occupancy_heat_material_id
        if signal_queue_depth > 0:
            material_id = signal_queue_material_id
        if route_spec_warning or spec_missing:
            material_id = spec_warn_material_id
        if route_curvature_warning:
            material_id = curve_warn_material_id
        if has_elec_trip:
            material_id = elec_trip_material_id
        if has_elec_fault:
            material_id = elec_ground_fault_material_id if has_ground_fault else elec_fault_material_id
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.networkgraph.edge.{}".format(canonical_sha256({"graph_id": graph_id, "edge_id": edge_id})[:16]),
                "semantic_id": "overlay.inspect.networkgraph.edge.{}".format(edge_id),
                "primitive_id": "prim.line.debug",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(is_route or spec_missing or route_spec_warning or route_curvature_warning)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_edge",
                    "edge_id": edge_id,
                    "from_node_id": str(edge.get("from_node_id", "")).strip(),
                    "to_node_id": str(edge.get("to_node_id", "")).strip(),
                    "directional": True,
                    "spec_id": spec_id,
                    "spec_missing": bool(spec_missing),
                    "route_spec_warning": bool(route_spec_warning),
                    "route_curvature_warning": bool(route_curvature_warning),
                    "capacity_units": int(occupancy_capacity_units),
                    "current_occupancy": int(occupancy_current),
                    "congestion_ratio_permille": int(occupancy_ratio_permille),
                    "over_capacity": bool(occupancy_over_capacity),
                    "signal_queue_depth": int(signal_queue_depth),
                    "signal_queue_heat_bucket": signal_queue_heat_bucket,
                    "elec_fault_count": int(len(fault_rows_for_edge)),
                    "elec_has_ground_fault": bool(has_ground_fault),
                    "elec_tripped": bool(has_elec_trip),
                },
            }
        )
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.networkgraph.arrow.{}".format(canonical_sha256({"graph_id": graph_id, "edge_id": edge_id, "arrow": True})[:16]),
                "semantic_id": "overlay.inspect.networkgraph.arrow.{}".format(edge_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": material_id,
                "layer_tags": ["overlay", "ui"],
                "label": ">",
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(is_route or spec_missing or route_spec_warning or route_curvature_warning)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_direction",
                    "edge_id": edge_id,
                },
            }
        )
        if signal_queue_depth > 0:
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.networkgraph.signalq.{}".format(
                        canonical_sha256({"graph_id": graph_id, "edge_id": edge_id, "signal_queue": True})[:16]
                    ),
                    "semantic_id": "overlay.inspect.networkgraph.signalq.{}".format(edge_id),
                    "primitive_id": "prim.glyph.label",
                    "transform": {
                        "position_mm": {"x": 0, "y": 0, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 850,
                    },
                    "material_id": signal_queue_material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": "SIG-Q {}".format(int(signal_queue_depth)),
                    "lod_hint": "lod.band.mid",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "signal_queue_depth",
                        "edge_id": edge_id,
                        "signal_queue_depth": int(signal_queue_depth),
                        "heat_bucket": signal_queue_heat_bucket,
                    },
                }
            )
        if has_elec_fault or has_elec_trip:
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.networkgraph.elecfault.{}".format(
                        canonical_sha256({"graph_id": graph_id, "edge_id": edge_id, "elec_fault": True, "elec_trip": bool(has_elec_trip)})[:16]
                    ),
                    "semantic_id": "overlay.inspect.networkgraph.elecfault.{}".format(edge_id),
                    "primitive_id": "prim.glyph.label",
                    "transform": {
                        "position_mm": {"x": 0, "y": 0, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 900,
                    },
                    "material_id": (
                        elec_ground_fault_material_id
                        if has_ground_fault
                        else (elec_fault_material_id if has_elec_fault else elec_trip_material_id)
                    ),
                    "layer_tags": ["overlay", "ui"],
                    "label": ("GFAULT" if has_ground_fault else ("FAULT" if has_elec_fault else "TRIP")),
                    "lod_hint": "lod.band.mid",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": ("elec_ground_fault" if has_ground_fault else ("elec_fault" if has_elec_fault else "elec_trip")),
                        "edge_id": edge_id,
                        "fault_count": int(len(fault_rows_for_edge)),
                        "tripped": bool(has_elec_trip),
                    },
                }
            )
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.networkgraph.occupancy.{}".format(
                    canonical_sha256({"graph_id": graph_id, "edge_id": edge_id, "occupancy": True})[:16]
                ),
                "semantic_id": "overlay.inspect.networkgraph.occupancy.{}".format(edge_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 850,
                },
                "material_id": occupancy_heat_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "OCC {}/{}".format(int(occupancy_current), int(occupancy_capacity_units)),
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(occupancy_over_capacity)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_occupancy_bar",
                    "edge_id": edge_id,
                    "capacity_units": int(occupancy_capacity_units),
                    "current_occupancy": int(occupancy_current),
                    "congestion_ratio_permille": int(occupancy_ratio_permille),
                    "over_capacity": bool(occupancy_over_capacity),
                },
            }
        )
        if spec_missing or route_spec_warning:
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.networkgraph.specwarn.{}".format(
                        canonical_sha256({"graph_id": graph_id, "edge_id": edge_id, "specwarn": True, "route_spec_warning": bool(route_spec_warning)})[:16]
                    ),
                    "semantic_id": "overlay.inspect.networkgraph.specwarn.{}".format(edge_id),
                    "primitive_id": "prim.glyph.label",
                    "transform": {
                        "position_mm": {"x": 0, "y": 0, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 900,
                    },
                    "material_id": spec_warn_material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": "SPEC!" if route_spec_warning else "SPEC?",
                    "lod_hint": "lod.band.mid",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "networkgraph_spec_warning" if route_spec_warning else "networkgraph_spec_missing",
                        "edge_id": edge_id,
                        "route_spec_warning": bool(route_spec_warning),
                    },
                }
            )
        if route_curvature_warning:
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.networkgraph.curvewarn.{}".format(
                        canonical_sha256({"graph_id": graph_id, "edge_id": edge_id, "curvewarn": True})[:16]
                    ),
                    "semantic_id": "overlay.inspect.networkgraph.curvewarn.{}".format(edge_id),
                    "primitive_id": "prim.glyph.label",
                    "transform": {
                        "position_mm": {"x": 0, "y": 0, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 900,
                    },
                    "material_id": curve_warn_material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": "CURVE",
                    "lod_hint": "lod.band.mid",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "networkgraph_curvature_warning",
                        "edge_id": edge_id,
                    },
                }
            )
    for node in node_rows:
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            continue
        payload = dict(node.get("payload") or {})
        node_kind = str(payload.get("node_kind", "")).strip() or "node"
        switch_state = dict(switch_state_by_node.get(node_id) or {})
        active_edge_id = str(switch_state.get("active_edge_id", "")).strip() or None
        node_label = node_id
        if node_kind == "switch":
            node_label = "SW {}".format(active_edge_id or node_id)
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.networkgraph.node.{}".format(canonical_sha256({"graph_id": graph_id, "node_id": node_id})[:16]),
                "semantic_id": "overlay.inspect.networkgraph.node.{}".format(node_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": switch_material_id if node_kind == "switch" else node_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": node_label,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(node_kind == "switch")},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_node",
                    "node_id": node_id,
                    "node_kind": node_kind,
                    "active_edge_id": active_edge_id,
                },
            }
        )
    timetable_board_rows = sorted(
        [dict(item) for item in list(network_summary_data.get("timetable_board_rows") or []) if isinstance(item, dict)],
        key=lambda item: (
            _to_int(item.get("next_departure_tick", 0), 0),
            str(item.get("schedule_id", "")),
            str(item.get("vehicle_id", "")),
        ),
    )
    delayed_board_count = 0
    for board_row in list(timetable_board_rows)[:64]:
        schedule_id = str(board_row.get("schedule_id", "")).strip()
        vehicle_id = str(board_row.get("vehicle_id", "")).strip()
        delayed = bool(vehicle_id and vehicle_id in delayed_vehicle_ids)
        if delayed:
            delayed_board_count += 1
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.networkgraph.board.{}".format(
                    canonical_sha256({"graph_id": graph_id, "schedule_id": schedule_id, "vehicle_id": vehicle_id})[:16]
                ),
                "semantic_id": "overlay.inspect.networkgraph.board.{}".format(
                    schedule_id or canonical_sha256({"vehicle_id": vehicle_id, "graph_id": graph_id})[:10]
                ),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 900,
                },
                "material_id": delayed_material_id if delayed else node_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "{} {}".format(
                    vehicle_id or "vehicle",
                    "DELAYED" if delayed else "ON-TIME",
                ),
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(delayed)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_station_board",
                    "schedule_id": schedule_id or None,
                    "vehicle_id": vehicle_id or None,
                    "next_departure_tick": int(max(0, _to_int(board_row.get("next_departure_tick", 0), 0))),
                    "projected_arrival_tick": int(max(0, _to_int(board_row.get("projected_arrival_tick", 0), 0))),
                    "delayed": bool(delayed),
                },
            }
        )
    congested_edge_count = int(
        len(
            [
                edge_id
                for edge_id, row in occupancy_by_edge.items()
                if str(edge_id).strip()
                and int(
                    max(
                        0,
                        _to_int(
                            row.get(
                                "congestion_ratio_permille",
                                (dict(row.get("extensions") or {})).get("congestion_ratio_permille", 0),
                            ),
                            0,
                        ),
                    )
                )
                > 1000
            ]
        )
    )
    summary = "graph:{} nodes={} edges={} route_edges={} warnings={} congested={} delayed={}".format(
        graph_id,
        len(node_rows),
        len(edge_rows),
        len(route_edge_ids),
        int(len(route_spec_warning_edge_ids) + len(route_curvature_warning_edge_ids)),
        int(max(congested_edge_count, len(congested_edge_ids))),
        int(delayed_board_count),
    )
    signal_queue_total = int(max(0, _to_int(signal_queue_data.get("queue_depth_total", 0), 0)))
    signal_delivery_status = str(signal_delivery_data.get("delivery_status", "")).strip() or None
    signal_quality_bucket = str(signal_quality_data.get("quality_bucket", "")).strip() or None
    signal_static_indicator = str(signal_quality_data.get("radio_static_indicator", "")).strip() or None
    if signal_queue_total > 0 or signal_delivery_status or signal_quality_bucket:
        summary = "{} signal_queue={} signal_status={} signal_quality={}".format(
            summary,
            int(signal_queue_total),
            signal_delivery_status or "n/a",
            signal_quality_bucket or "n/a",
        )
    if signal_static_indicator:
        summary = "{} static={}".format(summary, signal_static_indicator)
    if elec_fault_edge_count > 0 or elec_trip_edge_count > 0:
        summary = "{} elec_fault_edges={} elec_trip_edges={} ground_fault_edges={}".format(
            summary,
            int(elec_fault_edge_count),
            int(elec_trip_edge_count),
            int(elec_ground_fault_edge_count),
        )
    elec_compliance_state = str(elec_compliance_data.get("compliance_state", "")).strip() or None
    if elec_compliance_state:
        summary = "{} elec_compliance={}".format(summary, elec_compliance_state)
    elec_panel_status = str(elec_local_panel_data.get("panel_status", "")).strip() or None
    if elec_panel_status:
        summary = "{} elec_panel={}".format(summary, elec_panel_status)
    elec_pf_permille = int(max(0, _to_int(elec_pf_data.get("aggregate_pf_permille", 0), 0)))
    if elec_pf_permille > 0:
        summary = "{} elec_pf={}".format(summary, int(elec_pf_permille))
    elec_heat_loss_total = int(max(0, _to_int(elec_loss_heat_data.get("heat_loss_total_stub", 0), 0)))
    if elec_heat_loss_total > 0:
        summary = "{} elec_heat_loss={}".format(summary, int(elec_heat_loss_total))
    return {
        "mode": "networkgraph_overlay",
        "summary": summary,
        "target_semantic_id": str(target_semantic_id),
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": materials,
        "degraded": False,
        "extensions": {
            "overlay_kind": "networkgraph",
            "graph_id": graph_id,
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "route_edge_ids": sorted(route_edge_ids),
            "switch_count": int(len(switch_state_rows)),
            "spec_missing_edge_count": int(spec_missing_edge_count),
            "route_spec_warning_edge_ids": sorted(route_spec_warning_edge_ids),
            "route_spec_warning_edge_count": int(spec_warning_edge_count),
            "route_curvature_warning_edge_ids": sorted(route_curvature_warning_edge_ids),
            "route_curvature_warning_edge_count": int(curvature_warning_edge_count),
            "elec_fault_edge_count": int(elec_fault_edge_count),
            "elec_trip_edge_count": int(elec_trip_edge_count),
            "elec_ground_fault_edge_count": int(elec_ground_fault_edge_count),
            "elec_panel_status": elec_panel_status,
            "elec_panel_energized": bool(elec_local_panel_data.get("energized", False)),
            "elec_panel_tripped_count": int(max(0, _to_int(elec_local_panel_data.get("tripped_count", 0), 0))),
            "elec_device_state_count": int(max(0, _to_int(elec_device_states_data.get("device_count", 0), 0))),
            "elec_pf_permille": int(elec_pf_permille),
            "elec_heat_loss_total_stub": int(elec_heat_loss_total),
            "tripped_edge_ids": sorted(tripped_edge_ids),
            "ground_fault_edge_ids": sorted(ground_fault_edge_ids),
            "congested_edge_ids": sorted(
                set(
                    list(congested_edge_ids)
                    + [
                        str(edge_id).strip()
                        for edge_id, row in occupancy_by_edge.items()
                        if str(edge_id).strip()
                        and int(
                            max(
                                0,
                                _to_int(
                                    row.get(
                                        "congestion_ratio_permille",
                                        (dict(row.get("extensions") or {})).get("congestion_ratio_permille", 0),
                                    ),
                                    0,
                                ),
                            )
                        )
                        > 1000
                    ]
                )
            )[:512],
            "congested_edge_count": int(max(congested_edge_count, len(congested_edge_ids))),
            "delayed_vehicle_ids": sorted(delayed_vehicle_ids),
            "delayed_board_count": int(delayed_board_count),
            "congestion_delay_event_count": int(max(0, _to_int(congestion_data.get("delay_event_count", 0), 0))),
            "congestion_policy_id": str(congestion_data.get("congestion_policy_id", "")).strip() or None,
            "signal_queue_depth_total": int(signal_queue_total),
            "signal_queue_edge_count": int(len(signal_edge_queue_rows)),
            "signal_channel_count": int(max(0, _to_int(signal_network_data.get("channel_count", 0), 0))),
            "signal_delivery_status": signal_delivery_status,
            "signal_delivery_event_count": int(max(0, _to_int(signal_delivery_data.get("event_count", 0), 0))),
            "signal_delivery_ratio_permille": int(
                max(0, _to_int(signal_delivery_data.get("delivered_ratio_permille", 0), 0))
            ),
            "signal_quality_bucket": signal_quality_bucket,
            "signal_radio_static_indicator": signal_static_indicator,
            "signal_line_noisy": bool(signal_quality_data.get("line_noisy", False)),
            "signal_jammer_detected": bool(signal_quality_data.get("jammer_detected", False)),
        },
    }


def _mechanics_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    target_id = str(payload.get("target_id", "")).strip() or str(target_semantic_id).strip()
    ext = dict(payload.get("extensions") or {})
    stress_summary = dict(ext.get("mechanics_stress_summary") or {})
    failure_summary = dict(ext.get("failure_risk_summary") or {})
    risk_rows = [dict(row) for row in list(failure_summary.get("risk_rows") or []) if isinstance(row, dict)]
    max_stress = int(max(0, _to_int(stress_summary.get("max_stress_ratio_permille", 0), 0)))
    near_fracture = int(max(0, _to_int(stress_summary.get("near_fracture_edge_count", 0), 0)))
    failed_edges = int(max(0, _to_int(stress_summary.get("failed_edge_count", 0), 0)))
    derailment_risk = int(max(0, _to_int(stress_summary.get("derailment_risk_permille", 0), 0)))

    bucket = "ok"
    if max_stress >= 1000 or failed_edges > 0:
        bucket = "fracture"
    elif max_stress >= 800 or near_fracture > 0:
        bucket = "warn"
    colors = {
        "ok": {"r": 88, "g": 184, "b": 96},
        "warn": {"r": 231, "g": 188, "b": 68},
        "fracture": {"r": 221, "g": 84, "b": 84},
    }
    bucket_color = dict(colors[bucket])
    material_id = "mat.inspect.mechanics.{}".format(canonical_sha256({"target": target_id, "bucket": bucket})[:12])
    crack_material_id = "mat.inspect.mechanics.crack.{}".format(canonical_sha256({"target": target_id, "crack": True})[:12])
    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": material_id,
                "base_color": dict(bucket_color),
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": bucket_color["r"], "g": bucket_color["g"], "b": bucket_color["b"], "strength": 220},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "mechanics_stress_bucket"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": crack_material_id,
                "base_color": {"r": 244, "g": 240, "b": 232},
                "roughness": 320,
                "metallic": 0,
                "emission": {"r": 244, "g": 240, "b": 232, "strength": 300},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "mechanics_crack_glyph"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )
    renderables = _overlay_renderables(
        target_semantic_id=target_id,
        summary_label="stress={} risk={}".format(max_stress, derailment_risk),
        mode="mechanics_overlay",
    )
    renderables.append(
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.mechanics.stress.{}".format(canonical_sha256({"target": target_id, "stress": True})[:16]),
            "semantic_id": "overlay.inspect.mechanics.stress.{}".format(target_id),
            "primitive_id": "prim.glyph.label",
            "transform": {
                "position_mm": {"x": 0, "y": 180, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 920,
            },
            "material_id": material_id,
            "layer_tags": ["overlay", "ui"],
            "label": "STRESS {:>4}".format(max_stress),
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": bucket != "ok"},
            "extensions": {
                "interaction_overlay": True,
                "overlay_kind": "mechanics_stress",
                "max_stress_ratio_permille": max_stress,
                "derailment_risk_permille": derailment_risk,
            },
        }
    )
    if near_fracture > 0 or failed_edges > 0:
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.mechanics.crack.{}".format(canonical_sha256({"target": target_id, "crack": near_fracture, "failed": failed_edges})[:16]),
                "semantic_id": "overlay.inspect.mechanics.crack.{}".format(target_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 320, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": crack_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "CRACK x{}".format(max(near_fracture, failed_edges)),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": True},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "mechanics_crack",
                    "near_fracture_edge_count": near_fracture,
                    "failed_edge_count": failed_edges,
                },
            }
        )
    summary = "mechanics:{} stress={} near_fracture={} failed={}".format(
        target_id or str(target_semantic_id),
        max_stress,
        near_fracture,
        failed_edges,
    )
    return {
        "mode": "mechanics_overlay",
        "summary": summary,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": materials,
        "degraded": bool(not stress_summary),
        "extensions": {
            "overlay_kind": "mechanics",
            "bucket": bucket,
            "max_stress_ratio_permille": max_stress,
            "near_fracture_edge_count": near_fracture,
            "failed_edge_count": failed_edges,
            "derailment_risk_permille": derailment_risk,
            "risk_rows": risk_rows[:8],
            "collection": str(payload.get("collection", "")).strip(),
            "row_kind": str(target_row.get("schema_version", "")).strip() or None,
        },
    }


def _logistics_graph_for_target(graph_rows: list[dict], target_row: dict, target_semantic_id: str) -> dict:
    graph_id = str((dict(target_row or {})).get("graph_id", "")).strip()
    if graph_id:
        for row in graph_rows:
            if str(row.get("graph_id", "")).strip() == graph_id:
                return dict(row)
    node_id = str((dict(target_row or {})).get("node_id", "")).strip()
    if not node_id and str(target_semantic_id).startswith("node."):
        node_id = str(target_semantic_id).strip()
    if node_id:
        for row in graph_rows:
            nodes = list((dict(row or {})).get("nodes") or [])
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                if str(node.get("node_id", "")).strip() == node_id:
                    return dict(row)
    return dict(graph_rows[0]) if graph_rows else {}


def _interior_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    del runtime
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    sections = dict((dict(inspection_snapshot or {})).get("summary_sections") or {})
    connectivity_data = dict((dict(sections.get("section.interior.connectivity_summary") or {})).get("data") or {})
    layout_data = connectivity_data or dict((dict(sections.get("section.interior.layout") or {})).get("data") or {})
    portal_data = dict((dict(sections.get("section.interior.portal_state_table") or {})).get("data") or {})
    if not portal_data:
        portal_data = dict((dict(sections.get("section.interior.portal_states") or {})).get("data") or {})
    pressure_data = dict((dict(sections.get("section.interior.pressure_summary") or {})).get("data") or {})
    if not pressure_data:
        pressure_data = dict((dict(sections.get("section.interior.pressure_map") or {})).get("data") or {})
    flood_data = dict((dict(sections.get("section.interior.flood_summary") or {})).get("data") or {})
    if not flood_data:
        flood_data = dict((dict(sections.get("section.interior.flood_map") or {})).get("data") or {})
    smoke_data = dict((dict(sections.get("section.interior.smoke_summary") or {})).get("data") or {})
    leak_data = dict((dict(sections.get("section.interior.flow_summary") or {})).get("data") or {})
    if not leak_data:
        leak_data = dict((dict(sections.get("section.interior.portal_leaks") or {})).get("data") or {})

    graph_id = (
        str(layout_data.get("graph_id", "")).strip()
        or str(portal_data.get("graph_id", "")).strip()
        or str(target_row.get("graph_id", "")).strip()
        or str(target_semantic_id).strip()
    )
    available = bool(layout_data.get("available", False)) or bool(portal_data.get("available", False))
    if not available:
        return {
            "mode": "interior_overlay",
            "summary": "interior:{} unavailable".format(graph_id or str(target_semantic_id)),
            "target_semantic_id": str(target_semantic_id),
            "inspection_snapshot": dict(inspection_snapshot or {}),
            "renderables": _overlay_renderables(
                target_semantic_id=str(target_semantic_id),
                summary_label="interior unavailable",
                mode="interior_overlay",
            ),
            "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
            "degraded": True,
            "extensions": {"overlay_kind": "interior", "collection": collection, "graph_status": "missing"},
        }

    volume_count = max(0, _to_int(layout_data.get("volume_count", 0), 0))
    portal_states = sorted(
        [dict(item) for item in list(portal_data.get("portal_states") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("portal_id", "")),
    )
    portal_count = max(len(portal_states), max(0, _to_int(layout_data.get("portal_count", 0), 0)))
    pressure_rows = sorted(
        [dict(item) for item in list(pressure_data.get("rows") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("volume_id", "")),
    )
    flood_rows = sorted(
        [dict(item) for item in list(flood_data.get("rows") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("volume_id", "")),
    )
    leak_rows = sorted(
        [dict(item) for item in list(leak_data.get("leaks") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("leak_id", "")),
    )
    portal_flow_rows = sorted(
        [dict(item) for item in list(leak_data.get("portal_flow_rows") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("portal_id", "")),
    )
    pressure_by_volume = {
        str(row.get("volume_id", "")).strip(): int(max(0, _to_int(row.get("derived_pressure", 0), 0)))
        for row in pressure_rows
        if str(row.get("volume_id", "")).strip()
    }
    flood_by_volume = {
        str(row.get("volume_id", "")).strip(): int(max(0, _to_int(row.get("water_volume", 0), 0)))
        for row in flood_rows
        if str(row.get("volume_id", "")).strip()
    }
    smoke_rows = sorted(
        [dict(item) for item in list(smoke_data.get("rows") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("volume_id", "")),
    )
    smoke_by_volume = {
        str(row.get("volume_id", "")).strip(): int(max(0, _to_int(row.get("smoke_density", 0), 0)))
        for row in (smoke_rows or flood_rows)
        if str(row.get("volume_id", "")).strip()
    }
    indexed_volume_ids = [
        str(token).strip()
        for token in sorted(
            set(
                list(pressure_by_volume.keys())
                + list(flood_by_volume.keys())
                + [
                    str(item.get("volume_id", "")).strip()
                    for item in list(portal_states or [])
                    if str(item.get("from_volume_id", "")).strip()
                ]
            )
        )
        if str(token).strip()
    ]
    if not indexed_volume_ids and volume_count > 0:
        indexed_volume_ids = ["volume.{:04d}".format(index) for index in range(int(volume_count))]

    volume_material_id = "mat.inspect.interior.volume.{}".format(canonical_sha256({"graph_id": graph_id, "kind": "volume"})[:12])
    volume_warn_material_id = "mat.inspect.interior.volume.warn.{}".format(
        canonical_sha256({"graph_id": graph_id, "kind": "volume_warn"})[:12]
    )
    volume_danger_material_id = "mat.inspect.interior.volume.danger.{}".format(
        canonical_sha256({"graph_id": graph_id, "kind": "volume_danger"})[:12]
    )
    volume_flood_material_id = "mat.inspect.interior.volume.flood.{}".format(
        canonical_sha256({"graph_id": graph_id, "kind": "volume_flood"})[:12]
    )
    portal_open_material_id = "mat.inspect.interior.portal.open.{}".format(canonical_sha256({"graph_id": graph_id, "kind": "portal_open"})[:12])
    portal_closed_material_id = "mat.inspect.interior.portal.closed.{}".format(canonical_sha256({"graph_id": graph_id, "kind": "portal_closed"})[:12])
    leak_material_id = "mat.inspect.interior.leak.{}".format(canonical_sha256({"graph_id": graph_id, "kind": "leak"})[:12])

    materials = _overlay_materials(target_semantic_id=str(target_semantic_id))
    materials.extend(
        [
            {
                "schema_version": "1.0.0",
                "material_id": volume_material_id,
                "base_color": _color_from_seed({"graph_id": graph_id, "kind": "volume"}, floor=72),
                "roughness": 320,
                "metallic": 0,
                "emission": None,
                "transparency": 220,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_volume"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": volume_warn_material_id,
                "base_color": {"r": 239, "g": 186, "b": 70},
                "roughness": 300,
                "metallic": 0,
                "emission": {"r": 239, "g": 186, "b": 70, "strength": 220},
                "transparency": 220,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_volume_warn"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": volume_danger_material_id,
                "base_color": {"r": 229, "g": 93, "b": 86},
                "roughness": 280,
                "metallic": 0,
                "emission": {"r": 229, "g": 93, "b": 86, "strength": 280},
                "transparency": 220,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_volume_danger"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": volume_flood_material_id,
                "base_color": {"r": 70, "g": 132, "b": 228},
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": 70, "g": 132, "b": 228, "strength": 260},
                "transparency": 190,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_volume_flood"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": portal_open_material_id,
                "base_color": {"r": 86, "g": 214, "b": 124},
                "roughness": 280,
                "metallic": 0,
                "emission": {"r": 86, "g": 214, "b": 124, "strength": 320},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_portal_open"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": portal_closed_material_id,
                "base_color": {"r": 220, "g": 98, "b": 84},
                "roughness": 280,
                "metallic": 0,
                "emission": {"r": 220, "g": 98, "b": 84, "strength": 300},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_portal_closed"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": leak_material_id,
                "base_color": {"r": 214, "g": 84, "b": 170},
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": 214, "g": 84, "b": 170, "strength": 320},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "interior_leak"},
            },
        ]
    )
    materials = sorted(
        [dict(item) for item in materials if isinstance(item, dict)],
        key=lambda row: str(row.get("material_id", "")),
    )

    renderables = _overlay_renderables(
        target_semantic_id=str(target_semantic_id),
        summary_label="interior:{} volumes={} portals={} leaks={}".format(
            graph_id,
            volume_count,
            portal_count,
            len(leak_rows),
        ),
        mode="interior_overlay",
    )
    max_volume_markers = max(0, _to_int((dict(target_row.get("extensions") or {})).get("max_volume_markers", 128), 128))
    for index, volume_id in enumerate(indexed_volume_ids[: max(0, min(max_volume_markers, max(volume_count, len(indexed_volume_ids))))]):
        pressure = int(max(0, _to_int(pressure_by_volume.get(volume_id, 0), 0)))
        flood = int(max(0, _to_int(flood_by_volume.get(volume_id, 0), 0)))
        smoke = int(max(0, _to_int(smoke_by_volume.get(volume_id, 0), 0)))
        if flood >= 600:
            volume_material = volume_flood_material_id
            severity = "flood"
        elif pressure > 0 and pressure <= 100:
            volume_material = volume_danger_material_id
            severity = "danger"
        elif flood >= 200 or (pressure > 0 and pressure <= 200) or smoke >= 200:
            volume_material = volume_warn_material_id
            severity = "warn"
        else:
            volume_material = volume_material_id
            severity = "ok"
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.interior.volume.{}".format(
                    canonical_sha256({"graph_id": graph_id, "volume_id": volume_id})[:16]
                ),
                "semantic_id": "overlay.inspect.interior.volume.{}".format(volume_id),
                "primitive_id": "prim.box.debug",
                "transform": {
                    "position_mm": {"x": int(index * 1500), "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": volume_material,
                "layer_tags": ["overlay", "ui"],
                "label": "{} P:{} W:{}".format(volume_id, pressure, flood),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "interior_volume",
                    "volume_id": volume_id,
                    "derived_pressure": int(pressure),
                    "water_volume": int(flood),
                    "smoke_density": int(smoke),
                    "severity": severity,
                },
            }
        )
    for index, portal in enumerate(portal_states[:256]):
        portal_id = str(portal.get("portal_id", "")).strip()
        state_id = str(portal.get("state_id", "")).strip() or "unknown"
        is_open = state_id in {"open", "opening", "unlocked", "permeable"}
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.interior.portal.{}".format(canonical_sha256({"graph_id": graph_id, "portal_id": portal_id})[:16]),
                "semantic_id": "overlay.inspect.interior.portal.{}".format(portal_id or str(index).zfill(4)),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": int(index * 1500), "y": 1200, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": portal_open_material_id if is_open else portal_closed_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "{} ({})".format(portal_id or "portal", state_id),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "interior_portal_state",
                    "state_id": state_id,
                },
            }
        )
    for index, leak in enumerate(leak_rows[:128]):
        leak_id = str(leak.get("leak_id", "")).strip() or "leak.{}".format(index)
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.interior.leak.{}".format(
                    canonical_sha256({"graph_id": graph_id, "leak_id": leak_id})[:16]
                ),
                "semantic_id": "overlay.inspect.interior.leak.{}".format(leak_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": int(index * 1500), "y": 2400, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": leak_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "{} A:{} W:{}".format(
                    leak_id,
                    int(max(0, _to_int(leak.get("leak_rate_air", 0), 0))),
                    int(max(0, _to_int(leak.get("leak_rate_water", 0), 0))),
                ),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": True},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "interior_leak",
                    "leak_id": leak_id,
                    "volume_id": str(leak.get("volume_id", "")).strip(),
                },
            }
        )
    for index, portal_flow in enumerate(portal_flow_rows[:128]):
        portal_id = str(portal_flow.get("portal_id", "")).strip()
        if not portal_id:
            continue
        sealing = int(max(0, _to_int(portal_flow.get("sealing_coefficient", 0), 0)))
        conductance = int(
            max(
                0,
                _to_int(portal_flow.get("conductance_air", 0), 0)
                + _to_int(portal_flow.get("conductance_smoke", 0), 0)
                + _to_int(portal_flow.get("conductance_water", 0), 0),
            )
        )
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.interior.portal.flow.{}".format(
                    canonical_sha256({"graph_id": graph_id, "portal_id": portal_id, "flow": True})[:16]
                ),
                "semantic_id": "overlay.inspect.interior.portal.flow.{}".format(portal_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": int(index * 1500), "y": 3600, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": leak_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "{} C:{} S:{}".format(portal_id, conductance, sealing),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "interior_portal_flow",
                    "portal_id": portal_id,
                    "conductance_total": conductance,
                    "sealing_coefficient": sealing,
                },
            }
        )
    for index, smoke in enumerate(smoke_rows[:128]):
        volume_id = str(smoke.get("volume_id", "")).strip()
        smoke_density = int(max(0, _to_int(smoke.get("smoke_density", 0), 0)))
        if not volume_id or smoke_density < 200:
            continue
        severity = "DANGER" if smoke_density >= 450 else "WARN"
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.interior.smoke.{}".format(
                    canonical_sha256({"graph_id": graph_id, "volume_id": volume_id, "smoke": True})[:16]
                ),
                "semantic_id": "overlay.inspect.interior.smoke.{}".format(volume_id),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": int(index * 1500), "y": 4800, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": leak_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": "SMOKE {} {}".format(severity, volume_id),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": True},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "interior_smoke_alarm",
                    "volume_id": volume_id,
                    "smoke_density": smoke_density,
                    "severity": severity,
                },
            }
        )
    renderables = sorted(
        [dict(item) for item in renderables if isinstance(item, dict)],
        key=lambda row: str(row.get("renderable_id", "")),
    )

    return {
        "mode": "interior_overlay",
        "summary": "interior:{} volumes={} portals={}".format(graph_id, volume_count, portal_count),
        "target_semantic_id": str(target_semantic_id),
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": renderables,
        "materials": materials,
        "degraded": False,
        "extensions": {
            "overlay_kind": "interior",
            "collection": collection,
            "graph_id": graph_id,
            "volume_count": int(volume_count),
            "portal_count": int(portal_count),
            "pressure_volume_count": len(pressure_rows),
            "flooded_count": int(max(0, _to_int(flood_data.get("flooded_count", 0), 0))),
            "smoke_warn_count": len(
                [row for row in smoke_rows if int(max(0, _to_int(row.get("smoke_density", 0), 0))) >= 200]
            ),
            "leak_count": len(leak_rows),
        },
    }


def _logistics_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    repo_root = str(runtime.get("repo_root", "")).strip()
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    graph_rows = _logistics_graph_rows(runtime, repo_root)
    graph_row = _logistics_graph_for_target(graph_rows, target_row=target_row, target_semantic_id=target_semantic_id)
    if not graph_row:
        return {
            "mode": "macro_summary",
            "summary": "logistics:{} unavailable".format(str(target_semantic_id)),
            "target_semantic_id": str(target_semantic_id),
            "inspection_snapshot": dict(inspection_snapshot or {}),
            "renderables": _overlay_renderables(
                target_semantic_id=str(target_semantic_id),
                summary_label="logistics unavailable",
                mode="macro_summary",
            ),
            "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
            "degraded": True,
            "extensions": {"overlay_kind": "logistics", "graph_status": "missing"},
        }

    graph_id = str(graph_row.get("graph_id", "")).strip()
    edge_rows = sorted(
        [dict(item) for item in list((dict(graph_row or {})).get("edges") or []) if isinstance(item, dict)],
        key=lambda item: str(item.get("edge_id", "")),
    )
    sections = dict((dict(inspection_snapshot or {})).get("summary_sections") or {})
    flow_util_section = dict(sections.get("section.flow_utilization") or {})
    flow_util_data = dict(flow_util_section.get("data") or {})
    flow_util_edges = {
        str(item.get("edge_id", "")).strip(): dict(item)
        for item in list(flow_util_data.get("edges") or [])
        if isinstance(item, dict) and str(item.get("edge_id", "")).strip()
    }
    route_edge_ids = _sorted_unique_strings(
        list((dict(target_row.get("extensions") or {})).get("route_edge_ids") or [])
    )
    material_id = str(target_row.get("material_id", "")).strip() or "material.unknown"
    flow_color = _color_from_seed({"material_id": material_id, "kind": "flow"}, floor=72)
    flow_material_id = "mat.inspect.logistics.flow.{}".format(canonical_sha256({"material_id": material_id})[:12])
    node_material_id = "mat.inspect.logistics.node.{}".format(canonical_sha256({"target": target_semantic_id})[:12])
    util_bucket_materials = {}
    for edge_id in sorted(str(item.get("edge_id", "")).strip() for item in edge_rows if str(item.get("edge_id", "")).strip()):
        util_row = dict(flow_util_edges.get(edge_id) or {})
        util_permille = max(0, min(1000, _to_int(util_row.get("utilization_permille", 0), 0)))
        bucket = int(util_permille // 200)
        if bucket not in util_bucket_materials:
            # Deterministic green->red bucket palette for utilization.
            green = max(40, 220 - (bucket * 32))
            red = min(235, 52 + (bucket * 36))
            blue = max(32, 80 - (bucket * 6))
            util_bucket_materials[bucket] = {
                "schema_version": "1.0.0",
                "material_id": "mat.inspect.logistics.edge.util.{}.{}".format(bucket, canonical_sha256({"graph_id": graph_id, "bucket": bucket})[:8]),
                "base_color": {"r": red, "g": green, "b": blue},
                "roughness": 360,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "logistics_edge_utilization", "utilization_bucket": bucket},
            }
    default_edge_material_id = "mat.inspect.logistics.edge.default.{}".format(canonical_sha256({"graph_id": graph_id, "default": True})[:12])
    materials = [
        {
            "schema_version": "1.0.0",
            "material_id": default_edge_material_id,
            "base_color": _color_from_seed({"graph_id": graph_id, "kind": "edge.default"}, floor=58),
            "roughness": 360,
            "metallic": 0,
            "emission": None,
            "transparency": None,
            "pattern_id": None,
            "extensions": {"interaction_overlay": True, "overlay_kind": "logistics_edge"},
        },
        {
            "schema_version": "1.0.0",
            "material_id": flow_material_id,
            "base_color": dict(flow_color),
            "roughness": 220,
            "metallic": 0,
            "emission": {"r": flow_color["r"], "g": flow_color["g"], "b": flow_color["b"], "strength": 280},
            "transparency": None,
            "pattern_id": None,
            "extensions": {"interaction_overlay": True, "overlay_kind": "logistics_flow"},
        },
        {
            "schema_version": "1.0.0",
            "material_id": node_material_id,
            "base_color": _color_from_seed({"target": target_semantic_id, "kind": "node"}, floor=80),
            "roughness": 180,
            "metallic": 0,
            "emission": None,
            "transparency": None,
            "pattern_id": None,
            "extensions": {"interaction_overlay": True, "overlay_kind": "logistics_node"},
        },
    ] + [dict(util_bucket_materials[key]) for key in sorted(util_bucket_materials.keys())]
    materials = sorted(materials, key=lambda row: str(row.get("material_id", "")))

    renderables: list[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        util_row = dict(flow_util_edges.get(edge_id) or {})
        util_permille = max(0, min(1000, _to_int(util_row.get("utilization_permille", 0), 0)))
        util_bucket = int(util_permille // 200)
        edge_material_id = str(
            (dict(util_bucket_materials.get(util_bucket) or {})).get("material_id", "")
        ).strip() or default_edge_material_id
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.logistics.edge.{}".format(canonical_sha256({"edge_id": edge_id})[:16]),
                "semantic_id": "overlay.inspect.logistics.edge.{}".format(edge_id),
                "primitive_id": "prim.line.debug",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": edge_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "logistics_edge",
                    "edge_id": edge_id,
                    "from_node_id": str(edge.get("from_node_id", "")).strip(),
                    "to_node_id": str(edge.get("to_node_id", "")).strip(),
                    "utilization_permille": int(util_permille),
                },
            }
        )
        if edge_id in set(route_edge_ids):
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.logistics.flow.{}".format(canonical_sha256({"edge_id": edge_id, "flow": True})[:16]),
                    "semantic_id": "overlay.inspect.logistics.flow.{}".format(edge_id),
                    "primitive_id": "prim.line.debug",
                    "transform": {
                        "position_mm": {"x": 0, "y": 0, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 1000,
                    },
                    "material_id": flow_material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": None,
                    "lod_hint": "lod.band.mid",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "logistics_flow_arrow",
                        "edge_id": edge_id,
                        "animated": True,
                        "phase_tick": int(max(0, _to_int((dict(runtime.get("time_state") or {})).get("tick", 0), 0))),
                    },
                }
            )

    summary_bits = []
    summary_bits.append("graph={}".format(graph_id or "none"))
    summary_bits.append("edges={}".format(len(edge_rows)))
    if flow_util_data:
        summary_bits.append(
            "util={}".format(int(max(0, _to_int(flow_util_data.get("utilization_permille", 0), 0))))
        )
    if collection == "logistics_node_inventories":
        stocks = dict((dict(target_row or {})).get("material_stocks") or {})
        summary_bits.append("materials={}".format(len(stocks.keys())))
    if collection == "logistics_manifests":
        summary_bits.append("route_edges={}".format(len(route_edge_ids)))
        summary_bits.append("status={}".format(str(target_row.get("status", "planned")).strip() or "planned"))
    summary_label = "logistics:{} {}".format(str(target_semantic_id), " ".join(summary_bits))

    return {
        "mode": "logistics_overlay",
        "summary": summary_label,
        "target_semantic_id": str(target_semantic_id),
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "logistics",
            "graph_id": graph_id,
            "collection": collection,
            "route_edge_ids": list(route_edge_ids),
            "material_id": material_id,
            "flow_utilization_edge_count": len(flow_util_edges.keys()),
        },
    }


def _blueprint_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
) -> Dict[str, object]:
    repo_root = str(runtime.get("repo_root", "")).strip()
    blueprint_id = str(target_semantic_id).strip()
    blueprint_registry = _resolve_registry(runtime, "blueprint_registry", repo_root, "data/registries/blueprint_registry.json")
    part_class_registry = _resolve_registry(runtime, "part_class_registry", repo_root, "data/registries/part_class_registry.json")
    connection_type_registry = _resolve_registry(runtime, "connection_type_registry", repo_root, "data/registries/connection_type_registry.json")
    material_class_registry = _resolve_registry(runtime, "material_class_registry", repo_root, "data/registries/material_class_registry.json")
    if not blueprint_registry or not part_class_registry or not connection_type_registry:
        return {
            "mode": "macro_summary",
            "summary": "blueprint:{} unavailable".format(blueprint_id),
            "target_semantic_id": blueprint_id,
            "inspection_snapshot": {},
            "renderables": _overlay_renderables(
                target_semantic_id=blueprint_id,
                summary_label="blueprint unavailable",
                mode="macro_summary",
            ),
            "materials": _overlay_materials(target_semantic_id=blueprint_id),
            "degraded": True,
            "extensions": {"blueprint_id": blueprint_id, "compile_status": "registry_missing"},
        }

    try:
        compiled = compile_blueprint_artifacts(
            repo_root=repo_root or os.getcwd(),
            blueprint_id=blueprint_id,
            parameter_values={},
            pack_lock_hash=str(runtime.get("pack_lock_hash", "")).strip() or "pack_lock_hash.overlay",
            blueprint_registry=blueprint_registry,
            part_class_registry=part_class_registry,
            connection_type_registry=connection_type_registry,
            material_class_registry=material_class_registry,
        )
    except BlueprintCompileError as exc:
        return {
            "mode": "macro_summary",
            "summary": "blueprint:{} refused".format(blueprint_id),
            "target_semantic_id": blueprint_id,
            "inspection_snapshot": {},
            "renderables": _overlay_renderables(
                target_semantic_id=blueprint_id,
                summary_label="compile refused",
                mode="macro_summary",
            ),
            "materials": _overlay_materials(target_semantic_id=blueprint_id),
            "degraded": True,
            "extensions": {
                "blueprint_id": blueprint_id,
                "compile_status": "refused",
                "reason_code": str(exc.reason_code),
                "details": dict(exc.details),
            },
        }

    summary = blueprint_bom_summary(dict(compiled.get("compiled_bom_artifact") or {}))
    ghost = build_blueprint_ghost_overlay(
        compiled_ag_artifact=dict(compiled.get("compiled_ag_artifact") or {}),
        blueprint_id=blueprint_id,
        include_labels=bool(runtime.get("blueprint_preview_labels", True)),
    )
    return {
        "mode": "blueprint_preview",
        "summary": "blueprint:{} ghost".format(blueprint_id),
        "target_semantic_id": blueprint_id,
        "inspection_snapshot": {
            "summary_hash": str(summary.get("summary_hash", "")),
            "total_mass_raw": int(summary.get("total_mass_raw", 0) or 0),
            "total_part_count": int(summary.get("total_part_count", 0) or 0),
        },
        "renderables": list(ghost.get("renderables") or []),
        "materials": list(ghost.get("materials") or []),
        "degraded": False,
        "extensions": {
            "blueprint_id": blueprint_id,
            "cache_key": str(compiled.get("cache_key", "")),
            "bom_summary": summary,
            "compiled_bom_hash": str((dict(compiled.get("compiled_bom_artifact") or {})).get("artifact_hash", "")),
            "compiled_ag_hash": str((dict(compiled.get("compiled_ag_artifact") or {})).get("artifact_hash", "")),
        },
    }


def _plan_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    snapshot = dict(inspection_snapshot or {})
    payload = dict(snapshot.get("target_payload") or {})
    collection = str(payload.get("collection", "")).strip()
    row = dict(payload.get("row") or {})
    plan_id = str(row.get("plan_id", "")).strip() or str(target_semantic_id).strip()
    if collection != "plan_artifacts" or not row:
        return {
            "mode": "macro_summary",
            "summary": "plan:{} unavailable".format(plan_id or "unknown"),
            "target_semantic_id": str(target_semantic_id),
            "inspection_snapshot": dict(snapshot),
            "renderables": _overlay_renderables(
                target_semantic_id=str(target_semantic_id),
                summary_label="plan unavailable",
                mode="macro_summary",
            ),
            "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
            "degraded": True,
            "extensions": {"overlay_kind": "plan_ghost", "available": False},
        }

    preview = dict(row.get("spatial_preview_data") or {})
    preview_renderables = [dict(item) for item in list(preview.get("renderables") or []) if isinstance(item, dict)]
    preview_materials = [dict(item) for item in list(preview.get("materials") or []) if isinstance(item, dict)]
    resources = dict(row.get("required_resources_summary") or {})
    if not preview_renderables:
        return {
            "mode": "plan_preview",
            "summary": "plan:{} empty_preview".format(plan_id),
            "target_semantic_id": str(target_semantic_id),
            "inspection_snapshot": dict(snapshot),
            "renderables": _overlay_renderables(
                target_semantic_id=str(target_semantic_id),
                summary_label="empty plan preview",
                mode="plan_preview",
            ),
            "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
            "degraded": False,
            "extensions": {
                "overlay_kind": "plan_ghost",
                "available": True,
                "plan_id": plan_id,
            },
        }

    material_rows: Dict[str, dict] = {}
    for row_material in preview_materials:
        material_id = str(row_material.get("material_id", "")).strip()
        if not material_id:
            continue
        seeded_color = _color_from_seed({"plan_id": plan_id, "material_id": material_id}, floor=70)
        material_rows[material_id] = {
            **dict(row_material),
            "material_id": material_id,
            "base_color": dict(seeded_color),
            "roughness": 300,
            "metallic": 0,
            "emission": {
                "r": int(seeded_color["r"]),
                "g": int(seeded_color["g"]),
                "b": int(seeded_color["b"]),
                "strength": 180,
            },
            "transparency": {"alpha_permille": 620},
            "extensions": {
                **dict(row_material.get("extensions") or {}),
                "interaction_overlay": True,
                "overlay_kind": "plan_ghost_material",
                "derived_only": True,
            },
        }
    if not material_rows:
        fallback_material_id = "mat.plan.ghost.{}".format(canonical_sha256({"plan_id": plan_id})[:12])
        color = _color_from_seed({"plan_id": plan_id, "kind": "fallback"}, floor=72)
        material_rows[fallback_material_id] = {
            "schema_version": "1.0.0",
            "material_id": fallback_material_id,
            "base_color": dict(color),
            "roughness": 320,
            "metallic": 0,
            "emission": {"r": color["r"], "g": color["g"], "b": color["b"], "strength": 160},
            "transparency": {"alpha_permille": 620},
            "pattern_id": None,
            "extensions": {"interaction_overlay": True, "overlay_kind": "plan_ghost_material", "derived_only": True},
        }

    default_material_id = sorted(material_rows.keys())[0]
    renderables = []
    for index, row_renderable in enumerate(sorted(preview_renderables, key=lambda item: str(item.get("renderable_id", "")))):
        renderable_id = str(row_renderable.get("renderable_id", "")).strip() or "overlay.plan.ghost.{}".format(str(index).zfill(4))
        material_id = str(row_renderable.get("material_id", "")).strip()
        if material_id not in material_rows:
            material_id = default_material_id
        renderable = dict(row_renderable)
        renderable["renderable_id"] = "overlay.plan.ghost.{}".format(
            canonical_sha256({"plan_id": plan_id, "renderable_id": renderable_id})[:16]
        )
        renderable["semantic_id"] = "overlay.plan.ghost.{}".format(renderable_id)
        renderable["material_id"] = material_id
        renderable["layer_tags"] = ["overlay", "ui", "ghost"]
        renderable["flags"] = {"selectable": False, "highlighted": False}
        renderable["extensions"] = {
            **dict(row_renderable.get("extensions") or {}),
            "interaction_overlay": True,
            "overlay_kind": "plan_ghost",
            "plan_id": plan_id,
            "derived_only": True,
        }
        renderables.append(renderable)

    return {
        "mode": "plan_preview",
        "summary": "plan:{} ghost type={} status={}".format(
            plan_id,
            str(row.get("plan_type_id", "")).strip() or "custom",
            str(row.get("status", "")).strip() or "draft",
        ),
        "target_semantic_id": str(target_semantic_id),
        "inspection_snapshot": dict(snapshot),
        "renderables": sorted(renderables, key=lambda item: str(item.get("renderable_id", ""))),
        "materials": [dict(material_rows[key]) for key in sorted(material_rows.keys())],
        "degraded": False,
        "extensions": {
            "overlay_kind": "plan_ghost",
            "available": True,
            "derived_only": True,
            "plan_id": plan_id,
            "plan_type_id": str(row.get("plan_type_id", "")).strip() or "custom",
            "status": str(row.get("status", "")).strip() or "draft",
            "resource_summary": {
                "total_mass_raw": int(max(0, _to_int(resources.get("total_mass_raw", 0), 0))),
                "total_part_count": int(max(0, _to_int(resources.get("total_part_count", 0), 0))),
            },
        },
    }


def _formalization_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    snapshot = dict(inspection_snapshot or {})
    payload = dict(snapshot.get("target_payload") or {})
    row = dict(payload.get("row") or {})
    sections = dict(snapshot.get("summary_sections") or {})
    formalization_section = dict(sections.get("section.formalization_summary") or {})
    formalization_data = dict(formalization_section.get("data") or {})
    candidate_section = dict(sections.get("section.formalization_candidates") or {})
    candidate_data = dict(candidate_section.get("data") or {})

    formalization_id = (
        str(formalization_data.get("formalization_id", "")).strip()
        or str(row.get("formalization_id", "")).strip()
        or str(target_semantic_id).strip()
    )
    state_token = str(formalization_data.get("state", "")).strip() or str(row.get("state", "")).strip() or "raw"
    candidate_count = int(max(0, _to_int(candidate_data.get("candidate_count", formalization_data.get("candidate_count", 0)), 0)))
    spec_id = str(formalization_data.get("spec_id", "")).strip() or str(row.get("spec_id", "")).strip() or None
    network_graph_ref = str(formalization_data.get("network_graph_ref", "")).strip() or str(row.get("network_graph_ref", "")).strip() or None
    inferred_rows = [dict(item) for item in list(candidate_data.get("rows") or []) if isinstance(item, dict)]
    redaction = str(candidate_data.get("epistemic_redaction", "")).strip() or str(formalization_data.get("epistemic_redaction", "")).strip() or "unknown"

    if not formalization_id:
        return {
            "mode": "formalization_overlay",
            "summary": "formalization:unavailable",
            "target_semantic_id": str(target_semantic_id),
            "inspection_snapshot": dict(snapshot),
            "renderables": _overlay_renderables(
                target_semantic_id=str(target_semantic_id),
                summary_label="formalization unavailable",
                mode="formalization_overlay",
            ),
            "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
            "degraded": True,
            "extensions": {"overlay_kind": "formalization", "state": "missing"},
        }

    state_material_id = "mat.inspect.formalization.state.{}".format(canonical_sha256({"formalization_id": formalization_id})[:12])
    candidate_material_id = "mat.inspect.formalization.inferred.{}".format(
        canonical_sha256({"formalization_id": formalization_id, "candidate": True})[:12]
    )
    state_color = _color_from_seed({"formalization_id": formalization_id, "state": state_token}, floor=72)
    candidate_color = _color_from_seed({"formalization_id": formalization_id, "candidate_count": candidate_count}, floor=58)
    materials = sorted(
        _overlay_materials(target_semantic_id=formalization_id)
        + [
            {
                "schema_version": "1.0.0",
                "material_id": state_material_id,
                "base_color": dict(state_color),
                "roughness": 260,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "formalization_state"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": candidate_material_id,
                "base_color": dict(candidate_color),
                "roughness": 180,
                "metallic": 0,
                "emission": {
                    "r": candidate_color["r"],
                    "g": candidate_color["g"],
                    "b": candidate_color["b"],
                    "strength": 240,
                },
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "formalization_candidate"},
            },
        ],
        key=lambda item: str(item.get("material_id", "")),
    )

    summary_bits = ["state={}".format(state_token), "candidates={}".format(candidate_count)]
    if spec_id:
        summary_bits.append("spec=bound")
    if network_graph_ref:
        summary_bits.append("networked")
    summary_label = "formalize:{} {}".format(formalization_id, " ".join(summary_bits))
    renderables = _overlay_renderables(
        target_semantic_id=formalization_id,
        summary_label=summary_label,
        mode="formalization_overlay",
    )
    renderables.append(
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.formalization.state.{}".format(
                canonical_sha256({"formalization_id": formalization_id, "state": state_token})[:16]
            ),
            "semantic_id": "overlay.inspect.formalization.state.{}".format(formalization_id),
            "primitive_id": "prim.glyph.node",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1100,
            },
            "material_id": state_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": None,
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": state_token in {"formal", "networked"}},
            "extensions": {
                "interaction_overlay": True,
                "overlay_kind": "formalization_state",
                "formalization_id": formalization_id,
                "state": state_token,
            },
        }
    )

    if state_token == "inferred":
        for index, candidate in enumerate(inferred_rows[:16]):
            candidate_id = str(candidate.get("candidate_id", "")).strip()
            if not candidate_id:
                continue
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.formalization.candidate.{}".format(
                        canonical_sha256({"formalization_id": formalization_id, "candidate_id": candidate_id})[:16]
                    ),
                    "semantic_id": "overlay.inspect.formalization.candidate.{}".format(candidate_id),
                    "primitive_id": "prim.line.debug",
                    "transform": {
                        "position_mm": {"x": int(index) * 120, "y": 160, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 1000,
                    },
                    "material_id": candidate_material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": None,
                    "lod_hint": "lod.band.mid",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "formalization_candidate",
                        "formalization_id": formalization_id,
                        "candidate_id": candidate_id,
                        "geometry_preview_ref": str(candidate.get("geometry_preview_ref", "")).strip() or None,
                    },
                }
            )

    return {
        "mode": "formalization_overlay",
        "summary": summary_label,
        "target_semantic_id": formalization_id,
        "inspection_snapshot": dict(snapshot),
        "renderables": sorted(renderables, key=lambda item: str(item.get("renderable_id", ""))),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "formalization",
            "formalization_id": formalization_id,
            "state": state_token,
            "candidate_count": int(candidate_count),
            "spec_id": spec_id,
            "network_graph_ref": network_graph_ref,
            "epistemic_redaction": redaction,
        },
    }


def _guide_geometry_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    snapshot = dict(inspection_snapshot or {})
    payload = dict(snapshot.get("target_payload") or {})
    row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    target_id = str(target_semantic_id).strip()

    if collection == "mobility_junctions":
        junction_id = str(row.get("junction_id", "")).strip() or target_id
        connected_ids = _sorted_unique_strings(row.get("connected_geometry_ids"))
        point = _point_mm(dict(row.get("extensions") or {}).get("position_mm")) or {"x": 0, "y": 0, "z": 0}
        material_id = "mat.inspect.geometry.junction.{}".format(canonical_sha256({"junction_id": junction_id})[:12])
        summary = "junction:{} links={}".format(junction_id or "unknown", int(len(connected_ids)))
        return {
            "mode": "guide_geometry_overlay",
            "summary": summary,
            "target_semantic_id": target_id,
            "inspection_snapshot": dict(snapshot),
            "renderables": [
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.geometry.junction.{}".format(
                        canonical_sha256({"junction_id": junction_id})[:16]
                    ),
                    "semantic_id": "overlay.inspect.geometry.junction.{}".format(junction_id),
                    "primitive_id": "prim.glyph.node",
                    "transform": {
                        "position_mm": dict(point),
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 1100,
                    },
                    "material_id": material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": None,
                    "lod_hint": "lod.band.near",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "guide_junction",
                        "junction_id": junction_id or None,
                        "connected_geometry_ids": list(connected_ids),
                    },
                }
            ],
            "materials": [
                {
                    "schema_version": "1.0.0",
                    "material_id": material_id,
                    "base_color": _color_from_seed({"junction_id": junction_id, "kind": "junction"}, floor=70),
                    "roughness": 200,
                    "metallic": 0,
                    "emission": {"r": 206, "g": 236, "b": 122, "strength": 220},
                    "transparency": None,
                    "pattern_id": None,
                    "extensions": {"interaction_overlay": True, "overlay_kind": "guide_junction"},
                }
            ],
            "degraded": False,
            "extensions": {
                "overlay_kind": "guide_geometry",
                "collection": collection,
                "junction_id": junction_id or None,
                "connected_geometry_ids": list(connected_ids),
            },
        }

    geometry_row = {}
    if collection == "guide_geometries":
        geometry_row = dict(row)
    elif target_id.startswith("geometry.") and str(row.get("geometry_id", "")).strip():
        geometry_row = dict(row)
    geometry_id = str(geometry_row.get("geometry_id", "")).strip() or target_id
    if not geometry_row:
        return {
            "mode": "guide_geometry_overlay",
            "summary": "guide:{} unavailable".format(target_id or "unknown"),
            "target_semantic_id": target_id,
            "inspection_snapshot": dict(snapshot),
            "renderables": _overlay_renderables(
                target_semantic_id=target_id,
                summary_label="guide geometry unavailable",
                mode="guide_geometry_overlay",
            ),
            "materials": _overlay_materials(target_semantic_id=target_id),
            "degraded": True,
            "extensions": {"overlay_kind": "guide_geometry", "available": False},
        }

    geometry_type_id = str(geometry_row.get("geometry_type_id", "")).strip() or "geo.spline1D"
    points = _geometry_points_mm(geometry_row)
    bounds = dict(geometry_row.get("bounds") or {})
    min_mm = _point_mm(bounds.get("min_mm")) or {"x": 0, "y": 0, "z": 0}
    max_mm = _point_mm(bounds.get("max_mm")) or {"x": 0, "y": 0, "z": 0}
    junction_refs = _sorted_unique_strings(geometry_row.get("junction_refs"))

    line_material_id = "mat.inspect.geometry.line.{}".format(canonical_sha256({"geometry_id": geometry_id})[:12])
    shell_material_id = "mat.inspect.geometry.shell.{}".format(
        canonical_sha256({"geometry_id": geometry_id, "shell": True})[:12]
    )
    junction_material_id = "mat.inspect.geometry.junction_ref.{}".format(
        canonical_sha256({"geometry_id": geometry_id, "junction_ref": True})[:12]
    )
    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": line_material_id,
                "base_color": _color_from_seed({"geometry_id": geometry_id, "kind": "line"}, floor=72),
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": 104, "g": 236, "b": 180, "strength": 160},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "guide_geometry_line"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": shell_material_id,
                "base_color": _color_from_seed({"geometry_id": geometry_id, "kind": "shell"}, floor=62),
                "roughness": 320,
                "metallic": 0,
                "emission": None,
                "transparency": {"mode": "alpha", "value_permille": 680},
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "guide_geometry_shell"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": junction_material_id,
                "base_color": _color_from_seed({"geometry_id": geometry_id, "kind": "junction_ref"}, floor=76),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": 230, "g": 238, "b": 118, "strength": 220},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "guide_geometry_junction"},
            },
        ],
        key=lambda item: str(item.get("material_id", "")),
    )

    renderables = _overlay_renderables(
        target_semantic_id=geometry_id,
        summary_label="guide:{} type={} points={}".format(geometry_id, geometry_type_id, int(len(points))),
        mode="guide_geometry_overlay",
    )
    for index in range(max(0, len(points) - 1)):
        point_a = dict(points[index])
        point_b = dict(points[index + 1])
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.geometry.segment.{}".format(
                    canonical_sha256({"geometry_id": geometry_id, "segment": int(index)})[:16]
                ),
                "semantic_id": "overlay.inspect.geometry.segment.{}.{}".format(geometry_id, str(index).zfill(3)),
                "primitive_id": "prim.line.debug",
                "transform": {
                    "position_mm": dict(point_a),
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": line_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": True},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "guide_geometry_segment",
                    "geometry_id": geometry_id,
                    "geometry_type_id": geometry_type_id,
                    "segment_index": int(index),
                    "point_a_mm": dict(point_a),
                    "point_b_mm": dict(point_b),
                },
            }
        )
    if geometry_type_id in {"geo.corridor2D", "geo.volume3D"}:
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.geometry.shell.{}".format(
                    canonical_sha256({"geometry_id": geometry_id, "shell": True})[:16]
                ),
                "semantic_id": "overlay.inspect.geometry.shell.{}".format(geometry_id),
                "primitive_id": "prim.box.wire",
                "transform": {
                    "position_mm": {
                        "x": int((int(min_mm["x"]) + int(max_mm["x"])) // 2),
                        "y": int((int(min_mm["y"]) + int(max_mm["y"])) // 2),
                        "z": int((int(min_mm["z"]) + int(max_mm["z"])) // 2),
                    },
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": shell_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "guide_geometry_shell",
                    "geometry_id": geometry_id,
                    "bounds": {"min_mm": dict(min_mm), "max_mm": dict(max_mm)},
                },
            }
        )
    for index, junction_id in enumerate(junction_refs):
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.geometry.junction_ref.{}".format(
                    canonical_sha256({"geometry_id": geometry_id, "junction_id": junction_id})[:16]
                ),
                "semantic_id": "overlay.inspect.geometry.junction_ref.{}".format(junction_id),
                "primitive_id": "prim.glyph.node",
                "transform": {
                    "position_mm": {"x": int(index) * 120, "y": 160, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 900,
                },
                "material_id": junction_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "guide_geometry_junction_ref",
                    "geometry_id": geometry_id,
                    "junction_id": junction_id,
                },
            }
        )

    return {
        "mode": "guide_geometry_overlay",
        "summary": "guide:{} type={} points={}".format(geometry_id, geometry_type_id, int(len(points))),
        "target_semantic_id": geometry_id,
        "inspection_snapshot": dict(snapshot),
        "renderables": sorted(renderables, key=lambda item: str(item.get("renderable_id", ""))),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "guide_geometry",
            "available": True,
            "geometry_id": geometry_id,
            "geometry_type_id": geometry_type_id,
            "point_count": int(len(points)),
            "junction_ref_count": int(len(junction_refs)),
        },
    }


def _runtime_rows(runtime: dict, key: str) -> list[dict]:
    rows = list((dict(runtime or {})).get(key) or [])
    return sorted(
        [dict(item) for item in rows if isinstance(item, dict)],
        key=lambda item: str(item.get("project_id", "")) + "|" + str(item.get("step_id", "")) + "|" + str(item.get("instance_id", "")) + "|" + str(item.get("event_id", "")),
    )


def _has_materialized_micro_for_structure(runtime: dict, structure_id: str) -> bool:
    token = str(structure_id).strip()
    if not token:
        return False
    for row in _runtime_rows(runtime, "micro_part_instances"):
        if str(row.get("parent_structure_id", "")).strip() == token:
            return True
    return False


def _materialization_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    target_id = str(target_semantic_id).strip()

    micro_rows = _runtime_rows(runtime, "micro_part_instances")
    state_rows = _runtime_rows(runtime, "materialization_states")
    aggregate_rows = _runtime_rows(runtime, "distribution_aggregates")

    structure_id = ""
    roi_id = ""
    if collection == "micro_part_instances":
        structure_id = str(target_row.get("parent_structure_id", "")).strip()
        roi_id = str((dict(target_row.get("extensions") or {})).get("roi_id", "")).strip()
    elif collection == "materialization_states":
        structure_id = str(target_row.get("structure_id", "")).strip()
        roi_id = str(target_row.get("roi_id", "")).strip()
    elif collection == "distribution_aggregates":
        structure_id = str(target_row.get("structure_id", "")).strip()
    elif collection == "materialization_reenactment_descriptors":
        structure_id = str(target_row.get("structure_id", "")).strip()
    elif collection == "installed_structure_instances":
        structure_id = str(target_row.get("instance_id", "")).strip()
    elif target_id.startswith("materialization.state."):
        suffix = target_id[len("materialization.state."):]
        if "::" in suffix:
            structure_id, roi_id = suffix.split("::", 1)
    elif target_id.startswith("micro.part."):
        for row in micro_rows:
            if str(row.get("micro_part_id", "")).strip() == target_id:
                structure_id = str(row.get("parent_structure_id", "")).strip()
                roi_id = str((dict(row.get("extensions") or {})).get("roi_id", "")).strip()
                break

    filtered_micro_rows = [
        dict(row)
        for row in micro_rows
        if (not structure_id or str(row.get("parent_structure_id", "")).strip() == structure_id)
        and (
            (not roi_id)
            or str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() == roi_id
        )
    ]
    filtered_micro_rows = sorted(
        filtered_micro_rows,
        key=lambda row: (
            str(row.get("ag_node_id", "")),
            str(row.get("batch_id", "")),
            str(row.get("micro_part_id", "")),
        ),
    )
    filtered_aggregate_rows = [
        dict(row)
        for row in aggregate_rows
        if (not structure_id or str(row.get("structure_id", "")).strip() == structure_id)
    ]
    filtered_state_rows = [
        dict(row)
        for row in state_rows
        if (not structure_id or str(row.get("structure_id", "")).strip() == structure_id)
        and ((not roi_id) or str(row.get("roi_id", "")).strip() == roi_id)
    ]
    micro_mass_total = int(sum(max(0, _to_int(row.get("mass", 0), 0)) for row in filtered_micro_rows))
    aggregate_mass_total = int(sum(max(0, _to_int(row.get("total_mass", 0), 0)) for row in filtered_aggregate_rows))
    remaining_macro_mass = int(max(0, aggregate_mass_total - micro_mass_total))

    structure_token = structure_id or (str(target_row.get("instance_id", "")).strip() or "unknown")
    part_material_id = "mat.inspect.materialization.part.{}".format(
        canonical_sha256({"structure_id": structure_token, "kind": "part"})[:12]
    )
    label_material_id = "mat.inspect.materialization.label.{}".format(
        canonical_sha256({"structure_id": structure_token, "kind": "label"})[:12]
    )
    macro_material_id = "mat.inspect.materialization.macro.{}".format(
        canonical_sha256({"structure_id": structure_token, "kind": "macro"})[:12]
    )
    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": part_material_id,
                "base_color": _color_from_seed({"structure_id": structure_token, "kind": "micro_part"}, floor=64),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": 112, "g": 226, "b": 174, "strength": 120},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "materialization_part"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": macro_material_id,
                "base_color": {"r": 102, "g": 126, "b": 146},
                "roughness": 420,
                "metallic": 0,
                "emission": None,
                "transparency": {"mode": "alpha", "value_permille": 620},
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "materialization_macro"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": label_material_id,
                "base_color": {"r": 230, "g": 236, "b": 242},
                "roughness": 260,
                "metallic": 20,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "materialization_label"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )

    renderables: list[dict] = []
    max_renderable_parts = int(max(0, _to_int(runtime.get("materialization_overlay_max_parts", 256), 256)))
    selected_micro_rows = list(filtered_micro_rows[:max_renderable_parts])
    truncated = len(filtered_micro_rows) > len(selected_micro_rows)
    primitive_cycle = ("prim.box.debug", "prim.cylinder.debug", "prim.capsule.debug")
    for index, row in enumerate(selected_micro_rows):
        micro_part_id = str(row.get("micro_part_id", "")).strip()
        if not micro_part_id:
            continue
        transform = dict(row.get("transform") or {})
        if not isinstance(transform, dict) or not transform:
            transform = {
                "position_mm": {"x": int(index * 120), "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            }
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.materialization.part.{}".format(
                    canonical_sha256({"micro_part_id": micro_part_id})[:16]
                ),
                "semantic_id": "overlay.inspect.materialization.part.{}".format(micro_part_id),
                "primitive_id": primitive_cycle[index % len(primitive_cycle)],
                "transform": transform,
                "material_id": part_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": True},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "materialization_part",
                    "micro_part_id": micro_part_id,
                    "ag_node_id": str(row.get("ag_node_id", "")).strip(),
                    "batch_id": str(row.get("batch_id", "")).strip(),
                    "material_id": str(row.get("material_id", "")).strip(),
                },
            }
        )

    summary_label = "materialization:{} micro_parts={} macro_remaining_mass={}".format(
        structure_token or target_id or "unknown",
        int(len(filtered_micro_rows)),
        int(remaining_macro_mass),
    )
    renderables.append(
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.materialization.label.{}".format(
                canonical_sha256({"target": target_id, "structure_id": structure_token})[:16]
            ),
            "semantic_id": "overlay.inspect.materialization.label.{}".format(structure_token),
            "primitive_id": "prim.glyph.label",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": label_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": summary_label,
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": False},
            "extensions": {
                "interaction_overlay": True,
                "overlay_kind": "materialization_label",
            },
        }
    )
    if not filtered_micro_rows:
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.materialization.macro.{}".format(
                    canonical_sha256({"target": target_id, "structure_id": structure_token, "macro": True})[:16]
                ),
                "semantic_id": "overlay.inspect.materialization.macro.{}".format(structure_token),
                "primitive_id": "prim.line.debug",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": macro_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "materialization_macro_placeholder",
                },
            }
        )

    return {
        "mode": "materialization_overlay",
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "materialization",
            "structure_id": structure_token,
            "roi_id": roi_id,
            "materialized_part_count": int(len(filtered_micro_rows)),
            "materialization_state_count": int(len(filtered_state_rows)),
            "micro_mass_total": int(micro_mass_total),
            "aggregate_mass_total": int(aggregate_mass_total),
            "remaining_macro_mass": int(remaining_macro_mass),
            "truncated": bool(truncated),
            "truncated_count": int(max(0, len(filtered_micro_rows) - len(selected_micro_rows))),
            "hide_macro_ghost": bool(len(filtered_micro_rows) > 0),
        },
    }


def _machine_port_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    target_id = str(target_semantic_id).strip()
    machine_id = str(target_row.get("machine_id", "")).strip()
    if not machine_id and target_id.startswith("machine."):
        machine_id = target_id

    machine_rows = _runtime_rows(runtime, "machine_assemblies")
    port_rows = _runtime_rows(runtime, "machine_ports")
    connection_rows = [
        dict(row)
        for row in _runtime_rows(runtime, "machine_port_connections")
        if isinstance(row, dict) and bool(row.get("active", False))
    ]
    if machine_id:
        port_rows = [dict(row) for row in list(port_rows or []) if str(row.get("machine_id", "")).strip() == machine_id]
        connection_rows = [
            dict(row)
            for row in list(connection_rows or [])
            if machine_id in {
                str((dict(row)).get("machine_id", "")).strip(),
                str((dict(row)).get("from_machine_id", "")).strip(),
            }
            or str((dict(row)).get("from_port_id", "")).strip() in {
                str((dict(port)).get("port_id", "")).strip() for port in port_rows
            }
            or str((dict(row)).get("to_port_id", "")).strip() in {
                str((dict(port)).get("port_id", "")).strip() for port in port_rows
            }
        ]

    blocked = False
    full_count = 0
    empty_count = 0
    for row in sorted((item for item in list(port_rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("port_id", ""))):
        current_mass = int(
            sum(max(0, _to_int((dict(entry)).get("mass", 0), 0)) for entry in list((dict(row).get("current_contents") or [])))
        )
        capacity = row.get("capacity_mass")
        if capacity is not None and current_mass >= int(max(0, _to_int(capacity, 0))):
            full_count += 1
        if current_mass == 0:
            empty_count += 1
    machine_row = {}
    for row in sorted((item for item in machine_rows if isinstance(item, dict)), key=lambda item: str(item.get("machine_id", ""))):
        if str(row.get("machine_id", "")).strip() == machine_id:
            machine_row = dict(row)
            break
    machine_state = str(machine_row.get("operational_state", "")).strip()
    if machine_state == "blocked":
        blocked = True
    summary_label = "machine:{} state={} ports={} full={} empty={} links={}".format(
        machine_id or target_id or "unknown",
        machine_state or "idle",
        len(port_rows),
        int(full_count),
        int(empty_count),
        len(connection_rows),
    )
    base_materials = _overlay_materials(target_semantic_id=target_id)
    status_color = {"r": 90, "g": 210, "b": 130}
    if blocked:
        status_color = {"r": 232, "g": 94, "b": 64}
    elif full_count:
        status_color = {"r": 236, "g": 190, "b": 72}
    status_material_id = "mat.inspect.machine.status.{}".format(canonical_sha256({"target": target_id, "state": machine_state})[:12])
    materials = sorted(
        list(base_materials)
        + [
            {
                "schema_version": "1.0.0",
                "material_id": status_material_id,
                "base_color": dict(status_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": status_color["r"], "g": status_color["g"], "b": status_color["b"], "strength": 260},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "machine_port_status"},
            }
        ],
        key=lambda row: str(row.get("material_id", "")),
    )
    return {
        "mode": "machine_port_overlay",
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": _overlay_renderables(
            target_semantic_id=target_id,
            summary_label=summary_label,
            mode="machine_port_overlay",
        ),
        "materials": materials,
        "degraded": False,
        "extensions": {
            "overlay_kind": "machine_port",
            "collection": collection,
            "machine_id": machine_id or None,
            "port_count": len(port_rows),
            "active_connection_count": len(connection_rows),
            "full_port_count": int(full_count),
            "empty_port_count": int(empty_count),
            "blocked": bool(blocked),
        },
    }


def _construction_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    project_id = str(target_row.get("project_id", "")).strip()
    target_id = str(target_semantic_id).strip()
    if target_id.startswith("project.construction."):
        project_id = target_id
    projects = _runtime_rows(runtime, "construction_projects")
    steps = _runtime_rows(runtime, "construction_steps")
    commitments = _runtime_rows(runtime, "construction_commitments")
    structures = _runtime_rows(runtime, "installed_structure_instances")
    events = _runtime_rows(runtime, "construction_provenance_events")
    summary_sections = dict((dict(inspection_snapshot or {})).get("summary_sections") or {})
    spec_section = dict(summary_sections.get("section.spec_compliance_summary") or {})
    spec_data = dict(spec_section.get("data") or {})

    project_row = {}
    if project_id:
        for row in projects:
            if str(row.get("project_id", "")).strip() == project_id:
                project_row = dict(row)
                break
    if (not project_row) and collection == "construction_projects":
        project_row = dict(target_row)
        project_id = str(project_row.get("project_id", "")).strip()
    if not project_id and collection == "installed_structure_instances":
        project_id = str(target_row.get("project_id", "")).strip()

    project_steps = [
        dict(row)
        for row in steps
        if str(row.get("project_id", "")).strip() == project_id
    ]
    installed_row = {}
    for row in structures:
        if str(row.get("project_id", "")).strip() == project_id:
            installed_row = dict(row)
            break
    if (not installed_row) and collection == "installed_structure_instances":
        installed_row = dict(target_row)

    completed_nodes = _sorted_unique_strings(list(installed_row.get("installed_node_states") or []))
    if not completed_nodes:
        completed_nodes = _sorted_unique_strings(
            [
                str(row.get("ag_node_id", "")).strip()
                for row in project_steps
                if str(row.get("status", "")).strip() == "completed"
            ]
        )
    total_nodes = len(project_steps)
    completed_count = len(completed_nodes)
    progress_permille = 0
    if total_nodes > 0:
        progress_permille = int((int(completed_count) * 1000) // int(total_nodes))

    material_events = [
        dict(row)
        for row in events
        if str(row.get("linked_project_id", "")).strip() == project_id
        and str(row.get("event_type_id", "")).strip() == "event.material_consumed"
    ]
    materials_consumed_mass = 0
    for row in material_events:
        ledger_deltas = dict(row.get("ledger_deltas") or {})
        mass_delta = int(_to_int(ledger_deltas.get("quantity.mass", 0), 0))
        materials_consumed_mass += int(abs(mass_delta))

    next_commitments = sorted(
        [
            dict(row)
            for row in commitments
            if str(row.get("project_id", "")).strip() == project_id
            and str(row.get("status", "")).strip() in ("planned", "scheduled")
        ],
        key=lambda row: (_to_int(row.get("scheduled_tick", 0), 0), str(row.get("commitment_id", ""))),
    )
    next_commitment_ids = [str(row.get("commitment_id", "")).strip() for row in next_commitments[:4] if str(row.get("commitment_id", "")).strip()]
    project_extensions = dict(project_row.get("extensions") or {})
    manifests_required = _sorted_unique_strings(list(project_extensions.get("required_manifest_ids") or []))

    planned_material_id = "mat.inspect.construction.planned.{}".format(canonical_sha256({"project_id": project_id, "kind": "planned"})[:12])
    completed_material_id = "mat.inspect.construction.completed.{}".format(canonical_sha256({"project_id": project_id, "kind": "completed"})[:12])
    label_material_id = "mat.inspect.construction.label.{}".format(canonical_sha256({"project_id": project_id, "kind": "label"})[:12])
    spec_pass_material_id = "mat.inspect.construction.spec.pass.{}".format(canonical_sha256({"project_id": project_id, "kind": "spec_pass"})[:12])
    spec_warn_material_id = "mat.inspect.construction.spec.warn.{}".format(canonical_sha256({"project_id": project_id, "kind": "spec_warn"})[:12])
    spec_fail_material_id = "mat.inspect.construction.spec.fail.{}".format(canonical_sha256({"project_id": project_id, "kind": "spec_fail"})[:12])
    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": planned_material_id,
                "base_color": {"r": 120, "g": 170, "b": 220},
                "roughness": 420,
                "metallic": 0,
                "emission": {"r": 120, "g": 170, "b": 220, "strength": 120},
                "transparency": {"mode": "alpha", "value_permille": 560},
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "construction_planned"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": completed_material_id,
                "base_color": {"r": 144, "g": 214, "b": 124},
                "roughness": 280,
                "metallic": 40,
                "emission": {"r": 144, "g": 214, "b": 124, "strength": 80},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "construction_completed"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": label_material_id,
                "base_color": {"r": 232, "g": 238, "b": 242},
                "roughness": 260,
                "metallic": 20,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "construction_label"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": spec_pass_material_id,
                "base_color": {"r": 120, "g": 208, "b": 128},
                "roughness": 300,
                "metallic": 0,
                "emission": {"r": 120, "g": 208, "b": 128, "strength": 110},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "construction_spec_pass"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": spec_warn_material_id,
                "base_color": {"r": 236, "g": 196, "b": 92},
                "roughness": 280,
                "metallic": 0,
                "emission": {"r": 236, "g": 196, "b": 92, "strength": 120},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "construction_spec_warn"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": spec_fail_material_id,
                "base_color": {"r": 224, "g": 112, "b": 104},
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": 224, "g": 112, "b": 104, "strength": 140},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "construction_spec_fail"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )

    renderables: list[dict] = []
    for idx, step in enumerate(sorted(project_steps, key=lambda row: (str(row.get("ag_node_id", "")), str(row.get("step_id", ""))))):
        ag_node_id = str(step.get("ag_node_id", "")).strip()
        if not ag_node_id:
            continue
        is_completed = ag_node_id in set(completed_nodes)
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.construction.node.{}".format(canonical_sha256({"project_id": project_id, "ag_node_id": ag_node_id})[:16]),
                "semantic_id": "overlay.inspect.construction.node.{}".format(ag_node_id),
                "primitive_id": "prim.box.debug" if is_completed else "prim.line.debug",
                "transform": {
                    "position_mm": {"x": int(idx * 250), "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": completed_material_id if is_completed else planned_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(is_completed)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "construction_node",
                    "project_id": project_id,
                    "ag_node_id": ag_node_id,
                    "step_status": str(step.get("status", "")).strip(),
                },
            }
        )

    summary_label = "construction:{} progress={}permille steps={}/{} consumed_mass={}".format(
        project_id or target_id or "unknown",
        int(progress_permille),
        int(completed_count),
        int(total_nodes),
        int(materials_consumed_mass),
    )
    spec_grade = str(spec_data.get("overall_grade", "")).strip()
    if spec_grade in {"pass", "warn", "fail"}:
        summary_label = "{} spec={}".format(summary_label, spec_grade)
    renderables.append(
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.construction.label.{}".format(canonical_sha256({"project_id": project_id, "summary": True})[:16]),
            "semantic_id": "overlay.inspect.construction.label.{}".format(project_id or target_id),
            "primitive_id": "prim.glyph.label",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": label_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": summary_label,
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": False},
            "extensions": {
                "interaction_overlay": True,
                "overlay_kind": "construction_label",
                "project_id": project_id,
            },
        }
    )
    if bool(spec_data.get("available", False)):
        spec_status = spec_grade if spec_grade in {"pass", "warn", "fail"} else "unknown"
        spec_material_id = {
            "pass": spec_pass_material_id,
            "warn": spec_warn_material_id,
            "fail": spec_fail_material_id,
        }.get(spec_status, label_material_id)
        spec_label = "spec:{} {}".format(
            str(spec_data.get("bound_spec_id", "unbound")).strip() or "unbound",
            spec_status,
        )
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.construction.spec.{}".format(
                    canonical_sha256({"project_id": project_id, "target_id": target_id, "spec": spec_status})[:16]
                ),
                "semantic_id": "overlay.inspect.construction.spec.{}".format(project_id or target_id or "unknown"),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 180, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 850,
                },
                "material_id": spec_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": spec_label,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": spec_status in {"warn", "fail"}},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "construction_spec_compliance",
                    "overall_grade": spec_status,
                    "spec_id": str(spec_data.get("bound_spec_id", "")).strip() or None,
                    "result_id": str(spec_data.get("result_id", "")).strip() or None,
                },
            }
        )
    return {
        "mode": "construction_overlay",
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "construction",
            "project_id": project_id,
            "progress_permille": int(progress_permille),
            "materials_consumed_mass": int(materials_consumed_mass),
            "next_commitment_ids": list(next_commitment_ids),
            "manifests_required": list(manifests_required),
        },
    }


def _provenance_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    event_id = str(target_row.get("event_id", "")).strip() or str(target_semantic_id).strip()
    event_type_id = str(target_row.get("event_type_id", "")).strip() or "event.unknown"
    summary_label = "provenance:{} {}".format(event_id, event_type_id)
    return {
        "mode": "provenance_overlay",
        "summary": summary_label,
        "target_semantic_id": str(target_semantic_id),
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": _overlay_renderables(
            target_semantic_id=str(target_semantic_id),
            summary_label=summary_label,
            mode="provenance_overlay",
        ),
        "materials": _overlay_materials(target_semantic_id=str(target_semantic_id)),
        "degraded": False,
        "extensions": {
            "overlay_kind": "provenance",
            "event_id": event_id,
            "event_type_id": event_type_id,
            "linked_project_id": str(target_row.get("linked_project_id", "")).strip(),
            "linked_step_id": str(target_row.get("linked_step_id", "")).strip(),
        },
    }


def _maintenance_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    extensions = dict(payload.get("extensions") or {})
    target_id = str(target_semantic_id).strip()
    if collection == "failure_events":
        failure_mode_id = str(target_row.get("failure_mode_id", "")).strip() or "failure.unknown"
        severity = int(max(0, _to_int(target_row.get("severity", 0), 0)))
        summary_label = "failure:{} severity={}".format(failure_mode_id, severity)
        return {
            "mode": "maintenance_overlay",
            "summary": summary_label,
            "target_semantic_id": target_id,
            "inspection_snapshot": dict(inspection_snapshot or {}),
            "renderables": _overlay_renderables(
                target_semantic_id=target_id,
                summary_label=summary_label,
                mode="maintenance_failure",
            ),
            "materials": _overlay_materials(target_semantic_id=target_id),
            "degraded": False,
            "extensions": {
                "overlay_kind": "maintenance_failure",
                "failure_mode_id": failure_mode_id,
                "severity": severity,
                "asset_id": str(target_row.get("asset_id", "")).strip(),
            },
        }
    if collection == "maintenance_commitments":
        summary_label = "maintenance:{} {}@{}".format(
            str(target_row.get("commitment_kind", "")).strip() or "commitment",
            str(target_row.get("status", "")).strip() or "planned",
            int(max(0, _to_int(target_row.get("scheduled_tick", 0), 0))),
        )
        return {
            "mode": "maintenance_overlay",
            "summary": summary_label,
            "target_semantic_id": target_id,
            "inspection_snapshot": dict(inspection_snapshot or {}),
            "renderables": _overlay_renderables(
                target_semantic_id=target_id,
                summary_label=summary_label,
                mode="maintenance_commitment",
            ),
            "materials": _overlay_materials(target_semantic_id=target_id),
            "degraded": False,
            "extensions": {
                "overlay_kind": "maintenance_commitment",
                "asset_id": str(target_row.get("asset_id", "")).strip(),
                "maintenance_policy_id": str(target_row.get("maintenance_policy_id", "")).strip(),
            },
        }

    # asset_health_states (default maintenance inspection target)
    asset_id = str(target_row.get("asset_id", "")).strip() or target_id
    backlog_raw = int(max(0, _to_int(target_row.get("maintenance_backlog", 0), 0)))
    failed_mode_ids = _sorted_unique_strings(list((dict(target_row.get("hazard_state") or {})).get("failed_mode_ids") or []))
    risk_rows = list((dict(extensions.get("failure_risk_summary") or {})).get("risk_rows") or [])
    next_commitment_ids = _sorted_unique_strings(list(extensions.get("next_maintenance_commitment_ids") or []))
    summary_label = "maintenance:{} backlog={} failed_modes={} commitments={}".format(
        asset_id or "unknown",
        backlog_raw,
        len(failed_mode_ids),
        len(next_commitment_ids),
    )
    warn = bool(failed_mode_ids) or backlog_raw > 0
    materials = _overlay_materials(target_semantic_id=target_id)
    if warn:
        materials = sorted(
            list(materials)
            + [
                {
                    "schema_version": "1.0.0",
                    "material_id": "mat.inspect.maintenance.warn.{}".format(canonical_sha256({"target": target_id})[:12]),
                    "base_color": {"r": 232, "g": 94, "b": 64},
                    "roughness": 240,
                    "metallic": 0,
                    "emission": {"r": 232, "g": 94, "b": 64, "strength": 300},
                    "transparency": None,
                    "pattern_id": None,
                    "extensions": {"interaction_overlay": True, "overlay_kind": "maintenance_warning"},
                }
            ],
            key=lambda row: str(row.get("material_id", "")),
        )
    return {
        "mode": "maintenance_overlay",
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": _overlay_renderables(
            target_semantic_id=target_id,
            summary_label=summary_label,
            mode="maintenance_asset",
        ),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "maintenance_asset",
            "asset_id": asset_id,
            "maintenance_backlog_raw": backlog_raw,
            "failed_mode_ids": list(failed_mode_ids),
            "risk_rows": [dict(row) for row in risk_rows if isinstance(row, dict)],
            "next_maintenance_commitment_ids": list(next_commitment_ids),
        },
    }


def _commitment_reenactment_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    payload = dict((dict(inspection_snapshot or {})).get("target_payload") or {})
    target_row = dict(payload.get("row") or {})
    collection = str(payload.get("collection", "")).strip()
    target_id = str(target_semantic_id).strip()
    extensions = dict(payload.get("extensions") or {})

    summary_label = "history:{} unavailable".format(target_id or "unknown")
    mode = "history_overlay"
    overlay_kind = "history"
    if collection == "material_commitments":
        summary_label = "commitment:{} {} {}".format(
            str(target_row.get("commitment_type_id", "")).strip() or "type.unknown",
            str(target_row.get("status", "")).strip() or "planned",
            str(target_row.get("target_id", "")).strip() or "target.unknown",
        )
        overlay_kind = "commitment"
    elif collection == "event_stream_indices":
        summary_label = "history_stream:{} events={}".format(
            str(target_row.get("target_id", "")).strip() or target_id or "unknown",
            int(len(list(target_row.get("event_ids") or []))),
        )
        overlay_kind = "event_stream"
    elif collection == "reenactment_requests":
        summary_label = "reenactment_request:{} fidelity={} budget={}".format(
            str(target_row.get("target_id", "")).strip() or "unknown",
            str(target_row.get("desired_fidelity", "")).strip() or "macro",
            int(max(0, _to_int(target_row.get("max_cost_units", 0), 0))),
        )
        overlay_kind = "reenactment_request"
    elif collection == "reenactment_artifacts":
        artifact_ext = dict(target_row.get("extensions") or {})
        summary_label = "reenactment:{} fidelity={} degraded={}".format(
            str(target_row.get("reenactment_id", "")).strip() or target_id or "unknown",
            str(target_row.get("fidelity_achieved", "")).strip() or "macro",
            bool(artifact_ext.get("degraded", False)),
        )
        overlay_kind = "reenactment_artifact"

    return {
        "mode": mode,
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(inspection_snapshot or {}),
        "renderables": _overlay_renderables(
            target_semantic_id=target_id,
            summary_label=summary_label,
            mode=mode,
        ),
        "materials": _overlay_materials(target_semantic_id=target_id),
        "degraded": False,
        "extensions": {
            "overlay_kind": overlay_kind,
            "collection": collection,
            "target_row": target_row,
            "snapshot_extensions": extensions,
        },
    }


def _pose_mount_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    target_id = str(target_semantic_id).strip()
    snapshot = dict(inspection_snapshot or {})
    sections = dict(snapshot.get("summary_sections") or {})
    pose_data = dict((dict(sections.get("section.pose_slots_summary") or {})).get("data") or {})
    mount_data = dict((dict(sections.get("section.mount_points_summary") or {})).get("data") or {})
    pose_rows = [dict(item) for item in list(pose_data.get("rows") or []) if isinstance(item, dict)]
    mount_rows = [dict(item) for item in list(mount_data.get("rows") or []) if isinstance(item, dict)]
    pose_count = int(max(0, _to_int(pose_data.get("slot_count", len(pose_rows)), len(pose_rows))))
    mount_count = int(max(0, _to_int(mount_data.get("mount_point_count", len(mount_rows)), len(mount_rows))))

    pose_material_id = "mat.inspect.pose.slot.{}".format(canonical_sha256({"target": target_id, "kind": "pose"})[:12])
    pose_occupied_material_id = "mat.inspect.pose.slot.occupied.{}".format(
        canonical_sha256({"target": target_id, "kind": "pose_occupied"})[:12]
    )
    mount_material_id = "mat.inspect.mount.point.{}".format(canonical_sha256({"target": target_id, "kind": "mount"})[:12])
    occupant_material_id = "mat.inspect.pose.occupant.{}".format(canonical_sha256({"target": target_id, "kind": "occupant"})[:12])

    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": pose_material_id,
                "base_color": _color_from_seed({"target": target_id, "kind": "pose"}, floor=80),
                "roughness": 260,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "pose_slot"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": pose_occupied_material_id,
                "base_color": _color_from_seed({"target": target_id, "kind": "pose_occupied"}, floor=84),
                "roughness": 220,
                "metallic": 0,
                "emission": {"r": 232, "g": 198, "b": 86, "strength": 260},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "pose_slot_occupied"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": mount_material_id,
                "base_color": _color_from_seed({"target": target_id, "kind": "mount"}, floor=72),
                "roughness": 260,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "mount_point"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": occupant_material_id,
                "base_color": {"r": 245, "g": 235, "b": 220},
                "roughness": 180,
                "metallic": 0,
                "emission": {"r": 245, "g": 235, "b": 220, "strength": 220},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "pose_occupant"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )

    renderables: list[dict] = []
    for index, row in enumerate(sorted(pose_rows, key=lambda item: str(item.get("pose_slot_id", "")))):
        pose_slot_id = str(row.get("pose_slot_id", "")).strip() or "pose.slot.{}".format(str(index).zfill(4))
        occupied = bool(row.get("occupied", False))
        material_id = pose_occupied_material_id if occupied else pose_material_id
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.pose.slot.{}".format(canonical_sha256({"target": target_id, "pose_slot_id": pose_slot_id})[:16]),
                "semantic_id": "overlay.inspect.pose.slot.{}".format(pose_slot_id),
                "primitive_id": "prim.glyph.dot",
                "transform": {
                    "position_mm": {"x": int(index) * 140, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 900,
                },
                "material_id": material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": occupied},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "pose_slot",
                    "pose_slot_id": pose_slot_id,
                    "occupied": occupied,
                },
            }
        )
        if occupied:
            renderables.append(
                {
                    "schema_version": "1.0.0",
                    "renderable_id": "overlay.inspect.pose.occupant.{}".format(
                        canonical_sha256({"target": target_id, "pose_slot_id": pose_slot_id, "occupant": True})[:16]
                    ),
                    "semantic_id": "overlay.inspect.pose.occupant.{}".format(pose_slot_id),
                    "primitive_id": "prim.glyph.person",
                    "transform": {
                        "position_mm": {"x": int(index) * 140, "y": 0, "z": 120},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 800,
                    },
                    "material_id": occupant_material_id,
                    "layer_tags": ["overlay", "ui"],
                    "label": None,
                    "lod_hint": "lod.band.near",
                    "flags": {"selectable": False, "highlighted": True},
                    "extensions": {
                        "interaction_overlay": True,
                        "overlay_kind": "pose_occupant",
                        "pose_slot_id": pose_slot_id,
                    },
                }
            )

    for index, row in enumerate(sorted(mount_rows, key=lambda item: str(item.get("mount_point_id", "")))):
        mount_point_id = str(row.get("mount_point_id", "")).strip() or "mount.point.{}".format(str(index).zfill(4))
        attached = bool(row.get("attached", False))
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.inspect.mount.point.{}".format(
                    canonical_sha256({"target": target_id, "mount_point_id": mount_point_id})[:16]
                ),
                "semantic_id": "overlay.inspect.mount.point.{}".format(mount_point_id),
                "primitive_id": "prim.glyph.anchor",
                "transform": {
                    "position_mm": {"x": int(index) * 140, "y": 220, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 900,
                },
                "material_id": mount_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": attached},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "mount_point",
                    "mount_point_id": mount_point_id,
                    "attached": attached,
                    "connected_to_mount_point_id": str(row.get("connected_to_mount_point_id", "")).strip() or None,
                },
            }
        )

    summary_label = "pose_mount:{} slots={} mounts={}".format(target_id or "unknown", pose_count, mount_count)
    return {
        "mode": "pose_mount_overlay",
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(snapshot),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": list(materials),
        "degraded": False,
        "extensions": {
            "overlay_kind": "pose_mount",
            "pose_slot_count": pose_count,
            "mount_point_count": mount_count,
        },
    }


def _pollution_overlay_payload(
    *,
    target_semantic_id: str,
    inspection_snapshot: dict,
) -> Dict[str, object]:
    snapshot = dict(inspection_snapshot or {})
    sections = dict(snapshot.get("summary_sections") or {})
    concentration_section = dict(sections.get("section.pollution.concentration_map") or {})
    deposition_section = dict(sections.get("section.pollution.deposition_summary") or {})
    exposure_section = dict(sections.get("section.pollution.exposure_summary") or {})
    concentration_data = dict(concentration_section.get("data") or {})
    deposition_data = dict(deposition_section.get("data") or {})
    exposure_data = dict(exposure_section.get("data") or {})

    target_id = str(target_semantic_id).strip()
    scope_hint = str(
        concentration_data.get(
            "scope_id",
            deposition_data.get("scope_id", exposure_data.get("scope_id", "")),
        )
    ).strip()
    if not target_id:
        target_id = scope_hint or "region.pollution.global"

    max_concentration = int(max(0, _to_int(concentration_data.get("max_concentration", 0), 0)))
    hotspot_count = int(max(0, _to_int(concentration_data.get("hotspot_count", 0), 0)))
    deposited_mass_total = int(max(0, _to_int(deposition_data.get("deposited_mass_total", 0), 0)))
    accumulated_exposure_total = int(max(0, _to_int(exposure_data.get("accumulated_exposure_total", 0), 0)))
    subject_count = int(max(0, _to_int(exposure_data.get("subject_count", 0), 0)))
    risk_band = "low"
    status_color = {"r": 72, "g": 186, "b": 108}
    if max_concentration >= 600 or hotspot_count >= 8 or accumulated_exposure_total >= 3000:
        risk_band = "high"
        status_color = {"r": 224, "g": 86, "b": 62}
    elif max_concentration >= 250 or hotspot_count >= 2 or accumulated_exposure_total >= 1000:
        risk_band = "elevated"
        status_color = {"r": 236, "g": 186, "b": 72}

    summary_label = "pollution:{} band={} peak={} hotspots={} dep={} exp={}".format(
        scope_hint or (target_id or "global"),
        risk_band,
        int(max_concentration),
        int(hotspot_count),
        int(deposited_mass_total),
        int(accumulated_exposure_total),
    )
    base_materials = _overlay_materials(target_semantic_id=target_id)
    status_material_id = "mat.inspect.pollution.status.{}".format(
        canonical_sha256({"target": target_id, "risk_band": risk_band})[:12]
    )
    materials = sorted(
        list(base_materials)
        + [
            {
                "schema_version": "1.0.0",
                "material_id": status_material_id,
                "base_color": dict(status_color),
                "roughness": 220,
                "metallic": 0,
                "emission": {
                    "r": status_color["r"],
                    "g": status_color["g"],
                    "b": status_color["b"],
                    "strength": 260,
                },
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "pollution_status"},
            }
        ],
        key=lambda row: str(row.get("material_id", "")),
    )
    renderables = _overlay_renderables(
        target_semantic_id=target_id,
        summary_label=summary_label,
        mode="pollution_overlay",
    )
    renderables.append(
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.pollution.status.{}".format(
                canonical_sha256({"target": target_id, "mode": "pollution_overlay"})[:12]
            ),
            "semantic_id": "overlay.inspect.pollution.status.{}".format(target_id),
            "primitive_id": "prim.sprite.square",
            "transform": {
                "position_mm": {"x": 0, "y": 140, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1120,
            },
            "material_id": status_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": None,
            "lod_hint": "lod.band.mid",
            "flags": {"selectable": False, "highlighted": False},
            "extensions": {
                "interaction_overlay": True,
                "overlay_kind": "pollution_status",
                "risk_band": risk_band,
            },
        }
    )

    return {
        "mode": "pollution_overlay",
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(snapshot),
        "renderables": sorted(renderables, key=lambda row: str(row.get("renderable_id", ""))),
        "materials": materials,
        "degraded": False,
        "extensions": {
            "overlay_kind": "pollution",
            "scope_id": scope_hint or None,
            "risk_band": risk_band,
            "max_concentration": int(max_concentration),
            "hotspot_count": int(hotspot_count),
            "deposited_mass_total": int(deposited_mass_total),
            "accumulated_exposure_total": int(accumulated_exposure_total),
            "subject_count": int(subject_count),
            "hazard_hook_id": str(exposure_data.get("hazard_hook_id", "hazard.health_risk_stub")).strip()
            or "hazard.health_risk_stub",
        },
    }


def build_inspection_overlays(
    *,
    perceived_model: dict,
    target_semantic_id: str,
    authority_context: dict | None = None,
    inspection_snapshot: dict | None = None,
    overlay_runtime: dict | None = None,
    requested_cost_units: int = 1,
) -> Dict[str, object]:
    """Build deterministic inspection overlays with budgeted degrade path."""
    runtime = dict(overlay_runtime or {})
    perceived = dict(perceived_model or {})
    target_id = str(target_semantic_id).strip()
    tick = int(max(0, _to_int((dict(perceived.get("time_state") or {})).get("tick", 0), 0)))
    runtime["time_state"] = dict(perceived.get("time_state") or {})
    snapshot_payload = dict(inspection_snapshot or {})
    snapshot_target = dict(snapshot_payload.get("target_payload") or {})
    snapshot_collection = str(snapshot_target.get("collection", "")).strip()
    summary_sections = dict(snapshot_payload.get("summary_sections") or {})
    if (
        "section.pollution.concentration_map" in summary_sections
        or "section.pollution.deposition_summary" in summary_sections
        or "section.pollution.exposure_summary" in summary_sections
    ):
        pollution_overlay = _pollution_overlay_payload(
            target_semantic_id=target_id or str(target_semantic_id),
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": pollution_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("formalization.")
        or target_id.startswith("candidate.")
        or target_id.startswith("formalization.event.")
        or snapshot_collection in (
            "formalization_states",
            "formalization_inference_candidates",
            "formalization_events",
        )
    ):
        formalization_overlay = _formalization_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": formalization_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("geometry.")
        or target_id.startswith("junction.")
        or snapshot_collection in (
            "guide_geometries",
            "mobility_junctions",
            "geometry_candidates",
            "geometry_derived_metrics",
        )
    ):
        guide_overlay = _guide_geometry_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": guide_overlay,
            "overlay_runtime": runtime,
        }
    if target_id.startswith("graph.") or snapshot_collection == "network_graphs":
        graph_overlay = _network_graph_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": graph_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("pose.slot.")
        or target_id.startswith("mount.point.")
        or snapshot_collection in ("pose_slots", "mount_points", "pose_mount_provenance_events")
    ):
        pose_mount_overlay = _pose_mount_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": pose_mount_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("structural.graph.")
        or target_id.startswith("structural.node.")
        or target_id.startswith("structural.edge.")
        or snapshot_collection in ("structural_graphs", "structural_nodes", "structural_edges")
    ):
        mechanics_overlay = _mechanics_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": mechanics_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("interior.graph.")
        or target_id.startswith("interior.volume.")
        or target_id.startswith("interior.portal.")
        or snapshot_collection in ("interior_graphs", "interior_volumes", "interior_portals")
    ):
        interior_overlay = _interior_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": interior_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("manifest.")
        or target_id.startswith("commitment.shipment.")
        or target_id.startswith("node.")
        or target_id.startswith("logistics.node.")
        or snapshot_collection in ("logistics_manifests", "shipment_commitments", "logistics_node_inventories")
    ):
        logistics_overlay = _logistics_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": logistics_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("machine.")
        or target_id.startswith("port.")
        or snapshot_collection in (
            "machine_assemblies",
            "machine_ports",
            "machine_port_connections",
            "machine_provenance_events",
        )
    ):
        machine_overlay = _machine_port_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": machine_overlay,
            "overlay_runtime": runtime,
        }
    installed_structure_target = ""
    if snapshot_collection == "installed_structure_instances":
        installed_structure_target = str((dict(snapshot_target.get("row") or {})).get("instance_id", "")).strip()
    elif target_id.startswith("assembly.structure_instance."):
        installed_structure_target = target_id
    if (
        target_id.startswith("micro.part.")
        or target_id.startswith("materialization.state.")
        or target_id.startswith("distribution.aggregate.")
        or snapshot_collection in (
            "micro_part_instances",
            "materialization_states",
            "distribution_aggregates",
            "materialization_reenactment_descriptors",
        )
        or (
            installed_structure_target
            and _has_materialized_micro_for_structure(runtime, installed_structure_target)
        )
    ):
        materialization_overlay = _materialization_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": materialization_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("project.construction.")
        or target_id.startswith("assembly.structure_instance.")
        or snapshot_collection in (
            "construction_projects",
            "construction_steps",
            "construction_commitments",
            "installed_structure_instances",
        )
    ):
        construction_overlay = _construction_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": construction_overlay,
            "overlay_runtime": runtime,
        }
    if target_id.startswith("provenance.event.") or snapshot_collection == "construction_provenance_events":
        provenance_overlay = _provenance_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": provenance_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("commitment.")
        or target_id.startswith("stream.event.")
        or target_id.startswith("reenactment.")
        or snapshot_collection in (
            "material_commitments",
            "event_stream_indices",
            "reenactment_requests",
            "reenactment_artifacts",
        )
    ):
        history_overlay = _commitment_reenactment_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": history_overlay,
            "overlay_runtime": runtime,
        }
    if (
        target_id.startswith("asset.health.")
        or target_id.startswith("asset_health.")
        or target_id.startswith("failure.event.")
        or target_id.startswith("commitment.maintenance.")
        or snapshot_collection in (
            "asset_health_states",
            "failure_events",
            "maintenance_commitments",
            "maintenance_provenance_events",
        )
    ):
        maintenance_overlay = _maintenance_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": maintenance_overlay,
            "overlay_runtime": runtime,
        }
    if target_id.startswith("plan.") or snapshot_collection == "plan_artifacts":
        plan_overlay = _plan_overlay_payload(
            target_semantic_id=target_id,
            inspection_snapshot=snapshot_payload,
        )
        return {
            "result": "complete",
            "inspection_overlays": plan_overlay,
            "overlay_runtime": runtime,
        }
    if target_id.startswith("blueprint."):
        blueprint_overlay = _blueprint_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
        )
        return {
            "result": "complete",
            "inspection_overlays": blueprint_overlay,
            "overlay_runtime": runtime,
        }

    entitlements = set(_sorted_unique_strings(list((dict(authority_context or {})).get("entitlements") or [])))
    budget_envelope_registry = dict(runtime.get("budget_envelope_registry") or {})
    budget_policy_row = dict(runtime.get("budget_policy") or {})
    budget_envelope_id = str(runtime.get("budget_envelope_id", "")).strip()
    selected_budget_envelope = {}
    for row in sorted((item for item in list(budget_envelope_registry.get("envelopes") or []) if isinstance(item, dict)), key=lambda item: str(item.get("envelope_id", ""))):
        if str(row.get("envelope_id", "")).strip() == budget_envelope_id:
            selected_budget_envelope = dict(row)
            break
    normalized_budget_envelope = normalize_budget_envelope(
        envelope=selected_budget_envelope,
        budget_policy=budget_policy_row,
    )
    max_inspection_budget = max(0, _to_int(normalized_budget_envelope.get("max_inspection_cost_units_per_tick", 0), 0))
    reservation = reserve_inspection_budget(
        runtime_budget_state=dict(runtime.get("inspection_runtime_budget_state") or {}),
        tick=int(tick),
        requested_cost_units=max(1, int(max(0, _to_int(requested_cost_units, 1)))),
        max_cost_units_per_tick=int(max_inspection_budget),
    )
    degraded = str(reservation.get("result", "")) != "complete"
    if not degraded:
        runtime["inspection_runtime_budget_state"] = dict(reservation.get("runtime_budget_state") or {})

    summary_label = "inspect:{} macro-summary".format(target_id or "unknown")
    mode = "macro_summary" if degraded else "full"
    snapshot = dict(inspection_snapshot or {})
    if (not degraded) and (not snapshot):
        truth_overlay = dict(perceived.get("truth_overlay") or {})
        truth_hash_anchor = str(truth_overlay.get("state_hash_anchor", "")).strip()
        if truth_hash_anchor:
            cache_policy_registry = dict(runtime.get("inspection_cache_policy_registry") or {})
            cache_policy_id = str(runtime.get("inspection_cache_policy_id", "")).strip()
            selected_cache_policy = {}
            for row in sorted((item for item in list(cache_policy_registry.get("policies") or []) if isinstance(item, dict)), key=lambda item: str(item.get("cache_policy_id", ""))):
                if str(row.get("cache_policy_id", "")).strip() == cache_policy_id:
                    selected_cache_policy = dict(row)
                    break
            if not selected_cache_policy:
                selected_cache_policy = {
                    "cache_policy_id": "cache.off",
                    "enable_caching": False,
                    "invalidation_rules": [],
                    "max_cache_entries": 0,
                    "eviction_rule_id": "evict.none",
                    "extensions": {},
                }
            generated_snapshot = build_inspection_snapshot(
                target_id=target_id,
                tick=int(tick),
                physics_profile_id=str(runtime.get("physics_profile_id", "")),
                pack_lock_hash=str(runtime.get("pack_lock_hash", "")),
                truth_hash_anchor=str(truth_hash_anchor),
                policy_id=str(selected_cache_policy.get("cache_policy_id", "")),
                target_payload=_target_payload_from_perceived(perceived_model=perceived, target_semantic_id=target_id),
            )
            cache_key = inspection_build_cache_key(
                target_id=target_id,
                truth_hash_anchor=str(truth_hash_anchor),
                policy_id=str(selected_cache_policy.get("cache_policy_id", "")),
                physics_profile_id=str(runtime.get("physics_profile_id", "")),
                pack_lock_hash=str(runtime.get("pack_lock_hash", "")),
            )
            cache_result = inspection_cache_lookup_or_store(
                cache_state=dict(runtime.get("inspection_cache_state") or {}),
                cache_policy=selected_cache_policy,
                cache_key=str(cache_key),
                snapshot=generated_snapshot,
                tick=int(tick),
            )
            runtime["inspection_cache_state"] = dict(cache_result.get("cache_state") or {})
            snapshot = dict(cache_result.get("snapshot") or {})

    if snapshot:
        payload = dict(snapshot.get("target_payload") or {})
        exists = bool(payload.get("exists", False))
        if exists and ("entitlement.inspect" in entitlements):
            summary_label = "inspect:{} detail".format(target_id or "unknown")
        elif exists:
            summary_label = "inspect:{} observed".format(target_id or "unknown")
        else:
            summary_label = "inspect:{} missing".format(target_id or "unknown")

    overlay_payload = {
        "mode": mode,
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(snapshot or {}),
        "renderables": _overlay_renderables(
            target_semantic_id=target_id,
            summary_label=summary_label,
            mode=mode,
        ),
        "materials": _overlay_materials(target_semantic_id=target_id),
        "degraded": bool(degraded),
    }
    return {
        "result": "complete",
        "inspection_overlays": overlay_payload,
        "overlay_runtime": runtime,
    }
