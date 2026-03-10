"""FAST test: missing required registry ids are refused deterministically."""

from __future__ import annotations


TEST_ID = "test_registry_missing_refused"
TEST_TAGS = ["fast", "packs", "compat", "verification"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat1_testlib import (
        cleanup_temp_repo,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        mutate_pack_compat,
        report_refusal_codes,
        verify_fixture_pack_set,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        mutate_pack_compat(
            temp_repo,
            "pack.test.domain",
            lambda payload: {
                **payload,
                "required_registry_ids": ["dominium.registry.pack_compat1.missing"],
            },
        )
        result = verify_fixture_pack_set(repo_root, temp_repo)
        report = dict(result.get("report") or {})
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "verification pipeline hard-refused instead of reporting invalid pack set"}
        if bool(report.get("valid", False)):
            return {"status": "fail", "message": "missing registry requirement was accepted"}
        if "refusal.pack.registry_missing" not in report_refusal_codes(result):
            return {"status": "fail", "message": "wrong refusal code for missing registry"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "missing registry ids refuse deterministically"}
