"""FAST test: impact graph build is deterministic for identical inputs."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.dev.impact_graph_deterministic"
TEST_TAGS = ["smoke", "tools", "runner"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.dev.impact_graph import build_graph_and_write

    changed = [
        "schemas/session_spec.schema.json",
        "tools/xstack/testx/runner.py",
    ]
    first = build_graph_and_write(
        repo_root=repo_root,
        changed_files=changed,
        out_path="build/impact_graph.test.a.json",
    )
    second = build_graph_and_write(
        repo_root=repo_root,
        changed_files=changed,
        out_path="build/impact_graph.test.b.json",
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "impact graph build did not complete"}
    for key in ("graph_hash", "node_count", "edge_count"):
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "impact graph mismatch for '{}'".format(key)}
    for rel in ("build/impact_graph.test.a.json", "build/impact_graph.test.b.json"):
        if not os.path.isfile(os.path.join(repo_root, rel.replace("/", os.sep))):
            return {"status": "fail", "message": "missing impact graph artifact '{}'".format(rel)}
    return {"status": "pass", "message": "impact graph deterministic build passed"}
