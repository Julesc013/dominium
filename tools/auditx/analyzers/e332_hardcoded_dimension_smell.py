"""E332 hardcoded dimension smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E332_HARDCODED_DIMENSION_SMELL"
WATCH_PREFIXES = ("src/fields/",)
TARGET_FILE = "src/fields/field_engine.py"
LEGACY_TOKEN = 'return "cell.{}.{}.{}".format('


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    text = _read_text(repo_root, TARGET_FILE)
    if not text or ("geo_partition_cell_key(" in text and LEGACY_TOKEN not in text):
        return []
    findings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        snippet = str(line).strip()
        if LEGACY_TOKEN not in snippet:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.hardcoded_dimension_smell",
                severity="RISK",
                confidence=0.97,
                file_path=TARGET_FILE,
                line=line_no,
                evidence=[
                    "hardcoded 3-axis cell-key generation detected outside GEO kernel",
                    snippet[:160],
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-HARDCODED-DIMENSION-ASSUMPTIONS"],
                related_paths=[TARGET_FILE, "src/geo/kernel/geo_kernel.py"],
            )
        )
        break
    return findings
