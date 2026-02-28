"""Deterministic MAT-9 inspection snapshot engine (derived-only)."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from src.control.fidelity import (
    DEFAULT_FIDELITY_POLICY_ID,
    NO_DOWNGRADE,
    REFUSAL_CTRL_FIDELITY_DENIED,
    arbitrate_fidelity_requests,
    build_fidelity_request,
)
from src.interior import InteriorError, path_exists
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_INSPECT_FORBIDDEN_BY_LAW = "refusal.inspect.forbidden_by_law"
REFUSAL_INSPECT_BUDGET_EXCEEDED = "refusal.inspect.budget_exceeded"
REFUSAL_INSPECT_TARGET_INVALID = "refusal.inspect.target_invalid"

_VALID_TARGET_KINDS = {
    "structure",
    "project",
    "plan",
    "node",
    "manifest",
    "cohort",
    "faction",
    "machine",
    "port",
    "graph",
    "interior",
    "interior_graph",
    "interior_volume",
    "interior_portal",
    "pose_slot",
    "mount_point",
}
_VALID_FIDELITY = ("macro", "meso", "micro")
_SECTION_IDS_BY_FIDELITY = {
    "macro": [
        "section.capabilities_summary",
        "section.material_stocks",
        "section.flow_summary",
        "section.flow_utilization",
        "section.interior.connectivity_summary",
        "section.interior.portal_state_table",
        "section.interior.pressure_summary",
        "section.interior.flood_summary",
        "section.interior.smoke_summary",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.flow_utilization",
        "section.interior.connectivity_summary",
        "section.interior.portal_state_table",
        "section.interior.pressure_summary",
        "section.interior.flood_summary",
        "section.interior.smoke_summary",
        "section.interior.flow_summary",
        "section.interior.layout",
        "section.interior.portal_states",
        "section.interior.pressure_map",
        "section.interior.flood_map",
        "section.interior.portal_leaks",
        "section.ag_progress",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.flow_utilization",
        "section.interior.connectivity_summary",
        "section.interior.portal_state_table",
        "section.interior.pressure_summary",
        "section.interior.flood_summary",
        "section.interior.smoke_summary",
        "section.interior.flow_summary",
        "section.interior.layout",
        "section.interior.portal_states",
        "section.interior.pressure_map",
        "section.interior.flood_map",
        "section.interior.portal_leaks",
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
        "section.capabilities_summary",
        "section.networkgraph.summary",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.networkgraph.summary",
        "section.networkgraph.route",
        "section.networkgraph.capacity_utilization",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.networkgraph.summary",
        "section.networkgraph.route",
        "section.networkgraph.capacity_utilization",
    ],
}
_SECTION_IDS_BY_FIDELITY_POSE = {
    "macro": [
        "section.capabilities_summary",
        "section.pose_slots_summary",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.pose_slots_summary",
        "section.events_summary",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.pose_slots_summary",
        "section.events_summary",
    ],
}
_SECTION_IDS_BY_FIDELITY_MOUNT = {
    "macro": [
        "section.capabilities_summary",
        "section.mount_points_summary",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.mount_points_summary",
        "section.events_summary",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.mount_points_summary",
        "section.events_summary",
    ],
}
_SECTION_IDS_BY_FIDELITY_PLAN = {
    "macro": [
        "section.capabilities_summary",
        "section.plan_summary",
        "section.plan_resource_requirements",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.plan_summary",
        "section.plan_resource_requirements",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.plan_summary",
        "section.plan_resource_requirements",
    ],
}
_DEFAULT_SECTION_ROWS = {
    "section.capabilities_summary": {"title": "Capabilities Summary", "extensions": {"cost_units": 1}},
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
    "section.pose_slots_summary": {"title": "Pose Slots Summary", "extensions": {"cost_units": 1}},
    "section.mount_points_summary": {"title": "Mount Points Summary", "extensions": {"cost_units": 1}},
    "section.plan_summary": {"title": "Plan Summary", "extensions": {"cost_units": 1}},
    "section.plan_resource_requirements": {"title": "Plan Resource Requirements", "extensions": {"cost_units": 2}},
    "section.interior.connectivity_summary": {"title": "Interior Connectivity Summary", "extensions": {"cost_units": 1}},
    "section.interior.portal_state_table": {"title": "Interior Portal State Table", "extensions": {"cost_units": 2}},
    "section.interior.pressure_summary": {"title": "Interior Pressure Summary", "extensions": {"cost_units": 2}},
    "section.interior.flood_summary": {"title": "Interior Flood Summary", "extensions": {"cost_units": 2}},
    "section.interior.smoke_summary": {"title": "Interior Smoke Summary", "extensions": {"cost_units": 2}},
    "section.interior.flow_summary": {"title": "Interior Flow Summary", "extensions": {"cost_units": 3}},
    "section.interior.layout": {"title": "Interior Layout", "extensions": {"cost_units": 2}},
    "section.interior.portal_states": {"title": "Interior Portal States", "extensions": {"cost_units": 2}},
    "section.interior.pressure_map": {"title": "Interior Pressure Map", "extensions": {"cost_units": 2}},
    "section.interior.flood_map": {"title": "Interior Flood Map", "extensions": {"cost_units": 2}},
    "section.interior.portal_leaks": {"title": "Interior Portal Leaks", "extensions": {"cost_units": 2}},
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
    if token.startswith("plan."):
        return "plan"
    if token.startswith("pose.slot."):
        return "pose_slot"
    if token.startswith("mount.point."):
        return "mount_point"
    if token.startswith("interior.graph."):
        return "interior_graph"
    if token.startswith("graph."):
        return "graph"
    if token.startswith("interior.volume."):
        return "interior_volume"
    if token.startswith("interior.portal."):
        return "interior_portal"
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
    kind = str(target_kind).strip()
    if kind == "plan":
        return list(_SECTION_IDS_BY_FIDELITY_PLAN[token])
    if kind == "graph":
        return list(_SECTION_IDS_BY_FIDELITY_GRAPH[token])
    if kind == "pose_slot":
        return list(_SECTION_IDS_BY_FIDELITY_POSE[token])
    if kind == "mount_point":
        return list(_SECTION_IDS_BY_FIDELITY_MOUNT[token])
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
    requester_subject_id: str = "subject.inspect",
    tick: int = 0,
    server_profile_id: str = "server.profile.inspect",
    fidelity_policy_id: str = DEFAULT_FIDELITY_POLICY_ID,
) -> Tuple[str, List[str], int, bool, dict, dict, dict]:
    desired = str(desired_fidelity).strip() or "macro"
    if desired not in _VALID_FIDELITY:
        desired = "macro"
    budget = max(0, _as_int(max_cost_units, 0))
    fidelity_cost_by_level = {}
    for token in _VALID_FIDELITY:
        section_ids = _section_ids_for_fidelity(fidelity=token, target_kind=target_kind)
        fidelity_cost_by_level[token] = int(_section_cost(section_rows, section_ids))

    desired_cost = int(max(0, _as_int(fidelity_cost_by_level.get(desired, fidelity_cost_by_level.get("macro", 0)), 0)))
    fidelity_request = build_fidelity_request(
        requester_subject_id=str(requester_subject_id).strip() or "subject.inspect",
        target_kind=str(target_kind).strip() or "structure",
        target_id="inspect.target.{}".format(canonical_sha256({"target_kind": str(target_kind), "tick": int(max(0, _as_int(tick, 0)))} )[:16]),
        requested_level=str(desired),
        cost_estimate=int(desired_cost),
        priority=0,
        created_tick=int(max(0, _as_int(tick, 0))),
        extensions={
            "micro_allowed": bool(micro_allowed),
            "micro_available": bool(micro_available),
            "allowed_levels": ["micro", "meso", "macro"],
            "fidelity_cost_by_level": dict(fidelity_cost_by_level),
            "strict_budget": bool(strict_budget),
        },
    )
    arbitration = arbitrate_fidelity_requests(
        fidelity_requests=[dict(fidelity_request)],
        rs5_budget_state={
            "tick": int(max(0, _as_int(tick, 0))),
            "envelope_id": "budget.inspect",
            "fidelity_policy_id": str(fidelity_policy_id).strip() or DEFAULT_FIDELITY_POLICY_ID,
            "max_cost_units_per_tick": int(max(0, budget)),
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": [str(fidelity_request.get("requester_subject_id", ""))],
        },
        server_profile={"server_profile_id": str(server_profile_id).strip() or "server.profile.inspect"},
        fidelity_policy={"policy_id": str(fidelity_policy_id).strip() or DEFAULT_FIDELITY_POLICY_ID},
    )
    allocation_rows = [
        dict(row) for row in list(arbitration.get("fidelity_allocations") or []) if isinstance(row, dict)
    ]
    allocation = dict(allocation_rows[0] if allocation_rows else {})
    allocation_ext = dict(allocation.get("extensions") or {})
    refusal_codes = _sorted_unique_strings(list(allocation_ext.get("refusal_codes") or []))
    if strict_budget and REFUSAL_CTRL_FIDELITY_DENIED in set(refusal_codes):
        raise InspectionError(
            REFUSAL_INSPECT_BUDGET_EXCEEDED,
            "inspection budget cannot satisfy requested fidelity",
            {
                "desired_fidelity": desired,
                "required_cost_units": int(desired_cost),
                "max_cost_units": int(budget),
            },
        )

    achieved = str(allocation.get("resolved_level", "")).strip()
    if achieved not in _VALID_FIDELITY:
        achieved = "macro"
    section_ids = _section_ids_for_fidelity(fidelity=achieved, target_kind=target_kind)
    section_cost = int(_section_cost(section_rows, section_ids))
    degraded = bool(achieved != desired or str(allocation.get("downgrade_reason", NO_DOWNGRADE)).strip() not in ("", NO_DOWNGRADE))
    return (
        achieved,
        section_ids,
        section_cost,
        degraded,
        dict(fidelity_request),
        dict(allocation),
        dict(arbitration),
    )


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


def _row_index(rows: object, key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get(key, ""))):
        token = str(row.get(key, "")).strip()
        if not token:
            continue
        out[token] = dict(row)
    return out


def _agent_row_by_id(state: Mapping[str, object], subject_id: str) -> dict:
    token = str(subject_id).strip()
    if not token:
        return {}
    rows = [dict(item) for item in list((dict(state or {})).get("agent_states") or []) if isinstance(item, dict)]
    for row in sorted(rows, key=lambda item: str(item.get("agent_id", ""))):
        if token in (
            str(row.get("agent_id", "")).strip(),
            str(row.get("entity_id", "")).strip(),
        ):
            return row
    return {}


def _requester_volume_id(state: Mapping[str, object], requester_subject_id: str) -> str:
    agent = _agent_row_by_id(state, requester_subject_id)
    ext = dict(agent.get("extensions") or {}) if isinstance(agent.get("extensions"), dict) else {}
    return (
        str(agent.get("interior_volume_id", "")).strip()
        or str(agent.get("current_volume_id", "")).strip()
        or str(agent.get("volume_id", "")).strip()
        or str(ext.get("interior_volume_id", "")).strip()
        or str(ext.get("volume_id", "")).strip()
    )


def _pose_slot_graph_for_slot(state: Mapping[str, object], slot: Mapping[str, object]) -> dict:
    slot_row = dict(slot or {})
    slot_ext = dict(slot_row.get("extensions") or {}) if isinstance(slot_row.get("extensions"), dict) else {}
    desired_graph_id = str(slot_ext.get("interior_graph_id", "")).strip()
    graph_rows = [
        dict(item)
        for item in list((dict(state or {})).get("interior_graphs") or [])
        if isinstance(item, dict)
    ]
    if desired_graph_id:
        for graph in sorted(graph_rows, key=lambda item: str(item.get("graph_id", ""))):
            if str(graph.get("graph_id", "")).strip() == desired_graph_id:
                return graph
    parent_assembly_id = str(slot_row.get("parent_assembly_id", "")).strip()
    if parent_assembly_id:
        bindings = [
            dict(item)
            for item in list((dict(state or {})).get("interior_structure_bindings") or [])
            if isinstance(item, dict)
        ]
        for binding in sorted(bindings, key=lambda item: (str(item.get("structure_id", "")), str(item.get("graph_id", "")))):
            if str(binding.get("structure_id", "")).strip() != parent_assembly_id:
                continue
            graph_id = str(binding.get("graph_id", "")).strip()
            if not graph_id:
                continue
            for graph in sorted(graph_rows, key=lambda item: str(item.get("graph_id", ""))):
                if str(graph.get("graph_id", "")).strip() == graph_id:
                    return graph
    slot_volume_id = str(slot_row.get("interior_volume_id", "")).strip()
    if slot_volume_id:
        for graph in sorted(graph_rows, key=lambda item: str(item.get("graph_id", ""))):
            if slot_volume_id in set(_sorted_unique_strings(graph.get("volumes"))):
                return graph
    return {}


def _pose_slot_reachable(
    state: Mapping[str, object],
    *,
    from_volume_id: str,
    slot: Mapping[str, object],
) -> bool:
    slot_row = dict(slot or {})
    if not bool(slot_row.get("requires_access_path", True)):
        return True
    source = str(from_volume_id).strip()
    target = str(slot_row.get("interior_volume_id", "")).strip()
    if (not source) or (not target):
        return False
    if source == target:
        return True
    graph_row = _pose_slot_graph_for_slot(state, slot_row)
    if not graph_row:
        return False
    try:
        return bool(
            path_exists(
                graph_row=graph_row,
                volume_rows=list((dict(state or {})).get("interior_volumes") or []),
                portal_rows=list((dict(state or {})).get("interior_portals") or []),
                from_volume_id=source,
                to_volume_id=target,
                portal_state_rows=list((dict(state or {})).get("interior_portal_state_machines") or []),
            )
        )
    except InteriorError:
        return False


def _visible_pose_slots(
    state: Mapping[str, object],
    *,
    requester_subject_id: str,
    allow_hidden_state: bool,
) -> List[dict]:
    rows = [
        dict(item)
        for item in list((dict(state or {})).get("pose_slots") or [])
        if isinstance(item, dict)
    ]
    rows = sorted(rows, key=lambda item: str(item.get("pose_slot_id", "")))
    if allow_hidden_state:
        return rows
    requester_id = str(requester_subject_id).strip()
    requester_volume_id = _requester_volume_id(state, requester_id)
    visible = []
    for row in rows:
        current_occupant_id = str(row.get("current_occupant_id", "")).strip()
        ext = dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {}
        occupant_ids = set(_sorted_unique_strings(ext.get("occupant_ids")))
        if requester_id and (requester_id == current_occupant_id or requester_id in occupant_ids):
            visible.append(row)
            continue
        if _pose_slot_reachable(state, from_volume_id=requester_volume_id, slot=row):
            visible.append(row)
            continue
    return visible


def _portal_state_id(portal_row: Mapping[str, object], portal_state_index: Mapping[str, dict]) -> str:
    portal = dict(portal_row or {})
    machine_id = str(portal.get("state_machine_id", "")).strip()
    if machine_id:
        machine = dict(portal_state_index.get(machine_id) or {})
        token = str(machine.get("state_id", "")).strip()
        if token:
            return token
    ext = dict(portal.get("extensions") or {})
    return str(ext.get("state_id", "")).strip() or "open"


def _graph_for_target(state: Mapping[str, object], target_payload: Mapping[str, object], request: Mapping[str, object]) -> dict:
    payload = dict(target_payload or {})
    collection = str(payload.get("collection", "")).strip()
    row = dict(payload.get("row") or {})
    target_id = str(request.get("target_id", "")).strip()
    graph_rows = _row_index((dict(state or {})).get("interior_graphs"), "graph_id")

    if collection == "interior_graphs":
        graph_id = str(row.get("graph_id", "")).strip()
        if graph_id:
            return dict(graph_rows.get(graph_id) or row)
    if target_id.startswith("interior.graph."):
        token = str(target_id[len("interior.graph."):]).strip()
        if token:
            return dict(graph_rows.get(token) or {})
    if target_id.startswith("graph."):
        return dict(graph_rows.get(target_id) or {})

    graph_id = (
        str(row.get("interior_graph_id", "")).strip()
        or str((dict(row.get("extensions") or {})).get("interior_graph_id", "")).strip()
    )
    if not graph_id and collection in {"installed_structure_instances", "machine_assemblies"}:
        structure_id = str(row.get("instance_id", "")).strip() or str(row.get("machine_id", "")).strip()
        for binding in sorted(
            (item for item in list((dict(state or {})).get("interior_structure_bindings") or []) if isinstance(item, dict)),
            key=lambda item: (str(item.get("structure_id", "")), str(item.get("graph_id", ""))),
        ):
            if str(binding.get("structure_id", "")).strip() != structure_id:
                continue
            graph_id = str(binding.get("graph_id", "")).strip()
            if graph_id:
                break
    if graph_id:
        return dict(graph_rows.get(graph_id) or {})

    if collection == "interior_volumes":
        volume_id = str(row.get("volume_id", "")).strip()
        for graph_row in sorted(graph_rows.values(), key=lambda item: str(item.get("graph_id", ""))):
            if volume_id and volume_id in set(_sorted_unique_strings(graph_row.get("volumes"))):
                return dict(graph_row)
    if collection == "interior_portals":
        portal_id = str(row.get("portal_id", "")).strip()
        for graph_row in sorted(graph_rows.values(), key=lambda item: str(item.get("graph_id", ""))):
            if portal_id and portal_id in set(_sorted_unique_strings(graph_row.get("portals"))):
                return dict(graph_row)
    return {}


def _compartment_rows_for_graph(state: Mapping[str, object], graph: Mapping[str, object]) -> List[dict]:
    graph_volume_ids = set(_sorted_unique_strings((dict(graph or {})).get("volumes")))
    rows = []
    for row in list((dict(state or {})).get("compartment_states") or []):
        if not isinstance(row, dict):
            continue
        volume_id = str(row.get("volume_id", "")).strip()
        if not volume_id or volume_id not in graph_volume_ids:
            continue
        rows.append(dict(row))
    return sorted(rows, key=lambda item: str(item.get("volume_id", "")))


def _leak_rows_for_graph(state: Mapping[str, object], graph: Mapping[str, object]) -> List[dict]:
    graph_volume_ids = set(_sorted_unique_strings((dict(graph or {})).get("volumes")))
    rows = []
    for row in list((dict(state or {})).get("interior_leak_hazards") or []):
        if not isinstance(row, dict):
            continue
        volume_id = str(row.get("volume_id", "")).strip()
        if not volume_id or volume_id not in graph_volume_ids:
            continue
        rows.append(dict(row))
    return sorted(rows, key=lambda item: str(item.get("leak_id", "")))


def _build_section_data(
    section_id: str,
    *,
    state: Mapping[str, object],
    target_payload: Mapping[str, object],
    request: Mapping[str, object],
    quant_step: int,
    include_part_ids: bool,
    allow_hidden_state: bool,
) -> dict:
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
    if section_id in {"section.interior.layout", "section.interior.connectivity_summary"}:
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False}
        volume_rows_by_id = _row_index((dict(state or {})).get("interior_volumes"), "volume_id")
        volume_ids = _sorted_unique_strings(graph.get("volumes"))
        portal_ids = _sorted_unique_strings(graph.get("portals"))
        portal_rows_by_id = _row_index((dict(state or {})).get("interior_portals"), "portal_id")
        state_machine_rows_by_id = _row_index((dict(state or {})).get("interior_portal_state_machines"), "machine_id")
        volume_type_counts: Dict[str, int] = {}
        for volume_id in volume_ids:
            volume = dict(volume_rows_by_id.get(volume_id) or {})
            volume_type_id = str(volume.get("volume_type_id", "volume.unknown")).strip() or "volume.unknown"
            volume_type_counts[volume_type_id] = _as_int(volume_type_counts.get(volume_type_id, 0), 0) + 1
        blocked_states = {"closed", "locked", "damaged", "blocked"}
        open_states = {"open", "opening", "unlocked", "permeable"}
        open_portal_count = 0
        blocked_portal_count = 0
        for portal_id in portal_ids:
            portal = dict(portal_rows_by_id.get(portal_id) or {})
            if not portal:
                continue
            state_id = _portal_state_id(portal, state_machine_rows_by_id)
            if state_id in open_states:
                open_portal_count += 1
            elif state_id in blocked_states:
                blocked_portal_count += 1
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "volume_count": len(volume_ids),
            "portal_count": len(portal_ids),
            "open_portal_count": int(open_portal_count),
            "blocked_portal_count": int(blocked_portal_count),
            "connectivity_status": "connected" if open_portal_count > 0 else "isolated",
            "volume_type_counts": dict((k, volume_type_counts[k]) for k in sorted(volume_type_counts.keys())),
        }
    if section_id in {"section.interior.portal_states", "section.interior.portal_state_table"}:
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False, "portal_count": 0, "portal_states": []}
        portal_rows_by_id = _row_index((dict(state or {})).get("interior_portals"), "portal_id")
        state_machine_rows_by_id = _row_index((dict(state or {})).get("interior_portal_state_machines"), "machine_id")
        portal_states = []
        for portal_id in _sorted_unique_strings(graph.get("portals")):
            portal = dict(portal_rows_by_id.get(portal_id) or {})
            if not portal:
                continue
            state_id = _portal_state_id(portal, state_machine_rows_by_id)
            portal_states.append(
                {
                    "portal_id": portal_id,
                    "portal_type_id": str(portal.get("portal_type_id", "")).strip(),
                    "from_volume_id": str(portal.get("from_volume_id", "")).strip(),
                    "to_volume_id": str(portal.get("to_volume_id", "")).strip(),
                    "state_machine_id": str(portal.get("state_machine_id", "")).strip(),
                    "state_id": state_id,
                    "sealing_coefficient": int(max(0, _as_int(portal.get("sealing_coefficient", 0), 0))),
                }
            )
        state_counts: Dict[str, int] = {}
        for row in portal_states:
            state_token = str(row.get("state_id", "")).strip() or "unknown"
            state_counts[state_token] = _as_int(state_counts.get(state_token, 0), 0) + 1
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "portal_count": len(portal_states),
            "state_counts": dict((k, state_counts[k]) for k in sorted(state_counts.keys())),
            "portal_states": sorted(portal_states, key=lambda item: str(item.get("portal_id", "")))[:256],
        }
    if section_id in {"section.interior.pressure_map", "section.interior.pressure_summary"}:
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False, "graph_id": "", "rows": []}
        pressure_rows = []
        for row in _compartment_rows_for_graph(state, graph):
            volume_id = str(row.get("volume_id", "")).strip()
            if not volume_id:
                continue
            pressure = _quantize_map({"value": max(0, _as_int(row.get("derived_pressure", 0), 0))}, step=quant_step).get("value", 0)
            oxygen = _quantize_map({"value": max(0, _as_int(row.get("oxygen_fraction", 0), 0))}, step=quant_step).get("value", 0)
            pressure_rows.append(
                {
                    "volume_id": volume_id,
                    "derived_pressure": int(pressure),
                    "oxygen_fraction": int(oxygen),
                }
            )
        pressure_rows = sorted(pressure_rows, key=lambda item: str(item.get("volume_id", "")))
        min_pressure = min((int(item.get("derived_pressure", 0)) for item in pressure_rows), default=0)
        max_pressure = max((int(item.get("derived_pressure", 0)) for item in pressure_rows), default=0)
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "rows": pressure_rows[:512],
            "volume_count": len(pressure_rows),
            "min_pressure": int(min_pressure),
            "max_pressure": int(max_pressure),
        }
    if section_id in {"section.interior.flood_map", "section.interior.flood_summary"}:
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False, "graph_id": "", "rows": []}
        flood_rows = []
        for row in _compartment_rows_for_graph(state, graph):
            volume_id = str(row.get("volume_id", "")).strip()
            if not volume_id:
                continue
            water_volume = _quantize_map({"value": max(0, _as_int(row.get("water_volume", 0), 0))}, step=quant_step).get("value", 0)
            smoke_density = _quantize_map({"value": max(0, _as_int(row.get("smoke_density", 0), 0))}, step=quant_step).get("value", 0)
            flood_rows.append(
                {
                    "volume_id": volume_id,
                    "water_volume": int(water_volume),
                    "smoke_density": int(smoke_density),
                }
            )
        flood_rows = sorted(flood_rows, key=lambda item: str(item.get("volume_id", "")))
        flooded_count = len([item for item in flood_rows if int(item.get("water_volume", 0)) > 0])
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "rows": flood_rows[:512],
            "volume_count": len(flood_rows),
            "flooded_count": int(flooded_count),
        }
    if section_id == "section.interior.smoke_summary":
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False, "graph_id": "", "rows": []}
        smoke_rows = []
        warn_count = 0
        danger_count = 0
        for row in _compartment_rows_for_graph(state, graph):
            volume_id = str(row.get("volume_id", "")).strip()
            if not volume_id:
                continue
            smoke_density = _quantize_map({"value": max(0, _as_int(row.get("smoke_density", 0), 0))}, step=quant_step).get("value", 0)
            smoke_rows.append({"volume_id": volume_id, "smoke_density": int(smoke_density)})
            if int(smoke_density) >= 450:
                danger_count += 1
            elif int(smoke_density) >= 200:
                warn_count += 1
        smoke_rows = sorted(smoke_rows, key=lambda item: str(item.get("volume_id", "")))
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "rows": smoke_rows[:512],
            "volume_count": len(smoke_rows),
            "warn_count": int(warn_count),
            "danger_count": int(danger_count),
        }
    if section_id in {"section.interior.portal_leaks", "section.interior.flow_summary"}:
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False, "graph_id": "", "leaks": [], "portal_flow_rows": []}
        portal_ids = _sorted_unique_strings((dict(graph or {})).get("portals"))
        portal_rows_by_id = _row_index((dict(state or {})).get("interior_portals"), "portal_id")
        portal_flow_rows_by_id = _row_index((dict(state or {})).get("portal_flow_params"), "portal_id")
        leak_rows = []
        for row in _leak_rows_for_graph(state, graph):
            leak_rows.append(
                {
                    "leak_id": str(row.get("leak_id", "")).strip(),
                    "volume_id": str(row.get("volume_id", "")).strip(),
                    "leak_rate_air": int(_quantize_map({"value": max(0, _as_int(row.get("leak_rate_air", 0), 0))}, step=quant_step).get("value", 0)),
                    "leak_rate_water": int(_quantize_map({"value": max(0, _as_int(row.get("leak_rate_water", 0), 0))}, step=quant_step).get("value", 0)),
                    "hazard_model_id": str(row.get("hazard_model_id", "")).strip(),
                }
            )
        flow_rows = []
        for portal_id in portal_ids:
            portal_row = dict(portal_rows_by_id.get(portal_id) or {})
            flow_row = dict(portal_flow_rows_by_id.get(portal_id) or {})
            if not portal_row and not flow_row:
                continue
            flow_rows.append(
                {
                    "portal_id": portal_id,
                    "portal_type_id": str(portal_row.get("portal_type_id", "")).strip(),
                    "sealing_coefficient": int(_quantize_map({"value": max(0, _as_int(flow_row.get("sealing_coefficient", portal_row.get("sealing_coefficient", 0)), 0))}, step=quant_step).get("value", 0)),
                    "conductance_air": int(_quantize_map({"value": max(0, _as_int(flow_row.get("conductance_air", 0), 0))}, step=quant_step).get("value", 0)),
                    "conductance_water": int(_quantize_map({"value": max(0, _as_int(flow_row.get("conductance_water", 0), 0))}, step=quant_step).get("value", 0)),
                    "conductance_smoke": int(_quantize_map({"value": max(0, _as_int(flow_row.get("conductance_smoke", 0), 0))}, step=quant_step).get("value", 0)),
                }
            )
        if (not allow_hidden_state) and section_id == "section.interior.flow_summary":
            return {
                "available": True,
                "graph_id": str(graph.get("graph_id", "")).strip(),
                "redacted": True,
                "summary": "detail_redacted",
                "leak_count": int(len(leak_rows)),
            }
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "leak_count": len(leak_rows),
            "leaks": sorted(leak_rows, key=lambda item: str(item.get("leak_id", "")))[:256],
            "portal_flow_rows": sorted(flow_rows, key=lambda item: str(item.get("portal_id", "")))[:256],
        }
    if section_id == "section.pose_slots_summary":
        requester_subject_id = str(request.get("requester_subject_id", "")).strip()
        target_collection = str(target_payload.get("collection", "")).strip()
        target_slot_id = ""
        target_parent_assembly_id = ""
        if target_collection == "pose_slots":
            target_slot_id = str(row.get("pose_slot_id", "")).strip()
            target_parent_assembly_id = str(row.get("parent_assembly_id", "")).strip()
        visible_rows = _visible_pose_slots(
            state,
            requester_subject_id=requester_subject_id,
            allow_hidden_state=allow_hidden_state,
        )
        visible_by_id = dict((str(item.get("pose_slot_id", "")).strip(), dict(item)) for item in visible_rows if str(item.get("pose_slot_id", "")).strip())
        all_rows = [
            dict(item)
            for item in list((dict(state or {})).get("pose_slots") or [])
            if isinstance(item, dict)
        ]
        all_rows = sorted(all_rows, key=lambda item: str(item.get("pose_slot_id", "")))
        if allow_hidden_state:
            candidate_rows = list(all_rows)
        else:
            candidate_rows = list(visible_rows)
        if target_slot_id:
            candidate = dict(visible_by_id.get(target_slot_id) or {})
            candidate_rows = [candidate] if candidate else []
            if allow_hidden_state and not candidate_rows:
                candidate_rows = [dict(item) for item in all_rows if str(item.get("pose_slot_id", "")).strip() == target_slot_id]
        elif target_parent_assembly_id:
            candidate_rows = [
                dict(item)
                for item in candidate_rows
                if str(item.get("parent_assembly_id", "")).strip() == target_parent_assembly_id
            ]
        requester_volume_id = _requester_volume_id(state, requester_subject_id)
        slot_rows = []
        for slot in candidate_rows:
            slot_id = str(slot.get("pose_slot_id", "")).strip()
            if not slot_id:
                continue
            ext = dict(slot.get("extensions") or {}) if isinstance(slot.get("extensions"), dict) else {}
            occupant_ids = _sorted_unique_strings(ext.get("occupant_ids"))
            current_occupant_id = str(slot.get("current_occupant_id", "")).strip()
            occupied = bool(current_occupant_id or occupant_ids)
            show_occupant_id = (
                bool(allow_hidden_state)
                or bool(requester_subject_id and requester_subject_id == current_occupant_id)
                or bool(requester_subject_id and requester_subject_id in set(occupant_ids))
            )
            slot_rows.append(
                {
                    "pose_slot_id": slot_id,
                    "parent_assembly_id": str(slot.get("parent_assembly_id", "")).strip(),
                    "interior_volume_id": str(slot.get("interior_volume_id", "")).strip(),
                    "allowed_postures": _sorted_unique_strings(slot.get("allowed_postures")),
                    "requires_access_path": bool(slot.get("requires_access_path", True)),
                    "accessible": bool(
                        requester_subject_id
                        and _pose_slot_reachable(
                            state,
                            from_volume_id=requester_volume_id,
                            slot=slot,
                        )
                    ),
                    "exclusivity": str(slot.get("exclusivity", "single")).strip() or "single",
                    "occupied": occupied,
                    "current_occupant_id": current_occupant_id if show_occupant_id else None,
                    "control_binding_id": (
                        str(slot.get("control_binding_id", "")).strip() or None
                    ) if allow_hidden_state else None,
                }
            )
        return {
            "slot_count": len(slot_rows),
            "occupied_count": len([item for item in slot_rows if bool(item.get("occupied", False))]),
            "rows": sorted(slot_rows, key=lambda item: str(item.get("pose_slot_id", "")))[:256],
        }
    if section_id == "section.mount_points_summary":
        requester_subject_id = str(request.get("requester_subject_id", "")).strip()
        target_collection = str(target_payload.get("collection", "")).strip()
        target_mount_point_id = ""
        if target_collection == "mount_points":
            target_mount_point_id = str(row.get("mount_point_id", "")).strip()
        visible_pose_rows = _visible_pose_slots(
            state,
            requester_subject_id=requester_subject_id,
            allow_hidden_state=allow_hidden_state,
        )
        visible_parent_ids = set(
            str(item.get("parent_assembly_id", "")).strip()
            for item in visible_pose_rows
            if str(item.get("parent_assembly_id", "")).strip()
        )
        all_mount_rows = [
            dict(item)
            for item in list((dict(state or {})).get("mount_points") or [])
            if isinstance(item, dict)
        ]
        all_mount_rows = sorted(all_mount_rows, key=lambda item: str(item.get("mount_point_id", "")))
        if allow_hidden_state:
            candidate_rows = list(all_mount_rows)
        else:
            candidate_rows = [
                dict(item)
                for item in all_mount_rows
                if str(item.get("parent_assembly_id", "")).strip() in visible_parent_ids
            ]
        if target_mount_point_id:
            target_rows = [
                dict(item)
                for item in all_mount_rows
                if str(item.get("mount_point_id", "")).strip() == target_mount_point_id
            ]
            if target_rows:
                connected_id = str((dict(target_rows[0])).get("connected_to_mount_point_id", "")).strip()
                if connected_id:
                    target_rows.extend(
                        [
                            dict(item)
                            for item in all_mount_rows
                            if str(item.get("mount_point_id", "")).strip() == connected_id
                        ]
                    )
            candidate_rows = sorted(
                dict((str(item.get("mount_point_id", "")).strip(), dict(item)) for item in target_rows if str(item.get("mount_point_id", "")).strip()).values(),
                key=lambda item: str(item.get("mount_point_id", "")),
            )
        visible_ids = set(str(item.get("mount_point_id", "")).strip() for item in candidate_rows)
        rows = []
        for mount in candidate_rows:
            mount_point_id = str(mount.get("mount_point_id", "")).strip()
            if not mount_point_id:
                continue
            connected_to = str(mount.get("connected_to_mount_point_id", "")).strip()
            ext = dict(mount.get("extensions") or {}) if isinstance(mount.get("extensions"), dict) else {}
            rows.append(
                {
                    "mount_point_id": mount_point_id,
                    "parent_assembly_id": str(mount.get("parent_assembly_id", "")).strip(),
                    "mount_tags": _sorted_unique_strings(mount.get("mount_tags")),
                    "attached": bool(connected_to),
                    "connected_to_mount_point_id": (
                        connected_to if (allow_hidden_state or connected_to in visible_ids) else None
                    ) or None,
                    "state_machine_id": str(mount.get("state_machine_id", "")).strip() or None,
                    "state_id": str(ext.get("state_id", "")).strip() or None,
                }
            )
        return {
            "mount_point_count": len(rows),
            "attached_count": len([item for item in rows if bool(item.get("attached", False))]),
            "rows": sorted(rows, key=lambda item: str(item.get("mount_point_id", "")))[:256],
        }
    if section_id == "section.capabilities_summary":
        payload_ext = dict(target_payload.get("extensions") or {})
        summary = dict(payload_ext.get("capabilities_summary") or {})
        visible_capability_ids = _sorted_unique_strings(summary.get("visible_capability_ids"))
        all_capability_ids = _sorted_unique_strings(summary.get("all_capability_ids"))
        if not summary:
            return {
                "available": False,
                "entity_id": str(summary.get("entity_id", "")).strip() or None,
                "capability_count": 0,
                "visible_capability_ids": [],
                "epistemic_redaction": "unknown",
            }
        if allow_hidden_state:
            return {
                "available": True,
                "entity_id": str(summary.get("entity_id", "")).strip() or None,
                "capability_count": len(all_capability_ids),
                "visible_capability_ids": list(all_capability_ids),
                "all_capability_ids": list(all_capability_ids),
                "epistemic_redaction": "none",
            }
        return {
            "available": True,
            "entity_id": str(summary.get("entity_id", "")).strip() or None,
            "capability_count": len(visible_capability_ids),
            "visible_capability_ids": list(visible_capability_ids),
            "epistemic_redaction": str(summary.get("epistemic_redaction", "diegetic_filtered")).strip() or "diegetic_filtered",
        }
    if section_id == "section.plan_summary":
        target_collection = str(target_payload.get("collection", "")).strip()
        if target_collection != "plan_artifacts":
            return {"available": False}
        plan_row = dict(row)
        preview = dict(plan_row.get("spatial_preview_data") or {})
        preview_renderables = [dict(item) for item in list(preview.get("renderables") or []) if isinstance(item, dict)]
        preview_materials = [dict(item) for item in list(preview.get("materials") or []) if isinstance(item, dict)]
        extensions = dict(plan_row.get("extensions") or {})
        history = [dict(item) for item in list(extensions.get("update_history") or []) if isinstance(item, dict)]
        return {
            "available": True,
            "plan_id": str(plan_row.get("plan_id", "")).strip(),
            "plan_type_id": str(plan_row.get("plan_type_id", "")).strip(),
            "status": str(plan_row.get("status", "")).strip() or "draft",
            "compiled_ir_id": str(plan_row.get("compiled_ir_id", "")).strip() or None,
            "compiled_blueprint_ref": str(plan_row.get("compiled_blueprint_ref", "")).strip() or None,
            "estimated_bom_ref": str(plan_row.get("estimated_bom_ref", "")).strip() or None,
            "preview_renderable_count": len(preview_renderables),
            "preview_material_count": len(preview_materials),
            "update_count": len(history),
        }
    if section_id == "section.plan_resource_requirements":
        target_collection = str(target_payload.get("collection", "")).strip()
        if target_collection != "plan_artifacts":
            return {"available": False}
        plan_row = dict(row)
        resources = dict(plan_row.get("required_resources_summary") or {})
        material_mass_raw = dict(resources.get("material_mass_raw") or {})
        part_counts = dict(resources.get("part_counts") or {})
        summary = {
            "available": True,
            "plan_id": str(plan_row.get("plan_id", "")).strip(),
            "total_mass_raw": int(max(0, _as_int(resources.get("total_mass_raw", 0), 0))),
            "total_part_count": int(max(0, _as_int(resources.get("total_part_count", 0), 0))),
            "bom_summary_hash": str(resources.get("bom_summary_hash", "")).strip() or None,
            "material_class_count": len([key for key in material_mass_raw.keys() if str(key).strip()]),
            "part_class_count": len([key for key in part_counts.keys() if str(key).strip()]),
        }
        if not allow_hidden_state:
            summary["epistemic_redaction"] = "coarse_summary"
            return summary
        summary["material_mass_raw"] = dict(
            (str(key), int(max(0, _as_int(value, 0))))
            for key, value in sorted(material_mass_raw.items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
        summary["part_counts"] = dict(
            (str(key), int(max(0, _as_int(value, 0))))
            for key, value in sorted(part_counts.items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
        summary["epistemic_redaction"] = "none"
        return summary
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
    achieved_fidelity, section_ids, section_cost_units, degraded, fidelity_request, fidelity_allocation, fidelity_arbitration = _resolve_fidelity(
        desired_fidelity=str(request.get("desired_fidelity", "macro")),
        target_kind=str(request.get("target_kind", "")),
        max_cost_units=_as_int(request.get("max_cost_units", 0), 0),
        section_rows=section_rows,
        micro_allowed=micro_allowed,
        micro_available=micro_available,
        strict_budget=bool(strict_budget),
        requester_subject_id=str(request.get("requester_subject_id", "")).strip() or "subject.inspect",
        tick=_as_int(request.get("tick", 0), 0),
        server_profile_id=str((dict(policy_context or {})).get("server_profile_id", "server.profile.inspect")).strip()
        or "server.profile.inspect",
        fidelity_policy_id=str((dict(policy_context or {})).get("fidelity_policy_id", DEFAULT_FIDELITY_POLICY_ID)).strip()
        or DEFAULT_FIDELITY_POLICY_ID,
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
                allow_hidden_state=allow_hidden_state,
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
            "fidelity_request": dict(fidelity_request),
            "fidelity_allocation": dict(fidelity_allocation),
            "fidelity_arbitration": dict(fidelity_arbitration),
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
        "fidelity_request": dict(fidelity_request),
        "fidelity_allocation": dict(fidelity_allocation),
        "fidelity_arbitration": dict(fidelity_arbitration),
    }
    return snapshot, diagnostics
