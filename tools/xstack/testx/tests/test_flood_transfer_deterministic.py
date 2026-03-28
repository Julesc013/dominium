"""FAST test: INT-2 flood transfer over compartment flows is deterministic."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "testx.interior.flood_transfer_deterministic"
TEST_TAGS = ["fast", "interior", "flow", "flood", "determinism"]


def _states() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.a",
            "air_mass": 1500,
            "water_volume": 1000,
            "temperature": None,
            "oxygen_fraction": 210,
            "smoke_density": 0,
            "derived_pressure": 0,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.b",
            "air_mass": 1500,
            "water_volume": 0,
            "temperature": None,
            "oxygen_fraction": 210,
            "smoke_density": 0,
            "derived_pressure": 0,
            "extensions": {},
        },
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from interior_testlib import (
        compartment_flow_policy_row,
        flow_solver_policy_registry,
        interior_graph,
        portal_flow_template_registry,
        portal_rows,
        portal_state_rows,
        volume_rows,
    )
    from interior.compartment_flow_engine import tick_compartment_flows
    from tools.xstack.compatx.canonical_json import canonical_sha256

    common_kwargs = {
        "interior_graph_row": interior_graph(),
        "volume_rows": volume_rows(),
        "portal_rows": portal_rows(),
        "portal_state_rows": portal_state_rows(state_id="open"),
        "portal_flow_param_rows": [],
        "leak_hazard_rows": [],
        "leak_hazard_models": [],
        "portal_flow_template_registry": portal_flow_template_registry(),
        "compartment_flow_policy_row": compartment_flow_policy_row(),
        "flow_solver_policy_registry": flow_solver_policy_registry(),
        "current_tick": 0,
        "dt_ticks": 6,
        "fixed_point_scale": 1000,
        "channel_runtime": {},
        "outside_reservoir": {},
        "include_smoke": False,
        "conserved_quantity_ids": ["quantity.mass"],
        "graph_partition_row": None,
        "cost_units_per_channel": 1,
        "cost_units_per_hazard": 1,
    }

    first = tick_compartment_flows(compartment_state_rows=_states(), **common_kwargs)
    second = tick_compartment_flows(compartment_state_rows=_states(), **common_kwargs)

    if first != second:
        return {"status": "fail", "message": "flood transfer tick diverged across equivalent inputs"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "flood transfer hash mismatch"}

    state_rows = sorted(
        [dict(row) for row in list(first.get("states") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("volume_id", "")),
    )
    by_id = dict((str(row.get("volume_id", "")).strip(), row) for row in state_rows)

    a_water = int((dict(by_id.get("volume.a") or {})).get("water_volume", -1))
    b_water = int((dict(by_id.get("volume.b") or {})).get("water_volume", -1))
    if a_water >= 1000 or b_water <= 0:
        return {"status": "fail", "message": "water volume did not transfer across connected compartments"}
    if (a_water + b_water) != 1000:
        return {"status": "fail", "message": "flood transfer should preserve total water volume in closed compartments"}

    return {"status": "pass", "message": "compartment flood transfer deterministic behavior passed"}
