"""FAST test: future-version artifacts use explicit read-only fallback when policy allows it."""

from __future__ import annotations


TEST_ID = "test_load_future_version_read_only_when_allowed"
TEST_TAGS = ["fast", "compat", "migration", "readonly"]


def run(repo_root: str):
    from tools.xstack.testx.tests.migration_lifecycle_testlib import DECISION_READ_ONLY, future_save_read_only_decision

    decision = future_save_read_only_decision(repo_root)
    if str(decision.get("decision_action_id", "")).strip() != DECISION_READ_ONLY:
        return {"status": "fail", "message": "future save manifests must resolve to decision.read_only when policy allows it"}
    if not bool(decision.get("read_only_applied", False)):
        return {"status": "fail", "message": "read-only migration decisions must set read_only_applied=true"}
    return {"status": "pass", "message": "future save manifests use explicit read-only fallback"}
