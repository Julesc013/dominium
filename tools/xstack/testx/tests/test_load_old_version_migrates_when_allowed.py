"""FAST test: legacy artifacts resolve to deterministic migration chains when policy allows it."""

from __future__ import annotations


TEST_ID = "test_load_old_version_migrates_when_allowed"
TEST_TAGS = ["fast", "compat", "migration", "migrate"]


def run(repo_root: str):
    from tools.xstack.testx.tests.migration_lifecycle_testlib import DECISION_MIGRATE, blueprint_migrate_decision

    decision = blueprint_migrate_decision(repo_root)
    if str(decision.get("decision_action_id", "")).strip() != DECISION_MIGRATE:
        return {"status": "fail", "message": "legacy blueprint artifacts must resolve to decision.migrate"}
    if not list(decision.get("migration_chain") or []):
        return {"status": "fail", "message": "migration decision must include a deterministic chain"}
    return {"status": "pass", "message": "legacy blueprint artifacts migrate deterministically"}
