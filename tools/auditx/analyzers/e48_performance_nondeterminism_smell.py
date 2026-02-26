"""E48 performance non-determinism smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E48_PERFORMANCE_NONDETERMINISM_SMELL"
TARGET_PATHS = (
    "src/performance/cost_engine.py",
    "src/performance/inspection_cache.py",
    "src/reality/transitions/transition_controller.py",
    "tools/xstack/sessionx/process_runtime.py",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"\brandom\.", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
    re.compile(r"\btime\.time\(", re.IGNORECASE),
    re.compile(r"\btime\.perf_counter\(", re.IGNORECASE),
    re.compile(r"\btime\.monotonic\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.now\(", re.IGNORECASE),
    re.compile(r"\buuid\.uuid4\(", re.IGNORECASE),
    re.compile(r"\bos\.urandom\(", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


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
    del changed_files
    findings = []

    required_tokens_by_path = {
        "src/performance/cost_engine.py": (
            "compute_cost_snapshot(",
            "evaluate_envelope(",
            "reserve_inspection_budget(",
        ),
        "src/performance/inspection_cache.py": (
            "build_cache_key(",
            "build_inspection_snapshot(",
            "cache_lookup_or_store(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.inspect_generate_snapshot",
            "inspection_cache_lookup_or_store(",
            "reserve_inspection_budget(",
            "skip_state_log = True",
        ),
    }

    for rel_path in TARGET_PATHS:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="performance.performance_nondeterminism_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["performance file missing for determinism scan"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
                    related_paths=[rel_path],
                )
            )
            continue

        for token in required_tokens_by_path.get(rel_path, ()):
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="performance.performance_nondeterminism_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic performance token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
                    related_paths=[rel_path],
                )
            )

        for line_no, line in _iter_lines(repo_root, rel_path):
            for pattern in FORBIDDEN_PATTERNS:
                if not pattern.search(str(line)):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="performance.performance_nondeterminism_smell",
                        severity="VIOLATION",
                        confidence=0.98,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "nondeterministic API usage in performance constitution path",
                            str(line).strip()[:140],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
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

