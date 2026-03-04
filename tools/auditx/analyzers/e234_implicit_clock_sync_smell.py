"""E234 implicit clock synchronization smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E234_IMPLICIT_CLOCK_SYNC_SMELL"

_IMPLICIT_SYNC_PATTERNS = (
    re.compile(r"\b(?:clock_sync|sync_clock|time_sync|auto_sync|synchronize_clock)\b", re.IGNORECASE),
    re.compile(r"\bremote_domain_time\b.*\blocal_domain_time\b", re.IGNORECASE),
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
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "tools/xstack/sessionx/process_runtime.py",
        "tools/time/tool_verify_sync_consistency.py",
    }

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
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _IMPLICIT_SYNC_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="time.implicit_clock_sync_smell",
                            severity="VIOLATION",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "implicit clock synchronization pattern detected outside process.time_adjust",
                                snippet[:140],
                            ],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-TIME-ADJUST-LOGGED",
                                "INV-NO-CANONICAL-TICK-DRIFT",
                            ],
                            related_paths=[rel_path],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
