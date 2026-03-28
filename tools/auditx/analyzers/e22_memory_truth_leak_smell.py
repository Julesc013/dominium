"""E22 memory truth leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E22_MEMORY_TRUTH_LEAK_SMELL"
TARGET_PATH = "epistemics/memory/memory_kernel.py"
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
                category="epistemics.memory_truth_leak_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["Memory kernel missing; truth/memory separation cannot be validated."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MEMORY-NO-TRUTH"],
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
                category="epistemics.memory_truth_leak_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=line_no,
                evidence=[
                    "Memory kernel references truth-model token.",
                    snippet[:200],
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MEMORY-NO-TRUTH"],
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

