"""STRICT test: lawful perceived memory is preserved across micro->macro collapse."""

from __future__ import annotations

import sys


TEST_ID = "testx.epistemics.lod_memory_preserved_on_collapse"
TEST_TAGS = ["strict", "epistemics", "lod", "memory", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.lod_invariance_testlib import base_state, execute_region_transition

    state = base_state(camera_x_mm=12345)
    expanded = execute_region_transition(
        state=state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=True,
        desired_tier="fine",
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "region_expand refused unexpectedly before collapse memory preservation check"}

    collapsed = execute_region_transition(
        state=state,
        process_id="process.region_collapse",
        strict_contracts=True,
        memory_enabled=True,
    )
    if str(collapsed.get("result", "")) != "complete":
        return {"status": "fail", "message": "region_collapse refused unexpectedly during memory preservation check"}

    lod_summary = dict(collapsed.get("lod_invariance") or {})
    if str(lod_summary.get("status", "")) != "ok":
        return {"status": "fail", "message": "region_collapse did not preserve LOD invariance status=ok"}
    if list(lod_summary.get("missing_memory_item_ids") or []):
        return {"status": "fail", "message": "collapse dropped lawful memory items: {}".format(",".join(lod_summary.get("missing_memory_item_ids") or []))}
    return {"status": "pass", "message": "memory preservation across collapse passed"}

