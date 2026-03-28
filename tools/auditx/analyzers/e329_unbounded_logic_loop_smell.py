"""E329 unbounded-logic-loop smell analyzer for LOGIC-10 envelope hardening."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E329_UNBOUNDED_LOGIC_LOOP_SMELL"


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

    eval_rel = "logic/eval/logic_eval_engine.py"
    eval_text = _read_text(repo_root, eval_rel)
    for token in ("_loop_policy_refusal(", "REFUSAL_LOGIC_EVAL_LOOP_POLICY", "loop_classifications"):
        if token in eval_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_logic_loop_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=eval_rel,
                line=1,
                evidence=["logic evaluation path missing bounded-loop protection token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGIC-LOOP-REFUSAL-STABLE"],
                related_paths=[eval_rel],
            )
        )

    stress_rel = "tools/logic/tool_run_logic_stress.py"
    stress_text = _read_text(repo_root, stress_rel)
    for token in ("loop_refusal_deterministic", "no_unbounded_loops", "determinism_across_thread_counts"):
        if token in stress_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_logic_loop_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=stress_rel,
                line=1,
                evidence=["logic stress harness missing bounded-loop assertion token", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-LOOP-REFUSAL-STABLE"],
                related_paths=[stress_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_logic_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    for token in ("reason_code", "logic_eval_record_hash_chain", "forced_expand_event_hash_chain"):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unbounded_logic_loop_smell",
                severity="RISK",
                confidence=0.85,
                file_path=replay_rel,
                line=1,
                evidence=["logic replay surface missing loop-refusal proof token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-LOOP-REFUSAL-STABLE"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
