"""FAST test: selected mod policy pins overlay conflict policy deterministically."""

from __future__ import annotations


TEST_ID = "test_conflict_policy_applied_from_mod_policy"
TEST_TAGS = ["fast", "modding", "policy", "overlay"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mod_policy0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        load_fixture_lockfile,
        make_temp_mod_policy_repo,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_mod_policy_repo(repo_root)
    try:
        result = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.strict")
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "fixture compile failed before conflict-policy test"}
        if str(result.get("overlay_conflict_policy_id", "")) != "overlay.conflict.refuse":
            return {"status": "fail", "message": "strict mod policy did not resolve to overlay.conflict.refuse"}
        lockfile = load_fixture_lockfile(temp_repo)
        if str(lockfile.get("overlay_conflict_policy_id", "")) != "overlay.conflict.refuse":
            return {"status": "fail", "message": "lockfile did not persist overlay conflict policy from mod policy"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "mod policy pins overlay conflict policy deterministically"}
