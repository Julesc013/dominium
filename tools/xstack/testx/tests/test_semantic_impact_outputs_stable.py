"""FAST test: semantic impact output is deterministic for equivalent inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_semantic_impact_outputs_stable"
TEST_TAGS = ["fast", "governance", "topology", "impact"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.governance.tool_semantic_impact import compute_semantic_impact
    from tools.governance.tool_topology_generate import generate_topology_map
    from tools.xstack.compatx.canonical_json import canonical_sha256

    topology = generate_topology_map(repo_root=repo_root, commit_hash="", generated_tick=0)
    changed_files = [
        "schema/governance/topology_map.schema",
        "data/registries/inspection_section_registry.json",
        "src/core/graph/network_graph_engine.py",
        "tools/xstack/sessionx/observation.py",
    ]
    first = compute_semantic_impact(
        repo_root=repo_root,
        changed_files=changed_files,
        topology_map_payload=topology,
    )
    second = compute_semantic_impact(
        repo_root=repo_root,
        changed_files=changed_files,
        topology_map_payload=topology,
    )

    if first != second:
        return {"status": "fail", "message": "semantic impact payload diverged across equivalent runs"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "semantic impact deterministic_fingerprint diverged"}
    if sorted(list(first.get("required_test_suites") or [])) != sorted(list(second.get("required_test_suites") or [])):
        return {"status": "fail", "message": "semantic impact required_test_suites ordering unstable"}

    canonical_a = canonical_sha256(dict(first, deterministic_fingerprint=""))
    canonical_b = canonical_sha256(dict(second, deterministic_fingerprint=""))
    if canonical_a != canonical_b:
        return {"status": "fail", "message": "semantic impact canonical hash diverged"}
    return {"status": "pass", "message": "semantic impact determinism passed"}

