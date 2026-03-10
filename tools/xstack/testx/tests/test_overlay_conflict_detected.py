"""FAST test: strict offline verification refuses deterministic overlay conflicts."""

from __future__ import annotations


TEST_ID = "test_overlay_conflict_detected"
TEST_TAGS = ["fast", "packs", "compat", "verification", "overlay"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat1_testlib import (
        add_overlay_conflict_fixture,
        cleanup_temp_repo,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        report_refusal_codes,
        verify_fixture_pack_set,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        add_overlay_conflict_fixture(temp_repo)
        result = verify_fixture_pack_set(repo_root, temp_repo, mod_policy_id="mod_policy.strict")
        report = dict(result.get("report") or {})
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "verification pipeline hard-refused during strict overlay conflict dry-run"}
        if bool(report.get("valid", False)):
            return {"status": "fail", "message": "strict policy accepted conflicting overlay dry-run"}
        if not list(report.get("conflicts") or []):
            return {"status": "fail", "message": "conflict artifacts missing for strict overlay refusal"}
        if "refusal.pack.conflict_in_strict" not in report_refusal_codes(result):
            return {"status": "fail", "message": "wrong refusal code for strict overlay conflict"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "strict offline verification detects and refuses overlay conflicts"}
