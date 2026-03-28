"""E288 undeclared-maturity-transition smell analyzer for PROC-4 discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E288_UNDECLARED_MATURITY_TRANSITION_SMELL"


class UndeclaredMaturityTransitionSmell:
    analyzer_id = ANALYZER_ID


_MATURITY_TRANSITION_PATTERNS = (
    re.compile(r"\bcurrent_maturity_state\b", re.IGNORECASE),
    re.compile(r"\bprocess_maturity_record_rows\b", re.IGNORECASE),
    re.compile(r"\bevaluate_process_maturity\s*\(", re.IGNORECASE),
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
        os.path.join(repo_root, "src", "process"),
        os.path.join(repo_root, "tools", "process"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "process/process_run_engine.py",
        "process/maturity/maturity_engine.py",
        "process/maturity/__init__.py",
        "process/capsules/capsule_builder.py",
        "tools/process/tool_replay_maturity_window.py",
        "tools/process/tool_generate_proc_stress.py",
        "tools/process/tool_run_proc_stress.py",
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
                    if not any(pattern.search(snippet) for pattern in _MATURITY_TRANSITION_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="governance.undeclared_maturity_transition_smell",
                            severity="RISK",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "maturity transition token appears outside canonical PROC-4 transition engine",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-MATURITY-RECORD-CANONICAL",
                            ],
                            related_paths=[
                                rel_path,
                                "process/process_run_engine.py",
                                "process/maturity/maturity_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
