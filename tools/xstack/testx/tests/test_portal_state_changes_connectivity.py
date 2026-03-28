"""FAST test: portal state-machine transitions deterministically change connectivity."""

from __future__ import annotations

import sys


TEST_ID = "testx.interior.portal_state_changes_connectivity"
TEST_TAGS = ["fast", "interior", "state_machine", "connectivity"]


def _volume(volume_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "volume_id": volume_id,
        "parent_spatial_id": "spatial.site.beta",
        "local_transform": {
            "translation_mm": {"x": 0, "y": 0, "z": 0},
            "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "scale_permille": 1000,
        },
        "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 1000, "y": 1000, "z": 1000}}},
        "volume_type_id": "volume.room",
        "tags": [],
        "extensions": {},
    }


def _portal_state_machine(state_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "machine_id": "state.portal.alpha",
        "machine_type_id": "state_machine.portal",
        "state_id": state_id,
        "transitions": ["transition.portal.open_to_closed", "transition.portal.closed_to_open"],
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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from interior.interior_engine import apply_portal_transition, path_exists

    graph = {
        "schema_version": "1.0.0",
        "graph_id": "interior.graph.beta",
        "volumes": ["volume.a", "volume.b"],
        "portals": ["portal.ab"],
        "extensions": {},
    }
    volumes = [_volume("volume.a"), _volume("volume.b")]
    portal = {
        "schema_version": "1.0.0",
        "portal_id": "portal.ab",
        "from_volume_id": "volume.a",
        "to_volume_id": "volume.b",
        "portal_type_id": "portal.door",
        "state_machine_id": "state.portal.alpha",
        "sealing_coefficient": 800,
        "tags": [],
        "extensions": {},
    }

    closed_state = [_portal_state_machine("closed")]
    if path_exists(
        graph_row=graph,
        volume_rows=volumes,
        portal_rows=[portal],
        from_volume_id="volume.a",
        to_volume_id="volume.b",
        portal_state_rows=closed_state,
    ):
        return {"status": "fail", "message": "closed portal must block connectivity"}

    transition = apply_portal_transition(
        portal_row=portal,
        portal_state_rows=closed_state,
        trigger_process_id="process.portal_open",
        current_tick=10,
    )
    next_machine = dict(transition.get("state_machine") or {})
    if str(next_machine.get("state_id", "")).strip() != "open":
        return {"status": "fail", "message": "portal transition failed to open state"}

    if not path_exists(
        graph_row=graph,
        volume_rows=volumes,
        portal_rows=[dict(transition.get("portal") or {})],
        from_volume_id="volume.a",
        to_volume_id="volume.b",
        portal_state_rows=[next_machine],
    ):
        return {"status": "fail", "message": "open portal should enable connectivity"}
    return {"status": "pass", "message": "portal state transition connectivity behavior passed"}

