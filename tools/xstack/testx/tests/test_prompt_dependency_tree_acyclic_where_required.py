"""FAST test: PI-2 prompt dependency tree remains acyclic for prompt-to-prompt edges."""

from __future__ import annotations

from collections import deque


TEST_ID = "test_prompt_dependency_tree_acyclic_where_required"
TEST_TAGS = ["fast", "pi", "blueprint", "graph"]


def run(repo_root: str):
    from tools.xstack.testx.tests.final_prompt_inventory_testlib import committed_prompt_dependency_tree

    payload = committed_prompt_dependency_tree(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.2.prompt_dependency_tree.v1":
        return {"status": "fail", "message": "prompt dependency tree report_id drifted"}
    nodes = list(payload.get("prompt_nodes") or [])
    node_ids = {str(dict(row).get("prompt_id", "")).strip() for row in nodes if str(dict(row).get("prompt_id", "")).strip()}
    indegree = {node_id: 0 for node_id in node_ids}
    graph = {node_id: set() for node_id in node_ids}
    for edge in payload.get("edges") or []:
        current = dict(edge)
        source = str(current.get("from", "")).strip()
        target = str(current.get("to", "")).strip()
        if source in node_ids and target in node_ids and target not in graph[source]:
            graph[source].add(target)
            indegree[target] += 1
    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    visited = []
    while queue:
        current = queue.popleft()
        visited.append(current)
        for child in sorted(graph[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if len(visited) != len(node_ids):
        return {"status": "fail", "message": "prompt dependency tree contains a cycle"}
    if not list(payload.get("critical_path_prompts") or []):
        return {"status": "fail", "message": "prompt dependency tree must expose a critical path"}
    return {"status": "pass", "message": "PI-2 prompt dependency tree is acyclic where required"}
