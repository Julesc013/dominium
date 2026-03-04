"""E229 wallclock use smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E229_WALLCLOCK_USE_SMELL"
WATCH_PREFIXES = ("src/time/", "src/reality/transitions/", "src/performance/", "src/mobility/", "tools/xstack/sessionx/")

_WALLCLOCK_PATTERN = re.compile(
    r"\b(?:time\.time|time\.perf_counter|time\.monotonic|datetime\.now|datetime\.utcnow|time\.sleep)\s*\(",
    re.IGNORECASE,
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
        os.path.join(repo_root, "src", "time"),
        os.path.join(repo_root, "src", "reality", "transitions"),
        os.path.join(repo_root, "src", "performance"),
        os.path.join(repo_root, "src", "mobility"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
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
                    if not _WALLCLOCK_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="time.wallclock_use_smell",
                            severity="VIOLATION",
                            confidence=0.95,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "wall-clock usage detected in authoritative temporal/runtime path",
                                snippet[:140],
                            ],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-WALLCLOCK-TIME",
                            ],
                            related_paths=[rel_path],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
