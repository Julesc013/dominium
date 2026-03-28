"""Deterministic INT-2 compartment FlowChannel builder over InteriorVolumeGraph."""

from __future__ import annotations

from typing import Dict, List, Mapping

from core.flow.flow_engine import normalize_flow_channel
from core.state.state_machine_engine import StateMachineError, normalize_state_machine
from interior.interior_engine import normalize_interior_graph, portal_rows_by_id, volume_rows_by_id
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_INTERIOR_FLOW_INVALID = "refusal.interior.flow.invalid"

_OUTSIDE_NODE_ID = "interior.node.outside"
_OPEN_STATES = {"open", "opening", "unlocked", "permeable", "vented"}
_DAMAGED_STATES = {"damaged", "failed", "breached", "ruptured"}
_DEFAULT_TEMPLATE_BY_PORTAL_TYPE = {
    "portal.door": "door_basic",
    "portal.hatch": "hatch_basic",
    "portal.vent": "vent_basic",
    "portal.airlock": "airlock_basic",
}


class CompartmentFlowBuilderError(ValueError):
    """Deterministic interior flow graph refusal."""

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


def _safe_extensions(payload: Mapping[str, object]) -> dict:
    ext = payload.get("extensions")
    return dict(ext or {}) if isinstance(ext, dict) else {}


def normalize_compartment_state(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    volume_id = str(payload.get("volume_id", "")).strip()
    if not volume_id:
        raise CompartmentFlowBuilderError(
            REFUSAL_INTERIOR_FLOW_INVALID,
            "compartment_state requires volume_id",
            {"volume_id": volume_id},
        )

    def _opt_int(key: str) -> int | None:
        value = payload.get(key)
        if value is None:
            return None
        return int(_as_int(value, 0))

    oxygen_fraction = _opt_int("oxygen_fraction")
    if oxygen_fraction is not None:
        oxygen_fraction = max(0, oxygen_fraction)
    return {
        "schema_version": "1.0.0",
        "volume_id": volume_id,
        "air_mass": max(0, _as_int(payload.get("air_mass", 0), 0)),
        "water_volume": max(0, _as_int(payload.get("water_volume", 0), 0)),
        "temperature": _opt_int("temperature"),
        "oxygen_fraction": oxygen_fraction,
        "smoke_density": max(0, _as_int(payload.get("smoke_density", 0), 0)) if payload.get("smoke_density") is not None else None,
        "derived_pressure": _opt_int("derived_pressure"),
        "extensions": _safe_extensions(payload),
    }


def compartment_state_rows_by_volume_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("volume_id", ""))):
        normalized = normalize_compartment_state(row)
        out[str(normalized.get("volume_id", ""))] = normalized
    return out


def normalize_portal_flow_params(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    portal_id = str(payload.get("portal_id", "")).strip()
    if not portal_id:
        raise CompartmentFlowBuilderError(
            REFUSAL_INTERIOR_FLOW_INVALID,
            "portal_flow_params requires portal_id",
            {"portal_id": portal_id},
        )

    def _non_negative(key: str) -> int:
        return max(0, _as_int(payload.get(key, 0), 0))

    return {
        "schema_version": "1.0.0",
        "portal_id": portal_id,
        "conductance_air": int(_non_negative("conductance_air")),
        "conductance_water": int(_non_negative("conductance_water")),
        "conductance_smoke": int(_non_negative("conductance_smoke")),
        "sealing_coefficient": int(_non_negative("sealing_coefficient")),
        "open_state_multiplier": int(_non_negative("open_state_multiplier")),
        "extensions": _safe_extensions(payload),
    }


def portal_flow_param_rows_by_portal_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("portal_id", ""))):
        normalized = normalize_portal_flow_params(row)
        out[str(normalized.get("portal_id", ""))] = normalized
    return out


