"""E322 unbounded-trace smell analyzer for LOGIC-7."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E322_UNBOUNDED_TRACE_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e322_unbounded_trace_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/DEBUG_AND_INSTRUMENTATION.md",
    "schema/logic/debug_trace_request.schema",
    "schema/logic/debug_trace_artifact.schema",
    "schema/logic/debug_sampling_policy.schema",
    "data/registries/debug_sampling_policy_registry.json",
    "logic/debug/debug_engine.py",
    "tools/logic/tool_replay_trace_window.py",
)


class UnboundedTraceSmell:
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

    doc_rel = "docs/logic/DEBUG_AND_INSTRUMENTATION.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("bounded length", "bounded sampling rate", "deterministic sampling strategy", "observer effect"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_trace_smell",
                severity="RISK",
                confidence=0.84,
                file_path=doc_rel,
                line=1,
                evidence=["debug doctrine missing bounded-trace token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-TRACE-BOUNDED"],
                related_paths=[doc_rel],
            )
        )

    schema_rel = "schema/logic/debug_sampling_policy.schema"
    schema_text = _read_text(repo_root, schema_rel)
    for token in ("max_points", "max_ticks", "max_samples", "throttle_strategy"):
        if token in schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_trace_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=schema_rel,
                line=1,
                evidence=["debug sampling policy schema missing bounded-trace field", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRACE-BOUNDED"],
                related_paths=[schema_rel],
            )
        )

    registry_rel = "data/registries/debug_sampling_policy_registry.json"
    registry_text = _read_text(repo_root, registry_rel)
    for token in ("debug.sample.default", "max_points", "max_ticks", "max_samples", "throttle_strategy"):
        if token in registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_trace_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=registry_rel,
                line=1,
                evidence=["debug sampling registry missing bounded-trace token", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRACE-BOUNDED"],
                related_paths=[registry_rel],
            )
        )

    engine_rel = "logic/debug/debug_engine.py"
    engine_text = _read_text(repo_root, engine_rel)
    for token in ("max_points", "max_ticks", "max_samples", "throttle_strategy", "sample_count", "trace_compactable"):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_trace_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=engine_rel,
                line=1,
                evidence=["logic debug engine missing bounded-trace token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-TRACE-BOUNDED", "INV-DEBUG-BUDGETED"],
                related_paths=[engine_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_trace_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    for token in ("logic_debug_trace_hash_chain", "samples", "sample_count"):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_trace_smell",
                severity="RISK",
                confidence=0.88,
                file_path=replay_rel,
                line=1,
                evidence=["trace replay tool missing bounded-trace proof token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-TRACE-BOUNDED"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
