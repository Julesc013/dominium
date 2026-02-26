"""E39 non-deterministic demography rate usage smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E39_NONDETERMINISTIC_RATE_USAGE_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"

FORBIDDEN_PATTERNS = (
    re.compile(r"\brandom\.", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
    re.compile(r"\btime\.time\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.now\(", re.IGNORECASE),
    re.compile(r"\buuid\.uuid4\(", re.IGNORECASE),
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

    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    for token in (
        "process.demography_tick",
        "math.floor(",
        "sorted(cohorts",
        "tick_rate",
        "birth_multiplier",
        "death_multiplier",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.nondeterministic_rate_usage_smell",
                severity="RISK",
                confidence=0.88,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "Demography runtime missing deterministic-rate token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                ],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    for line_no, line in _iter_lines(repo_root, PROCESS_RUNTIME_PATH):
        lowered = str(line).lower()
        if "demography" not in lowered and "birth_" not in lowered and "death_" not in lowered:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if not pattern.search(str(line)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="civilisation.nondeterministic_rate_usage_smell",
                    severity="VIOLATION",
                    confidence=0.97,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=line_no,
                    evidence=[
                        "Nondeterministic API usage detected in demography path.",
                        str(line).strip()[:140],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                    ],
                    related_paths=[PROCESS_RUNTIME_PATH],
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
