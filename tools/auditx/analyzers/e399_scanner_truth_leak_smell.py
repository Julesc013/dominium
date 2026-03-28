"""E399 scanner truth-leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E399_SCANNER_TRUTH_LEAK_SMELL"
REQUIRED_TOKENS = {
    "embodiment/tools/scanner_tool.py": (
        '"source_kind": "derived.scan_result"',
        "inspection_snapshot",
        "field_values",
        "property_origin_result",
    ),
    "client/ui/inspect_panels.py": (
        "build_scan_result_panel(",
        'panel.inspect.scan_result',
    ),
    "docs/embodiment/MVP_TOOLBELT_MODEL.md": (
        "scanner output may only be built from inspection snapshots, field summaries, and explain/provenance artifacts",
    ),
}
FORBIDDEN_TOKENS = {
    "embodiment/tools/scanner_tool.py": ("truth_model", "universe_state", "process_runtime"),
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
                    category="embodiment.scanner_truth_leak_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EMB-1 scanner-derived surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-SCANS"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.scanner_truth_leak_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EMB-1 scanner marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-SCANS"],
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
                    category="embodiment.scanner_truth_leak_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden scanner truth-leak token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-SCANS"],
                    related_paths=related_paths,
                )
            )
    return findings
