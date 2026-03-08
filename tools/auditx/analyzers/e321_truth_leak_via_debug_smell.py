"""E321 truth-leak-via-debug smell analyzer for LOGIC-7."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E321_TRUTH_LEAK_VIA_DEBUG_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e321_truth_leak_via_debug_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/DEBUG_AND_INSTRUMENTATION.md",
    "src/logic/debug/",
    "tools/logic/tool_replay_trace_window.py",
)

_LEAK_PATTERNS = (
    re.compile(r"\btruth_model\b", re.IGNORECASE),
    re.compile(r"\brender_model\b", re.IGNORECASE),
    re.compile(r"\buniverse_state\b", re.IGNORECASE),
)


class TruthLeakViaDebugSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _debug_runtime_paths(repo_root: str):
    for root_rel in ("src/logic/debug", "tools/logic"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                yield _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    doctrine_rel = "docs/logic/DEBUG_AND_INSTRUMENTATION.md"
    doctrine_text = _read_text(repo_root, doctrine_rel).lower()
    for token in ("without omniscience", "epistemic", "remote monitoring requires", "force expand"):
        if token in doctrine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.truth_leak_via_debug_smell",
                severity="RISK",
                confidence=0.84,
                file_path=doctrine_rel,
                line=1,
                evidence=["logic debug doctrine missing anti-leak token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-NO-OMNISCIENT-DEBUG"],
                related_paths=[doctrine_rel],
            )
        )

    engine_rel = "src/logic/debug/debug_engine.py"
    engine_text = _read_text(repo_root, engine_rel)
    for token in ("generate_measurement_observation(", "REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND", "available_instrument_type_ids"):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.truth_leak_via_debug_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=engine_rel,
                line=1,
                evidence=["logic debug engine missing epistemic gating token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-OMNISCIENT-DEBUG"],
                related_paths=[engine_rel],
            )
        )

    for rel_path in sorted(set(_debug_runtime_paths(repo_root))):
        text = _read_text(repo_root, rel_path)
        for pattern in _LEAK_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="logic.truth_leak_via_debug_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["logic debug path references omniscient state token", match.group(0)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-OMNISCIENT-DEBUG"],
                    related_paths=[rel_path],
                )
            )
            break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
