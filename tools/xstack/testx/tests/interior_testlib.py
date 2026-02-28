"""Shared deterministic INT-2 fixtures for compartment flow tests."""

from __future__ import annotations


def interior_graph() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "interior.graph.test.alpha",
        "volumes": ["volume.a", "volume.b"],
        "portals": ["portal.ab"],
        "extensions": {},
    }


def volume(volume_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "volume_id": volume_id,
        "parent_spatial_id": "spatial.site.test",
        "local_transform": {
            "translation_mm": {"x": 0, "y": 0, "z": 0},
            "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "scale_permille": 1000,
        },
        "bounding_shape": {
            "shape_type": "aabb",
            "shape_data": {"half_extents_mm": {"x": 1000, "y": 1000, "z": 1000}},
        },
        "volume_type_id": "volume.room",
        "tags": [],
        "extensions": {},
    }


def volume_rows() -> list[dict]:
    return [volume("volume.a"), volume("volume.b")]


def portal_row(*, portal_type_id: str = "portal.door") -> dict:
    return {
        "schema_version": "1.0.0",
        "portal_id": "portal.ab",
        "from_volume_id": "volume.a",
        "to_volume_id": "volume.b",
        "portal_type_id": str(portal_type_id),
        "state_machine_id": "state.portal.ab",
        "sealing_coefficient": 900,
        "tags": [],
        "extensions": {},
    }


def portal_rows(*, portal_type_id: str = "portal.door") -> list[dict]:
    return [portal_row(portal_type_id=portal_type_id)]


def portal_state_rows(*, state_id: str = "open") -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "machine_id": "state.portal.ab",
            "machine_type_id": "state_machine.portal",
            "state_id": str(state_id),
            "transitions": [
                "transition.portal.open_to_closed",
                "transition.portal.closed_to_open",
            ],
            "transition_rows": [
                {
                    "schema_version": "1.0.0",
                    "transition_id": "transition.portal.open_to_closed",
                    "from_state": "open",
                    "to_state": "closed",
                    "trigger_process_id": "process.portal_close",
                    "guard_conditions": {},
                    "priority": 10,
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "transition_id": "transition.portal.closed_to_open",
                    "from_state": "closed",
                    "to_state": "open",
                    "trigger_process_id": "process.portal_open",
                    "guard_conditions": {},
                    "priority": 10,
                    "extensions": {},
                },
            ],
            "extensions": {},
        }
    ]


def portal_flow_template_registry() -> dict:
    return {
        "format_version": "1.0.0",
        "templates": [
            {
                "schema_version": "1.0.0",
                "template_id": "door_basic",
                "description": "test door",
                "portal_type_id": "portal.door",
                "conductance_air": 420,
                "conductance_water": 120,
                "conductance_smoke": 360,
                "sealing_coefficient": 820,
                "open_state_multiplier": 1000,
                "extensions": {},
            }
        ],
        "registry_hash": "",
    }


def flow_solver_policy_registry() -> dict:
    return {
        "flow.coarse_default": {
            "schema_version": "1.0.0",
            "solver_policy_id": "flow.coarse_default",
            "mode": "bulk",
            "allow_partial_transfer": True,
            "overflow_policy": "queue",
            "extensions": {},
        }
    }


def compartment_flow_policy_row() -> dict:
    return {
        "schema_version": "1.0.0",
        "policy_id": "flow.policy.default",
        "description": "test policy",
        "flow_solver_policy_id": "flow.coarse_default",
        "update_interval_ticks": 1,
        "max_substep_ticks": 16,
        "strict_budget": False,
        "max_channels_per_tick": 1024,
        "max_hazards_per_tick": 1024,
        "pressure_warn_threshold": 200,
        "pressure_danger_threshold": 100,
        "oxygen_warn_fraction": 190,
        "oxygen_danger_fraction": 150,
        "smoke_warn_density": 200,
        "smoke_danger_density": 450,
        "flood_warn_volume": 250,
        "flood_danger_volume": 700,
        "movement_slow_flood_volume": 350,
        "movement_block_flood_volume": 850,
        "extensions": {},
    }
