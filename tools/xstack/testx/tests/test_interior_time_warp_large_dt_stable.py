"""FAST test: INT-2 large dt compartment flow integration remains deterministic and stable."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "testx.interior.time_warp_large_dt_stable"
TEST_TAGS = ["fast", "interior", "flow", "time_warp", "determinism"]


def _states() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.a",
            "air_mass": 5000,
            "water_volume": 900,
            "temperature": None,
            "oxygen_fraction": 210,
            "smoke_density": 120,
            "derived_pressure": 0,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.b",
            "air_mass": 200,
            "water_volume": 10,
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

    kwargs = {
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
        "dt_ticks": 20000,
        "fixed_point_scale": 1000,
        "channel_runtime": {},
        "outside_reservoir": {},
        "include_smoke": True,
        "conserved_quantity_ids": ["quantity.mass"],
        "graph_partition_row": None,
        "cost_units_per_channel": 1,
        "cost_units_per_hazard": 1,
    }

    first = tick_compartment_flows(compartment_state_rows=_states(), **kwargs)
    second = tick_compartment_flows(compartment_state_rows=_states(), **kwargs)
    if first != second:
        return {"status": "fail", "message": "large dt compartment flow diverged across equivalent runs"}

    states = sorted(
        [dict(row) for row in list(first.get("states") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("volume_id", "")),
    )
    if len(states) != 2:
        return {"status": "fail", "message": "large dt compartment flow lost state rows"}
    for row in states:
        if int(row.get("air_mass", -1)) < 0:
            return {"status": "fail", "message": "air_mass became negative under large dt flow integration"}
        if int(row.get("water_volume", -1)) < 0:
            return {"status": "fail", "message": "water_volume became negative under large dt flow integration"}
        if int(row.get("smoke_density", -1)) < 0:
            return {"status": "fail", "message": "smoke_density became negative under large dt flow integration"}
        if int(row.get("derived_pressure", -1)) < 0:
            return {"status": "fail", "message": "derived_pressure became negative under large dt flow integration"}

    return {"status": "pass", "message": "large dt compartment flow stability passed"}
