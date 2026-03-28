"""FAST test: bulk FlowSystem channel transfer is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.core.flow_bulk_deterministic"
TEST_TAGS = ["fast", "core", "flow", "determinism"]


def _solver_policies() -> dict:
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
        "channel_id": "flow.channel.bulk.alpha",
        "graph_id": "graph.flow.bulk.alpha",
        "quantity_id": "quantity.mass",
        "source_node_id": "node.source",
        "sink_node_id": "node.sink",
        "capacity_per_tick": 600,
        "delay_ticks": 0,
        "loss_fraction": 0,
        "solver_policy_id": "flow.coarse_default",
        "priority": 0,
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from core.flow.flow_engine import tick_flow_channels
    from tools.xstack.compatx.canonical_json import canonical_sha256

    channels = [_channel()]
    node_balances = {"node.source": 1000, "node.sink": 0}
    runtime = {}
    first = tick_flow_channels(
        channels=channels,
        node_balances=copy.deepcopy(node_balances),
        current_tick=0,
        fixed_point_scale=1000,
        solver_policies=_solver_policies(),
        conserved_quantity_ids=["quantity.mass"],
        max_channels=8,
        strict_budget=False,
        sink_capacities={},
        channel_runtime=copy.deepcopy(runtime),
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
    )
    second = tick_flow_channels(
        channels=channels,
        node_balances=copy.deepcopy(node_balances),
        current_tick=0,
        fixed_point_scale=1000,
        solver_policies=_solver_policies(),
        conserved_quantity_ids=["quantity.mass"],
        max_channels=8,
        strict_budget=False,
        sink_capacities={},
        channel_runtime=copy.deepcopy(runtime),
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
    )
    if first != second:
        return {"status": "fail", "message": "bulk flow tick diverged across equivalent runs"}
    if int((dict(first.get("node_balances") or {})).get("node.source", -1)) != 400:
        return {"status": "fail", "message": "source debit mismatch in bulk deterministic transfer"}
    if int((dict(first.get("node_balances") or {})).get("node.sink", -1)) != 600:
        return {"status": "fail", "message": "sink credit mismatch in bulk deterministic transfer"}
    channel_results = list(first.get("channel_results") or [])
    if len(channel_results) != 1:
        return {"status": "fail", "message": "expected one channel result row"}
    row = dict(channel_results[0])
    if int(row.get("deferred_amount", -1)) != 400:
        return {"status": "fail", "message": "bulk flow deferred amount mismatch"}
    if int(first.get("processed_count", -1)) != 1 or int(first.get("remaining_count", -1)) != 0:
        return {"status": "fail", "message": "bulk flow processed/remaining counters mismatch"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "bulk flow result hash diverged"}
    return {"status": "pass", "message": "flow bulk deterministic transfer passed"}

