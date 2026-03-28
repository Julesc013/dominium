"""E54 platform leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E54_PLATFORM_LEAK_SMELL"
PLATFORM_FILES = (
    "engine/platform/__init__.py",
    "engine/platform/platform_window.py",
    "engine/platform/platform_input.py",
    "engine/platform/platform_gfx.py",
    "engine/platform/platform_audio.py",
    "engine/platform/platform_input_routing.py",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"^\s*#\s*include\s*[<\"]windows\.h[\">]", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]X11/", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]Cocoa/", re.IGNORECASE),
    re.compile(r"\bctypes\.windll\b", re.IGNORECASE),
    re.compile(r"\bimport\s+win32api\b", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path in PLATFORM_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="platform.platform_leak_smell",
                severity="RISK",
                confidence=0.93,
                file_path=rel_path,
                line=1,
                evidence=["platform abstraction file missing; platform boundary cannot be validated"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-PLATFORM-ISOLATION"],
                related_paths=[rel_path],
            )
        )

    src_root = os.path.join(repo_root, "src")
    if os.path.isdir(src_root):
        for walk_root, dirs, files in os.walk(src_root):
            dirs[:] = sorted(dirs)
            files = sorted(files)
            rel_root = _norm(os.path.relpath(walk_root, repo_root))
            if rel_root.startswith("src/platform"):
                continue
            for name in files:
                _, ext = os.path.splitext(name.lower())
                if ext not in (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                for line_no, line in _iter_lines(repo_root, rel_path):
                    snippet = str(line).strip()
                    if not snippet:
                        continue
                    for pattern in FORBIDDEN_PATTERNS:
                        if not pattern.search(snippet):
                            continue
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="platform.platform_leak_smell",
                                severity="VIOLATION",
                                confidence=0.95,
                                file_path=rel_path,
                                line=line_no,
                                evidence=[
                                    "platform-specific OS dependency token leaked outside src/platform",
                                    snippet[:200],
                                ],
                                suggested_classification="INVALID",
                                recommended_action="REWRITE",
                                related_invariants=["INV-PLATFORM-ISOLATION"],
                                related_paths=[rel_path],
                            )
                        )
                        break

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
