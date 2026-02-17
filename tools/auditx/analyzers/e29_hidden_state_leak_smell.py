"""E29 hidden state leak smell analyzer for LOD refinement paths."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E29_HIDDEN_STATE_LEAK_SMELL"
TARGET_PATHS = (
    "tools/xstack/sessionx/observation.py",
    "src/net/policies/policy_server_authoritative.py",
    "src/net/srz/shard_coordinator.py",
)
FORBIDDEN_PATTERN = re.compile(
    r"\b(hidden_inventory|internal_state|micro_solver|native_precision)\b",
    re.IGNORECASE,
)
SAFE_PATTERN = re.compile(
    r"\b(lod_redaction|refusal\.ep\.lod_information_gain|test_force_lod_information_gain)\b",
    re.IGNORECASE,
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_lines(text: str):
    for line_no, line in enumerate(str(text or "").splitlines(), start=1):
        yield line_no, str(line)


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path in TARGET_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            continue
        for line_no, line in _iter_lines(text):
            if not FORBIDDEN_PATTERN.search(line):
                continue
            if SAFE_PATTERN.search(line):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="epistemics.hidden_state_leak_smell",
                    severity="RISK",
                    confidence=0.8,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "potential hidden-state token in perceived/network refinement path",
                        line.strip()[:200],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-DIRECT-MICRO-TO-PERCEIVED"],
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

