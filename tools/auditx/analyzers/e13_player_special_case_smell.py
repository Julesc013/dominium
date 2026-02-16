"""E13 Player special-case smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E13_PLAYER_SPECIAL_CASE_SMELL"
WATCH_PREFIXES = (
    "engine/",
    "game/",
    "client/",
    "server/",
    "tools/",
    "launcher/",
    "setup/",
)

_PLAYER_LITERAL_RE = re.compile(r"[\"']player(?:\.[a-z0-9_.-]+)?[\"']", re.IGNORECASE)
_SCAN_ROOTS = (
    "engine",
    "game",
    "client",
    "server",
    "tools",
    "launcher",
    "setup",
)
_SKIP_PREFIXES = (
    "data/",
    "docs/",
    "schemas/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
)
_ALLOWED_EXTS = {".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".cmd"}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_code_files(repo_root: str):
    for root in _SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                _, ext = os.path.splitext(name.lower())
                if ext not in _ALLOWED_EXTS:
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if any(rel_path.startswith(prefix) for prefix in _SKIP_PREFIXES):
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    for rel_path in _iter_code_files(repo_root):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            if not _PLAYER_LITERAL_RE.search(str(line)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="control.player_special_case_smell",
                    severity="WARN",
                    confidence=0.82,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Hardcoded player literal detected in control/runtime code path.",
                        str(line).strip()[:200],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-HARDCODED-PLAYER"],
                    related_paths=[rel_path],
                )
            )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

