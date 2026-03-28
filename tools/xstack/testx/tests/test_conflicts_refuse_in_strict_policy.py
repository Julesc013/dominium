"""FAST test: COMPONENT-GRAPH-0 strict conflicts refuse deterministically."""

from __future__ import annotations


TEST_ID = "test_conflicts_refuse_in_strict_policy"
TEST_TAGS = ["fast", "release", "dist", "component-graph"]


def run(repo_root: str):
    del repo_root
    from release.component_graph_resolver import (
        COMPONENT_KIND_BINARY,
        EDGE_KIND_CONFLICTS,
        REFUSAL_COMPONENT_GRAPH_CONFLICT,
        canonicalize_component_graph,
        resolve_component_graph,
    )

    graph = canonicalize_component_graph(
        {
            "graph_id": "graph.test.conflict",
            "release_id": "release.test",
            "components": [
                {"component_id": "binary.a", "component_kind": COMPONENT_KIND_BINARY, "content_hash": "a" * 64, "version": "0.0.0"},
                {"component_id": "binary.b", "component_kind": COMPONENT_KIND_BINARY, "content_hash": "b" * 64, "version": "0.0.0"},
            ],
            "edges": [
                {
                    "from_component_id": "binary.a",
                    "edge_kind": EDGE_KIND_CONFLICTS,
                    "to_component_selector": "binary.b",
                }
            ],
        }
    )
    result = resolve_component_graph(
        graph,
        requested_component_ids=["binary.a", "binary.b"],
        strict_conflicts=True,
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "strict conflict resolution must refuse"}
    if str(result.get("refusal_code", "")).strip() != REFUSAL_COMPONENT_GRAPH_CONFLICT:
        return {"status": "fail", "message": "strict conflict resolution must emit the canonical conflict refusal code"}
    return {"status": "pass", "message": "strict conflicts refuse deterministically"}
