"""E302 omniscient-readout smell analyzer for instrumentation surfaces."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E302_OMNISCIENT_READOUT_SMELL"
RULE_ID = "INV-NO-TRUTH-READOUT-WITHOUT-INSTRUMENT"
TARGET_REL = "src/meta/instrumentation/instrumentation_engine.py"

FORBIDDEN_PATTERN = re.compile(r"\b(truth_model|universe_state|render_model)\b", re.IGNORECASE)
REQUIRED_TOKENS = (
    "REFUSAL_INSTRUMENTATION_INSTRUMENT_REQUIRED",
    "required_instrument not in available_instruments",
    "\"artifact_family_id\": \"OBSERVATION\"",
)


class OmniscientReadoutSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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

    text = _read_text(repo_root, TARGET_REL)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.instrumentation.omniscient_readout_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=TARGET_REL,
                line=1,
                evidence=["instrumentation engine missing; cannot enforce non-omniscient readout discipline"],
                suggested_classification="BLOCKER",
                recommended_action="ADD_CONTRACT",
                related_invariants=[RULE_ID],
                related_paths=[TARGET_REL],
            )
        )
        return findings

    for line_no, line in enumerate(text.splitlines(), start=1):
        if not FORBIDDEN_PATTERN.search(str(line)):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.instrumentation.omniscient_readout_smell",
                severity="RISK",
                confidence=0.9,
                file_path=TARGET_REL,
                line=line_no,
                evidence=["forbidden omniscient token in instrumentation readout path", str(line).strip()[:160]],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[RULE_ID],
                related_paths=[TARGET_REL],
            )
        )

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.instrumentation.omniscient_readout_smell",
                severity="RISK",
                confidence=0.86,
                file_path=TARGET_REL,
                line=1,
                evidence=["required instrumentation safety token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=[RULE_ID],
                related_paths=[TARGET_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
