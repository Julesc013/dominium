"""E58 hardcoded periodic table smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E58_HARDCODED_PERIODIC_TABLE_SMELL"
ELEMENT_TOKEN_RE = re.compile(r"element\.[A-Z][A-Za-z0-9_]*")


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
    findings = []
    candidate_files = []
    changed_tokens = sorted(set(_norm(path) for path in list(changed_files or []) if isinstance(path, str)))
    for rel_path in changed_tokens:
        if not rel_path.startswith("src/"):
            continue
        if not rel_path.endswith((".py", ".c", ".h", ".cpp", ".hpp")):
            continue
        candidate_files.append(rel_path)
    if not candidate_files:
        for root, _dirs, files in os.walk(os.path.join(repo_root, "src")):
            for name in files:
                if not name.endswith((".py", ".c", ".h", ".cpp", ".hpp")):
                    continue
                abs_path = os.path.join(root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                candidate_files.append(rel_path)
    for rel_path in sorted(set(candidate_files)):
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if "element_registry" in token:
                continue
            if not ELEMENT_TOKEN_RE.search(token):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.hardcoded_periodic_table_smell",
                    severity="VIOLATION",
                    confidence=0.97,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["hardcoded element token detected in runtime source", token[:140]],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-HARDCODED-ELEMENTS"],
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
