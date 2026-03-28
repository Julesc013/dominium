"""E56 raw float in invariant quantity math smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E56_RAW_FLOAT_IN_INVARIANT_SMELL"
INVARIANT_MATH_FILES = (
    "materials/dimension_engine.py",
    "reality/ledger/ledger_engine.py",
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


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path in INVARIANT_MATH_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.raw_float_in_invariant_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=rel_path,
                    line=1,
                    evidence=["required invariant math file missing for raw-float scan"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-RAW-FLOAT-IN-INVARIANT-MATH"],
                    related_paths=[rel_path],
                )
            )
            continue

        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            lowered = token.lower()
            if "deterministic_float" in lowered:
                continue
            if (
                "float(" not in lowered
                and ": float" not in lowered
                and "-> float" not in lowered
                and "float " not in lowered
            ):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.raw_float_in_invariant_smell",
                    severity="VIOLATION",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["raw float token detected in invariant quantity path", token[:140]],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-RAW-FLOAT-IN-INVARIANT-MATH"],
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
