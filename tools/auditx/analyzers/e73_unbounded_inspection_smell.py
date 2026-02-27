"""E73 unbounded inspection smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E73_UNBOUNDED_INSPECTION_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
INSPECTION_ENGINE_PATH = "src/inspection/inspection_engine.py"
INSPECTION_CACHE_PATH = "src/performance/inspection_cache.py"
REQUIRED_RUNTIME_TOKENS = (
    "reserve_inspection_budget(",
    "max_inspection_cost_units_per_tick",
    "inspection_budget_share_per_peer",
    "inspection_runtime_budget_state",
    "refusal.inspect.budget_exceeded",
)
REQUIRED_ENGINE_TOKENS = (
    "_resolve_fidelity(",
    "_section_cost(",
    "section_cost_units",
    "max_cost_units",
    "degraded",
)
REQUIRED_CACHE_TOKENS = (
    "build_cache_key(",
    "cache_lookup_or_store(",
    "max_cache_entries",
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

    for rel_path, tokens in (
        (PROCESS_RUNTIME_PATH, REQUIRED_RUNTIME_TOKENS),
        (INSPECTION_ENGINE_PATH, REQUIRED_ENGINE_TOKENS),
        (INSPECTION_CACHE_PATH, REQUIRED_CACHE_TOKENS),
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.unbounded_inspection_smell",
                    severity="VIOLATION",
                    confidence=0.94,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MAT-9 inspection budget file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-INSPECTION-BUDGETED"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.unbounded_inspection_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=rel_path,
                    line=1,
                    evidence=["inspection budget/cache control token missing", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-INSPECTION-BUDGETED"],
                    related_paths=[rel_path],
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

