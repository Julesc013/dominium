"""E87 flow bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E87_FLOW_BYPASS_SMELL"
WATCH_PREFIXES = ("src/", "tools/xstack/sessionx/")


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

    required_tokens = {
        "src/core/flow/flow_engine.py": ("flow_transfer(", "quantity_id"),
        "src/logistics/logistics_engine.py": ("tick_flow_channels(", "_best_route(", "flow_channel_id"),
        "tools/xstack/sessionx/process_runtime.py": ("_ledger_emit_exception(", "process.manifest_tick", "flow_transfer_events"),
    }
    for rel_path, tokens in required_tokens.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.flow_bypass_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["required flow/ledger integration file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-FLOW-USES-LEDGER-FOR-CONSERVED"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.flow_bypass_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing flow/ledger coupling token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-FLOW-USES-LEDGER-FOR-CONSERVED"],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
