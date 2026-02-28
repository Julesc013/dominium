"""E90 silent flow smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E90_SILENT_FLOW_SMELL"
WATCH_PREFIXES = ("src/core/flow/", "src/logistics/", "tools/xstack/sessionx/")

FLOW_ENGINE_PATH = "src/core/flow/flow_engine.py"
LOGISTICS_ENGINE_PATH = "src/logistics/logistics_engine.py"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _missing_token_finding(*, file_path: str, token: str, invariant_id: str):
    return make_finding(
        analyzer_id=ANALYZER_ID,
        category="architecture.silent_flow_smell",
        severity="RISK",
        confidence=0.9,
        file_path=file_path,
        line=1,
        evidence=["missing expected deterministic flow event token", token],
        suggested_classification="NEEDS_REVIEW",
        recommended_action="ADD_RULE",
        related_invariants=[invariant_id],
        related_paths=[file_path],
    )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    flow_text = _read_text(repo_root, FLOW_ENGINE_PATH)
    if not flow_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_flow_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=FLOW_ENGINE_PATH,
                line=1,
                evidence=["missing flow engine"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DUPLICATE-FLOW-LOGIC"],
                related_paths=[FLOW_ENGINE_PATH],
            )
        )
    else:
        for token in ("tick_flow_channels(", "normalize_flow_transfer_event(", "transfer_events"):
            if token not in flow_text:
                findings.append(
                    _missing_token_finding(
                        file_path=FLOW_ENGINE_PATH,
                        token=token,
                        invariant_id="INV-NO-DUPLICATE-FLOW-LOGIC",
                    )
                )

    logistics_text = _read_text(repo_root, LOGISTICS_ENGINE_PATH)
    if not logistics_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_flow_smell",
                severity="VIOLATION",
                confidence=0.95,
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
        for token in ("tick_flow_channels(", "flow_transfer_events", "shipment_arrive"):
            if token not in logistics_text:
                findings.append(
                    _missing_token_finding(
                        file_path=LOGISTICS_ENGINE_PATH,
                        token=token,
                        invariant_id="INV-FLOW-USES-LEDGER-FOR-CONSERVED",
                    )
                )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

