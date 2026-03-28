"""FAST test: leak cascade processing is deterministically bounded."""

from __future__ import annotations

import sys


TEST_ID = "test_cascade_bounded"
TEST_TAGS = ["fast", "fluid", "containment", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fluid import build_leak_state, build_tank_state, process_leak_tick

    leak_rows = [
        build_leak_state(
            target_id="edge.leak.{}".format(idx),
            leak_rate=10,
            active=True,
            last_update_tick=60,
            source_node_id="node.tank.c",
            sink_kind="external",
            sink_id="sink.void",
        )
        for idx in range(6)
    ]
    ticked = process_leak_tick(
        current_tick=61,
        leak_state_rows=leak_rows,
        tank_state_by_node_id={
            "node.tank.c": build_tank_state(node_id="node.tank.c", stored_mass=400, max_mass=400, last_update_tick=60),
        },
        max_processed_targets=3,
    )
    if int(ticked.get("processed_count", 0) or 0) != 3:
        return {"status": "fail", "message": "expected processed_count=3"}
    if int(ticked.get("deferred_count", 0) or 0) != 3:
        return {"status": "fail", "message": "expected deferred_count=3"}
    if str(ticked.get("budget_outcome", "")).strip() != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome when cascade cap is hit"}
    decisions = [dict(row) for row in list(ticked.get("decision_log_rows") or []) if isinstance(row, dict)]
    if not decisions:
        return {"status": "fail", "message": "expected decision log for cascade cap"}
    return {"status": "pass", "message": "leak cascade remains bounded and logged"}