"""E23 memory non-determinism smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E23_MEMORY_NONDETERMINISM_SMELL"
TARGET_PATH = "src/epistemics/memory/memory_kernel.py"
WALL_CLOCK_PATTERN = re.compile(
    r"(time\.time|time\.perf_counter|time\.monotonic|datetime\.|utcnow\(|now\(|random\.|uuid\.|os\.urandom)",
    re.IGNORECASE,
)
REQUIRED_TOKENS = (
    "SOURCE_TICK_BUCKET_SIZE",
    "tick_delta",
    "ttl_ticks",
    "_apply_eviction",
    "_sort_items",
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
                category="epistemics.memory_nondeterminism_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["Memory kernel missing; deterministic memory envelope cannot be validated."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MEMORY-TICK-BASED"],
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
                category="epistemics.memory_nondeterminism_smell",
                severity="WARN",
                confidence=0.78,
                file_path=rel_path,
                line=1,
                evidence=["Missing deterministic memory token '{}'".format(token)],
                suggested_classification="PROTOTYPE",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MEMORY-TICK-BASED"],
                related_paths=[rel_path],
            )
        )

    for line_no, line in enumerate(lines, start=1):
        snippet = str(line).strip()
        if not snippet:
            continue
        if not WALL_CLOCK_PATTERN.search(snippet):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="epistemics.memory_nondeterminism_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=line_no,
                evidence=[
                    "Wall-clock or nondeterministic API used in memory kernel.",
                    snippet[:200],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MEMORY-TICK-BASED"],
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

