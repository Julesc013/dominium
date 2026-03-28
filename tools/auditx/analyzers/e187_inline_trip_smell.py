"""E187 inline trip smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E187_INLINE_TRIP_SMELL"


class InlineTripSmell:
    analyzer_id = ANALYZER_ID


_INLINE_TRIP_PATTERNS = (
    re.compile(r"\bbreaker_state\b\s*=\s*[\"'](?:tripped|open|closed|reset)[\"']", re.IGNORECASE),
    re.compile(r"\bcapacity_per_tick\b\s*=\s*0\b", re.IGNORECASE),
    re.compile(r"\b(?:trip|tripped|trip_threshold|trip_delay_ticks)\b[^\n]*(?:=|set|append)", re.IGNORECASE),
)
_FAULT_CONTEXT_PATTERN = re.compile(r"\b(?:fault|overcurrent|short_circuit|ground_fault|open_circuit)\b", re.IGNORECASE)


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
        "schema/",
        "schemas/",
    )
    allowed_files = {
        "electric/protection/protection_engine.py",
        "safety/safety_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
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
                    if not any(pattern.search(snippet) for pattern in _INLINE_TRIP_PATTERNS):
                        continue
                    if (not _FAULT_CONTEXT_PATTERN.search(snippet)) and "trip_" not in snippet.lower():
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_trip_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline electrical trip logic detected outside canonical protection runtime", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-ELEC-PROTECTION-THROUGH-SAFETY",
                                "INV-NO-ADHOC-FAULT-TRIP",
                            ],
                            related_paths=[
                                rel_path,
                                "electric/protection/protection_engine.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

