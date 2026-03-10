"""E411 silent feature disable smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E411_SILENT_FEATURE_DISABLE_SMELL"
REQUIRED_TOKENS = {
    "docs/compat/DEGRADE_LADDERS.md": (
        "Silent feature disablement is forbidden.",
        "compat status",
        "explain.feature_disabled",
    ),
    "src/compat/negotiation/degrade_enforcer.py": (
        "REFUSAL_COMPAT_FEATURE_DISABLED",
        "def build_compat_status_payload(",
        '"effective_ui_mode"',
    ),
    "src/server/server_console.py": (
        "def compat_status(",
        '"compat_rows"',
    ),
    "src/embodiment/tools/logic_tool.py": (
        "enforce_negotiated_capability",
        '"cap.logic.debug_analyzer"',
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
    related_paths = sorted(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.degrade.silent_feature_disable_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required degrade-enforcement surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-SILENT-DEGRADE", "INV-DEGRADE-RECORDED-IN-NEGOTIATION"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.degrade.silent_feature_disable_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing CAP-NEG-3 marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-SILENT-DEGRADE", "INV-DEGRADE-RECORDED-IN-NEGOTIATION"],
                    related_paths=related_paths,
                )
            )
    return findings
