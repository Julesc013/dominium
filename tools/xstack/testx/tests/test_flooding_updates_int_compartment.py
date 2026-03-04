"""FAST test: interior-directed leak emits deterministic flooding coupling rows."""

from __future__ import annotations

import sys


TEST_ID = "test_flooding_updates_int_compartment"
TEST_TAGS = ["fast", "fluid", "interior", "coupling"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.fluid import build_tank_state, process_leak_tick, process_start_leak

    started = process_start_leak(
        leak_state_rows=[],
        target_id="edge.pipe.int",
        leak_rate=30,
        current_tick=50,
        source_node_id="node.tank.int",
        sink_kind="interior",
        sink_id="compartment.alpha",
    )
    ticked = process_leak_tick(
        current_tick=51,
        leak_state_rows=list(started.get("leak_state_rows") or []),
        tank_state_by_node_id={
            "node.tank.int": build_tank_state(node_id="node.tank.int", stored_mass=140, max_mass=140, last_update_tick=50),
        },
        max_processed_targets=8,
    )
    interior_rows = [dict(row) for row in list(ticked.get("interior_coupling_rows") or []) if isinstance(row, dict)]
    if not interior_rows:
        return {"status": "fail", "message": "expected interior coupling rows for interior leak"}
    row = interior_rows[0]
    if str(row.get("compartment_id", "")).strip() != "compartment.alpha":
        return {"status": "fail", "message": "interior coupling row has wrong compartment id"}
    if int(row.get("transferred_mass", 0) or 0) <= 0:
        return {"status": "fail", "message": "interior transferred mass must be positive"}
    if int(row.get("hazard_flood_increment", 0) or 0) <= 0:
        return {"status": "fail", "message": "flood hazard increment should be positive"}
    return {"status": "pass", "message": "interior flooding coupling rows emitted"}