"""FAST test: impacted-tests subset resolves deterministically and to known TestX IDs."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.dev.impacted_tests_subset"
TEST_TAGS = ["smoke", "tools", "runner"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.dev.impact_graph import build_graph, compute_impacted_sets

    changed_files = ["schemas/session_spec.schema.json"]
    graph = build_graph(repo_root=repo_root, changed_files=changed_files)
    impacted = compute_impacted_sets(graph_payload=graph, changed_files=changed_files)
    if impacted.get("result") != "complete":
        return {"status": "fail", "message": "impacted set computation failed"}
    impacted_tests = list(impacted.get("impacted_test_ids") or [])
    if not impacted_tests:
        return {"status": "fail", "message": "schema change produced empty impacted test subset"}

    tests_root = os.path.join(repo_root, "tools", "xstack", "testx", "tests")
    available = set()
    for root, _dirs, files in os.walk(tests_root):
        for name in sorted(files):
            if name.startswith("test_") and name.endswith(".py"):
                available.add("tools.xstack.testx.tests." + name[:-3])
    # Impact graph uses TEST_ID where present; verify at least one known schema test id is included.
    expected_any = {
        "testx.compatx.schema_validate",
        "testx.session.create",
        "testx.lockfile.validate",
    }
    if not expected_any.intersection(set(impacted_tests)):
        return {
            "status": "fail",
            "message": "impacted subset missing expected schema-adjacent tests",
        }

    # deterministic ordering
    if impacted_tests != sorted(impacted_tests):
        return {"status": "fail", "message": "impacted test subset ordering is non-deterministic"}
    return {"status": "pass", "message": "impacted tests subset computation passed"}
