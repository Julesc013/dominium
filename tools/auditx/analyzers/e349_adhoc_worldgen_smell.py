"""E349 ad hoc worldgen smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E349_ADHOC_WORLDGEN_SMELL"

REQUIRED_FILES = {
    "src/geo/worldgen/worldgen_engine.py": (
        "generate_worldgen_result(",
        "geo_object_id(",
        "worldgen_stream_seed(",
        '"geo_cell_key"',
    ),
    "tools/xstack/sessionx/process_runtime.py": (
        '"process.worldgen_request"',
        "generate_worldgen_result(",
        "build_worldgen_request(",
    ),
    "src/geo/projection/projection_engine.py": (
        "build_worldgen_requests_for_projection(",
    ),
    "src/system/roi/system_roi_scheduler.py": (
        "build_worldgen_requests_for_roi(",
    ),
    "tools/geo/tool_replay_worldgen_cell.py": (
        "verify_worldgen_cell_replay(",
        "worldgen_result_hash_chain",
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
                    category="worldgen.adhoc_worldgen_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-8 worldgen contract file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-WORLDGEN-ONLY-BY-CELL-KEY"],
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
                category="worldgen.adhoc_worldgen_smell",
                severity="RISK",
                confidence=0.94,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-8 worldgen contract token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-WORLDGEN-ONLY-BY-CELL-KEY", "INV-GENERATOR-VERSION-LOCKED"],
                related_paths=[rel_path, "src/geo/worldgen/worldgen_engine.py", "tools/xstack/sessionx/process_runtime.py"],
            )
        )
    return findings
