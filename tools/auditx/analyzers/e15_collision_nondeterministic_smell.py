"""E15 Collision non-deterministic ordering smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E15_COLLISION_NONDETERMINISTIC_SMELL"
TARGET_PATH = "tools/xstack/sessionx/process_runtime.py"
REQUIRED_TOKENS = (
    "def _broadphase_pairs(",
    "for cell_key in sorted(grid.keys()):",
    "return sorted(list(pair_set)",
)
UNSORTED_PATTERNS = (
    re.compile(r"for\s+\w+\s+in\s+grid\s*:", re.IGNORECASE),
    re.compile(r"for\s+\w+\s+in\s+pair_set\s*:", re.IGNORECASE),
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
                category="collision.nondeterministic_order_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["process runtime file missing; collision ordering guarantees cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-DETERMINISTIC-PAIR-ORDER"],
                related_paths=[rel_path],
            )
        )
        return findings

    try:
        lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return findings
    text = "\n".join(lines)

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="collision.nondeterministic_order_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=[
                    "Missing deterministic collision ordering token.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DETERMINISTIC-PAIR-ORDER"],
                related_paths=[rel_path],
            )
        )

    for line_no, line in enumerate(lines, start=1):
        snippet = str(line).strip()
        if not snippet:
            continue
        for pattern in UNSORTED_PATTERNS:
            if not pattern.search(snippet):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="collision.nondeterministic_order_smell",
                    severity="WARN",
                    confidence=0.75,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Potential unsorted collision iteration detected.",
                        snippet[:200],
                    ],
                    suggested_classification="PROTOTYPE",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DETERMINISTIC-PAIR-ORDER"],
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

