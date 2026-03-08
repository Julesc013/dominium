"""E341 field sample bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E341_FIELD_SAMPLE_BYPASS_SMELL"
REQUIRED_FILES = {
    "tools/xstack/sessionx/process_runtime.py": (
        "field_binding_registry_hash",
        "exchange_field_boundary_values(",
        "field_binding_registry=",
    ),
    "tools/geo/tool_replay_field_geo_window.py": (
        "verify_geo_field_replay_window(",
        "field_binding_registry_hash",
        "verify_field_replay_window(",
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
                    category="geometry.field_sample_bypass_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-bound field runtime/proof file is missing"],
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
                category="geometry.field_sample_bypass_smell",
                severity="RISK",
                confidence=0.92,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-bound field runtime/proof token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-FIELD-STORAGE-GEO-KEYED", "INV-NO-RAW-FIELD-GRID-ASSUMPTION"],
                related_paths=[rel_path, "src/field/field_boundary_exchange.py"],
            )
        )
    return findings
