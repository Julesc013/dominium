"""E117 Control IR non-determinism smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E117_IR_NONDETERMINISM_SMELL"
WATCH_PREFIXES = (
    "src/control/ir/",
)

IR_FILES = (
    "src/control/ir/control_ir_verifier.py",
    "src/control/ir/control_ir_compiler.py",
    "src/control/ir/control_ir_programs.py",
    "src/control/ir/control_ir_multiplayer.py",
)

FORBIDDEN_TOKENS = (
    "random.",
    "time.time(",
    "datetime.now(",
    "uuid.uuid4(",
    "secrets.",
)

REQUIRED_TOKENS = (
    "canonical_sha256(",
    "sorted(",
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

    for rel_path in IR_FILES:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.ir_nondeterminism_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing control IR file"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-DYNAMIC-EVAL"],
                    related_paths=[rel_path],
                )
            )
            continue

        for token in FORBIDDEN_TOKENS:
            if token not in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.ir_nondeterminism_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["non-deterministic token detected in Control IR path", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-DYNAMIC-EVAL"],
                    related_paths=[rel_path],
                )
            )

        for token in REQUIRED_TOKENS:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.ir_nondeterminism_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-MACRO-BEHAVIOR-WITHOUT-IR"],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

