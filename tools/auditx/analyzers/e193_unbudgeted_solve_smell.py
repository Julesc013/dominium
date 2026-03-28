"""E193 unbudgeted electrical solve smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E193_UNBUDGETED_SOLVE_SMELL"


class UnbudgetedSolveSmell:
    analyzer_id = ANALYZER_ID


_SOLVE_CALL_PATTERN = re.compile(r"\bsolve_power_network_e1\s*\(", re.IGNORECASE)


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
    required_runtime_tokens = (
        "apply_elec_budget_degradation(",
        "max_network_solves_per_tick",
        "max_model_cost_units",
        "state[\"elec_degradation_events\"]",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbudgeted_solve_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["missing electrical budget/degradation token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-ELEC-BUDGETED"],
                related_paths=[runtime_rel],
            )
        )

    scan_roots = (os.path.join(repo_root, "src"), os.path.join(repo_root, "tools", "xstack", "sessionx"))
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
        "schema/",
        "schemas/",
    )
    allowed_files = {
        runtime_rel,
        "electric/power_network_engine.py",
        "tools/xstack/repox/check.py",
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
                    if not _SOLVE_CALL_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unbudgeted_solve_smell",
                            severity="RISK",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["electrical solve call outside canonical budgeted runtime", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-ELEC-BUDGETED"],
                            related_paths=[rel_path, runtime_rel],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

