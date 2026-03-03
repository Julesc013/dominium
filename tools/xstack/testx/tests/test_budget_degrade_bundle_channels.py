"""FAST test: bundle channels degrade deterministically under flow budget."""

from __future__ import annotations

import sys


TEST_ID = "test_budget_degrade_bundle_channels"
TEST_TAGS = ["fast", "core", "flow", "bundle", "budget"]


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


def _bundle_registry() -> dict:
    return {
        "quantity_bundles": [
            {
                "schema_version": "1.0.0",
                "bundle_id": "bundle.power_phasor",
                "quantity_ids": ["quantity.power.p", "quantity.power.q", "quantity.power.s"],
                "description": "phasor bundle",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }


def _channels() -> list[dict]:
    rows = []
    for token in ("a", "b", "c"):
        rows.append(
            {
                "schema_version": "1.1.0",
                "channel_id": "flow.channel.bundle.{}.budget".format(token),
                "graph_id": "graph.flow.bundle.budget",
                "quantity_bundle_id": "bundle.power_phasor",
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


def _run_once(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.core.flow.flow_engine import tick_flow_channels

    return tick_flow_channels(
        channels=_channels(),
        node_balances=_balances(),
        current_tick=40,
        fixed_point_scale=1000,
        solver_policies=_solver(),
        conserved_quantity_ids=["quantity.power.p", "quantity.power.q", "quantity.power.s"],
        max_channels=2,
        strict_budget=False,
        sink_capacities={},
        channel_runtime={},
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
        quantity_bundle_rows=_bundle_registry(),
        component_capacity_policies={},
        component_loss_policies={},
    )


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if first != second:
        return {"status": "fail", "message": "bundle budget degradation diverged across equivalent runs"}
    if str(first.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome for bundle channels"}
    result_rows = list(first.get("channel_results") or [])
    channel_ids = [str(dict(row).get("channel_id", "")) for row in result_rows]
    expected = ["flow.channel.bundle.a.budget", "flow.channel.bundle.b.budget"]
    if channel_ids != expected:
        return {"status": "fail", "message": "bundle channel processing order mismatch under budget"}
    for row in result_rows:
        if not dict(dict(row).get("transferred_components") or {}):
            return {"status": "fail", "message": "processed bundle channel missing transferred_components"}
    return {"status": "pass", "message": "bundle budget degradation deterministic"}
