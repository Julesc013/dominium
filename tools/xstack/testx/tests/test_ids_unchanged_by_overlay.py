"""FAST test: SOL-0 official overlays preserve object identity for overlapping procedural objects."""

from __future__ import annotations

import sys


TEST_ID = "test_ids_unchanged_by_overlay"
TEST_TAGS = ["fast", "sol", "overlay", "identity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.sol0_testlib import build_sol_overlay_fixture, effective_object_map

    fixture = build_sol_overlay_fixture(repo_root, refinement_level=2)
    slot_ids = dict(fixture.get("patch_document", {}).get("slot_object_ids") or {})
    base_rows = effective_object_map(fixture.get("base_objects"))
    merged_rows = effective_object_map(dict(fixture.get("merge_result") or {}).get("effective_object_views"))
    unpinned_rows = effective_object_map(dict(fixture.get("unpinned_merge_result") or {}).get("effective_object_views"))
    for slot_id in list(fixture.get("existing_slot_ids") or []):
        object_id = str(slot_ids.get(slot_id, "")).strip()
        if not object_id:
            return {"status": "fail", "message": "slot {} is missing an object_id".format(slot_id)}
        if object_id not in base_rows:
            return {"status": "fail", "message": "slot {} was missing from the base procedural overlap set".format(slot_id)}
        if object_id not in merged_rows:
            return {"status": "fail", "message": "slot {} disappeared after applying the official overlay".format(slot_id)}
        if dict(unpinned_rows.get(object_id) or {}) != dict(base_rows.get(object_id) or {}):
            return {"status": "fail", "message": "slot {} does not revert to the base view when the official layer is absent".format(slot_id)}
    return {"status": "pass", "message": "SOL-0 official overlay preserves overlap-set object identities"}

