"""E306 silent-throttle smell analyzer for META-COMPUTE0 logging/explain coverage."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E306_SILENT_THROTTLE_SMELL"


class SilentThrottleSmell:
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

    compute_engine_rel = "meta/compute/compute_budget_engine.py"
    compute_engine_text = _read_text(repo_root, compute_engine_rel)
    required_compute_tokens = (
        "explain.compute_throttle",
        "explain.compute_refusal",
        "explain.compute_shutdown",
        "runtime_state[\"throttled_owner_ids\"]",
        "runtime_state[\"explain_artifact_rows\"]",
    )
    for token in required_compute_tokens:
        if token in compute_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.compute.silent_throttle_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=compute_engine_rel,
                line=1,
                evidence=["compute engine missing required throttle/refusal explain token '{}'".format(token)],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-THROTTLE-LOGGED"],
                related_paths=[compute_engine_rel],
            )
        )

    explain_registry_rel = "data/registries/explain_contract_registry.json"
    explain_registry_text = _read_text(repo_root, explain_registry_rel)
    for token in ("explain.compute_throttle", "explain.compute_refusal", "explain.compute_shutdown"):
        if token in explain_registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.compute.silent_throttle_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=explain_registry_rel,
                line=1,
                evidence=["compute explain contract missing from registry", token],
                suggested_classification="INVALID",
                recommended_action="ADD_CONTRACT",
                related_invariants=["INV-THROTTLE-LOGGED"],
                related_paths=[explain_registry_rel],
            )
        )

    integration_specs = (
        (
            "system/macro/macro_capsule_engine.py",
            ("compute_request.get(\"decision_log_row\")", "compute_request.get(\"explain_artifact_row\")"),
        ),
        (
            "meta/compile/compile_engine.py",
            ("compute_decision_log_row", "compute_explain_artifact_row"),
        ),
        (
            "process/software/pipeline_engine.py",
            ("compute_decision_log_rows", "compute_explain_artifact_rows"),
        ),
    )
    for rel_path, required_tokens in integration_specs:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.compute.silent_throttle_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=rel_path,
                    line=1,
                    evidence=["compute integration file missing for throttle logging path"],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-THROTTLE-LOGGED"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.compute.silent_throttle_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=1,
                    evidence=["integration path missing throttle/refusal logging token '{}'".format(token)],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-THROTTLE-LOGGED"],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

