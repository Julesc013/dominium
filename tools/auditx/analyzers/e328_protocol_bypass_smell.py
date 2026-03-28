"""E328 protocol-bypass smell analyzer for LOGIC-9."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E328_PROTOCOL_BYPASS_SMELL"


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

    engine_rel = "logic/protocol/protocol_engine.py"
    engine_text = _read_text(repo_root, engine_rel)
    for token in ("process_signal_send(", "transport_logic_sig_receipts", "logic_protocol_target_slots", "process_signal_set_fn("):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.protocol_bypass_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=engine_rel,
                line=1,
                evidence=["protocol engine missing required transport-or-delivery seam token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-FRAME-DELIVERY"],
                related_paths=[engine_rel],
            )
        )

    runtime_rel = "logic/eval/logic_eval_engine.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    for token in ("transport_logic_sig_receipts(", "arbitrate_logic_protocol_frames("):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.protocol_bypass_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["logic evaluation path missing protocol transport token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-FRAME-DELIVERY"],
                related_paths=[runtime_rel],
            )
        )

    shard_rel = "docs/logic/PROTOCOL_SHARD_RULES.md"
    shard_text = _read_text(repo_root, shard_rel).lower()
    for token in ("boundary", "carrier.sig", "no direct synchronous"):
        if token in shard_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.protocol_bypass_smell",
                severity="RISK",
                confidence=0.84,
                file_path=shard_rel,
                line=1,
                evidence=["protocol shard rule missing bypass-prevention token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-NO-DIRECT-FRAME-DELIVERY"],
                related_paths=[shard_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
