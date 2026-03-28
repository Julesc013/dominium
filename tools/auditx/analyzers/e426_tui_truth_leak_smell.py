"""E426 TUI truth leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E426_TUI_TRUTH_LEAK_SMELL"
DOCTRINE_REL = "docs/appshell/TUI_FRAMEWORK.md"
ENGINE_REL = "appshell/tui/tui_engine.py"
REQUIRED_DOCTRINE_TOKENS = (
    "derived view artifacts only",
    "must not read TruthModel directly",
)
REQUIRED_ENGINE_TOKENS = (
    "build_map_view_set(",
    "build_inspection_panel_set(",
)
FORBIDDEN_ENGINE_TOKENS = (
    "TruthModel",
    "truth_model",
    "authoritative_state",
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
    related_paths = [DOCTRINE_REL, ENGINE_REL]
    doctrine_text = _read_text(repo_root, DOCTRINE_REL)
    missing = [token for token in REQUIRED_DOCTRINE_TOKENS if token not in doctrine_text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.tui_truth_leak_smell",
                severity="RISK",
                confidence=0.96,
                file_path=DOCTRINE_REL,
                line=1,
                evidence=["missing TUI truth-boundary doctrine marker(s): {}".format(", ".join(missing[:3]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-TUI-NO-TRUTH-READ"],
                related_paths=related_paths,
            )
        )
    engine_text = _read_text(repo_root, ENGINE_REL)
    missing = [token for token in REQUIRED_ENGINE_TOKENS if token not in engine_text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.tui_truth_leak_smell",
                severity="RISK",
                confidence=0.97,
                file_path=ENGINE_REL,
                line=1,
                evidence=["missing derived-view marker(s): {}".format(", ".join(missing[:3]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-TUI-NO-TRUTH-READ"],
                related_paths=related_paths,
            )
        )
    for token in FORBIDDEN_ENGINE_TOKENS:
        if token in engine_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.tui_truth_leak_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=ENGINE_REL,
                    line=1,
                    evidence=["forbidden direct-truth token '{}' detected in TUI engine".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TUI-NO-TRUTH-READ"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
