"""E139 inline friction smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E139_INLINE_FRICTION_SMELL"


class InlineFrictionSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = ("src/", "tools/xstack/sessionx/")
_FRICTION_PATTERNS = (
    re.compile(r"\b(?:traction|friction)\b\s*[*+\-\/]=\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)", re.IGNORECASE),
    re.compile(r"\bif\b[^\n]*(?:rain|fog|ice|snow|weather)[^\n]*(?:traction|friction)\b", re.IGNORECASE),
    re.compile(r"\b(?:traction|friction)_permille\b[^\n]*=\s*(?!.*field_)"),
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

    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
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
                if rel_path in ("fields/field_engine.py", "tools/xstack/sessionx/process_runtime.py"):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _FRICTION_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_friction_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline friction/traction logic outside FIELD runtime", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-FIELD-QUERIES-ONLY", "INV-NO-ADHOC-WEATHER-FLAGS"],
                            related_paths=[rel_path, "fields/field_engine.py", "tools/xstack/sessionx/process_runtime.py"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

