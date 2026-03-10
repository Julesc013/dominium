"""FAST test: overlay refuse policy blocks deterministic conflicts."""

from __future__ import annotations

import sys


TEST_ID = "test_refuse_policy_blocks_conflicts"
TEST_TAGS = ["fast", "geo", "overlay", "compat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo9_testlib import overlay_fixture_merge_result

    merge = dict(
        overlay_fixture_merge_result(include_mods=True, overlay_conflict_policy_id="overlay.conflict.refuse").get(
            "merge_result"
        )
        or {}
    )
    if str(merge.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "refuse policy did not refuse conflicting overlay merge"}
    if str(merge.get("refusal_code", "")).strip() != "refusal.overlay.conflict":
        return {"status": "fail", "message": "refuse policy used the wrong refusal code"}
    if not list(merge.get("overlay_conflict_artifacts") or []):
        return {"status": "fail", "message": "refuse policy did not emit conflict artifacts"}
    return {"status": "pass", "message": "overlay refuse policy blocks deterministic conflicts"}
