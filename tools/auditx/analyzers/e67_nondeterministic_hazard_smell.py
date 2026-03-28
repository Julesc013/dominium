"""E67 nondeterministic hazard smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E67_NONDETERMINISTIC_HAZARD_SMELL"
DECAY_ENGINE_PATH = "materials/maintenance/decay_engine.py"
REQUIRED_TOKENS = (
    "tick_decay(",
    "step_sizes",
    "sorted(",
    "_as_int(",
    "canonical_sha256(",
)
FORBIDDEN_TOKENS = (
    "import random",
    "from random import",
    "random.",
    "secrets.",
    "time.time(",
    "datetime.now(",
    "uuid.uuid4(",
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

    text = _read_text(repo_root, DECAY_ENGINE_PATH)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.nondeterministic_hazard_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=DECAY_ENGINE_PATH,
                line=1,
                evidence=["maintenance decay engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FAILURE-MODES-REGISTRY-DRIVEN"],
                related_paths=[DECAY_ENGINE_PATH],
            )
        )
        return findings

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.nondeterministic_hazard_smell",
                severity="RISK",
                confidence=0.87,
                file_path=DECAY_ENGINE_PATH,
                line=1,
                evidence=["decay hazard implementation missing deterministic token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-FAILURE-MODES-REGISTRY-DRIVEN"],
                related_paths=[DECAY_ENGINE_PATH],
            )
        )

    for line_no, line in _iter_lines(repo_root, DECAY_ENGINE_PATH):
        token = str(line).strip()
        if not token:
            continue
        lowered = token.lower()
        if not any(item in lowered for item in FORBIDDEN_TOKENS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.nondeterministic_hazard_smell",
                severity="VIOLATION",
                confidence=0.97,
                file_path=DECAY_ENGINE_PATH,
                line=line_no,
                evidence=["nondeterministic hazard source detected", token[:140]],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FAILURE-MODES-REGISTRY-DRIVEN"],
                related_paths=[DECAY_ENGINE_PATH],
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

