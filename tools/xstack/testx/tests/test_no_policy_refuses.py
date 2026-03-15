"""FAST test: artifacts without declared lifecycle policy refuse deterministically."""

from __future__ import annotations


TEST_ID = "test_no_policy_refuses"
TEST_TAGS = ["fast", "compat", "migration", "refusal"]


def run(repo_root: str):
    from src.compat.migration_lifecycle import DECISION_REFUSE
    from tools.xstack.testx.tests.migration_lifecycle_testlib import REFUSAL_MIGRATION_NO_PATH, no_policy_decision

    decision = no_policy_decision(repo_root)
    if str(decision.get("decision_action_id", "")).strip() != DECISION_REFUSE:
        return {"status": "fail", "message": "missing lifecycle policy must refuse deterministically"}
    if str(decision.get("refusal_code", "")).strip() != REFUSAL_MIGRATION_NO_PATH:
        return {"status": "fail", "message": "missing lifecycle policy must refuse with refusal.migration.no_path"}
    return {"status": "pass", "message": "missing lifecycle policy refuses deterministically"}
