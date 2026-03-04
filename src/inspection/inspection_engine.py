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
    "vehicle",
    "project",
    "plan",
    "institution",
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
    "formalization",
}
_VALID_FIDELITY = ("macro", "meso", "micro")
_SECTION_IDS_BY_FIDELITY = {
    "macro": [
        "section.capabilities_summary",
        "section.material_stocks",
        "section.flow_summary",
        "section.flow_utilization",
        "section.field.summary",
        "section.field.gravity",
        "section.field.radiation",
        "section.field.irradiance",
        "section.chem.fuel_levels",
        "section.chem.energy_output",
        "section.chem.emissions",
        "section.chem.efficiency",
        "section.interior.connectivity_summary",
        "section.interior.portal_state_table",
        "section.interior.pressure_summary",
        "section.interior.flood_summary",
        "section.interior.smoke_summary",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.spec_compliance_summary",
        "section.commitments_summary",
        "section.events_summary",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.flow_utilization",
        "section.field.summary",
        "section.field.gravity",
        "section.field.radiation",
        "section.field.irradiance",
        "section.chem.fuel_levels",
        "section.chem.energy_output",
        "section.chem.emissions",
        "section.chem.efficiency",
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
        "section.spec_compliance_summary",
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
        "section.field.summary",
        "section.field.gravity",
        "section.field.radiation",
        "section.field.irradiance",
        "section.chem.fuel_levels",
        "section.chem.energy_output",
        "section.chem.emissions",
        "section.chem.efficiency",
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
        "section.spec_compliance_summary",
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
        "section.mob.network_summary",
        "section.mob.congestion_summary",
        "section.signal.network_summary",
        "section.signal.quality_summary",
        "section.models.summary",
        "section.phys.momentum_summary",
        "section.phys.kinetic_energy",
        "section.phys.entropy_summary",
        "section.phys.entropy_effects",
        "section.field.summary",
        "section.field.gravity",
        "section.field.radiation",
        "section.field.irradiance",
        "section.safety.instances",
        "section.safety.events",
        "section.elec.local_panel_state",
        "section.elec.pf_summary",
        "section.elec.loss_heat_summary",
        "section.elec.fault_summary",
        "section.elec.compliance_summary",
        "section.thermal.node_summary",
        "section.thermal.edge_summary",
        "section.thermal.overheat_risks",
        "section.thermal.phase_states",
        "section.thermal.cure_progress",
        "section.thermal.insulation_effects",
        "section.thermal.ambient_exchange_summary",
        "section.thermal.radiator_efficiency",
        "section.thermal.fire_states",
        "section.thermal.runaway_events",
        "section.chem.fuel_levels",
        "section.chem.energy_output",
        "section.chem.emissions",
        "section.chem.efficiency",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.networkgraph.summary",
        "section.mob.network_summary",
        "section.networkgraph.route",
        "section.mob.route_result",
        "section.mob.congestion_summary",
        "section.mob.edge_occupancy",
        "section.networkgraph.capacity_utilization",
        "section.signal.network_summary",
        "section.signal.channel_queue_depth",
        "section.signal.delivery_status",
        "section.signal.quality_summary",
        "section.signal.inbox_summary",
        "section.inbox.acceptance_summary",
        "section.trust.edges_summary",
        "section.signal.sent_messages",
        "section.signal.aggregation_status",
        "section.models.summary",
        "section.phys.momentum_summary",
        "section.phys.kinetic_energy",
        "section.phys.entropy_summary",
        "section.phys.entropy_effects",
        "section.field.summary",
        "section.field.gravity",
        "section.field.radiation",
        "section.field.irradiance",
        "section.safety.instances",
        "section.safety.events",
        "section.elec.local_panel_state",
        "section.elec.fault_summary",
        "section.elec.protection_device_states",
        "section.elec.device_states",
        "section.elec.pf_summary",
        "section.elec.loss_heat_summary",
        "section.elec.compliance_summary",
        "section.thermal.node_summary",
        "section.thermal.edge_summary",
        "section.thermal.overheat_risks",
        "section.thermal.phase_states",
        "section.thermal.cure_progress",
        "section.thermal.insulation_effects",
        "section.thermal.ambient_exchange_summary",
        "section.thermal.radiator_efficiency",
        "section.thermal.fire_states",
        "section.thermal.runaway_events",
        "section.chem.fuel_levels",
        "section.chem.energy_output",
        "section.chem.emissions",
        "section.chem.efficiency",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.networkgraph.summary",
        "section.mob.network_summary",
        "section.networkgraph.route",
        "section.mob.route_result",
        "section.mob.congestion_summary",
        "section.mob.edge_occupancy",
        "section.networkgraph.capacity_utilization",
        "section.signal.network_summary",
        "section.signal.channel_queue_depth",
        "section.signal.delivery_status",
        "section.signal.quality_summary",
        "section.signal.inbox_summary",
        "section.inbox.acceptance_summary",
        "section.trust.edges_summary",
        "section.signal.sent_messages",
        "section.signal.aggregation_status",
        "section.models.summary",
        "section.phys.momentum_summary",
        "section.phys.kinetic_energy",
        "section.phys.entropy_summary",
        "section.phys.entropy_effects",
        "section.field.summary",
        "section.field.gravity",
        "section.field.radiation",
        "section.field.irradiance",
        "section.safety.instances",
        "section.safety.events",
        "section.elec.local_panel_state",
        "section.elec.fault_summary",
        "section.elec.protection_device_states",
        "section.elec.device_states",
        "section.elec.pf_summary",
        "section.elec.loss_heat_summary",
        "section.elec.compliance_summary",
        "section.thermal.node_summary",
        "section.thermal.edge_summary",
        "section.thermal.overheat_risks",
        "section.thermal.phase_states",
        "section.thermal.cure_progress",
        "section.thermal.insulation_effects",
        "section.thermal.ambient_exchange_summary",
        "section.thermal.radiator_efficiency",
        "section.thermal.fire_states",
        "section.thermal.runaway_events",
        "section.chem.fuel_levels",
        "section.chem.energy_output",
        "section.chem.emissions",
        "section.chem.efficiency",
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
_SECTION_IDS_BY_FIDELITY_FORMALIZATION = {
    "macro": [
        "section.capabilities_summary",
        "section.formalization_summary",
        "section.spec_compliance_summary",
        "section.commitments_summary",
        "section.events_summary",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.formalization_summary",
        "section.formalization_candidates",
        "section.spec_compliance_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.formalization_summary",
        "section.formalization_candidates",
        "section.spec_compliance_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
    ],
}
_SECTION_IDS_BY_FIDELITY_INSTITUTION = {
    "macro": [
        "section.capabilities_summary",
        "section.institution.bulletins",
        "section.institution.dispatch_state",
        "section.institution.compliance_reports",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.institution.bulletins",
        "section.institution.dispatch_state",
        "section.institution.compliance_reports",
        "section.events_summary",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.institution.bulletins",
        "section.institution.dispatch_state",
        "section.institution.compliance_reports",
        "section.events_summary",
    ],
}
_SECTION_IDS_BY_FIDELITY_VEHICLE = {
    "macro": [
        "section.capabilities_summary",
        "section.vehicle.summary",
        "section.vehicle.specs",
        "section.vehicle.ports",
        "section.vehicle.interior_summary",
        "section.vehicle.wear_risk",
    ],
    "meso": [
        "section.capabilities_summary",
        "section.vehicle.summary",
        "section.vehicle.specs",
        "section.vehicle.ports",
        "section.vehicle.pose_slots",
        "section.vehicle.interior_summary",
        "section.vehicle.portal_states",
        "section.vehicle.pressure_map",
        "section.vehicle.wear_risk",
        "section.events_summary",
    ],
    "micro": [
        "section.capabilities_summary",
        "section.vehicle.summary",
        "section.vehicle.specs",
        "section.vehicle.ports",
        "section.vehicle.pose_slots",
        "section.vehicle.interior_summary",
        "section.vehicle.portal_states",
        "section.vehicle.pressure_map",
        "section.vehicle.wear_risk",
        "section.events_summary",
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
    "section.mob.network_summary": {"title": "Mobility Network Summary", "extensions": {"cost_units": 1}},
    "section.mob.route_result": {"title": "Mobility Route Result", "extensions": {"cost_units": 2}},
    "section.mob.edge_occupancy": {"title": "Mobility Edge Occupancy", "extensions": {"cost_units": 2}},
    "section.mob.congestion_summary": {"title": "Mobility Congestion Summary", "extensions": {"cost_units": 1}},
    "section.signal.network_summary": {"title": "Signal Network Summary", "extensions": {"cost_units": 1}},
    "section.signal.channel_queue_depth": {"title": "Signal Channel Queue Depth", "extensions": {"cost_units": 2}},
    "section.signal.delivery_status": {"title": "Signal Delivery Status", "extensions": {"cost_units": 2}},
    "section.signal.quality_summary": {"title": "Signal Quality Summary", "extensions": {"cost_units": 2}},
    "section.signal.inbox_summary": {"title": "Signal Inbox Summary", "extensions": {"cost_units": 1}},
    "section.inbox.acceptance_summary": {"title": "Inbox Acceptance Summary", "extensions": {"cost_units": 1}},
    "section.trust.edges_summary": {"title": "Trust Edge Summary", "extensions": {"cost_units": 2}},
    "section.signal.sent_messages": {"title": "Signal Sent Messages", "extensions": {"cost_units": 2}},
    "section.signal.aggregation_status": {"title": "Signal Aggregation Status", "extensions": {"cost_units": 2}},
    "section.models.summary": {"title": "Constitutive Model Summary", "extensions": {"cost_units": 2}},
    "section.phys.momentum_summary": {"title": "Physics Momentum Summary", "extensions": {"cost_units": 1}},
    "section.phys.kinetic_energy": {"title": "Physics Kinetic Energy", "extensions": {"cost_units": 1}},
    "section.phys.entropy_summary": {"title": "Physics Entropy Summary", "extensions": {"cost_units": 1}},
    "section.phys.entropy_effects": {"title": "Physics Entropy Effects", "extensions": {"cost_units": 1}},
    "section.field.summary": {"title": "Field Summary", "extensions": {"cost_units": 1}},
    "section.field.gravity": {"title": "Field Gravity", "extensions": {"cost_units": 1}},
    "section.field.radiation": {"title": "Field Radiation", "extensions": {"cost_units": 1}},
    "section.field.irradiance": {"title": "Field Irradiance", "extensions": {"cost_units": 1}},
    "section.safety.instances": {"title": "Safety Instances", "extensions": {"cost_units": 1}},
    "section.safety.events": {"title": "Safety Events", "extensions": {"cost_units": 2}},
    "section.elec.local_panel_state": {"title": "Electrical Local Panel State", "extensions": {"cost_units": 1}},
    "section.elec.device_states": {"title": "Electrical Device States", "extensions": {"cost_units": 2}},
    "section.elec.fault_summary": {"title": "Electrical Fault Summary", "extensions": {"cost_units": 2}},
    "section.elec.protection_device_states": {"title": "Electrical Protection Devices", "extensions": {"cost_units": 2}},
    "section.elec.pf_summary": {"title": "Electrical PF Summary", "extensions": {"cost_units": 1}},
    "section.elec.loss_heat_summary": {"title": "Electrical Loss/Heat Summary", "extensions": {"cost_units": 1}},
    "section.elec.compliance_summary": {"title": "Electrical Compliance Summary", "extensions": {"cost_units": 1}},
    "section.thermal.node_summary": {"title": "Thermal Node Summary", "extensions": {"cost_units": 1}},
    "section.thermal.edge_summary": {"title": "Thermal Edge Summary", "extensions": {"cost_units": 2}},
    "section.thermal.overheat_risks": {"title": "Thermal Overheat Risks", "extensions": {"cost_units": 2}},
    "section.thermal.phase_states": {"title": "Thermal Phase States", "extensions": {"cost_units": 2}},
    "section.thermal.cure_progress": {"title": "Thermal Cure Progress", "extensions": {"cost_units": 2}},
    "section.thermal.insulation_effects": {"title": "Thermal Insulation Effects", "extensions": {"cost_units": 2}},
    "section.thermal.ambient_exchange_summary": {"title": "Thermal Ambient Exchange", "extensions": {"cost_units": 2}},
    "section.thermal.radiator_efficiency": {"title": "Thermal Radiator Efficiency", "extensions": {"cost_units": 2}},
    "section.thermal.fire_states": {"title": "Thermal Fire States", "extensions": {"cost_units": 2}},
    "section.thermal.runaway_events": {"title": "Thermal Runaway Events", "extensions": {"cost_units": 2}},
    "section.chem.fuel_levels": {"title": "Combustion Fuel Levels", "extensions": {"cost_units": 1}},
    "section.chem.energy_output": {"title": "Combustion Energy Output", "extensions": {"cost_units": 1}},
    "section.chem.emissions": {"title": "Combustion Emissions", "extensions": {"cost_units": 1}},
    "section.chem.efficiency": {"title": "Combustion Efficiency", "extensions": {"cost_units": 1}},
    "section.institution.bulletins": {"title": "Institution Bulletins", "extensions": {"cost_units": 2}},
    "section.institution.dispatch_state": {"title": "Institution Dispatch State", "extensions": {"cost_units": 2}},
    "section.institution.compliance_reports": {"title": "Institution Compliance Reports", "extensions": {"cost_units": 2}},
    "section.networkgraph.capacity_utilization": {
        "title": "NetworkGraph Capacity Utilization",
        "extensions": {"cost_units": 2},
    },
    "section.pose_slots_summary": {"title": "Pose Slots Summary", "extensions": {"cost_units": 1}},
    "section.mount_points_summary": {"title": "Mount Points Summary", "extensions": {"cost_units": 1}},
    "section.plan_summary": {"title": "Plan Summary", "extensions": {"cost_units": 1}},
    "section.plan_resource_requirements": {"title": "Plan Resource Requirements", "extensions": {"cost_units": 2}},
    "section.formalization_summary": {"title": "Formalization Summary", "extensions": {"cost_units": 1}},
    "section.formalization_candidates": {"title": "Formalization Candidates", "extensions": {"cost_units": 2}},
    "section.vehicle.summary": {"title": "Vehicle Summary", "extensions": {"cost_units": 1}},
    "section.vehicle.specs": {"title": "Vehicle Specs", "extensions": {"cost_units": 1}},
    "section.vehicle.ports": {"title": "Vehicle Ports", "extensions": {"cost_units": 1}},
    "section.vehicle.pose_slots": {"title": "Vehicle Pose Slots", "extensions": {"cost_units": 2}},
    "section.vehicle.interior_summary": {"title": "Vehicle Interior Summary", "extensions": {"cost_units": 2}},
    "section.vehicle.portal_states": {"title": "Vehicle Portal States", "extensions": {"cost_units": 2}},
    "section.vehicle.pressure_map": {"title": "Vehicle Pressure Map", "extensions": {"cost_units": 2}},
    "section.vehicle.wear_risk": {"title": "Vehicle Wear Risk", "extensions": {"cost_units": 1}},
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
    "section.spec_compliance_summary": {"title": "Spec Compliance Summary", "extensions": {"cost_units": 1}},
    "section.commitments_summary": {"title": "Commitments", "extensions": {"cost_units": 2}},
    "section.events_summary": {"title": "Events", "extensions": {"cost_units": 2}},
    "section.reenactment_link": {"title": "Reenactment", "extensions": {"cost_units": 1}},
    "section.micro_parts_summary": {"title": "Micro Parts Summary", "extensions": {"cost_units": 4}},
}
_MOBILITY_CURVATURE_WARN_RADIUS_MM = 12000


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
    if token.startswith("institution."):
        return "institution"
    if token.startswith("vehicle."):
        return "vehicle"
    if token.startswith("formalization.") or token.startswith("candidate.") or token.startswith("formalization.event."):
        return "formalization"
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
    if kind == "vehicle":
        return list(_SECTION_IDS_BY_FIDELITY_VEHICLE[token])
    if kind == "plan":
        return list(_SECTION_IDS_BY_FIDELITY_PLAN[token])
    if kind == "graph":
        return list(_SECTION_IDS_BY_FIDELITY_GRAPH[token])
    if kind == "pose_slot":
        return list(_SECTION_IDS_BY_FIDELITY_POSE[token])
    if kind == "mount_point":
        return list(_SECTION_IDS_BY_FIDELITY_MOUNT[token])
    if kind == "formalization":
        return list(_SECTION_IDS_BY_FIDELITY_FORMALIZATION[token])
    if kind == "institution":
        return list(_SECTION_IDS_BY_FIDELITY_INSTITUTION[token])
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
        "vehicle_events",
        "formalization_events",
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
                str(row.get("formalization_id", "")).strip(),
                str(ext.get("asset_id", "")).strip(),
                str(ext.get("project_id", "")).strip(),
                str(ext.get("manifest_id", "")).strip(),
                str(ext.get("machine_id", "")).strip(),
                str(ext.get("port_id", "")).strip(),
                str(ext.get("operation_id", "")).strip(),
                str(ext.get("connection_id", "")).strip(),
                str(ext.get("formalization_id", "")).strip(),
                str(ext.get("candidate_id", "")).strip(),
                str(ext.get("network_graph_ref", "")).strip(),
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
    collection = str(target_payload.get("collection", "")).strip()

    def _formalization_id_from_payload() -> str:
        if collection == "formalization_states":
            return str(row.get("formalization_id", "")).strip()
        if collection == "formalization_inference_candidates":
            return str(row.get("formalization_id", "")).strip()
        if collection == "formalization_events":
            return str(row.get("formalization_id", "")).strip()
        token = str(request.get("target_id", "")).strip()
        if token.startswith("formalization."):
            return token
        if token.startswith("candidate."):
            for candidate in list((dict(state or {})).get("formalization_inference_candidates") or []):
                if not isinstance(candidate, dict):
                    continue
                if str(candidate.get("candidate_id", "")).strip() != token:
                    continue
                return str(candidate.get("formalization_id", "")).strip()
        if token.startswith("formalization.event."):
            for event_row in list((dict(state or {})).get("formalization_events") or []):
                if not isinstance(event_row, dict):
                    continue
                if str(event_row.get("event_id", "")).strip() != token:
                    continue
                return str(event_row.get("formalization_id", "")).strip()
        return ""

    def _formalization_state_row() -> dict:
        formalization_id = _formalization_id_from_payload()
        if not formalization_id:
            return {}
        for state_row in list((dict(state or {})).get("formalization_states") or []):
            if not isinstance(state_row, dict):
                continue
            if str(state_row.get("formalization_id", "")).strip() == formalization_id:
                return dict(state_row)
        return {}

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

    if section_id == "section.formalization_summary":
        formalization_row = _formalization_state_row()
        formalization_id = str(formalization_row.get("formalization_id", "")).strip()
        if not formalization_row:
            return {"available": False}
        state_token = str(formalization_row.get("state", "raw")).strip() or "raw"
        target_context_id = str(formalization_row.get("target_context_id", "")).strip() or None
        raw_sources = _sorted_unique_strings(formalization_row.get("raw_sources"))
        candidate_count = len(
            [
                candidate
                for candidate in list((dict(state or {})).get("formalization_inference_candidates") or [])
                if isinstance(candidate, dict)
                and str(candidate.get("formalization_id", "")).strip() == formalization_id
            ]
        )
        event_rows = [
            dict(item)
            for item in list((dict(state or {})).get("formalization_events") or [])
            if isinstance(item, dict) and str(item.get("formalization_id", "")).strip() == formalization_id
        ]
        latest_event = (
            sorted(
                event_rows,
                key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("event_id", ""))),
            )[-1]
            if event_rows
            else {}
        )
        payload = {
            "available": True,
            "formalization_id": formalization_id,
            "target_kind": str(formalization_row.get("target_kind", "")).strip() or "custom",
            "state": state_token,
            "state_rank": {"raw": 0, "inferred": 1, "formal": 2, "networked": 3}.get(state_token, 0),
            "raw_source_count": len(raw_sources),
            "candidate_count": int(candidate_count),
            "event_count": int(len(event_rows)),
            "spec_id": str(formalization_row.get("spec_id", "")).strip() or None,
            "has_formal_artifact": bool(str(formalization_row.get("formal_artifact_ref", "")).strip()),
            "has_network_graph_ref": bool(str(formalization_row.get("network_graph_ref", "")).strip()),
            "latest_transition": str(latest_event.get("transition", "")).strip() or None,
            "latest_event_id": str(latest_event.get("event_id", "")).strip() or None,
        }
        if not allow_hidden_state:
            payload["epistemic_redaction"] = "coarse_summary"
            return payload
        payload["target_context_id"] = target_context_id
        payload["raw_sources"] = list(raw_sources)
        payload["inferred_artifact_ref"] = str(formalization_row.get("inferred_artifact_ref", "")).strip() or None
        payload["formal_artifact_ref"] = str(formalization_row.get("formal_artifact_ref", "")).strip() or None
        payload["network_graph_ref"] = str(formalization_row.get("network_graph_ref", "")).strip() or None
        payload["created_tick"] = int(max(0, _as_int(formalization_row.get("created_tick", 0), 0)))
        payload["epistemic_redaction"] = "none"
        return payload

    if section_id == "section.formalization_candidates":
        formalization_id = _formalization_id_from_payload()
        if not formalization_id:
            return {"available": False}
        candidate_rows = [
            dict(item)
            for item in list((dict(state or {})).get("formalization_inference_candidates") or [])
            if isinstance(item, dict) and str(item.get("formalization_id", "")).strip() == formalization_id
        ]
        candidate_rows = sorted(
            candidate_rows,
            key=lambda item: (
                str(item.get("candidate_kind", "")),
                -_as_int(item.get("confidence_score", 0), 0),
                str(item.get("candidate_id", "")),
            ),
        )
        payload = {
            "available": True,
            "formalization_id": formalization_id,
            "candidate_count": int(len(candidate_rows)),
            "candidate_kind_counts": {},
            "max_confidence_score": int(
                max([_as_int(item.get("confidence_score", 0), 0) for item in candidate_rows], default=0)
            ),
        }
        counts: Dict[str, int] = {}
        for candidate in candidate_rows:
            candidate_kind = str(candidate.get("candidate_kind", "")).strip() or "corridor"
            counts[candidate_kind] = _as_int(counts.get(candidate_kind, 0), 0) + 1
        payload["candidate_kind_counts"] = dict((key, counts[key]) for key in sorted(counts.keys()))
        if not allow_hidden_state:
            payload["epistemic_redaction"] = "coarse_summary"
            return payload
        payload["rows"] = [
            {
                "candidate_id": str(candidate.get("candidate_id", "")).strip(),
                "candidate_kind": str(candidate.get("candidate_kind", "")).strip() or "corridor",
                "confidence_score": int(max(0, _as_int(candidate.get("confidence_score", 0), 0))),
                "geometry_preview_ref": str(candidate.get("geometry_preview_ref", "")).strip() or None,
                "suggested_spec_ids": _sorted_unique_strings(candidate.get("suggested_spec_ids")),
            }
            for candidate in candidate_rows[:128]
            if str(candidate.get("candidate_id", "")).strip()
        ]
        payload["epistemic_redaction"] = "none"
        return payload

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
    if section_id in {"section.networkgraph.summary", "section.mob.network_summary"}:
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip()
        node_rows = [dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, dict)]
        edge_rows = [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, dict)]
        validation_mode = str(graph.get("validation_mode", "")).strip() or "strict"
        switch_rows = []
        switch_count = 0
        switch_machine_rows = {
            str(item.get("machine_id", "")).strip(): dict(item)
            for item in list((dict(state or {})).get("mobility_switch_state_machines") or [])
            if isinstance(item, dict) and str(item.get("machine_id", "")).strip()
        }
        spec_missing_edge_count = 0
        edge_kind_counts: Dict[str, int] = {}
        for edge in edge_rows:
            payload = dict(edge.get("payload") or {})
            edge_kind = str(payload.get("edge_kind", "")).strip() or "unknown"
            edge_kind_counts[edge_kind] = _as_int(edge_kind_counts.get(edge_kind, 0), 0) + 1
            if not str(payload.get("spec_id", "")).strip():
                spec_missing_edge_count += 1
        for node in node_rows:
            payload = dict(node.get("payload") or {})
            if str(payload.get("node_kind", "")).strip() != "switch":
                continue
            switch_count += 1
            machine_id = str(payload.get("state_machine_id", "")).strip()
            machine = dict(switch_machine_rows.get(machine_id) or {})
            switch_rows.append(
                {
                    "node_id": str(node.get("node_id", "")).strip(),
                    "machine_id": machine_id or None,
                    "active_edge_id": str(machine.get("state_id", "")).strip() or None,
                    "outgoing_edge_ids": _sorted_unique_strings((dict(machine.get("extensions") or {})).get("outgoing_edge_ids")),
                }
            )
        itinerary_rows_by_id = _row_index((dict(state or {})).get("itineraries"), "itinerary_id")
        timetable_board_rows = []
        for schedule_row in sorted(
            (dict(item) for item in list((dict(state or {})).get("travel_schedules") or []) if isinstance(item, dict)),
            key=lambda item: (_as_int(item.get("next_due_tick", 0), 0), str(item.get("schedule_id", ""))),
        ):
            if not bool(schedule_row.get("active", True)):
                continue
            itinerary_id = str((dict(schedule_row.get("extensions") or {})).get("itinerary_id", "")).strip()
            itinerary_row = dict(itinerary_rows_by_id.get(itinerary_id) or {})
            if not itinerary_row:
                continue
            itinerary_ext = dict(itinerary_row.get("extensions") or {})
            if str(itinerary_ext.get("graph_id", "")).strip() != graph_id:
                continue
            departure_tick = int(max(0, _as_int(itinerary_row.get("departure_tick", 0), 0)))
            estimated_arrival_tick = int(max(0, _as_int(itinerary_row.get("estimated_arrival_tick", departure_tick), departure_tick)))
            duration_ticks = int(max(0, estimated_arrival_tick - departure_tick))
            next_due_tick = int(max(0, _as_int(schedule_row.get("next_due_tick", schedule_row.get("start_tick", 0)), 0)))
            route_node_ids = [str(item).strip() for item in list(itinerary_row.get("route_node_ids") or []) if str(item).strip()]
            timetable_board_rows.append(
                {
                    "schedule_id": str(schedule_row.get("schedule_id", "")).strip() or None,
                    "vehicle_id": str(schedule_row.get("target_id", "")).strip() or None,
                    "itinerary_id": itinerary_id,
                    "next_departure_tick": int(next_due_tick),
                    "projected_arrival_tick": int(next_due_tick + duration_ticks),
                    "origin_node_id": route_node_ids[0] if route_node_ids else None,
                    "destination_node_id": route_node_ids[-1] if route_node_ids else None,
                    "travel_state": str(itinerary_ext.get("status", "")).strip() or "planned",
                }
            )
        return {
            "graph_id": graph_id,
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "validation_mode": validation_mode,
            "routing_policy_id": str(graph.get("deterministic_routing_policy_id", "")).strip(),
            "graph_partition_id": str(graph.get("graph_partition_id", "")).strip() or None,
            "switch_count": int(switch_count),
            "switch_states": sorted(switch_rows, key=lambda item: str(item.get("node_id", ""))),
            "spec_missing_edge_count": int(spec_missing_edge_count),
            "edge_kind_counts": dict((k, edge_kind_counts[k]) for k in sorted(edge_kind_counts.keys())),
            "timetable_board_count": int(len(timetable_board_rows)),
            "timetable_board_rows": list(timetable_board_rows)[:128],
        }
    if section_id in {"section.networkgraph.route", "section.mob.route_result"}:
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
        graph_row = _graph_row()
        edge_rows_by_id = dict(
            (str(edge.get("edge_id", "")).strip(), dict(edge))
            for edge in list(graph_row.get("edges") or [])
            if isinstance(edge, dict) and str(edge.get("edge_id", "")).strip()
        )
        guide_geometry_rows_by_id = _row_index((dict(state or {})).get("guide_geometries"), "geometry_id")
        geometry_metrics_by_id = _row_index((dict(state or {})).get("geometry_derived_metrics"), "geometry_id")
        spec_warning_edge_ids = []
        curvature_warning_edge_ids = []
        for edge_id in path_edge_ids:
            edge_row = dict(edge_rows_by_id.get(edge_id) or {})
            payload = dict(edge_row.get("payload") or {})
            geometry_id = str(payload.get("guide_geometry_id", "")).strip()
            geometry_row = dict(guide_geometry_rows_by_id.get(geometry_id) or {})
            metric_row = dict(geometry_metrics_by_id.get(geometry_id) or {})
            edge_spec_id = str(payload.get("spec_id", "")).strip()
            geometry_spec_id = str(geometry_row.get("spec_id", "")).strip()
            if (not edge_spec_id) and (not geometry_spec_id):
                spec_warning_edge_ids.append(edge_id)
            curvature_bands = _as_map(metric_row.get("curvature_bands"))
            high_band_count = int(max(0, _as_int(curvature_bands.get("high", 0), 0)))
            min_radius = int(max(0, _as_int(metric_row.get("min_curvature_radius_mm", 0), 0)))
            if high_band_count > 0 or (0 < min_radius <= int(_MOBILITY_CURVATURE_WARN_RADIUS_MM)):
                curvature_warning_edge_ids.append(edge_id)
        itinerary_id = str(route_payload.get("itinerary_id", "")).strip() or None
        speed_policy_id = str(route_payload.get("speed_policy_id", "")).strip() or None
        estimated_arrival_tick = (
            int(max(0, _as_int(route_payload.get("estimated_arrival_tick", 0), 0)))
            if route_payload.get("estimated_arrival_tick") is not None
            else None
        )
        per_edge_profile = [
            dict(item)
            for item in list(route_payload.get("per_edge_profile") or [])
            if isinstance(item, dict)
        ]
        warning_edge_ids = sorted(set(list(spec_warning_edge_ids) + list(curvature_warning_edge_ids)))
        return {
            "available": bool(route_payload),
            "path_node_ids": list(path_node_ids),
            "path_edge_ids": list(path_edge_ids),
            "total_cost": int(max(0, _as_int(route_payload.get("total_cost", 0), 0))),
            "route_policy_id": str(route_payload.get("route_policy_id", "")).strip(),
            "itinerary_id": itinerary_id,
            "speed_policy_id": speed_policy_id,
            "estimated_arrival_tick": estimated_arrival_tick,
            "curvature_warning_edge_ids": sorted(set(curvature_warning_edge_ids)),
            "curvature_warning_count": int(len(set(curvature_warning_edge_ids))),
            "spec_warning_edge_ids": sorted(set(spec_warning_edge_ids)),
            "spec_warning_count": int(len(set(spec_warning_edge_ids))),
            "warning_edge_ids": warning_edge_ids,
            "warning_count": int(len(warning_edge_ids)),
            "per_edge_profile": list(per_edge_profile)[:256],
        }
    if section_id == "section.mob.edge_occupancy":
        graph = _graph_row()
        edge_rows = sorted(
            [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, dict)],
            key=lambda item: str(item.get("edge_id", "")),
        )
        occupancy_rows_by_edge = _row_index((dict(state or {})).get("edge_occupancies"), "edge_id")
        edge_items: List[dict] = []
        over_capacity_edge_count = 0
        peak_ratio_permille = 0
        for edge in edge_rows:
            edge_id = str(edge.get("edge_id", "")).strip()
            if not edge_id:
                continue
            occupancy_row = dict(occupancy_rows_by_edge.get(edge_id) or {})
            payload = dict(edge.get("payload") or {})
            capacity_units = int(
                max(
                    1,
                    _as_int(
                        occupancy_row.get(
                            "capacity_units",
                            payload.get("capacity_units", edge.get("capacity", 1)),
                        ),
                        1,
                    ),
                )
            )
            current_occupancy = int(max(0, _as_int(occupancy_row.get("current_occupancy", 0), 0)))
            ratio_permille = int(
                max(
                    0,
                    _as_int(
                        (dict(occupancy_row.get("extensions") or {})).get(
                            "congestion_ratio_permille",
                            (int(current_occupancy) * 1000) // int(max(1, capacity_units)),
                        ),
                        0,
                    ),
                )
            )
            if int(ratio_permille) > 1000:
                over_capacity_edge_count += 1
            peak_ratio_permille = max(int(peak_ratio_permille), int(ratio_permille))
            edge_items.append(
                {
                    "edge_id": edge_id,
                    "capacity_units": int(capacity_units),
                    "current_occupancy": int(current_occupancy),
                    "congestion_ratio_permille": int(ratio_permille),
                    "congestion_ratio": float(ratio_permille) / 1000.0,
                    "over_capacity": bool(ratio_permille > 1000),
                }
            )
        return {
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "edge_count": int(len(edge_items)),
            "over_capacity_edge_count": int(over_capacity_edge_count),
            "peak_congestion_ratio_permille": int(peak_ratio_permille),
            "edges": list(edge_items)[:512],
        }
    if section_id == "section.mob.congestion_summary":
        edge_occ = _build_section_data(
            "section.mob.edge_occupancy",
            state=state,
            target_payload=target_payload,
            request=request,
            quant_step=quant_step,
            include_part_ids=include_part_ids,
            allow_hidden_state=allow_hidden_state,
        )
        edge_rows = [dict(item) for item in list((dict(edge_occ or {})).get("edges") or []) if isinstance(item, dict)]
        congested_edge_ids = sorted(
            str(item.get("edge_id", "")).strip()
            for item in edge_rows
            if str(item.get("edge_id", "")).strip() and int(max(0, _as_int(item.get("congestion_ratio_permille", 0), 0))) > 1000
        )
        travel_events = [dict(item) for item in list((dict(state or {})).get("travel_events") or []) if isinstance(item, dict)]
        delay_events = []
        for row in travel_events:
            if str(row.get("kind", "")).strip() != "delay":
                continue
            details = dict(row.get("details") or {})
            if str(details.get("reason", "")).strip() != "event.delay.congestion":
                continue
            delay_events.append(dict(row))
        delay_events = sorted(
            delay_events,
            key=lambda row: (
                _as_int(row.get("tick", 0), 0),
                str(row.get("event_id", "")),
            ),
        )
        last_tick = int(max(0, _as_int(request.get("tick", 0), 0)))
        latest_delay_events = [
            dict(row)
            for row in delay_events
            if int(max(0, _as_int(row.get("tick", 0), 0))) == int(last_tick)
        ]
        delayed_vehicle_ids = _sorted_unique_strings(
            [row.get("vehicle_id") for row in latest_delay_events]
        )
        total_delay_ticks = int(
            sum(
                int(max(0, _as_int((dict(row.get("details") or {})).get("delta_ticks", 0), 0)))
                for row in latest_delay_events
            )
        )
        runtime_state = dict((dict(state or {})).get("mobility_travel_runtime_state") or {})
        return {
            "graph_id": str((dict(edge_occ or {})).get("graph_id", "")).strip() or None,
            "edge_count": int(max(0, _as_int((dict(edge_occ or {})).get("edge_count", 0), 0))),
            "over_capacity_edge_count": int(max(0, _as_int((dict(edge_occ or {})).get("over_capacity_edge_count", 0), 0))),
            "peak_congestion_ratio_permille": int(
                max(0, _as_int((dict(edge_occ or {})).get("peak_congestion_ratio_permille", 0), 0))
            ),
            "congested_edge_ids": list(congested_edge_ids)[:256],
            "congested_edge_count": int(len(congested_edge_ids)),
            "congestion_policy_id": str(runtime_state.get("congestion_policy_id", "")).strip() or None,
            "delay_event_count": int(len(latest_delay_events)),
            "total_delay_ticks": int(total_delay_ticks),
            "delayed_vehicle_ids": list(delayed_vehicle_ids)[:256],
            "delay_status": "delayed" if latest_delay_events else "on_time",
        }
    if section_id == "section.signal.network_summary":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        signal_channels = [
            dict(item)
            for item in list((dict(state or {})).get("signal_channels") or (dict(state or {})).get("signal_channel_rows") or [])
            if isinstance(item, dict)
        ]
        signal_queues = [
            dict(item)
            for item in list((dict(state or {})).get("signal_transport_queue") or (dict(state or {})).get("signal_transport_queue_rows") or [])
            if isinstance(item, dict)
        ]
        signal_events = [
            dict(item)
            for item in list((dict(state or {})).get("message_delivery_events") or (dict(state or {})).get("message_delivery_event_rows") or [])
            if isinstance(item, dict)
        ]
        channel_rows = [
            row
            for row in list(signal_channels)
            if (not graph_id) or str(row.get("network_graph_id", "")).strip() == str(graph_id)
        ]
        channel_ids = set(str(row.get("channel_id", "")).strip() for row in channel_rows if str(row.get("channel_id", "")).strip())
        queue_rows = [row for row in signal_queues if str(row.get("channel_id", "")).strip() in channel_ids]
        event_rows = [
            row
            for row in signal_events
            if str((dict(row.get("extensions") or {})).get("channel_id", "")).strip() in channel_ids
        ]
        channel_type_counts: Dict[str, int] = {}
        for row in sorted(channel_rows, key=lambda item: str(item.get("channel_id", ""))):
            channel_type_id = str(row.get("channel_type_id", "")).strip() or "channel.unknown"
            channel_type_counts[channel_type_id] = _as_int(channel_type_counts.get(channel_type_id, 0), 0) + 1
        return {
            "graph_id": graph_id,
            "channel_count": int(len(channel_rows)),
            "queue_depth_total": int(len(queue_rows)),
            "delivery_event_count": int(len(event_rows)),
            "channel_type_counts": dict((key, channel_type_counts[key]) for key in sorted(channel_type_counts.keys())),
            "status": "degraded" if queue_rows else "stable",
        }
    if section_id == "section.signal.channel_queue_depth":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        signal_channels = [
            dict(item)
            for item in list((dict(state or {})).get("signal_channels") or (dict(state or {})).get("signal_channel_rows") or [])
            if isinstance(item, dict)
        ]
        signal_queues = [
            dict(item)
            for item in list((dict(state or {})).get("signal_transport_queue") or (dict(state or {})).get("signal_transport_queue_rows") or [])
            if isinstance(item, dict)
        ]
        channel_rows = [
            row
            for row in list(signal_channels)
            if (not graph_id) or str(row.get("network_graph_id", "")).strip() == str(graph_id)
        ]
        channel_ids = set(str(row.get("channel_id", "")).strip() for row in channel_rows if str(row.get("channel_id", "")).strip())
        queue_rows = [row for row in signal_queues if str(row.get("channel_id", "")).strip() in channel_ids]
        queue_by_channel: Dict[str, int] = {}
        queue_by_edge: Dict[str, int] = {}
        for row in sorted(queue_rows, key=lambda item: (str(item.get("channel_id", "")), str(item.get("envelope_id", "")), str(item.get("queue_key", "")))):
            channel_id = str(row.get("channel_id", "")).strip()
            if not channel_id:
                continue
            queue_by_channel[channel_id] = _as_int(queue_by_channel.get(channel_id, 0), 0) + 1
            extensions = dict(row.get("extensions") or {})
            edge_ids = _sorted_unique_strings(list(extensions.get("path_edge_ids") or []))
            if not edge_ids:
                edge_ids = [str(extensions.get("from_edge_id", "")).strip()] if str(extensions.get("from_edge_id", "")).strip() else []
            for edge_id in edge_ids:
                queue_by_edge[edge_id] = _as_int(queue_by_edge.get(edge_id, 0), 0) + 1
        edge_rows = []
        for edge_id in sorted(queue_by_edge.keys()):
            depth = int(max(0, _as_int(queue_by_edge.get(edge_id, 0), 0)))
            heat_bucket = "low"
            if depth >= 6:
                heat_bucket = "high"
            elif depth >= 3:
                heat_bucket = "medium"
            edge_rows.append(
                {
                    "edge_id": edge_id,
                    "queue_depth": int(depth),
                    "heat_bucket": heat_bucket,
                }
            )
        return {
            "graph_id": graph_id,
            "channel_count": int(len(channel_rows)),
            "queue_depth_total": int(len(queue_rows)),
            "channel_queue_depth_rows": sorted(
                [
                    {
                        "channel_id": channel_id,
                        "queue_depth": int(max(0, _as_int(queue_by_channel.get(channel_id, 0), 0))),
                    }
                    for channel_id in sorted(queue_by_channel.keys())
                ],
                key=lambda item: (str(item.get("channel_id", "")), int(max(0, _as_int(item.get("queue_depth", 0), 0)))),
            ),
            "edge_queue_depth_rows": list(edge_rows)[:512],
            "max_queue_depth": int(max([0] + [int(max(0, _as_int(value, 0))) for value in queue_by_channel.values()])),
        }
    if section_id == "section.signal.delivery_status":
        signal_events = [
            dict(item)
            for item in list((dict(state or {})).get("message_delivery_events") or (dict(state or {})).get("message_delivery_event_rows") or [])
            if isinstance(item, dict)
        ]
        sorted_events = sorted(
            signal_events,
            key=lambda row: (
                _as_int(row.get("delivered_tick", row.get("tick", 0)), 0),
                str(row.get("event_id", "")),
            ),
        )
        delivered_count = 0
        lost_count = 0
        corrupted_count = 0
        for row in sorted_events:
            state_token = str(row.get("delivery_state", "")).strip().lower()
            if state_token == "delivered":
                delivered_count += 1
            elif state_token == "corrupted":
                corrupted_count += 1
            else:
                lost_count += 1
        total = int(delivered_count + lost_count + corrupted_count)
        delivered_ratio_permille = int((1000 * delivered_count) // total) if total > 0 else 1000
        status = "ok"
        if delivered_ratio_permille < 700:
            status = "poor"
        elif delivered_ratio_permille < 900:
            status = "degraded"
        payload = {
            "event_count": int(total),
            "delivered_count": int(delivered_count),
            "lost_count": int(lost_count),
            "corrupted_count": int(corrupted_count),
            "delivered_ratio_permille": int(delivered_ratio_permille),
            "delivery_status": status,
        }
        if allow_hidden_state:
            payload["recent_events"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "envelope_id": str(row.get("envelope_id", "")).strip() or None,
                    "channel_id": str((dict(row.get("extensions") or {})).get("channel_id", "")).strip() or None,
                    "delivery_state": str(row.get("delivery_state", "")).strip() or "lost",
                    "delivered_tick": int(max(0, _as_int(row.get("delivered_tick", row.get("tick", 0)), 0))),
                }
                for row in list(sorted_events[-128:])
            ]
        return payload
    if section_id == "section.signal.quality_summary":
        tick = int(max(0, _as_int(request.get("tick", 0), 0)))
        signal_events = [
            dict(item)
            for item in list((dict(state or {})).get("message_delivery_events") or (dict(state or {})).get("message_delivery_event_rows") or [])
            if isinstance(item, dict)
        ]
        sorted_events = sorted(
            signal_events,
            key=lambda row: (
                _as_int(row.get("delivered_tick", row.get("tick", 0)), 0),
                str(row.get("event_id", "")),
            ),
        )
        window_start = int(max(0, tick - 256))
        window_events = [
            row
            for row in sorted_events
            if _as_int(row.get("delivered_tick", row.get("tick", 0)), 0) >= window_start
        ]
        delivered_count = 0
        lost_count = 0
        corrupted_count = 0
        loss_modifier_values = []
        channel_failure_counts: Dict[str, int] = {}
        channel_total_counts: Dict[str, int] = {}
        for row in window_events:
            state_token = str(row.get("delivery_state", "")).strip().lower()
            ext = dict(row.get("extensions") or {})
            channel_id = str(ext.get("channel_id", "")).strip() or "channel.unknown"
            channel_total_counts[channel_id] = _as_int(channel_total_counts.get(channel_id, 0), 0) + 1
            if state_token == "delivered":
                delivered_count += 1
            elif state_token == "corrupted":
                corrupted_count += 1
                channel_failure_counts[channel_id] = _as_int(channel_failure_counts.get(channel_id, 0), 0) + 1
            else:
                lost_count += 1
                channel_failure_counts[channel_id] = _as_int(channel_failure_counts.get(channel_id, 0), 0) + 1
            loss_modifier_values.append(
                int(max(0, _as_int(ext.get("field_loss_modifier_permille", 0), 0)))
            )
        event_count = int(delivered_count + lost_count + corrupted_count)
        delivered_ratio_permille = int((1000 * delivered_count) // event_count) if event_count > 0 else 1000
        avg_loss_modifier_permille = int(sum(loss_modifier_values) // max(1, len(loss_modifier_values)))
        jamming_rows = [
            dict(item)
            for item in list((dict(state or {})).get("signal_jamming_effect_rows") or (dict(state or {})).get("signal_jamming_effects") or [])
            if isinstance(item, dict)
        ]
        active_jamming_rows = []
        for row in sorted(jamming_rows, key=lambda item: str(item.get("effect_id", ""))):
            start_tick = int(max(0, _as_int(row.get("start_tick", 0), 0)))
            end_tick = int(max(start_tick, _as_int(row.get("end_tick", start_tick), start_tick)))
            if tick < start_tick or tick >= end_tick:
                continue
            active_jamming_rows.append(row)
        avg_jam_strength_permille = int(
            sum(int(max(0, _as_int(row.get("strength_modifier", 0), 0))) for row in active_jamming_rows)
            // max(1, len(active_jamming_rows))
        ) if active_jamming_rows else 0
        quality_bucket = "clear"
        if delivered_ratio_permille < 700 or avg_jam_strength_permille >= 700:
            quality_bucket = "poor"
        elif delivered_ratio_permille < 900 or avg_loss_modifier_permille >= 400:
            quality_bucket = "noisy"
        payload = {
            "tick_window_start": int(window_start),
            "event_count": int(event_count),
            "delivered_count": int(delivered_count),
            "lost_count": int(lost_count),
            "corrupted_count": int(corrupted_count),
            "delivered_ratio_permille": int(delivered_ratio_permille),
            "avg_loss_modifier_permille": int(avg_loss_modifier_permille),
            "active_jammer_count": int(len(active_jamming_rows)),
            "avg_jam_strength_permille": int(avg_jam_strength_permille),
            "quality_bucket": quality_bucket,
            "radio_static_indicator": ("high" if quality_bucket == "poor" else ("low" if quality_bucket == "noisy" else "none")),
            "line_noisy": bool(quality_bucket in {"noisy", "poor"}),
            "jammer_detected": bool(active_jamming_rows),
        }
        if allow_hidden_state:
            payload["channel_failure_rate_permille"] = dict(
                (
                    channel_id,
                    int(
                        (1000 * _as_int(channel_failure_counts.get(channel_id, 0), 0))
                        // max(1, _as_int(channel_total_counts.get(channel_id, 0), 0))
                    ),
                )
                for channel_id in sorted(channel_total_counts.keys())
            )
            payload["active_jamming_rows"] = [
                {
                    "effect_id": str(row.get("effect_id", "")).strip() or None,
                    "target_channel_id": str(row.get("target_channel_id", "")).strip() or None,
                    "strength_modifier": int(max(0, _as_int(row.get("strength_modifier", 0), 0))),
                    "start_tick": int(max(0, _as_int(row.get("start_tick", 0), 0))),
                    "end_tick": int(max(0, _as_int(row.get("end_tick", 0), 0))),
                }
                for row in active_jamming_rows[:128]
            ]
        return payload
    if section_id == "section.elec.local_panel_state":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        edge_status_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_edge_status_rows") or [])
            if isinstance(item, dict)
        ]
        fault_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_fault_states") or [])
            if isinstance(item, dict) and bool(item.get("active", False))
        ]
        protection_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_protection_devices") or [])
            if isinstance(item, dict)
        ]
        total_p = int(sum(max(0, _as_int(row.get("P", 0), 0)) for row in edge_status_rows))
        total_s = int(sum(max(0, _as_int(row.get("S", 0), 0)) for row in edge_status_rows))
        energized = bool(total_p > 0)
        tripped_count = int(
            sum(
                1
                for row in protection_rows
                if str((dict(row.get("extensions") or {})).get("breaker_state", "")).strip() == "tripped"
            )
        )
        active_fault_count = int(len(fault_rows))
        payload = {
            "graph_id": graph_id,
            "energized": bool(energized and tripped_count == 0),
            "active_power_p": int(total_p),
            "apparent_power_s": int(total_s),
            "tripped_count": int(tripped_count),
            "active_fault_count": int(active_fault_count),
            "panel_status": "tripped" if tripped_count > 0 else ("warning" if active_fault_count > 0 else ("energized" if energized else "deenergized")),
        }
        if allow_hidden_state:
            payload["edge_status_rows"] = [
                {
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "P": int(max(0, _as_int(row.get("P", 0), 0))),
                    "Q": int(max(0, _as_int(row.get("Q", 0), 0))),
                    "S": int(max(0, _as_int(row.get("S", 0), 0))),
                    "pf_permille": int(max(0, _as_int(row.get("pf_permille", 0), 0))),
                }
                for row in sorted(edge_status_rows, key=lambda item: str(item.get("edge_id", "")))[:128]
            ]
        return payload
    if section_id == "section.elec.device_states":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        graph_edge_ids = set(
            str(edge.get("edge_id", "")).strip()
            for edge in list(graph.get("edges") or [])
            if isinstance(edge, dict) and str(edge.get("edge_id", "")).strip()
        )
        protection_rows = sorted(
            [dict(item) for item in list((dict(state or {})).get("elec_protection_devices") or []) if isinstance(item, dict)],
            key=lambda item: str(item.get("device_id", "")),
        )
        explanation_rows = sorted(
            [dict(item) for item in list((dict(state or {})).get("elec_trip_explanations") or []) if isinstance(item, dict)],
            key=lambda item: (str(item.get("device_id", "")), str(item.get("explanation_id", ""))),
        )
        device_rows = []
        for row in protection_rows:
            device_id = str(row.get("device_id", "")).strip()
            if not device_id:
                continue
            attached_to = dict(row.get("attached_to") or {})
            edge_id = str(attached_to.get("edge_id", "")).strip()
            if graph_edge_ids and edge_id and edge_id not in graph_edge_ids:
                continue
            ext = dict(row.get("extensions") or {})
            device_rows.append(
                {
                    "device_id": device_id,
                    "device_kind_id": str(row.get("device_kind_id", "")).strip() or "breaker",
                    "edge_id": edge_id or None,
                    "channel_id": str(ext.get("channel_id", "")).strip() or None,
                    "breaker_state": str(ext.get("breaker_state", "closed")).strip() or "closed",
                    "loto_active": bool(ext.get("loto_active", False)),
                    "state_machine_id": str(row.get("state_machine_id", "")).strip() or None,
                }
            )
        payload = {
            "graph_id": graph_id,
            "device_count": int(len(device_rows)),
            "tripped_count": int(len([row for row in device_rows if str(row.get("breaker_state", "")).strip() == "tripped"])),
            "loto_active_count": int(len([row for row in device_rows if bool(row.get("loto_active", False))])),
            "trip_explanation_count": int(len(explanation_rows)),
        }
        if allow_hidden_state:
            payload["devices"] = list(device_rows)[:256]
            payload["trip_explanations"] = list(explanation_rows)[-128:]
        return payload
    if section_id == "section.elec.pf_summary":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        edge_status_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_edge_status_rows") or [])
            if isinstance(item, dict)
        ]
        total_p = int(sum(max(0, _as_int(row.get("P", 0), 0)) for row in edge_status_rows))
        total_s = int(sum(max(0, _as_int(row.get("S", 0), 0)) for row in edge_status_rows))
        aggregate_pf_permille = int((1000 * int(total_p)) // max(1, int(total_s))) if total_s > 0 else 0
        payload = {
            "graph_id": graph_id,
            "edge_count": int(len(edge_status_rows)),
            "active_power_p": int(total_p),
            "apparent_power_s": int(total_s),
            "aggregate_pf_permille": int(aggregate_pf_permille),
            "pf_bucket": (
                "good"
                if aggregate_pf_permille >= 950
                else ("fair" if aggregate_pf_permille >= 800 else ("poor" if aggregate_pf_permille > 0 else "none"))
            ),
        }
        if allow_hidden_state:
            payload["edges"] = [
                {
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "pf_permille": int(max(0, _as_int(row.get("pf_permille", 0), 0))),
                    "P": int(max(0, _as_int(row.get("P", 0), 0))),
                    "S": int(max(0, _as_int(row.get("S", 0), 0))),
                }
                for row in sorted(edge_status_rows, key=lambda item: str(item.get("edge_id", "")))[:256]
            ]
        return payload
    if section_id == "section.elec.loss_heat_summary":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        edge_status_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_edge_status_rows") or [])
            if isinstance(item, dict)
        ]
        total_heat_loss = int(sum(max(0, _as_int(row.get("heat_loss_stub", 0), 0)) for row in edge_status_rows))
        high_loss_edges = [
            dict(row)
            for row in sorted(edge_status_rows, key=lambda item: (int(max(0, _as_int(item.get("heat_loss_stub", 0), 0))), str(item.get("edge_id", ""))), reverse=True)
            if int(max(0, _as_int(row.get("heat_loss_stub", 0), 0))) > 0
        ]
        payload = {
            "graph_id": graph_id,
            "edge_count": int(len(edge_status_rows)),
            "heat_loss_total_stub": int(total_heat_loss),
            "high_loss_edge_count": int(len(high_loss_edges)),
            "loss_state": "high" if total_heat_loss >= 1000 else ("medium" if total_heat_loss >= 200 else ("low" if total_heat_loss > 0 else "none")),
        }
        if allow_hidden_state:
            payload["edges"] = [
                {
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "heat_loss_stub": int(max(0, _as_int(row.get("heat_loss_stub", 0), 0))),
                    "S": int(max(0, _as_int(row.get("S", 0), 0))),
                }
                for row in high_loss_edges[:256]
            ]
        return payload
    if section_id == "section.elec.fault_summary":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        graph_edge_ids = set(
            str(edge.get("edge_id", "")).strip()
            for edge in list(graph.get("edges") or [])
            if isinstance(edge, dict) and str(edge.get("edge_id", "")).strip()
        )
        fault_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_fault_states") or [])
            if isinstance(item, dict)
        ]
        active_rows = []
        for row in sorted(fault_rows, key=lambda item: (str(item.get("target_id", "")), str(item.get("fault_kind_id", "")), str(item.get("fault_id", "")))):
            if not bool(row.get("active", False)):
                continue
            target_kind = str(row.get("target_kind", "")).strip()
            target_id = str(row.get("target_id", "")).strip()
            if (not target_id) or (target_kind not in {"edge", "node", "device"}):
                continue
            if graph_edge_ids and target_kind == "edge" and target_id not in graph_edge_ids:
                continue
            active_rows.append(row)
        by_kind: Dict[str, int] = {}
        for row in active_rows:
            kind = str(row.get("fault_kind_id", "")).strip() or "fault.unknown"
            by_kind[kind] = _as_int(by_kind.get(kind, 0), 0) + 1
        total_severity = int(sum(max(0, _as_int(row.get("severity", 0), 0)) for row in active_rows))
        runtime_state = dict((dict(state or {})).get("elec_fault_runtime_state") or {})
        payload = {
            "graph_id": graph_id,
            "active_fault_count": int(len(active_rows)),
            "fault_kind_counts": dict((key, int(by_kind[key])) for key in sorted(by_kind.keys())),
            "ground_fault_count": int(_as_int(by_kind.get("fault.ground_fault", 0), 0)),
            "overcurrent_fault_count": int(_as_int(by_kind.get("fault.overcurrent", 0), 0)),
            "fault_severity_total": int(total_severity),
            "fault_state_hash_chain": str((dict(state or {})).get("fault_state_hash_chain", "")).strip() or None,
            "fault_budget_outcome": str(runtime_state.get("last_budget_outcome", "")).strip() or "complete",
        }
        if allow_hidden_state:
            payload["fault_rows"] = [
                {
                    "fault_id": str(row.get("fault_id", "")).strip(),
                    "fault_kind_id": str(row.get("fault_kind_id", "")).strip(),
                    "target_kind": str(row.get("target_kind", "")).strip(),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "severity": int(max(0, _as_int(row.get("severity", 0), 0))),
                    "detected_tick": int(max(0, _as_int(row.get("detected_tick", 0), 0))),
                }
                for row in active_rows[:256]
            ]
        return payload
    if section_id == "section.elec.protection_device_states":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        graph_edge_ids = set(
            str(edge.get("edge_id", "")).strip()
            for edge in list(graph.get("edges") or [])
            if isinstance(edge, dict) and str(edge.get("edge_id", "")).strip()
        )
        settings_by_id = _row_index((dict(state or {})).get("elec_protection_settings"), "settings_id")
        trip_events = [
            dict(item)
            for item in list((dict(state or {})).get("elec_trip_events") or [])
            if isinstance(item, dict)
        ]
        trip_event_ids = set(
            str((dict(row.get("details") or {})).get("device_id", "")).strip()
            for row in trip_events
            if str(row.get("status", "")).strip() == "trip_planned"
            and str((dict(row.get("details") or {})).get("device_id", "")).strip()
        )
        device_rows = []
        for row in sorted(
            [dict(item) for item in list((dict(state or {})).get("elec_protection_devices") or []) if isinstance(item, dict)],
            key=lambda item: str(item.get("device_id", "")),
        ):
            device_id = str(row.get("device_id", "")).strip()
            if not device_id:
                continue
            attached_to = dict(row.get("attached_to") or {})
            edge_id = str(attached_to.get("edge_id", "")).strip()
            if graph_edge_ids and edge_id and edge_id not in graph_edge_ids:
                continue
            ext = dict(row.get("extensions") or {})
            settings_id = str(row.get("settings_ref", "")).strip()
            settings_row = dict(settings_by_id.get(settings_id) or {})
            breaker_state = str(ext.get("breaker_state", "closed")).strip() or "closed"
            device_rows.append(
                {
                    "device_id": device_id,
                    "device_kind_id": str(row.get("device_kind_id", "")).strip() or "breaker",
                    "edge_id": edge_id or None,
                    "channel_id": str(ext.get("channel_id", "")).strip() or None,
                    "state_machine_id": str(row.get("state_machine_id", "")).strip() or None,
                    "breaker_state": breaker_state,
                    "loto_active": bool(ext.get("loto_active", False)),
                    "trip_planned": bool(device_id in trip_event_ids),
                    "settings_id": settings_id or None,
                    "trip_threshold_S": None if settings_row.get("trip_threshold_S") is None else int(max(0, _as_int(settings_row.get("trip_threshold_S", 0), 0))),
                    "gfci_threshold": None if settings_row.get("gfci_threshold") is None else int(max(0, _as_int(settings_row.get("gfci_threshold", 0), 0))),
                }
            )
        tripped_count = len([row for row in device_rows if str(row.get("breaker_state", "")).strip() == "tripped"])
        loto_count = len([row for row in device_rows if bool(row.get("loto_active", False))])
        payload = {
            "graph_id": graph_id,
            "device_count": int(len(device_rows)),
            "tripped_count": int(tripped_count),
            "loto_active_count": int(loto_count),
            "trip_event_hash_chain": str((dict(state or {})).get("trip_event_hash_chain", "")).strip() or None,
            "status": "tripped" if tripped_count > 0 else ("locked_out" if loto_count > 0 else "normal"),
        }
        if allow_hidden_state:
            payload["devices"] = list(device_rows)[:256]
        return payload
    if section_id == "section.elec.compliance_summary":
        graph = _graph_row()
        edge_rows = [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, dict)]
        edge_spec_missing = 0
        for edge_row in edge_rows:
            payload = dict(edge_row.get("payload") or {})
            if not str(payload.get("spec_id", "")).strip():
                edge_spec_missing += 1
        protection_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_protection_devices") or [])
            if isinstance(item, dict)
        ]
        protection_spec_missing = len(
            [
                row
                for row in protection_rows
                if not str(row.get("spec_id", "")).strip()
            ]
        )
        fault_rows = [
            dict(item)
            for item in list((dict(state or {})).get("elec_fault_states") or [])
            if isinstance(item, dict) and bool(item.get("active", False))
        ]
        compliance_ok = (edge_spec_missing == 0) and (protection_spec_missing == 0)
        payload = {
            "graph_id": str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None,
            "edge_count": int(len(edge_rows)),
            "edge_spec_missing_count": int(edge_spec_missing),
            "protection_device_count": int(len(protection_rows)),
            "protection_spec_missing_count": int(protection_spec_missing),
            "active_fault_count": int(len(fault_rows)),
            "compliance_state": "pass" if compliance_ok else "warn",
            "status": "compliant" if compliance_ok else "spec_missing",
        }
        if allow_hidden_state:
            payload["missing_edge_spec_ids"] = [
                str((dict(edge.get("payload") or {})).get("spec_id", "")).strip() or None
                for edge in edge_rows
                if not str((dict(edge.get("payload") or {})).get("spec_id", "")).strip()
            ][:64]
        return payload
    if section_id == "section.thermal.node_summary":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        rows = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_node_status_rows") or [])
            if isinstance(item, dict)
        ]
        total_energy = int(sum(max(0, _as_int(row.get("thermal_energy", 0), 0)) for row in rows))
        avg_temp = int(
            (sum(_as_int(row.get("temperature", 0), 0) for row in rows) // max(1, len(rows)))
            if rows
            else 0
        )
        max_temp = int(max([_as_int(row.get("temperature", 0), 0) for row in rows], default=0))
        payload = {
            "graph_id": graph_id,
            "node_count": int(len(rows)),
            "total_thermal_energy": int(total_energy),
            "average_temperature": int(avg_temp),
            "max_temperature": int(max_temp),
            "thermal_network_hash": str((dict(state or {})).get("thermal_network_hash", "")).strip() or None,
        }
        if allow_hidden_state:
            payload["nodes"] = [
                {
                    "node_id": str(row.get("node_id", "")).strip(),
                    "node_kind": str(row.get("node_kind", "")).strip() or None,
                    "temperature": int(_as_int(row.get("temperature", 0), 0)),
                    "thermal_energy": int(max(0, _as_int(row.get("thermal_energy", 0), 0))),
                    "heat_input": int(max(0, _as_int(row.get("heat_input", 0), 0))),
                }
                for row in sorted(rows, key=lambda item: str(item.get("node_id", "")))[:256]
            ]
        return payload
    if section_id == "section.thermal.edge_summary":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        rows = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_edge_status_rows") or [])
            if isinstance(item, dict)
        ]
        total_transfer = int(sum(max(0, _as_int(row.get("heat_transfer", 0), 0)) for row in rows))
        payload = {
            "graph_id": graph_id,
            "edge_count": int(len(rows)),
            "total_heat_transfer": int(total_transfer),
            "active_edge_count": int(
                len([row for row in rows if int(max(0, _as_int(row.get("heat_transfer", 0), 0))) > 0])
            ),
            "budget_outcome": str((dict(state or {})).get("thermal_budget_outcome", "")).strip()
            or str((dict((dict(state or {})).get("thermal_runtime_state") or {})).get("last_budget_outcome", "")).strip()
            or "complete",
        }
        if allow_hidden_state:
            payload["edges"] = [
                {
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "from_node_id": str(row.get("effective_from_node_id", row.get("from_node_id", ""))).strip() or None,
                    "to_node_id": str(row.get("effective_to_node_id", row.get("to_node_id", ""))).strip() or None,
                    "heat_transfer": int(max(0, _as_int(row.get("heat_transfer", 0), 0))),
                    "channel_id": str(row.get("channel_id", "")).strip() or None,
                }
                for row in sorted(rows, key=lambda item: str(item.get("edge_id", "")))[:256]
            ]
        return payload
    if section_id == "section.thermal.overheat_risks":
        graph = _graph_row()
        graph_id = str(graph.get("graph_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        hazard_rows = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_hazard_rows") or (dict(state or {})).get("hazard_rows") or [])
            if isinstance(item, dict) and str(item.get("hazard_type_id", "")).strip() == "hazard.overheat"
        ]
        safety_rows = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_safety_event_rows") or (dict(state or {})).get("safety_event_rows") or [])
            if isinstance(item, dict) and str(item.get("pattern_id", "")).strip() == "safety.overtemp_trip"
        ]
        payload = {
            "graph_id": graph_id,
            "overheat_hazard_count": int(len(hazard_rows)),
            "overtemp_trip_count": int(len(safety_rows)),
            "overheat_event_hash_chain": str((dict(state or {})).get("overheat_event_hash_chain", "")).strip() or None,
            "risk_state": "critical" if hazard_rows else "normal",
        }
        if allow_hidden_state:
            payload["hazards"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip(),
                    "accumulated_value": int(max(0, _as_int(row.get("accumulated_value", 0), 0))),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
                for row in sorted(hazard_rows, key=lambda item: str(item.get("target_id", "")))[:256]
            ]
            payload["safety_events"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_ids": [str(token).strip() for token in list(row.get("target_ids") or []) if str(token).strip()],
                }
                for row in sorted(safety_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.thermal.phase_states":
        batches = [
            dict(item)
            for item in list((dict(state or {})).get("material_batches") or [])
            if isinstance(item, dict)
        ]
        phase_events = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_phase_events") or [])
            if isinstance(item, dict)
        ]
        phase_counts: Dict[str, int] = {}
        for batch in sorted(batches, key=lambda item: str(item.get("batch_id", ""))):
            phase_tag = str((dict(batch.get("extensions") or {})).get("phase_tag", "")).strip() or "unknown"
            phase_counts[phase_tag] = _as_int(phase_counts.get(phase_tag, 0), 0) + 1
        payload = {
            "batch_count": int(len(batches)),
            "phase_counts": dict((key, int(phase_counts[key])) for key in sorted(phase_counts.keys())),
            "phase_event_count": int(len(phase_events)),
        }
        if allow_hidden_state:
            payload["recent_events"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "batch_id": str(row.get("batch_id", "")).strip() or None,
                    "from_phase": str(row.get("from_phase", "")).strip() or None,
                    "to_phase": str(row.get("to_phase", "")).strip() or None,
                }
                for row in sorted(phase_events, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[-128:]
            ]
        return payload
    if section_id == "section.thermal.cure_progress":
        cure_rows = [
            dict(item)
            for item in list((dict(state or {})).get("cure_states") or [])
            if isinstance(item, dict)
        ]
        avg_permille = int(
            sum(int(max(0, min(1000, _as_int(row.get("cure_progress", 0), 0)))) for row in cure_rows) // max(1, len(cure_rows))
        ) if cure_rows else 0
        defect_count = len(
            [
                row for row in cure_rows
                if list(row.get("defect_flags") or [])
            ]
        )
        payload = {
            "target_count": int(len(cure_rows)),
            "average_progress_permille": int(avg_permille),
            "average_progress_percent": int((avg_permille * 100) // 1000),
            "defect_target_count": int(defect_count),
        }
        if allow_hidden_state:
            payload["targets"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip(),
                    "cure_progress_permille": int(max(0, min(1000, _as_int(row.get("cure_progress", 0), 0)))),
                    "defect_flags": _sorted_unique_strings(list(row.get("defect_flags") or [])),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
                for row in sorted(cure_rows, key=lambda item: str(item.get("target_id", "")))[:256]
            ]
        return payload
    if section_id == "section.thermal.insulation_effects":
        edge_rows = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_edge_status_rows") or [])
            if isinstance(item, dict)
        ]
        tracked = []
        for row in sorted(edge_rows, key=lambda item: str(item.get("edge_id", ""))):
            base_conductance = int(max(0, _as_int(row.get("base_conductance_value", row.get("conductance_value", 0)), 0)))
            effective_conductance = int(max(0, _as_int(row.get("effective_conductance_value", base_conductance), base_conductance)))
            factor = int(max(0, _as_int(row.get("insulation_factor_permille", 1000), 1000)))
            if (base_conductance <= 0) and (effective_conductance <= 0):
                continue
            tracked.append(
                {
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "base_conductance_value": int(base_conductance),
                    "effective_conductance_value": int(effective_conductance),
                    "insulation_factor_permille": int(factor),
                }
            )
        payload = {
            "insulated_edge_count": int(len(tracked)),
            "average_factor_permille": int(
                (sum(int(row.get("insulation_factor_permille", 1000)) for row in tracked) // max(1, len(tracked)))
                if tracked
                else 1000
            ),
        }
        if allow_hidden_state:
            payload["edges"] = list(tracked)[:256]
        return payload
    if section_id == "section.thermal.ambient_exchange_summary":
        runtime_state = dict((dict(state or {})).get("thermal_runtime_state") or {})
        ambient_rows = [
            dict(item)
            for item in list(
                (dict(state or {})).get("thermal_ambient_exchange_rows")
                or (dict(state or {})).get("ambient_exchange_rows")
                or runtime_state.get("ambient_exchange_rows")
                or []
            )
            if isinstance(item, dict)
        ]
        radiator_rows = [
            dict(item)
            for item in list(
                (dict(state or {})).get("thermal_radiator_exchange_rows")
                or (dict(state or {})).get("radiator_exchange_rows")
                or runtime_state.get("radiator_exchange_rows")
                or []
            )
            if isinstance(item, dict)
        ]
        combined_rows = sorted(
            [dict(item) for item in list(ambient_rows) + list(radiator_rows)],
            key=lambda item: (str(item.get("node_id", "")), str(item.get("binding_id", ""))),
        )
        temp_values = [
            int(_as_int(row.get("ambient_temperature", 0), 0))
            for row in combined_rows
            if row.get("ambient_temperature") is not None
        ]
        total_exchange = int(sum(max(0, _as_int(row.get("heat_exchange", 0), 0)) for row in combined_rows))
        total_delta_energy = int(sum(_as_int(row.get("delta_thermal_energy", 0), 0) for row in combined_rows))
        payload = {
            "ambient_row_count": int(len(ambient_rows)),
            "radiator_row_count": int(len(radiator_rows)),
            "exchange_row_count": int(len(combined_rows)),
            "total_heat_exchange": int(total_exchange),
            "net_delta_thermal_energy": int(total_delta_energy),
            "average_ambient_temperature": int(
                (sum(temp_values) // max(1, len(temp_values)))
                if temp_values
                else 0
            ),
            "ambient_eval_stride": int(
                max(
                    1,
                    _as_int(
                        (dict(state or {})).get("ambient_eval_stride", runtime_state.get("ambient_eval_stride", 1)),
                        1,
                    ),
                )
            ),
            "ambient_deferred_count": int(
                max(
                    0,
                    _as_int(
                        (dict(state or {})).get("ambient_deferred_count", runtime_state.get("ambient_deferred_count", 0)),
                        0,
                    ),
                )
            ),
            "ambient_exchange_hash": str(
                (dict(state or {})).get("ambient_exchange_hash", runtime_state.get("ambient_exchange_hash", ""))
            ).strip()
            or None,
        }
        if allow_hidden_state:
            payload["ambient_rows"] = [
                {
                    "node_id": str(row.get("node_id", "")).strip(),
                    "heat_exchange": int(max(0, _as_int(row.get("heat_exchange", 0), 0))),
                    "delta_thermal_energy": int(_as_int(row.get("delta_thermal_energy", 0), 0)),
                    "node_temperature": int(_as_int(row.get("node_temperature", 0), 0)),
                    "ambient_temperature": int(_as_int(row.get("ambient_temperature", 0), 0)),
                }
                for row in sorted(ambient_rows, key=lambda item: (str(item.get("node_id", "")), str(item.get("binding_id", ""))))[:256]
            ]
            payload["radiator_rows"] = [
                {
                    "node_id": str(row.get("node_id", "")).strip(),
                    "radiator_profile_id": str(row.get("radiator_profile_id", "")).strip() or None,
                    "forced_cooling_on": bool(row.get("forced_cooling_on", False)),
                    "heat_exchange": int(max(0, _as_int(row.get("heat_exchange", 0), 0))),
                    "delta_thermal_energy": int(_as_int(row.get("delta_thermal_energy", 0), 0)),
                }
                for row in sorted(radiator_rows, key=lambda item: (str(item.get("node_id", "")), str(item.get("binding_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.thermal.radiator_efficiency":
        runtime_state = dict((dict(state or {})).get("thermal_runtime_state") or {})
        radiator_rows = [
            dict(item)
            for item in list(
                (dict(state or {})).get("thermal_radiator_exchange_rows")
                or (dict(state or {})).get("radiator_exchange_rows")
                or runtime_state.get("radiator_exchange_rows")
                or []
            )
            if isinstance(item, dict)
        ]
        forced_on_count = len([row for row in radiator_rows if bool(row.get("forced_cooling_on", False))])
        passive_count = int(max(0, len(radiator_rows) - forced_on_count))
        total_exchange = int(sum(max(0, _as_int(row.get("heat_exchange", 0), 0)) for row in radiator_rows))
        efficiency_terms = []
        for row in sorted(radiator_rows, key=lambda item: (str(item.get("node_id", "")), str(item.get("binding_id", "")))):
            delta_temp = abs(_as_int(row.get("node_temperature", 0), 0) - _as_int(row.get("ambient_temperature", 0), 0))
            if delta_temp <= 0:
                continue
            efficiency_terms.append(
                int((max(0, _as_int(row.get("heat_exchange", 0), 0)) * 1000) // max(1, delta_temp))
            )
        avg_efficiency_permille = int(
            (sum(efficiency_terms) // max(1, len(efficiency_terms)))
            if efficiency_terms
            else 0
        )
        payload = {
            "radiator_count": int(len(radiator_rows)),
            "forced_cooling_on_count": int(forced_on_count),
            "passive_count": int(passive_count),
            "total_heat_exchange": int(total_exchange),
            "average_exchange_per_delta_temp_permille": int(avg_efficiency_permille),
            "status": "forced" if forced_on_count > 0 else ("passive" if radiator_rows else "none"),
        }
        if allow_hidden_state:
            payload["radiators"] = [
                {
                    "node_id": str(row.get("node_id", "")).strip(),
                    "radiator_profile_id": str(row.get("radiator_profile_id", "")).strip() or None,
                    "forced_cooling_on": bool(row.get("forced_cooling_on", False)),
                    "node_temperature": int(_as_int(row.get("node_temperature", 0), 0)),
                    "ambient_temperature": int(_as_int(row.get("ambient_temperature", 0), 0)),
                    "heat_exchange": int(max(0, _as_int(row.get("heat_exchange", 0), 0))),
                    "delta_thermal_energy": int(_as_int(row.get("delta_thermal_energy", 0), 0)),
                }
                for row in sorted(radiator_rows, key=lambda item: (str(item.get("node_id", "")), str(item.get("binding_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.thermal.fire_states":
        runtime_state = dict((dict(state or {})).get("thermal_runtime_state") or {})
        fire_rows = [
            dict(item)
            for item in list(
                (dict(state or {})).get("thermal_fire_state_rows")
                or (dict(state or {})).get("fire_state_rows")
                or runtime_state.get("fire_state_rows")
                or []
            )
            if isinstance(item, dict)
        ]
        active_rows = [row for row in fire_rows if bool(row.get("active", False))]
        total_fuel_remaining = int(sum(max(0, _as_int(row.get("fuel_remaining", 0), 0)) for row in fire_rows))
        payload = {
            "fire_state_count": int(len(fire_rows)),
            "active_fire_count": int(len(active_rows)),
            "total_fuel_remaining": int(total_fuel_remaining),
            "fire_state_hash_chain": str(
                (dict(state or {})).get("fire_state_hash_chain", runtime_state.get("fire_state_hash_chain", ""))
            ).strip()
            or None,
        }
        if allow_hidden_state:
            payload["fire_states"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "active": bool(row.get("active", False)),
                    "fuel_remaining": int(max(0, _as_int(row.get("fuel_remaining", 0), 0))),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
                for row in sorted(fire_rows, key=lambda item: str(item.get("target_id", "")))[:256]
            ]
        return payload
    if section_id == "section.thermal.runaway_events":
        runtime_state = dict((dict(state or {})).get("thermal_runtime_state") or {})
        fire_event_rows = [
            dict(item)
            for item in list(
                (dict(state or {})).get("thermal_fire_event_rows")
                or (dict(state or {})).get("fire_event_rows")
                or runtime_state.get("fire_event_rows")
                or []
            )
            if isinstance(item, dict)
        ]
        runaway_rows = [
            dict(item)
            for item in list(
                (dict(state or {})).get("thermal_safety_event_rows")
                or (dict(state or {})).get("safety_event_rows")
                or runtime_state.get("safety_event_rows")
                or []
            )
            if isinstance(item, dict) and str(item.get("pattern_id", "")).strip() == "safety.thermal_runaway"
        ]
        started_count = len(
            [
                row
                for row in fire_event_rows
                if str(row.get("event_type", "")).strip() in {"event.fire_started", "event.fire_spread_started"}
            ]
        )
        spread_count = len(
            [
                row
                for row in fire_event_rows
                if str(row.get("event_type", "")).strip() == "event.fire_spread_started"
            ]
        )
        payload = {
            "fire_event_count": int(len(fire_event_rows)),
            "fire_started_count": int(started_count),
            "fire_spread_count": int(spread_count),
            "runaway_event_count": int(len(runaway_rows)),
            "ignition_event_hash_chain": str(
                (dict(state or {})).get("ignition_event_hash_chain", runtime_state.get("ignition_event_hash_chain", ""))
            ).strip()
            or None,
            "fire_spread_hash_chain": str(
                (dict(state or {})).get("fire_spread_hash_chain", runtime_state.get("fire_spread_hash_chain", ""))
            ).strip()
            or None,
            "runaway_event_hash_chain": str(
                (dict(state or {})).get("runaway_event_hash_chain", runtime_state.get("runaway_event_hash_chain", ""))
            ).strip()
            or None,
        }
        if allow_hidden_state:
            payload["runaway_events"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_ids": [str(token).strip() for token in list(row.get("target_ids") or []) if str(token).strip()],
                    "pattern_id": str(row.get("pattern_id", "")).strip() or None,
                }
                for row in sorted(runaway_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[:256]
            ]
            payload["fire_events"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "event_type": str(row.get("event_type", "")).strip() or None,
                    "fuel_after": int(max(0, _as_int(row.get("fuel_after", 0), 0))),
                    "heat_emission": int(max(0, _as_int(row.get("heat_emission", 0), 0))),
                    "pollutant_emission": int(max(0, _as_int(row.get("pollutant_emission", 0), 0))),
                }
                for row in sorted(fire_event_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.chem.fuel_levels":
        fire_rows = [
            dict(item)
            for item in list((dict(state or {})).get("thermal_fire_state_rows") or (dict(state or {})).get("fire_state_rows") or [])
            if isinstance(item, dict)
        ]
        species_rows = [
            dict(item)
            for item in list((dict(state or {})).get("chem_species_pool_rows") or [])
            if isinstance(item, dict)
        ]
        fuel_rows = [
            row
            for row in species_rows
            if str(row.get("material_id", "")).strip().startswith("material.fuel")
            or str(row.get("material_id", "")).strip().endswith("_fuel_stub")
        ]
        total_fuel_remaining = int(sum(max(0, _as_int(row.get("fuel_remaining", 0), 0)) for row in fire_rows))
        pool_fuel_mass = int(sum(max(0, _as_int(row.get("mass_value", 0), 0)) for row in fuel_rows))
        payload = {
            "active_fire_count": int(len([row for row in fire_rows if bool(row.get("active", False))])),
            "fire_fuel_remaining_total": int(total_fuel_remaining),
            "species_pool_fuel_mass_total": int(pool_fuel_mass),
            "species_pool_fuel_entry_count": int(len(fuel_rows)),
        }
        if allow_hidden_state:
            payload["fire_states"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "fuel_remaining": int(max(0, _as_int(row.get("fuel_remaining", 0), 0))),
                    "active": bool(row.get("active", False)),
                }
                for row in sorted(fire_rows, key=lambda item: str(item.get("target_id", "")))[:256]
            ]
            payload["species_pool_rows"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "material_id": str(row.get("material_id", "")).strip() or None,
                    "mass_value": int(max(0, _as_int(row.get("mass_value", 0), 0))),
                }
                for row in sorted(fuel_rows, key=lambda item: (str(item.get("target_id", "")), str(item.get("material_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.chem.energy_output":
        combustion_rows = [
            dict(item)
            for item in list((dict(state or {})).get("combustion_event_rows") or [])
            if isinstance(item, dict)
        ]
        total_chemical = int(sum(max(0, _as_int(row.get("chemical_energy_in", 0), 0)) for row in combustion_rows))
        total_thermal = int(sum(max(0, _as_int(row.get("thermal_energy_out", 0), 0)) for row in combustion_rows))
        total_electrical = int(sum(max(0, _as_int(row.get("electrical_energy_out", 0), 0)) for row in combustion_rows))
        total_irreversibility = int(sum(max(0, _as_int(row.get("irreversibility_loss", 0), 0)) for row in combustion_rows))
        payload = {
            "combustion_event_count": int(len(combustion_rows)),
            "total_chemical_energy_in": int(total_chemical),
            "total_thermal_energy_out": int(total_thermal),
            "total_electrical_energy_out": int(total_electrical),
            "total_irreversibility_loss": int(total_irreversibility),
            "combustion_hash_chain": str((dict(state or {})).get("combustion_hash_chain", "")).strip() or None,
            "energy_ledger_hash_chain": str((dict(state or {})).get("energy_ledger_hash_chain", "")).strip() or None,
        }
        if allow_hidden_state:
            payload["rows"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "reaction_id": str(row.get("reaction_id", "")).strip() or None,
                    "chemical_energy_in": int(max(0, _as_int(row.get("chemical_energy_in", 0), 0))),
                    "thermal_energy_out": int(max(0, _as_int(row.get("thermal_energy_out", 0), 0))),
                    "electrical_energy_out": int(max(0, _as_int(row.get("electrical_energy_out", 0), 0))),
                }
                for row in sorted(combustion_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.chem.emissions":
        emission_rows = [
            dict(item)
            for item in list((dict(state or {})).get("combustion_emission_rows") or (dict(state or {})).get("chem_emission_pool_rows") or [])
            if isinstance(item, dict)
        ]
        by_material: Dict[str, int] = {}
        for row in emission_rows:
            material_id = str(row.get("material_id", "")).strip() or "material.pollutant_coarse_stub"
            by_material[material_id] = _as_int(by_material.get(material_id, 0), 0) + int(max(0, _as_int(row.get("mass_value", 0), 0)))
        payload = {
            "emission_event_count": int(len(emission_rows)),
            "total_emission_mass": int(sum(int(value) for value in by_material.values())),
            "material_totals": dict((key, int(by_material[key])) for key in sorted(by_material.keys())),
            "emission_hash_chain": str((dict(state or {})).get("emission_hash_chain", "")).strip() or None,
        }
        if allow_hidden_state:
            payload["rows"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "material_id": str(row.get("material_id", "")).strip() or None,
                    "mass_value": int(max(0, _as_int(row.get("mass_value", 0), 0))),
                    "source_reaction_id": str(row.get("source_reaction_id", "")).strip() or None,
                }
                for row in sorted(emission_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.chem.efficiency":
        combustion_rows = [
            dict(item)
            for item in list((dict(state or {})).get("combustion_event_rows") or [])
            if isinstance(item, dict)
        ]
        eff_values = [int(max(0, min(1000, _as_int(row.get("efficiency_permille", 0), 0)))) for row in combustion_rows]
        low_eff_threshold = int(max(0, _as_int(request.get("low_eff_threshold_permille", 700), 700)))
        low_eff_count = int(len([value for value in eff_values if value > 0 and value < low_eff_threshold]))
        payload = {
            "efficiency_sample_count": int(len(eff_values)),
            "avg_efficiency_permille": int(sum(eff_values) // len(eff_values)) if eff_values else 0,
            "min_efficiency_permille": int(min(eff_values)) if eff_values else 0,
            "max_efficiency_permille": int(max(eff_values)) if eff_values else 0,
            "low_efficiency_event_count": int(low_eff_count),
            "low_efficiency_threshold_permille": int(low_eff_threshold),
        }
        if allow_hidden_state:
            payload["rows"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "reaction_id": str(row.get("reaction_id", "")).strip() or None,
                    "efficiency_permille": int(max(0, min(1000, _as_int(row.get("efficiency_permille", 0), 0)))),
                    "irreversibility_loss": int(max(0, _as_int(row.get("irreversibility_loss", 0), 0))),
                }
                for row in sorted(combustion_rows, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))))[:256]
            ]
        return payload
    if section_id == "section.signal.inbox_summary":
        receipts = [
            dict(item)
            for item in list((dict(state or {})).get("knowledge_receipts") or (dict(state or {})).get("knowledge_receipt_rows") or [])
            if isinstance(item, dict)
        ]
        target_subject_id = str(request.get("subject_id", "")).strip() or str(request.get("target_id", "")).strip()
        filtered = [
            row
            for row in receipts
            if (not target_subject_id) or str(row.get("subject_id", "")).strip() == target_subject_id
        ]
        artifact_ids = _sorted_unique_strings([row.get("artifact_id") for row in filtered])
        trust_values = [float(dict(row).get("trust_weight", 1.0)) for row in filtered]
        avg_trust_permille = int(
            sum(int(max(0, min(1000, int(float(value) * 1000)))) for value in trust_values) // max(1, len(trust_values))
        ) if trust_values else 1000
        payload = {
            "subject_id": target_subject_id or None,
            "receipt_count": int(len(filtered)),
            "artifact_count": int(len(artifact_ids)),
            "avg_trust_permille": int(avg_trust_permille),
            "verification_state_counts": {},
        }
        by_verification: Dict[str, int] = {}
        for row in sorted(filtered, key=lambda item: (_as_int(item.get("acquired_tick", 0), 0), str(item.get("receipt_id", "")))):
            verification_state = str(row.get("verification_state", "unverified")).strip() or "unverified"
            by_verification[verification_state] = _as_int(by_verification.get(verification_state, 0), 0) + 1
        payload["verification_state_counts"] = dict((key, int(by_verification[key])) for key in sorted(by_verification.keys()))
        if allow_hidden_state:
            payload["recent_receipts"] = [
                {
                    "receipt_id": str(row.get("receipt_id", "")).strip(),
                    "subject_id": str(row.get("subject_id", "")).strip() or None,
                    "artifact_id": str(row.get("artifact_id", "")).strip() or None,
                    "acquired_tick": int(max(0, _as_int(row.get("acquired_tick", 0), 0))),
                    "trust_weight": float(row.get("trust_weight", 1.0)),
                    "verification_state": str(row.get("verification_state", "unverified")).strip() or "unverified",
                }
                for row in sorted(
                    filtered,
                    key=lambda item: (
                        _as_int(item.get("acquired_tick", 0), 0),
                        str(item.get("receipt_id", "")),
                    ),
                )[-128:]
            ]
        return payload
    if section_id == "section.inbox.acceptance_summary":
        receipts = [
            dict(item)
            for item in list((dict(state or {})).get("knowledge_receipts") or (dict(state or {})).get("knowledge_receipt_rows") or [])
            if isinstance(item, dict)
        ]
        target_subject_id = str(request.get("subject_id", "")).strip() or str(request.get("target_id", "")).strip()
        filtered = [
            row
            for row in receipts
            if (not target_subject_id) or str(row.get("subject_id", "")).strip() == target_subject_id
        ]
        accepted_count = 0
        untrusted_count = 0
        unknown_count = 0
        confidence_counts: Dict[str, int] = {}
        for row in sorted(filtered, key=lambda item: (_as_int(item.get("acquired_tick", 0), 0), str(item.get("receipt_id", "")))):
            ext = dict(row.get("extensions") or {})
            trust_weight = float(row.get("trust_weight", 1.0))
            threshold = float(ext.get("acceptance_threshold", 0.5))
            accepted = bool(ext.get("accepted", trust_weight >= threshold))
            confidence_tag = str(ext.get("confidence_tag", "")).strip().lower()
            if not confidence_tag:
                confidence_tag = "accepted" if accepted else "untrusted"
            confidence_counts[confidence_tag] = _as_int(confidence_counts.get(confidence_tag, 0), 0) + 1
            if accepted:
                accepted_count += 1
            elif confidence_tag == "untrusted":
                untrusted_count += 1
            else:
                unknown_count += 1
        total = int(len(filtered))
        payload = {
            "subject_id": target_subject_id or None,
            "receipt_count": int(total),
            "accepted_count": int(accepted_count),
            "untrusted_count": int(untrusted_count),
            "unknown_count": int(unknown_count),
            "accepted_ratio_permille": int((1000 * accepted_count) // total) if total > 0 else 0,
            "confidence_counts": dict((key, int(confidence_counts[key])) for key in sorted(confidence_counts.keys())),
        }
        if allow_hidden_state:
            payload["recent_acceptance"] = [
                {
                    "receipt_id": str(row.get("receipt_id", "")).strip(),
                    "artifact_id": str(row.get("artifact_id", "")).strip() or None,
                    "acquired_tick": int(max(0, _as_int(row.get("acquired_tick", 0), 0))),
                    "trust_weight": float(row.get("trust_weight", 1.0)),
                    "accepted": bool(dict(row.get("extensions") or {}).get("accepted", False)),
                    "confidence_tag": str(dict(row.get("extensions") or {}).get("confidence_tag", "")).strip() or None,
                    "belief_policy_id": str(dict(row.get("extensions") or {}).get("belief_policy_id", "")).strip() or None,
                }
                for row in sorted(
                    filtered,
                    key=lambda item: (
                        _as_int(item.get("acquired_tick", 0), 0),
                        str(item.get("receipt_id", "")),
                    ),
                )[-128:]
            ]
        return payload
    if section_id == "section.trust.edges_summary":
        trust_rows = [
            dict(item)
            for item in list((dict(state or {})).get("trust_edge_rows") or (dict(state or {})).get("signal_trust_edge_rows") or [])
            if isinstance(item, dict)
        ]
        subject_id = str(request.get("subject_id", "")).strip() or str(request.get("target_id", "")).strip()
        filtered = []
        for row in sorted(
            trust_rows,
            key=lambda item: (
                str(item.get("from_subject_id", "")),
                str(item.get("to_subject_id", "")),
            ),
        ):
            from_subject_id = str(row.get("from_subject_id", "")).strip()
            to_subject_id = str(row.get("to_subject_id", "")).strip()
            if not from_subject_id or not to_subject_id:
                continue
            if subject_id and subject_id not in {from_subject_id, to_subject_id}:
                continue
            filtered.append(row)
        trust_permille = [
            int(max(0, min(1000, int(float(dict(row).get("trust_weight", 0.5)) * 1000))))
            for row in filtered
        ]
        avg_trust_permille = int(sum(trust_permille) // max(1, len(trust_permille))) if trust_permille else 500
        outgoing_count = int(
            len([row for row in filtered if str(dict(row).get("from_subject_id", "")).strip() == subject_id])
        ) if subject_id else 0
        incoming_count = int(
            len([row for row in filtered if str(dict(row).get("to_subject_id", "")).strip() == subject_id])
        ) if subject_id else 0
        payload = {
            "subject_id": subject_id or None,
            "edge_count": int(len(filtered)),
            "avg_trust_permille": int(avg_trust_permille),
            "outgoing_edge_count": int(outgoing_count),
            "incoming_edge_count": int(incoming_count),
        }
        if allow_hidden_state:
            payload["edges"] = [
                {
                    "from_subject_id": str(row.get("from_subject_id", "")).strip() or None,
                    "to_subject_id": str(row.get("to_subject_id", "")).strip() or None,
                    "trust_weight": float(row.get("trust_weight", 0.5)),
                    "evidence_count": int(max(0, _as_int(row.get("evidence_count", 0), 0))),
                    "last_updated_tick": int(max(0, _as_int(row.get("last_updated_tick", 0), 0))),
                }
                for row in list(filtered[:256])
            ]
        return payload
    if section_id == "section.signal.sent_messages":
        envelopes = [
            dict(item)
            for item in list((dict(state or {})).get("signal_message_envelopes") or (dict(state or {})).get("signal_message_envelope_rows") or [])
            if isinstance(item, dict)
        ]
        sender_subject_id = str(request.get("subject_id", "")).strip() or str(request.get("target_id", "")).strip()
        filtered = [
            row
            for row in envelopes
            if (not sender_subject_id) or str(row.get("sender_subject_id", "")).strip() == sender_subject_id
        ]
        by_address_type: Dict[str, int] = {}
        for row in sorted(filtered, key=lambda item: (_as_int(item.get("created_tick", 0), 0), str(item.get("envelope_id", "")))):
            addr = dict(row.get("recipient_address") or {})
            address_type = str(addr.get("address_type", "")).strip().lower() or str(addr.get("kind", "")).strip().lower() or "subject"
            if address_type == "single":
                address_type = "subject"
            by_address_type[address_type] = _as_int(by_address_type.get(address_type, 0), 0) + 1
        payload = {
            "sender_subject_id": sender_subject_id or None,
            "sent_count": int(len(filtered)),
            "address_type_counts": dict((key, int(by_address_type[key])) for key in sorted(by_address_type.keys())),
        }
        if allow_hidden_state:
            payload["recent_sent"] = [
                {
                    "envelope_id": str(row.get("envelope_id", "")).strip(),
                    "artifact_id": str(row.get("artifact_id", "")).strip() or None,
                    "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
                    "address_type": str(dict(row.get("recipient_address") or {}).get("address_type", "")).strip()
                    or str(dict(row.get("recipient_address") or {}).get("kind", "")).strip()
                    or "subject",
                }
                for row in sorted(
                    filtered,
                    key=lambda item: (
                        _as_int(item.get("created_tick", 0), 0),
                        str(item.get("envelope_id", "")),
                    ),
                )[-128:]
            ]
        return payload
    if section_id == "section.signal.aggregation_status":
        artifacts = [
            dict(item)
            for item in list((dict(state or {})).get("info_artifact_rows") or (dict(state or {})).get("knowledge_artifacts") or [])
            if isinstance(item, dict)
        ]
        agg_artifacts = []
        by_policy: Dict[str, int] = {}
        latest_tick_by_policy: Dict[str, int] = {}
        for row in sorted(artifacts, key=lambda item: (_as_int(item.get("created_tick", 0), 0), str(item.get("artifact_id", "")))):
            ext = dict(row.get("extensions") or {})
            policy_id = str(ext.get("aggregation_policy_id", "")).strip()
            if not policy_id:
                continue
            agg_artifacts.append(row)
            by_policy[policy_id] = _as_int(by_policy.get(policy_id, 0), 0) + 1
            latest_tick_by_policy[policy_id] = max(
                _as_int(latest_tick_by_policy.get(policy_id, 0), 0),
                _as_int(row.get("created_tick", 0), 0),
            )
        schedule_rows = [
            dict(item)
            for item in list((dict(state or {})).get("signal_aggregation_schedules") or (dict(state or {})).get("aggregation_schedule_rows") or [])
            if isinstance(item, dict)
        ]
        payload = {
            "aggregated_report_count": int(len(agg_artifacts)),
            "policy_count": int(len(by_policy.keys())),
            "policy_counts": dict((key, int(by_policy[key])) for key in sorted(by_policy.keys())),
            "next_due_by_schedule_id": dict(
                (
                    str(row.get("schedule_id", "")).strip(),
                    int(max(0, _as_int(row.get("next_due_tick", 0), 0))),
                )
                for row in sorted(schedule_rows, key=lambda item: str(item.get("schedule_id", "")))
                if str(row.get("schedule_id", "")).strip()
            ),
        }
        if allow_hidden_state:
            payload["latest_tick_by_policy"] = dict((key, int(latest_tick_by_policy[key])) for key in sorted(latest_tick_by_policy.keys()))
            payload["recent_reports"] = [
                {
                    "artifact_id": str(row.get("artifact_id", "")).strip(),
                    "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
                    "aggregation_policy_id": str(dict(row.get("extensions") or {}).get("aggregation_policy_id", "")).strip() or None,
                }
                for row in list(agg_artifacts[-128:])
            ]
        return payload
    if section_id == "section.models.summary":
        bindings = [
            dict(item)
            for item in list((dict(state or {})).get("model_bindings") or [])
            if isinstance(item, dict)
        ]
        results = [
            dict(item)
            for item in list((dict(state or {})).get("model_evaluation_results") or [])
            if isinstance(item, dict)
        ]
        cache_rows = [
            dict(item)
            for item in list((dict(state or {})).get("model_cache_rows") or [])
            if isinstance(item, dict)
        ]
        runtime = dict((dict(state or {})).get("model_runtime_state") or {})
        by_model: Dict[str, int] = {}
        by_tier: Dict[str, int] = {}
        for row in bindings:
            model_id = str(row.get("model_id", "")).strip() or "model.unknown"
            tier = str(row.get("tier", "")).strip() or "macro"
            by_model[model_id] = _as_int(by_model.get(model_id, 0), 0) + 1
            by_tier[tier] = _as_int(by_tier.get(tier, 0), 0) + 1
        payload = {
            "binding_count": int(len(bindings)),
            "evaluation_result_count": int(len(results)),
            "cache_entry_count": int(len(cache_rows)),
            "model_counts": dict((key, int(by_model[key])) for key in sorted(by_model.keys())),
            "tier_counts": dict((key, int(by_tier[key])) for key in sorted(by_tier.keys())),
            "last_tick": int(max(0, _as_int(runtime.get("last_tick", 0), 0))),
            "last_budget_outcome": str(runtime.get("last_budget_outcome", "complete")).strip() or "complete",
        }
        if allow_hidden_state:
            payload["last_cost_units"] = int(max(0, _as_int(runtime.get("last_cost_units", 0), 0)))
            payload["last_processed_binding_count"] = int(
                max(0, _as_int(runtime.get("last_processed_binding_count", 0), 0))
            )
            payload["last_deferred_binding_count"] = int(
                max(0, _as_int(runtime.get("last_deferred_binding_count", 0), 0))
            )
            payload["recent_results"] = [
                {
                    "result_id": str(row.get("result_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "model_id": str(row.get("model_id", "")).strip() or None,
                    "binding_id": str(row.get("binding_id", "")).strip() or None,
                }
                for row in sorted(
                    results,
                    key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("result_id", ""))),
                )[-128:]
            ]
        return payload
    if section_id == "section.phys.momentum_summary":
        momentum_rows = [
            dict(item)
            for item in list((dict(state or {})).get("momentum_states") or [])
            if isinstance(item, dict)
        ]
        force_rows = [
            dict(item)
            for item in list((dict(state or {})).get("force_application_rows") or [])
            if isinstance(item, dict)
        ]
        impulse_rows = [
            dict(item)
            for item in list((dict(state or {})).get("impulse_application_rows") or [])
            if isinstance(item, dict)
        ]
        total_mass = 0
        total_momentum_l1 = 0
        nonzero_count = 0
        for row in momentum_rows:
            linear = dict(row.get("momentum_linear") or {})
            px = int(_as_int(linear.get("x", 0), 0))
            py = int(_as_int(linear.get("y", 0), 0))
            pz = int(_as_int(linear.get("z", 0), 0))
            total_mass += int(max(1, _as_int(row.get("mass_value", 1), 1)))
            total_momentum_l1 += int(abs(px) + abs(py) + abs(pz))
            if (px != 0) or (py != 0) or (pz != 0):
                nonzero_count += 1
        payload = {
            "momentum_state_count": int(len(momentum_rows)),
            "nonzero_momentum_count": int(nonzero_count),
            "total_mass_value": int(total_mass),
            "total_momentum_l1": int(total_momentum_l1),
            "force_application_count": int(len(force_rows)),
            "impulse_application_count": int(len(impulse_rows)),
            "momentum_hash_chain": str((dict(state or {})).get("momentum_hash_chain", "")).strip() or None,
            "impulse_event_hash_chain": str((dict(state or {})).get("impulse_event_hash_chain", "")).strip() or None,
        }
        if allow_hidden_state:
            payload["rows"] = [
                {
                    "assembly_id": str(row.get("assembly_id", "")).strip(),
                    "mass_value": int(max(1, _as_int(row.get("mass_value", 1), 1))),
                    "momentum_linear": {
                        "x": int(_as_int((dict(row.get("momentum_linear") or {})).get("x", 0), 0)),
                        "y": int(_as_int((dict(row.get("momentum_linear") or {})).get("y", 0), 0)),
                        "z": int(_as_int((dict(row.get("momentum_linear") or {})).get("z", 0), 0)),
                    },
                    "momentum_angular": row.get("momentum_angular", 0),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
                for row in sorted(momentum_rows, key=lambda item: str(item.get("assembly_id", "")))[:256]
            ]
        return payload
    if section_id == "section.phys.kinetic_energy":
        artifact_rows = [
            dict(item)
            for item in list((dict(state or {})).get("info_artifact_rows") or (dict(state or {})).get("knowledge_artifacts") or [])
            if isinstance(item, dict)
        ]
        kinetic_rows = []
        for row in artifact_rows:
            ext = dict(row.get("extensions") or {})
            if str(ext.get("quantity_id", "")).strip() != "quantity.energy_kinetic":
                continue
            kinetic_rows.append(
                {
                    "artifact_id": str(row.get("artifact_id", "")).strip(),
                    "assembly_id": str(ext.get("assembly_id", "")).strip() or None,
                    "value": int(max(0, _as_int(ext.get("value", 0), 0))),
                    "tick": int(max(0, _as_int(ext.get("tick", 0), 0))),
                    "source_process_id": str(ext.get("source_process_id", "")).strip() or None,
                    "source_application_id": str(ext.get("source_application_id", "")).strip() or None,
                }
            )
        kinetic_rows = sorted(
            kinetic_rows,
            key=lambda item: (int(max(0, _as_int(item.get("tick", 0), 0))), str(item.get("artifact_id", ""))),
        )
        total_energy = int(sum(int(max(0, _as_int(row.get("value", 0), 0))) for row in kinetic_rows))
        payload = {
            "observation_count": int(len(kinetic_rows)),
            "total_kinetic_energy": int(total_energy),
            "latest_tick": int(max([0] + [int(max(0, _as_int(row.get("tick", 0), 0))) for row in kinetic_rows])),
            "status": ("present" if kinetic_rows else "none"),
        }
        if allow_hidden_state:
            payload["rows"] = list(kinetic_rows[-256:])
        return payload
    if section_id == "section.phys.entropy_summary":
        entropy_state_rows = [
            dict(item)
            for item in list((dict(state or {})).get("entropy_state_rows") or [])
            if isinstance(item, dict)
        ]
        entropy_event_rows = [
            dict(item)
            for item in list((dict(state or {})).get("entropy_event_rows") or [])
            if isinstance(item, dict)
        ]
        entropy_reset_rows = [
            dict(item)
            for item in list((dict(state or {})).get("entropy_reset_events") or [])
            if isinstance(item, dict)
        ]
        entropy_values = [int(max(0, _as_int(row.get("entropy_value", 0), 0))) for row in entropy_state_rows]
        payload = {
            "target_count": int(len(entropy_state_rows)),
            "event_count": int(len(entropy_event_rows)),
            "reset_event_count": int(len(entropy_reset_rows)),
            "total_entropy_value": int(sum(entropy_values)),
            "max_entropy_value": int(max([0] + entropy_values)),
            "entropy_hash_chain": str((dict(state or {})).get("entropy_hash_chain", "")).strip() or None,
            "entropy_reset_events_hash_chain": str(
                (dict(state or {})).get(
                    "entropy_reset_events_hash_chain",
                    (dict(state or {})).get("entropy_reset_hash_chain", ""),
                )
            ).strip() or None,
        }
        if allow_hidden_state:
            payload["rows"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip(),
                    "entropy_value": int(max(0, _as_int(row.get("entropy_value", 0), 0))),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
                for row in sorted(entropy_state_rows, key=lambda item: str(item.get("target_id", "")))[:256]
            ]
        return payload
    if section_id == "section.phys.entropy_effects":
        effect_rows = [
            dict(item)
            for item in list((dict(state or {})).get("entropy_effect_rows") or [])
            if isinstance(item, dict)
        ]
        degraded_count = 0
        min_eff = 1000
        max_hazard = 1000
        policy_counts: Dict[str, int] = {}
        for row in effect_rows:
            eff = int(max(0, _as_int(row.get("efficiency_multiplier_permille", 1000), 1000)))
            hazard = int(max(0, _as_int(row.get("hazard_multiplier_permille", 1000), 1000)))
            if bool(row.get("degraded", False)) or eff < 1000:
                degraded_count += 1
            if eff < min_eff:
                min_eff = eff
            if hazard > max_hazard:
                max_hazard = hazard
            policy_id = str(row.get("policy_id", "")).strip() or "entropy_effect.basic_linear"
            policy_counts[policy_id] = _as_int(policy_counts.get(policy_id, 0), 0) + 1
        payload = {
            "effect_target_count": int(len(effect_rows)),
            "degraded_target_count": int(degraded_count),
            "min_efficiency_multiplier_permille": int(min_eff if effect_rows else 1000),
            "max_hazard_multiplier_permille": int(max_hazard if effect_rows else 1000),
            "policy_counts": dict((key, int(policy_counts[key])) for key in sorted(policy_counts.keys())),
        }
        if allow_hidden_state:
            payload["rows"] = [
                {
                    "target_id": str(row.get("target_id", "")).strip(),
                    "policy_id": str(row.get("policy_id", "")).strip() or None,
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "entropy_value": int(max(0, _as_int(row.get("entropy_value", 0), 0))),
                    "efficiency_multiplier_permille": int(max(0, _as_int(row.get("efficiency_multiplier_permille", 1000), 1000))),
                    "hazard_multiplier_permille": int(max(0, _as_int(row.get("hazard_multiplier_permille", 1000), 1000))),
                    "maintenance_interval_modifier_permille": int(
                        max(0, _as_int(row.get("maintenance_interval_modifier_permille", 1000), 1000))
                    ),
                    "degraded": bool(row.get("degraded", False)),
                }
                for row in sorted(effect_rows, key=lambda item: str(item.get("target_id", "")))[:256]
            ]
        return payload
    if section_id == "section.field.summary":
        field_layers = [
            dict(item)
            for item in list((dict(state or {})).get("field_layers") or [])
            if isinstance(item, dict)
        ]
        field_cells = [
            dict(item)
            for item in list((dict(state or {})).get("field_cells") or [])
            if isinstance(item, dict)
        ]
        sample_rows = [
            dict(item)
            for item in list((dict(state or {})).get("field_sample_rows") or [])
            if isinstance(item, dict)
        ]
        policy_counts: Dict[str, int] = {}
        field_ids = set()
        for row in field_layers:
            field_id = str(row.get("field_id", "")).strip()
            if field_id:
                field_ids.add(field_id)
            policy_id = str(row.get("update_policy_id", "")).strip() or "field.static_default"
            policy_counts[policy_id] = _as_int(policy_counts.get(policy_id, 0), 0) + 1
        payload = {
            "field_layer_count": int(len(field_layers)),
            "field_cell_count": int(len(field_cells)),
            "field_sample_count": int(len(sample_rows)),
            "field_ids": sorted(field_ids),
            "update_policy_counts": dict((key, int(policy_counts[key])) for key in sorted(policy_counts.keys())),
        }
        if allow_hidden_state:
            payload["layers"] = [
                {
                    "field_id": str(row.get("field_id", "")).strip(),
                    "field_type_id": str(row.get("field_type_id", "")).strip() or None,
                    "update_policy_id": str(row.get("update_policy_id", "")).strip() or "field.static_default",
                    "spatial_scope_id": str(row.get("spatial_scope_id", "")).strip() or None,
                    "resolution_level": str(row.get("resolution_level", "")).strip() or None,
                }
                for row in sorted(field_layers, key=lambda item: str(item.get("field_id", "")))[:256]
            ]
        return payload
    if section_id in {"section.field.gravity", "section.field.radiation", "section.field.irradiance"}:
        target_field_ids = {
            "section.field.gravity": {"field.gravity_vector", "field.gravity.vector"},
            "section.field.radiation": {"field.radiation_intensity", "field.radiation"},
            "section.field.irradiance": {"field.irradiance"},
        }.get(section_id, set())
        field_cells = [
            dict(item)
            for item in list((dict(state or {})).get("field_cells") or [])
            if isinstance(item, dict) and str(item.get("field_id", "")).strip() in target_field_ids
        ]
        sample_rows = [
            dict(item)
            for item in list((dict(state or {})).get("field_sample_rows") or [])
            if isinstance(item, dict) and str(item.get("field_id", "")).strip() in target_field_ids
        ]
        latest_tick = int(
            max(
                [0]
                + [int(max(0, _as_int(row.get("tick", 0), 0))) for row in sample_rows]
                + [int(max(0, _as_int(row.get("last_updated_tick", 0), 0))) for row in field_cells]
            )
        )
        payload = {
            "field_ids": sorted(target_field_ids),
            "field_cell_count": int(len(field_cells)),
            "field_sample_count": int(len(sample_rows)),
            "latest_tick": int(latest_tick),
        }
        if section_id == "section.field.gravity":
            latest_sample = {}
            if sample_rows:
                latest_row = sorted(
                    sample_rows,
                    key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("field_id", "")), str(item.get("spatial_node_id", ""))),
                )[-1]
                latest_value = dict(latest_row.get("sampled_value") or {}) if isinstance(latest_row.get("sampled_value"), dict) else {}
                latest_sample = {
                    "x": int(_as_int(latest_value.get("x", 0), 0)),
                    "y": int(_as_int(latest_value.get("y", 0), 0)),
                    "z": int(_as_int(latest_value.get("z", 0), 0)),
                }
            payload["latest_vector"] = latest_sample or None
        else:
            latest_scalar = 0
            if sample_rows:
                latest_row = sorted(
                    sample_rows,
                    key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("field_id", "")), str(item.get("spatial_node_id", ""))),
                )[-1]
                latest_scalar = int(_as_int(latest_row.get("sampled_value", 0), 0))
            payload["latest_scalar"] = int(latest_scalar)
        if allow_hidden_state:
            payload["recent_samples"] = [
                {
                    "field_id": str(row.get("field_id", "")).strip(),
                    "spatial_node_id": str(row.get("spatial_node_id", "")).strip() or None,
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "sampled_value": row.get("sampled_value"),
                }
                for row in sorted(
                    sample_rows,
                    key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("field_id", "")), str(item.get("spatial_node_id", ""))),
                )[-256:]
            ]
        return payload
    if section_id == "section.safety.instances":
        rows = [
            dict(item)
            for item in list((dict(state or {})).get("safety_instances") or [])
            if isinstance(item, dict)
        ]
        rows = sorted(rows, key=lambda item: str(item.get("instance_id", "")))
        active_rows = [row for row in rows if bool(row.get("active", True))]
        by_pattern: Dict[str, int] = {}
        for row in active_rows:
            pattern_id = str(row.get("pattern_id", "")).strip() or "safety.unknown"
            by_pattern[pattern_id] = _as_int(by_pattern.get(pattern_id, 0), 0) + 1
        payload = {
            "instance_count": int(len(rows)),
            "active_instance_count": int(len(active_rows)),
            "pattern_counts": dict((key, int(by_pattern[key])) for key in sorted(by_pattern.keys())),
        }
        if allow_hidden_state:
            payload["instances"] = [
                {
                    "instance_id": str(row.get("instance_id", "")).strip(),
                    "pattern_id": str(row.get("pattern_id", "")).strip() or None,
                    "active": bool(row.get("active", True)),
                    "target_count": int(len(_sorted_unique_strings(list(row.get("target_ids") or [])))),
                    "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
                }
                for row in list(rows[:256])
            ]
        return payload
    if section_id == "section.safety.events":
        rows = [
            dict(item)
            for item in list((dict(state or {})).get("safety_events") or [])
            if isinstance(item, dict)
        ]
        rows = sorted(
            rows,
            key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("event_id", ""))),
        )
        status_counts: Dict[str, int] = {}
        for row in rows:
            status = str(row.get("status", "")).strip().lower() or "unknown"
            status_counts[status] = _as_int(status_counts.get(status, 0), 0) + 1
        payload = {
            "event_count": int(len(rows)),
            "status_counts": dict((key, int(status_counts[key])) for key in sorted(status_counts.keys())),
            "latest_tick": int(max([0] + [int(max(0, _as_int(row.get("tick", 0), 0))) for row in rows])),
        }
        if allow_hidden_state:
            payload["recent_events"] = [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "pattern_id": str(row.get("pattern_id", "")).strip() or None,
                    "pattern_type": str(row.get("pattern_type", "")).strip() or None,
                    "status": str(row.get("status", "")).strip() or "unknown",
                    "action_count": int(max(0, _as_int(row.get("action_count", 0), 0))),
                }
                for row in list(rows[-256:])
            ]
        return payload
    if section_id == "section.institution.bulletins":
        institution_id = str(request.get("target_id", "")).strip() or str(request.get("institution_id", "")).strip()
        artifacts = [
            dict(item)
            for item in list((dict(state or {})).get("info_artifact_rows") or (dict(state or {})).get("knowledge_artifacts") or [])
            if isinstance(item, dict)
        ]
        bulletin_rows = []
        for row in sorted(artifacts, key=lambda item: (_as_int(item.get("created_tick", 0), 0), str(item.get("artifact_id", "")))):
            if str(row.get("artifact_family_id", "")).strip() != "REPORT":
                continue
            ext = dict(row.get("extensions") or {})
            row_institution_id = str(ext.get("institution_id", "")).strip()
            if institution_id and row_institution_id != institution_id:
                continue
            if (not row_institution_id) and institution_id:
                continue
            if institution_id and not row_institution_id:
                continue
            if (not institution_id) and (not row_institution_id):
                continue
            if (not ext.get("bulletin_policy_id")) and ("headline" not in dict(row.get("summary") or {})):
                continue
            bulletin_rows.append(row)
        latest_tick = int(
            max([0] + [int(max(0, _as_int(row.get("created_tick", 0), 0))) for row in bulletin_rows])
        )
        payload = {
            "institution_id": institution_id or None,
            "bulletin_count": int(len(bulletin_rows)),
            "latest_bulletin_tick": int(latest_tick),
            "status": "new" if latest_tick >= int(max(0, _as_int(request.get("tick", 0), 0)) - 64) else "stable",
        }
        if allow_hidden_state:
            payload["recent_bulletins"] = [
                {
                    "artifact_id": str(row.get("artifact_id", "")).strip(),
                    "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
                    "bulletin_policy_id": str(dict(row.get("extensions") or {}).get("bulletin_policy_id", "")).strip() or None,
                    "coarse_summary": bool(dict(row.get("extensions") or {}).get("coarse_summary", False)),
                }
                for row in bulletin_rows[-128:]
            ]
        return payload
    if section_id == "section.institution.dispatch_state":
        institution_id = str(request.get("target_id", "")).strip() or str(request.get("institution_id", "")).strip()
        control_intent_rows = [
            dict(item)
            for item in list((dict(state or {})).get("control_intent_rows") or (dict(state or {})).get("control_intents") or [])
            if isinstance(item, dict)
        ]
        dispatch_intents = []
        for row in sorted(control_intent_rows, key=lambda item: (_as_int(item.get("created_tick", 0), 0), str(item.get("control_intent_id", "")))):
            params = dict(row.get("parameters") or {})
            inputs = dict(params.get("inputs") or {})
            process_id = str(params.get("process_id", "")).strip() or str(inputs.get("process_id", "")).strip()
            if process_id != "process.travel_schedule_set":
                continue
            row_institution_id = str(inputs.get("institution_id", "")).strip() or str(dict(row.get("extensions") or {}).get("institution_id", "")).strip()
            if institution_id and row_institution_id != institution_id:
                continue
            dispatch_intents.append(row)
        schedule_rows = [
            dict(item)
            for item in list((dict(state or {})).get("travel_schedules") or [])
            if isinstance(item, dict)
        ]
        institution_schedule_rows = []
        for row in sorted(schedule_rows, key=lambda item: (str(item.get("schedule_id", "")), _as_int(item.get("next_due_tick", 0), 0))):
            row_inst = str((dict(row.get("extensions") or {})).get("institution_id", "")).strip()
            if institution_id and row_inst and row_inst != institution_id:
                continue
            institution_schedule_rows.append(row)
        payload = {
            "institution_id": institution_id or None,
            "dispatch_intent_count": int(len(dispatch_intents)),
            "schedule_count": int(len(institution_schedule_rows)),
            "next_due_tick": int(
                min(
                    [int(max(0, _as_int(row.get("next_due_tick", 0), 0))) for row in institution_schedule_rows]
                    or [0]
                )
            ),
            "delayed_service_indicator": bool(
                len(
                    [
                        row
                        for row in list((dict(state or {})).get("travel_events") or [])
                        if isinstance(row, dict)
                        and str(row.get("kind", "")).strip() == "delay"
                    ]
                )
                > 0
            ),
        }
        if allow_hidden_state:
            payload["recent_dispatch_intents"] = [
                {
                    "control_intent_id": str(row.get("control_intent_id", "")).strip(),
                    "target_id": str(row.get("target_id", "")).strip() or None,
                    "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
                }
                for row in dispatch_intents[-128:]
            ]
            payload["schedule_rows"] = [
                {
                    "schedule_id": str(row.get("schedule_id", "")).strip(),
                    "next_due_tick": int(max(0, _as_int(row.get("next_due_tick", 0), 0))),
                    "interval_ticks": int(max(1, _as_int(row.get("interval_ticks", 1), 1))),
                }
                for row in institution_schedule_rows[:128]
            ]
        return payload
    if section_id == "section.institution.compliance_reports":
        institution_id = str(request.get("target_id", "")).strip() or str(request.get("institution_id", "")).strip()
        report_rows = [
            dict(item)
            for item in list((dict(state or {})).get("info_artifact_rows") or (dict(state or {})).get("knowledge_artifacts") or [])
            if isinstance(item, dict)
            and str(item.get("artifact_family_id", "")).strip() == "REPORT"
            and str((dict(item.get("extensions") or {})).get("standards_policy_id", "")).strip()
        ]
        report_rows = [
            row
            for row in sorted(report_rows, key=lambda item: (_as_int(item.get("created_tick", 0), 0), str(item.get("artifact_id", ""))))
            if (not institution_id) or str((dict(row.get("extensions") or {})).get("institution_id", "")).strip() == institution_id
        ]
        compliance_rows = [
            dict(item)
            for item in list((dict(state or {})).get("spec_compliance_results") or [])
            if isinstance(item, dict)
        ]
        pass_count = len([row for row in compliance_rows if str(row.get("overall_grade", "")).strip() == "pass"])
        warn_count = len([row for row in compliance_rows if str(row.get("overall_grade", "")).strip() == "warn"])
        fail_count = len([row for row in compliance_rows if str(row.get("overall_grade", "")).strip() == "fail"])
        payload = {
            "institution_id": institution_id or None,
            "compliance_report_count": int(len(report_rows)),
            "spec_result_count": int(len(compliance_rows)),
            "grade_counts": {
                "pass": int(pass_count),
                "warn": int(warn_count),
                "fail": int(fail_count),
            },
            "status": "attention" if fail_count > 0 else "ok",
        }
        if allow_hidden_state:
            payload["recent_compliance_reports"] = [
                {
                    "artifact_id": str(row.get("artifact_id", "")).strip(),
                    "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
                    "standards_policy_id": str((dict(row.get("extensions") or {})).get("standards_policy_id", "")).strip() or None,
                }
                for row in report_rows[-128:]
            ]
        return payload
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
    if section_id == "section.vehicle.interior_summary":
        graph = _graph_for_target(state, target_payload, request)
        if not graph:
            return {"available": False}
        pressure_rows = _compartment_rows_for_graph(state, graph)
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
                    "state_id": state_id,
                }
            )
        min_pressure = min(
            (int(max(0, _as_int(row.get("derived_pressure", 0), 0))) for row in pressure_rows),
            default=0,
        )
        min_oxygen = min(
            (int(max(0, _as_int(row.get("oxygen_fraction", 0), 0))) for row in pressure_rows),
            default=0,
        )
        max_smoke = max(
            (int(max(0, _as_int(row.get("smoke_density", 0), 0))) for row in pressure_rows),
            default=0,
        )
        flooded_count = len(
            [
                row
                for row in pressure_rows
                if int(max(0, _as_int(row.get("water_volume", 0), 0))) > 0
            ]
        )
        return {
            "available": True,
            "graph_id": str(graph.get("graph_id", "")).strip(),
            "volume_count": int(len(pressure_rows)),
            "portal_count": int(len(portal_states)),
            "portal_open_count": int(
                len(
                    [
                        row
                        for row in portal_states
                        if str(row.get("state_id", "")).strip() in {"open", "unlocked", "permeable", "opening"}
                    ]
                )
            ),
            "min_pressure": int(_quantize_map({"value": int(min_pressure)}, step=quant_step).get("value", 0)),
            "min_oxygen_fraction": int(_quantize_map({"value": int(min_oxygen)}, step=quant_step).get("value", 0)),
            "max_smoke_density": int(_quantize_map({"value": int(max_smoke)}, step=quant_step).get("value", 0)),
            "flooded_count": int(flooded_count),
            "alarm_state": (
                "ALERT"
                if (int(min_pressure) < 700 or int(min_oxygen) < 160 or int(max_smoke) >= 450 or int(flooded_count) > 0)
                else ("WARN" if (int(min_pressure) < 900 or int(min_oxygen) < 200 or int(max_smoke) >= 200) else "OK")
            ),
            "epistemic_redaction": "none" if allow_hidden_state else "coarse_summary",
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
    if section_id in {"section.interior.portal_states", "section.interior.portal_state_table", "section.vehicle.portal_states"}:
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
    if section_id in {"section.interior.pressure_map", "section.interior.pressure_summary", "section.vehicle.pressure_map"}:
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
    if section_id == "section.vehicle.summary":
        if collection != "vehicles":
            return {"available": False}
        vehicle_row = dict(row)
        vehicle_id = str(vehicle_row.get("vehicle_id", "")).strip()
        motion_row = dict(_row_index((dict(state or {})).get("vehicle_motion_states"), "vehicle_id").get(vehicle_id) or {})
        macro_state = dict(motion_row.get("macro_state") or {})
        itinerary_id = str(macro_state.get("itinerary_id", "")).strip()
        itinerary_row = dict(_row_index((dict(state or {})).get("itineraries"), "itinerary_id").get(itinerary_id) or {})
        itinerary_ext = dict(itinerary_row.get("extensions") or {})
        per_edge_profile = [dict(item) for item in list(itinerary_ext.get("per_edge_profile") or []) if isinstance(item, dict)]
        current_edge_id = str(macro_state.get("current_edge_id", "")).strip()
        current_profile = next(
            (
                dict(item)
                for item in per_edge_profile
                if str(item.get("edge_id", "")).strip() == current_edge_id
            ),
            {},
        )
        speed_estimate_mm_per_tick = int(max(0, _as_int(current_profile.get("allowed_speed_mm_per_tick", 0), 0)))
        current_tick = int(max(0, _as_int((dict(state or {})).get("simulation_time", {}).get("tick", 0), 0)))
        eta_tick = (
            int(max(0, _as_int(macro_state.get("eta_tick", itinerary_row.get("estimated_arrival_tick", 0)), 0)))
            if (macro_state.get("eta_tick") is not None or itinerary_row.get("estimated_arrival_tick") is not None)
            else None
        )
        eta_ticks_remaining = None if eta_tick is None else int(max(0, int(eta_tick) - int(current_tick)))
        schedule_rows = sorted(
            [
                dict(item)
                for item in list((dict(state or {})).get("travel_schedules") or [])
                if isinstance(item, dict)
                and str(item.get("target_id", "")).strip() == vehicle_id
                and bool(item.get("active", True))
            ],
            key=lambda item: (_as_int(item.get("next_due_tick", 0), 0), str(item.get("schedule_id", ""))),
        )
        next_schedule_row = dict(schedule_rows[0] if schedule_rows else {})
        next_due_tick = (
            None
            if not next_schedule_row
            else int(max(0, _as_int(next_schedule_row.get("next_due_tick", next_schedule_row.get("start_tick", 0)), 0)))
        )
        payload = {
            "available": bool(vehicle_id),
            "vehicle_id": vehicle_id or None,
            "vehicle_class_id": str(vehicle_row.get("vehicle_class_id", "")).strip() or None,
            "spatial_id": str(vehicle_row.get("spatial_id", "")).strip() or None,
            "motion_tier": str(motion_row.get("tier", "")).strip() or None,
            "travel_state": (
                "enroute"
                if itinerary_id
                else ("scheduled" if bool(next_schedule_row) else "idle")
            ),
            "has_interior_graph": bool(str(vehicle_row.get("interior_graph_id", "")).strip()),
            "port_count": int(len(_sorted_unique_strings(vehicle_row.get("port_ids")))),
            "pose_slot_count": int(len(_sorted_unique_strings(vehicle_row.get("pose_slot_ids")))),
            "mount_point_count": int(len(_sorted_unique_strings(vehicle_row.get("mount_point_ids")))),
        }
        if not allow_hidden_state:
            payload["driver_instrument"] = {
                "speed_state": (
                    "stopped"
                    if int(speed_estimate_mm_per_tick) <= 0
                    else ("cruise" if int(speed_estimate_mm_per_tick) >= 1000 else "limited")
                ),
                "eta_state": (
                    None
                    if eta_ticks_remaining is None
                    else (
                        "imminent"
                        if int(eta_ticks_remaining) <= 16
                        else ("soon" if int(eta_ticks_remaining) <= 64 else "later")
                    )
                ),
                "timetable_state": (
                    None
                    if next_due_tick is None
                    else ("due" if int(next_due_tick) <= int(current_tick) else "scheduled")
                ),
            }
            payload["epistemic_redaction"] = "coarse_summary"
            return payload
        payload["parent_structure_instance_id"] = (
            str(vehicle_row.get("parent_structure_instance_id", "")).strip() or None
        )
        payload["maintenance_policy_id"] = str(vehicle_row.get("maintenance_policy_id", "")).strip() or None
        payload["macro_travel"] = {
            "itinerary_id": itinerary_id or None,
            "current_edge_id": current_edge_id or None,
            "progress_fraction_q16": int(max(0, _as_int(macro_state.get("progress_fraction_q16", 0), 0))),
            "speed_estimate_mm_per_tick": int(max(0, speed_estimate_mm_per_tick)),
            "eta_tick": eta_tick,
            "eta_ticks_remaining": eta_ticks_remaining,
            "next_schedule_due_tick": next_due_tick,
            "next_schedule_id": str(next_schedule_row.get("schedule_id", "")).strip() or None,
            "speed_policy_id": str(itinerary_row.get("speed_policy_id", "")).strip() or None,
        }
        payload["upcoming_timetable_rows"] = [
            {
                "schedule_id": str(item.get("schedule_id", "")).strip() or None,
                "next_due_tick": int(max(0, _as_int(item.get("next_due_tick", item.get("start_tick", 0)), 0))),
                "itinerary_id": str((dict(item.get("extensions") or {})).get("itinerary_id", "")).strip() or None,
            }
            for item in list(schedule_rows)[:8]
        ]
        payload["motion_state"] = dict(motion_row)
        payload["hazard_ids"] = _sorted_unique_strings(vehicle_row.get("hazard_ids"))
        payload["epistemic_redaction"] = "none"
        return payload
    if section_id == "section.vehicle.specs":
        if collection != "vehicles":
            return {"available": False}
        vehicle_row = dict(row)
        payload_ext = dict(target_payload.get("extensions") or {})
        compliance_summary = dict(payload_ext.get("spec_compliance_summary") or {})
        spec_ids = _sorted_unique_strings(vehicle_row.get("spec_ids"))
        payload = {
            "available": True,
            "vehicle_id": str(vehicle_row.get("vehicle_id", "")).strip() or None,
            "spec_ids": list(spec_ids),
            "spec_count": int(len(spec_ids)),
            "compliance_available": bool(compliance_summary),
            "overall_grade": str(compliance_summary.get("overall_grade", "")).strip() or None,
        }
        if not allow_hidden_state:
            payload["epistemic_redaction"] = "coarse_summary"
            return payload
        payload["spec_compliance_summary"] = dict(compliance_summary)
        payload["epistemic_redaction"] = "none"
        return payload
    if section_id == "section.vehicle.ports":
        if collection != "vehicles":
            return {"available": False}
        vehicle_row = dict(row)
        declared_port_ids = _sorted_unique_strings(vehicle_row.get("port_ids"))
        port_index = _row_index((dict(state or {})).get("machine_ports"), "port_id")
        rows = []
        for port_id in declared_port_ids:
            port_row = dict(port_index.get(port_id) or {})
            if not port_row:
                rows.append(
                    {
                        "port_id": port_id,
                        "available": False,
                    }
                )
                continue
            ext = dict(port_row.get("extensions") or {}) if isinstance(port_row.get("extensions"), dict) else {}
            rows.append(
                {
                    "port_id": port_id,
                    "available": True,
                    "port_type_id": str(port_row.get("port_type_id", "")).strip() or None,
                    "machine_id": str(port_row.get("machine_id", "")).strip() or None,
                    "capacity_mass": int(max(0, _as_int(port_row.get("capacity_mass", 0), 0))),
                    "stored_mass": int(max(0, _as_int(port_row.get("stored_mass", 0), 0))),
                    "accepted_tags": _sorted_unique_strings(ext.get("accepted_tags")),
                }
            )
        return {
            "available": True,
            "vehicle_id": str(vehicle_row.get("vehicle_id", "")).strip() or None,
            "port_count": int(len(rows)),
            "rows": sorted(rows, key=lambda item: str(item.get("port_id", "")))[:256],
        }
    if section_id == "section.vehicle.pose_slots":
        if collection != "vehicles":
            return {"available": False}
        vehicle_row = dict(row)
        declared_pose_slot_ids = _sorted_unique_strings(vehicle_row.get("pose_slot_ids"))
        slot_index = _row_index((dict(state or {})).get("pose_slots"), "pose_slot_id")
        rows = []
        for pose_slot_id in declared_pose_slot_ids:
            slot_row = dict(slot_index.get(pose_slot_id) or {})
            if not slot_row:
                rows.append({"pose_slot_id": pose_slot_id, "available": False})
                continue
            ext = dict(slot_row.get("extensions") or {}) if isinstance(slot_row.get("extensions"), dict) else {}
            current_occupant_id = str(slot_row.get("current_occupant_id", "")).strip() or None
            row_payload = {
                "pose_slot_id": pose_slot_id,
                "available": True,
                "parent_assembly_id": str(slot_row.get("parent_assembly_id", "")).strip() or None,
                "control_binding_id": str(slot_row.get("control_binding_id", "")).strip() or None,
                "allowed_postures": _sorted_unique_strings(slot_row.get("allowed_postures")),
                "driver_station": bool(ext.get("driver_station", False)),
                "occupied": bool(current_occupant_id),
                "current_occupant_id": current_occupant_id if allow_hidden_state else None,
            }
            rows.append(row_payload)
        return {
            "available": True,
            "vehicle_id": str(vehicle_row.get("vehicle_id", "")).strip() or None,
            "pose_slot_count": int(len(rows)),
            "rows": sorted(rows, key=lambda item: str(item.get("pose_slot_id", "")))[:256],
        }
    if section_id == "section.vehicle.wear_risk":
        if collection != "vehicles":
            return {"available": False}
        payload_ext = dict(target_payload.get("extensions") or {})
        explicit = dict(payload_ext.get("failure_risk_summary") or {})
        stress_summary = dict(payload_ext.get("mechanics_stress_summary") or {})
        risk_rows = [dict(item) for item in list(explicit.get("risk_rows") or []) if isinstance(item, dict)]
        if not risk_rows and stress_summary:
            risk_rows = [
                {
                    "target_id": str(stress_summary.get("target_id", "")).strip() or str(row.get("vehicle_id", "")).strip(),
                    "max_stress_ratio_permille": int(max(0, _as_int(stress_summary.get("max_stress_ratio_permille", 0), 0))),
                    "near_fracture_edge_count": int(max(0, _as_int(stress_summary.get("near_fracture_edge_count", 0), 0))),
                    "failed_edge_count": int(max(0, _as_int(stress_summary.get("failed_edge_count", 0), 0))),
                    "derailment_risk_permille": int(max(0, _as_int(stress_summary.get("derailment_risk_permille", 0), 0))),
                    "high_risk": bool(
                        int(max(0, _as_int(stress_summary.get("max_stress_ratio_permille", 0), 0))) > 1000
                        or int(max(0, _as_int(stress_summary.get("derailment_risk_permille", 0), 0))) >= 900
                    ),
                }
            ]
        payload = {
            "available": bool(risk_rows),
            "vehicle_id": str(row.get("vehicle_id", "")).strip() or None,
            "risk_rows": [dict(item) for item in list(risk_rows)[:16] if isinstance(item, dict)],
        }
        if not allow_hidden_state:
            payload["epistemic_redaction"] = "coarse_summary"
            return payload
        payload["mechanics_stress_summary"] = dict(stress_summary)
        payload["epistemic_redaction"] = "none"
        return payload
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
    if section_id == "section.spec_compliance_summary":
        payload_ext = dict(target_payload.get("extensions") or {})
        summary = dict(payload_ext.get("spec_compliance_summary") or {})
        if not summary and collection == "formalization_states":
            formalization_row = dict(row)
            formalization_spec_id = str(formalization_row.get("spec_id", "")).strip()
            if formalization_spec_id:
                target_context_id = str(formalization_row.get("target_context_id", "")).strip()
                compliance_rows = [
                    dict(item)
                    for item in list((dict(state or {})).get("spec_compliance_results") or [])
                    if isinstance(item, dict)
                    and str(item.get("spec_id", "")).strip() == formalization_spec_id
                    and str(item.get("target_id", "")).strip() == target_context_id
                ]
                compliance_rows = sorted(
                    compliance_rows,
                    key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("result_id", ""))),
                )
                latest = dict(compliance_rows[-1] if compliance_rows else {})
                check_counts = {"pass": 0, "warn": 0, "fail": 0}
                for check_row in list(latest.get("check_results") or []):
                    if not isinstance(check_row, dict):
                        continue
                    grade = str(check_row.get("grade", "")).strip()
                    if grade in check_counts:
                        check_counts[grade] = _as_int(check_counts.get(grade, 0), 0) + 1
                summary = {
                    "available": True,
                    "target_kind": "structure",
                    "target_id": target_context_id,
                    "bound_spec_id": formalization_spec_id,
                    "binding_id": None,
                    "binding_tick": int(max(0, _as_int(formalization_row.get("created_tick", 0), 0))),
                    "result_id": str(latest.get("result_id", "")).strip() or None,
                    "result_tick": int(max(0, _as_int(latest.get("tick", 0), 0))),
                    "overall_grade": str(latest.get("overall_grade", "")).strip() or "",
                    "check_count": int(len(list(latest.get("check_results") or []))),
                    "check_grade_counts": dict(check_counts),
                    "failure_refusal_codes": [],
                    "strict_noncompliant": False,
                }
        if not summary:
            return {"available": False}
        target_id = str(summary.get("target_id", "")).strip() or str(request.get("target_id", "")).strip() or None
        bound_spec_id = str(summary.get("bound_spec_id", "")).strip() or None
        result_id = str(summary.get("result_id", "")).strip() or None
        overall_grade = str(summary.get("overall_grade", "")).strip()
        check_grade_counts = {
            "pass": int(max(0, _as_int((dict(summary.get("check_grade_counts") or {})).get("pass", 0), 0))),
            "warn": int(max(0, _as_int((dict(summary.get("check_grade_counts") or {})).get("warn", 0), 0))),
            "fail": int(max(0, _as_int((dict(summary.get("check_grade_counts") or {})).get("fail", 0), 0))),
        }
        payload = {
            "available": bool(summary.get("available", True)),
            "target_kind": str(summary.get("target_kind", "")).strip() or None,
            "target_id": target_id,
            "bound_spec_id": bound_spec_id,
            "has_compliance_result": bool(result_id),
            "overall_grade": overall_grade or None,
            "status": (
                overall_grade
                if overall_grade in {"pass", "warn", "fail"}
                else ("bound" if bound_spec_id else "unbound")
            ),
            "check_count": int(max(0, _as_int(summary.get("check_count", 0), 0))),
            "check_grade_counts": dict(check_grade_counts),
        }
        if not allow_hidden_state:
            payload["epistemic_redaction"] = "coarse_summary"
            return payload
        payload["binding_id"] = str(summary.get("binding_id", "")).strip() or None
        payload["binding_tick"] = int(max(0, _as_int(summary.get("binding_tick", 0), 0)))
        payload["result_id"] = result_id
        payload["result_tick"] = int(max(0, _as_int(summary.get("result_tick", 0), 0)))
        payload["failure_refusal_codes"] = _sorted_unique_strings(summary.get("failure_refusal_codes"))
        payload["strict_noncompliant"] = bool(summary.get("strict_noncompliant", False))
        return payload
    if section_id == "section.commitments_summary":
        rows = []
        for key in ("material_commitments", "construction_commitments", "shipment_commitments", "maintenance_commitments"):
            rows.extend([dict(item) for item in list((dict(state or {})).get(key) or []) if isinstance(item, dict)])
        formalization_id = _formalization_id_from_payload()
        if formalization_id:
            rows = [
                item
                for item in rows
                if str(item.get("target_id", "")).strip() == formalization_id
                or str((dict(item.get("extensions") or {})).get("formalization_id", "")).strip() == formalization_id
            ]
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
