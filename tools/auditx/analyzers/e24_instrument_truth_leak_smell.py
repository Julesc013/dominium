"""E24 instrument truth leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E24_INSTRUMENT_TRUTH_LEAK_SMELL"
TARGET_PATH = "src/diegetics/instrument_kernel.py"
FORBIDDEN_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state|registry_payloads)\b", re.IGNORECASE)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    rel_path = _norm(TARGET_PATH)
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetics.instrument_truth_leak_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["Instrument kernel missing; Perceived-only diegetic contract cannot be validated."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-INSTRUMENTS-PERCEIVED-ONLY"],
                related_paths=[rel_path],
            )
        )
        return findings

    try:
        lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return findings

    for line_no, line in enumerate(lines, start=1):
        snippet = str(line).strip()
        if not snippet:
            continue
        if not FORBIDDEN_PATTERN.search(snippet):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetics.instrument_truth_leak_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=line_no,
                evidence=[
                    "Diegetic instrument kernel references forbidden TruthModel token.",
                    snippet[:200],
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-INSTRUMENTS-PERCEIVED-ONLY"],
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

