"""FAST test: Omega ecosystem update coverage excludes yanked candidates."""

from __future__ import annotations

import sys


TEST_ID = "test_update_plan_excludes_yanked"
TEST_TAGS = ["fast", "omega", "ecosystem", "update"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.ecosystem_verify_common import verify_ecosystem

    report = verify_ecosystem(repo_root)
    update = dict(report.get("update_coverage") or {})
    if str(update.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ecosystem update coverage failed"}
    if list(update.get("selected_yanked_component_ids") or []):
        return {"status": "fail", "message": "ecosystem update coverage selected a yanked component"}
    if int(update.get("skipped_yanked_count", 0) or 0) < 1:
        return {"status": "fail", "message": "ecosystem update coverage did not record a skipped yanked candidate"}
    return {"status": "pass", "message": "ecosystem update coverage excludes yanked candidates"}
