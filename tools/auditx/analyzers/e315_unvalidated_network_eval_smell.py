"""E315 unvalidated-network-eval smell analyzer for LOGIC-3."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E315_UNVALIDATED_NETWORK_EVAL_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e315_unvalidated_network_eval_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "src/logic/network/",
    "tools/xstack/sessionx/process_runtime.py",
)

_ALLOWED_PATHS = {
    "logic/network/logic_network_engine.py",
    "logic/network/logic_network_validator.py",
    "logic/network/instrumentation_binding.py",
    "logic/network/__init__.py",
}
_EXECUTION_TOKENS = (
    "evaluate_logic_network",
    "logic_network_tick",
    "propagate_signal",
    "propagate_logic_network",
    "commit_logic_network",
)


class UnvalidatedNetworkEvalSmell:
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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    if '"process.logic_network_validate"' not in runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unvalidated_network_eval_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["control-plane runtime missing process.logic_network_validate dispatch"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-NETWORK-VALIDATED-BEFORE-EVAL"],
                related_paths=[runtime_rel, "logic/network/logic_network_engine.py"],
            )
        )

    abs_root = os.path.join(repo_root, "src", "logic", "network")
    if not os.path.isdir(abs_root):
        return findings

    for walk_root, _dirs, files in os.walk(abs_root):
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
            if rel_path in _ALLOWED_PATHS:
                continue
            text = _read_text(repo_root, rel_path)
            lower_text = text.lower()
            if not any(token in lower_text for token in _EXECUTION_TOKENS):
                continue
            if "validate_logic_network" in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="logic.unvalidated_network_eval_smell",
                    severity="VIOLATION",
                    confidence=0.94,
                    file_path=rel_path,
                    line=1,
                    evidence=["logic network execution-like path appears without validator hook", rel_path],
                    suggested_classification="INVALID",
                    recommended_action="MOVE_TO_PROCESS",
                    related_invariants=["INV-LOGIC-NETWORK-VALIDATED-BEFORE-EVAL"],
                    related_paths=[rel_path, "logic/network/logic_network_validator.py"],
                )
            )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
