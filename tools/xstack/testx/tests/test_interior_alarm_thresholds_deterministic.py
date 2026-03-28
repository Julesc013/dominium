"""FAST test: INT-3 interior alarm thresholds are deterministic."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "testx.interior.interior_alarm_thresholds_deterministic"
TEST_TAGS = ["fast", "interior", "diegetics", "determinism"]


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

    states = [
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.a",
            "air_mass": 50,
            "water_volume": 900,
            "temperature": None,
            "oxygen_fraction": 140,
            "smoke_density": 900,
            "derived_pressure": 0,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.b",
            "air_mass": 20000,
            "water_volume": 0,
            "temperature": None,
            "oxygen_fraction": 210,
            "smoke_density": 0,
            "derived_pressure": 0,
            "extensions": {},
        },
    ]

    kwargs = {
        "interior_graph_row": interior_graph(),
        "volume_rows": volume_rows(),
        "portal_rows": portal_rows(),
        "portal_state_rows": portal_state_rows(state_id="open"),
        "compartment_state_rows": states,
        "portal_flow_param_rows": [],
        "leak_hazard_rows": [],
        "leak_hazard_models": [],
        "portal_flow_template_registry": portal_flow_template_registry(),
        "compartment_flow_policy_row": compartment_flow_policy_row(),
        "flow_solver_policy_registry": flow_solver_policy_registry(),
        "current_tick": 10,
        "dt_ticks": 1,
        "fixed_point_scale": 1000,
        "channel_runtime": {},
        "outside_reservoir": {},
        "include_smoke": True,
    }

    first = tick_compartment_flows(**copy.deepcopy(kwargs))
    second = tick_compartment_flows(**copy.deepcopy(kwargs))

    if dict(first) != dict(second):
        return {"status": "fail", "message": "compartment alarm outputs diverged across identical inputs"}

    first_alarm = next(
        (dict(row) for row in list(first.get("alarm_summary") or []) if str(row.get("volume_id", "")) == "volume.a"),
        {},
    )
    if str(first_alarm.get("overall", "")) != "DANGER":
        return {"status": "fail", "message": "expected volume.a overall alarm state DANGER under critical thresholds"}
    if str(first_alarm.get("smoke", "")) != "DANGER":
        return {"status": "fail", "message": "expected volume.a smoke alarm DANGER under critical thresholds"}

    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "compartment flow deterministic fingerprint mismatch"}

    return {"status": "pass", "message": "interior alarm thresholds deterministic"}
