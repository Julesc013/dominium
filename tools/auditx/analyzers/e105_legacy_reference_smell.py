"""E105 legacy reference smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E105_LEGACY_REFERENCE_SMELL"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for root, _dirs, files in os.walk(repo_root):
        for name in files:
            if not name.endswith((".py", ".cpp", ".h", ".hpp", ".c", ".cc")):
                continue
            abs_path = os.path.join(root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if not rel_path.startswith(("src/", "engine/", "game/", "server/", "client/")):
                continue
            if rel_path.startswith(
                (
                    "legacy/",
                    "docs/",
                    "tools/xstack/testx/tests/",
                    "tools/xstack/out/",
                )
            ):
                continue
            try:
                lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, start=1):
                if "legacy/" not in line and "legacy\\" not in line:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.legacy_reference_smell",
                        severity="RISK",
                        confidence=0.9,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[line.strip()[:180], "legacy quarantine reference detected in production/runtime code"],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-LEGACY-REFERENCE"],
                        related_paths=[rel_path, "legacy/"],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
