"""FAST test: fault evaluation budget degradation remains deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_budget_degrade_fault_eval_stable"
TEST_TAGS = ["fast", "electric", "fault", "budget", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from electric.fault.fault_engine import detect_faults

    edge_status_rows = [
        {
            "graph_id": "graph.elec.main",
            "edge_id": "edge.elec.main.1",
            "channel_id": "channel.elec.main.1",
            "P": 120,
            "Q": 30,
            "S": 130,
            "capacity_rating": 50,
            "overloaded": True,
        },
        {
            "graph_id": "graph.elec.main",
            "edge_id": "edge.elec.main.2",
            "channel_id": "channel.elec.main.2",
            "P": 90,
            "Q": 10,
            "S": 95,
            "capacity_rating": 40,
            "overloaded": True,
        },
    ]
    channel_rows = [
        {"channel_id": "channel.elec.main.1", "capacity_per_tick": 50, "extensions": {}},
        {"channel_id": "channel.elec.main.2", "capacity_per_tick": 40, "extensions": {}},
    ]
    grounding_policy_row = {
        "grounding_policy_id": "ground.basic_grounded",
        "default_mode": "grounded",
        "gfci_required": True,
        "fault_detection_rule_id": "rule.ground.imbalance_basic",
    }

    first = detect_faults(
        edge_status_rows=copy.deepcopy(edge_status_rows),
        channel_rows=copy.deepcopy(channel_rows),
        fault_rows=[],
        current_tick=17,
        max_fault_evals=1,
        grounding_policy_row=copy.deepcopy(grounding_policy_row),
        protection_settings_rows_by_target_id={},
    )
    second = detect_faults(
        edge_status_rows=copy.deepcopy(edge_status_rows),
        channel_rows=copy.deepcopy(channel_rows),
        fault_rows=[],
        current_tick=17,
        max_fault_evals=1,
        grounding_policy_row=copy.deepcopy(grounding_policy_row),
        protection_settings_rows_by_target_id={},
    )
    if first != second:
        return {"status": "fail", "message": "fault detection budget degradation diverged for equivalent inputs"}
    if str(first.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "fault budget degradation fixture should report degraded outcome"}
    deferred = [str(item).strip() for item in list(first.get("deferred_target_ids") or []) if str(item).strip()]
    if deferred != ["edge.elec.main.2"]:
        return {"status": "fail", "message": "deferred fault targets are not deterministically ordered"}
    return {"status": "pass", "message": "fault evaluation budget degradation stable and deterministic"}

