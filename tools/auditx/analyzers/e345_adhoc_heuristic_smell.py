"""E345 ad hoc heuristic smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E345_ADHOC_HEURISTIC_SMELL"
REQUIRED_FILES = {
    "geo/path/path_engine.py": (
        "_heuristic_cost(",
        "heuristic_policy",
        "traversal_policy_id",
        "geo_distance(",
    ),
    "data/registries/traversal_policy_registry.json": (
        "traverse.default_walk",
        "\"heuristic_policy\"",
        "\"partial_result_policy\"",
    ),
}


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
    for rel_path, required_tokens in sorted(REQUIRED_FILES.items()):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geometry.adhoc_heuristic_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-6 heuristic or traversal policy file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-PATHING-DETERMINISTIC", "INV-NO-ADHOC-NEIGHBOR-ENUMERATION"],
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
                category="geometry.adhoc_heuristic_smell",
                severity="RISK",
                confidence=0.92,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-6 heuristic discipline token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-PATHING-DETERMINISTIC", "INV-NO-ADHOC-NEIGHBOR-ENUMERATION"],
                related_paths=[rel_path, "geo/path/path_engine.py"],
            )
        )
    return findings
