"""E225 infinite leak loop smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E225_INFINITE_LEAK_LOOP_SMELL"


class InfiniteLeakLoopSmell:
    analyzer_id = ANALYZER_ID


_WHILE_PATTERN = re.compile(r"^\s*while\s+", re.IGNORECASE)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_lines(repo_root: str, rel_path: str) -> list:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return []


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    scan_root = os.path.join(repo_root, "src", "fluid")
    if not os.path.isdir(scan_root):
        return findings
    for walk_root, _dirs, files in os.walk(scan_root):
        for name in files:
            if not name.endswith(".py"):
                continue
            abs_path = os.path.join(walk_root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if rel_path.startswith("tools/xstack/testx/tests/") or rel_path.startswith("tools/auditx/analyzers/"):
                continue
            rows = _read_lines(repo_root, rel_path)
            if not rows:
                continue
            text = "\n".join(rows)
            if "leak" not in text.lower():
                continue
            if "max_processed_targets" in text:
                continue
            for line_no, line in enumerate(rows, start=1):
                snippet = str(line).strip()
                if (not snippet) or snippet.startswith("#"):
                    continue
                if not _WHILE_PATTERN.search(snippet):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="performance.infinite_leak_loop_smell",
                        severity="RISK",
                        confidence=0.82,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "potential unbounded loop in FLUID leak-processing path",
                            snippet[:140],
                        ],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-FLUID-BUDGETED",
                            "INV-FLUID-DEGRADE-LOGGED",
                        ],
                        related_paths=[rel_path, "fluid/network/fluid_network_engine.py"],
                    )
                )
                break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
