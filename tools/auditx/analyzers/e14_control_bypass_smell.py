"""E14 Control bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E14_CONTROL_BYPASS_SMELL"
WATCH_PREFIXES = (
    "engine/",
    "game/",
    "client/",
    "server/",
    "tools/",
    "launcher/",
    "setup/",
)

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
_ALLOWED_MUTATION_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/creator.py",
)
_ALLOWED_EXTS = {".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".cmd"}
_CONTROL_MUTATION_RE = re.compile(
    r"state\s*\[\s*[\"'](control_bindings|controller_assemblies)[\"']\s*\]\s*=|"
    r"\b(control_bindings|controller_assemblies)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
    re.IGNORECASE,
)


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
        if any(rel_path.startswith(prefix) for prefix in _ALLOWED_MUTATION_PREFIXES):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            if not _CONTROL_MUTATION_RE.search(str(line)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="control.bypass_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Control state mutation detected outside process runtime.",
                        str(line).strip()[:200],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-CONTROL-PROCESSES-ONLY"],
                    related_paths=[rel_path, "tools/xstack/sessionx/process_runtime.py"],
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

