"""FAST test: bundle loss can deterministically transform into heat quantity."""

from __future__ import annotations

import sys


TEST_ID = "test_transform_loss_to_heat"
TEST_TAGS = ["fast", "core", "flow", "bundle", "ledger"]


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
                "bundle_id": "bundle.thermal_basic",
                "quantity_ids": ["quantity.flow", "quantity.heat_loss"],
                "description": "thermal bundle",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }


def _loss_policy_registry() -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "policy_id": "loss.transform.to_heat",
                "per_quantity_rules": {
                    "quantity.flow": {
                        "transform_to_quantity_id": "quantity.heat_loss",
                        "preserve_conservation": True,
                    }
                },
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }


def _run_once(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.core.flow.flow_engine import tick_flow_channels

    return tick_flow_channels(
        channels=[
            {
                "schema_version": "1.1.0",
                "channel_id": "flow.channel.bundle.heat.transform",
                "graph_id": "graph.flow.bundle",
                "quantity_bundle_id": "bundle.thermal_basic",
                "component_loss_policy_id": "loss.transform.to_heat",
                "source_node_id": "node.source",
                "sink_node_id": "node.sink",
                "capacity_per_tick": 100,
                "delay_ticks": 0,
                "loss_fraction": 200,
                "solver_policy_id": "flow.coarse_default",
                "priority": 0,
                "extensions": {
                    "component_weights": {
                        "quantity.flow": 1000,
                        "quantity.heat_loss": 0,
                    }
                },
            }
        ],
        node_balances={"node.source": 100, "node.sink": 0},
        current_tick=31,
        fixed_point_scale=1000,
        solver_policies=_solver(),
        conserved_quantity_ids=["quantity.flow", "quantity.heat_loss"],
        max_channels=1,
        strict_budget=False,
        sink_capacities={},
        channel_runtime={},
        graph_row=None,
        partition_row=None,
        cost_units_per_channel=1,
        quantity_bundle_rows=_bundle_registry(),
        component_capacity_policies={},
        component_loss_policies=_loss_policy_registry(),
    )


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if first != second:
        return {"status": "fail", "message": "loss transform behavior diverged across equivalent runs"}
    transform_rows = list(first.get("loss_transform_rows") or [])
    if not transform_rows:
        return {"status": "fail", "message": "expected deterministic loss_transform_rows output"}
    row = dict(transform_rows[0])
    if str(row.get("from_quantity_id", "")) != "quantity.flow":
        return {"status": "fail", "message": "unexpected transform source quantity"}
    if str(row.get("to_quantity_id", "")) != "quantity.heat_loss":
        return {"status": "fail", "message": "unexpected transform target quantity"}
    if int(row.get("amount", 0)) <= 0:
        return {"status": "fail", "message": "transform amount should be positive"}
    return {"status": "pass", "message": "loss-to-heat transform deterministic"}
