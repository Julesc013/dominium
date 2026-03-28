"""E342 map truth leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E342_MAP_TRUTH_LEAK_SMELL"
TARGET_FILE = "geo/projection/view_adapters.py"
FORBIDDEN = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
REQUIRED_TOKENS = ("render_projected_view_ascii(", "build_projected_view_layer_buffers(")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    text = _read_text(repo_root, TARGET_FILE)
    if not text:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.map_truth_leak_smell",
                severity="RISK",
                confidence=0.97,
                file_path=TARGET_FILE,
                line=1,
                evidence=["projection view adapter is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-TRUTH-IN-UI", "INV-VIEWS-MUST-USE-LENS"],
                related_paths=[TARGET_FILE],
            )
        ]
    findings = []
    missing = [token for token in REQUIRED_TOKENS if token not in text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.map_truth_leak_smell",
                severity="RISK",
                confidence=0.94,
                file_path=TARGET_FILE,
                line=1,
                evidence=["missing projected-view adapter token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-TRUTH-IN-UI", "INV-VIEWS-MUST-USE-LENS"],
                related_paths=[TARGET_FILE, "geo/lens/lens_engine.py"],
            )
        )
    for line_no, line in enumerate(text.splitlines(), start=1):
        snippet = str(line).strip()
        if (not snippet) or snippet.startswith("#"):
            continue
        if not FORBIDDEN.search(snippet):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.map_truth_leak_smell",
                severity="RISK",
                confidence=0.98,
                file_path=TARGET_FILE,
                line=line_no,
                evidence=["projection adapter references forbidden truth symbol", snippet[:160]],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-TRUTH-IN-UI"],
                related_paths=[TARGET_FILE],
            )
        )
        break
    return findings
