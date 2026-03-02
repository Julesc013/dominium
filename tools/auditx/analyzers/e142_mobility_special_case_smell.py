"""E142 mobility special-case smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E142_MOBILITY_SPECIAL_CASE_SMELL"


class MobilitySpecialCaseSmell:
    analyzer_id = ANALYZER_ID


_SPECIALCASE_PATTERNS = (
    re.compile(r"\bspec\.track\b", re.IGNORECASE),
    re.compile(r"\bmovement_surface\b[^\n]*(?:track|rail|road)", re.IGNORECASE),
    re.compile(r"\bif\b[^\n]*(?:train|rail|track|road)[^\n]*(?:speed|traction|signal|derail|curve|curvature)", re.IGNORECASE),
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

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
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
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _SPECIALCASE_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.mobility_special_case_smell",
                            severity="RISK",
                            confidence=0.88,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["mobility special-case branch detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-TRAIN-SPECIALCASE",
                                "INV-MOB-USES-GUIDEGEOMETRY",
                                "INV-MOB-USES-NETWORKGRAPH",
                            ],
                            related_paths=[rel_path, "docs/mobility/MOBILITY_CONSTITUTION.md"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
