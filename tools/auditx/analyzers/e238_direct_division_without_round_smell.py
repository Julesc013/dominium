"""E238 direct division without deterministic round helper smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E238_DIRECT_DIVISION_WITHOUT_ROUND_SMELL"


class DirectDivisionWithoutRoundSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = (
    "src/time/",
    "src/physics/",
    "src/mobility/micro/",
)

_TARGET_FILES = (
    "src/time/time_mapping_engine.py",
    "src/physics/momentum_engine.py",
    "src/mobility/micro/free_motion_solver.py",
)

_DIVISION_PATTERN = re.compile(r"\b[A-Za-z0-9_)\]]+\s+/\s+[A-Za-z0-9_(\[]+")


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

    for rel_path in _TARGET_FILES:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if "deterministic_divide(" in snippet or "deterministic_mul_div(" in snippet:
                continue
            if not _DIVISION_PATTERN.search(snippet):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.direct_division_without_round_smell",
                    severity="RISK",
                    confidence=0.92,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["direct arithmetic division detected in deterministic numeric path", snippet[:140]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-DETERMINISTIC-ROUND-ONLY",
                        "INV-NO-IMPLICIT-FLOAT",
                    ],
                    related_paths=[rel_path, "src/meta/numeric.py"],
                )
            )
            break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
