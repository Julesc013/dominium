"""E330 silent-logic-throttle smell analyzer for LOGIC-10 envelope hardening."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E330_SILENT_LOGIC_THROTTLE_SMELL"


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

    stress_rel = "tools/logic/tool_run_logic_stress.py"
    stress_text = _read_text(repo_root, stress_rel)
    for token in ("throttle_event_count", "degradation_behavior", "compiled_execution_ratio", "security_block_count"):
        if token in stress_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_logic_throttle_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=stress_rel,
                line=1,
                evidence=["logic stress harness missing throttle/degrade reporting token", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-DEGRADE-LOGGED", "INV-SECURITY-BLOCK-LOGGED"],
                related_paths=[stress_rel],
            )
        )

    degrade_rel = "src/logic/eval/degradation_policy.py"
    degrade_text = _read_text(repo_root, degrade_rel)
    for token in (
        "prefer_compiled_execution",
        "reduce_low_priority_eval_frequency",
        "cap_networks_per_tick",
        "reduce_debug_sampling_rate",
        "refuse_new_debug_sessions",
        "apply_fail_safe_outputs",
    ):
        if token in degrade_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_logic_throttle_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=degrade_rel,
                line=1,
                evidence=["logic degradation policy missing deterministic action token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGIC-BUDGETED", "INV-LOGIC-DEGRADE-LOGGED"],
                related_paths=[degrade_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_logic_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    for token in ("logic_throttle_event_hash_chain", "logic_security_fail_hash_chain"):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_logic_throttle_smell",
                severity="RISK",
                confidence=0.84,
                file_path=replay_rel,
                line=1,
                evidence=["logic replay proof surface missing throttle/security hash token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-DEGRADE-LOGGED", "INV-SECURITY-BLOCK-LOGGED"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
