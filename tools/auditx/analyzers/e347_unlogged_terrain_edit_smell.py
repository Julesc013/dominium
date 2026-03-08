"""E347 unlogged terrain edit smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E347_UNLOGGED_TERRAIN_EDIT_SMELL"

REQUIRED_FILES = {
    "src/geo/edit/geometry_state_engine.py": (
        "build_geometry_edit_event(",
        "geometry_edit_event_hash_chain(",
        "geometry_state_hash_surface(",
    ),
    "tools/xstack/sessionx/process_runtime.py": (
        "_append_geometry_edit_event(",
        "_append_geometry_edit_event_artifact(",
        "_refresh_geometry_hash_chains(",
        '"artifact.geometry_edit_event."',
        "geometry_edit_event_hash_chain",
    ),
    "tools/geo/tool_replay_geometry_window.py": (
        "verify_geometry_replay_window(",
        "geometry_edit_event_hash_chain",
        "stable_across_repeated_runs",
    ),
    "src/control/proof/control_proof_bundle.py": (
        "geometry_edit_policy_registry_hash",
        "geometry_state_hash_chain",
        "geometry_edit_event_hash_chain",
    ),
    "src/net/policies/policy_server_authoritative.py": (
        "geometry_edit_policy_registry_hash",
        "geometry_state_hash_chain",
        "geometry_edit_event_hash_chain",
    ),
    "src/net/srz/shard_coordinator.py": (
        "geometry_edit_policy_registry_hash",
        "geometry_state_hash_chain",
        "geometry_edit_event_hash_chain",
    ),
}


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    for rel_path, required_tokens in sorted(REQUIRED_FILES.items()):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geometry.unlogged_terrain_edit_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-7 geometry logging or replay file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-GEOMETRY-EDIT-RECORDED"],
                    related_paths=[rel_path],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.unlogged_terrain_edit_smell",
                severity="RISK",
                confidence=0.94,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-7 terrain edit logging token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-GEOMETRY-EDIT-RECORDED"],
                related_paths=[rel_path, "tools/xstack/sessionx/process_runtime.py"],
            )
        )
    return findings
