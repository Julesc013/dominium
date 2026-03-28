"""E79 tool truth leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E79_TOOL_TRUTH_LEAK_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
DISPATCH_PATH = "client/interaction/interaction_dispatch.py"

REQUIRED_RUNTIME_TOKENS = (
    "inputs.get(\"perceived_now\")",
    "_upsert_tool_readout_instrument(",
    "ch.diegetic.tool.torque",
    "ch.diegetic.tool.measurement",
    "ch.diegetic.tool.health",
)
REQUIRED_OBSERVATION_TOKENS = (
    "\"ch.diegetic.tool.torque\"",
    "\"ch.diegetic.tool.measurement\"",
    "\"ch.diegetic.tool.health\"",
    "\"instrument.tool.torque\"",
    "\"instrument.tool.measurement\"",
    "\"instrument.tool.health\"",
)
FORBIDDEN_DISPATCH_TOKENS = (
    "truth_model",
    "truthmodel",
    "universe_state",
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
                category="interaction.tool_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.94,
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
                category="interaction.tool_truth_leak_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=["missing tool observation/readout safety token", token],
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
        invariant_id="INV-ACTION-PROCESS-ONLY",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=OBSERVATION_PATH,
        tokens=REQUIRED_OBSERVATION_TOKENS,
        invariant_id="INV-ACTION-PROCESS-ONLY",
    )
    dispatch_text = _read_text(repo_root, DISPATCH_PATH)
    if not dispatch_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.tool_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=DISPATCH_PATH,
                line=1,
                evidence=["interaction dispatch file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-ACTION-PROCESS-ONLY"],
                related_paths=[DISPATCH_PATH],
            )
        )
    else:
        lowered = dispatch_text.lower()
        for token in FORBIDDEN_DISPATCH_TOKENS:
            if token not in lowered:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.tool_truth_leak_smell",
                    severity="VIOLATION",
                    confidence=0.9,
                    file_path=DISPATCH_PATH,
                    line=1,
                    evidence=["dispatch path references truth payload token", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-ACTION-PROCESS-ONLY"],
                    related_paths=[DISPATCH_PATH],
                )
            )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

