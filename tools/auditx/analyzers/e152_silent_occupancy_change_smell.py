"""E152 silent occupancy change smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E152_SILENT_OCCUPANCY_CHANGE_SMELL"


class SilentOccupancyChangeSmell:
    analyzer_id = ANALYZER_ID


_STATE_OCC_PATTERN = re.compile(r"\bstate\s*\[\s*[\"']edge_occupancies[\"']\s*\]\s*=", re.IGNORECASE)
_INLINE_OCC_PATTERN = re.compile(
    r"\b(?:current_occupancy|capacity_units|congestion_ratio_permille)\b\s*(?:\+{1,2}|-{1,2}|[*+\-\/]=)",
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
    allowed_files = {
        "tools/xstack/sessionx/process_runtime.py",
        "src/mobility/traffic/traffic_engine.py",
        "src/mobility/travel/travel_engine.py",
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
                    if not (_STATE_OCC_PATTERN.search(snippet) or _INLINE_OCC_PATTERN.search(snippet)):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.silent_occupancy_change_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["occupancy mutation token outside mobility traffic process path", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-SILENT-EDGE-ENTRY",
                                "INV-TRAVEL-THROUGH-COMMITMENTS",
                            ],
                            related_paths=[
                                rel_path,
                                "src/mobility/traffic/traffic_engine.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

