"""FAST test: GEO-9 overlay merge is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_overlay_merge_deterministic"
TEST_TAGS = ["fast", "geo", "overlay", "determinism"]


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo9_testlib import overlay_fixture_merge_result

    fixture = overlay_fixture_merge_result(include_mods=True, include_save=True)
    return {
        "merge_result": copy.deepcopy(fixture.get("merge_result")),
        "property_patches": copy.deepcopy(fixture.get("property_patches")),
        "overlay_manifest": copy.deepcopy(fixture.get("overlay_manifest")),
    }


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if first != second:
        return {"status": "fail", "message": "overlay merge drifted across repeated runs"}
    merge_result = dict(first.get("merge_result") or {})
    if str(merge_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "overlay merge did not complete"}
    if not str(merge_result.get("overlay_merge_result_hash_chain", "")).strip():
        return {"status": "fail", "message": "overlay merge result hash chain was not populated"}
    return {"status": "pass", "message": "GEO-9 overlay merge deterministic for identical inputs"}
