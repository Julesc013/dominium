"""FAST test: Ξ-0 architecture graph exposes the expected top-level structure."""

from __future__ import annotations


TEST_ID = "test_architecture_graph_schema_valid"
TEST_TAGS = ["fast", "xi", "architecture", "graph"]


def run(repo_root: str):
    from tools.xstack.testx.tests.architecture_graph_testlib import committed_architecture_graph

    payload = committed_architecture_graph(repo_root)
    if str(payload.get("report_id", "")).strip() != "architecture.graph.v1":
        return {"status": "fail", "message": "architecture graph report_id drifted"}
    concepts = list(payload.get("concepts") or [])
    modules = list(payload.get("modules") or [])
    if not concepts:
        return {"status": "fail", "message": "architecture graph must contain concepts"}
    if not modules:
        return {"status": "fail", "message": "architecture graph must contain modules"}
    first = dict(modules[0] or {})
    for key in ("module_id", "module_root", "owned_files", "symbols", "dependencies", "dependents"):
        if key not in first:
            return {"status": "fail", "message": "architecture module row missing '{}'".format(key)}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "architecture graph missing deterministic_fingerprint"}
    return {"status": "pass", "message": "Ξ-0 architecture graph exposes the expected structure"}
