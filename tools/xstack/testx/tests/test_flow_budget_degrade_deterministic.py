"""FAST test: flow budget degradation order is deterministic by channel_id."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.core.flow_budget_degrade_deterministic"
TEST_TAGS = ["fast", "core", "flow", "budget", "determinism"]


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


def _channels() -> list[dict]:
    rows = []
    for token in ("a", "b", "c"):
        rows.append(
            {
                "schema_version": "1.0.0",
                "channel_id": "flow.channel.{}.budget".format(token),
                "graph_id": "graph.flow.budget",
                "quantity_id": "quantity.mass",
                "source_node_id": "node.source.{}".format(token),
                "sink_node_id": "node.sink.{}".format(token),
                "capacity_per_tick": 100,
                "delay_ticks": 0,
                "loss_fraction": 0,
                "solver_policy_id": "flow.coarse_default",
                "priority": 0,
                "extensions": {},
            }
        )
    return rows


def _balances() -> dict:
    return {
        "node.source.a": 100,
        "node.source.b": 100,
        "node.source.c": 100,
        "node.sink.a": 0,
        "node.sink.b": 0,
        "node.sink.c": 0,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.flow.flow_engine import tick_flow_channels

    first = tick_flow_channels(
        channels=_channels(),
        node_balances=copy.deepcopy(_balances()),
        current_tick=9,
        fixed_point_scale=1000,
        solver_policies=_solver(),
        conserved_quantity_ids=["quantity.mass"],
        max_channels=2,
        strict_budget=False,
        sink_capacities={},
        channel_runtime={},
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
    )
    second = tick_flow_channels(
        channels=_channels(),
        node_balances=copy.deepcopy(_balances()),
        current_tick=9,
        fixed_point_scale=1000,
        solver_policies=_solver(),
        conserved_quantity_ids=["quantity.mass"],
        max_channels=2,
        strict_budget=False,
        sink_capacities={},
        channel_runtime={},
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
    )
    if first != second:
        return {"status": "fail", "message": "budget-degraded flow tick diverged across equivalent runs"}
    if int(first.get("processed_count", -1)) != 2 or int(first.get("remaining_count", -1)) != 1:
        return {"status": "fail", "message": "flow budget degrade counters mismatch"}
    if str(first.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "flow budget outcome should be degraded"}
    channel_ids = [str(dict(row).get("channel_id", "")) for row in list(first.get("channel_results") or [])]
    if channel_ids != sorted(channel_ids) or channel_ids != ["flow.channel.a.budget", "flow.channel.b.budget"]:
        return {"status": "fail", "message": "flow budget deterministic channel processing order mismatch"}
    return {"status": "pass", "message": "flow budget degradation deterministic order passed"}

