"""FAST test: Omega ecosystem migration policy coverage is complete."""

from __future__ import annotations

import sys


TEST_ID = "test_migration_policy_complete"
TEST_TAGS = ["fast", "omega", "ecosystem", "migration"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.ecosystem_verify_common import verify_ecosystem

    report = verify_ecosystem(repo_root)
    migration = dict(report.get("migration_coverage") or {})
    if str(migration.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ecosystem migration coverage failed"}
    if list(migration.get("missing_policy_ids") or []):
        return {"status": "fail", "message": "ecosystem migration coverage is missing policies"}
    if not bool(migration.get("read_only_decision_defined")):
        return {"status": "fail", "message": "ecosystem migration coverage is missing read-only fallback evidence"}
    return {"status": "pass", "message": "ecosystem migration coverage is complete"}
