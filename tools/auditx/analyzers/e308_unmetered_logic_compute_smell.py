"""E308 unmetered-logic-compute smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E308_UNMETERED_LOGIC_COMPUTE_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e308_unmetered_logic_compute_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/",
    "data/registries/logic_policy_registry.json",
    "data/registries/compute_budget_profile_registry.json",
    "src/logic/",
    "tools/logic/",
)


class UnmeteredLogicComputeSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid"


def _logic_runtime_paths(repo_root: str):
    for root_rel in ("src/logic", "tools/logic"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                rel_lower = rel_path.lower()
                if "transducer" in rel_lower or "carrier" in rel_lower:
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    constitution_rel = "docs/logic/LOGIC_CONSTITUTION.md"
    constitution_text = _read_text(repo_root, constitution_rel).lower()
    for token in ("instruction_units", "memory_units"):
        if token in constitution_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_compute_smell",
                severity="RISK",
                confidence=0.85,
                file_path=constitution_rel,
                line=1,
                evidence=["logic constitution missing compute budgeting token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-LOGIC-USES-COMPUTE-BUDGET"],
                related_paths=[constitution_rel],
            )
        )

    logic_policy_rel = "data/registries/logic_policy_registry.json"
    compute_rel = "data/registries/compute_budget_profile_registry.json"
    logic_payload, logic_err = _read_json(repo_root, logic_policy_rel)
    compute_payload, compute_err = _read_json(repo_root, compute_rel)
    logic_rows = list((dict(logic_payload.get("record") or {})).get("logic_policies") or logic_payload.get("logic_policies") or [])
    compute_rows = list((dict(compute_payload.get("record") or {})).get("compute_budget_profiles") or compute_payload.get("compute_budget_profiles") or [])
    known_compute_ids = {
        str(row.get("compute_profile_id", "")).strip()
        for row in compute_rows
        if isinstance(row, dict) and str(row.get("compute_profile_id", "")).strip()
    }
    if logic_err or not logic_rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_compute_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=logic_policy_rel,
                line=1,
                evidence=["logic policy registry missing or invalid"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-USES-COMPUTE-BUDGET"],
                related_paths=[logic_policy_rel, compute_rel],
            )
        )
    else:
        for row in logic_rows:
            if not isinstance(row, dict):
                continue
            policy_id = str(row.get("policy_id", "")).strip() or "<unknown>"
            compute_profile_id = str(row.get("compute_profile_id", "")).strip()
            if not compute_profile_id:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="logic.unmetered_logic_compute_smell",
                        severity="VIOLATION",
                        confidence=0.93,
                        file_path=logic_policy_rel,
                        line=1,
                        evidence=["logic policy missing compute_profile_id", policy_id],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-LOGIC-USES-COMPUTE-BUDGET"],
                        related_paths=[logic_policy_rel],
                    )
                )
                continue
            if compute_err or compute_profile_id not in known_compute_ids:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="logic.unmetered_logic_compute_smell",
                        severity="VIOLATION",
                        confidence=0.92,
                        file_path=logic_policy_rel,
                        line=1,
                        evidence=["logic policy references unknown compute profile", "{} -> {}".format(policy_id, compute_profile_id)],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-LOGIC-USES-COMPUTE-BUDGET"],
                        related_paths=[logic_policy_rel, compute_rel],
                    )
                )

    execution_tokens = ("evaluate_logic", "logic_tick", "propagate_signal", "commit_logic", "compute_next")
    delegated_budget_tokens = (
        "request_compute(",
        "request_logic_element_compute(",
        "evaluate_logic_compute_phase(",
        "process_signal_set_fn(",
        "process_signal_emit_pulse_fn(",
    )
    for rel_path in _logic_runtime_paths(repo_root):
        text = _read_text(repo_root, rel_path)
        lower_text = text.lower()
        if not any(token in lower_text for token in execution_tokens):
            continue
        if rel_path.endswith(("sense_engine.py", "commit_engine.py")):
            continue
        if any(token in text for token in delegated_budget_tokens):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_compute_smell",
                severity="RISK",
                confidence=0.88,
                file_path=rel_path,
                line=1,
                evidence=["logic runtime path appears to execute without request_compute hook"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGIC-USES-COMPUTE-BUDGET"],
                related_paths=[rel_path, logic_policy_rel, compute_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
