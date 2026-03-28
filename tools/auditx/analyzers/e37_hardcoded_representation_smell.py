"""E37 hardcoded representation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E37_HARDCODED_REPRESENTATION_SMELL"
TARGET_PATH = "client/render/representation_resolver.py"
REQUIRED_TOKENS = (
    "representation_rule_registry",
    "_rule_rows(",
    "_select_rule(",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"if\s+.*material_tag.*==", re.IGNORECASE),
    re.compile(r"if\s+.*entity_kind.*==", re.IGNORECASE),
    re.compile(r"if\s+.*view_mode_id.*==", re.IGNORECASE),
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
                category="render.hardcoded_representation_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["Representation resolver missing; data-driven mapping cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-REPRESENTATION-RULES-DATA-DRIVEN"],
                related_paths=[rel_path],
            )
        )
        return findings

    try:
        text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return findings

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="render.hardcoded_representation_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["Missing representation registry token.", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-REPRESENTATION-RULES-DATA-DRIVEN"],
                related_paths=[rel_path],
            )
        )

    for line_no, line in enumerate(text.splitlines(), start=1):
        snippet = str(line).strip()
        if not snippet:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if not pattern.search(snippet):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="render.hardcoded_representation_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Representation resolver appears to hardcode mapping branch.",
                        snippet[:200],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-REPRESENTATION-RULES-DATA-DRIVEN"],
                    related_paths=[rel_path],
                )
            )
            break

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
