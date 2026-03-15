"""FAST test: COMPONENT-GRAPH-0 registry and baseline graph are structurally valid."""

from __future__ import annotations


TEST_ID = "test_component_graph_schema_valid"
TEST_TAGS = ["fast", "release", "dist", "component-graph"]


def run(repo_root: str):
    from tools.xstack.testx.tests.component_graph_testlib import build_report, current_violations, load_graph, load_graph_registry

    registry = load_graph_registry(repo_root)
    graph = load_graph(repo_root)
    report = build_report(repo_root)
    violations = current_violations(repo_root)
    if str(registry.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "component graph registry schema_version must be 1.0.0"}
    if str(graph.get("graph_id", "")).strip() != "graph.release.v0_0_0_mock":
        return {"status": "fail", "message": "default component graph id is missing or incorrect"}
    if not list(graph.get("components") or []):
        return {"status": "fail", "message": "component graph must contain components"}
    if not list(graph.get("edges") or []):
        return {"status": "fail", "message": "component graph must contain dependency edges"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "component graph report did not complete successfully"}
    if violations:
        return {"status": "fail", "message": "component graph governance violations remain: {}".format(len(violations))}
    return {"status": "pass", "message": "component graph registry and baseline graph are valid"}
