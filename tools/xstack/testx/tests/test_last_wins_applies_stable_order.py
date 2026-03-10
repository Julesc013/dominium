"""FAST test: overlay last_wins policy applies stable deterministic resolution order."""

from __future__ import annotations

import sys


TEST_ID = "test_last_wins_applies_stable_order"
TEST_TAGS = ["fast", "geo", "overlay", "compat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo9_testlib import OBJECT_ID_EARTH, overlay_fixture_merge_result

    merge = dict(
        overlay_fixture_merge_result(
            include_mods=True,
            reverse_mod_order=True,
            reverse_patch_order=True,
            overlay_conflict_policy_id="overlay.conflict.last_wins",
        ).get("merge_result")
        or {}
    )
    if str(merge.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "last_wins merge did not complete"}
    if str(merge.get("overlay_conflict_mode", "")).strip() != "last_wins":
        return {"status": "fail", "message": "last_wins conflict mode was not preserved"}
    rows = {
        str(dict(row).get("object_id", "")).strip(): dict(row)
        for row in list(merge.get("effective_object_views") or [])
        if isinstance(row, dict)
    }
    earth = dict(rows.get(OBJECT_ID_EARTH) or {})
    if str(((earth.get("properties") or {}).get("display_name", ""))).strip() != "Gaia":
        return {"status": "fail", "message": "last_wins did not resolve to the stable highest-precedence patch"}
    return {"status": "pass", "message": "overlay last_wins policy applies stable deterministic resolution order"}
