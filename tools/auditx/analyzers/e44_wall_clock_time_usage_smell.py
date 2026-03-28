"""E44 wall-clock time usage smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E44_WALL_CLOCK_TIME_USAGE_SMELL"
SCAN_PATHS = (
    "engine/time/time_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/scheduler.py",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\btime\.time\(", re.IGNORECASE),
    re.compile(r"\btime\.perf_counter\(", re.IGNORECASE),
    re.compile(r"\btime\.monotonic\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.now\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.utcnow\(", re.IGNORECASE),
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

    for rel_path in SCAN_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="time.wall_clock_time_usage_smell",
                    severity="RISK",
                    confidence=0.83,
                    file_path=rel_path,
                    line=1,
                    evidence=["required time runtime path is missing for wall-clock scan"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-WALLCLOCK-IN-TIME-ENGINE"],
                    related_paths=[rel_path],
                )
            )
            continue

        for line_no, line in _iter_lines(repo_root, rel_path):
            for pattern in FORBIDDEN_PATTERNS:
                if not pattern.search(str(line)):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="time.wall_clock_time_usage_smell",
                        severity="VIOLATION" if rel_path == "engine/time/time_engine.py" else "RISK",
                        confidence=0.97 if rel_path == "engine/time/time_engine.py" else 0.9,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "wall-clock API usage detected in deterministic time path",
                            str(line).strip()[:140],
                        ],
                        suggested_classification="INVALID" if rel_path == "engine/time/time_engine.py" else "NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-WALLCLOCK-IN-TIME-ENGINE"],
                        related_paths=[rel_path],
                    )
                )

    time_engine_text = _read_text(repo_root, "engine/time/time_engine.py")
    for token in ("advance_time(", "_tick_dt_permille(", "policy_context", "time_tick_log"):
        if token in time_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="time.wall_clock_time_usage_smell",
                severity="RISK",
                confidence=0.85,
                file_path="engine/time/time_engine.py",
                line=1,
                evidence=["time engine missing deterministic governance token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-WALLCLOCK-IN-TIME-ENGINE"],
                related_paths=["engine/time/time_engine.py"],
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
