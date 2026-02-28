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
    route_section = dict(sections.get("section.networkgraph.route") or {})
    route_data = dict(route_section.get("data") or {})
    route_edge_ids = set(_sorted_unique_strings(route_data.get("path_edge_ids")))
    edge_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_edge"}, floor=60)
    node_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_node"}, floor=72)
    route_color = _color_from_seed({"graph_id": graph_id, "kind": "graph_route"}, floor=68)
    edge_material_id = "mat.inspect.networkgraph.edge.{}".format(canonical_sha256({"graph_id": graph_id})[:12])
    node_material_id = "mat.inspect.networkgraph.node.{}".format(canonical_sha256({"graph_id": graph_id, "node": True})[:12])
    route_material_id = "mat.inspect.networkgraph.route.{}".format(canonical_sha256({"graph_id": graph_id, "route": True})[:12])
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
        ],
        key=lambda row: str(row.get("material_id", "")),
    )
    renderables: list[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        is_route = edge_id in route_edge_ids
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
                "material_id": route_material_id if is_route else edge_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(is_route)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_edge",
                    "edge_id": edge_id,
                    "from_node_id": str(edge.get("from_node_id", "")).strip(),
                    "to_node_id": str(edge.get("to_node_id", "")).strip(),
                    "directional": True,
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
                "material_id": route_material_id if is_route else edge_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": ">",
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": bool(is_route)},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_direction",
                    "edge_id": edge_id,
                },
            }
        )
    for node in node_rows:
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            continue
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
                "material_id": node_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": node_id,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "networkgraph_node",
                    "node_id": node_id,
                },
            }
        )
    summary = "graph:{} nodes={} edges={} route_edges={}".format(
        graph_id,
        len(node_rows),
        len(edge_rows),
        len(route_edge_ids),
    )
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
    route_edge_ids = _sorted_unique_strings(
        list((dict(target_row.get("extensions") or {})).get("route_edge_ids") or [])
    )
    material_id = str(target_row.get("material_id", "")).strip() or "material.unknown"
    edge_color = _color_from_seed({"graph_id": graph_id, "kind": "edge"}, floor=58)
    flow_color = _color_from_seed({"material_id": material_id, "kind": "flow"}, floor=72)
    edge_material_id = "mat.inspect.logistics.edge.{}".format(canonical_sha256({"graph_id": graph_id})[:12])
    flow_material_id = "mat.inspect.logistics.flow.{}".format(canonical_sha256({"material_id": material_id})[:12])
    node_material_id = "mat.inspect.logistics.node.{}".format(canonical_sha256({"target": target_semantic_id})[:12])
    materials = sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": edge_material_id,
                "base_color": dict(edge_color),
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
        ],
        key=lambda row: str(row.get("material_id", "")),
    )

    renderables: list[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
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
