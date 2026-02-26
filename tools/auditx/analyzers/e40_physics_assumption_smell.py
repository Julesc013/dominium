"""E40 hardcoded physics assumption smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E40_PHYSICS_ASSUMPTION_SMELL"
SCAN_PATHS = (
    "tools/xstack/sessionx/creator.py",
    "tools/xstack/sessionx/runner.py",
    "tools/xstack/sessionx/script_runner.py",
    "tools/xstack/sessionx/net_handshake.py",
    "src/client/render/render_model_adapter.py",
)
FORBIDDEN_LITERAL = "physics.default.realistic"


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

    for rel_path in SCAN_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.physics_assumption_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=rel_path,
                    line=1,
                    evidence=["required runtime file missing for physics assumption scan"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-HARDCODED-PHYSICS-ASSUMPTIONS"],
                    related_paths=[rel_path],
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            if FORBIDDEN_LITERAL not in str(line):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.physics_assumption_smell",
                    severity="VIOLATION",
                    confidence=0.97,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["hardcoded optional realistic profile literal in runtime path", str(line).strip()[:140]],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-HARDCODED-PHYSICS-ASSUMPTIONS"],
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
