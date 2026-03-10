"""FAST test: MW-4 refinement request ordering is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_refinement_request_order_deterministic"
TEST_TAGS = ["fast", "mw4", "worldgen", "refinement", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.worldgen.refinement.refinement_scheduler import build_scheduler_plan
    from tools.worldgen.mw4_probe import refinement_request_for

    rows = [
        refinement_request_for(
            request_id="request.path",
            request_kind="path",
            index_tuple=[5, 0, 0],
            refinement_level=1,
            priority_class="priority.path.current",
        ),
        refinement_request_for(
            request_id="request.teleport",
            request_kind="teleport",
            index_tuple=[1, 0, 0],
            refinement_level=2,
            priority_class="priority.teleport.destination",
        ),
        refinement_request_for(
            request_id="request.roi",
            request_kind="roi",
            index_tuple=[2, 0, 0],
            refinement_level=0,
            priority_class="priority.roi.current",
        ),
        refinement_request_for(
            request_id="request.inspect",
            request_kind="inspect",
            index_tuple=[3, 0, 0],
            refinement_level=2,
            priority_class="priority.inspect.focus",
        ),
    ]
    first = build_scheduler_plan(
        pending_request_rows=rows,
        current_tick=0,
        compute_budget_units=2,
        refinement_cost_units=1,
        queue_capacity=8,
    )
    second = build_scheduler_plan(
        pending_request_rows=list(reversed(rows)),
        current_tick=0,
        compute_budget_units=2,
        refinement_cost_units=1,
        queue_capacity=8,
    )
    first_ids = [str(row.get("request_id", "")) for row in list(first.get("approved_rows") or [])]
    second_ids = [str(row.get("request_id", "")) for row in list(second.get("approved_rows") or [])]
    if first_ids != second_ids:
        return {"status": "fail", "message": "scheduler approval order drifted across repeated permutations"}
    if first_ids[:2] != ["request.teleport", "request.roi"]:
        return {"status": "fail", "message": "scheduler precedence drifted from teleport -> roi ordering"}
    return {"status": "pass", "message": "MW-4 refinement request ordering is deterministic"}
