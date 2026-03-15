"""FAST test: every governed migration artifact kind has a declared policy row."""

from __future__ import annotations


TEST_ID = "test_policy_exists_for_each_artifact_kind"
TEST_TAGS = ["fast", "compat", "migration", "policy"]


def run(repo_root: str):
    from tools.xstack.testx.tests.migration_lifecycle_testlib import ARTIFACT_KIND_IDS, policy_ids

    declared = set(policy_ids(repo_root))
    expected = set(ARTIFACT_KIND_IDS)
    missing = sorted(expected - declared)
    if missing:
        return {"status": "fail", "message": "missing migration policies for: {}".format(", ".join(missing))}
    return {"status": "pass", "message": "all governed artifact kinds declare a migration policy"}
