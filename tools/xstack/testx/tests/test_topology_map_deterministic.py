"""FAST test: topology map generation is deterministic for equivalent repository state."""

from __future__ import annotations

import sys


TEST_ID = "test_topology_map_deterministic"
TEST_TAGS = ["fast", "governance", "topology", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.governance.tool_topology_generate import generate_topology_map
    from tools.xstack.compatx.canonical_json import canonical_sha256

    first = generate_topology_map(repo_root=repo_root, commit_hash="", generated_tick=0)
    second = generate_topology_map(repo_root=repo_root, commit_hash="", generated_tick=0)
    if first != second:
        return {"status": "fail", "message": "topology map payload diverged across equivalent runs"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "topology deterministic_fingerprint diverged"}
    if int((dict(first.get("summary") or {})).get("node_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "topology map produced zero nodes unexpectedly"}
    if int((dict(first.get("summary") or {})).get("edge_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "topology map produced zero edges unexpectedly"}

    hash_a = canonical_sha256(dict(first, generated_tick=0))
    hash_b = canonical_sha256(dict(second, generated_tick=0))
    if hash_a != hash_b:
        return {"status": "fail", "message": "canonical topology hash diverged"}
    return {"status": "pass", "message": "topology map determinism passed"}

