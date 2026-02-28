"""E110 tools contamination smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E110_TOOLS_CONTAMINATION_SMELL"
WATCH_PREFIXES = ("src/", "engine/", "game/", "client/", "server/")

RUNTIME_ROOTS = ("src", "engine", "game", "client", "server")
RUNTIME_EXTS = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp")
PATTERNS = (
    re.compile(r"^\s*from\s+tools\.auditx\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.auditx\b", re.IGNORECASE),
    re.compile(r"^\s*from\s+tools\.governance\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.governance\b", re.IGNORECASE),
    re.compile(r"^\s*from\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]tools/", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for root in RUNTIME_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                _, ext = os.path.splitext(name)
                if ext.lower() not in RUNTIME_EXTS:
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                try:
                    lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
                except OSError:
                    continue
                for line_no, line in enumerate(lines, start=1):
                    if not any(pattern.search(line) for pattern in PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.tools_contamination_smell",
                            severity="RISK",
                            confidence=0.92,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[line.strip()[:180], "runtime path references tool-suite import/include"],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-TOOLS-IN-RUNTIME"],
                            related_paths=[rel_path],
                        )
                    )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
