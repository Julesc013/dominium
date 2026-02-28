"""E77 surface leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E77_SURFACE_LEAK_SMELL"
ACTION_SURFACE_ENGINE_PATH = "src/interaction/action_surface_engine.py"
AFFORDANCE_PATH = "src/client/interaction/affordance_generator.py"
DISPATCH_PATH = "src/client/interaction/interaction_dispatch.py"
REQUIRED_ENGINE_TOKENS = (
    "_visible_under_policy(",
    "visibility_policy_id",
    "authority_entitlements",
    "channels",
    "process_entitlement_requirements",
)
REQUIRED_AFFORDANCE_TOKENS = (
    "surface_visibility_policy_id",
    "disabled_reason_code",
    "refusal.tool.incompatible",
)
REQUIRED_DISPATCH_TOKENS = (
    "action_surfaces",
    "build_selection_overlay(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(findings, repo_root: str, rel_path: str, tokens, invariant: str):
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.surface_leak_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=rel_path,
                line=1,
                evidence=["required ActionSurface safety file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant],
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
                category="interaction.surface_leak_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=["missing ActionSurface epistemic/tool-compat token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[invariant],
                related_paths=[rel_path],
            )
        )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    _append_missing_token_findings(
        findings,
        repo_root,
        ACTION_SURFACE_ENGINE_PATH,
        REQUIRED_ENGINE_TOKENS,
        "INV-ACTION-SURFACE-DATA-DRIVEN",
    )
    _append_missing_token_findings(
        findings,
        repo_root,
        AFFORDANCE_PATH,
        REQUIRED_AFFORDANCE_TOKENS,
        "INV-ACTION-PROCESS-ONLY",
    )
    _append_missing_token_findings(
        findings,
        repo_root,
        DISPATCH_PATH,
        REQUIRED_DISPATCH_TOKENS,
        "INV-ACTION-PROCESS-ONLY",
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

