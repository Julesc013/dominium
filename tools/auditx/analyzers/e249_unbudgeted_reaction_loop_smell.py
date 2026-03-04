"""E249 unbudgeted reaction loop smell analyzer for CHEM evaluation paths."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E249_UNBUDGETED_REACTION_LOOP_SMELL"


class UnbudgetedReactionLoopSmell:
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

    checks = (
        (
            "tools/chem/tool_run_chem_stress.py",
            (
                "run_chem_stress_scenario(",
                "max_reaction_evaluations_per_tick",
                "max_cost_units_per_tick",
                "max_model_cost_units_per_tick",
                "max_emission_events_per_tick",
                "degrade.chem.eval_cap",
            ),
        ),
        (
            "tools/xstack/sessionx/process_runtime.py",
            (
                'elif process_id == "process.process_run_tick":',
                "chem_max_process_run_evaluations_per_tick",
                "degrade.chem.eval_cap",
                "_record_energy_transformation_in_state(",
            ),
        ),
    )
    for rel_path, required_tokens in checks:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="performance.unbudgeted_reaction_loop_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["required CHEM evaluation file missing or unreadable"],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-CHEM-BUDGETED",
                    ],
                    related_paths=[rel_path],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="performance.unbudgeted_reaction_loop_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=[
                    "CHEM reaction evaluation surface appears without complete deterministic budget/degrade envelope tokens",
                    "missing tokens: {}".format(", ".join(missing[:5])),
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-CHEM-BUDGETED",
                    "INV-CHEM-DEGRADE-LOGGED",
                ],
                related_paths=[
                    rel_path,
                    "tools/chem/tool_run_chem_stress.py",
                    "tools/xstack/sessionx/process_runtime.py",
                ],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

