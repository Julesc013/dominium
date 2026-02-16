"""E25 omniscient map smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E25_OMNISCIENT_MAP_SMELL"
TARGET_PATH = "src/diegetics/instrument_kernel.py"
FORBIDDEN_PATTERN = re.compile(r"\b(truth_overlay|truth_model|universe_state)\b", re.IGNORECASE)
REQUIRED_TOKENS = (
    "_map_entries_from_memory(",
    "memory_store",
    "\"instrument.map_local\"",
    "\"ch.diegetic.map_local\"",
)


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
                category="diegetics.omniscient_map_smell",
                severity="RISK",
                confidence=0.92,
                file_path=rel_path,
                line=1,
                evidence=["Instrument kernel missing; map_local memory-derived behavior cannot be validated."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-INSTRUMENTS-PERCEIVED-ONLY"],
                related_paths=[rel_path],
            )
        )
        return findings

    try:
        text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return findings
    lines = text.splitlines()

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetics.omniscient_map_smell",
                severity="WARN",
                confidence=0.76,
                file_path=rel_path,
                line=1,
                evidence=["Missing map determinism token '{}'".format(token)],
                suggested_classification="PROTOTYPE",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DIEGETIC-CHANNELS-REGISTRY-DRIVEN"],
                related_paths=[rel_path],
            )
        )

    for line_no, line in enumerate(lines, start=1):
        snippet = str(line).strip()
        if not snippet:
            continue
        if not FORBIDDEN_PATTERN.search(snippet):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetics.omniscient_map_smell",
                severity="RISK",
                confidence=0.88,
                file_path=rel_path,
                line=line_no,
                evidence=[
                    "Map-local diegetic path references truth-like token.",
                    snippet[:200],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-INSTRUMENTS-PERCEIVED-ONLY", "INV-DIEGETIC-CHANNELS-REGISTRY-DRIVEN"],
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

