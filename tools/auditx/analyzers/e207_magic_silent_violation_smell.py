"""E207 magic silent violation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E207_MAGIC_SILENT_VIOLATION_SMELL"


class MagicSilentViolationSmell:
    analyzer_id = ANALYZER_ID


_MAGIC_VIOLATION_PATTERNS = (
    re.compile(r"\bmagic_injection\b", re.IGNORECASE),
    re.compile(r"\bconservation_violation\b", re.IGNORECASE),
)

_REQUIRED_LOG_TOKENS = (
    "exception_event",
    "deterministic_fingerprint",
    "ledger",
    "decision_log",
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
        "tools/xstack/repox/check.py",
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
                    if not any(pattern.search(snippet) for pattern in _MAGIC_VIOLATION_PATTERNS):
                        continue
                    lower = snippet.lower()
                    if any(token in lower for token in _REQUIRED_LOG_TOKENS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.magic_silent_violation_smell",
                            severity="RISK",
                            confidence=0.84,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["magic/conservation violation token without explicit exception/proof logging token", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-SILENT-VIOLATIONS",
                                "INV-PHYS-PROFILE-DECLARED",
                            ],
                            related_paths=[
                                rel_path,
                                "docs/physics/PHYSICS_CONSTITUTION.md",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
