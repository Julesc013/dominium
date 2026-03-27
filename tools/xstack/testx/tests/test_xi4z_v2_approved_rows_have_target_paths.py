"""FAST test: XI-4z-fix1 approved rows all carry exact target paths."""

from __future__ import annotations


TEST_ID = "test_xi4z_v2_approved_rows_have_target_paths"
TEST_TAGS = ["fast", "xi", "restructure", "target-paths"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4z_fix1_testlib import committed_lock_v2

    payload = committed_lock_v2(repo_root)
    seen_targets: set[str] = set()
    for row in list(payload.get("approved_for_xi5") or []):
        source_path = str(row.get("source_path", "")).strip()
        target_path = str(row.get("target_path", "")).strip()
        if not source_path or not target_path:
            return {"status": "fail", "message": "XI-4z-fix1 approved row missing source_path or target_path"}
        lowered = target_path.lower()
        if lowered.startswith("src/") or "/src/" in lowered or lowered.startswith("source/") or "/source/" in lowered:
            return {"status": "fail", "message": f"XI-4z-fix1 target path still source-like: {target_path}"}
        if target_path in seen_targets:
            return {"status": "fail", "message": f"XI-4z-fix1 target path reused by multiple rows: {target_path}"}
        seen_targets.add(target_path)
    return {"status": "pass", "message": "XI-4z-fix1 approved rows all carry exact target paths"}
