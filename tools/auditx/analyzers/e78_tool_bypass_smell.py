"""E78 tool bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E78_TOOL_BYPASS_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
DISPATCH_PATH = "client/interaction/interaction_dispatch.py"
ACTION_SURFACE_PATH = "interaction/action_surface_engine.py"
AFFORDANCE_PATH = "client/interaction/affordance_generator.py"

REQUIRED_RUNTIME_TOKENS = (
    "process.tool_bind",
    "process.tool_unbind",
    "process.tool_use_prepare",
    "process.tool_readout_tick",
    "_active_tool_binding(tool_bindings, subject_id)",
    "refusal.tool.bind_required",
)
REQUIRED_DISPATCH_TOKENS = (
    "_active_tool_context(",
    "if reason_code in {\"refusal.tool.bind_required\", \"refusal.tool.not_found\"}:",
    "_record_authority_violation(",
)
REQUIRED_SURFACE_TOKENS = (
    "_tool_type_rows_by_id(",
    "_tool_effect_rows_by_id(",
    "tool_process_allowed_ids",
)
REQUIRED_AFFORDANCE_TOKENS = (
    "tool_process_compatible",
    "tool_process_allowed_ids",
    "refusal.tool.incompatible",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(
    findings,
    *,
    repo_root: str,
    rel_path: str,
    tokens,
    invariant_id: str,
) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.tool_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required ACT-2 file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )
        return
    for token in tokens:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.tool_bypass_smell",
                severity="RISK",
                confidence=0.88,
                file_path=rel_path,
                line=1,
                evidence=["missing tool-gating token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=PROCESS_RUNTIME_PATH,
        tokens=REQUIRED_RUNTIME_TOKENS,
        invariant_id="INV-TOOL_USE_REQUIRES_BIND",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=DISPATCH_PATH,
        tokens=REQUIRED_DISPATCH_TOKENS,
        invariant_id="INV-TOOL_USE_REQUIRES_BIND",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=ACTION_SURFACE_PATH,
        tokens=REQUIRED_SURFACE_TOKENS,
        invariant_id="INV-TOOLS-DATA-DRIVEN",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=AFFORDANCE_PATH,
        tokens=REQUIRED_AFFORDANCE_TOKENS,
        invariant_id="INV-TOOLS-DATA-DRIVEN",
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

