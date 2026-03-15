"""FAST test: COMPONENT-GRAPH-0 requires edges are enforced by the resolver."""

from __future__ import annotations


TEST_ID = "test_requires_edges_enforced"
TEST_TAGS = ["fast", "release", "dist", "component-graph"]


def run(repo_root: str):
    del repo_root
    from src.release.component_graph_resolver import (
        COMPONENT_KIND_BINARY,
        COMPONENT_KIND_LOCK,
        EDGE_KIND_REQUIRES,
        canonicalize_component_graph,
        resolve_component_graph,
    )

    graph = canonicalize_component_graph(
        {
            "graph_id": "graph.test.requires",
            "release_id": "release.test",
            "components": [
                {"component_id": "binary.client", "component_kind": COMPONENT_KIND_BINARY, "content_hash": "a" * 64, "version": "0.0.0"},
                {"component_id": "lock.pack_lock.mvp_default", "component_kind": COMPONENT_KIND_LOCK, "content_hash": "b" * 64, "version": "0.0.0"},
            ],
            "edges": [
                {
                    "from_component_id": "binary.client",
                    "edge_kind": EDGE_KIND_REQUIRES,
                    "to_component_selector": "lock.pack_lock.mvp_default",
                }
            ],
        }
    )
    result = resolve_component_graph(
        graph,
        requested_component_ids=["binary.client"],
        include_recommends=False,
        include_suggests=False,
    )
    plan = dict(result.get("install_plan") or {})
    selected = list(plan.get("selected_components") or [])
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "resolver refused a graph with a satisfiable requires edge"}
    if "lock.pack_lock.mvp_default" not in selected:
        return {"status": "fail", "message": "resolver did not add the required component"}
    return {"status": "pass", "message": "requires edges are enforced by the resolver"}
