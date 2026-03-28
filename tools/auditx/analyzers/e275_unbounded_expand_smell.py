"""E275 unbounded expand smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E275_UNBOUNDED_EXPAND_SMELL"


class UnboundedExpandSmell:
    analyzer_id = ANALYZER_ID


_EXPAND_MUTATION_PATTERN = re.compile(
    r"\b(system_expand_event_rows|system_tier_change_event_rows)\b.*(?:=|append\()",
    re.IGNORECASE,
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

    scheduler_rel = "system/roi/system_roi_scheduler.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    stress_rel = "tools/system/tool_run_sys_stress.py"

    scheduler_text = _read_text(repo_root, scheduler_rel)
    runtime_text = _read_text(repo_root, runtime_rel)
    stress_text = _read_text(repo_root, stress_rel)

    for token in (
        "max_expands_per_tick",
        "max_collapses_per_tick",
        "priority_rank",
        "decision.system.roi.expand_cap",
    ):
        if token in scheduler_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_expand_smell",
                severity="RISK",
                confidence=0.95,
                file_path=scheduler_rel,
                line=1,
                evidence=["SYS scheduler missing deterministic expand budget token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-BUDGETED"],
                related_paths=[scheduler_rel, runtime_rel, stress_rel],
            )
        )

    for token in (
        "process.system_roi_tick",
        "approved_expand_count",
        "control_decision_log",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_expand_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["SYS runtime missing budgeted tier transition token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-BUDGETED"],
                related_paths=[runtime_rel, scheduler_rel],
            )
        )

    for token in (
        "max_expands_per_tick",
        "bounded_expands_per_tick",
        "degradation_policy_order",
    ):
        if token in stress_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_expand_smell",
                severity="RISK",
                confidence=0.88,
                file_path=stress_rel,
                line=1,
                evidence=["SYS stress harness missing expand-cap assertion token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-BUDGETED"],
                related_paths=[stress_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src", "system"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        scheduler_rel,
        runtime_rel,
        "tools/xstack/repox/check.py",
        "system/system_expand_engine.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not _EXPAND_MUTATION_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unbounded_expand_smell",
                            severity="RISK",
                            confidence=0.84,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential unbudgeted SYS expand/tier mutation outside canonical scheduler/runtime pathways",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-SYS-BUDGETED"],
                            related_paths=[rel_path, scheduler_rel, runtime_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
