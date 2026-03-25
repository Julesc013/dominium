"""FAST test: Ξ-0 symbol index matches a fresh deterministic regeneration."""

from __future__ import annotations


TEST_ID = "test_symbol_index_deterministic"
TEST_TAGS = ["fast", "xi", "architecture", "symbols"]


def run(repo_root: str):
    from tools.xstack.testx.tests.architecture_graph_testlib import committed_symbol_index, fresh_snapshot

    committed = committed_symbol_index(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("symbol_index") or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "Ξ-0 symbol index fingerprint drifted on regeneration"}
    return {"status": "pass", "message": "Ξ-0 symbol index is deterministic"}
