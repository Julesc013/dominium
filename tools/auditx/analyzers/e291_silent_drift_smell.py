"""E291 silent-drift smell analyzer for PROC-6 drift logging discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E291_SILENT_DRIFT_SMELL"


class SilentDriftSmell:
    analyzer_id = ANALYZER_ID


_DRIFT_PATTERNS = (
    re.compile(r"\bevaluate_process_drift\s*\(", re.IGNORECASE),
    re.compile(r"\bprocess_drift_state_rows\b", re.IGNORECASE),
    re.compile(r"\bdrift_event_record_rows\b", re.IGNORECASE),
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
        "src/process/process_run_engine.py",
        "src/process/drift/drift_engine.py",
        "src/process/drift/__init__.py",
        "src/process/__init__.py",
        "tools/process/tool_replay_drift_window.py",
        "tools/xstack/repox/check.py",
    }
    required_logging_tokens = (
        "drift_state_hash_chain",
        "drift_event_hash_chain",
        "decision_log_rows",
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
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _DRIFT_PATTERNS):
                        continue
                    if any(token in text for token in required_logging_tokens):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="governance.silent_drift_smell",
                            severity="RISK",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "drift pathway token appears without explicit drift hash/logging tokens",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-DRIFT-SCORE-DETERMINISTIC",
                                "INV-NO-SILENT-QC-ESCALATION",
                            ],
                            related_paths=[
                                rel_path,
                                "src/process/process_run_engine.py",
                                "src/process/drift/drift_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
