"""FAST test: INT-2 compartment flow builder output is deterministic."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "testx.interior.flow_builder_deterministic"
TEST_TAGS = ["fast", "interior", "flow", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from interior_testlib import (
        interior_graph,
        portal_flow_template_registry,
        portal_rows,
        portal_state_rows,
        volume_rows,
    )
    from src.interior.compartment_flow_builder import build_compartment_flow_channels
    from tools.xstack.compatx.canonical_json import canonical_sha256

    graph = interior_graph()
    volumes = volume_rows()
    portals = portal_rows()
    portal_states = portal_state_rows(state_id="open")
    templates = portal_flow_template_registry()

    first = build_compartment_flow_channels(
        interior_graph_row=graph,
        volume_rows=copy.deepcopy(volumes),
        portal_rows=copy.deepcopy(portals),
        portal_state_rows=copy.deepcopy(portal_states),
        portal_flow_param_rows=[],
        leak_hazard_rows=[
            {
                "schema_version": "1.0.0",
                "leak_id": "leak.test.a",
                "volume_id": "volume.a",
                "leak_rate_air": 5,
                "leak_rate_water": 2,
                "hazard_model_id": "hazard.leak.test.a",
                "extensions": {},
            }
        ],
        portal_flow_template_registry=templates,
        flow_solver_policy_id="flow.coarse_default",
        fixed_point_scale=1000,
        include_smoke=True,
    )
    second = build_compartment_flow_channels(
        interior_graph_row=copy.deepcopy(graph),
        volume_rows=list(reversed(copy.deepcopy(volumes))),
        portal_rows=list(reversed(copy.deepcopy(portals))),
        portal_state_rows=copy.deepcopy(portal_states),
        portal_flow_param_rows=[],
        leak_hazard_rows=[
            {
                "schema_version": "1.0.0",
                "leak_id": "leak.test.a",
                "volume_id": "volume.a",
                "leak_rate_air": 5,
                "leak_rate_water": 2,
                "hazard_model_id": "hazard.leak.test.a",
                "extensions": {},
            }
        ],
        portal_flow_template_registry=copy.deepcopy(templates),
        flow_solver_policy_id="flow.coarse_default",
        fixed_point_scale=1000,
        include_smoke=True,
    )

    if first != second:
        return {"status": "fail", "message": "compartment flow builder diverged across equivalent inputs"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "compartment flow builder hash mismatch"}

    channels = list(first.get("channels") or [])
    if not channels:
        return {"status": "fail", "message": "compartment flow builder returned no channels"}
    channel_ids = [str(row.get("channel_id", "")).strip() for row in channels]
    if channel_ids != sorted(channel_ids):
        return {"status": "fail", "message": "compartment flow channels are not sorted deterministically"}
    if str(first.get("outside_node_id", "")).strip() != "interior.node.outside":
        return {"status": "fail", "message": "outside node was not included for leak channels"}

    return {"status": "pass", "message": "compartment flow builder deterministic output passed"}
