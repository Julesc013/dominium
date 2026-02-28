"""Deterministic MAT-9 inspection snapshot engine (derived-only)."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_INSPECT_FORBIDDEN_BY_LAW = "refusal.inspect.forbidden_by_law"
REFUSAL_INSPECT_BUDGET_EXCEEDED = "refusal.inspect.budget_exceeded"
REFUSAL_INSPECT_TARGET_INVALID = "refusal.inspect.target_invalid"

_VALID_TARGET_KINDS = {"structure", "project", "node", "manifest", "cohort", "faction", "machine", "port", "graph"}
_VALID_FIDELITY = ("macro", "meso", "micro")
_SECTION_IDS_BY_FIDELITY = {
    "macro": [
        "section.material_stocks",
        "section.flow_summary",
        "section.flow_utilization",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
    ],
    "meso": [
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.flow_utilization",
        "section.ag_progress",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
    ],
    "micro": [
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.flow_utilization",
        "section.ag_progress",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
        "section.micro_parts_summary",
    ],
}
_SECTION_IDS_BY_FIDELITY_GRAPH = {
    "macro": [
        "section.networkgraph.summary",
    ],
    "meso": [
        "section.networkgraph.summary",
        "section.networkgraph.route",
        "section.networkgraph.capacity_utilization",
    ],
    "micro": [
        "section.networkgraph.summary",
        "section.networkgraph.route",
        "section.networkgraph.capacity_utilization",
    ],
}
_DEFAULT_SECTION_ROWS = {
    "section.material_stocks": {"title": "Material Stocks", "extensions": {"cost_units": 1}},
    "section.batches_summary": {"title": "Batches Summary", "extensions": {"cost_units": 2}},
    "section.flow_summary": {"title": "Flow Summary", "extensions": {"cost_units": 1}},
    "section.flow_utilization": {"title": "Flow Utilization", "extensions": {"cost_units": 1}},
    "section.networkgraph.summary": {"title": "NetworkGraph Summary", "extensions": {"cost_units": 1}},
    "section.networkgraph.route": {"title": "NetworkGraph Route", "extensions": {"cost_units": 2}},
    "section.networkgraph.capacity_utilization": {
        "title": "NetworkGraph Capacity Utilization",
        "extensions": {"cost_units": 2},
    },
    "section.ag_progress": {"title": "Assembly Progress", "extensions": {"cost_units": 2}},
    "section.maintenance_backlog": {"title": "Maintenance Backlog", "extensions": {"cost_units": 1}},
    "section.failure_risk_summary": {"title": "Failure Risk Summary", "extensions": {"cost_units": 1}},
    "section.commitments_summary": {"title": "Commitments", "extensions": {"cost_units": 2}},
    "section.events_summary": {"title": "Events", "extensions": {"cost_units": 2}},
    "section.reenactment_link": {"title": "Reenactment", "extensions": {"cost_units": 1}},
    "section.micro_parts_summary": {"title": "Micro Parts Summary", "extensions": {"cost_units": 4}},
}


class InspectionError(ValueError):
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
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _quantize_map(values: object, *, step: int) -> dict:
    if not isinstance(values, dict):
        return {}
    quant = max(1, _as_int(step, 1))
    out = {}
    for key, value in sorted(values.items(), key=lambda item: str(item[0])):
        token = str(key).strip()
        if not token:
            continue
        raw = _as_int(value, 0)
        if quant > 1:
            raw = (raw // quant) * quant
        out[token] = int(raw)
    return out


def _target_kind_from_target_id(target_id: str) -> str:
    token = str(target_id or "").strip()
    if token.startswith("graph."):
        return "graph"
    if token.startswith("machine."):
        return "machine"
    if token.startswith("port."):
        return "port"
    if token.startswith("assembly.structure_instance."):
        return "structure"
    if token.startswith("project.construction."):
        return "project"
    if token.startswith("node.") or token.startswith("logistics.node."):
        return "node"
    if token.startswith("manifest."):
        return "manifest"
    if token.startswith("cohort."):
        return "cohort"
    if token.startswith("faction."):
        return "faction"
    return "structure"


def normalize_inspection_request_row(row: Mapping[str, object], *, current_tick: int) -> dict:
    payload = dict(row or {})
    target_id = str(payload.get("target_id", "")).strip()
    if not target_id:
        raise InspectionError(REFUSAL_INSPECT_TARGET_INVALID, "inspection target_id is required", {})
    desired_fidelity = str(payload.get("desired_fidelity", "macro")).strip() or "macro"
    if desired_fidelity not in _VALID_FIDELITY:
        desired_fidelity = "macro"
    target_kind = str(payload.get("target_kind", "")).strip() or _target_kind_from_target_id(target_id)
    if target_kind not in _VALID_TARGET_KINDS:
        target_kind = _target_kind_from_target_id(target_id)
    time_range = payload.get("time_range")
    normalized_time_range = None
    if isinstance(time_range, dict):
        start_tick = max(0, _as_int(time_range.get("start_tick", 0), 0))
        end_tick = max(start_tick, _as_int(time_range.get("end_tick", start_tick), start_tick))
        normalized_time_range = {"start_tick": int(start_tick), "end_tick": int(end_tick)}
    tick = max(0, _as_int(payload.get("tick", current_tick), current_tick))
    requester_subject_id = str(payload.get("requester_subject_id", "")).strip() or "subject.system"
    max_cost_units = max(0, _as_int(payload.get("max_cost_units", 0), 0))
    request_id = str(payload.get("request_id", "")).strip()
    if not request_id:
        request_id = "inspection.request.{}".format(
            canonical_sha256(
                {
                    "target_id": target_id,
                    "target_kind": target_kind,
                    "desired_fidelity": desired_fidelity,
                    "tick": int(tick),
                    "time_range": dict(normalized_time_range or {}),
                    "requester_subject_id": requester_subject_id,
                    "max_cost_units": int(max_cost_units),
                }
            )[:24]
        )
    return {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "requester_subject_id": requester_subject_id,
        "target_kind": target_kind,
        "target_id": target_id,
        "desired_fidelity": desired_fidelity,
        "tick": int(tick),
        "time_range": normalized_time_range,
        "max_cost_units": int(max_cost_units),
        "extensions": dict(payload.get("extensions") or {}),
    }


def inspection_section_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("sections")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("sections") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("section_id", ""))):
        section_id = str(row.get("section_id", "")).strip()
        if not section_id:
            continue
        ext = dict(row.get("extensions") or {})
        out[section_id] = {
            "schema_version": "1.0.0",
            "section_id": section_id,
            "title": str(row.get("title", "")).strip() or section_id,
            "extensions": {"cost_units": max(0, _as_int(ext.get("cost_units", 1), 1)), **ext},
        }
    for section_id, default in _DEFAULT_SECTION_ROWS.items():
        if section_id in out:
            continue
        out[section_id] = {
            "schema_version": "1.0.0",
            "section_id": section_id,
            "title": str(default.get("title", section_id)),
            "extensions": dict(default.get("extensions") or {}),
        }
    return out


def _section_cost(section_rows: Mapping[str, dict], section_ids: List[str]) -> int:
    return int(
        sum(
            max(0, _as_int((dict(section_rows.get(section_id) or {}).get("extensions") or {}).get("cost_units", 1), 1))
            for section_id in section_ids
        )
    )


def _section_ids_for_fidelity(*, fidelity: str, target_kind: str) -> List[str]:
    token = str(fidelity).strip() or "macro"
    if token not in _VALID_FIDELITY:
        token = "macro"
    if str(target_kind).strip() == "graph":
        return list(_SECTION_IDS_BY_FIDELITY_GRAPH[token])
    return list(_SECTION_IDS_BY_FIDELITY[token])


def _resolve_fidelity(
    *,
    desired_fidelity: str,
    target_kind: str,
    max_cost_units: int,
    section_rows: Mapping[str, dict],
    micro_allowed: bool,
    micro_available: bool,
    strict_budget: bool,
) -> Tuple[str, List[str], int, bool]:
    desired = str(desired_fidelity).strip() or "macro"
    if desired not in _VALID_FIDELITY:
        desired = "macro"
    candidates = [desired]
    if desired == "micro":
        candidates.extend(["meso", "macro"])
    elif desired == "meso":
        candidates.append("macro")
    if desired == "micro" and (not micro_allowed or not micro_available):
        candidates = ["meso", "macro"]
    seen = set()
    ordered = []
    for token in candidates:
        if token in seen:
            continue
        seen.add(token)
        ordered.append(token)

    budget = max(0, _as_int(max_cost_units, 0))
    fallback = "macro"
    fallback_sections = _section_ids_for_fidelity(fidelity="macro", target_kind=target_kind)
    fallback_cost = _section_cost(section_rows, fallback_sections)
    for token in ordered:
        section_ids = _section_ids_for_fidelity(fidelity=token, target_kind=target_kind)
        cost = _section_cost(section_rows, section_ids)
        if budget <= 0 or cost <= budget:
            return token, section_ids, int(cost), bool(token != desired)
        fallback = token
        fallback_sections = section_ids
        fallback_cost = cost
    if strict_budget:
        raise InspectionError(
            REFUSAL_INSPECT_BUDGET_EXCEEDED,
            "inspection budget cannot satisfy requested fidelity",
            {
                "desired_fidelity": desired,
                "required_cost_units": int(fallback_cost),
                "max_cost_units": int(budget),
            },
        )
    return fallback, fallback_sections, int(fallback_cost), True


def _target_structure_id(target_payload: Mapping[str, object], target_id: str) -> str:
    collection = str(target_payload.get("collection", "")).strip()
    row = dict(target_payload.get("row") or {})
    if collection == "installed_structure_instances":
        return str(row.get("instance_id", "")).strip()
    if collection == "materialization_states":
        return str(row.get("structure_id", "")).strip()
    if collection == "distribution_aggregates":
        return str(row.get("structure_id", "")).strip()
    if collection == "micro_part_instances":
        return str(row.get("parent_structure_id", "")).strip()
    if str(target_id).startswith("assembly.structure_instance."):
        return str(target_id).strip()
    return ""


def _events_for_target(state: Mapping[str, object], target_id: str, time_range: Mapping[str, object] | None) -> List[dict]:
    token = str(target_id).strip()
    rows = []
    for key in (
        "logistics_provenance_events",
        "construction_provenance_events",
        "maintenance_provenance_events",
        "machine_provenance_events",
    ):
        for row in list((dict(state or {})).get(key) or []):
            if not isinstance(row, dict):
                continue
            ext = dict(row.get("extensions") or {})
            candidates = {
                str(row.get("event_id", "")).strip(),
                str(row.get("commitment_id", "")).strip(),
                str(row.get("manifest_id", "")).strip(),
                str(row.get("linked_project_id", "")).strip(),
                str(row.get("linked_step_id", "")).strip(),
                str(row.get("asset_id", "")).strip(),
                str(ext.get("asset_id", "")).strip(),
                str(ext.get("project_id", "")).strip(),
                str(ext.get("manifest_id", "")).strip(),
                str(ext.get("machine_id", "")).strip(),
                str(ext.get("port_id", "")).strip(),
                str(ext.get("operation_id", "")).strip(),
                str(ext.get("connection_id", "")).strip(),
            }
            if token not in candidates:
                continue
            rows.append(dict(row))
    if isinstance(time_range, dict):
        start_tick = max(0, _as_int(time_range.get("start_tick", 0), 0))
        end_tick = max(start_tick, _as_int(time_range.get("end_tick", start_tick), start_tick))
        rows = [row for row in rows if start_tick <= _as_int(row.get("tick", 0), 0) <= end_tick]
    return sorted(rows, key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", ""))))


def _build_section_data(section_id: str, *, state: Mapping[str, object], target_payload: Mapping[str, object], request: Mapping[str, object], quant_step: int, include_part_ids: bool) -> dict:
    row = dict(target_payload.get("row") or {})
    payload_extensions = dict(target_payload.get("extensions") or {})

    def _graph_row() -> dict:
        graph_id = str(row.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip()
        if isinstance(row.get("nodes"), list) and isinstance(row.get("edges"), list):
            return dict(row)
        for candidate in list((dict(state or {})).get("network_graphs") or []):
            if not isinstance(candidate, dict):
                continue
            if str(candidate.get("graph_id", "")).strip() == graph_id:
                return dict(candidate)
        return dict(row)

    if section_id == "section.material_stocks":
        port_contents = list(row.get("current_contents") or [])
        if port_contents:
            stocks: Dict[str, int] = {}
            for item in sorted((entry for entry in port_contents if isinstance(entry, dict)), key=lambda entry: (str(entry.get("material_id", "")), str(entry.get("batch_id", "")))):
                material_id = str(item.get("material_id", "")).strip()
                if not material_id:
                    continue
                stocks[material_id] = _as_int(stocks.get(material_id, 0), 0) + max(0, _as_int(item.get("mass", 0), 0))
            return {"stocks": _quantize_map(stocks, step=quant_step), "material_count": len(stocks.keys())}
        stocks = dict(row.get("material_stocks") or {})
        if not stocks:
            stocks = {}
            for inv in list((dict(state or {})).get("logistics_node_inventories") or []):
                if not isinstance(inv, dict):
                    continue
                for material_id, mass in sorted((dict(inv.get("material_stocks") or {})).items(), key=lambda item: str(item[0])):
                    token = str(material_id).strip()
                    if not token:
                        continue
                    stocks[token] = _as_int(stocks.get(token, 0), 0) + max(0, _as_int(mass, 0))
        return {"stocks": _quantize_map(stocks, step=quant_step), "material_count": len(stocks.keys())}
    if section_id == "section.batches_summary":
        batches = [dict(item) for item in list((dict(state or {})).get("material_batches") or []) if isinstance(item, dict)]
        return {"batch_count": len(batches), "sample_batch_ids": [str(item.get("batch_id", "")).strip() for item in batches[:16] if str(item.get("batch_id", "")).strip()]}
    if section_id == "section.flow_summary":
        if "machine_ports" in dict(state or {}):
            ports = [dict(item) for item in list((dict(state or {})).get("machine_ports") or []) if isinstance(item, dict)]
            connections = [
                dict(item)
                for item in list((dict(state or {})).get("machine_port_connections") or [])
                if isinstance(item, dict) and bool(item.get("active", False))
            ]
            if str(request.get("target_kind", "")) in {"machine", "port"}:
                return {
                    "machine_port_count": len(ports),
                    "active_port_connection_count": len(connections),
                }
        manifests = [dict(item) for item in list((dict(state or {})).get("logistics_manifests") or []) if isinstance(item, dict)]
        status_counts: Dict[str, int] = {}
        channel_rows = []
        scale = 1 << 24
        runtime_state = dict((dict(state or {})).get("logistics_runtime_state") or {})
        runtime_ext = dict(runtime_state.get("extensions") or {})
        latest_flow_results = {
            str(item.get("channel_id", "")).strip(): dict(item)
            for item in list(runtime_ext.get("last_flow_channel_results") or [])
            if isinstance(item, dict) and str(item.get("channel_id", "")).strip()
        }
        for item in manifests:
            status = str(item.get("status", "planned")).strip() or "planned"
            status_counts[status] = _as_int(status_counts.get(status, 0), 0) + 1
            ext = dict(item.get("extensions") or {})
            flow_channel = dict(ext.get("flow_channel") or {})
            channel_id = str(flow_channel.get("channel_id", "")).strip() or str(ext.get("flow_channel_id", "")).strip()
            if not channel_id:
                continue
            capacity_per_tick = flow_channel.get("capacity_per_tick")
            if capacity_per_tick is None:
                capacity_int = 0
            else:
                capacity_int = max(0, _as_int(capacity_per_tick, 0))
            loss_fraction = max(0, _as_int(flow_channel.get("loss_fraction", ext.get("loss_fraction", 0)), 0))
            quantity_mass = max(0, _as_int(item.get("quantity_mass", 0), 0))
            latest = dict(latest_flow_results.get(channel_id) or {})
            throughput = max(0, _as_int(latest.get("transferred_amount", 0), 0))
            if throughput <= 0 and status in {"delivered", "lost"}:
                est_loss = _as_int((quantity_mass * loss_fraction) // max(1, int(scale)), 0)
                throughput = max(0, quantity_mass - max(0, est_loss))
            utilization_permille = 0
            if capacity_int > 0:
                utilization_permille = int((1000 * throughput) // capacity_int)
            channel_rows.append(
                {
                    "channel_id": channel_id,
                    "manifest_id": str(item.get("manifest_id", "")).strip(),
                    "capacity_per_tick": int(capacity_int),
                    "throughput": int(throughput),
                    "loss_fraction": int(loss_fraction),
                    "utilization_permille": int(max(0, utilization_permille)),
                    "status": status,
                    "route_edge_count": len(_sorted_unique_strings(list(ext.get("route_edge_ids") or []))),
                }
            )
        return {
            "manifest_count": len(manifests),
            "status_counts": dict((k, status_counts[k]) for k in sorted(status_counts.keys())),
            "channel_count": len(channel_rows),
            "channels": sorted(channel_rows, key=lambda row: str(row.get("channel_id", "")))[:128],
        }
    if section_id == "section.flow_utilization":
        manifests = [dict(item) for item in list((dict(state or {})).get("logistics_manifests") or []) if isinstance(item, dict)]
        runtime_state = dict((dict(state or {})).get("logistics_runtime_state") or {})
        runtime_ext = dict(runtime_state.get("extensions") or {})
        latest_flow_results = {
            str(item.get("channel_id", "")).strip(): dict(item)
            for item in list(runtime_ext.get("last_flow_channel_results") or [])
            if isinstance(item, dict) and str(item.get("channel_id", "")).strip()
        }
        by_edge: Dict[str, dict] = {}
        for manifest in sorted(manifests, key=lambda row: str(row.get("manifest_id", ""))):
            ext = dict(manifest.get("extensions") or {})
            flow_channel = dict(ext.get("flow_channel") or {})
            channel_id = str(flow_channel.get("channel_id", "")).strip() or str(ext.get("flow_channel_id", "")).strip()
            route_edge_ids = _sorted_unique_strings(list(ext.get("route_edge_ids") or []))
            if not channel_id or not route_edge_ids:
                continue
            capacity = flow_channel.get("capacity_per_tick")
            capacity_int = max(0, _as_int(capacity, 0)) if capacity is not None else 0
            latest = dict(latest_flow_results.get(channel_id) or {})
            throughput = max(0, _as_int(latest.get("transferred_amount", 0), 0))
            for edge_id in route_edge_ids:
                bucket = dict(by_edge.get(edge_id) or {"capacity": 0, "throughput": 0, "channel_count": 0})
                bucket["capacity"] = _as_int(bucket.get("capacity", 0), 0) + int(capacity_int)
                bucket["throughput"] = _as_int(bucket.get("throughput", 0), 0) + int(throughput)
                bucket["channel_count"] = _as_int(bucket.get("channel_count", 0), 0) + 1
                by_edge[edge_id] = bucket
        edge_rows = []
        capacity_total = 0
        throughput_total = 0
        for edge_id in sorted(by_edge.keys()):
            row = dict(by_edge.get(edge_id) or {})
            capacity = max(0, _as_int(row.get("capacity", 0), 0))
            throughput = max(0, _as_int(row.get("throughput", 0), 0))
            capacity_total += capacity
            throughput_total += throughput
            util = int((1000 * throughput) // capacity) if capacity > 0 else 0
            edge_rows.append(
                {
                    "edge_id": edge_id,
                    "capacity": int(capacity),
                    "throughput": int(throughput),
                    "utilization_permille": int(max(0, util)),
                    "channel_count": int(max(0, _as_int(row.get("channel_count", 0), 0))),
                }
            )
        total_util = int((1000 * throughput_total) // capacity_total) if capacity_total > 0 else 0
        return {
            "edge_count": len(edge_rows),
            "capacity_total": int(capacity_total),
            "throughput_total": int(throughput_total),
            "utilization_permille": int(max(0, total_util)),
            "edges": edge_rows[:256],
        }
    if section_id == "section.networkgraph.summary":
        graph = _graph_row()
        node_rows = [dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, dict)]
        edge_rows = [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, dict)]
        validation_mode = str(graph.get("validation_mode", "")).strip() or "strict"
        return {
            "graph_id": str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip(),
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "validation_mode": validation_mode,
            "routing_policy_id": str(graph.get("deterministic_routing_policy_id", "")).strip(),
            "graph_partition_id": str(graph.get("graph_partition_id", "")).strip() or None,
        }
    if section_id == "section.networkgraph.route":
        route_payload = {}
        for candidate in (
            dict(payload_extensions.get("route_result") or {}),
            dict((dict(row.get("extensions") or {})).get("route_result") or {}),
            dict((dict(request.get("extensions") or {})).get("route_result") or {}),
        ):
            if candidate:
                route_payload = candidate
                break
        path_edge_ids = [str(item).strip() for item in list(route_payload.get("path_edge_ids") or []) if str(item).strip()]
        path_node_ids = [str(item).strip() for item in list(route_payload.get("path_node_ids") or []) if str(item).strip()]
        return {
            "available": bool(route_payload),
            "path_node_ids": list(path_node_ids),
            "path_edge_ids": list(path_edge_ids),
            "total_cost": int(max(0, _as_int(route_payload.get("total_cost", 0), 0))),
            "route_policy_id": str(route_payload.get("route_policy_id", "")).strip(),
        }
    if section_id == "section.networkgraph.capacity_utilization":
        graph = _graph_row()
        edge_rows = [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, dict)]
        used_by_edge = dict(payload_extensions.get("capacity_used_by_edge") or {})
        capacity_total = 0
        used_total = 0
        edges_with_capacity = 0
        for edge in edge_rows:
            edge_id = str(edge.get("edge_id", "")).strip()
            capacity = edge.get("capacity")
            if capacity is None:
                continue
            cap_val = max(0, _as_int(capacity, 0))
            capacity_total += cap_val
            edges_with_capacity += 1
            used_total += max(0, _as_int(used_by_edge.get(edge_id, 0), 0))
        utilization_permille = int((1000 * used_total) // capacity_total) if capacity_total > 0 else 0
        return {
            "edge_with_capacity_count": int(edges_with_capacity),
            "capacity_total": int(_quantize_map({"value": capacity_total}, step=quant_step).get("value", 0)),
            "capacity_used_total": int(_quantize_map({"value": used_total}, step=quant_step).get("value", 0)),
            "utilization_permille": int(utilization_permille),
        }
    if section_id == "section.ag_progress":
        projects = [dict(item) for item in list((dict(state or {})).get("construction_projects") or []) if isinstance(item, dict)]
        steps = [dict(item) for item in list((dict(state or {})).get("construction_steps") or []) if isinstance(item, dict)]
        completed = len([item for item in steps if str(item.get("status", "")).strip() == "completed"])
        total = max(1, len(steps))
        return {"project_count": len(projects), "step_total": len(steps), "step_completed": completed, "progress_permille": int((1000 * completed) // total)}
    if section_id == "section.maintenance_backlog":
        assets = [dict(item) for item in list((dict(state or {})).get("asset_health_states") or []) if isinstance(item, dict)]
        total = sum(max(0, _as_int(item.get("maintenance_backlog", 0), 0)) for item in assets)
        return {"asset_count": len(assets), "backlog_total": int(_quantize_map({"value": total}, step=quant_step).get("value", 0))}
    if section_id == "section.failure_risk_summary":
        payload_ext = dict(target_payload.get("extensions") or {})
        explicit = dict(payload_ext.get("failure_risk_summary") or {})
        if explicit:
            return {"risk_rows": [dict(item) for item in list(explicit.get("risk_rows") or [])[:16] if isinstance(item, dict)]}
        return {"risk_rows": []}
    if section_id == "section.commitments_summary":
        rows = []
        for key in ("material_commitments", "construction_commitments", "shipment_commitments", "maintenance_commitments"):
            rows.extend([dict(item) for item in list((dict(state or {})).get(key) or []) if isinstance(item, dict)])
        status_counts: Dict[str, int] = {}
        for item in rows:
            status = str(item.get("status", "planned")).strip() or "planned"
            status_counts[status] = _as_int(status_counts.get(status, 0), 0) + 1
        return {"commitment_count": len(rows), "status_counts": dict((k, status_counts[k]) for k in sorted(status_counts.keys()))}
    if section_id == "section.events_summary":
        rows = _events_for_target(state, str(request.get("target_id", "")), request.get("time_range") if isinstance(request.get("time_range"), dict) else None)
        return {"event_count": len(rows), "sample_event_ids": [str(item.get("event_id", "")).strip() for item in rows[:24] if str(item.get("event_id", "")).strip()]}
    if section_id == "section.reenactment_link":
        requests = [dict(item) for item in list((dict(state or {})).get("reenactment_requests") or []) if isinstance(item, dict)]
        request_ids = {str(item.get("request_id", "")).strip() for item in requests if str(item.get("target_id", "")).strip() == str(request.get("target_id", "")).strip()}
        artifacts = [dict(item) for item in list((dict(state or {})).get("reenactment_artifacts") or []) if isinstance(item, dict) and str(item.get("request_id", "")).strip() in request_ids]
        latest = sorted(artifacts, key=lambda item: str(item.get("reenactment_id", "")))[-1] if artifacts else {}
        return {"available": bool(latest), "artifact_count": len(artifacts), "latest_reenactment_id": str(latest.get("reenactment_id", "")).strip()}
    if section_id == "section.micro_parts_summary":
        structure_id = _target_structure_id(target_payload, str(request.get("target_id", "")))
        micro_rows = [dict(item) for item in list((dict(state or {})).get("micro_part_instances") or []) if isinstance(item, dict)]
        if structure_id:
            micro_rows = [item for item in micro_rows if str(item.get("parent_structure_id", "")).strip() == structure_id]
        return {
            "structure_id": structure_id,
            "part_count": len(micro_rows),
            "part_ids": [str(item.get("micro_part_id", "")).strip() for item in micro_rows[:128] if include_part_ids and str(item.get("micro_part_id", "")).strip()],
        }
    return {}


def build_inspection_snapshot_artifact(
    *,
    request_row: Mapping[str, object],
    target_payload: Mapping[str, object],
    state: Mapping[str, object],
    truth_hash_anchor: str,
    ledger_hash: str,
    section_registry_payload: Mapping[str, object] | None,
    policy_context: Mapping[str, object] | None,
    law_profile: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    physics_profile_id: str,
    pack_lock_hash: str,
    cache_policy_id: str,
    strict_budget: bool,
) -> Tuple[dict, dict]:
    request = normalize_inspection_request_row(request_row, current_tick=_as_int(request_row.get("tick", 0), 0))
    payload = dict(target_payload or {})
    if not bool(payload.get("exists", False)):
        raise InspectionError(REFUSAL_INSPECT_TARGET_INVALID, "inspection target is unavailable", {"target_id": str(request.get("target_id", ""))})

    visibility_level = str((dict((dict(authority_context or {})).get("epistemic_scope") or {})).get("visibility_level", "")).strip() or "diegetic"
    entitlements = set(_sorted_unique_strings(list((dict(authority_context or {})).get("entitlements") or [])))
    allow_hidden_state = bool((dict(law_profile or {})).get("epistemic_limits", {}).get("allow_hidden_state_access", False))
    micro_allowed = visibility_level != "diegetic" and allow_hidden_state and "entitlement.inspect" in entitlements
    if str(request.get("desired_fidelity", "")) == "micro" and not micro_allowed and bool(strict_budget):
        raise InspectionError(REFUSAL_INSPECT_FORBIDDEN_BY_LAW, "micro inspection forbidden by law/epistemic scope", {})
    structure_id = _target_structure_id(payload, str(request.get("target_id", "")))
    micro_rows = [dict(item) for item in list((dict(state or {})).get("micro_part_instances") or []) if isinstance(item, dict)]
    micro_available = bool(micro_rows if not structure_id else [item for item in micro_rows if str(item.get("parent_structure_id", "")).strip() == structure_id])

    section_rows = inspection_section_rows_by_id(section_registry_payload)
    achieved_fidelity, section_ids, section_cost_units, degraded = _resolve_fidelity(
        desired_fidelity=str(request.get("desired_fidelity", "macro")),
        target_kind=str(request.get("target_kind", "")),
        max_cost_units=_as_int(request.get("max_cost_units", 0), 0),
        section_rows=section_rows,
        micro_allowed=micro_allowed,
        micro_available=micro_available,
        strict_budget=bool(strict_budget),
    )

    quant_step = 100 if visibility_level == "diegetic" else (1 if allow_hidden_state else 10)
    include_part_ids = bool(micro_allowed and achieved_fidelity == "micro")
    redaction_level = "none" if include_part_ids else ("diegetic" if visibility_level == "diegetic" else "coarse")

    summary_sections: Dict[str, dict] = {}
    for section_id in section_ids:
        section_row = dict(section_rows.get(section_id) or {})
        summary_sections[section_id] = {
            "schema_version": "1.0.0",
            "section_id": section_id,
            "title": str(section_row.get("title", section_id)),
            "data": _build_section_data(
                section_id,
                state=state,
                target_payload=payload,
                request=request,
                quant_step=int(quant_step),
                include_part_ids=include_part_ids,
            ),
            "epistemic_redaction_level": redaction_level,
            "extensions": {
                "cost_units": max(0, _as_int((dict(section_row.get("extensions") or {})).get("cost_units", 1), 1)),
                "quantization_step": int(quant_step),
            },
        }

    epistemic_policy_id = str((dict(policy_context or {})).get("epistemic_policy_id", "")).strip() or str((dict(law_profile or {})).get("epistemic_policy_id", "")).strip() or "ep.policy.unknown"
    section_policy_id = str((dict(policy_context or {})).get("inspection_section_policy_id", "")).strip() or "section.policy.default"
    normalized_truth_hash = str(truth_hash_anchor).strip() or canonical_sha256({"truth": truth_hash_anchor})
    normalized_ledger_hash = str(ledger_hash).strip() or canonical_sha256({"ledger": ledger_hash, "target_id": request.get("target_id", "")})
    inputs_hash = canonical_sha256(
        {
            "request": dict(request),
            "truth_hash_anchor": normalized_truth_hash,
            "ledger_hash": normalized_ledger_hash,
            "target_payload_hash": canonical_sha256(payload),
            "section_ids": list(sorted(summary_sections.keys())),
            "achieved_fidelity": achieved_fidelity,
            "epistemic_policy_id": epistemic_policy_id,
            "section_policy_id": section_policy_id,
        }
    )
    snapshot_hash = canonical_sha256(
        {
            "request_id": str(request.get("request_id", "")),
            "target_id": str(request.get("target_id", "")),
            "achieved_fidelity": achieved_fidelity,
            "tick": int(_as_int(request.get("tick", 0), 0)),
            "inputs_hash": inputs_hash,
            "summary_sections": dict(summary_sections),
        }
    )
    snapshot_id = "inspect.snapshot.{}".format(snapshot_hash[:16])
    snapshot = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id,
        "request_id": str(request.get("request_id", "")),
        "target_id": str(request.get("target_id", "")),
        "achieved_fidelity": achieved_fidelity,
        "tick": int(_as_int(request.get("tick", 0), 0)),
        "physics_profile_id": str(physics_profile_id or ""),
        "pack_lock_hash": str(pack_lock_hash or ""),
        "cache_policy_id": str(cache_policy_id or ""),
        "truth_hash_anchor": normalized_truth_hash,
        "snapshot_hash": snapshot_hash,
        "ledger_hash": normalized_ledger_hash,
        "inputs_hash": inputs_hash,
        "summary_sections": dict(summary_sections),
        "detail_refs": ["inspection.section.{}".format(section_id) for section_id in sorted(summary_sections.keys())],
        "target_payload": payload,
        "deterministic_fingerprint": "",
        "extensions": {
            "derived_only": True,
            "requested_fidelity": str(request.get("desired_fidelity", "macro")),
            "degraded": bool(degraded or achieved_fidelity != str(request.get("desired_fidelity", "macro"))),
            "section_cost_units": int(section_cost_units),
            "max_cost_units": int(_as_int(request.get("max_cost_units", 0), 0)),
            "micro_detail_allowed": bool(micro_allowed),
            "micro_available": bool(micro_available),
            "epistemic_policy_id": epistemic_policy_id,
            "section_policy_id": section_policy_id,
            "visibility_level": visibility_level,
        },
    }
    snapshot["deterministic_fingerprint"] = canonical_sha256(dict(snapshot, deterministic_fingerprint=""))
    diagnostics = {
        "request_row": dict(request),
        "desired_fidelity": str(request.get("desired_fidelity", "macro")),
        "achieved_fidelity": achieved_fidelity,
        "degraded": bool(snapshot["extensions"].get("degraded", False)),
        "section_ids": list(sorted(summary_sections.keys())),
        "section_cost_units": int(section_cost_units),
        "micro_detail_allowed": bool(micro_allowed),
        "micro_available": bool(micro_available),
        "epistemic_policy_id": epistemic_policy_id,
        "section_policy_id": section_policy_id,
    }
    return snapshot, diagnostics
