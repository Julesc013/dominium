"""Deterministic MECH-1 structural graph mechanics engine (meso tier)."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.control.effects import get_effective_modifier
from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_PLASTIC_THRESHOLD_PERMILLE = 850
DEFAULT_FAILURE_THRESHOLD_PERMILLE = 1000

_VALID_FAILURE_STATES = {"none", "yielded", "failed"}
_TENSION_ONLY_TYPES = {"conn.rope", "conn.cable"}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def _failure_state(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_FAILURE_STATES:
        return token
    return "none"


def connection_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("connection_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("connection_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("connection_type_id", ""))):
        connection_type_id = str(row.get("connection_type_id", "")).strip()
        if not connection_type_id:
            continue
        out[connection_type_id] = {
            "schema_version": "1.0.0",
            "connection_type_id": connection_type_id,
            "description": str(row.get("description", "")).strip(),
            "default_stiffness": int(max(0, _as_int(row.get("default_stiffness", 0), 0))),
            "default_max_load": int(max(0, _as_int(row.get("default_max_load", 0), 0))),
            "supports_rotation": bool(row.get("supports_rotation", False)),
            "supports_translation": bool(row.get("supports_translation", False)),
            "requires_part_classes": _sorted_unique_strings(row.get("requires_part_classes")),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def build_structural_node(
    *,
    node_id: str,
    assembly_part_id: str,
    applied_force: int = 0,
    applied_torque: int = 0,
    elastic_strain: int = 0,
    plastic_strain: int = 0,
    failure_state: str = "none",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    row = {
        "schema_version": "1.0.0",
        "node_id": str(node_id).strip(),
        "assembly_part_id": str(assembly_part_id).strip(),
        "applied_force": int(_as_int(applied_force, 0)),
        "applied_torque": int(_as_int(applied_torque, 0)),
        "elastic_strain": int(max(0, _as_int(elastic_strain, 0))),
        "plastic_strain": int(max(0, _as_int(plastic_strain, 0))),
        "failure_state": _failure_state(failure_state),
        "deterministic_fingerprint": "",
        "extensions": _canon(dict(extensions or {})),
    }
    return _with_fingerprint(row)


def normalize_structural_node_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", ""))):
        node_id = str(row.get("node_id", "")).strip()
        assembly_part_id = str(row.get("assembly_part_id", "")).strip()
        if not node_id or not assembly_part_id:
            continue
        out[node_id] = build_structural_node(
            node_id=node_id,
            assembly_part_id=assembly_part_id,
            applied_force=_as_int(row.get("applied_force", 0), 0),
            applied_torque=_as_int(row.get("applied_torque", 0), 0),
            elastic_strain=_as_int(row.get("elastic_strain", 0), 0),
            plastic_strain=_as_int(row.get("plastic_strain", 0), 0),
            failure_state=_failure_state(row.get("failure_state")),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def build_structural_edge(
    *,
    edge_id: str,
    node_a_id: str,
    node_b_id: str,
    connection_type_id: str,
    stiffness: int,
    max_load: int,
    fatigue_state: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
    failure_state: str = "none",
    stress_ratio_permille: int = 0,
    applied_load: int = 0,
    effective_max_load: int | None = None,
    last_evaluated_tick: int | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "edge_id": str(edge_id).strip(),
        "node_a_id": str(node_a_id).strip(),
        "node_b_id": str(node_b_id).strip(),
        "connection_type_id": str(connection_type_id).strip() or "conn.rigid_joint",
        "stiffness": int(max(0, _as_int(stiffness, 0))),
        "max_load": int(max(0, _as_int(max_load, 0))),
        "fatigue_state": _canon(dict(fatigue_state or {})),
        "failure_state": _failure_state(failure_state),
        "stress_ratio_permille": int(max(0, _as_int(stress_ratio_permille, 0))),
        "applied_load": int(max(0, _as_int(applied_load, 0))),
        "effective_max_load": (
            int(max(0, _as_int(effective_max_load, 0)))
            if effective_max_load is not None
            else int(max(0, _as_int(max_load, 0)))
        ),
        "last_evaluated_tick": None if last_evaluated_tick is None else int(max(0, _as_int(last_evaluated_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(dict(extensions or {})),
    }
    return _with_fingerprint(payload)


def normalize_structural_edge_rows(
    rows: object,
    *,
    connection_type_rows: Mapping[str, Mapping[str, object]] | None = None,
) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    connection_rows = dict(connection_type_rows or {})
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(row.get("edge_id", "")).strip()
        node_a_id = str(row.get("node_a_id", "")).strip()
        node_b_id = str(row.get("node_b_id", "")).strip()
        if not edge_id or not node_a_id or not node_b_id:
            continue
        connection_type_id = str(row.get("connection_type_id", "")).strip() or "conn.rigid_joint"
        type_row = dict(connection_rows.get(connection_type_id) or {})
        default_stiffness = int(max(0, _as_int(type_row.get("default_stiffness", 0), 0)))
        default_max_load = int(max(0, _as_int(type_row.get("default_max_load", 0), 0)))
        edge = build_structural_edge(
            edge_id=edge_id,
            node_a_id=node_a_id,
            node_b_id=node_b_id,
            connection_type_id=connection_type_id,
            stiffness=int(max(0, _as_int(row.get("stiffness", default_stiffness), default_stiffness))),
            max_load=int(max(0, _as_int(row.get("max_load", default_max_load), default_max_load))),
            fatigue_state=_as_map(row.get("fatigue_state")),
            extensions=_as_map(row.get("extensions")),
            failure_state=_failure_state(row.get("failure_state")),
            stress_ratio_permille=_as_int(row.get("stress_ratio_permille", 0), 0),
            applied_load=_as_int(row.get("applied_load", 0), 0),
            effective_max_load=(
                int(max(0, _as_int(row.get("effective_max_load", row.get("max_load", default_max_load)), default_max_load)))
            ),
            last_evaluated_tick=(
                None
                if row.get("last_evaluated_tick") is None
                else int(max(0, _as_int(row.get("last_evaluated_tick", 0), 0)))
            ),
        )
        out[edge_id] = edge
    return [dict(out[key]) for key in sorted(out.keys())]


def build_structural_graph(
    *,
    structural_graph_id: str,
    assembly_id: str,
    node_ids: object,
    edge_ids: object,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "structural_graph_id": str(structural_graph_id).strip(),
        "assembly_id": str(assembly_id).strip(),
        "node_ids": _sorted_unique_strings(node_ids),
        "edge_ids": _sorted_unique_strings(edge_ids),
        "deterministic_fingerprint": "",
        "extensions": _canon(dict(extensions or {})),
    }
    return _with_fingerprint(payload)


def normalize_structural_graph_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("structural_graph_id", ""))):
        structural_graph_id = str(row.get("structural_graph_id", "")).strip()
        assembly_id = str(row.get("assembly_id", "")).strip()
        if not structural_graph_id or not assembly_id:
            continue
        out[structural_graph_id] = build_structural_graph(
            structural_graph_id=structural_graph_id,
            assembly_id=assembly_id,
            node_ids=row.get("node_ids"),
            edge_ids=row.get("edge_ids"),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def _incident_degrees(*, edge_rows: List[dict], graph_node_ids: List[str]) -> Dict[str, int]:
    node_set = set(graph_node_ids)
    degree_by_node = dict((node_id, 0) for node_id in graph_node_ids)
    for row in edge_rows:
        if str(row.get("failure_state", "none")).strip() == "failed":
            continue
        node_a_id = str(row.get("node_a_id", "")).strip()
        node_b_id = str(row.get("node_b_id", "")).strip()
        if node_a_id in node_set:
            degree_by_node[node_a_id] = int(max(0, _as_int(degree_by_node.get(node_a_id, 0), 0))) + 1
        if node_b_id in node_set:
            degree_by_node[node_b_id] = int(max(0, _as_int(degree_by_node.get(node_b_id, 0), 0))) + 1
    return degree_by_node


def _ratio_permille(load_value: int, max_load_value: int) -> int:
    load = int(max(0, _as_int(load_value, 0)))
    max_load = int(max(0, _as_int(max_load_value, 0)))
    if max_load <= 0:
        return 1000 if load > 0 else 0
    return int((int(load) * 1000) // int(max_load))


def evaluate_structural_graphs(
    *,
    structural_graph_rows: object,
    structural_node_rows: object,
    structural_edge_rows: object,
    current_tick: int,
    max_cost_units: int,
    cost_units_per_graph: int = 1,
    connection_type_registry: Mapping[str, object] | None = None,
    effect_rows: object = None,
    effect_type_registry: Mapping[str, object] | None = None,
    stacking_policy_registry: Mapping[str, object] | None = None,
    plastic_threshold_permille: int = DEFAULT_PLASTIC_THRESHOLD_PERMILLE,
    failure_threshold_permille: int = DEFAULT_FAILURE_THRESHOLD_PERMILLE,
) -> dict:
    connection_rows = connection_type_rows_by_id(connection_type_registry)
    graphs = normalize_structural_graph_rows(structural_graph_rows)
    nodes = normalize_structural_node_rows(structural_node_rows)
    edges = normalize_structural_edge_rows(structural_edge_rows, connection_type_rows=connection_rows)

    node_by_id = dict((str(row.get("node_id", "")).strip(), dict(row)) for row in nodes)
    edge_by_id = dict((str(row.get("edge_id", "")).strip(), dict(row)) for row in edges)

    tick = int(max(0, _as_int(current_tick, 0)))
    unit_cost = int(max(1, _as_int(cost_units_per_graph, 1)))
    budget = int(max(0, _as_int(max_cost_units, 0)))
    total_graphs = len(graphs)
    max_graphs_from_budget = 0 if budget <= 0 else min(total_graphs, budget // unit_cost)
    selected_graphs = list(graphs[:max_graphs_from_budget])
    skipped_graphs = list(graphs[max_graphs_from_budget:])

    fracture_edge_ids: List[str] = []
    node_peak_ratio: Dict[str, int] = dict((node_id, 0) for node_id in node_by_id.keys())
    evaluated_graph_ids: List[str] = []

    for graph in selected_graphs:
        graph_id = str(graph.get("structural_graph_id", "")).strip()
        if not graph_id:
            continue
        evaluated_graph_ids.append(graph_id)
        graph_node_ids = [token for token in _sorted_unique_strings(graph.get("node_ids")) if token in set(node_by_id.keys())]
        graph_edge_ids = [token for token in _sorted_unique_strings(graph.get("edge_ids")) if token in set(edge_by_id.keys())]
        graph_edges = [dict(edge_by_id[edge_id]) for edge_id in graph_edge_ids]
        degree_by_node = _incident_degrees(edge_rows=graph_edges, graph_node_ids=graph_node_ids)
        node_id_set = set(graph_node_ids)

        for edge_id in graph_edge_ids:
            row = dict(edge_by_id.get(edge_id) or {})
            node_a_id = str(row.get("node_a_id", "")).strip()
            node_b_id = str(row.get("node_b_id", "")).strip()
            if node_a_id not in node_id_set or node_b_id not in node_id_set:
                continue
            node_a = dict(node_by_id.get(node_a_id) or {})
            node_b = dict(node_by_id.get(node_b_id) or {})

            degree_a = int(max(1, _as_int(degree_by_node.get(node_a_id, 1), 1)))
            degree_b = int(max(1, _as_int(degree_by_node.get(node_b_id, 1), 1)))
            force_a = int(_as_int(node_a.get("applied_force", 0), 0))
            force_b = int(_as_int(node_b.get("applied_force", 0), 0))
            torque_a = int(_as_int(node_a.get("applied_torque", 0), 0))
            torque_b = int(_as_int(node_b.get("applied_torque", 0), 0))

            load_share = int(abs(force_a) // degree_a) + int(abs(force_b) // degree_b)
            torque_share = int(abs(torque_a) // max(1, degree_a * 4)) + int(abs(torque_b) // max(1, degree_b * 4))
            stiffness = int(max(1, _as_int(row.get("stiffness", 0), 0)))
            computed_load = int(((int(load_share) + int(torque_share)) * int(stiffness)) // 1000)
            computed_load = int(max(0, computed_load))

            type_ext = _as_map((dict(connection_rows.get(str(row.get("connection_type_id", "")).strip()) or {})).get("extensions"))
            edge_ext = _as_map(row.get("extensions"))
            tension_only = bool(
                str(row.get("connection_type_id", "")).strip() in _TENSION_ONLY_TYPES
                or bool(type_ext.get("tension_only", False))
                or bool(edge_ext.get("tension_only", False))
            )
            if tension_only and int(force_a + force_b) < 0:
                computed_load = 0

            base_max_load = int(max(0, _as_int(row.get("max_load", 0), 0)))
            effective_max_load = int(base_max_load)
            effect_modifier = get_effective_modifier(
                target_id=edge_id,
                key="machine_output_permille",
                effect_rows=effect_rows,
                current_tick=tick,
                effect_type_registry=effect_type_registry,
                stacking_policy_registry=stacking_policy_registry,
            )
            if bool(effect_modifier.get("present", False)):
                modifier_permille = int(max(1, _as_int(effect_modifier.get("value", 1000), 1000)))
                effective_max_load = int((int(effective_max_load) * int(modifier_permille)) // 1000)

            stress_ratio_permille = _ratio_permille(computed_load, effective_max_load)
            current_failure_state = _failure_state(row.get("failure_state"))
            next_failure_state = current_failure_state
            if current_failure_state != "failed":
                if stress_ratio_permille > int(max(0, _as_int(failure_threshold_permille, DEFAULT_FAILURE_THRESHOLD_PERMILLE))):
                    next_failure_state = "yielded"
                elif stress_ratio_permille > int(max(0, _as_int(plastic_threshold_permille, DEFAULT_PLASTIC_THRESHOLD_PERMILLE))):
                    next_failure_state = "yielded"
                else:
                    next_failure_state = "none"

            if (
                current_failure_state != "failed"
                and stress_ratio_permille > int(max(0, _as_int(failure_threshold_permille, DEFAULT_FAILURE_THRESHOLD_PERMILLE)))
            ):
                fracture_edge_ids.append(edge_id)

            updated_ext = dict(edge_ext)
            updated_ext["tension_only"] = bool(tension_only)
            updated_ext["effect_machine_output_permille"] = (
                int(max(1, _as_int(effect_modifier.get("value", 1000), 1000)))
                if bool(effect_modifier.get("present", False))
                else None
            )
            updated_ext["connection_supports_rotation"] = bool(
                (dict(connection_rows.get(str(row.get("connection_type_id", "")).strip()) or {})).get("supports_rotation", False)
            )
            updated_ext["connection_supports_translation"] = bool(
                (dict(connection_rows.get(str(row.get("connection_type_id", "")).strip()) or {})).get("supports_translation", False)
            )
            edge_by_id[edge_id] = build_structural_edge(
                edge_id=edge_id,
                node_a_id=node_a_id,
                node_b_id=node_b_id,
                connection_type_id=str(row.get("connection_type_id", "")).strip() or "conn.rigid_joint",
                stiffness=stiffness,
                max_load=base_max_load,
                fatigue_state=_as_map(row.get("fatigue_state")),
                extensions=updated_ext,
                failure_state=next_failure_state,
                stress_ratio_permille=stress_ratio_permille,
                applied_load=computed_load,
                effective_max_load=effective_max_load,
                last_evaluated_tick=tick,
            )

            node_peak_ratio[node_a_id] = int(max(int(node_peak_ratio.get(node_a_id, 0)), int(stress_ratio_permille)))
            node_peak_ratio[node_b_id] = int(max(int(node_peak_ratio.get(node_b_id, 0)), int(stress_ratio_permille)))

    for node_id in sorted(node_peak_ratio.keys()):
        row = dict(node_by_id.get(node_id) or {})
        if not row:
            continue
        peak = int(max(0, _as_int(node_peak_ratio.get(node_id, 0), 0)))
        current_plastic = int(max(0, _as_int(row.get("plastic_strain", 0), 0)))
        elastic = int(min(1000, peak))
        plastic_increment = int(max(0, peak - int(max(0, _as_int(plastic_threshold_permille, DEFAULT_PLASTIC_THRESHOLD_PERMILLE)))) // 20)
        next_plastic = int(max(0, current_plastic + plastic_increment))

        current_failure = _failure_state(row.get("failure_state"))
        next_failure = current_failure
        if current_failure != "failed":
            if peak > int(max(0, _as_int(failure_threshold_permille, DEFAULT_FAILURE_THRESHOLD_PERMILLE))):
                next_failure = "failed"
            elif peak > int(max(0, _as_int(plastic_threshold_permille, DEFAULT_PLASTIC_THRESHOLD_PERMILLE))):
                next_failure = "yielded"
            else:
                next_failure = "none"

        ext = _as_map(row.get("extensions"))
        ext["peak_stress_ratio_permille"] = int(peak)
        ext["last_mechanics_tick"] = int(tick)
        node_by_id[node_id] = build_structural_node(
            node_id=node_id,
            assembly_part_id=str(row.get("assembly_part_id", "")).strip(),
            applied_force=int(_as_int(row.get("applied_force", 0), 0)),
            applied_torque=int(_as_int(row.get("applied_torque", 0), 0)),
            elastic_strain=elastic,
            plastic_strain=next_plastic,
            failure_state=next_failure,
            extensions=ext,
        )

    updated_nodes = normalize_structural_node_rows(list(node_by_id.values()))
    updated_edges = normalize_structural_edge_rows(
        list(edge_by_id.values()),
        connection_type_rows=connection_rows,
    )
    updated_graphs = normalize_structural_graph_rows(graphs)

    out = {
        "structural_graph_rows": updated_graphs,
        "structural_node_rows": updated_nodes,
        "structural_edge_rows": updated_edges,
        "evaluated_graph_ids": sorted(set(str(token).strip() for token in evaluated_graph_ids if str(token).strip())),
        "skipped_graph_ids": sorted(
            set(str(row.get("structural_graph_id", "")).strip() for row in skipped_graphs if str(row.get("structural_graph_id", "")).strip())
        ),
        "fracture_edge_ids": sorted(set(str(token).strip() for token in fracture_edge_ids if str(token).strip())),
        "cost_units_used": int(len(selected_graphs) * unit_cost),
        "degraded": bool(len(skipped_graphs) > 0),
        "degrade_reason": "degrade.mechanics.budget" if len(skipped_graphs) > 0 else None,
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def summarize_stress_for_target(
    *,
    target_id: str,
    structural_graph_rows: object,
    structural_edge_rows: object,
) -> dict:
    graph_rows = normalize_structural_graph_rows(structural_graph_rows)
    edge_rows = normalize_structural_edge_rows(structural_edge_rows)
    edge_by_id = dict((str(row.get("edge_id", "")).strip(), dict(row)) for row in edge_rows)
    token = str(target_id).strip()

    candidate_graph_ids = set()
    if token.startswith("structural.graph."):
        candidate_graph_ids.add(token)
    for row in graph_rows:
        graph_id = str(row.get("structural_graph_id", "")).strip()
        assembly_id = str(row.get("assembly_id", "")).strip()
        if token in {graph_id, assembly_id}:
            candidate_graph_ids.add(graph_id)

    matching_edges: List[dict] = []
    for row in graph_rows:
        graph_id = str(row.get("structural_graph_id", "")).strip()
        if graph_id not in candidate_graph_ids:
            continue
        for edge_id in _sorted_unique_strings(row.get("edge_ids")):
            edge_row = dict(edge_by_id.get(edge_id) or {})
            if edge_row:
                matching_edges.append(edge_row)

    max_ratio = 0
    near_fracture = 0
    failed_count = 0
    for row in matching_edges:
        ratio = int(max(0, _as_int(row.get("stress_ratio_permille", 0), 0)))
        max_ratio = max(max_ratio, ratio)
        if ratio >= 900:
            near_fracture += 1
        if _failure_state(row.get("failure_state")) == "failed":
            failed_count += 1

    payload = {
        "target_id": token,
        "matching_graph_ids": sorted(candidate_graph_ids),
        "edge_count": int(len(matching_edges)),
        "max_stress_ratio_permille": int(max_ratio),
        "near_fracture_edge_count": int(near_fracture),
        "failed_edge_count": int(failed_count),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_FAILURE_THRESHOLD_PERMILLE",
    "DEFAULT_PLASTIC_THRESHOLD_PERMILLE",
    "build_structural_edge",
    "build_structural_graph",
    "build_structural_node",
    "connection_type_rows_by_id",
    "evaluate_structural_graphs",
    "normalize_structural_edge_rows",
    "normalize_structural_graph_rows",
    "normalize_structural_node_rows",
    "summarize_stress_for_target",
]
