"""E138 inline strength check smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E138_INLINE_STRENGTH_CHECK_SMELL"
MECH_ENGINE_REL = "src/mechanics/structural_graph_engine.py"

_INLINE_PATTERNS = (
    re.compile(r"\bif\b[^\n]*(?:load|stress_ratio|max_load)[^\n]*[><=]{1,2}[^\n]*(?:break|fracture|fail)", re.IGNORECASE),
    re.compile(r"\b(?:max_load|stress_ratio)\b\s*[*+/=-]+\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)", re.IGNORECASE),
    re.compile(r"\bif\b[^\n]*(?:damaged|overload|overloaded)[^\n]*(?:joint|edge|node)", re.IGNORECASE),
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

    mech_text = _read_text(repo_root, MECH_ENGINE_REL)
    if not mech_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.inline_strength_check_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=MECH_ENGINE_REL,
                line=1,
                evidence=["missing mechanics structural graph engine"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-ADHOC-LOAD-CHECK"],
                related_paths=[MECH_ENGINE_REL],
            )
        )
        return findings

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "src/mechanics/",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _INLINE_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_strength_check_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline structural load/strength check outside mechanics substrate", snippet[:180]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-NO-ADHOC-LOAD-CHECK"],
                            related_paths=[rel_path, MECH_ENGINE_REL],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

