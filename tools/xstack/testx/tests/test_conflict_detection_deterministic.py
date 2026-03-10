"""FAST test: overlay conflict detection is deterministic across ordering permutations."""

from __future__ import annotations

import sys


TEST_ID = "test_conflict_detection_deterministic"
TEST_TAGS = ["fast", "geo", "overlay", "compat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo9_testlib import overlay_fixture_merge_result

    first = dict(
        overlay_fixture_merge_result(include_mods=True, overlay_conflict_policy_id="overlay.conflict.last_wins").get(
            "merge_result"
        )
        or {}
    )
    second = dict(
        overlay_fixture_merge_result(
            include_mods=True,
            reverse_mod_order=True,
            reverse_patch_order=True,
            reverse_resolved_packs=True,
            overlay_conflict_policy_id="overlay.conflict.last_wins",
        ).get("merge_result")
        or {}
    )
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "overlay merge fixture did not complete under last_wins"}
    if str(first.get("overlay_conflict_artifact_hash_chain", "")).strip() != str(
        second.get("overlay_conflict_artifact_hash_chain", "")
    ).strip():
        return {"status": "fail", "message": "overlay conflict artifact hash drifted across ordering permutations"}
    if list(first.get("overlay_conflict_artifacts") or []) != list(second.get("overlay_conflict_artifacts") or []):
        return {"status": "fail", "message": "overlay conflict artifact rows drifted across ordering permutations"}
    return {"status": "pass", "message": "overlay conflict detection is deterministic across ordering permutations"}
