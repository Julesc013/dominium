"""E297 silent process execution smell analyzer for PROC-9 envelope logging."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E297_SILENT_PROCESS_EXECUTION_SMELL"


class SilentProcessExecutionSmell:
    analyzer_id = ANALYZER_ID


_EXECUTION_PATTERNS = (
    re.compile(r"\bexecute_process_capsule\s*\(", re.IGNORECASE),
    re.compile(r"\bexecute_pipeline\s*\(", re.IGNORECASE),
    re.compile(r"\brun_proc_stress\s*\(", re.IGNORECASE),
)

_RECORD_TOKENS = (
    "process_run_record_rows",
    "capsule_execution_record_rows",
    "deployment_record_rows",
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
        "tools/process/tool_run_proc_stress.py",
        "tools/xstack/sessionx/process_runtime.py",
        "src/process/capsules/capsule_executor.py",
        "src/process/process_run_engine.py",
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
                if not any(pattern.search(text) for pattern in _EXECUTION_PATTERNS):
                    continue
                if all(token in text for token in _RECORD_TOKENS):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.silent_process_execution_smell",
                        severity="RISK",
                        confidence=0.88,
                        file_path=rel_path,
                        line=1,
                        evidence=[
                            "process execution token detected without explicit canonical record outputs",
                        ],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-PROC-CAPSULE-EXEC-RECORDED",
                        ],
                        related_paths=[
                            rel_path,
                            "tools/process/tool_run_proc_stress.py",
                            "src/process/process_run_engine.py",
                        ],
                    )
                )
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
