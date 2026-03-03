"""FAST test: bundle flow transfer is deterministic with component maps."""

from __future__ import annotations

import sys


TEST_ID = "test_bundle_transfer_deterministic"
TEST_TAGS = ["fast", "core", "flow", "bundle", "determinism"]


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


def _channel() -> dict:
    return {
        "schema_version": "1.1.0",
        "channel_id": "flow.channel.bundle.det",
        "graph_id": "graph.flow.bundle",
        "quantity_bundle_id": "bundle.power_phasor",
        "source_node_id": "node.source",
        "sink_node_id": "node.sink",
        "capacity_per_tick": 120,
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
        node_balances={"node.source": 150, "node.sink": 0},
        current_tick=22,
        fixed_point_scale=1000,
        solver_policies=_solver(),
        conserved_quantity_ids=["quantity.power.p", "quantity.power.q", "quantity.power.s"],
        max_channels=1,
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
        return {"status": "fail", "message": "bundle flow output diverged across equivalent runs"}
    event_rows = list(first.get("transfer_events") or [])
    if len(event_rows) != 1:
        return {"status": "fail", "message": "expected one bundle transfer event"}
    event = dict(event_rows[0])
    if str(event.get("schema_version", "")) != "1.1.0":
        return {"status": "fail", "message": "bundle transfer event must use schema_version 1.1.0"}
    transferred_components = dict(event.get("transferred_components") or {})
    lost_components = dict(event.get("lost_components") or {})
    if sorted(transferred_components.keys()) != ["quantity.power.p", "quantity.power.q", "quantity.power.s"]:
        return {"status": "fail", "message": "bundle transfer missing expected transferred component keys"}
    if sorted(lost_components.keys()) != ["quantity.power.p", "quantity.power.q", "quantity.power.s"]:
        return {"status": "fail", "message": "bundle transfer missing expected lost component keys"}
    if sum(int(v) for v in transferred_components.values()) != int(event.get("transferred_amount", -1)):
        return {"status": "fail", "message": "transferred component sum mismatch"}
    if sum(int(v) for v in lost_components.values()) != int(event.get("lost_amount", -1)):
        return {"status": "fail", "message": "lost component sum mismatch"}
    return {"status": "pass", "message": "bundle transfer deterministic"}
