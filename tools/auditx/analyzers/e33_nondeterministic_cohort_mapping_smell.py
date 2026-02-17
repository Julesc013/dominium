"""E33 Non-deterministic cohort mapping smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E33_NONDETERMINISTIC_COHORT_MAPPING_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/",
    "docs/civilisation/",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\brandom\.", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
    re.compile(r"\btime\.time\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.now\(", re.IGNORECASE),
    re.compile(r"\buuid\.uuid4\(", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


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
    runtime_text = _read_text(repo_root, runtime_rel)
    required_deterministic_tokens = (
        "def _cohort_seed_material(",
        "canonical_sha256(",
        "sorted(",
        "_expand_cohort_to_micro_internal(",
        "_collapse_cohort_from_micro_internal(",
    )
    for token in required_deterministic_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.nondeterministic_cohort_mapping_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=[
                    "Missing deterministic cohort mapping token in runtime.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-COHORT-EXPAND-COLLAPSE-PROCESS-ONLY",
                ],
                related_paths=[runtime_rel],
            )
        )

    for line_no, line in _iter_lines(repo_root, runtime_rel):
        lowered = str(line).lower()
        if "cohort" not in lowered and "mapping_policy" not in lowered:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if not pattern.search(str(line)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="civilisation.nondeterministic_cohort_mapping_smell",
                    severity="VIOLATION",
                    confidence=0.97,
                    file_path=runtime_rel,
                    line=line_no,
                    evidence=[
                        "Nondeterministic API usage detected in cohort mapping path.",
                        str(line).strip()[:140],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-COHORT-EXPAND-COLLAPSE-PROCESS-ONLY",
                    ],
                    related_paths=[runtime_rel],
                )
            )

    docs_rel = "docs/civilisation/COHORT_MODEL.md"
    docs_text = _read_text(repo_root, docs_rel)
    if "named RNG streams" not in docs_text and "deterministic seeds" not in docs_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.nondeterministic_cohort_mapping_smell",
                severity="WARN",
                confidence=0.7,
                file_path=docs_rel,
                line=1,
                evidence=[
                    "Cohort model docs should call out deterministic seed derivation.",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[],
                related_paths=[docs_rel],
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

