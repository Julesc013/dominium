"""FAST test: INT-2 portal state transitions affect compartment flow conductance."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.interior.portal_open_close_affects_flow"
TEST_TAGS = ["fast", "interior", "flow", "portal"]


def _air_capacity_sum(channels: list[dict]) -> int:
    total = 0
    for row in channels:
        if not isinstance(row, dict):
            continue
        ext = dict(row.get("extensions") or {})
        if str(ext.get("medium_id", "")).strip() != "air":
            continue
        total += int(row.get("capacity_per_tick", 0) or 0)
    return int(total)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from interior_testlib import interior_graph, portal_flow_template_registry, portal_rows, portal_state_rows, volume_rows
    from src.interior.compartment_flow_builder import build_compartment_flow_channels

    open_build = build_compartment_flow_channels(
        interior_graph_row=interior_graph(),
        volume_rows=volume_rows(),
        portal_rows=portal_rows(),
        portal_state_rows=portal_state_rows(state_id="open"),
        portal_flow_param_rows=[],
        leak_hazard_rows=[],
        portal_flow_template_registry=portal_flow_template_registry(),
        flow_solver_policy_id="flow.coarse_default",
        fixed_point_scale=1000,
        include_smoke=False,
    )
    closed_build = build_compartment_flow_channels(
        interior_graph_row=interior_graph(),
        volume_rows=volume_rows(),
        portal_rows=portal_rows(),
        portal_state_rows=portal_state_rows(state_id="closed"),
        portal_flow_param_rows=[],
        leak_hazard_rows=[],
        portal_flow_template_registry=portal_flow_template_registry(),
        flow_solver_policy_id="flow.coarse_default",
        fixed_point_scale=1000,
        include_smoke=False,
    )

    open_air = _air_capacity_sum(list(open_build.get("channels") or []))
    closed_air = _air_capacity_sum(list(closed_build.get("channels") or []))
    if open_air <= 0:
        return {"status": "fail", "message": "open portal should produce non-zero air conductance"}
    if closed_air >= open_air:
        return {"status": "fail", "message": "closed portal should reduce air conductance deterministically"}

    return {"status": "pass", "message": "portal open/close conductance impact passed"}
