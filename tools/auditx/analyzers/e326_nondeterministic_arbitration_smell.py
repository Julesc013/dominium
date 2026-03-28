"""E326 nondeterministic-arbitration smell analyzer for LOGIC-9."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E326_NONDETERMINISTIC_ARBITRATION_SMELL"


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
    for token in ("sorted(", "arb.fixed_priority", "arb.time_slice", "arb.token", "build_arbitration_state_row("):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.nondeterministic_arbitration_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=engine_rel,
                line=1,
                evidence=["protocol arbitration path missing deterministic arbitration token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-PROTOCOL-ARBITRATION-DETERMINISTIC"],
                related_paths=[engine_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_protocol_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    for token in ("logic_protocol_frame_hash_chain", "logic_protocol_event_hash_chain", "logic_arbitration_state_hash_chain"):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.nondeterministic_arbitration_smell",
                severity="RISK",
                confidence=0.87,
                file_path=replay_rel,
                line=1,
                evidence=["protocol replay surface missing deterministic arbitration proof token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-PROTOCOL-ARBITRATION-DETERMINISTIC"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