def normalize_leak_hazard(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    leak_id = str(payload.get("leak_id", "")).strip()
    volume_id = str(payload.get("volume_id", "")).strip()
    hazard_model_id = str(payload.get("hazard_model_id", "")).strip()
    if not leak_id or not volume_id or not hazard_model_id:
        raise CompartmentFlowBuilderError(
            REFUSAL_INTERIOR_FLOW_INVALID,
            "leak_hazard requires leak_id, volume_id, hazard_model_id",
            {
                "leak_id": leak_id,
                "volume_id": volume_id,
                "hazard_model_id": hazard_model_id,
            },
        )
    return {
        "schema_version": "1.0.0",
        "leak_id": leak_id,
        "volume_id": volume_id,
        "leak_rate_air": max(0, _as_int(payload.get("leak_rate_air", 0), 0)),
        "leak_rate_water": max(0, _as_int(payload.get("leak_rate_water", 0), 0)),
        "hazard_model_id": hazard_model_id,
        "extensions": _safe_extensions(payload),
    }


def leak_hazard_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("leak_id", ""))):
        normalized = normalize_leak_hazard(row)
        out[str(normalized.get("leak_id", ""))] = normalized
    return out


def compartment_flow_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("policies")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "flow_solver_policy_id": str(row.get("flow_solver_policy_id", "flow.coarse_default")).strip() or "flow.coarse_default",
            "update_interval_ticks": max(0, _as_int(row.get("update_interval_ticks", 1), 1)),
            "max_substep_ticks": max(0, _as_int(row.get("max_substep_ticks", 16), 16)),
            "strict_budget": bool(row.get("strict_budget", False)),
            "max_channels_per_tick": max(0, _as_int(row.get("max_channels_per_tick", 1024), 1024)),
            "max_hazards_per_tick": max(0, _as_int(row.get("max_hazards_per_tick", 1024), 1024)),
            "pressure_warn_threshold": max(0, _as_int(row.get("pressure_warn_threshold", 200), 200)),
            "pressure_danger_threshold": max(0, _as_int(row.get("pressure_danger_threshold", 100), 100)),
            "oxygen_warn_fraction": max(0, _as_int(row.get("oxygen_warn_fraction", 190), 190)),
            "oxygen_danger_fraction": max(0, _as_int(row.get("oxygen_danger_fraction", 150), 150)),
            "smoke_warn_density": max(0, _as_int(row.get("smoke_warn_density", 200), 200)),
            "smoke_danger_density": max(0, _as_int(row.get("smoke_danger_density", 450), 450)),
            "flood_warn_volume": max(0, _as_int(row.get("flood_warn_volume", 250), 250)),
            "flood_danger_volume": max(0, _as_int(row.get("flood_danger_volume", 700), 700)),
            "movement_slow_flood_volume": max(0, _as_int(row.get("movement_slow_flood_volume", 350), 350)),
            "movement_block_flood_volume": max(0, _as_int(row.get("movement_block_flood_volume", 850), 850)),
            "extensions": _safe_extensions(row),
        }
    return out


def portal_flow_template_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("templates")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("templates")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("template_id", ""))):
        template_id = str(row.get("template_id", "")).strip()
        if not template_id:
            continue
        out[template_id] = {
            "schema_version": "1.0.0",
            "template_id": template_id,
            "description": str(row.get("description", "")).strip(),
            "portal_type_id": str(row.get("portal_type_id", "")).strip(),
            "conductance_air": max(0, _as_int(row.get("conductance_air", 0), 0)),
            "conductance_water": max(0, _as_int(row.get("conductance_water", 0), 0)),
            "conductance_smoke": max(0, _as_int(row.get("conductance_smoke", 0), 0)),
            "sealing_coefficient": max(0, _as_int(row.get("sealing_coefficient", 0), 0)),
            "open_state_multiplier": max(0, _as_int(row.get("open_state_multiplier", 1000), 1000)),
            "extensions": _safe_extensions(row),
        }
    return out


def _state_machine_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("machine_id", ""))):
        machine_id = str(row.get("machine_id", "")).strip()
        if not machine_id:
            continue
        try:
            normalized = normalize_state_machine(row)
        except StateMachineError:
            continue
        out[machine_id] = normalized
    return out


def _portal_state_id(portal_row: Mapping[str, object], state_rows_by_id: Mapping[str, object]) -> str:
    portal = dict(portal_row or {})
    machine_id = str(portal.get("state_machine_id", "")).strip()
    machine = dict(state_rows_by_id.get(machine_id) or {})
    if machine:
        token = str(machine.get("state_id", "")).strip()
        if token:
            return token
    ext = _safe_extensions(portal)
    token = str(ext.get("state_id", "")).strip()
    if token:
        return token
    return "open"


