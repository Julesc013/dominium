"""E324 silent-noise smell analyzer for LOGIC-8."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E324_SILENT_NOISE_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e324_silent_noise_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/FAULT_NOISE_SECURITY_MODEL.md",
    "schema/logic/noise_policy.schema",
    "data/registries/logic_noise_policy_registry.json",
    "src/logic/noise/noise_engine.py",
    "src/logic/eval/sense_engine.py",
    "tools/logic/tool_replay_fault_window.py",
)


class SilentNoiseSmell:
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

    doc_rel = "docs/logic/FAULT_NOISE_SECURITY_MODEL.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("deterministic quantization", "named rng", "proof-visible", "signal sampling"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_noise_smell",
                severity="RISK",
                confidence=0.83,
                file_path=doc_rel,
                line=1,
                evidence=["fault/noise doctrine missing explicit noise token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[doc_rel],
            )
        )

    schema_rel = "schema/logic/noise_policy.schema"
    schema_text = _read_text(repo_root, schema_rel)
    for token in ("noise_policy_id", "kind", "magnitude", "rng_stream_name"):
        if token in schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_noise_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=schema_rel,
                line=1,
                evidence=["logic noise policy schema missing declared field", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[schema_rel],
            )
        )

    registry_rel = "data/registries/logic_noise_policy_registry.json"
    registry_text = _read_text(repo_root, registry_rel)
    for token in ("noise.none", "noise.quantize_default", "noise.named_rng_optional"):
        if token in registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_noise_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=registry_rel,
                line=1,
                evidence=["logic noise registry missing declared noise policy", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[registry_rel],
            )
        )

    sense_rel = "src/logic/eval/sense_engine.py"
    sense_text = _read_text(repo_root, sense_rel)
    for token in ("apply_noise_policy_to_value(", "logic_noise_decision_rows", "explain.logic_noise_effect"):
        if token in sense_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_noise_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=sense_rel,
                line=1,
                evidence=["logic SENSE path missing explicit noise trace token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[sense_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_fault_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    if "logic_noise_decision_hash_chain" not in replay_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.silent_noise_smell",
                severity="RISK",
                confidence=0.88,
                file_path=replay_rel,
                line=1,
                evidence=["fault replay tool missing noise proof surface", "logic_noise_decision_hash_chain"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
