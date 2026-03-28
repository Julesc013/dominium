"""E319 silent-compiled-invalidation smell analyzer for LOGIC-6."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E319_SILENT_COMPILED_INVALIDATION_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e319_silent_compiled_invalidation_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/LOGIC_COMPILATION_MODEL.md",
    "logic/eval/logic_eval_engine.py",
    "tools/logic/tool_replay_logic_window.py",
    "tools/logic/tool_replay_compiled_logic_window.py",
)


class SilentCompiledInvalidationSmell:
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

    doctrine_rel = "docs/logic/LOGIC_COMPILATION_MODEL.md"
    doctrine_text = _read_text(repo_root, doctrine_rel).lower()
    for token in ("must not silently change path", "explicit fallback", "forced expand"):
        if token in doctrine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_compiled_invalidation_smell",
                severity="RISK",
                confidence=0.85,
                file_path=doctrine_rel,
                line=1,
                evidence=["logic compilation doctrine missing explicit invalidation/fallback token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-NO-SILENT-FALLBACK"],
                related_paths=[doctrine_rel],
            )
        )

    eval_rel = "logic/eval/logic_eval_engine.py"
    eval_text = _read_text(repo_root, eval_rel)
    for token in (
        "compiled_fallback_logged",
        "build_logic_compiled_invalid_explain_artifact(",
        "build_logic_compiled_forced_expand_event(",
        "compiled_path_selected",
    ):
        if token in eval_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_compiled_invalidation_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=eval_rel,
                line=1,
                evidence=["logic eval path missing explicit compiled invalidation token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-FALLBACK"],
                related_paths=[eval_rel, "logic/compile/logic_compiler.py"],
            )
        )

    replay_rel = "tools/logic/tool_replay_logic_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    for token in ("forced_expand_event_hash_chain", "compile_result_hash_chain"):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_compiled_invalidation_smell",
                severity="RISK",
                confidence=0.87,
                file_path=replay_rel,
                line=1,
                evidence=["logic replay window missing invalidation/fallback proof surface", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-FALLBACK"],
                related_paths=[replay_rel],
            )
        )

    compiled_replay_rel = "tools/logic/tool_replay_compiled_logic_window.py"
    compiled_replay_text = _read_text(repo_root, compiled_replay_rel)
    for token in ("compiled_path_observed", "reason_code"):
        if token in compiled_replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_compiled_invalidation_smell",
                severity="RISK",
                confidence=0.88,
                file_path=compiled_replay_rel,
                line=1,
                evidence=["compiled replay tool missing fallback-detection token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-FALLBACK"],
                related_paths=[compiled_replay_rel, replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
