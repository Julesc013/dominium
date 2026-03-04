"""FAST test: topology map includes all repository schema files."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_topology_map_includes_all_schemas"
TEST_TAGS = ["fast", "governance", "topology", "schema"]


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _schema_paths(repo_root: str):
    out = []
    for root_name, suffix in (("schema", ".schema"), ("schemas", ".schema.json")):
        abs_root = os.path.join(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if name.endswith(suffix):
                    out.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))
    return sorted(set(out))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.governance.tool_topology_generate import generate_topology_map

    topology = generate_topology_map(repo_root=repo_root, commit_hash="", generated_tick=0)
    declared = sorted(
        set(
            _norm(str(row.get("path", "")).strip())
            for row in list(topology.get("nodes") or [])
            if isinstance(row, dict) and str(row.get("node_kind", "")).strip() == "schema"
        )
    )
    expected = _schema_paths(repo_root)
    missing = sorted(token for token in expected if token not in set(declared))
    if missing:
        return {
            "status": "fail",
            "message": "topology map missing schema nodes (count={}): {}".format(len(missing), ", ".join(missing[:8])),
        }
    return {"status": "pass", "message": "topology map schema coverage passed"}

