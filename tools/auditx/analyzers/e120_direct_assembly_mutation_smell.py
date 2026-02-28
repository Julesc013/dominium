"""E120 direct assembly mutation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E120_DIRECT_ASSEMBLY_MUTATION_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
)


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
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.direct_assembly_mutation_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["missing process runtime file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-STRUCTURE-INSTALL"],
                related_paths=[runtime_rel],
            )
        )
        return findings

    token = 'elif process_id == "process.plan_execute":'
    branch_start = runtime_text.find(token)
    if branch_start < 0:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.direct_assembly_mutation_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=runtime_rel,
                line=1,
                evidence=["missing process.plan_execute branch"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-STRUCTURE-INSTALL"],
                related_paths=[runtime_rel],
            )
        )
        return findings

    branch_end = runtime_text.find('elif process_id == "process.construction_project_create":', branch_start)
    branch_text = runtime_text[branch_start : (branch_end if branch_end > branch_start else len(runtime_text))]
    for forbidden in ("installed_structure_instances =", "create_construction_project("):
        if forbidden not in branch_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.direct_assembly_mutation_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=runtime_rel,
                line=1,
                evidence=["direct structure install token found in plan_execute branch", forbidden],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-STRUCTURE-INSTALL"],
                related_paths=[runtime_rel],
            )
        )
    if "construction_commitments" not in branch_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.direct_assembly_mutation_smell",
                severity="RISK",
                confidence=0.86,
                file_path=runtime_rel,
                line=1,
                evidence=["plan_execute branch missing explicit construction_commitments handling"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-DIRECT-STRUCTURE-INSTALL"],
                related_paths=[runtime_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