def _template_for_portal(*, portal_row: Mapping[str, object], template_rows_by_id: Mapping[str, object]) -> dict:
    portal = dict(portal_row or {})
    ext = _safe_extensions(portal)
    template_id = str(ext.get("flow_template_id", "")).strip()
    if not template_id:
        template_id = _DEFAULT_TEMPLATE_BY_PORTAL_TYPE.get(str(portal.get("portal_type_id", "")).strip(), "")
    row = dict(template_rows_by_id.get(template_id) or {})
    if row:
        return row
    # Deterministic fallback if template registry is absent.
    return {
        "schema_version": "1.0.0",
        "template_id": "template.fallback",
        "portal_type_id": str(portal.get("portal_type_id", "")).strip(),
        "conductance_air": 0,
        "conductance_water": 0,
        "conductance_smoke": 0,
        "sealing_coefficient": max(0, _as_int(portal.get("sealing_coefficient", 0), 0)),
        "open_state_multiplier": 1000,
        "extensions": {},
    }


def _effective_conductance(*, base_value: int, sealing_coefficient: int, open_state_multiplier: int, state_id: str, fixed_point_scale: int) -> int:
    scale = max(1, _as_int(fixed_point_scale, 1000))
    base = max(0, _as_int(base_value, 0))
    sealing = max(0, min(scale, _as_int(sealing_coefficient, 0)))
    open_mul = max(0, _as_int(open_state_multiplier, scale))
    state = str(state_id).strip().lower()
    if state in _DAMAGED_STATES:
        breach_factor = max(scale, scale + (scale - sealing))
        return int((base * breach_factor) // scale)
    if state in _OPEN_STATES:
        return int((base * open_mul) // scale)
    closed_factor = max(0, scale - sealing)
    return int((base * closed_factor) // scale)


def _channel_id(seed: Mapping[str, object]) -> str:
    return "channel.interior.{}".format(canonical_sha256(dict(seed))[:24])


def _directed_channel(
    *,
    graph_id: str,
    source_node_id: str,
    sink_node_id: str,
    edge_id: str,
    medium_id: str,
    quantity_id: str,
    capacity_per_tick: int,
    solver_policy_id: str,
    sequence: int,
    priority: int,
    route_edge_ids: List[str],
) -> dict:
    seed = {
        "graph_id": str(graph_id),
        "source_node_id": str(source_node_id),
        "sink_node_id": str(sink_node_id),
        "edge_id": str(edge_id),
        "medium_id": str(medium_id),
        "sequence": int(max(0, _as_int(sequence, 0))),
    }
    channel_id = _channel_id(seed)
    return normalize_flow_channel(
        {
            "schema_version": "1.0.0",
            "channel_id": channel_id,
            "graph_id": str(graph_id),
            "quantity_id": str(quantity_id),
            "source_node_id": str(source_node_id),
            "sink_node_id": str(sink_node_id),
            "capacity_per_tick": max(0, _as_int(capacity_per_tick, 0)),
            "delay_ticks": 0,
            "loss_fraction": 0,
            "solver_policy_id": str(solver_policy_id).strip() or "flow.coarse_default",
            "priority": int(max(0, _as_int(priority, 0))),
            "extensions": {
                "source_subsystem": "interior.compartment_flow",
                "medium_id": str(medium_id),
                "edge_id": str(edge_id),
                "route_edge_ids": _sorted_unique_strings(route_edge_ids),
                "route_node_ids": [str(source_node_id), str(sink_node_id)],
            },
        }
    )


def build_compartment_flow_channels(
    *,
    interior_graph_row: Mapping[str, object],
    volume_rows: object,
    portal_rows: object,
    portal_state_rows: object | None,
    portal_flow_param_rows: object | None,
    leak_hazard_rows: object | None,
    portal_flow_template_registry: Mapping[str, object] | None,
    flow_solver_policy_id: str,
    fixed_point_scale: int = 1000,
    include_smoke: bool = True,
) -> dict:
    """Build deterministic FlowChannels for compartment air/water/smoke transfer."""

    graph = normalize_interior_graph(interior_graph_row)
    volume_index = volume_rows_by_id(volume_rows)
    portal_index = portal_rows_by_id(portal_rows, volume_rows=volume_index)
    state_rows_by_id = _state_machine_rows_by_id(portal_state_rows)
    param_rows_by_portal = portal_flow_param_rows_by_portal_id(portal_flow_param_rows)
    leak_rows_by_id = leak_hazard_rows_by_id(leak_hazard_rows)
    template_rows_by_id = portal_flow_template_rows_by_id(portal_flow_template_registry)

    graph_volume_ids = [
        token for token in _sorted_unique_strings(list(graph.get("volumes") or []))
        if token in set(volume_index.keys())
    ]
    graph_portal_ids = [
        token for token in _sorted_unique_strings(list(graph.get("portals") or []))
        if token in set(portal_index.keys())
    ]

    node_ids = list(graph_volume_ids)
    channels: List[dict] = []
    route_edges: List[dict] = []
    scale = max(1, _as_int(fixed_point_scale, 1000))

    medium_rows = [
        ("air", "quantity.mass", "conductance_air", 100),
        ("water", "quantity.mass", "conductance_water", 200),
    ]
    if include_smoke:
        medium_rows.append(("smoke", "quantity.mass", "conductance_smoke", 300))

    sequence = 0
    for portal_id in graph_portal_ids:
        portal = dict(portal_index.get(portal_id) or {})
        if not portal:
            continue
        from_volume_id = str(portal.get("from_volume_id", "")).strip()
        to_volume_id = str(portal.get("to_volume_id", "")).strip()
        if from_volume_id not in set(graph_volume_ids) or to_volume_id not in set(graph_volume_ids):
            continue

        template = _template_for_portal(portal_row=portal, template_rows_by_id=template_rows_by_id)
        override = dict(param_rows_by_portal.get(portal_id) or {})
        state_id = _portal_state_id(portal, state_rows_by_id)
        sealing = max(
            0,
            _as_int(
                override.get("sealing_coefficient", template.get("sealing_coefficient", portal.get("sealing_coefficient", 0))),
                0,
            ),
        )
        open_multiplier = max(
            0,
            _as_int(
                override.get("open_state_multiplier", template.get("open_state_multiplier", scale)),
                scale,
            ),
        )
        for medium_id, quantity_id, conductance_key, priority_base in medium_rows:
            base_conductance = max(
                0,
                _as_int(
                    override.get(conductance_key, template.get(conductance_key, 0)),
                    0,
                ),
            )
            effective = _effective_conductance(
                base_value=base_conductance,
                sealing_coefficient=sealing,
                open_state_multiplier=open_multiplier,
                state_id=state_id,
                fixed_point_scale=scale,
            )
            route_edges.append(
                {
                    "edge_id": "interior.edge.portal.{}".format(portal_id),
                    "from_node_id": from_volume_id,
                    "to_node_id": to_volume_id,
                }
            )
            channels.append(
                _directed_channel(
                    graph_id=str(graph.get("graph_id", "")).strip(),
                    source_node_id=from_volume_id,
                    sink_node_id=to_volume_id,
                    edge_id="interior.edge.portal.{}".format(portal_id),
                    medium_id=medium_id,
                    quantity_id=quantity_id,
                    capacity_per_tick=effective,
                    solver_policy_id=flow_solver_policy_id,
                    sequence=sequence,
                    priority=int(priority_base),
                    route_edge_ids=["interior.edge.portal.{}".format(portal_id)],
                )
            )
            sequence += 1
            channels.append(
                _directed_channel(
                    graph_id=str(graph.get("graph_id", "")).strip(),
                    source_node_id=to_volume_id,
                    sink_node_id=from_volume_id,
                    edge_id="interior.edge.portal.{}".format(portal_id),
                    medium_id=medium_id,
                    quantity_id=quantity_id,
                    capacity_per_tick=effective,
                    solver_policy_id=flow_solver_policy_id,
                    sequence=sequence,
                    priority=int(priority_base),
                    route_edge_ids=["interior.edge.portal.{}".format(portal_id)],
                )
            )
            sequence += 1

    leak_rows = sorted(
        (dict(leak_rows_by_id[key]) for key in leak_rows_by_id.keys()),
        key=lambda row: str(row.get("leak_id", "")),
    )
    if leak_rows:
        node_ids.append(_OUTSIDE_NODE_ID)

    for leak in leak_rows:
        leak_id = str(leak.get("leak_id", "")).strip()
        volume_id = str(leak.get("volume_id", "")).strip()
        if volume_id not in set(graph_volume_ids):
            continue
        edge_id = "interior.edge.leak.{}".format(leak_id)
        route_edges.append(
            {
                "edge_id": edge_id,
                "from_node_id": volume_id,
                "to_node_id": _OUTSIDE_NODE_ID,
            }
        )
        leak_air = max(0, _as_int(leak.get("leak_rate_air", 0), 0))
        leak_water = max(0, _as_int(leak.get("leak_rate_water", 0), 0))
        leak_smoke = int(leak_air)

        leak_medium_rows = [
            ("air", "quantity.mass", leak_air, 400),
            ("water", "quantity.mass", leak_water, 500),
        ]
        if include_smoke:
            leak_medium_rows.append(("smoke", "quantity.mass", leak_smoke, 600))
        for medium_id, quantity_id, capacity, priority in leak_medium_rows:
            channels.append(
                _directed_channel(
                    graph_id=str(graph.get("graph_id", "")).strip(),
                    source_node_id=volume_id,
                    sink_node_id=_OUTSIDE_NODE_ID,
                    edge_id=edge_id,
                    medium_id=medium_id,
                    quantity_id=quantity_id,
                    capacity_per_tick=capacity,
                    solver_policy_id=flow_solver_policy_id,
                    sequence=sequence,
                    priority=int(priority),
                    route_edge_ids=[edge_id],
                )
            )
            sequence += 1

    channel_rows = sorted(
        channels,
        key=lambda row: (
            str(row.get("channel_id", "")),
            str((dict(row.get("extensions") or {})).get("medium_id", "")),
            int(_as_int(row.get("priority", 0), 0)),
        ),
    )
    medium_channel_ids: Dict[str, List[str]] = {}
    for row in channel_rows:
        ext = dict(row.get("extensions") or {})
        medium_id = str(ext.get("medium_id", "")).strip() or "air"
        medium_channel_ids.setdefault(medium_id, []).append(str(row.get("channel_id", "")).strip())
    medium_channel_ids = dict((key, sorted(medium_channel_ids[key])) for key in sorted(medium_channel_ids.keys()))

    return {
        "graph_id": str(graph.get("graph_id", "")).strip(),
        "volume_ids": list(graph_volume_ids),
        "node_ids": sorted(set(node_ids)),
        "outside_node_id": _OUTSIDE_NODE_ID if leak_rows else None,
        "channels": channel_rows,
        "channel_count": len(channel_rows),
        "medium_channel_ids": medium_channel_ids,
        "route_edges": sorted(
            (
                {
                    "edge_id": str(row.get("edge_id", "")).strip(),
                    "from_node_id": str(row.get("from_node_id", "")).strip(),
                    "to_node_id": str(row.get("to_node_id", "")).strip(),
                }
                for row in route_edges
                if str(row.get("edge_id", "")).strip()
            ),
            key=lambda row: (str(row.get("edge_id", "")), str(row.get("from_node_id", "")), str(row.get("to_node_id", ""))),
        ),
        "deterministic_fingerprint": canonical_sha256(
            {
                "graph_id": str(graph.get("graph_id", "")).strip(),
                "volume_ids": list(graph_volume_ids),
                "channel_ids": [str(row.get("channel_id", "")).strip() for row in channel_rows],
                "outside_node_id": _OUTSIDE_NODE_ID if leak_rows else None,
            }
        ),
    }


__all__ = [
    "CompartmentFlowBuilderError",
    "REFUSAL_INTERIOR_FLOW_INVALID",
    "build_compartment_flow_channels",
    "compartment_flow_policy_rows_by_id",
    "compartment_state_rows_by_volume_id",
    "leak_hazard_rows_by_id",
    "normalize_compartment_state",
    "normalize_leak_hazard",
    "normalize_portal_flow_params",
    "portal_flow_param_rows_by_portal_id",
    "portal_flow_template_rows_by_id",
]
