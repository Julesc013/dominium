"""E356 eager galaxy instantiation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E356_EAGER_GALAXY_INSTANTIATION_SMELL"

REQUIRED_FILES = {
    "worldgen/mw/mw_cell_generator.py": (
        "generate_mw_cell_payload(",
        "geo_cell_key",
        "max_systems_per_cell",
        "system_seed_rows",
    ),
    "geo/worldgen/worldgen_engine.py": (
        "generate_mw_cell_payload(",
        "worldgen_request",
        "generated_system_seed_rows",
    ),
}

FORBIDDEN_TOKENS = (
    "instantiate_full_galaxy",
    "generate_full_galaxy",
    "generate_all_galaxy_cells",
    "for x_index in range(",
    "for y_index in range(",
    "for z_index in range(",
)


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
                    category="worldgen.eager_galaxy_instantiation_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required Milky Way on-demand generation surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-MW-CELL-ON-DEMAND-ONLY"],
                    related_paths=[rel_path, "worldgen/mw/mw_cell_generator.py"],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.eager_galaxy_instantiation_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing Milky Way on-demand marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-MW-CELL-ON-DEMAND-ONLY"],
                    related_paths=[rel_path, "geo/worldgen/worldgen_engine.py"],
                )
            )
            continue
        for token in FORBIDDEN_TOKENS:
            if token not in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.eager_galaxy_instantiation_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=rel_path,
                    line=1,
                    evidence=["eager galaxy expansion token detected: {}".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-MW-CELL-ON-DEMAND-ONLY"],
                    related_paths=[rel_path, "worldgen/mw/mw_cell_generator.py"],
                )
            )
            break
    return findings
