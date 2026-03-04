"""E233 implicit civil-time mapping smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E233_IMPLICIT_CIVIL_TIME_SMELL"

_IMPLICIT_CIVIL_TICK_CONVERSION = re.compile(
    r"\b(?:current_tick|canonical_tick|simulation_tick|tick)\s*[*\/]\s*(?:24|60|3600|86400)\b",
    re.IGNORECASE,
)
_CIVIL_KEYWORD_PATTERN = re.compile(
    r"\b(?:civil_time|calendar_time|day_night|daynight|time_of_day|timeofday)\b",
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
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/time/time_mapping_engine.py",
        "src/models/model_engine.py",
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
                    lowered = snippet.lower()
                    implicit_tick_conversion = bool(_IMPLICIT_CIVIL_TICK_CONVERSION.search(snippet))
                    implicit_civil_keyword = bool(_CIVIL_KEYWORD_PATTERN.search(snippet) and "tick" in lowered)
                    if not implicit_tick_conversion and not implicit_civil_keyword:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="time.implicit_civil_time_smell",
                            severity="VIOLATION",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "civil/proper time appears derived inline instead of through time_mapping model",
                                snippet[:140],
                            ],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-TIME-MAPPING-MODEL-ONLY",
                                "INV-SCHEDULE-DOMAIN-RESOLUTION-DETERMINISTIC",
                            ],
                            related_paths=[rel_path],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
