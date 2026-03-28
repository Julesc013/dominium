"""E253 unbounded cell loop smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E253_UNBOUNDED_CELL_LOOP_SMELL"


class UnboundedCellLoopSmell:
    analyzer_id = ANALYZER_ID


_LOOP_PATTERN = re.compile(r"\bfor\s+[a-zA-Z_][a-zA-Z0-9_]*\s+in\s+.*\b(field_cells|work_cells|neighbor_map)\b", re.IGNORECASE)
_POLLUTION_PATTERN = re.compile(r"\b(pollution|dispersion|concentration)\b", re.IGNORECASE)


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

    canonical_engine_rel = "pollution/dispersion_engine.py"
    canonical_text = _read_text(repo_root, canonical_engine_rel)
    for token in ("max_cell_updates_per_tick", "_split_cell_work(", "degrade.pollution.cell_budget"):
        if token in canonical_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_cell_loop_smell",
                severity="RISK",
                confidence=0.94,
                file_path=canonical_engine_rel,
                line=1,
                evidence=[
                    "Canonical pollution dispersion engine is missing required bounded-loop token",
                    token,
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-POLLUTION-FIELD-UPDATE-THROUGH-PROCESS"],
                related_paths=[
                    canonical_engine_rel,
                    "docs/pollution/DISPERSION_MODEL.md",
                ],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        canonical_engine_rel,
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/check.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not _LOOP_PATTERN.search(snippet):
                        continue
                    if not _POLLUTION_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unbounded_cell_loop_smell",
                            severity="RISK",
                            confidence=0.88,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential unbounded pollution cell iteration detected outside canonical bounded engine path",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-POLLUTION-FIELD-UPDATE-THROUGH-PROCESS"],
                            related_paths=[
                                rel_path,
                                canonical_engine_rel,
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
