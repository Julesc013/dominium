"""E318 implicit-timing-assumption smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E318_IMPLICIT_TIMING_ASSUMPTION_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e318_implicit_timing_assumption_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/TIMING_AND_OSCILLATION_MODEL.md",
    "src/logic/timing/",
    "src/logic/eval/",
    "tools/logic/tool_replay_timing_window.py",
)

_SUSPECT_PATTERNS = (
    re.compile(r"\btime\.time\s*\("),
    re.compile(r"\bdatetime\.(?:now|utcnow)\s*\("),
    re.compile(r"\bperf_counter\s*\("),
    re.compile(r"\bsleep\s*\("),
    re.compile(r"\b(?:clock_hz|frequency_hz|tick_rate|period_ms|deadline_ms|real_time|wall_clock)\b", re.IGNORECASE),
)


class ImplicitTimingAssumptionSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _scan_runtime_files(repo_root: str):
    for root, _dirs, files in os.walk(os.path.join(repo_root, "src", "logic")):
        for name in files:
            if name.endswith(".py"):
                yield _norm(os.path.relpath(os.path.join(root, name), repo_root))
    for root, _dirs, files in os.walk(os.path.join(repo_root, "tools", "logic")):
        for name in files:
            if name.endswith(".py"):
                yield _norm(os.path.relpath(os.path.join(root, name), repo_root))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    doc_rel = "docs/logic/TIMING_AND_OSCILLATION_MODEL.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("delay.temporal_domain", "no global free-running clock", "watchdog", "synchronizer"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.implicit_timing_assumption_smell",
                severity="RISK",
                confidence=0.81,
                file_path=doc_rel,
                line=1,
                evidence=["timing doctrine missing required token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-DELAY-USES-TEMP", "INV-NO-GLOBAL-CLOCK"],
                related_paths=[doc_rel],
            )
        )

    propagate_rel = "src/logic/eval/propagate_engine.py"
    propagate_text = _read_text(repo_root, propagate_rel)
    for token in ("evaluate_time_mappings(", "temporal_domain_registry_payload", "time_mapping_registry_payload"):
        if token in propagate_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.implicit_timing_assumption_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=propagate_rel,
                line=1,
                evidence=["logic propagation missing TEMP timing token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DELAY-USES-TEMP"],
                related_paths=[propagate_rel],
            )
        )

    engine_rel = "src/logic/eval/logic_eval_engine.py"
    engine_text = _read_text(repo_root, engine_rel)
    for token in ("detect_network_oscillation(", "evaluate_logic_timing_constraints(", "requires_l2_timing"):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.implicit_timing_assumption_smell",
                severity="RISK",
                confidence=0.86,
                file_path=engine_rel,
                line=1,
                evidence=["logic evaluation missing timing-governance token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-DELAY-USES-TEMP", "INV-OSCILLATION-EXPLAIN-AVAILABLE"],
                related_paths=[engine_rel, propagate_rel],
            )
        )

    for rel_path in sorted(set(_scan_runtime_files(repo_root))):
        if rel_path.startswith("tools/xstack/testx/tests/"):
            continue
        text = _read_text(repo_root, rel_path)
        for pattern in _SUSPECT_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="logic.implicit_timing_assumption_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["implicit timing/global-clock token detected in logic runtime path", match.group(0)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-GLOBAL-CLOCK"],
                    related_paths=[rel_path],
                )
            )
            break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
