"""E343 uninstrumented map access smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E343_UNINSTRUMENTED_MAP_ACCESS_SMELL"
REQUIRED_FILES = {
    "geo/lens/lens_engine.py": (
        "build_lens_request(",
        "build_projected_view_artifact(",
        "map_instrument_required",
        "allow_omniscient_debug",
    ),
    "geo/lens/cctv_engine.py": (
        "build_signal_message_envelope(",
        "build_knowledge_receipt(",
    ),
    "tools/geo/tool_replay_view_window.py": (
        "verify_view_window(",
        "projection_profile_registry_hash",
        "lens_layer_registry_hash",
        "view_type_registry_hash",
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
                    category="geometry.uninstrumented_map_access_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-5 lens/proof file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-VIEWS-MUST-USE-LENS", "INV-OMNISCIENCE-PROFILED"],
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
                category="geometry.uninstrumented_map_access_smell",
                severity="RISK",
                confidence=0.93,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-5 lens or proof token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-VIEWS-MUST-USE-LENS", "INV-OMNISCIENCE-PROFILED"],
                related_paths=[rel_path, "geo/projection/projection_engine.py"],
            )
        )
    return findings
