"""FAST test: component loss policy deterministically changes bundle loss distribution."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_component_loss_policy"
TEST_TAGS = ["fast", "core", "flow", "bundle", "policy"]


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


def _loss_policy_registry() -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "policy_id": "loss.q_heavy",
                "per_quantity_rules": {
                    "quantity.power.q": {"loss_fraction": 350},
                    "quantity.power.p": {"loss_fraction": 50},
                    "quantity.power.s": {"loss_fraction": 50},
                },
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }


def _base_channel() -> dict:
    return {
        "schema_version": "1.1.0",
        "channel_id": "flow.channel.bundle.loss.policy",
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


def _run(repo_root: str, *, with_policy: bool):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from core.flow.flow_engine import tick_flow_channels

    channel = _base_channel()
    if with_policy:
        channel["component_loss_policy_id"] = "loss.q_heavy"
    return tick_flow_channels(
        channels=[channel],
        node_balances={"node.source": 150, "node.sink": 0},
        current_tick=30,
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
        component_loss_policies=_loss_policy_registry() if with_policy else {},
    )


def run(repo_root: str):
    baseline = _run(repo_root, with_policy=False)
    with_policy_a = _run(repo_root, with_policy=True)
    with_policy_b = _run(repo_root, with_policy=True)
    if with_policy_a != with_policy_b:
        return {"status": "fail", "message": "component loss policy output is not deterministic"}
    base_event = dict((list(baseline.get("transfer_events") or [{}]) or [{}])[0])
    policy_event = dict((list(with_policy_a.get("transfer_events") or [{}]) or [{}])[0])
    base_lost = dict(base_event.get("lost_components") or {})
    policy_lost = dict(policy_event.get("lost_components") or {})
    if not base_lost or not policy_lost:
        return {"status": "fail", "message": "missing lost_components in bundle events"}
    if copy.deepcopy(base_lost) == copy.deepcopy(policy_lost):
        return {"status": "fail", "message": "component loss policy did not change loss distribution"}
    if int(policy_lost.get("quantity.power.q", 0)) < int(base_lost.get("quantity.power.q", 0)):
        return {"status": "fail", "message": "q-component should not lose less under q-heavy policy"}
    return {"status": "pass", "message": "component loss policy applied deterministically"}
