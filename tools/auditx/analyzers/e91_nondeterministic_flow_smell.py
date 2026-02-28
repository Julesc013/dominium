"""E91 non-deterministic flow smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E91_NONDETERMINISTIC_FLOW_SMELL"
WATCH_PREFIXES = ("src/core/flow/",)

FLOW_ENGINE_PATH = "src/core/flow/flow_engine.py"
FORBIDDEN_NONDET_TOKENS = (
    "time.time(",
    "datetime.now(",
    "uuid.uuid4(",
    "random.",
    "secrets.",
)
REQUIRED_TOKENS = (
    "sorted(",
    "channel_id",
    "tick_flow_channels(",
    "budget_outcome",
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

    text = _read_text(repo_root, FLOW_ENGINE_PATH)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_flow_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=FLOW_ENGINE_PATH,
                line=1,
                evidence=["missing deterministic flow engine substrate"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DUPLICATE-FLOW-LOGIC"],
                related_paths=[FLOW_ENGINE_PATH],
            )
        )
        return findings

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_flow_smell",
                severity="RISK",
                confidence=0.88,
                file_path=FLOW_ENGINE_PATH,
                line=1,
                evidence=["missing deterministic flow token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-DUPLICATE-FLOW-LOGIC"],
                related_paths=[FLOW_ENGINE_PATH],
            )
        )

    for token in FORBIDDEN_NONDET_TOKENS:
        if token not in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.nondeterministic_flow_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=FLOW_ENGINE_PATH,
                line=1,
                evidence=["non-deterministic token in flow engine", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DUPLICATE-FLOW-LOGIC"],
                related_paths=[FLOW_ENGINE_PATH],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

