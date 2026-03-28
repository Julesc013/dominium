"""E339 hardcoded distance smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E339_HARDCODED_DISTANCE_SMELL"
WATCH_PREFIXES = ("src/mobility/", "src/fields/", "src/pollution/", "src/system/")
DISTANCE_PATTERNS = (
    re.compile(r"\bdx\s*\*\s*dx\b"),
    re.compile(r"\bdy\s*\*\s*dy\b"),
    re.compile(r"\bdz\s*\*\s*dz\b"),
    re.compile(r"\bdist(?:ance)?_sq\b"),
)
ALLOWLIST = {
    "geo/kernel/geo_kernel.py",
    "geo/metric/metric_engine.py",
}


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_candidate_files(repo_root: str):
    for prefix in WATCH_PREFIXES:
        abs_prefix = os.path.join(repo_root, prefix.replace("/", os.sep))
        if not os.path.isdir(abs_prefix):
            continue
        for root, _dirs, files in os.walk(abs_prefix):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(root, name)
                rel_path = os.path.relpath(abs_path, repo_root).replace(os.sep, "/")
                if rel_path in ALLOWLIST:
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    if changed_files:
        candidates = [
            str(rel_path).replace(os.sep, "/")
            for rel_path in list(changed_files or [])
            if str(rel_path).replace(os.sep, "/").endswith(".py")
            and any(str(rel_path).replace(os.sep, "/").startswith(prefix) for prefix in WATCH_PREFIXES)
            and str(rel_path).replace(os.sep, "/") not in ALLOWLIST
        ]
    else:
        candidates = list(_iter_candidate_files(repo_root))
    for rel_path in sorted(set(candidates)):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in DISTANCE_PATTERNS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geometry.hardcoded_distance_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "ad hoc distance heuristic detected outside GEO metric engine",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-RAW-DISTANCE-CALCULATION", "INV-METRIC-PROFILE-DECLARED"],
                    related_paths=[rel_path, "geo/metric/metric_engine.py"],
                )
            )
            break
    return findings
