"""FAST test: leak tick moves mass through FlowSystem and logs transfer events."""

from __future__ import annotations

import sys


TEST_ID = "test_leak_mass_transfer_logged"
TEST_TAGS = ["fast", "fluid", "leak", "flow"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fluid import build_tank_state, process_leak_tick, process_start_leak

    started = process_start_leak(
        leak_state_rows=[],
        target_id="edge.pipe.a",
        leak_rate=25,
        current_tick=40,
        source_node_id="node.tank.a",
        sink_kind="external",
        sink_id="sink.void",
    )
    tank_state_by_node_id = {
        "node.tank.a": build_tank_state(node_id="node.tank.a", stored_mass=100, max_mass=120, last_update_tick=39),
    }
    ticked = process_leak_tick(
        current_tick=41,
        leak_state_rows=list(started.get("leak_state_rows") or []),
        tank_state_by_node_id=tank_state_by_node_id,
        max_processed_targets=16,
    )
    transfer_rows = [dict(row) for row in list(ticked.get("flow_transfer_events") or []) if isinstance(row, dict)]
    leak_events = [dict(row) for row in list(ticked.get("leak_event_rows") or []) if isinstance(row, dict)]
    if not transfer_rows:
        return {"status": "fail", "message": "expected flow transfer rows for leak tick"}
    if not leak_events:
        return {"status": "fail", "message": "expected leak event rows"}
    transferred = int(transfer_rows[0].get("transferred_amount", 0) or 0)
    if transferred <= 0:
        return {"status": "fail", "message": "leak transfer amount must be positive"}
    updated_tank = dict((ticked.get("tank_state_by_node_id") or {}).get("node.tank.a") or {})
    if int(updated_tank.get("stored_mass", 0) or 0) >= 100:
        return {"status": "fail", "message": "source tank mass did not decrement after leak tick"}
    return {"status": "pass", "message": "leak mass transfer logged deterministically"}