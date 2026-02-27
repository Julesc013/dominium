"""E60 hardcoded blueprint smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E60_HARDCODED_BLUEPRINT_SMELL"
BLUEPRINT_TOKEN_RE = re.compile(r"blueprint\.[a-zA-Z0-9_.]+")
ALLOWED_PREFIXES = (
    "packs/blueprints/",
    "data/registries/blueprint_registry.json",
    "docs/",
    "schemas/",
    "schema/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
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
    findings = []
    candidate_files = []
    changed_tokens = sorted(set(_norm(path) for path in list(changed_files or []) if isinstance(path, str)))
    if changed_tokens:
        for rel_path in changed_tokens:
            if not rel_path.endswith((".py", ".c", ".h", ".cpp", ".hpp", ".json", ".md")):
                continue
            candidate_files.append(rel_path)
    else:
        for root in ("src", "tools/materials", "tools/xstack/sessionx"):
            abs_root = os.path.join(repo_root, root.replace("/", os.sep))
            if not os.path.isdir(abs_root):
                continue
            for walk_root, _dirs, files in os.walk(abs_root):
                for name in files:
                    if not name.endswith((".py", ".c", ".h", ".cpp", ".hpp", ".json", ".md")):
                        continue
                    rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                    candidate_files.append(rel_path)

    for rel_path in sorted(set(candidate_files)):
        if rel_path.startswith(ALLOWED_PREFIXES):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            match = BLUEPRINT_TOKEN_RE.search(token)
            if not match:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.hardcoded_blueprint_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["hardcoded blueprint token detected in non-data source", token[:140]],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-HARDCODED-STRUCTURES"],
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
