"""E28 precision leak on refinement smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E28_PRECISION_LEAK_ON_REFINEMENT_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
REQUIRED_OBSERVATION_TOKENS = (
    "def _apply_lod_invariance_redaction(",
    "perceived_model = _apply_lod_invariance_redaction(",
    "lod_precision_envelope_id",
)
REQUIRED_PROCESS_TOKENS = (
    "process.region_expand",
    "process.region_collapse",
    "refusal.ep.lod_information_gain",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return open(abs_path, "r", encoding="utf-8").read()


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path, required_tokens, invariant in (
        (OBSERVATION_PATH, REQUIRED_OBSERVATION_TOKENS, "INV-SOLVER-TIER-REDACTION-REQUIRED"),
        (PROCESS_RUNTIME_PATH, REQUIRED_PROCESS_TOKENS, "INV-SOLVER-TIER-REDACTION-REQUIRED"),
    ):
        try:
            text = _read_text(repo_root, rel_path)
        except OSError:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="epistemics.lod_precision_leak_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["required runtime file missing for LOD invariance precision checks"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[invariant],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="epistemics.lod_precision_leak_smell",
                    severity="WARN",
                    confidence=0.82,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing LOD precision invariance token '{}'".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[invariant],
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

