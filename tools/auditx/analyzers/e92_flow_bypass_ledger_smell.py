"""E92 flow bypass ledger smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E92_FLOW_BYPASS_LEDGER_SMELL"
WATCH_PREFIXES = ("src/logistics/", "tools/xstack/sessionx/")

LOGISTICS_ENGINE_PATH = "src/logistics/logistics_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"


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

    logistics_text = _read_text(repo_root, LOGISTICS_ENGINE_PATH)
    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)

    if not logistics_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.flow_bypass_ledger_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=LOGISTICS_ENGINE_PATH,
                line=1,
                evidence=["missing logistics engine"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FLOW-USES-LEDGER-FOR-CONSERVED"],
                related_paths=[LOGISTICS_ENGINE_PATH],
            )
        )
    else:
        for token in ("tick_flow_channels(", "loss_entries", "LOGISTICS_FLOW_QUANTITY_ID"):
            if token in logistics_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.flow_bypass_ledger_smell",
                    severity="RISK",
                    confidence=0.89,
                    file_path=LOGISTICS_ENGINE_PATH,
                    line=1,
                    evidence=["missing conserved-flow token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-FLOW-USES-LEDGER-FOR-CONSERVED"],
                    related_paths=[LOGISTICS_ENGINE_PATH],
                )
            )

    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.flow_bypass_ledger_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["missing process runtime"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FLOW-USES-LEDGER-FOR-CONSERVED"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in ("process.manifest_tick", "_ledger_emit_exception(", "loss_entries"):
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.flow_bypass_ledger_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["missing ledger-accounting token for conserved flow", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-FLOW-USES-LEDGER-FOR-CONSERVED"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

