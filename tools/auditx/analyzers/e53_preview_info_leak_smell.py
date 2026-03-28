"""E53 preview info leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E53_PREVIEW_INFO_LEAK_SMELL"
WATCH_PREFIXES = (
    "client/interaction/preview_generator.py",
    "client/interaction/interaction_dispatch.py",
)
PREVIEW_PATH = "client/interaction/preview_generator.py"
FORBIDDEN_SYMBOL_PATTERNS = (
    re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE),
    re.compile(r"predicted_effects.*target_payload", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    preview_text = _read_text(repo_root, PREVIEW_PATH)
    if not preview_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.preview_info_leak_smell",
                severity="RISK",
                confidence=0.95,
                file_path=PREVIEW_PATH,
                line=1,
                evidence=["preview generator missing; epistemic preview redaction cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-AFFORDANCES-DERIVED-FROM-LAW"],
                related_paths=[PREVIEW_PATH],
            )
        )
        return findings

    for token in (
        "refusal.preview.forbidden_by_epistemics",
        "refusal.preview.budget_exceeded",
        "_target_payload_from_perceived(",
        "_ranked_redact_preview(",
        "truth_overlay",
    ):
        if token in preview_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.preview_info_leak_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PREVIEW_PATH,
                line=1,
                evidence=["missing preview epistemic/budget guard token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-AFFORDANCES-DERIVED-FROM-LAW"],
                related_paths=[PREVIEW_PATH],
            )
        )

    for line_no, line in _iter_lines(repo_root, PREVIEW_PATH):
        snippet = str(line).strip()
        if not snippet:
            continue
        for pattern in FORBIDDEN_SYMBOL_PATTERNS:
            if not pattern.search(snippet):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.preview_info_leak_smell",
                    severity="VIOLATION",
                    confidence=0.94,
                    file_path=PREVIEW_PATH,
                    line=line_no,
                    evidence=[
                        "preview path appears to expose forbidden truth payload details",
                        snippet[:200],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-UI-NEVER-MUTATES-TRUTH"],
                    related_paths=[PREVIEW_PATH],
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
