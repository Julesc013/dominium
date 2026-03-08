"""E346 direct geometry write smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E346_DIRECT_GEOMETRY_WRITE_SMELL"

_WRITE_PATTERNS = (
    re.compile(r"\bstate\s*\[\s*[\"']geometry_cell_states[\"']\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\bstate\s*\[\s*[\"']geometry_chunk_states[\"']\s*\]\s*=", re.IGNORECASE),
)

_ALLOWED_FILES = {
    "tools/xstack/sessionx/process_runtime.py",
}

_SKIP_PREFIXES = (
    "tools/xstack/testx/tests/",
    "tools/auditx/analyzers/",
    "docs/",
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
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(_SKIP_PREFIXES):
                    continue
                if rel_path in _ALLOWED_FILES:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _WRITE_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="geometry.direct_geometry_write_smell",
                            severity="RISK",
                            confidence=0.96,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["direct geometry state write detected outside canonical process runtime", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-GEOMETRY-MUTATION-PROCESS-ONLY",
                                "INV-NO-DIRECT-TERRAIN-WRITES",
                            ],
                            related_paths=[rel_path, "tools/xstack/sessionx/process_runtime.py"],
                        )
                    )
                    break
    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
