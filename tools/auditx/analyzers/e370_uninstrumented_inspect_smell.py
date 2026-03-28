"""E370 UX-0 uninstrumented inspect smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E370_UNINSTRUMENTED_INSPECT_SMELL"
VIEWER_SHELL_REL = "client/ui/viewer_shell.py"
INSPECT_PANELS_REL = "client/ui/inspect_panels.py"
DOC_REL = "docs/ux/MVP_VIEWER_SHELL.md"
REQUIRED_TOKENS = {
    VIEWER_SHELL_REL: (
        "build_inspection_panel_set(",
        '"inspection_surfaces": dict(inspection_surfaces)',
    ),
    INSPECT_PANELS_REL: (
        "build_inspection_overlays(",
        "explain_property_origin_report(",
        "process.inspect_generate_snapshot",
        "tool.geo.explain_property_origin",
        '"inspection_overlay_payload"',
        '"used_tool_ids"',
    ),
    DOC_REL: (
        "Inspection content must come from:",
        "process.inspect_generate_snapshot",
        "derived inspection overlays",
        "explain/provenance tools",
    ),
}
FORBIDDEN_TOKENS = (
    "instrumentation_bypass",
    "raw_snapshot_dump",
    "manual_provenance_chain",
)


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
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.uninstrumented_inspect_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required UX-0 inspection artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-VIEW-ARTIFACT-ONLY"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.uninstrumented_inspect_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing UX-0 inspection instrumentation marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-VIEW-ARTIFACT-ONLY"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
    for rel_path in (VIEWER_SHELL_REL, INSPECT_PANELS_REL):
        text = _read_text(repo_root, rel_path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.uninstrumented_inspect_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["uninstrumented inspection token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-VIEW-ARTIFACT-ONLY"],
                    related_paths=[VIEWER_SHELL_REL, INSPECT_PANELS_REL, DOC_REL],
                )
            )
            break
    return findings
