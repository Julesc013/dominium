"""E305 unmetered-loop smell analyzer for META-COMPUTE0 budget enforcement."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E305_UNMETERED_LOOP_SMELL"


class UnmeteredLoopSmell:
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

    required_files = (
        "src/meta/compute/compute_budget_engine.py",
        "src/system/macro/macro_capsule_engine.py",
        "src/meta/compile/compile_engine.py",
        "src/process/software/pipeline_engine.py",
    )
    for rel_path in required_files:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.compute.unmetered_loop_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required compute budgeting integration file missing"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-ALL-EXECUTION-BUDGETED", "INV-NO-UNMETERED-COMPUTE"],
                related_paths=[rel_path],
            )
        )

    hook_checks = (
        (
            "src/system/macro/macro_capsule_engine.py",
            ("evaluate_model_bindings(", "request_compute(", "compute_consumption_record_rows"),
        ),
        (
            "src/meta/compile/compile_engine.py",
            ("compiled_model_execute(", "request_compute(", "compute_consumption_record_row"),
        ),
        (
            "src/process/software/pipeline_engine.py",
            ("evaluate_software_pipeline_execution(", "request_compute(", "compute_consumption_record_rows"),
        ),
    )
    for rel_path, required_tokens in hook_checks:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.compute.unmetered_loop_smell",
                    severity="VIOLATION",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing required metered-execution token '{}'".format(token)],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-ALL-EXECUTION-BUDGETED", "INV-NO-UNMETERED-COMPUTE"],
                    related_paths=[rel_path],
                )
            )

    compute_engine_rel = "src/meta/compute/compute_budget_engine.py"
    compute_engine_text = _read_text(repo_root, compute_engine_rel)
    for token in (
        "build_compute_consumption_record_row(",
        "\"decision_kind\": \"compute_budget\"",
        "runtime_state[\"consumption_record_rows\"]",
    ):
        if token in compute_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.compute.unmetered_loop_smell",
                severity="VIOLATION",
                confidence=0.88,
                file_path=compute_engine_rel,
                line=1,
                evidence=["compute engine missing canonical metering token '{}'".format(token)],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNMETERED-COMPUTE"],
                related_paths=[compute_engine_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

