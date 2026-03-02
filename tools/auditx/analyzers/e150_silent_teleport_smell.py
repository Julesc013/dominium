"""E150 silent teleport smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E150_SILENT_TELEPORT_SMELL"


class SilentTeleportSmell:
    analyzer_id = ANALYZER_ID


_TELEPORT_PATTERN = re.compile(r"\b(?:teleport|instant[_-]?travel|warp)\b", re.IGNORECASE)
_MOBILITY_CONTEXT_PATTERN = re.compile(
    r"\b(?:vehicle|itinerary|travel|route|current_edge_id|progress_fraction_q16)\b",
    re.IGNORECASE,
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

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
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
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not _TELEPORT_PATTERN.search(snippet):
                        continue
                    if not _MOBILITY_CONTEXT_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.silent_teleport_smell",
                            severity="RISK",
                            confidence=0.83,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["mobility teleport-like token detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-TRAVEL-THROUGH-COMMITMENTS",
                                "INV-NO-SILENT-POSITION-UPDATES",
                            ],
                            related_paths=[rel_path, "docs/mobility/MACRO_TRAVEL_MODEL.md"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

