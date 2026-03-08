"""FAST test: GEO-9 save patches persist over official overlays."""

from __future__ import annotations

import sys


TEST_ID = "test_save_patch_survives_official_overlay"
TEST_TAGS = ["fast", "geo", "overlay", "save"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo9_testlib import (
        OBJECT_ID_EARTH,
        merge_state_overlay,
        run_overlay_save_patch_process,
        seed_overlay_state,
    )

    state = seed_overlay_state(include_mods=False)
    process_result = run_overlay_save_patch_process(state=state, value="New Earth")
    if str(process_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "save patch process did not complete"}
    merged = merge_state_overlay(state=state, include_mods=False)
    merge_result = dict(merged.get("merge_result") or {})
    if str(merge_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "overlay merge after save patch did not complete"}
    earth = next(
        (
            dict(row)
            for row in list(merge_result.get("effective_object_views") or [])
            if str(dict(row).get("object_id", "")).strip() == OBJECT_ID_EARTH
        ),
        {},
    )
    display_name = str((dict(earth.get("properties") or {})).get("display_name", "")).strip()
    if display_name != "New Earth":
        return {"status": "fail", "message": "save patch value did not survive official overlay merge"}
    if not str(state.get("property_patch_hash_chain", "")).strip():
        return {"status": "fail", "message": "save patch hash chain was not refreshed"}
    return {"status": "pass", "message": "GEO-9 save patches survive official overlays deterministically"}
