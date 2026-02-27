"""Deterministic MAT-3 blueprint compilation and ghost-overlay helpers."""

from __future__ import annotations

import copy
import json
import os
from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_BLUEPRINT_MISSING_PART_CLASS = "refusal.blueprint.missing_part_class"
REFUSAL_BLUEPRINT_INVALID_GRAPH = "refusal.blueprint.invalid_graph"
REFUSAL_BLUEPRINT_PARAMETER_INVALID = "refusal.blueprint.parameter_invalid"

_TOOL_ID = "tool.materials.tool_blueprint_compile"
_TOOL_VERSION = "1.0.0"
_BII_ID = "BII.MAT3.BLUEPRINT_COMPILE.1"
_NODE_KINDS = {"part", "subassembly", "connector", "site_anchor"}


class BlueprintCompileError(ValueError):
    """Deterministic blueprint compilation refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _rows_by_id(rows: object, key_field: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(key_field, ""))):
        token = str(row.get(key_field, "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _registry_rows(payload: Mapping[str, object] | None, key: str) -> list[dict]:
    root = dict(payload or {})
    direct = root.get(key)
    if isinstance(direct, list):
        return [dict(item) for item in direct if isinstance(item, dict)]
    record = dict(root.get("record") or {})
    rows = record.get(key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, dict)]
    return []


def _registry_hash(payload: Mapping[str, object] | None) -> str:
    row = dict(payload or {})
    token = str(row.get("registry_hash", "")).strip()
    if token:
        return token
    return canonical_sha256(row)


def _read_json_payload(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint payload is missing or invalid JSON",
            {"path": _norm(path)},
        )
    if not isinstance(payload, dict):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint payload root must be object",
            {"path": _norm(path)},
        )
    return payload


def _to_int(value: object, *, reason_code: str, field: str) -> int:
    try:
        if isinstance(value, bool):
            raise ValueError
        return int(value)
    except (TypeError, ValueError):
        raise BlueprintCompileError(
            reason_code,
            "integer field is invalid",
            {"field": str(field), "value": str(value)},
        )


def _normalize_transform(transform: Mapping[str, object] | None) -> dict:
    row = dict(transform or {})
    position = dict(row.get("position_mm") or {})
    orientation = dict(row.get("orientation_mdeg") or {})
    scale_permille = _to_int(row.get("scale_permille", 1000), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="scale_permille")
    if scale_permille < 1:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "local_transform.scale_permille must be >= 1",
            {"scale_permille": int(scale_permille)},
        )
    return {
        "position_mm": {
            "x": _to_int(position.get("x", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="position_mm.x"),
            "y": _to_int(position.get("y", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="position_mm.y"),
            "z": _to_int(position.get("z", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="position_mm.z"),
        },
        "orientation_mdeg": {
            "yaw": _to_int(orientation.get("yaw", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="orientation_mdeg.yaw"),
            "pitch": _to_int(orientation.get("pitch", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="orientation_mdeg.pitch"),
            "roll": _to_int(orientation.get("roll", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="orientation_mdeg.roll"),
        },
        "scale_permille": int(scale_permille),
    }


def _resolve_blueprint_payload(
    *,
    repo_root: str,
    blueprint_registry: Mapping[str, object],
    blueprint_id: str,
) -> tuple[dict, dict]:
    registry_rows = _rows_by_id(_registry_rows(blueprint_registry, "blueprints"), "blueprint_id")
    row = dict(registry_rows.get(str(blueprint_id).strip()) or {})
    if not row:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint_id is missing from blueprint registry",
            {"blueprint_id": str(blueprint_id)},
        )
    blueprint_path = str(row.get("blueprint_path", "")).strip()
    if not blueprint_path:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint registry entry is missing blueprint_path",
            {"blueprint_id": str(blueprint_id)},
        )
    abs_path = os.path.join(repo_root, blueprint_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint path does not exist",
            {"blueprint_id": str(blueprint_id), "blueprint_path": _norm(blueprint_path)},
        )
    payload = _read_json_payload(abs_path)
    payload_blueprint_id = str(payload.get("blueprint_id", "")).strip()
    if payload_blueprint_id != str(blueprint_id).strip():
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint payload id does not match registry entry",
            {
                "blueprint_id": str(blueprint_id),
                "payload_blueprint_id": str(payload_blueprint_id),
                "blueprint_path": _norm(blueprint_path),
            },
        )
    return row, payload


def _resolve_parameters(blueprint_payload: Mapping[str, object], parameter_values: Mapping[str, object] | None) -> dict:
    defs = list((dict(blueprint_payload or {})).get("parameters") or [])
    if not isinstance(defs, list):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_PARAMETER_INVALID,
            "blueprint parameters must be a list",
            {"blueprint_id": str((blueprint_payload or {}).get("blueprint_id", ""))},
        )
    provided = dict(parameter_values or {})
    by_id: Dict[str, dict] = {}
    for entry in sorted((row for row in defs if isinstance(row, dict)), key=lambda row: str(row.get("parameter_id", ""))):
        parameter_id = str(entry.get("parameter_id", "")).strip()
        if not parameter_id:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                "parameter definition missing parameter_id",
                {"blueprint_id": str((blueprint_payload or {}).get("blueprint_id", ""))},
            )
        if parameter_id in by_id:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                "duplicate parameter_id in blueprint definition",
                {"parameter_id": parameter_id},
            )
        by_id[parameter_id] = dict(entry)

    unknown = sorted(set(str(key).strip() for key in provided.keys() if str(key).strip()) - set(by_id.keys()))
    if unknown:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_PARAMETER_INVALID,
            "unknown blueprint parameter(s) provided",
            {"unknown_parameters": ",".join(unknown)},
        )

    resolved = {}
    for parameter_id in sorted(by_id.keys()):
        entry = dict(by_id.get(parameter_id) or {})
        required = bool(entry.get("required", False))
        value_type = str(entry.get("value_type", "")).strip()
        if parameter_id in provided:
            value = provided.get(parameter_id)
        else:
            value = entry.get("default_value")
        if value is None and required:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                "required blueprint parameter is missing",
                {"parameter_id": parameter_id},
            )
        if value is None:
            resolved[parameter_id] = None
            continue
        if value_type == "int":
            if isinstance(value, bool) or not isinstance(value, int):
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                    "integer blueprint parameter is invalid",
                    {"parameter_id": parameter_id, "value": str(value)},
                )
            resolved[parameter_id] = int(value)
            continue
        if value_type == "bool":
            if not isinstance(value, bool):
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                    "boolean blueprint parameter is invalid",
                    {"parameter_id": parameter_id, "value": str(value)},
                )
            resolved[parameter_id] = bool(value)
            continue
        if value_type == "string":
            if not isinstance(value, str):
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                    "string blueprint parameter is invalid",
                    {"parameter_id": parameter_id, "value": str(value)},
                )
            resolved[parameter_id] = str(value)
            continue
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_PARAMETER_INVALID,
            "parameter value_type is unsupported",
            {"parameter_id": parameter_id, "value_type": value_type},
        )
    return dict((key, resolved[key]) for key in sorted(resolved.keys()))


def _normalize_bom(
    bom_ref: Mapping[str, object],
    *,
    part_class_ids: set[str],
    material_ids: set[str],
) -> dict:
    row = dict(bom_ref or {})
    required_materials = list(row.get("required_materials") or [])
    required_part_classes = list(row.get("required_part_classes") or [])
    if not isinstance(required_materials, list):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "bom required_materials must be a list",
            {"bom_id": str(row.get("bom_id", ""))},
        )
    if not isinstance(required_part_classes, list):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "bom required_part_classes must be a list",
            {"bom_id": str(row.get("bom_id", ""))},
        )
    materials = []
    for entry in sorted((item for item in required_materials if isinstance(item, dict)), key=lambda item: str(item.get("material_id_or_class", ""))):
        material_token = str(entry.get("material_id_or_class", "")).strip()
        quantity_mass_raw = _to_int(
            entry.get("quantity_mass_raw", 0),
            reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH,
            field="required_materials.quantity_mass_raw",
        )
        if not material_token:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "bom material row missing material_id_or_class",
                {"bom_id": str(row.get("bom_id", ""))},
            )
        if quantity_mass_raw < 0:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "bom material quantity_mass_raw must be >= 0",
                {"material_id_or_class": material_token},
            )
        if material_token.startswith("material.") and material_ids and material_token not in material_ids:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "bom material reference is unknown",
                {"material_id_or_class": material_token},
            )
        materials.append(
            {
                "material_id_or_class": material_token,
                "quantity_mass_raw": int(quantity_mass_raw),
            }
        )
    part_classes = []
    for entry in sorted((item for item in required_part_classes if isinstance(item, dict)), key=lambda item: str(item.get("part_class_id", ""))):
        part_class_id = str(entry.get("part_class_id", "")).strip()
        count = _to_int(entry.get("count", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="required_part_classes.count")
        if not part_class_id:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "bom part-class row missing part_class_id",
                {"bom_id": str(row.get("bom_id", ""))},
            )
        if int(count) < 0:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "bom part-class count must be >= 0",
                {"part_class_id": part_class_id},
            )
        if part_class_id not in part_class_ids:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_MISSING_PART_CLASS,
                "bom references unknown part_class_id",
                {"part_class_id": part_class_id},
            )
        part_classes.append(
            {
                "part_class_id": part_class_id,
                "count": int(count),
            }
        )
    return {
        "schema_version": "1.0.0",
        "bom_id": str(row.get("bom_id", "")).strip() or "bom.{}".format(canonical_sha256(row)[:16]),
        "description": str(row.get("description", "")).strip(),
        "required_materials": materials,
        "required_part_classes": part_classes,
        "tolerances": dict(row.get("tolerances") or {}),
        "version_introduced": str(row.get("version_introduced", "")).strip() or "1.0.0",
        "extensions": dict(row.get("extensions") or {}),
    }


def _normalize_ag(
    ag_ref: Mapping[str, object],
    *,
    part_class_ids: set[str],
    connection_type_ids: set[str],
) -> dict:
    row = dict(ag_ref or {})
    nodes_map = dict(row.get("nodes") or {})
    if not isinstance(nodes_map, dict):
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "ag nodes must be an object map",
            {"ag_id": str(row.get("ag_id", ""))},
        )
    normalized_nodes: Dict[str, dict] = {}
    for node_id in sorted(nodes_map.keys()):
        node_key = str(node_id).strip()
        node_row = dict(nodes_map.get(node_id) or {})
        payload_node_id = str(node_row.get("node_id", "")).strip()
        if not node_key or not payload_node_id or payload_node_id != node_key:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "ag node id mismatch between map key and payload",
                {"node_key": node_key, "payload_node_id": payload_node_id},
            )
        node_kind = str(node_row.get("node_kind", "")).strip()
        if node_kind not in _NODE_KINDS:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "ag node_kind is invalid",
                {"node_id": node_key, "node_kind": node_kind},
            )
        part_class_id = node_row.get("part_class_id")
        if part_class_id is None:
            part_class_token = None
        else:
            part_class_token = str(part_class_id).strip() or None
        if node_kind == "part" and not part_class_token:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_MISSING_PART_CLASS,
                "part node requires part_class_id",
                {"node_id": node_key},
            )
        if part_class_token and part_class_token not in part_class_ids:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_MISSING_PART_CLASS,
                "ag node references unknown part_class_id",
                {"node_id": node_key, "part_class_id": part_class_token},
            )
        children = sorted(set(str(item).strip() for item in list(node_row.get("children") or []) if str(item).strip()))
        material_requirements = [dict(item) for item in list(node_row.get("material_requirements") or []) if isinstance(item, dict)]
        planned_commitment_ids = sorted(
            set(str(item).strip() for item in list(node_row.get("planned_commitment_ids") or []) if str(item).strip())
        )
        tags = sorted(set(str(item).strip() for item in list(node_row.get("tags") or []) if str(item).strip()))
        normalized_nodes[node_key] = {
            "schema_version": "1.0.0",
            "node_id": node_key,
            "node_kind": node_kind,
            "part_class_id": part_class_token,
            "material_requirements": material_requirements,
            "children": children,
            "local_transform": _normalize_transform(dict(node_row.get("local_transform") or {})),
            "planned_commitment_ids": planned_commitment_ids,
            "tags": tags,
            "extensions": dict(node_row.get("extensions") or {}),
        }
    root_node_id = str(row.get("root_node_id", "")).strip()
    if not root_node_id or root_node_id not in normalized_nodes:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "ag root_node_id must reference an existing node",
            {"root_node_id": root_node_id},
        )
    for node_id in sorted(normalized_nodes.keys()):
        for child_id in list((normalized_nodes.get(node_id) or {}).get("children") or []):
            if child_id not in normalized_nodes:
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_INVALID_GRAPH,
                    "ag node children reference unknown node_id",
                    {"node_id": node_id, "child_id": str(child_id)},
                )
    edges = []
    seen_edge_ids = set()
    for entry in sorted((item for item in list(row.get("edges") or []) if isinstance(item, dict)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(entry.get("edge_id", "")).strip()
        from_node_id = str(entry.get("from_node_id", "")).strip()
        to_node_id = str(entry.get("to_node_id", "")).strip()
        connection_type_id = str(entry.get("connection_type_id", "")).strip()
        if not edge_id or edge_id in seen_edge_ids:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "ag edge_id is missing or duplicated",
                {"edge_id": edge_id},
            )
        seen_edge_ids.add(edge_id)
        if from_node_id not in normalized_nodes or to_node_id not in normalized_nodes:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "ag edge references unknown node_id",
                {"edge_id": edge_id, "from_node_id": from_node_id, "to_node_id": to_node_id},
            )
        if connection_type_id not in connection_type_ids:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "ag edge references unknown connection_type_id",
                {"edge_id": edge_id, "connection_type_id": connection_type_id},
            )
        edges.append(
            {
                "schema_version": "1.0.0",
                "edge_id": edge_id,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "connection_type_id": connection_type_id,
                "connection_params": dict(entry.get("connection_params") or {}),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    return {
        "schema_version": "1.0.0",
        "ag_id": str(row.get("ag_id", "")).strip() or "ag.{}".format(canonical_sha256(row)[:16]),
        "description": str(row.get("description", "")).strip(),
        "root_node_id": root_node_id,
        "nodes": dict((node_id, normalized_nodes[node_id]) for node_id in sorted(normalized_nodes.keys())),
        "edges": list(sorted(edges, key=lambda edge: str(edge.get("edge_id", "")))),
        "instancing_rules": dict(row.get("instancing_rules") or {}),
        "constraints": dict(row.get("constraints") or {}),
        "version_introduced": str(row.get("version_introduced", "")).strip() or "1.0.0",
        "extensions": dict(row.get("extensions") or {}),
    }


def _expanded_nodes_and_edges(
    *,
    nodes: Dict[str, dict],
    edges: list[dict],
    rules: list[dict],
    parameters: Mapping[str, object],
) -> tuple[Dict[str, dict], list[dict]]:
    expanded_nodes = dict((key, copy.deepcopy(nodes[key])) for key in sorted(nodes.keys()))
    expanded_edges = [copy.deepcopy(row) for row in sorted(edges, key=lambda edge: str(edge.get("edge_id", "")))]
    seen_edge_ids = set(str(row.get("edge_id", "")) for row in expanded_edges)

    for rule in sorted((item for item in rules if isinstance(item, dict)), key=lambda item: str(item.get("rule_id", ""))):
        rule_id = str(rule.get("rule_id", "")).strip()
        template_node_id = str(rule.get("template_node_id", "")).strip()
        count_parameter = str(rule.get("count_parameter", "")).strip()
        instance_prefix = str(rule.get("instance_prefix", "")).strip() or template_node_id
        default_count = _to_int(rule.get("default_count", 1), reason_code=REFUSAL_BLUEPRINT_PARAMETER_INVALID, field="default_count")
        if int(default_count) < 1:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                "instancing rule default_count must be >= 1",
                {"rule_id": rule_id, "default_count": int(default_count)},
            )
        if not rule_id or not template_node_id:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "instancing rule missing rule_id or template_node_id",
                {"rule_id": rule_id, "template_node_id": template_node_id},
            )
        if template_node_id not in expanded_nodes:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "instancing template_node_id is missing from AG",
                {"rule_id": rule_id, "template_node_id": template_node_id},
            )
        template_node = dict(expanded_nodes.get(template_node_id) or {})
        if list(template_node.get("children") or []):
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_INVALID_GRAPH,
                "instancing template nodes with children are not supported in MAT-3",
                {"rule_id": rule_id, "template_node_id": template_node_id},
            )
        resolved_count = int(default_count)
        if count_parameter:
            if count_parameter not in parameters:
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                    "instancing rule count_parameter is missing",
                    {"rule_id": rule_id, "count_parameter": count_parameter},
                )
            value = parameters.get(count_parameter)
            if isinstance(value, bool) or not isinstance(value, int):
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                    "instancing count_parameter must resolve to integer",
                    {"rule_id": rule_id, "count_parameter": count_parameter, "value": str(value)},
                )
            resolved_count = int(value)
        if int(resolved_count) < 1:
            raise BlueprintCompileError(
                REFUSAL_BLUEPRINT_PARAMETER_INVALID,
                "instancing resolved count must be >= 1",
                {"rule_id": rule_id, "resolved_count": int(resolved_count)},
            )
        step_mm = dict(rule.get("step_mm") or {})
        step_x = _to_int(step_mm.get("x", 0), reason_code=REFUSAL_BLUEPRINT_PARAMETER_INVALID, field="step_mm.x")
        step_y = _to_int(step_mm.get("y", 0), reason_code=REFUSAL_BLUEPRINT_PARAMETER_INVALID, field="step_mm.y")
        step_z = _to_int(step_mm.get("z", 0), reason_code=REFUSAL_BLUEPRINT_PARAMETER_INVALID, field="step_mm.z")

        connected_edges = [row for row in expanded_edges if str(row.get("from_node_id", "")) == template_node_id or str(row.get("to_node_id", "")) == template_node_id]
        parent_node_ids = [
            node_id
            for node_id in sorted(expanded_nodes.keys())
            if template_node_id in list((expanded_nodes.get(node_id) or {}).get("children") or [])
        ]

        for index in range(1, int(resolved_count)):
            new_node_id = "{}.{}".format(instance_prefix, str(index).zfill(4))
            if new_node_id in expanded_nodes:
                raise BlueprintCompileError(
                    REFUSAL_BLUEPRINT_INVALID_GRAPH,
                    "instanced node_id collision detected",
                    {"rule_id": rule_id, "node_id": new_node_id},
                )
            new_node = copy.deepcopy(template_node)
            new_node["node_id"] = new_node_id
            transform = dict(new_node.get("local_transform") or {})
            position = dict(transform.get("position_mm") or {})
            position["x"] = int(_to_int(position.get("x", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="position_mm.x") + (int(step_x) * int(index)))
            position["y"] = int(_to_int(position.get("y", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="position_mm.y") + (int(step_y) * int(index)))
            position["z"] = int(_to_int(position.get("z", 0), reason_code=REFUSAL_BLUEPRINT_INVALID_GRAPH, field="position_mm.z") + (int(step_z) * int(index)))
            transform["position_mm"] = position
            new_node["local_transform"] = transform
            tags = sorted(set(str(item).strip() for item in list(new_node.get("tags") or []) if str(item).strip()) | {"instanced"})
            new_node["tags"] = tags
            expanded_nodes[new_node_id] = new_node

            for edge in sorted(connected_edges, key=lambda row: str(row.get("edge_id", ""))):
                base_edge_id = str(edge.get("edge_id", "")).strip()
                new_edge_id = "{}.{}".format(base_edge_id, str(index).zfill(4))
                if not new_edge_id or new_edge_id in seen_edge_ids:
                    raise BlueprintCompileError(
                        REFUSAL_BLUEPRINT_INVALID_GRAPH,
                        "instanced edge_id collision detected",
                        {"rule_id": rule_id, "edge_id": new_edge_id},
                    )
                seen_edge_ids.add(new_edge_id)
                copied = copy.deepcopy(edge)
                copied["edge_id"] = new_edge_id
                if str(copied.get("from_node_id", "")) == template_node_id:
                    copied["from_node_id"] = new_node_id
                if str(copied.get("to_node_id", "")) == template_node_id:
                    copied["to_node_id"] = new_node_id
                expanded_edges.append(copied)

            for parent_node_id in parent_node_ids:
                parent = dict(expanded_nodes.get(parent_node_id) or {})
                children = list(parent.get("children") or [])
                if new_node_id not in children:
                    children.append(new_node_id)
                parent["children"] = children
                expanded_nodes[parent_node_id] = parent

    normalized_nodes = {}
    for node_id in sorted(expanded_nodes.keys()):
        row = dict(expanded_nodes.get(node_id) or {})
        row["children"] = sorted(set(str(item).strip() for item in list(row.get("children") or []) if str(item).strip()))
        normalized_nodes[node_id] = row
    normalized_edges = sorted(expanded_edges, key=lambda row: str(row.get("edge_id", "")))
    return normalized_nodes, normalized_edges


def blueprint_compile_cache_key(*, blueprint_id: str, parameters: Mapping[str, object], pack_lock_hash: str) -> str:
    params_hash = canonical_sha256(dict((str(key), (dict(parameters or {})).get(key)) for key in sorted((parameters or {}).keys())))
    return canonical_sha256(
        {
            "blueprint_id": str(blueprint_id),
            "params_hash": str(params_hash),
            "pack_lock_hash": str(pack_lock_hash),
        }
    )


def compile_blueprint_artifacts(
    *,
    repo_root: str,
    blueprint_id: str,
    parameter_values: Mapping[str, object] | None,
    pack_lock_hash: str,
    blueprint_registry: Mapping[str, object],
    part_class_registry: Mapping[str, object],
    connection_type_registry: Mapping[str, object],
    material_class_registry: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    blueprint_token = str(blueprint_id).strip()
    if not blueprint_token:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint_id is required",
            {},
        )
    pack_hash = str(pack_lock_hash).strip()
    if not pack_hash:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "pack_lock_hash is required for deterministic artifact identity",
            {"blueprint_id": blueprint_token},
        )

    part_class_ids = set(_rows_by_id(_registry_rows(part_class_registry, "part_classes"), "part_class_id").keys())
    connection_type_ids = set(_rows_by_id(_registry_rows(connection_type_registry, "connection_types"), "connection_type_id").keys())
    material_ids = set(_rows_by_id(_registry_rows(material_class_registry, "materials"), "material_id").keys())

    registry_row, blueprint_payload = _resolve_blueprint_payload(
        repo_root=str(repo_root),
        blueprint_registry=blueprint_registry,
        blueprint_id=blueprint_token,
    )
    parameters = _resolve_parameters(blueprint_payload, parameter_values)
    bom_ref = dict(blueprint_payload.get("bom_ref") or {})
    ag_ref = dict(blueprint_payload.get("ag_ref") or {})
    if "required_materials" not in bom_ref:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint bom_ref must be inline at MAT-3",
            {"blueprint_id": blueprint_token},
        )
    if "nodes" not in ag_ref:
        raise BlueprintCompileError(
            REFUSAL_BLUEPRINT_INVALID_GRAPH,
            "blueprint ag_ref must be inline at MAT-3",
            {"blueprint_id": blueprint_token},
        )
    normalized_bom = _normalize_bom(bom_ref, part_class_ids=part_class_ids, material_ids=material_ids)
    normalized_ag = _normalize_ag(ag_ref, part_class_ids=part_class_ids, connection_type_ids=connection_type_ids)

    instancing_rules = list((dict(normalized_ag.get("instancing_rules") or {})).get("rules") or [])
    expanded_nodes, expanded_edges = _expanded_nodes_and_edges(
        nodes=dict(normalized_ag.get("nodes") or {}),
        edges=list(normalized_ag.get("edges") or []),
        rules=instancing_rules,
        parameters=parameters,
    )
    normalized_ag["nodes"] = dict((node_id, expanded_nodes[node_id]) for node_id in sorted(expanded_nodes.keys()))
    normalized_ag["edges"] = sorted(expanded_edges, key=lambda row: str(row.get("edge_id", "")))

    params_hash = canonical_sha256(parameters)
    cache_key = blueprint_compile_cache_key(
        blueprint_id=blueprint_token,
        parameters=parameters,
        pack_lock_hash=pack_hash,
    )
    input_hashes = {
        "blueprint_registry_hash": _registry_hash(blueprint_registry),
        "part_class_registry_hash": _registry_hash(part_class_registry),
        "connection_type_registry_hash": _registry_hash(connection_type_registry),
        "material_class_registry_hash": _registry_hash(material_class_registry),
        "blueprint_entry_hash": canonical_sha256(registry_row),
        "blueprint_payload_hash": canonical_sha256(blueprint_payload),
        "params_hash": params_hash,
        "pack_lock_hash": pack_hash,
    }
    provenance_header = {
        "bii_id": _BII_ID,
        "tool_id": _TOOL_ID,
        "tool_version": _TOOL_VERSION,
        "blueprint_id": blueprint_token,
        "input_hashes": input_hashes,
        "cache_key": cache_key,
    }

    bom_artifact = {
        "format_version": "1.0.0",
        "artifact_type": "compiled_bom",
        "blueprint_id": blueprint_token,
        "parameters": parameters,
        "bom": normalized_bom,
        "provenance_header": provenance_header,
        "artifact_hash": "",
    }
    bom_artifact["artifact_hash"] = canonical_sha256(dict(bom_artifact))

    ag_artifact = {
        "format_version": "1.0.0",
        "artifact_type": "compiled_ag",
        "blueprint_id": blueprint_token,
        "parameters": parameters,
        "ag": normalized_ag,
        "provenance_header": provenance_header,
        "artifact_hash": "",
    }
    ag_artifact["artifact_hash"] = canonical_sha256(dict(ag_artifact))

    return {
        "result": "complete",
        "blueprint_id": blueprint_token,
        "parameters": parameters,
        "cache_key": cache_key,
        "params_hash": params_hash,
        "pack_lock_hash": pack_hash,
        "compilation_provenance_header": provenance_header,
        "compiled_bom_artifact": bom_artifact,
        "compiled_ag_artifact": ag_artifact,
    }


def blueprint_bom_summary(compiled_bom_artifact: Mapping[str, object]) -> dict:
    row = dict(compiled_bom_artifact or {})
    bom = dict(row.get("bom") or {})
    required_materials = list(bom.get("required_materials") or [])
    required_part_classes = list(bom.get("required_part_classes") or [])
    material_rows = []
    total_mass_raw = 0
    for entry in sorted((item for item in required_materials if isinstance(item, dict)), key=lambda item: str(item.get("material_id_or_class", ""))):
        material_token = str(entry.get("material_id_or_class", "")).strip()
        quantity_mass_raw = int(entry.get("quantity_mass_raw", 0) or 0)
        total_mass_raw += int(quantity_mass_raw)
        material_rows.append({"material_id_or_class": material_token, "quantity_mass_raw": int(quantity_mass_raw)})
    part_rows = []
    total_part_count = 0
    for entry in sorted((item for item in required_part_classes if isinstance(item, dict)), key=lambda item: str(item.get("part_class_id", ""))):
        part_class_id = str(entry.get("part_class_id", "")).strip()
        count = int(entry.get("count", 0) or 0)
        total_part_count += int(count)
        part_rows.append({"part_class_id": part_class_id, "count": int(count)})
    payload = {
        "blueprint_id": str(row.get("blueprint_id", "")),
        "bom_id": str(bom.get("bom_id", "")),
        "material_rows": material_rows,
        "part_rows": part_rows,
        "total_mass_raw": int(total_mass_raw),
        "total_part_count": int(total_part_count),
        "material_row_count": len(material_rows),
        "part_row_count": len(part_rows),
    }
    payload["summary_hash"] = canonical_sha256(payload)
    return payload


def _rgb_from_token(token: str) -> dict:
    digest = canonical_sha256({"token": str(token)})
    return {
        "r": 64 + (int(digest[0:2], 16) % 160),
        "g": 64 + (int(digest[2:4], 16) % 160),
        "b": 64 + (int(digest[4:6], 16) % 160),
    }


def build_blueprint_ghost_overlay(
    *,
    compiled_ag_artifact: Mapping[str, object],
    blueprint_id: str,
    include_labels: bool = True,
) -> dict:
    artifact = dict(compiled_ag_artifact or {})
    ag = dict(artifact.get("ag") or {})
    nodes = dict(ag.get("nodes") or {})
    renderables = []
    materials_by_id: Dict[str, dict] = {}

    for node_id in sorted(nodes.keys()):
        node = dict(nodes.get(node_id) or {})
        part_class_id = str(node.get("part_class_id", "")).strip()
        node_kind = str(node.get("node_kind", "")).strip()
        material_seed = part_class_id or node_kind or node_id
        material_digest = canonical_sha256({"blueprint_id": blueprint_id, "node_id": node_id, "seed": material_seed})
        material_id = "mat.blueprint.ghost.{}".format(material_digest[:12])
        if material_id not in materials_by_id:
            color = _rgb_from_token(material_seed)
            materials_by_id[material_id] = {
                "schema_version": "1.0.0",
                "material_id": material_id,
                "base_color": color,
                "roughness": 420,
                "metallic": 0,
                "emission": {"r": color["r"], "g": color["g"], "b": color["b"], "strength": 190},
                "transparency": {"mode": "alpha", "value_permille": 380},
                "pattern_id": None,
                "extensions": {"blueprint_ghost": True, "node_kind": node_kind},
            }
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.blueprint.{}.{}".format(canonical_sha256({"blueprint_id": blueprint_id, "node_id": node_id})[:16], node_id),
                "semantic_id": "overlay.blueprint.node.{}".format(node_id),
                "primitive_id": "prim.line.debug",
                "transform": _normalize_transform(dict(node.get("local_transform") or {})),
                "material_id": material_id,
                "layer_tags": ["overlay", "ui"],
                "label": str(node_id) if bool(include_labels) else None,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {
                    "blueprint_id": str(blueprint_id),
                    "node_id": str(node_id),
                    "part_class_id": part_class_id,
                    "node_kind": node_kind,
                },
            }
        )

    label_material_id = "mat.blueprint.label.{}".format(canonical_sha256({"blueprint_id": blueprint_id, "label": True})[:12])
    materials_by_id[label_material_id] = {
        "schema_version": "1.0.0",
        "material_id": label_material_id,
        "base_color": {"r": 226, "g": 236, "b": 244},
        "roughness": 240,
        "metallic": 30,
        "emission": None,
        "transparency": None,
        "pattern_id": None,
        "extensions": {"blueprint_ghost": True, "label": True},
    }
    renderables.append(
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.blueprint.label.{}".format(canonical_sha256({"blueprint_id": blueprint_id, "summary": True})[:16]),
            "semantic_id": "overlay.blueprint.label.{}".format(blueprint_id),
            "primitive_id": "prim.glyph.label",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": label_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": "blueprint:{}".format(str(blueprint_id)),
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": False},
            "extensions": {"blueprint_id": str(blueprint_id), "summary_label": True},
        }
    )

    sorted_renderables = sorted(renderables, key=lambda row: str(row.get("renderable_id", "")))
    sorted_materials = [materials_by_id[key] for key in sorted(materials_by_id.keys())]
    payload = {
        "blueprint_id": str(blueprint_id),
        "renderables": sorted_renderables,
        "materials": sorted_materials,
    }
    payload["overlay_hash"] = canonical_sha256(payload)
    return payload
