"""E214 inline degradation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E214_INLINE_DEGRADATION_SMELL"


class InlineDegradationSmell:
    analyzer_id = ANALYZER_ID


_INLINE_PATTERNS = (
    re.compile(r"\bbacklog_penalty\b", re.IGNORECASE),
    re.compile(r"\bwear_penalty\b", re.IGNORECASE),
    re.compile(
        r"\bmachine_output_permille\s*=\s*max\(\s*100\s*,\s*1000\s*-\s*min\(",
        re.IGNORECASE,
    ),
)


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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    text = _read_text(repo_root, runtime_rel)
    if not text:
        return findings
    for line_no, line in enumerate(text.splitlines(), start=1):
        snippet = str(line).strip()
        if (not snippet) or snippet.startswith("#"):
            continue
        if not any(pattern.search(snippet) for pattern in _INLINE_PATTERNS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.inline_degradation_smell",
                severity="RISK",
                confidence=0.92,
                file_path=runtime_rel,
                line=line_no,
                evidence=["inline degradation heuristic detected; route through entropy policy", snippet[:160]],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-SILENT-EFFICIENCY-DROP",
                    "INV-ENTROPY-UPDATE-THROUGH-ENGINE",
                ],
                related_paths=[runtime_rel, "src/physics/entropy/entropy_engine.py"],
            )
        )
        break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
