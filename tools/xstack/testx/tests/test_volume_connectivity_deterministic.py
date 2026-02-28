"""FAST test: interior volume connectivity queries are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.interior.volume_connectivity_deterministic"
TEST_TAGS = ["fast", "interior", "determinism", "connectivity"]


def _volume(volume_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "volume_id": volume_id,
        "parent_spatial_id": "spatial.site.alpha",
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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.interior.interior_engine import reachable_volumes
    from tools.xstack.compatx.canonical_json import canonical_sha256

    graph = {
        "schema_version": "1.0.0",
        "graph_id": "interior.graph.alpha",
        "volumes": ["volume.a", "volume.b", "volume.c"],
        "portals": ["portal.ab", "portal.bc"],
        "extensions": {},
    }
    volumes = [_volume("volume.a"), _volume("volume.b"), _volume("volume.c")]
    portals = [
        {
            "schema_version": "1.0.0",
            "portal_id": "portal.ab",
            "from_volume_id": "volume.a",
            "to_volume_id": "volume.b",
            "portal_type_id": "portal.door",
            "state_machine_id": "state.portal.ab",
            "sealing_coefficient": 900,
            "tags": [],
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "portal_id": "portal.bc",
            "from_volume_id": "volume.b",
            "to_volume_id": "volume.c",
            "portal_type_id": "portal.hatch",
            "state_machine_id": "state.portal.bc",
            "sealing_coefficient": 900,
            "tags": [],
            "extensions": {},
        },
    ]
    portal_states = [
        {
            "schema_version": "1.0.0",
            "machine_id": "state.portal.ab",
            "machine_type_id": "state_machine.portal",
            "state_id": "open",
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
        },
        {
            "schema_version": "1.0.0",
            "machine_id": "state.portal.bc",
            "machine_type_id": "state_machine.portal",
            "state_id": "open",
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
        },
    ]

    first = reachable_volumes(
        graph_row=graph,
        volume_rows=volumes,
        portal_rows=portals,
        start_volume_id="volume.a",
        portal_state_rows=portal_states,
    )
    second = reachable_volumes(
        graph_row=graph,
        volume_rows=volumes,
        portal_rows=portals,
        start_volume_id="volume.a",
        portal_state_rows=portal_states,
    )
    expected = ["volume.a", "volume.b", "volume.c"]
    if list(first.get("reachable_volume_ids") or []) != expected:
        return {"status": "fail", "message": "reachable volume set mismatch for deterministic baseline"}
    if first != second:
        return {"status": "fail", "message": "reachable_volumes diverged across equivalent inputs"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "reachable volume hash mismatch across equivalent runs"}
    return {"status": "pass", "message": "interior volume connectivity deterministic query passed"}

