"""FAST test: legacy scalar flow behavior is unchanged after bundle upgrade."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_legacy_flow_behavior_unchanged"
TEST_TAGS = ["fast", "core", "flow", "compat"]


def _solver() -> dict:
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


def _channel() -> dict:
    return {
        "schema_version": "1.0.0",
        "channel_id": "flow.channel.legacy.compat",
        "graph_id": "graph.flow.compat",
        "quantity_id": "quantity.mass",
        "source_node_id": "node.source",
        "sink_node_id": "node.sink",
        "capacity_per_tick": 400,
        "delay_ticks": 0,
        "loss_fraction": 100,
        "solver_policy_id": "flow.coarse_default",
        "priority": 0,
        "extensions": {},
    }


def _run_once(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.core.flow.flow_engine import tick_flow_channels

    return tick_flow_channels(
        channels=[_channel()],
        node_balances={"node.source": 500, "node.sink": 0},
        current_tick=12,
        fixed_point_scale=1000,
        solver_policies=_solver(),
        conserved_quantity_ids=["quantity.mass"],
        max_channels=1,
        strict_budget=False,
        sink_capacities={},
        channel_runtime={},
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
    )


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if first != second:
        return {"status": "fail", "message": "legacy scalar flow output diverged across equivalent runs"}
    event_rows = list(first.get("transfer_events") or [])
    if len(event_rows) != 1:
        return {"status": "fail", "message": "expected exactly one legacy transfer event"}
    event = dict(event_rows[0])
    if str(event.get("schema_version", "")) != "1.0.0":
        return {"status": "fail", "message": "legacy transfer event should remain schema_version 1.0.0"}
    if dict(event.get("transferred_components") or {}):
        return {"status": "fail", "message": "legacy transfer event unexpectedly emitted transferred_components"}
    if dict(event.get("lost_components") or {}):
        return {"status": "fail", "message": "legacy transfer event unexpectedly emitted lost_components"}
    result_rows = list(first.get("channel_results") or [])
    row = dict(result_rows[0] if result_rows else {})
    if int(row.get("transferred_amount", -1)) != 360:
        return {"status": "fail", "message": "legacy transferred_amount changed"}
    if int(row.get("lost_amount", -1)) != 40:
        return {"status": "fail", "message": "legacy lost_amount changed"}
    if int(row.get("deferred_amount", -1)) != 0:
        return {"status": "fail", "message": "legacy deferred_amount changed"}
    if first != copy.deepcopy(first):
        return {"status": "fail", "message": "legacy flow result must be deep-copy stable"}
    return {"status": "pass", "message": "legacy scalar flow behavior unchanged"}
