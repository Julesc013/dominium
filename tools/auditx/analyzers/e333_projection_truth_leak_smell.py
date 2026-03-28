"""E333 projection truth leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E333_PROJECTION_TRUTH_LEAK_SMELL"
WATCH_PREFIXES = ("src/client/render/renderers/",)
TARGET_FILE = "client/render/renderers/software_renderer.py"
LEGACY_TOKENS = (
    "x, y, z = _camera_space(",
    "sx_f, sy_f, zf = _project_point(",
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
    text = _read_text(repo_root, TARGET_FILE)
    if not text:
        return []
    findings = []
    if "geo_project(" not in text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.projection_truth_leak_smell",
                severity="RISK",
                confidence=0.94,
                file_path=TARGET_FILE,
                line=1,
                evidence=["renderer projection path does not route through geo_project()"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-PROJECTION-EPITEMIC-GATED"],
                related_paths=[TARGET_FILE, "geo/kernel/geo_kernel.py"],
            )
        )
        return findings
    for line_no, line in enumerate(text.splitlines(), start=1):
        snippet = str(line).strip()
        if not snippet or snippet.startswith("#"):
            continue
        if not any(token in snippet for token in LEGACY_TOKENS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="geometry.projection_truth_leak_smell",
                severity="RISK",
                confidence=0.96,
                file_path=TARGET_FILE,
                line=line_no,
                evidence=[
                    "renderer still uses direct camera/projection path instead of GEO projection",
                    snippet[:160],
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-PROJECTION-EPITEMIC-GATED"],
                related_paths=[TARGET_FILE, "geo/kernel/geo_kernel.py"],
            )
        )
        break
    return findings
