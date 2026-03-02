"""E146 hardcoded track spec smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E146_HARDCODED_TRACK_SPEC_SMELL"


class HardcodedTrackSpecSmell:
    analyzer_id = ANALYZER_ID


_SPEC_PATTERNS = (
    re.compile(r"\b(?:gauge_mm|track_gauge_mm)\b\s*[:=]\s*\d{2,6}\b", re.IGNORECASE),
    re.compile(r"[\"'](?:gauge_mm|track_gauge_mm)[\"']\s*:\s*\d{2,6}\b", re.IGNORECASE),
    re.compile(r"\bmin_curvature_radius_mm\b\s*[:=]\s*\d{4,8}\b", re.IGNORECASE),
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
        "src/specs/",
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
                    if not any(pattern.search(snippet) for pattern in _SPEC_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.hardcoded_track_spec_smell",
                            severity="RISK",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["hardcoded track spec constant detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-HARDCODED-GAUGE",
                                "INV-NO-HARDCODED-GAUGE-WIDTH-SPECS",
                            ],
                            related_paths=[rel_path, "packs/specs/specs.default.realistic.m1/data/spec_sheets.json"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
