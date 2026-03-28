"""E396 blocking worldgen smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E396_BLOCKING_WORLDGEN_SMELL"
REQUIRED_TOKENS = {
    "client/ui/viewer_shell.py": (
        '"nonblocking": True',
        '"source_kind": "derived.refinement_status_view"',
        '"provenance_tool_id": "tool.geo.explain_property_origin"',
    ),
    "client/ui/teleport_controller.py": (
        "process.refinement_request_enqueue",
        "process.camera_teleport",
        "build_refinement_request_record(",
    ),
    "docs/worldgen/REFINEMENT_PIPELINE_MODEL.md": (
        "movement/teleport never blocks on generation",
        "shows coarse view until refined",
        "explain.refinement_deferred",
    ),
    "tools/worldgen/tool_run_refinement_stress.py": (
        "rapid-teleport and ROI-thrash",
        "run_refinement_stress(",
    ),
}
FORBIDDEN_TOKENS = {
    "client/ui/viewer_shell.py": ("process.worldgen_request", "generate_worldgen_result("),
    "client/ui/teleport_controller.py": ("process.worldgen_request", "generate_worldgen_result("),
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
    related_paths = sorted(set(REQUIRED_TOKENS.keys()) | set(FORBIDDEN_TOKENS.keys()))
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.blocking_worldgen_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MW-4 nonblocking surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-BLOCKING-WORLDGEN-IN-UI"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.blocking_worldgen_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing MW-4 nonblocking marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-BLOCKING-WORLDGEN-IN-UI"],
                    related_paths=related_paths,
                )
            )
    for rel_path, tokens in FORBIDDEN_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        found = [token for token in tokens if token in text]
        if found:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.blocking_worldgen_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden blocking worldgen token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-BLOCKING-WORLDGEN-IN-UI"],
                    related_paths=related_paths,
                )
            )
    return findings
