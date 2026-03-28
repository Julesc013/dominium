"""E340 raw field grid smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E340_RAW_FIELD_GRID_SMELL"
REQUIRED_FILES = {
    "fields/field_engine.py": ("geo_cell_key", "def field_get_value(", "def field_sample_position_ref("),
    "field/field_boundary_exchange.py": ("exchange_field_boundary_values(", '"field_sampled_geo_cell_keys"'),
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
                    category="geometry.raw_field_grid_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-bound field file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-FIELD-STORAGE-GEO-KEYED", "INV-NO-RAW-FIELD-GRID-ASSUMPTION"],
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
                category="geometry.raw_field_grid_smell",
                severity="RISK",
                confidence=0.93,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-bound field token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-FIELD-STORAGE-GEO-KEYED", "INV-NO-RAW-FIELD-GRID-ASSUMPTION"],
                related_paths=[rel_path, "fields/field_engine.py"],
            )
        )
    return findings
