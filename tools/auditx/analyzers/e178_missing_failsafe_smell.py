"""E178 missing fail-safe smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E178_MISSING_FAILSAFE_SMELL"


class MissingFailSafeSmell:
    analyzer_id = ANALYZER_ID


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

    checks = (
        (
            "docs/safety/SAFETY_PATTERN_LIBRARY.md",
            ("FAIL-SAFE DEFAULT", "safety.fail_safe_stop"),
            "SAFETY doctrine must include fail-safe baseline mapping and pattern id declaration",
        ),
        (
            "tools/xstack/sessionx/process_runtime.py",
            ('elif process_id == "process.safety_tick":', "safety.fail_safe_stop"),
            "runtime must expose process.safety_tick and fail-safe pattern hook usage",
        ),
        (
            "src/safety/safety_engine.py",
            ("def evaluate_safety_instances(", "status=\"triggered\""),
            "safety engine must evaluate deterministic trigger outcomes for fail-safe activation",
        ),
    )
    for rel_path, required_tokens, message in checks:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_failsafe_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["file missing for fail-safe coverage check"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-ADHOC-SAFETY-LOGIC"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_failsafe_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing fail-safe token", token, message],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-ADHOC-SAFETY-LOGIC"],
                    related_paths=[rel_path, "docs/safety/SAFETY_PATTERN_LIBRARY.md"],
                )
            )
    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
