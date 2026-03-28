"""E190 omniscient electrical UI leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E190_OMNISCIENT_ELECTRICAL_UI_LEAK_SMELL"


class OmniscientElectricalUILeakSmell:
    analyzer_id = ANALYZER_ID


_UI_PATHS = (
    "tools/xstack/sessionx/observation.py",
    "client/interaction/inspection_overlays.py",
    "inspection/inspection_engine.py",
)
_FORBIDDEN_PATTERNS = (
    re.compile(r"ch\.truth\.overlay\.[^\n]*elec", re.IGNORECASE),
    re.compile(r"truth_overlay[^\n]*elec", re.IGNORECASE),
    re.compile(r"state_hash_anchor[^\n]*elec", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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
    for rel_path in _UI_PATHS:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in _FORBIDDEN_PATTERNS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="epistemics.omniscient_electrical_ui_leak_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["electrical UI path appears to reference truth-overlay data directly", snippet[:140]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-IN-UI"],
                    related_paths=list(_UI_PATHS),
                )
            )
            break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
