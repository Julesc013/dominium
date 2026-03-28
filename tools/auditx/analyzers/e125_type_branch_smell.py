"""E125 type-branch smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E125_TYPE_BRANCH_SMELL"
WATCH_PREFIXES = (
    "src/control/",
    "src/interaction/",
    "tools/xstack/sessionx/",
)
SCAN_ROOTS = (
    "src/control",
    "src/interaction",
    "tools/xstack/sessionx",
)
SCAN_EXTENSIONS = (".py",)
SKIP_PREFIXES = (
    "tools/xstack/testx/tests/",
    "tools/auditx/analyzers/",
)
TYPE_BRANCH_PATTERNS = (
    re.compile(r"\b(entity_type|assembly_type|entity_class|assembly_class)\b\s*=="),
    re.compile(r"\b\w*type\w*\s*==\s*[\"'](?:vehicle|building|machine)[\"']"),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return ""
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _scan_candidates(repo_root: str):
    for root_rel in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not str(name).lower().endswith(SCAN_EXTENSIONS):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(SKIP_PREFIXES):
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path in _scan_candidates(repo_root):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            matched = False
            for pattern in TYPE_BRANCH_PATTERNS:
                if pattern.search(snippet):
                    matched = True
                    break
            if not matched:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.type_branch_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "core gameplay type/class branch detected",
                        snippet[:200],
                    ],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TYPE-BRANCHING"],
                    related_paths=[rel_path, "control/capability/capability_engine.py"],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

