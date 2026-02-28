"""FAST test: flow loss handling is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.flow_loss_deterministic"
TEST_TAGS = ["fast", "core", "flow", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.flow.flow_engine import tick_flow_channels

    channel = {
        "schema_version": "1.0.0",
        "channel_id": "flow.channel.loss.alpha",
        "graph_id": "graph.flow.loss.alpha",
        "quantity_id": "quantity.mass",
        "source_node_id": "node.source",
        "sink_node_id": "node.sink",
        "capacity_per_tick": None,
        "delay_ticks": 0,
        "loss_fraction": 100,
        "solver_policy_id": "flow.coarse_default",
        "priority": 0,
        "extensions": {},
    }
    solver = {
        "flow.coarse_default": {
            "schema_version": "1.0.0",
            "solver_policy_id": "flow.coarse_default",
            "mode": "bulk",
            "allow_partial_transfer": True,
            "overflow_policy": "queue",
            "extensions": {},
        }
    }
    result = tick_flow_channels(
        channels=[channel],
        node_balances={"node.source": 1000, "node.sink": 0},
        current_tick=5,
        fixed_point_scale=1000,
        solver_policies=solver,
        conserved_quantity_ids=["quantity.mass"],
        max_channels=4,
        strict_budget=False,
        sink_capacities={},
        channel_runtime={},
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
    )
    row = dict((list(result.get("channel_results") or [{}]) or [{}])[0])
    if int(row.get("transferred_amount", -1)) != 900:
        return {"status": "fail", "message": "flow loss deterministic transferred_amount mismatch"}
    if int(row.get("lost_amount", -1)) != 100:
        return {"status": "fail", "message": "flow loss deterministic lost_amount mismatch"}
    loss_rows = list(result.get("loss_entries") or [])
    if len(loss_rows) != 1:
        return {"status": "fail", "message": "expected one deterministic flow loss entry"}
    loss = dict(loss_rows[0])
    if int(loss.get("lost_amount", -1)) != 100 or not bool(loss.get("conserved", False)):
        return {"status": "fail", "message": "conserved flow loss row mismatch"}
    events = list(result.get("transfer_events") or [])
    if len(events) != 1:
        return {"status": "fail", "message": "expected one deterministic flow transfer event"}
    event = dict(events[0])
    if int(event.get("transferred_amount", -1)) != 900 or int(event.get("lost_amount", -1)) != 100:
        return {"status": "fail", "message": "flow transfer event amounts mismatch"}
    return {"status": "pass", "message": "flow loss deterministic behavior passed"}

