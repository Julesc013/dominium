"""E344 nondeterministic path smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E344_NONDETERMINISTIC_PATH_SMELL"
REQUIRED_FILES = {
    "src/geo/path/path_engine.py": (
        "geo_path_query(",
        "_best_open_candidate(",
        "max_expansions",
        "geo_neighbors(",
        "_policy_partial_result(",
    ),
    "src/geo/path/shard_route_planner.py": (
        "build_shard_route_plan(",
        "resolve_cell_shard_id(",
        "boundary_hops",
    ),
    "tools/geo/tool_replay_path_request.py": (
        "verify_path_request_replay(",
        "path_result_hash_chain",
        "stable_across_repeated_runs",
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
                    category="geometry.nondeterministic_path_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-6 path runtime or replay file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-PATHING-DETERMINISTIC"],
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
                category="geometry.nondeterministic_path_smell",
                severity="RISK",
                confidence=0.93,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-6 deterministic path token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-PATHING-DETERMINISTIC"],
                related_paths=[rel_path, "src/geo/path/path_engine.py"],
            )
        )
    return findings
