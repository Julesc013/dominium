"""FAST test: GEO-7 remove-volume process is deterministic and GEO-keyed."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_remove_volume_deterministic"
TEST_TAGS = ["fast", "geo", "geometry", "determinism"]


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo7_testlib import geometry_cell_row, geometry_cell_key, run_geometry_process, seed_geometry_state

    state = seed_geometry_state()
    result = run_geometry_process(
        state=state,
        process_id="process.geometry_remove",
        inputs={
            "target_cell_keys": [geometry_cell_key([0, 0, 0])],
            "volume_amount": 250,
        },
    )
    return {
        "result": dict(result),
        "state": copy.deepcopy(state),
        "cell_row": dict(geometry_cell_row(state, [0, 0, 0]) or {}),
    }


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if first != second:
        return {"status": "fail", "message": "geometry remove process drifted across repeated runs"}
    result = dict(first.get("result") or {})
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "geometry remove process did not complete"}
    cell_row = dict(first.get("cell_row") or {})
    if int(cell_row.get("occupancy_fraction", -1)) != 750:
        return {"status": "fail", "message": "remove volume produced unexpected occupancy {}".format(cell_row.get("occupancy_fraction"))}
    if int(result.get("volume_amount_applied", -1)) != 250:
        return {"status": "fail", "message": "remove volume metadata did not report applied volume"}
    if not str(result.get("edit_id", "")).strip():
        return {"status": "fail", "message": "remove volume metadata missing edit_id"}
    return {"status": "pass", "message": "GEO-7 remove-volume process is deterministic"}
