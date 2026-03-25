"""FAST test: Ξ-0 module registry matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_module_registry_deterministic"
TEST_TAGS = ["fast", "xi", "architecture", "modules"]


def run(repo_root: str):
    from tools.xstack.testx.tests.architecture_graph_testlib import committed_module_registry, fresh_snapshot

    committed = committed_module_registry(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("module_registry") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "Ξ-0 module registry fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "Ξ-0 module registry is deterministic"}
