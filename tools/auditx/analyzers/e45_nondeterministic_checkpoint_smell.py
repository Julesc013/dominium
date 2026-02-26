"""E45 non-deterministic checkpoint/branching smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E45_NONDETERMINISTIC_CHECKPOINT_SMELL"

REQUIRED_TOKENS = {
    "tools/xstack/sessionx/scheduler.py": (
        "checkpoint_interval_from_policy(",
        "if int(scheduler_tick % checkpoint_interval) == 0",
        "checkpoint_hash(",
    ),
    "tools/xstack/sessionx/script_runner.py": (
        "_write_checkpoint_artifacts(",
        "schema_name=\"time_checkpoint\"",
        "checkpoint_id = \"checkpoint.",
        "sorted(",
    ),
    "tools/xstack/sessionx/time_lineage.py": (
        "branch_from_checkpoint(",
        "compact_save(",
        "divergence_tick",
        "sorted(",
    ),
}

FORBIDDEN_PATTERNS = (
    re.compile(r"\brandom\.", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
    re.compile(r"\buuid\.uuid4\(", re.IGNORECASE),
    re.compile(r"\btime\.time\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.now\(", re.IGNORECASE),
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

    for rel_path, tokens in REQUIRED_TOKENS.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="time.nondeterministic_checkpoint_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=1,
                    evidence=["required time checkpoint/lineage file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TIME_BRANCH_IS_LINEAGE"],
                    related_paths=[rel_path],
                )
            )
            continue

        text = _read_text(repo_root, rel_path)
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="time.nondeterministic_checkpoint_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic checkpoint token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TIME_BRANCH_IS_LINEAGE"],
                    related_paths=[rel_path],
                )
            )

        for line_no, line in _iter_lines(repo_root, rel_path):
            lowered = str(line).lower()
            if "checkpoint" not in lowered and "branch" not in lowered and "compact" not in lowered:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if not pattern.search(str(line)):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="time.nondeterministic_checkpoint_smell",
                        severity="VIOLATION",
                        confidence=0.95,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "nondeterministic API usage in checkpoint/branching path",
                            str(line).strip()[:140],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-TIME_BRANCH_IS_LINEAGE"],
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
