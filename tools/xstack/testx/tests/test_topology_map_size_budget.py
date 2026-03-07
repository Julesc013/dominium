"""FAST test: topology map artifact stays within hosted repository size budget."""

from __future__ import annotations

import sys


TEST_ID = "test_topology_map_size_budget"
TEST_TAGS = ["fast", "governance", "topology", "artifact_budget"]


def _count_empty_extensions(rows) -> int:
    return int(
        sum(
            1
            for row in list(rows or [])
            if isinstance(row, dict) and "extensions" in row and not dict(row.get("extensions") or {})
        )
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.governance.tool_topology_generate import (
        TOPOLOGY_MAP_BUDGET_BYTES,
        generate_topology_map,
        topology_payload_json_size_bytes,
    )

    payload = generate_topology_map(repo_root=repo_root, commit_hash="", generated_tick=0)
    json_size_bytes = int(topology_payload_json_size_bytes(payload))
    if json_size_bytes > int(TOPOLOGY_MAP_BUDGET_BYTES):
        return {
            "status": "fail",
            "message": "topology map exceeds size budget (size_bytes={}, budget_bytes={})".format(
                json_size_bytes,
                int(TOPOLOGY_MAP_BUDGET_BYTES),
            ),
        }

    empty_node_extensions = _count_empty_extensions(payload.get("nodes") or [])
    empty_edge_extensions = _count_empty_extensions(payload.get("edges") or [])
    if empty_node_extensions or empty_edge_extensions:
        return {
            "status": "fail",
            "message": "topology map emitted empty extensions maps (nodes={}, edges={})".format(
                empty_node_extensions,
                empty_edge_extensions,
            ),
        }

    return {
        "status": "pass",
        "message": "topology map size budget passed (size_bytes={}, budget_bytes={})".format(
            json_size_bytes,
            int(TOPOLOGY_MAP_BUDGET_BYTES),
        ),
    }
