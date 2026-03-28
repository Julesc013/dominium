"""E63 nondeterministic routing smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E63_NONDETERMINISTIC_ROUTING_SMELL"
LOGISTICS_ENGINE_PATH = "logistics/logistics_engine.py"
REQUIRED_TOKENS = (
    "_best_route(",
    "sorted(",
    "heapq",
    "route.shortest_delay",
    "route.min_cost_units",
    "edge_id",
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

    text = _read_text(repo_root, LOGISTICS_ENGINE_PATH)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.nondeterministic_routing_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=LOGISTICS_ENGINE_PATH,
                line=1,
                evidence=["logistics engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGISTICS-DETERMINISTIC-ROUTING"],
                related_paths=[LOGISTICS_ENGINE_PATH],
            )
        )
    else:
        for token in REQUIRED_TOKENS:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.nondeterministic_routing_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=LOGISTICS_ENGINE_PATH,
                    line=1,
                    evidence=["logistics routing implementation missing deterministic token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-LOGISTICS-DETERMINISTIC-ROUTING"],
                    related_paths=[LOGISTICS_ENGINE_PATH],
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
