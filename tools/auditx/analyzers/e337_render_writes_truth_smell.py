"""E337 render writes truth smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E337_RENDER_WRITES_TRUTH_SMELL"
TARGET_FILES = ("geo/render/floating_origin_policy.py",)
_TOKENS = (
    'position_ref["',
    "position_ref[",
    'camera_position_ref["',
    "camera_position_ref[",
)


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
    for rel_path in TARGET_FILES:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(token in snippet for token in _TOKENS):
                continue
            if "position_ref_hash(" in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geometry.render_writes_truth_smell",
                    severity="RISK",
                    confidence=0.93,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "render policy appears to index into truth refs directly",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-RENDER-REBASING-NO-TRUTH-MUTATION"],
                    related_paths=[rel_path, "geo/render/floating_origin_policy.py"],
                )
            )
            break
    return findings
